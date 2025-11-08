from tkinter import Tk, Frame, Label, Button, Entry
from calc import calc
from adjust_formula import AdjustFormula

# TODO signchange 를 이전의 입력숫자만 (- 로 처리하도록 고려: (- 이런식으로 식이 작성된 경우, 연산자 변경시 (%, %* 식으로 되는것을 막을것)

#### Constants for Design (You can fix) ####
COLORS:list         = ["#2C3333", "#395B64", "#A5C9CA", "#E7F6F2"]   #Color set from https://colorhunt.co/palette/2c3333395b64a5c9cae7f6f2
BUTTON_FONT:tuple   = ("Courier", 25, "bold")
DISPLAY_FONT:tuple  = ("Courier", 14, "italic")
BUTTON_WIDTH:int = 2
BUTTON_HEIGHT:int = 1
DISPLAY_WIDTH:int = 24


#### Globally defined constants ####
OPS:list            = ["*", "/", "+", "-", "%"]
ALLOWED_CHARS:list  = list("0123456789./-+*%()")
INPUT_LIMIT:int     = 30    # user input length limit.


#### Globally accessible variables ####
g_last_display:str = ""               # last history result memory: globally update.
g_prepare_for_new_input:bool = False  # check ready for input trigger: turn on True after equals(). (clear_button display after result print if you click number)


#### Global Functions: Treat dispay_entry Funcs: read, write, delete ####
def get_entry() -> str:                                     return display_entry.get() 
def insert_entry(idx = 0, string:str = "") -> None:         display_entry.insert(idx, string)
def push_entry(string:str) -> None:                         display_entry.insert("end", string)
def remove_entry(start_index:int = 0, end_index: int | str = "end") -> None:   display_entry.delete(start_index, end_index);
''' Note 
delete() 는 요소가 한개일때는 한글자만 지우나, remove_entry는 (target, target + 1) 로 지워야함을 반드시 숙지.
반대로 delete(start, "end") 로 start부터 끝까지 지웠으나, remove_entry는 (target) 하면 뒤로 완전히 지워짐.
'''


#### Keyboard bind helper functions

def open_parentheses():      # 열때 직전입력 ')' 면 사이에 '*' 추가
    content:str = get_entry()
    if content != "" and content[-1] == ")":    push_entry("*(")
    else: push_entry("(")
        
def close_parentheses():
    content:str = get_entry()
    if content == "":                               return      # ignore close if entry is empty
    if content.count("(") <= content.count(")"):    return      # ignore close if not openned
    if content[-1] == "(":                          return      # ignore close if last input was just openned
    push_entry(")")
    
def backspace(event):       # It's created to handle the scenario where the entry widget loses focus.
    content:str = get_entry()
    focus = str(window.focus_get())         #TIP. tkinter focus_get() return your active widget name.
    if (focus != ".!frame.!entry") and (len(content)) > 0:
        last_index = len(content) -1
        remove_entry(last_index)

def set_window_focus(event):                # display_entry 포커스시 강제 포커스해제, break
    window.focus_set()
    key_perssed:str = event.char
    if get_entry() == "":                   # 첫입력은 허용: 숫자, - 까지도 허용. (괄호열기는 이미 처리됨)
        if key_perssed in "0123456789":     number_button(key_perssed)
        if key_perssed == "-":              operator_button(key_perssed)
    return "break"


#### Inheritance/Dependency Functions for Button Logic ####

def find_last_ops_index(user_input:str) -> int:     # Used as an inheritance function : #! += 버튼에만 종속됨. 내부화 고려.
    last_ops_index = 0
    for i in range(len(user_input)):                #! 연산자 찾기 코드 리팩토링, 디버깅 25-04-22
        if user_input[i] in "/-+*%()":              last_ops_index = i
    return last_ops_index

def update_input_ready_status(func=False) -> None:  # first_input trigger switching method. 
    global g_prepare_for_new_input
    if func:        g_prepare_for_new_input = True
    else:           g_prepare_for_new_input = False
  
def error_display(errmsg: str = "ERROR") -> None:    # Display a message in the entry, disable the button, and restore it after 3 seconds.    
    def disable_button():   equals_button.config(bg="red", state="disabled")
    def restore_button():   equals_button.config(bg=COLORS[1], fg=COLORS[3], state="normal")
    def clear_display():    remove_entry()
    
    disable_button()
    clear_display()
    insert_entry(0, errmsg)
    window.after(3000, lambda: (restore_button(), clear_display())) # tip: windows에 전달할 함수가 복수라면 람다를 사용

def adjust_precision(result: float) -> float:                   # 정밀도 보정함수 : 25-04-20
    if result == int(result):   result = int(result)            # 정수로 변환 가능한 경우 정수로 변환
    else:                       result = round(result, 13)      # 소수점 이하 13자리까지 반올림
    
    if abs(result - int(round(result))) < 0.000_000_000_001:    # 매우 작은 오차 보정(정수 반올림)
        result = int(round(result))                 
    return result                
                
def update_recent_labels(formula:str, result:float) -> None:      
    # Update recent labels and Update display_entry(except input just "=") : 25-04-21
    remove_entry()
    insert_entry(0, str(result))
    
    global g_last_display
    # Extract the last result from Last_Display.
    last_display_result:str

    if "=" in str(g_last_display): last_display_result = g_last_display.split('=')[-1]
    else: last_display_result = g_last_display
    
    #! debug: 아무 입력 없이 = 호출할 때 3자리 미만 숫자만 갱신 막는 것을 해결(쉼표,처리 제거) : 25-11-02
    last_display_result = last_display_result.replace(",", "")
    
    old_display:str = g_last_display
    g_last_display = f"{formula}={result:,}"  #for update recent label.
        
    if len(g_last_display) >= 40: g_last_display = f"{result:,}"    # Last_Display is just result if that is longer than 40 chars
        
    if last_display_result != formula:
        if recent_label_1["text"] == "":
            recent_label_1.config(text=g_last_display)
        else:
            recent_label_2.config(text=old_display)
            recent_label_1.config(text=g_last_display)


#### Button functions ####

## Number (0~9) and Operators (*, /, +, -, %) ##

def number_button(num:str):
    content:str = get_entry()
    if content != "" and content[-1] == ")":    push_entry("*")    # Auto insert "*" after ")"
    if g_prepare_for_new_input:                   remove_entry()
    update_input_ready_status()                 #Trigger make False.
    push_entry(num)

def operator_button(operator):
    content:str = get_entry()
    if content != "" and content[-1] == "(" and operator!= "-" : return     #! DEBUG: 괄호 뒤 연산자 입력차단 (25-11-09)
    if content != "" and content[-1] == "%" and operator == "%": return     #! DEBUG: % 연속입력 금지 (25-04-22)
    if operator in "+*/%" and content == "":    return     # DEBUG: 비어있는상태에선 연산자로 시작할 수 없음(-제외) 25-04-21
    if content == "-":                  # DEBUG: - 기호만 입력된 상태에서 연산자를 다시 누르는것을 허용하지 않음 25-04-22
        if operator == "-":                     remove_entry()            # 단항 '-' 입력된 상태에서 다시 입력시 제거
        return   

    if len(content) > 0 and content[-1] in OPS:  # 연산자 연속입력시 최근입력된 연산자만 사용 기능 내부화 25-04-22
        last_index:int = len(content) -1
        remove_entry(last_index) 
            
    update_input_ready_status()
    push_entry(operator)


## Special Action Buttons    (., C, +-, (), =) ##

def point_button():  # '.' Button
    content:str = display_entry.get()
    if content == "" or content[-1] in OPS:     return   # 비어있으면 입력금지, 직전입력 연산자이면 입력금지
    
    # 뒤에서부터 탐색하여 마지막 연산자 이후의 숫자를 가져옴 (연산자, 비어있는기준 마지막 입력된 숫자 파싱)
    last_number:str = ""
    for char in reversed(content):
        if char in OPS:                         break
        last_number = char + last_number        #! 숫자를 앞에 추가 (reversed 된걸 다시 거꾸로 추가함)
        
    if "." in last_number:                      return   # 마지막 숫자에 이미 '.'이 포함되어 있으면 입력 차단
    update_input_ready_status()
    push_entry(".")
    
def clear_button():    # 'C' Button
    window.focus_set()
    update_input_ready_status()
    remove_entry()

# signchange_button() function turns the input into negative or positive based on various conditions.
# The content isn't really important. I just kept debugging until it worked as wished.
#! TODO: 간소화 리펙토링 필요  
def signchange_button():       # '+-' Button.
    update_input_ready_status()
    content:str = get_entry()
    if content == "" or content == '0': return      # DEBUG: clicked with empty or 0   (25-04-20)
    last_index:int = find_last_ops_index(content)    
    
    if len(content) > 0 and len(content)-1 != last_index and last_index > 0:      
        if last_index > 0:
            if content[last_index] == "*": 
                insert_entry(last_index + 1, "(-")
            elif content[last_index] == "-": 
                remove_entry(last_index, last_index + 1)
                insert_entry(last_index, "+")
            elif content[last_index] == "+":
                remove_entry(last_index, last_index + 1)
                insert_entry(last_index, "-") 
            elif content[last_index] == "(":
                insert_entry(last_index + 1, "-")
    elif len(content)-1 == last_index and last_index > 0:
        if content[last_index] == "-":
            remove_entry(last_index, last_index + 1)
            insert_entry(last_index, "+")
        elif content[last_index] == "(":
            insert_entry(last_index + 1, "-")  
        else:
            remove_entry(last_index, last_index + 1)
            insert_entry(last_index, "-")                                
    else:
        if content[0] != "-":
            insert_entry(0, "-")
        elif content[0] == "-":
            remove_entry(0, 1)

# Auto Open/Closing: Algorithm for deciding whether to open or close parentheses_button when "pressing the corresponding button"
def parentheses_button():      # '( )' Bottn.
    update_input_ready_status()
    content:str = get_entry()
    left:int = content.count("(")
    right:int = content.count(")")
    if content == "":           push_entry("(")
    elif content[-1] == "(":    push_entry("(")
    elif content[-1] in OPS:    push_entry("(")
    elif left > right:          push_entry(")")
    elif left == right:
        if content[-1] in OPS:  push_entry("(") 
        else:                   push_entry("*(")
    else:                       push_entry("error")

# '=' Button
def equals():
    window.focus_set()    
    # make and init user_formula and user_formula result.    
    user_formula:str = AdjustFormula(get_entry()).get_standard_fix()        # Adjustments for various formula errors 25-04-21
    user_formula_result:float = 0.0
          
    # Error handling:   #! 리팩토링: equals()에서만 다뤄지는 간단한 함수 모두 삭제 :25-04-22
    try:    
        for c in user_formula:  # 허용되지 않은 문자입력시 (현재는 쓰일일은 없으나 유지.)
            if c not in ALLOWED_CHARS:          raise ValueError("Unauthorized input")
        if len(user_formula) > INPUT_LIMIT:     raise ValueError("Out of range") # 최대 입력문자 한계 초과
        
    except ValueError as e:
        # print(f"ERR: err = {str(e)}, user_formula = {user_formula}, user_formula_result = {user_formula_result}")       #! TEST DEBUG CODE
        if str(e) == "Unauthorized input": 
            window.after(0,     lambda: error_display(errmsg= "Unauthorized input"))
        if str(e) == "Out of range": 
            window.after(0,     lambda: error_display(errmsg= f"OUT OF RANGE({len(user_formula)}/{INPUT_LIMIT})"))
        return
    
    # print(f"DEBUG: {user_formula}")       #! TEST DEBUG CODE
    # calculating and fix precision with Handling unexpected errors (25-04-21)
    try:
        user_formula_result:float = adjust_precision(calc(user_formula))     # 정밀도 보정 함수 적용 (25-04-20)
    except:
        if user_formula == "":
            user_formula = "EMPTY"    #! 수식 문자열이 비어있음을 경고
        errmsg:str = f"Failed read formula: {user_formula}"
        window.after(0,         lambda: error_display(errmsg= errmsg))
        return
    
    update_input_ready_status(True)             # This trigger will clear_button display if you click number after calc.

    # UI update recent_label 1, 2 and update display_entry
    update_recent_labels(formula=user_formula, result= user_formula_result)     
            
            
#### UI OBJECTS ####

# Make Window
window = Tk()
window.config(padx=15, pady=15, bg=COLORS[0], highlightthickness=0)
window.title("Python calc")

#### DISPLAY FRAME ####

# Recent result label
display_frame = Frame(window)
display_frame.config(bg=COLORS[0], pady=15, highlightthickness=0)
display_frame.grid(column=0, row=0)
recent_label_2 = Label(display_frame, text="", bg=COLORS[0], fg=COLORS[3])
recent_label_2.grid(column=0, row=1, sticky='e')
recent_label_1 = Label(display_frame, text="", bg=COLORS[0], fg=COLORS[3])
recent_label_1.grid(column=0, row=2, sticky="e")

# Display Entry
display_entry = Entry(display_frame, justify="right", width=DISPLAY_WIDTH, highlightthickness=0, font=DISPLAY_FONT, bg=COLORS[2], fg=COLORS[0])
display_entry.grid(column=0, row=3)


#### BUTTONS FRAME ####

button_frame = Frame(window)
button_frame.grid(column=0, row=2)

# BUTTONS DESIGN(text, position, function, color)
color_types = {"normal": (3, 0), "equalClear": (1, 3), "operator": (2, 3),}     # COLORS Index. (background, forground)
buttons = [         #(text, row, col, command, color_type)
    # ROW 0
    ("C", 0, 0, clear_button, "equalClear"),
    ("( )", 0, 1, parentheses_button, "operator"),
    ("%",   0, 2, lambda: operator_button("%"), "operator"),
    ("/",   0, 3, lambda: operator_button("/"), "operator"),
    # ROW 1
    ("7", 1, 0, lambda: number_button("7"), "normal"),
    ("8", 1, 1, lambda: number_button("8"), "normal"),
    ("9", 1, 2, lambda: number_button("9"), "normal"),
    ("*",   1, 3, lambda: operator_button("*"), "operator"),
    # ROW 2
    ("4", 2, 0, lambda: number_button("4"), "normal"),
    ("5", 2, 1, lambda: number_button("5"), "normal"),
    ("6", 2, 2, lambda: number_button("6"), "normal"),
    ("-",   2, 3, lambda: operator_button("-"), "operator"),
    # ROW 3
    ("1", 3, 0, lambda: number_button("1"), "normal"),
    ("2", 3, 1, lambda: number_button("2"), "normal"),
    ("3", 3, 2, lambda: number_button("3"), "normal"),
    ("+",   3, 3, lambda: operator_button("+"), "operator"),
    # ROW 4
    ("+/-", 4, 0, signchange_button, "normal"),
    ("0", 4, 1, lambda: number_button("0"), "normal"),
    (".", 4, 2, point_button, "normal"),
    ("=",   4, 3, equals,                       "equalClear"),
]

for text, row, col, cmd, color_type in buttons:
    bg_idx, fg_idx = color_types[color_type]
    btn = Button( button_frame, text=text, font=BUTTON_FONT, 
                 width=BUTTON_WIDTH, height=BUTTON_HEIGHT, highlightthickness=0,
                 command=cmd, bg=COLORS[bg_idx], fg=COLORS[fg_idx],)
    btn.grid(column=col, row=row)
    
    if text == "=":     # eqauls_button 은 에러 발생 등 색상 변경과 잠시 비활성화 해야 하기 때문에 글로벌 변수로 지정(의미있는 행동인지 검토)
        global equals_button
        equals_button = btn
        

#### Bind keyboard  - Button input is preferred. Only some function keys are bound to the keyboard. ####

# number and operator keys bind.
for n in "0123456789":  window.bind(n, lambda event, n = n: number_button(num=n))
for o in "+-*/%":       window.bind(o, lambda event, o = o: operator_button(operator=o))

# function keys bind.
window.bind(".", lambda event:   point_button())
window.bind("<Return>", lambda event:   equals())               # enter
window.bind("<Escape>", lambda event:   clear_button())                # esc
window.bind("(", lambda event:   open_parentheses())
window.bind(")", lambda event:   close_parentheses())
window.bind("<BackSpace>",              backspace)              # backspace

# deactive display_entry focus bind.(every key event on display_entry -> set_window_focus(): window.focus_set())
display_entry.bind("<Key>", set_window_focus)

#### MAIN ####
window.mainloop()
from tkinter import *
from calc import calc

OPS = ["*", "/", "+", "-"]
BUTTON_FONT = "Courier", 25, "bold"
DISPLAY_FONT = "Courier", 14, "italic"
COLORS = ["#2C3333", "#395B64", "#A5C9CA", "#E7F6F2"]   #Color set from https://colorhunt.co/palette/2c3333395b64a5c9cae7f6f2
ALLOWED_CHARS =list("0123456789./-+*%()")
INPUT_LIMIT = 30    # user input length limit.

Last_Display = ""                  # 계산 기록 추가용 임시 변수: global로 업데이트됨.
Prepare_for_New_input = False      # this trigger will turn on True after calc. (for clear display if you click number.)


#### Inheritance functions

def check_safe_for_eval(user_input):  #Check unauthorized input because this code use eval(this is dangerous) function.
    for char in user_input:
        if char not in ALLOWED_CHARS:
            return False 
    return True

def find_last_ops_index(user_input):     # Used as an inheritance function
    last_ops_index = 0
    chars = list("/-+*&()")
    replace = list(user_input)
    for c in replace:
        if c in chars:
            if replace.index(c) > last_ops_index:
                last_ops_index = replace.index(c)
                replace[replace.index(c)] = "removed"
    return last_ops_index

def update_input_ready_status(func=False):     #first_input trigger switching method. 
    global Prepare_for_New_input   
    if func == True:
        Prepare_for_New_input = True
    else:
        Prepare_for_New_input = False 
        
def pop_last_ops() -> None:     # remove the last operator if the last input is an operator. - Used as an inheritance function.
    current = display_entry.get()
    if len(current) > 0:
        if current[-1] in OPS:
            last_index = len(current) -1
            display_entry.delete(last_index, END)    
            
def invalid_formula_length(formula:str) -> bool:        # Check if the formula exceeds the allowed length limit
    if len(formula) > INPUT_LIMIT: return True
    return False


#! pop_last_ops() 부분 내부구현 고려.-> 진행중.
#! adjust_formula 기능이 더 첨가될 것을 고려하여 모듈화 고민(각기능 함수화).
#! TODO: 05 + 2 등 입력시 5 + 2 등으로 수정하는 기능 필요 (calc.py 단에서 수정해야할지, 숫자버튼에서 비어있는 상태 혹은 연산자 뒤 0이 선입력인지 고려할 것. 예: 비어있는상태 or 연산자, 괄호 뒤 등에 0 입력후 다른숫자 입력시: 05-> 5로 변경 필요)
def adjust_formula(formula: str) -> str:                # Fix formula. 여러 입력오류들을 보정.
    # replace "(*" to "(1*"
    if "(*" in formula:
        formula = formula.replace("(*", "(1*")
    
    # Ensure "*" is automatically inserted after "%" when necessary
    if "%" in formula:
        result = []
        for i, char in enumerate(formula):
            result.append(char)
            if char == "%" and i + 1 < len(formula) and formula[i + 1] not in OPS + [")"]:
                result.append("*")  # "%" 뒤에 "*" 추가
        formula = "".join(result)
    
    # Add "*" for implicit multiplication (keyboard input only) (e.g: 3(2+1) -> 3*(2+1),  (3+2)4 -> (3+2)*4)
    i = 0
    while i < len(formula) - 1:
        # Insert "*" before "(" if preceded by a number
        if formula[i].isdigit() and formula[i + 1] == "(":
            formula = formula[:i + 1] + "*" + formula[i + 1:]
            i += 1
        # Insert "*" after ")" if followed by a number
        elif formula[i] == ")" and formula[i + 1].isdigit():
            formula = formula[:i + 1] + "*" + formula[i + 1:]
            i += 1
        i += 1
    i = 0       # Reset index for reprocessing after modifications
    
    # Automatically close any unclosed parentheses in the formula
    openedParentheses = formula.count("(")
    closedParentheses = formula.count(")")
    if openedParentheses > closedParentheses:
        for _ in range(openedParentheses-closedParentheses):
            formula += ")"    

    # If the formula is empty, set the result to '0' by default
    if formula == "": formula = '0'

    return formula

#! TODO: error_print 조정중: 25-04-20
def error_print(msg: str = "ERROR"):
    """엔트리에 msg를 출력하고, 버튼을 비활성화 후 3초 후 복원"""
    
    def disable_button():
        equals_button.config(bg="red", state=DISABLED)
    
    def restore_button():
        equals_button.config(bg=COLORS[1], fg=COLORS[3], state=NORMAL)
    
    def clear_display():
        display_entry.delete(0, END)
    
    disable_button()
    clear_display()
    display_entry.insert(0, msg)
    
    # 3초 후 restore_button과 clear_display를 동시에 실행
    window.after(3000, lambda: (restore_button(), clear_display()))

#! TEST: 정밀도 보정함수추가 : 25-04-20
def adjust_precision(result: float) -> float:    
    if result == int(result): result = int(result)      # 정수로 변환 가능한 경우 정수로 변환
    else: result = round(result, 13)                    # 소수점 이하 13자리까지 반올림

    if abs(result - int(round(result))) < 0.000_000_000_001:    
        result = int(round(result))                 # 매우 작은 오차 보정 (결과값이 정수에 가까운 경우 정수로 변환)
    return result                
                
                
#### Button functions.

## Number (0~9) and Operators (*, /, +, -, %)  
def insert_multiplication():   # Auto insert "*" after ")" - Used as an inheritance function
    current = display_entry.get()
    if current != "":
        if current[-1] == ")":
            display_entry.insert(END, "*")
            
def number_input(num):
    insert_multiplication() 
    if Prepare_for_New_input:
        display_entry.delete(0, END)      
    update_input_ready_status()    #Trigger make False.
    display_entry.insert(END, num)
    
def operator_button(operator):
    pop_last_ops()
    update_input_ready_status()
    display_entry.insert(END, operator)
    
    
## Function keys    (., C, +=, (), =)
def point():
    update_input_ready_status()
    display_entry.insert(END, ".")
def clear():
    update_input_ready_status()
    display_entry.delete(0, END)

# signchange() function turns the input into negative or positive based on various conditions. 
# The content isn't really important. I just kept debugging until it worked as wished.    
def signchange():
    update_input_ready_status()
    current = display_entry.get()
    if current == "" or current == '0': return      #! DEBUG: clicked with empty or 0   (25-04-20)
    last_index = find_last_ops_index(current)    
    
    if len(current) > 0 and len(current)-1 != last_index and last_index > 0:      
        if last_index > 0:
            if current[last_index] == "*":
                display_entry.insert(last_index + 1, "(-")
            elif current[last_index] == "-":
                display_entry.delete(last_index)
                display_entry.insert(last_index, "+")
            elif current[last_index] == "+":
                display_entry.delete(last_index)
                display_entry.insert(last_index, "-")   
            elif current[last_index] == "(":
                display_entry.insert(last_index + 1, "-")
    elif len(current)-1 == last_index and last_index > 0:
        if current[last_index] == "-":
            display_entry.delete(last_index)
            display_entry.insert(last_index, "+")
        elif current[last_index] == "(":
            display_entry.insert(last_index + 1, "-")    
        else:
            display_entry.delete(last_index)
            display_entry.insert(last_index, "-")                                  
    else:
        if current[0] != "-":
            display_entry.insert(0, "-")
        elif current[0] == "-":
            display_entry.delete(0)      

# Auto Open/Closing: Algorithm for deciding whether to open or close parentheses when "pressing the corresponding button"            
def parentheses():
    update_input_ready_status()
    current = display_entry.get()
    left = current.count("(")
    right = current.count(")")
    if current == "":
        display_entry.insert(END, "(")
    elif current[-1] == "(":
        display_entry.insert(END, "(")
    elif current[-1] in OPS:
        display_entry.insert(END, "(")
    elif left > right:
        display_entry.insert(END, ")")
    elif left == right:
        if current[-1] in OPS:    
            display_entry.insert(END, "(")    
        else:
            display_entry.insert(END, "*(")     # Auto Multiplication insert.
    else:
        display_entry.insert(END, "error")

#! TODO : equals() 함수내부 복잡도때문에 함수화 리팩토링 진행중
def equals():       # Button Function.
    
    #! TODO: adjust_formula() 에 내부구현 가능한지 리펙토링 검토.  : 현재 pop_last_ops()는 다른데서도 쓰이니 신중히 검토.
    pop_last_ops()   # remove incorrect operators before calculation. ('1+3-=' > '1+3=')
        
    current:str = adjust_formula(display_entry.get())       # 계산식 여러 오류 검토/보정
    
    # check formula is valid length
    if invalid_formula_length(current):        
        window.after(0, lambda: error_print(f"OUT OF RANGE({len(current)}/{INPUT_LIMIT})"))
        return
              
    #! TODO: adjust_formula() 에 내부구현 가능한지 리펙토링 검토. : 어려운부분: 히스토리에는 last_questestion 사용, 내부적으로는 current사용.
    # Replace "/ 100" instead of "%"
    #!  /100 으로 유지하고 last_questestion 을 사용하지 않는방향이면 쉽게 가능. (아래 recent result 업데이트도 리팩토링 해야함.)
    last_questestion = current  # maintain "%" on recent label
    if "%" in current:
        for _ in range(current.count("%")):
            current = current.replace("%", "/100")
            
    # Try make Result
    try:
        if check_safe_for_eval(current):  #! 원래 eval검사용이었으나, calc로 바뀌고 현재 식에 사용된 문자 유효성 검사로 사용중.
            result: float = calc(current)  # eval에서 calc모듈(직접작성) 으로 변경됨.
            result: float = adjust_precision(result)   # 정밀도 보정 함수 적용 (25-04-20)
            update_input_ready_status(True)  # This trigger will clear display if you click number after calc.
        else:
            raise ValueError("Unauthorized input")
        
    # Exception Handling -> result = 'err'
    except:
        window.after(0, lambda: error_print("ERROR"))   
        return      #! quit equal() instead of make result.
        # result = "err"  
        
    # Update result on display_entry
    display_entry.delete(0, END)
    display_entry.insert(0, str(result))
    
    
    #! TODO: 최근검사식 업데이트 함수화 고려.
    # Recent result labels Update (except input just "=")
    global Last_Display 
    if "=" in str(Last_Display):    # if Last_Display has result without fomula.
        Last_Display_result = Last_Display.split('=')[-1]   
    else:
        Last_Display_result = Last_Display  
    Last_Display_2 = Last_Display
    if result == "err":
        Last_Display = (f"{last_questestion}={result}")  #for update recent label.
    else:
        Last_Display = (f"{last_questestion}={result:,}")  #for update recent label.
    if len(Last_Display) >= 40:
        Last_Display = f"{result:,}"   #Last_Display is just result if that is longer than 27 chars
    if Last_Display_result != current:  
        if recent_label_1["text"] == "":
            recent_label_1.config(text=Last_Display)
        else:
            recent_label_2.config(text=Last_Display_2)
            recent_label_1.config(text=Last_Display)
            
            
#### UI
#Make Window
window = Tk()
window.config(padx=15, pady=15, bg=COLORS[0], highlightthickness=0)
window.title("Python calc")

####DISPLAY FRAME####
#Recent result label
display_frame = Frame(window)
display_frame.config(bg=COLORS[0], pady=15, highlightthickness=0)
display_frame.grid(column=0, row=0)
recent_label_2 = Label(display_frame, text="", bg=COLORS[0], fg=COLORS[3])
recent_label_2.grid(column=0, row=1, sticky='e')
recent_label_1 = Label(display_frame, text="", bg=COLORS[0], fg=COLORS[3])
recent_label_1.grid(column=0, row=2, sticky="e")
#Display Entry
display_entry = Entry(display_frame, text="Display", justify=RIGHT, width=24, highlightthickness=0, font=DISPLAY_FONT, bg=COLORS[2], fg=COLORS[0])
# display_entry.focus()
display_entry.grid(column=0, row=3)

####BUTTONS FRAME ####
button_frame = Frame(window)
button_frame.grid(column=0,row=2)
#FirstLine(Top)         #Tip. Use lambda to delay function call until event (e.g., button press)
clear_button = Button(button_frame, text="C", font=BUTTON_FONT, width=3,height=1, highlightthickness=0, command=clear, bg=COLORS[1], fg=COLORS[3])
clear_button.grid(column=0, row=0)
parentheses_button = Button(button_frame, text="( )", font=BUTTON_FONT, width=3,height=1, highlightthickness=0, command=parentheses, bg=COLORS[2], fg=COLORS[3])
parentheses_button.grid(column=1, row=0)
percent_button = Button(button_frame, text="%", font=BUTTON_FONT, width=3,height=1, highlightthickness=0, command=lambda:operator_button("%"), bg=COLORS[2], fg=COLORS[3])
percent_button.grid(column=2, row=0)
division_button = Button(button_frame, text="/", font=BUTTON_FONT, width=3,height=1, highlightthickness=0, command=lambda:operator_button("/"), bg=COLORS[2], fg=COLORS[3])
division_button.grid(column=3, row=0)
#SecondLine
seven_button = Button(button_frame, text="7", font=BUTTON_FONT, width=3,height=1, highlightthickness=0, command=lambda:number_input("7"), bg=COLORS[3], fg=COLORS[0])
seven_button.grid(column=0, row=1)
eight_button = Button(button_frame, text="8", font=BUTTON_FONT, width=3,height=1, highlightthickness=0, command=lambda:number_input("8"), bg=COLORS[3], fg=COLORS[0])
eight_button.grid(column=1, row=1)
nine_button = Button(button_frame, text="9", font=BUTTON_FONT, width=3,height=1, highlightthickness=0, command=lambda:number_input("9"), bg=COLORS[3], fg=COLORS[0])
nine_button.grid(column=2, row=1)
multiplication_button = Button(button_frame, text="*", font=BUTTON_FONT, width=3,height=1, highlightthickness=0, command=lambda:operator_button("*"), bg=COLORS[2], fg=COLORS[3])
multiplication_button.grid(column=3, row=1)
#ThirdLine
four_button = Button(button_frame, text="4", font=BUTTON_FONT, width=3,height=1, highlightthickness=0, command=lambda:number_input("4"), bg=COLORS[3], fg=COLORS[0])
four_button.grid(column=0, row=2)
five_button = Button(button_frame, text="5", font=BUTTON_FONT, width=3,height=1, highlightthickness=0, command=lambda:number_input("5"), bg=COLORS[3], fg=COLORS[0])
five_button.grid(column=1, row=2)
six_button = Button(button_frame, text="6", font=BUTTON_FONT, width=3,height=1, highlightthickness=0, command=lambda:number_input("6"), bg=COLORS[3], fg=COLORS[0])
six_button.grid(column=2, row=2)
subtraction_button = Button(button_frame, text="-", font=BUTTON_FONT, width=3,height=1, highlightthickness=0, command=lambda:operator_button("-"), bg=COLORS[2], fg=COLORS[3])
subtraction_button.grid(column=3, row=2)
#FourthLine
one_button = Button(button_frame, text="1", font=BUTTON_FONT, width=3,height=1, highlightthickness=0, command=lambda:number_input("1"), bg=COLORS[3], fg=COLORS[0])
one_button.grid(column=0, row=3)
two_button = Button(button_frame, text="2", font=BUTTON_FONT, width=3,height=1, highlightthickness=0, command=lambda:number_input("2"), bg=COLORS[3], fg=COLORS[0])
two_button.grid(column=1, row=3)
three_button = Button(button_frame, text="3", font=BUTTON_FONT, width=3,height=1, highlightthickness=0, command=lambda:number_input("3"), bg=COLORS[3], fg=COLORS[0])
three_button.grid(column=2, row=3)
addition_button = Button(button_frame, text="+", font=BUTTON_FONT, width=3,height=1, highlightthickness=0, command=lambda:operator_button("+"), bg=COLORS[2], fg=COLORS[3])
addition_button.grid(column=3, row=3)
#FifthLine(Bottom)
signchange_button = Button(button_frame, text="+/-", font=BUTTON_FONT, width=3,height=1, highlightthickness=0, command=signchange, bg=COLORS[3], fg=COLORS[0])
signchange_button.grid(column=0, row=4)
zero_button = Button(button_frame, text="0", font=BUTTON_FONT, width=3,height=1, highlightthickness=0, command=lambda:number_input("0"), bg=COLORS[3], fg=COLORS[0])
zero_button.grid(column=1, row=4)
point_button = Button(button_frame, text=".", font=BUTTON_FONT, width=3,height=1, highlightthickness=0, command=point, bg=COLORS[3], fg=COLORS[0])
point_button.grid(column=2, row=4)
equals_button = Button(button_frame, text="=", font=BUTTON_FONT, width=3,height=1, highlightthickness=0, command=equals, bg=COLORS[1], fg=COLORS[3])
equals_button.grid(column=3, row=4)

#### Bind keyboard  - Button input is preferred. Only some function keys are bound to the keyboard.
def backspace(event):    # It's created to handle the scenario where the entry widget loses focus.
    current = display_entry.get()
    focus = str(window.focus_get())        #TIP. tkinter focus_get() return your active widget name.
    if focus != ".!frame.!entry":
        if len(current) > 0:
            last_index = len(current) -1
            display_entry.delete(last_index, END)  
            
window.bind("<BackSpace>", backspace) 
window.bind("<Escape>", lambda event: clear())      #TIP. bind need 'event' argument. use lambda because it is very simple. 
window.bind("<Return>", lambda event: equals())


window.mainloop()

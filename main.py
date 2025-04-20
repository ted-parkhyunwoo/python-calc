from tkinter import *
from calc import calc
from adjust_formula import AdjustFormula

OPS = ["*", "/", "+", "-"]
BUTTON_FONT = "Courier", 25, "bold"
DISPLAY_FONT = "Courier", 14, "italic"
COLORS = ["#2C3333", "#395B64", "#A5C9CA", "#E7F6F2"]   #Color set from https://colorhunt.co/palette/2c3333395b64a5c9cae7f6f2
ALLOWED_CHARS =list("0123456789./-+*%()")
INPUT_LIMIT = 30    # user input length limit.

Last_Display = ""                  # 계산 기록 추가용 임시 변수: global로 업데이트됨.
Prepare_for_New_input = False      # this trigger will turn on True after calc. (for clear display if you click number.)


#### Inheritance functions ####

def check_safe_for_eval(user_input):        #Check unauthorized input because this code use eval(this is dangerous) function.
    for char in user_input:
        if char not in ALLOWED_CHARS:
            return False 
    return True

def find_last_ops_index(user_input):        # Used as an inheritance function
    last_ops_index = 0
    chars = list("/-+*&()")
    replace = list(user_input)
    for c in replace:
        if c in chars:
            if replace.index(c) > last_ops_index:
                last_ops_index = replace.index(c)
                replace[replace.index(c)] = "removed"
    return last_ops_index

def update_input_ready_status(func=False):  #first_input trigger switching method. 
    global Prepare_for_New_input   
    if func == True:
        Prepare_for_New_input = True
    else:
        Prepare_for_New_input = False 
        
def pop_last_invalid_ops() -> None:         # remove the last operator if the last input is an operator. - Used as an inheritance function.
    current = display_entry.get()
    if len(current) > 0:
        if current[-1] in OPS:
            last_index = len(current) -1
            display_entry.delete(last_index, END)    
            
def invalid_formula_length(formula:str) -> bool:        # Check if the formula exceeds the allowed length limit
    if len(formula) > INPUT_LIMIT: return True
    return False

def error_print(msg: str = "ERROR") -> None:    # Display a message in the entry, disable the button, and restore it after 3 seconds.    
    def disable_button(): equals_button.config(bg="red", state=DISABLED)
    def restore_button(): equals_button.config(bg=COLORS[1], fg=COLORS[3], state=NORMAL)
    def clear_display(): display_entry.delete(0, END)
    
    disable_button()
    clear_display()
    display_entry.insert(0, msg)
    
    window.after(3000, lambda: (restore_button(), clear_display())) # windows에 전달할 함수가 복수라면 램다를 사용

# 정밀도 보정함수 : 25-04-20
def adjust_precision(result: float) -> float:    
    if result == int(result): result = int(result)      # 정수로 변환 가능한 경우 정수로 변환
    else: result = round(result, 13)                    # 소수점 이하 13자리까지 반올림

    if abs(result - int(round(result))) < 0.000_000_000_001:    
        result = int(round(result))                 # 매우 작은 오차 보정 (결과값이 정수에 가까운 경우 정수로 변환)
    return result                
                
                
#### Button functions ####

## Number (0~9) and Operators (*, /, +, -, %) ##
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
    pop_last_invalid_ops()
    update_input_ready_status()
    display_entry.insert(END, operator)
    
    
## Function keys    (., C, +-, (), =) ##
def point():    # '.' Button
    update_input_ready_status()
    display_entry.insert(END, ".")
def clear():    # 'C' Button
    update_input_ready_status()
    display_entry.delete(0, END)

# signchange() function turns the input into negative or positive based on various conditions. 
# The content isn't really important. I just kept debugging until it worked as wished.    
def signchange():       # '+-' Button.
    update_input_ready_status()
    current = display_entry.get()
    if current == "" or current == '0': return      # DEBUG: clicked with empty or 0   (25-04-20)
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
def parentheses():      # '( )' Bottn.
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
def equals():       # '=' Button.
    
    #! TODO : str 리턴식으로 바꿀 것을 검토. : equals()함수에도 쓰이지만, operator_button() 에서도 쓰여서 아래 AdjustFormula모듈 첨가에 어려움을 겪는중.
    pop_last_invalid_ops()   # remove incorrect operators before calculation. ('1+3-=' > '1+3=')
    user_formula:str = AdjustFormula(display_entry.get()).get_standard_fix()        # adjust_formula class화 (다양한 수식 오류 보정) 25-04-21
    
    if invalid_formula_length(user_formula):            # 수식길이제한 예외처리: check formula is valid length
        window.after(0, lambda: error_print(f"OUT OF RANGE({len(user_formula)}/{INPUT_LIMIT})"))
        return
                  
    # Try make Result
    user_formula_result:float = 0.0            # init user_formula_result.
    
    #! IMPORTANT TODO: 잘못된 에러처리 검토. 잘못된 입력은 check_safe_for_eval에서 실패해야되는데 왜 except로 넘어가는지 모르겠음
    try:
        if check_safe_for_eval(user_formula):  #! 원래 eval검사용이었으나, calc로 바뀌고 현재 식에 사용된 문자 유효성 검사로 사용중.
            user_formula_result = calc(user_formula)  # eval에서 calc모듈(직접작성) 으로 변경됨.
            user_formula_result = adjust_precision(user_formula_result)   # 정밀도 보정 함수 적용 (25-04-20)
            update_input_ready_status(True)  # This trigger will clear display if you click number after calc.
        else:
            raise ValueError("Unauthorized input")      #! TODO: raise 대신 except처럼 사용 고려.
        
    # Exception Handling -> quit equals.
    except:
        print(f"DEBUG: user_formula = {user_formula}, user_formula_result = {user_formula_result}")       #! TEST디버그출력
        window.after(0, lambda: error_print("ERROR"))
        return
        
    # Update result on display_entry : entry의 계산식을 제거하고, 결과로 업데이트.
    display_entry.delete(0, END)
    display_entry.insert(0, str(user_formula_result))
    
    
    #! TODO: 최근 계산결과 업데이트 기록기능:  함수화 고려.
    # Recent result labels Update (except input just "=")
    global Last_Display 
    if "=" in str(Last_Display):    # if Last_Display has result without fomula.
        Last_Display_result = Last_Display.split('=')[-1]   
    else:
        Last_Display_result = Last_Display  
        
    Last_Display_2 = Last_Display
    Last_Display = (f"{user_formula}={user_formula_result:,}")  #for update recent label.   #! last_questestion->current. 기능 삭제(%->/100) 25-04-21
        
    if len(Last_Display) >= 40:
        Last_Display = f"{user_formula_result:,}"   #Last_Display is just result if that is longer than 27 chars
        
    if Last_Display_result != user_formula:  
        if recent_label_1["text"] == "":
            recent_label_1.config(text=Last_Display)
        else:
            recent_label_2.config(text=Last_Display_2)
            recent_label_1.config(text=Last_Display)
            
            
#### UI ####
## Make Window ##
window = Tk()
window.config(padx=15, pady=15, bg=COLORS[0], highlightthickness=0)
window.title("Python calc")

#### DISPLAY FRAME ####
## Recent result label ##
display_frame = Frame(window)
display_frame.config(bg=COLORS[0], pady=15, highlightthickness=0)
display_frame.grid(column=0, row=0)
recent_label_2 = Label(display_frame, text="", bg=COLORS[0], fg=COLORS[3])
recent_label_2.grid(column=0, row=1, sticky='e')
recent_label_1 = Label(display_frame, text="", bg=COLORS[0], fg=COLORS[3])
recent_label_1.grid(column=0, row=2, sticky="e")
## Display Entry ##
display_entry = Entry(display_frame, text="Display", justify=RIGHT, width=24, highlightthickness=0, font=DISPLAY_FONT, bg=COLORS[2], fg=COLORS[0])
# display_entry.focus()
display_entry.grid(column=0, row=3)

#### BUTTONS FRAME ####
button_frame = Frame(window)
button_frame.grid(column=0,row=2)
## FirstLine(Top)         #Tip. Use lambda to delay function call until event (e.g., button press)
clear_button = Button(button_frame, text="C", font=BUTTON_FONT, width=3,height=1, highlightthickness=0, command=clear, bg=COLORS[1], fg=COLORS[3])
clear_button.grid(column=0, row=0)
parentheses_button = Button(button_frame, text="( )", font=BUTTON_FONT, width=3,height=1, highlightthickness=0, command=parentheses, bg=COLORS[2], fg=COLORS[3])
parentheses_button.grid(column=1, row=0)
percent_button = Button(button_frame, text="%", font=BUTTON_FONT, width=3,height=1, highlightthickness=0, command=lambda:operator_button("%"), bg=COLORS[2], fg=COLORS[3])
percent_button.grid(column=2, row=0)
division_button = Button(button_frame, text="/", font=BUTTON_FONT, width=3,height=1, highlightthickness=0, command=lambda:operator_button("/"), bg=COLORS[2], fg=COLORS[3])
division_button.grid(column=3, row=0)
## SecondLine
seven_button = Button(button_frame, text="7", font=BUTTON_FONT, width=3,height=1, highlightthickness=0, command=lambda:number_input("7"), bg=COLORS[3], fg=COLORS[0])
seven_button.grid(column=0, row=1)
eight_button = Button(button_frame, text="8", font=BUTTON_FONT, width=3,height=1, highlightthickness=0, command=lambda:number_input("8"), bg=COLORS[3], fg=COLORS[0])
eight_button.grid(column=1, row=1)
nine_button = Button(button_frame, text="9", font=BUTTON_FONT, width=3,height=1, highlightthickness=0, command=lambda:number_input("9"), bg=COLORS[3], fg=COLORS[0])
nine_button.grid(column=2, row=1)
multiplication_button = Button(button_frame, text="*", font=BUTTON_FONT, width=3,height=1, highlightthickness=0, command=lambda:operator_button("*"), bg=COLORS[2], fg=COLORS[3])
multiplication_button.grid(column=3, row=1)
## ThirdLine
four_button = Button(button_frame, text="4", font=BUTTON_FONT, width=3,height=1, highlightthickness=0, command=lambda:number_input("4"), bg=COLORS[3], fg=COLORS[0])
four_button.grid(column=0, row=2)
five_button = Button(button_frame, text="5", font=BUTTON_FONT, width=3,height=1, highlightthickness=0, command=lambda:number_input("5"), bg=COLORS[3], fg=COLORS[0])
five_button.grid(column=1, row=2)
six_button = Button(button_frame, text="6", font=BUTTON_FONT, width=3,height=1, highlightthickness=0, command=lambda:number_input("6"), bg=COLORS[3], fg=COLORS[0])
six_button.grid(column=2, row=2)
subtraction_button = Button(button_frame, text="-", font=BUTTON_FONT, width=3,height=1, highlightthickness=0, command=lambda:operator_button("-"), bg=COLORS[2], fg=COLORS[3])
subtraction_button.grid(column=3, row=2)
## FourthLine
one_button = Button(button_frame, text="1", font=BUTTON_FONT, width=3,height=1, highlightthickness=0, command=lambda:number_input("1"), bg=COLORS[3], fg=COLORS[0])
one_button.grid(column=0, row=3)
two_button = Button(button_frame, text="2", font=BUTTON_FONT, width=3,height=1, highlightthickness=0, command=lambda:number_input("2"), bg=COLORS[3], fg=COLORS[0])
two_button.grid(column=1, row=3)
three_button = Button(button_frame, text="3", font=BUTTON_FONT, width=3,height=1, highlightthickness=0, command=lambda:number_input("3"), bg=COLORS[3], fg=COLORS[0])
three_button.grid(column=2, row=3)
addition_button = Button(button_frame, text="+", font=BUTTON_FONT, width=3,height=1, highlightthickness=0, command=lambda:operator_button("+"), bg=COLORS[2], fg=COLORS[3])
addition_button.grid(column=3, row=3)
## FifthLine(Bottom)
signchange_button = Button(button_frame, text="+/-", font=BUTTON_FONT, width=3,height=1, highlightthickness=0, command=signchange, bg=COLORS[3], fg=COLORS[0])
signchange_button.grid(column=0, row=4)
zero_button = Button(button_frame, text="0", font=BUTTON_FONT, width=3,height=1, highlightthickness=0, command=lambda:number_input("0"), bg=COLORS[3], fg=COLORS[0])
zero_button.grid(column=1, row=4)
point_button = Button(button_frame, text=".", font=BUTTON_FONT, width=3,height=1, highlightthickness=0, command=point, bg=COLORS[3], fg=COLORS[0])
point_button.grid(column=2, row=4)
equals_button = Button(button_frame, text="=", font=BUTTON_FONT, width=3,height=1, highlightthickness=0, command=equals, bg=COLORS[1], fg=COLORS[3])
equals_button.grid(column=3, row=4)

#### Bind keyboard  - Button input is preferred. Only some function keys are bound to the keyboard. ####
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
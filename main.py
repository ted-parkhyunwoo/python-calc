from tkinter import *
from calc import calc


OPS = ["*", "/", "+", "-"]
BUTTON_FONT = "Courier", 25, "bold"
DISPLAY_FONT = "Courier", 14, "italic"
COLORS = ["#2C3333", "#395B64", "#A5C9CA", "#E7F6F2"]   #Color set from https://colorhunt.co/palette/2c3333395b64a5c9cae7f6f2
ALLOWED_CHARS =list("0123456789./-+*%()")

Last_Display = ""
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
        
def del_operator():     # remove the last operator if the last input is an operator. - Used as an inheritance function.
    current = display_entry.get()
    if len(current) > 0:
        if current[-1] in OPS:
            last_index = len(current) -1
            display_entry.delete(last_index, END)    
            
            
#! TEST: ERROR MESSAGE CONTROL.  : 25-04-05
def error_print(msg: str = "ERROR"):
    def restore_button():  # 버튼 색상 및 상태 복구 함수
        equals_button.config(bg=COLORS[1], fg=COLORS[3], state=NORMAL)
        
    def clear_display():
        display_entry.delete(0, END)
        restore_button()      
    
    equals_button.config(bg="red", state=DISABLED)  # 버튼을 일시적으로 red로 설정
    display_entry.delete(0, END)
    display_entry.insert(0, msg)
    
    # 3초 후 색상과 상태를 복원
    window.after(1500, restore_button)
    window.after(1500, clear_display) 
                
                
#### Button functions.

# Number (0~9) and Operators (*, /, +, -, %)  
def insert_multiplication():   # Auto insert "*" after ")" - Used as an inheritance function
    current = display_entry.get()
    if current != "":
        if current[-1] == ")":
            display_entry.insert(END, "*")
            
def number_input(num):
    insert_multiplication() 
    if Prepare_for_New_input == True:
        display_entry.delete(0, END)      
    update_input_ready_status()    #Trigger make False.
    display_entry.insert(END, num)
    
def operator_button(operator):
    del_operator()
    update_input_ready_status()
    display_entry.insert(END, operator)
    
    
# Function keys

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
            
def parentheses():              # Auto Open/Closing
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

#! CHECK SYNTEX. Update: 25-04-02
def check_syntax(formula: str) -> str:
    # "(*"를 "(1*"로 교체
    if "(*" in formula:
        formula = formula.replace("(*", "(1*")
    
    # "%" 뒤에 "*"가 오도록 처리
    if "%" in formula:
        result = []
        for i, char in enumerate(formula):
            result.append(char)
            if char == "%" and i + 1 < len(formula) and formula[i + 1] not in OPS + [")"]:
                result.append("*")  # "%" 뒤에 "*" 추가
        formula = "".join(result)
    
    #! 버튼 대신 키보드 입력문제.
    # 숫자와 괄호 사이에 "*" 추가
    i = 0
    while i < len(formula) - 1:
        # 숫자가 "(" 앞에 오는 경우
        if formula[i].isdigit() and formula[i + 1] == "(":
            formula = formula[:i + 1] + "*" + formula[i + 1:]
            i += 1
        # ")" 뒤에 숫자가 오는 경우
        elif formula[i] == ")" and formula[i + 1].isdigit():
            formula = formula[:i + 1] + "*" + formula[i + 1:]
            i += 1
        i += 1
    
    return formula

def equals():
    
    del_operator()   # remove incorrect operators before calculation. ('1+3-=' > '1+3=')
    
    #! DEBUG. The commented-out code is planned for removal. Update: 25-04-02
    # current = display_entry.get()   # Making 'current' variable from display_entry
    current = check_syntax(display_entry.get())
    
    #! TEST: input length limit : 25-04-05
    limit = 30
    if len(current) > limit:
        window.after(0, lambda: error_print(f"OUT OF RANGE({len(current)}/{limit})")) 
        return

    if current == "":   # Empty result input
        current = '0'
        
    # Auto parenthesis closing
    left = current.count("(")
    right = current.count(")")
    if left > right:
        for _ in range(left-right):
            current += ")"

    # Replace "/ 100" instead of "%"
    last_questestion = current  # maintain "%" on recent label
    if "%" in current:
        for _ in range(current.count("%")):
            current = current.replace("%", "/100")
            
    # Try make Result
    try:
        if check_safe_for_eval(current):     # Check Unauthorized input
            #~ TODO. eval 사용 하고 있으나, 역폴란드 후위표기법 변환 후 연산할 수 있도록 처리할 것.
            #! eval 대신 calc 모듈을 사용함.
            #! TODO. eval을 calc로 바꾸면서 첨삭할 부분 있는지 체크.(어차피 직접 string을 연산해도 입력자료의 유효성검사는 필요해서 일단 킵.)
            result = calc(current)       
            # Float make int ('6.0' -> '6')
            if result == int(result):
                result = int(result)
                
            # Rounding and adjusting the operation result
            result = round(result, 13) 
            #### IMPORTANT!
            # Without using round,' 1.2 * 3 = 3.6' would not be accurate but rather '3.59999999...' on python.
            # Using round, multiplying the result of '6/11' by '11' again does not give '6' but outputs '6.000000000005' instead.
            
            # When the error of the result is less than '.000000000001', adjust by truncating.
            if abs(result - int(round(result))) < 0.000_000_000_001:
                result = int(round(result))
            
            update_input_ready_status(True) # This trigger will clear display if you click number after calc.
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

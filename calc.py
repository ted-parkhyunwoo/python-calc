# Declaration of constants required for replace.
SIMPLIFY_OPS:dict = {"+-": "-", "++": "+", "-+": "-", "--": "+", "*+": "*", "/+": "/"}


################ Utility Functions ################

def has_parentheses(s: str) -> bool:
    """check string has parentheses.\n
    e.g : "(3*(2+ 1))" return True """
    
    for c in s:
        if c == '(' or c == ')':
            return True
    return False


def remove_space(s: str) -> str:
    """return removed 'space' in string.\n
    e.g : "3 + 1 *2" return "3+1*2" """
    
    return ''.join(s.split(' '))


def simple_calc(left: float, right: float, ops: str = '*') -> float:
    """calculating simple math problem has only 2 operands, operator."""
    
    if ops == '+': return left + right
    elif ops == '-': return left - right
    elif ops == '*':  return left * right
    elif ops == '/': return left / right
    else: raise ValueError(f"Unsupported operator: {ops}")
    

def simplify_ops(s: str) -> str:
    """make simplify operator likes "--" to "+" in string."""
    
    prev_s = None
    while s != prev_s:
        prev_s = s
        for op, simplified_op in SIMPLIFY_OPS.items():
            s = s.replace(op, simplified_op)
        if s[0] == '+': s = s[1:]       # DEBUG: remove char if string start with '+'
    return s


def clean_scientific_notation(f: float)-> str:
    """Converts a float to a string with fixed-point notation, avoiding scientific notation (e-** or e+**)."""
    
    formatted = "{:.15f}".format(f)
    return formatted


def calc_simple_token_list(l: list) -> float:
    """calc_simple_token_list work only [float, str(operator), float].\n
    e.g : [2.3, '*', 3.0] return 6.9"""
    
    leftoperand: float = l[0]
    ops: str = l[1]
    rightoperand: float = l[2]
    return simple_calc(leftoperand, rightoperand, ops)
    

''' NOTE: To improve calculation accuracy, the list contains both FLOAT and STRING data types.
's' need without space in string.  '''
def parsing_nums_and_ops(s: str) -> list:
    """Parsing elements from string. Make token list from string.\n
    e.g : "-3.0/-2*4" return [-3.0, '/', -2.0, '*', 4.0] """
    
    res = []
    current_num= ""
    if s[0] == '-':
        current_num += '-'
        s = s[1:]
    for i in range(len(s)):
        c = s[i]
        if c.isdigit() or (c == '.' and '.' not in current_num):  # DEBUG: Handling float number
            current_num += c
        elif c in "+-*/":
            if current_num:
                res.append(float(current_num))
                current_num = ""
            if c == '-' and (i > 0 and s[i - 1] in "+-*/"):
                current_num += c
            else:
                res.append(c)
    if current_num:
        res.append(float(current_num))
        
    return res     
     
     
################ Higher-Order Functions (has Dependencies.) ################

# DEPENDENCIES : Requires has_parentheses();
def get_priority_parent_index(s: str) -> list:
    """getting the parent index list to resolve priorities. find parentheses based on depth and priority, while considering if their content is negative. \n
    e.g: "-(3+2) + (2+1)"  return [0, 4, False]."""
    
    if not has_parentheses(s):
        return []
    left_index:int = -1
    right_index:int = -1
    
    for i in range(len(s)):
        c:str = s[i]
        if c == '(':
            left_index = i
        elif c == ')':
            right_index = i
            break
    is_negative:bool = False
    if left_index > 0:
        if s[left_index - 1] == '-': is_negative = True
    return [left_index, right_index, is_negative]


# DEPENDENCIES : Requires simplify_ops(), parsing_nums_and_ops().
def calc_priority_str(s: str) -> float:
    """resolves consecutive polynomial expressions in cases WITHOUT PARENTHESES, based on OPERATOR PRECEDENCE.\n
    e.g : "3+4/2.0+-2" return 3.0:float """
    
    s = simplify_ops(s)
    sl: list = parsing_nums_and_ops(s)         # Tokens list.
    def reduce_expression(ops_order):
        stack = []
        i = 0
        while i < len(sl):
            if isinstance(sl[i], str) and sl[i] in ops_order:
                left = stack.pop()
                operator = sl[i]
                right = sl[i + 1]
                stack.append(calc_simple_token_list([left, operator, right]))
                i += 1                 # Skip the next number since it's already used
            else:
                stack.append(sl[i])
            i += 1
        return stack
    
    for ops_group in ("*/", "+-"):
        sl = reduce_expression(ops_group)
    
    return sl[0]


# DEPENDENCIES: Requires has_parentheses(), get_priority_parent_index(), and calc_priority_str() to manage parentheses prioritization. clean_scientific_notation() and simplify_ops() are required for string simplification.
''' NOTE:
It can be used independently if you has requires functions, but it does not handle spaces. Use return remove_space(s) if you want to remove spaces. 
To prevent the frequent reuse of the remove_space(s) in multiple place, it currently returns only s.
'''
def calc_priority_parent(s: str) -> str:
    """Resolves parentheses based on their depth, prioritizing the innermost ones first. Continues in a while loop until no parentheses remain.\n
    e.g : "(3+2) * 4 * (2+ 3)" return "5.000000000000000 * 4* 5.000000000000000" """
    
    while has_parentheses(s):
        # Slice the expressions to the left and right of the selected parentheses.
        p_index:list = get_priority_parent_index(s)
        left_substr_index:int = p_index[0]
        is_negative_content:bool = p_index[2]
        
        if is_negative_content:                  # DEBUG: Handling negative content.
            left_substr_index -= 1
            
        left_substr = s[:left_substr_index]
        right_substr = s[p_index[1] + 1:]

        # Resolve the parentheses
        parentheses_result: float = calc_priority_str(s[p_index[0] + 1: p_index[1]])
        
        # update s (remove scientific notation, "--" replace "+", insert '-' if parentheses was negative.)
        p_str: str = clean_scientific_notation(parentheses_result) #! TEST: remove scientific notation.
        negative_char = "-" if is_negative_content else ""
        s = simplify_ops(f"{left_substr}{negative_char}{p_str}{right_substr}")   # replace
    return s


################ MAIN FUNCTION ################

def calc(expression: str) -> float:
    """
    DESC: calculating string -> float.\n
    INPUT: expression (str) - A mathematical expression as a string.\n
    OUTPUT: (float) - The result of the calculation.\n
    E.G: "3+2*(4-1)"  return 9.0
    """
    
    s = remove_space(expression)        # remove all ' ' in string.
    res: str = calc_priority_parent(s)  # remove all parentheses
    res = str(calc_priority_str(res))   # calculate *,/ and +,-
    return float(res)


################ TEST CASES ################

#test_cases = [
#    "-(-17)*(15/-46*-(77))/(64*-((((-68*28))))/65)",
#    "+17.0*25.108695652173914/1874.7076923076922",
#    "-(-28) + (-46 * 58 + (10)) + (-3 / ((((-37 * 42)))) / 23)"
#]
#
#for test_case in test_cases:
#    print(f"{test_case} = {calc(test_case)}")

# Declaration of constants required for replace.
# OPS:list = ['+', '-', '*', '/']           # NOTE: This code is scheduled for removal
SIMPLIFY_OPS:dict = {"+-": "-", "++": "+", "-+": "-", "--": "+", "*+": "*", "/+": "/"}


################ Utility Functions ################

def hasParentheses(s: str) -> bool:
    '''check string has parentheses.\n
    e.g : "(3*(2+ 1))" return True '''
    
    for c in s:
        if c == '(' or c == ')':
            return True
    return False


def removeSpace(s: str) -> str:
    '''return removed 'space' in string.\n
    e.g : "3 + 1 *2" return "3+1*2" '''
    
    return ''.join(s.split(' '))


def simpleCalc(left: float, right: float, ops: str = '*') -> float:
    '''calculating simple math problem has only 2 operands, operator.'''
    
    if ops == '+': return left + right
    elif ops == '-': return left - right
    elif ops == '*':  return left * right
    elif ops == '/': return left / right
    else: raise ValueError(f"Unsupported operator: {ops}")
    

def simplifyOps(s: str) -> str:
    '''make simplify operator likes "--" to "+" in string.'''
    
    prev_s = None
    while s != prev_s:
        prev_s = s
        for op, simplified_op in SIMPLIFY_OPS.items():
            s = s.replace(op, simplified_op)
        if s[0] == '+': s = s[1:]       # DEBUG: remove char if string start with '+'
    return s


def cleanScientificNotation(f: float)-> str:
    '''Converts a float to a string with fixed-point notation, avoiding scientific notation (e-** or e+**).'''
    
    formatted = "{:.15f}".format(f)
    return formatted


def calcSimpleTokenList(l: list) -> float:
    '''calcSimpleTokenList work only [float, str(operator), float].\n
    e.g : [2.3, '*', 3.0] return 6.9'''
    
    leftoperand: float = l[0]
    ops: str = l[1]
    rightoperand: float = l[2]
    return simpleCalc(leftoperand, rightoperand, ops)
    

''' NOTE: To improve calculation accuracy, the list contains both FLOAT and STRING data types.
's' need without space in string.  '''
def parsingNumsAndOps(s: str) -> list:
    '''Parsing elements from string. Make token list from string.\n
    e.g : "-3.0/-2*4" return [-3.0, '/', -2.0, '*', 4.0] '''
    
    res = []
    currentNum= ""
    if s[0] == '-':
        currentNum += '-'
        s = s[1:]
    for i in range(len(s)):
        c = s[i]
        if c.isdigit() or (c == '.' and '.' not in currentNum):  # DEBUG: Handling float number
            currentNum += c
        elif c in "+-*/":
            if currentNum:
                res.append(float(currentNum))
                currentNum = ""
            if c == '-' and (i > 0 and s[i - 1] in "+-*/"):
                currentNum += c
            else:
                res.append(c)
    if currentNum:
        res.append(float(currentNum))
        
    return res     
     
     
################ Higher-Order Functions (has Dependencies.) ################

# DEPENDENCIES : Requires hasParentheses();
def getPriorityParentIndex(s: str) -> list:
    '''getting the parent index list to resolve priorities. find parentheses based on depth and priority, while considering if their content is negative. \n
    e.g: "-(3+2) + (2+1)"  return [0, 4, False].'''
    
    if not hasParentheses(s):
        return []
    leftIndex:int = -1
    rightIndex:int = -1
    
    for i in range(len(s)):
        c:str = s[i]
        if c == '(':
            leftIndex = i
        elif c == ')':
            rightIndex = i
            break
    isNegative:bool = False
    if (leftIndex > 0):
        if (s[leftIndex - 1] == '-'): isNegative = True
    return [leftIndex, rightIndex, isNegative]


# DEPENDENCIES : Requires simplifyOps(), parsingNumsAndOps().
def calcPriorityStr(s: str) -> float:
    '''resolves consecutive polynomial expressions in cases WITHOUT PARENTHESES, based on OPERATOR PRECEDENCE.\n
    e.g : "3+4/2.0+-2" return 3.0:float '''
    
    s = simplifyOps(s)
    sl: list = parsingNumsAndOps(s)         # Tokens list.
    def reduce_expression(ops_order):
        stack = []
        i = 0
        while i < len(sl):
            if isinstance(sl[i], str) and sl[i] in ops_order:
                left = stack.pop()
                operator = sl[i]
                right = sl[i + 1]
                stack.append(calcSimpleTokenList([left, operator, right]))
                i += 1                 # Skip the next number since it's already used
            else:
                stack.append(sl[i])
            i += 1
        return stack
    
    for ops_group in ("*/", "+-"):
        sl = reduce_expression(ops_group)
    
    return sl[0]


# DEPENDENCIES: Requires hasParentheses(), getPriorityParentIndex(), and calcPriorityStr() to manage parentheses prioritization. cleanScientificNotation() and simplifyOps() are required for string simplification.
''' NOTE:
It can be used independently if you has requires functions, but it does not handle spaces. Use return removeSpace(s) if you want to remove spaces. 
To prevent the frequent reuse of the removeSpace(s) in multiple place, it currently returns only s.
'''
def calcPriorityParent(s: str) -> str:
    '''Resolves parentheses based on their depth, prioritizing the innermost ones first. Continues in a while loop until no parentheses remain.\n
    e.g : "(3+2) * 4 * (2+ 3)" return "5.000000000000000 * 4* 5.000000000000000" '''
    
    while hasParentheses(s):
        # Slice the expressions to the left and right of the selected parentheses.
        pIndex:list = getPriorityParentIndex(s)
        leftSubstrIndex:int = pIndex[0]
        isNegativeContent:bool = pIndex[2]
        
        if isNegativeContent:                  # DEBUG: Handling negative content.
            leftSubstrIndex -= 1
            
        leftSubstr = s[:leftSubstrIndex]
        rightSubstr = s[pIndex[1] + 1:]

        # Resolve the parentheses
        parenthesesResult: float = calcPriorityStr(s[pIndex[0] + 1 : pIndex[1]])
        
        # update s (remove scientific notation, "--" replace "+", insert '-' if parentheses was negative.)
        pStr: str = cleanScientificNotation(parenthesesResult) #! TEST: remove scientific notation.
        negativeChar = "-" if isNegativeContent else ""
        s = simplifyOps(f"{leftSubstr}{negativeChar}{pStr}{rightSubstr}")   # replace
    return s


################ MAIN FUNCTION ################

def calc(expression: str) -> float:
    '''
    DESC: calculating string -> float.\n
    INPUT: expression (str) - A mathematical expression as a string.\n
    OUTPUT: (float) - The result of the calculation.\n
    E.G: "3+2*(4-1)"  return 9.0
    '''
    
    s = removeSpace(expression)        # remove all ' ' in string.
    res: str = calcPriorityParent(s)   # remove all parentheses
    res = calcPriorityStr(res)         # calculate *,/ and +,-
    return res


################ TEST CASE ################

#test_cases = [
#    "-(-17)*(15/-46*-(77))/(64*-((((-68*28))))/65)",
#    "+17.0*25.108695652173914/1874.7076923076922",
#    "-(-28) + (-46 * 58 + (10)) + (-3 / ((((-37 * 42)))) / 23)"
#]
#
#for test_case in test_cases:
#    print(f"{test_case} = {calc(test_case)}")

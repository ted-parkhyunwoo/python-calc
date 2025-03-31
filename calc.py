OPS:list = ['+', '-', '*', '/']
SIMPLIFY_OPS:dict = {"+-": "-", "++": "+", "-+": "-", "--": "+", "*+": "*", "/+": "/"}

################ Utility Functions ################

# check string has parentheses.   e.g: "(3*(2+ 1))" return True
def hasParentheses(s: str) -> bool:
    for c in s:
        if c == '(' or c == ')':
            return True
    return False


# return removed 'space' in string.  e.g: "3 + 1 *2" return "3+1*2"
def removeSpace(s: str) -> str:
    return ''.join(s.split(' '))


# calculating simple math problem has only 2 operands, operator.
def simpleCalc(left: float, right: float, ops: str = '*') -> float:
    if ops == '+': return left + right
    elif ops == '-': return left - right
    elif ops == '*':  return left * right
    elif ops == '/': return left / right
    else: raise ValueError(f"Unsupported operator: {ops}")
    

# make simplify operator likes "--" to "+" in string.
def simplifyOps(s: str) -> str:
    prev_s = None
    while s != prev_s:
        prev_s = s
        for op, simplified_op in SIMPLIFY_OPS.items():
            s = s.replace(op, simplified_op)
            
        # DEBUG: remove char if string start with '+'
        if s[0] == '+': s = s[1:]
    return s


# Converts a float to a string with fixed-point notation, avoiding scientific notation (e-** or e+**).
def cleanScientificNotation(f: float)-> str:
    formatted = "{:.15f}".format(f)
    return formatted


# calcSimpleTokenList work only [float, str(operator), float]. e.g: [2.3, '*', 3.0] return 6.9
def calcSimpleTokenList(l: list) -> float:
    leftoperand = l[0]
    ops = l[1]
    rightoperand = l[2]
    return simpleCalc(leftoperand, rightoperand, ops)
    

# parsing elements from string. Make token list from string. e.g: "-3.0/-2*4" return [-3.0, '/', -2.0, '*', 4.0]
#! IMPORTANT: To improve calculation accuracy, the list contains both FLOAT and STRING data types.
#! IMPORTANT: 's' need without space. 
def parsingNumsAndOps(s: str) -> list:
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
     
     
################ Higher-Order Functions ################
     
     
# getting the parent index list to resolve priorities. e.g: "-(3+2) + (2+1)"  return [0, 4, False].
# find parentheses based on depth and priority, while considering if their content is negative.
def getPriorityParentIndex(s: str) -> list:
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


# resolves consecutive polynomial expressions in cases WITHOUT PARENTHESES, based on OPERATOR PRECEDENCE.
# e.g "3+4/2.0+-2" return 3.0:float
def calcPriorityStr(s: str) -> float:
    s = simplifyOps(s)
    sl: list = parsingNumsAndOps(s)         #! Tokens list.
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

    
# Resolves parentheses based on their depth, prioritizing the innermost ones first.
# Continues in a while loop until no parentheses remain.
def calcPriorityParent(s: str) -> str:
    while hasParentheses(s):
        pIndex:list = getPriorityParentIndex(s)
        leftSubstrIndex:int = pIndex[0]
        isNegativeContent:bool = pIndex[2]
        
        if isNegativeContent:                  # DEBUG: Handling negative content.
            leftSubstrIndex -= 1
            
        leftSubstr = s[:leftSubstrIndex]
        rightSubstr = s[pIndex[1] + 1:]

        # resolved parentheses.
        parenthesesResult: float = calcPriorityStr(s[pIndex[0] + 1 : pIndex[1]])
        
        #~ IMPORTANT TODO: Scientific notation style p have to change normal format. -> OK
        pStr: str = cleanScientificNotation(parenthesesResult) #! TEST: remove scientific notation.
        
        negativeChar = "-" if isNegativeContent else ""
        s = simplifyOps(f"{leftSubstr}{negativeChar}{pStr}{rightSubstr}")
    return s


################ MAIN FUNCTION ################
def calc(expression: str) -> float:
    s = removeSpace(expression)        # remove all ' ' in string.
    res: str = calcPriorityParent(s)   # remove all parentheses
    res = calcPriorityStr(res)         # calculate *,/ and +,-
    return res



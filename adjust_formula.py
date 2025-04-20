OPS = ["*", "/", "+", "-"]

#! TODO: 05 + 2 등 입력시 5 + 2 등으로 수정하는 기능 필요 (calc.py 단에서 수정해야할지, 숫자버튼에서 비어있는 상태 혹은 연산자 뒤 0이 선입력인지 고려할 것. 예: 비어있는상태 or 연산자, 괄호 뒤 등에 0 입력후 다른숫자 입력시: 05-> 5로 변경 필요)

#! 모든 멤버함수들은 생성자에서 초기화한 formula를 void함수처럼 수정하지만, str타입으로 formula를 리턴하기도 한다.
class AdjustFormula:
    def __init__(self, formula:str = ""):
        self.formula:str = formula
        
    def fix_missing_one(self) -> str:
        # replace "(*" to "(1*"
        if "(*" in self.formula:
            self.formula = self.formula.replace("(*", "(1*")
        return self.formula

    def insert_multipication_after_percent(self) -> str:
        # Ensure "*" is automatically inserted after "%" when necessary
        if "%" in self.formula:
            result = []
            for i, char in enumerate(self.formula):
                result.append(char)
                if char == "%" and i + 1 < len(self.formula) and self.formula[i + 1] not in OPS + [")"]:
                    result.append("*")  # "%" 뒤에 "*" 추가
            self.formula = "".join(result)
        return self.formula
    
    def fix_missing_parentheses_multipication(self) -> str:
        # Add "*" for implicit multiplication (keyboard input only) (e.g: 3(2+1) -> 3*(2+1),  (3+2)4 -> (3+2)*4)
        i = 0
        while i < len(self.formula) - 1:
            # Insert "*" before "(" if preceded by a number
            if self.formula[i].isdigit() and self.formula[i + 1] == "(":
                self.formula = self.formula[:i + 1] + "*" + self.formula[i + 1:]
                i += 1
            # Insert "*" after ")" if followed by a number
            elif self.formula[i] == ")" and self.formula[i + 1].isdigit():
                self.formula = self.formula[:i + 1] + "*" + self.formula[i + 1:]
                i += 1
            i += 1
        return self.formula
    
    def close_unmatched_parentheses(self) -> str:
        # Automatically close any unclosed parentheses in the formula
        openedParentheses = self.formula.count("(")
        closedParentheses = self.formula.count(")")
        if openedParentheses > closedParentheses:
            for _ in range(openedParentheses-closedParentheses):
                self.formula += ")"    
        return self.formula

    def handle_missing_formula(self) -> str:
        # If the formula is empty, set the result to '0' by default
        if self.formula == "": self.formula = '0'
        return self.formula

    def replace_percent_with_division(self) -> str:
        # Replace "/ 100" instead of "%"
        if "%" in self.formula:
            for _ in range(self.formula.count("%")):
                self.formula = self.formula.replace("%", "/100")  
        return self.formula

    # 종합 실행(수식보정 모든함수)
    def get_standard_fix(self) -> str:
        self.fix_missing_one()
        self.insert_multipication_after_percent()
        self.fix_missing_parentheses_multipication()
        self.close_unmatched_parentheses()
        self.handle_missing_formula()
        self.replace_percent_with_division()
        return self.formula
    
    

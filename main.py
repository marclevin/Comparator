# Entry point 
from comparator import *
import ast

def main():
    print("Hello World")
    # with open("./test_ast/isWeekend.py", "r") as f:
    #     ast1 = ast.parse(f.read())
    # with open("./test_ast/isWeekendBroken.py", "r") as f:
    #     ast2 = ast.parse(f.read())
    with open("./test_ast/twoSum.py", "r") as f:
        ast1 = ast.parse(f.read())
    with open("./test_ast/twoSumBroken.py", "r") as f:
        ast2 = ast.parse(f.read())
    for edit in diffAsts(ast2, ast1):
        print(edit.__repr__())
    

if __name__ == "__main__":
    main()
    

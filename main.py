# Entry point 
from comparator import *
import ast
from generate_message import *
import os

def main():
    # with open("./test_ast/isWeekend.py", "r") as f:
    #     ast1 = ast.parse(f.read())
    # with open("./test_ast/isWeekendBroken.py", "r") as f:
    #     ast2 = ast.parse(f.read())
    print("Welcome to AST-Hints Comparator")
    print("Problems are in /test_ast/ folder, a pair of a correct solution \"Foo.py\" and a broken solution \"FooBroken.py\" must exist to populate the list below")
    # Scan the dir test_ast for pairs of files, foo.py and fooBroken.py and list the correct solution filename
    files = {}
    # files should contain a number as a key and the filename as a value
    for file in os.listdir("./test_ast/"):
        if "Broken" not in file:
            files[len(files)] = {file, file[:-3]+"Broken.py"}
    while True:
        print("Enter the index of the problem to select for comparison:")
        print("Enter -1 to exit")
        for i in files:
            print(f"({i+1})", list(files[i])[0])
        problem = int(input())
        if (problem == -1):
            print("Exiting...")
            break
        problem -= 1
        if (int(problem) not in files):
            print("Invalid index")
            continue
        with open("./test_ast/"+list(files[int(problem)])[0], "r") as f:
            ast1 = ast.parse(f.read())
        with open("./test_ast/"+list(files[int(problem)])[1], "r") as f:
            ast2 = ast.parse(f.read())
            
        edits = diff_asts(ast1, ast2)
        print("\n")
        print(formatHints(edits,"next_step",ast2))
    

if __name__ == "__main__":
    main()
    

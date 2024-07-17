# Entry point
import json
from path_construction.comparator import *
import ast
from generate_message import *
import os
from ast2json import ast2json

from path_construction.state_creator import (
    applyChangeVectors,
    getNextState,
    optimizeGoal,
    updateChangeVectors,
)



def compare(studentCodeFile, solutionCodeFile):
    # Open /test_ast/twoSum.py and /test_ast/twoSumBroken.py
    with open(studentCodeFile, "r") as f:
        studentAST = f.read()
    with open(solutionCodeFile, "r") as f:
        solutionAST = f.read()
    solutionAST = ast.parse(solutionAST)
    studentAST = ast.parse(studentAST)
    astDifferences = diff_asts(solutionAST, studentAST)
    studentCodeState = CodeState(solutionAST)
    goalState = IntermediateState(tree=studentAST)
    # For each vector, set start to the original tree
    for changeVector in astDifferences:
        changeVector.start = solutionAST
    studentCodeState.goal = IntermediateState(tree=studentAST)
    something = optimizeGoal(studentCodeState, astDifferences)
    with open(".\\out\\output.txt", "a") as f:
        f.write(formatHints(studentCodeState.next.change_vectors, 1))
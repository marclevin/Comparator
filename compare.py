# Entry point

from comparison.path_construction.comparator import *
from comparison.path_construction.state_creator import get_next_state
from comparison.utils.generate_message import *


def compare_solutions(student_ast, solution_ast) -> str:
    student_code_state = CodeState(tree=ast.parse(student_ast), goal=IntermediateState(tree=ast.parse(solution_ast)))
    get_next_state(student_code_state)
    return formatHints(student_code_state.change_vectors, 1)

# compare(".\\data\\isWeekendBroken.py", ".\\data\\isWeekend.py")

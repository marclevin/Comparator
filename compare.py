# Entry point

import autopep8

from comparison.canonicalize.deanonymizer import DeanonymizeNames
from comparison.individualize import map_edit
from comparison.path_construction.comparator import *
from comparison.path_construction.state_creator import get_next_state, create_state
from comparison.utils.generate_message import *


def compare_solutions(student_code, solution_code, canonicalize) -> str:
    # First we must use pep8 to format the code to ensure we have a consistent format
    student_code = autopep8.fix_code(student_code)
    solution_code = autopep8.fix_code(solution_code)
    try:
        ast.parse(student_code)
        ast.parse(solution_code)
    except SyntaxError:
        return "Student code OR solution code has syntax errors."

    student_code_state = create_state(student_code, solution_code, canonicalize)

    get_next_state(student_code_state)
    if student_code_state.next is None:
        return "No hint available, student code is identical to the goal code."
    # Doing individualize step here.
    if canonicalize:
        deanonymizer = DeanonymizeNames(student_code_state.reverse_map)
        deanonymizer.visit(student_code_state.tree)
        deanonymizer = DeanonymizeNames(student_code_state.reverse_map)
        deanonymizer.visit(student_code_state.goal.tree)

    edit = map_edit(student_code_state.tree, ast.parse(student_code), student_code_state.change_vectors)
    return formatHints(edit, 2)


def test_compare():
    student_file = ".\\data\\multiFuncBroken.py"
    solution_file = ".\\data\\multiFunc.py"
    student_code = open(student_file, "r").read()
    solution_code = open(solution_file, "r").read()
    print("\n", compare_solutions(student_code, solution_code, True))


def test_compare_no_canonicalize():
    student_file = ".\\data\\twoSumBroken.py"
    solution_file = ".\\data\\twoSum.py"
    student_code = open(student_file, "r").read()
    solution_code = open(solution_file, "r").read()
    print("\n", compare_solutions(student_code, solution_code, False))


def validate_student_attempts(student_attempts: List[str], goal_code: str) -> float:
    """Compare student attempts to the goal code, returns a score based on the comparison of the student attempts."""
    # First we must use pep8 to format the code to ensure we have a consistent format
    goal_code_ast = autopep8.fix_code(goal_code)
    # We can now create the goal state
    goal_code_state = IntermediateState(tree=ast.parse(goal_code_ast))
    distances = {}
    for student_ast in student_attempts:
        student_ast = autopep8.fix_code(student_ast)
        student_code_state = CodeState(tree=ast.parse(student_ast), goal=goal_code_state)
        change_vectors = diff_asts(student_code_state, goal_code_state)
        ast_distance, _ = distance(student_code_state, goal_code_state, given_changes=change_vectors)
        distances[student_code_state] = ast_distance
    # Now we have the distances, this will be used for now. Desirability would be useful here too.
    return 1 - sum(distances.values()) / len(distances)

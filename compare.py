# Entry point

import autopep8

from comparison.canonicalize.deanonymizer import DeanonymizeNames
from comparison.path_construction.comparator import *
from comparison.path_construction.state_creator import get_next_state, create_state, desirability, \
    create_canonical_intermediate_state
from comparison.utils.generate_message import *


def compare_solutions(student_code, solution_code, canonicalize) -> str:
    # Format the code to ensure consistent format
    student_code = autopep8.fix_code(student_code)
    solution_code = autopep8.fix_code(solution_code)

    # Check for syntax errors
    try:
        ast.parse(student_code)
        ast.parse(solution_code)
    except SyntaxError:
        return "Student code OR solution code has syntax errors."

    # Create initial state and generate next state
    student_code_state = create_state(student_code, solution_code, canonicalize)
    get_next_state(student_code_state)

    if student_code_state.next is None:
        return "No hint available, student code is identical to the goal code."

    # De-anonymize if canonicalize is enabled
    if canonicalize:
        deanonymizer = DeanonymizeNames(reverse_map=student_code_state.reverse_map)
        deanonymizer.visit(student_code_state.tree)
        deanonymizer.visit(student_code_state.next.tree)

    return formatHints(student_code_state.change_vectors, 2)


def test_compare():
    student_file = ".\\data\\isWeekendBroken.py"
    solution_file = ".\\data\\isWeekend.py"
    student_code = open(student_file, "r").read()
    solution_code = open(solution_file, "r").read()
    print("\n", compare_solutions(student_code, solution_code, True))


def test_compare_no_canonicalize():
    student_file = ".\\data\\multiFuncBroken.py"
    solution_file = ".\\data\\multiFunc.py"
    student_code = open(student_file, "r").read()
    solution_code = open(solution_file, "r").read()
    print("\n", compare_solutions(student_code, solution_code, False))


def validate_student_attempts(student_attempts: List[str], goal_code: str, student_code: str) -> float:
    """Compare student attempts to the goal code, returns a score based on the comparison of the student attempts."""
    # First we must use pep8 to format the code to ensure we have a consistent format
    goal_code_ast = autopep8.fix_code(goal_code)
    student_code_ast = autopep8.fix_code(student_code)
    scores = {}
    for generative_attempt in student_attempts:
        try:
            generative_attempt = autopep8.fix_code(generative_attempt)
            student_code_state = create_canonical_intermediate_state(student_code_ast)
            generative_attempt_state = create_canonical_intermediate_state(generative_attempt)
            goal_code_state = create_canonical_intermediate_state(goal_code_ast)
            scores[student_code_state] = desirability(student_state=student_code_state,
                                                      candidate_state=generative_attempt_state,
                                                      goal_state=goal_code_state)
        except SyntaxError:
            log("Syntax error in one of the student attempts.")

    # Now we have the distances, this will be used for now. Desirability would be useful here too.
    return sum(scores.values()) / len(scores)

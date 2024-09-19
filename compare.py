# Entry point
from typing import Tuple

import autopep8

from comparison.canonicalize.deanonymizer import DeanonymizeNames
from comparison.path_construction.comparator import *
from comparison.path_construction.state_creator import get_next_state, create_state, desirability, \
    create_canonical_intermediate_state
from comparison.utils.generate_message import *

ephemeral_goal: str = ""


def compare_solutions(student_code, solution_code, canonicalize) -> str:
    # Format the code to ensure consistent format
    student_code = autopep8.fix_code(student_code)
    solution_code = autopep8.fix_code(solution_code)

    # Check for syntax errors
    try:
        ast.parse(student_code)
    except Exception as e:
        return "Your code has syntax errors. You need to fix them before we can provide hints."

    try:
        ast.parse(solution_code)
    except Exception as e:
        return "The solution code has syntax errors. Please contact your instructor."

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
    # We should check the change vectors next_tree here to ensure if something new is added, we use a reverse map to convert back to the original code in the goal_ast.
    global ephemeral_goal
    ephemeral_goal = print_function(student_code_state.next.tree)
    log(f"Ephemeral goal generated:\n{ephemeral_goal}", "goals")

    return formatHints(student_code_state.change_vectors, 2)


def compare_and_return_new_goal(student_code, solution_code, canonicalize) -> Tuple[str, str]:
    global ephemeral_goal
    hint = compare_solutions(student_code, solution_code, canonicalize)
    log(f"Hint generated:\n{hint}", "hint_generation")
    return hint, ephemeral_goal


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
    if len(scores) == 0:
        return 0
    return sum(scores.values()) / len(scores)

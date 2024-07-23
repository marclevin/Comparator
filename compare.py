# Entry point
import autopep8

from comparison.path_construction.comparator import *
from comparison.path_construction.state_creator import get_next_state
from comparison.utils.generate_message import *


def compare_solutions(student_ast, solution_ast) -> str:
    # First we must use pep8 to format the code to ensure we have a consistent format
    student_ast = autopep8.fix_code(student_ast)
    solution_ast = autopep8.fix_code(solution_ast)
    # Maybe we should consider type erasure here?
    student_code_state = CodeState(tree=ast.parse(student_ast),
                                   goal=IntermediateState(tree=ast.parse(solution_ast)))
    get_next_state(student_code_state)
    return formatHints(student_code_state.change_vectors, 1)


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


def test_compare():
    student_solution = open(
        'C:\\Users\\marcl\\OneDrive\\Desktop\\University\\AST-Hints\\Comparator\\problems/p1/student_code.py', 'r')
    correct_solution = open(
        'C:\\Users\\marcl\\OneDrive\\Desktop\\University\\AST-Hints\\Comparator\\problems/p1/goal_code.py', 'r')
    print(compare_solutions(student_solution.read(), correct_solution.read()))

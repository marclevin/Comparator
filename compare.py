# Entry point
from typing import Tuple, Dict

import autopep8

from comparison.canonicalize import get_canonical_form
from comparison.path_construction.comparator import *
from comparison.path_construction.state_creator import get_next_state
from comparison.utils.generate_message import *
from individualize import map_edit


def compare_solutions(student_code, solution_code) -> str:
    # First we must use pep8 to format the code to ensure we have a consistent format
    student_code = autopep8.fix_code(student_code)
    solution_code = autopep8.fix_code(solution_code)
    try:
        ast.parse(student_code)
        ast.parse(solution_code)
    except SyntaxError:
        return "Student code OR solution code has syntax errors."

    student_code_state = create_state(student_code, solution_code)

    get_next_state(student_code_state)
    if student_code_state.next is None:
        return "No hint available, student code is identical to the goal code."
    # Doing individualize step here.
    edit = map_edit(student_code_state.tree, ast.parse(student_code), student_code_state.change_vectors)
    return formatHints(edit, 2)


# compare(".\\data\\isWeekendBroken.py", ".\\data\\isWeekend.py")

def create_state(student_code: str, goal_code: str) -> CodeState:
    student_code_state = CodeState(tree=ast.parse(student_code))
    goal_code_state = IntermediateState(tree=ast.parse(goal_code))
    # Canonicalize
    # Student imports & names
    student_imports, student_names, student_args = collect_attributes(student_code_state)
    student_code_state = get_canonical_form(student_code_state, given_names=student_names, imports=student_imports,
                                            arg_types=student_args)
    # Goal imports & names
    goal_imports, goal_names, goal_args = collect_attributes(goal_code_state)
    goal_code_state = get_canonical_form(goal_code_state, given_names=goal_names, imports=goal_imports,
                                         arg_types=goal_args)
    student_code_state.goal = goal_code_state
    return student_code_state


def collect_attributes(given_ast) -> Tuple[List[ast.AST], List[str], Dict[str, None]]:
    args = given_ast.tree.body[0].args.args
    args = {arg.arg: None for arg in args}
    import_names = get_all_imports(given_ast) + get_all_imports(given_ast)
    inp = import_names + (list(args.keys()) if type(args) is dict else [])
    given_names = [str(x) for x in inp]
    imports = get_all_import_statements(given_ast) + get_all_import_statements(given_ast)
    return imports, given_names, args


def test_compare():
    student_file = ".\\data\\twoSumBroken.py"
    solution_file = ".\\data\\twoSum.py"
    student_code = open(student_file, "r").read()
    solution_code = open(solution_file, "r").read()
    print("\n", compare_solutions(student_code, solution_code))


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

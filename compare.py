# Entry point

import autopep8

from comparison.canonicalize import getCanonicalForm
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
    # Get the args from the AST

    args = student_code_state.tree.body[0].args.args
    args = {arg.arg: None for arg in args}
    given_code = ast.parse(student_ast)
    import_names = getAllImports(student_code_state.tree) + getAllImports(given_code)
    inp = import_names + (list(args.keys()) if type(args) is dict else [])
    given_names = [str(x) for x in inp]
    imports = getAllImportStatements(student_code_state.tree) + getAllImportStatements(given_code)
    student_code_state = getCanonicalForm(student_code_state, given_names, imports)

    # Do the same thing for the solution code
    solution_code_state = student_code_state.goal
    args = solution_code_state.tree.body[0].args.args
    args = {arg.arg: None for arg in args}
    given_code = ast.parse(solution_ast)
    import_names = getAllImports(solution_code_state.tree) + getAllImports(given_code)
    inp = import_names + (list(args.keys()) if type(args) is dict else [])
    given_names = [str(x) for x in inp]
    imports = getAllImportStatements(solution_code_state.tree) + getAllImportStatements(given_code)
    solution_code_state = getCanonicalForm(solution_code_state, given_names, imports)

    print("\n", print_function(student_code_state.goal.tree))
    print("\n", print_function(student_code_state.tree))

    get_next_state(student_code_state)
    # Doing individualize step here.
    # edit = map_edit(student_code_state.tree, original_tree, student_code_state.change_vectors)

    # return formatHints(edit, 2)
    return formatHints(student_code_state.change_vectors, 2)


# compare(".\\data\\isWeekendBroken.py", ".\\data\\isWeekend.py")

def prepare_code(student_code_state, student_ast) -> CodeState:
    args = student_code_state.tree.body[0].args.args
    args = {arg.arg: None for arg in args}
    given_code = ast.parse(student_ast)
    import_names = getAllImports(student_code_state.tree) + getAllImports(given_code)
    inp = import_names + (list(args.keys()) if type(args) is dict else [])
    given_names = [str(x) for x in inp]
    imports = getAllImportStatements(student_code_state.tree) + getAllImportStatements(given_code)

    student_code_state = getCanonicalForm(student_code_state, given_names, imports)
    return student_code_state


def test_compare():
    student_file = ".\\data\\twoSumBroken.py"
    solution_file = ".\\data\\twoSum.py"
    student_code = open(student_file, "r").read()
    solution_code = open(solution_file, "r").read()
    print(compare_solutions(student_code, solution_code))


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

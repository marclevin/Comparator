import uuid

from .transformations import *

id_counter = 0


def give_ids(node):
    global id_counter
    if isinstance(node, ast.AST):
        if type(node) in [ast.Load, ast.Store, ast.Del, ast.AugLoad, ast.AugStore, ast.Param]:
            return  # skip these
        node.global_id = uuid.uuid1()
        id_counter += 1
        for field in node.__getattribute__("_fields"):
            if hasattr(node, field):
                child = getattr(node, field)
            else:
                continue
            if type(child) is list:
                for i in range(len(child)):
                    # Get rid of aliased items
                    if hasattr(child[i], "global_id"):
                        child[i] = copy.deepcopy(child[i])
                    give_ids(child[i])
            else:
                # Get rid of aliased items
                if hasattr(child, "global_id"):
                    child = copy.deepcopy(child)
                    setattr(node, field, child)
                give_ids(child)


def get_canonical_form(student_state, given_names=None, arg_types=None, imports=None):
    student_state.tree = deepcopy(student_state.tree)  # no shallow copying! We need to leave the old tree alone

    give_ids(student_state.tree)
    if imports is None:
        imports = []

    transformation_list = [
        constantFolding,

        cleanupEquals,
        cleanupBoolOps,
        cleanupRanges,
        cleanupSlices,
        cleanupTypes,
        cleanupNegations,

        conditionalRedundancy,
        combineConditionals,
        collapseConditionals,

        copyPropagation,
        orderCommutativeOperations,
        deMorganize,

        deadCodeRemoval
    ]
    # student_state.tree = propagate_metadata(student_state.tree, arg_types, {}, [0])
    student_state.tree = simplify(student_state.tree)
    student_state.tree = anonymizeNames(student_state.tree, given_names, imports)
    old_tree = None
    # Get the name of the main function in the student's code
    main_function_name = None
    for item in student_state.tree.body:
        if type(item) is ast.FunctionDef:
            main_function_name = item.name
            break
    while compare_trees(old_tree, student_state.tree, check_equality=True) != 0:
        old_tree = deepcopy(student_state.tree)
        helperFolding(student_state.tree, main_function_name, imports)
        for transformation in transformation_list:
            student_state.tree = transformation(student_state.tree)  # modify in place
    student_state.code = print_function(student_state.tree)
    return student_state

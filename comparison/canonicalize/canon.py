import uuid

from comparison.canonicalize.ConditionalRedundancyTransformer import ConditionalRedundancyTransformer
from comparison.canonicalize.ConstantFoldingTransformer import ConstantFoldingTransformer
from comparison.canonicalize.DeadCodeEliminationTransformer import DeadCodeEliminationTransformer
from comparison.canonicalize.anonymizer import AnonymizeNames
from comparison.canonicalize.deMorganizeTransformer import DeMorganizeTransformer
from comparison.canonicalize.transformations import *

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


def get_canonical_form(student_state, given_names=None, imports=None):
    # student_state.tree = deepcopy(student_state.tree)  # no shallow copying! We need to leave the old tree alone

    if given_names is None:
        given_names = {}
    if imports is None:
        imports = []
    give_ids(student_state.tree)
    transformations = [ConstantFoldingTransformer(), DeadCodeEliminationTransformer(), DeMorganizeTransformer(),
                       ConditionalRedundancyTransformer()]

    student_state.tree = simplify(student_state.tree)
    anonymizer_instance = AnonymizeNames()

    for transformation in transformations:
        try:
            copy_of_tree = copy.deepcopy(student_state.tree)
            transformation.visit(copy_of_tree)
            student_state.tree = copy_of_tree
        except Exception as e:
            log(f"Error in applying transformation {transformation.__class__.__name__}: {e}", "canonicalize")

    temp_tree = anonymizer_instance.visit(student_state.tree)
    student_state.anonymized_code = ast.unparse(temp_tree)
    student_state.reverse_map = anonymizer_instance.reverse_name_map
    return student_state

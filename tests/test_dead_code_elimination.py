import ast
import unittest

from canonicalize.DeadCodeEliminationTransformer import DeadCodeEliminationTransformer


class TestDeadCodeEliminationTransformer(unittest.TestCase):
    def test_keeps_reachable_assignments(self):
        code = """
def foo():
    a = 1
    b = 2
    return a
    """
        tree = ast.parse(code)
        transformer = DeadCodeEliminationTransformer()
        transformed_tree = transformer.visit(tree)
        transformed_code = ast.unparse(transformed_tree)
        self.assertIn("a = 1", transformed_code)
        self.assertIn("b = 2", transformed_code)

    def test_removes_unreachable_assignments(self):
        code = """
def foo():
    a = 1
    return a
    b = 2
    """
        tree = ast.parse(code)
        transformer = DeadCodeEliminationTransformer()
        transformed_tree = transformer.visit(tree)
        transformed_code = ast.unparse(transformed_tree)
        self.assertIn("a = 1", transformed_code)
        self.assertNotIn("b = 2", transformed_code)

    def test_removes_unreachable_assignments_in_if(self):
        code = """
def foo():
    if True:
        a = 1
        return a
    else:
        b = 2
    """
        tree = ast.parse(code)
        transformer = DeadCodeEliminationTransformer()
        transformed_tree = transformer.visit(tree)
        transformed_code = ast.unparse(transformed_tree)
        self.assertIn("a = 1", transformed_code)
        self.assertNotIn("b = 2", transformed_code)

    def test_does_not_remove_unreachable_assignments_in_try(self):
        code = """
def foo():
    try:
        a = 1
        return a
    except:
        b = 2
    """
        tree = ast.parse(code)
        transformer = DeadCodeEliminationTransformer()
        transformed_tree = transformer.visit(tree)
        transformed_code = ast.unparse(transformed_tree)
        self.assertIn("a = 1", transformed_code)
        self.assertIn("b = 2", transformed_code)

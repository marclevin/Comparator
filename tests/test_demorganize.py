import ast
import unittest

from canonicalize.deMorganizeTransformer import DeMorganizeTransformer


class TestDeMorganizeTransformer(unittest.TestCase):
    def test_applies_demorgans_law_to_and(self):
        code = """
def foo():
    if not (a and b):
        return True
    return False
        """
        tree = ast.parse(code)
        transformer = DeMorganizeTransformer()
        transformed_tree = transformer.visit(tree)
        transformed_code = ast.unparse(transformed_tree)
        self.assertIn("if not a or not b", transformed_code)

    def test_applies_demorgans_law_to_or(self):
        code = """
def foo():
    if not (a or b):
        return True
    return False
        """
        tree = ast.parse(code)
        transformer = DeMorganizeTransformer()
        transformed_tree = transformer.visit(tree)
        transformed_code = ast.unparse(transformed_tree)
        self.assertIn("if not a and (not b)", transformed_code)

    def test_handles_nested_not_and(self):
        code = """
def foo():
    if not (a and (b and c)):
        return True
    return False
        """
        tree = ast.parse(code)
        transformer = DeMorganizeTransformer()
        transformed_tree = transformer.visit(tree)
        transformed_code = ast.unparse(transformed_tree)
        self.assertIn("if not a or (not b or not c)", transformed_code)

    def test_handles_nested_not_or(self):
        code = """
def foo():
    if not (a or (b or c)):
        return True
    return False
        """
        tree = ast.parse(code)
        transformer = DeMorganizeTransformer()
        transformed_tree = transformer.visit(tree)
        transformed_code = ast.unparse(transformed_tree)
        self.assertIn("if not a and (not b and (not c))", transformed_code)

    def test_does_not_change_non_demorgan_cases(self):
        code = """
def foo():
    if a and b:
        return True
    return False
        """
        tree = ast.parse(code)
        transformer = DeMorganizeTransformer()
        transformed_tree = transformer.visit(tree)
        transformed_code = ast.unparse(transformed_tree)
        self.assertIn("if a and b", transformed_code)

import ast
import unittest

from canonicalize.ConditionalRedundancyTransformer import ConditionalRedundancyTransformer


class TestConditionalRedundancy(unittest.TestCase):
    def test_handles_if_true_condition(self):
        code = """
if True:
    x = 1
else:
    x = 2
"""
        tree = ast.parse(code)
        transformer = ConditionalRedundancyTransformer()
        new_tree = transformer.visit(tree)
        new_code = ast.unparse(new_tree)
        self.assertIn("x = 1", new_code)
        self.assertNotIn("x = 2", new_code)

    def test_handles_if_false_condition(self):
        code = """
if False:
    x = 1
else:
    x = 2
"""
        tree = ast.parse(code)
        transformer = ConditionalRedundancyTransformer()
        new_tree = transformer.visit(tree)
        new_code = ast.unparse(new_tree)
        self.assertIn("x = 2", new_code)
        self.assertNotIn("x = 1", new_code)

    def test_handles_ifexp_true_condition(self):
        code = """
x = 1 if True else 2
"""
        tree = ast.parse(code)
        transformer = ConditionalRedundancyTransformer()
        new_tree = transformer.visit(tree)
        new_code = ast.unparse(new_tree)
        self.assertIn("x = 1", new_code)
        self.assertNotIn("x = 2", new_code)

    def test_handles_ifexp_false_condition(self):
        code = """
x = 1 if False else 2
"""
        tree = ast.parse(code)
        transformer = ConditionalRedundancyTransformer()
        new_tree = transformer.visit(tree)
        new_code = ast.unparse(new_tree)
        self.assertIn("x = 2", new_code)
        self.assertNotIn("x = 1", new_code)

    def test_handles_while_true_condition(self):
        code = """
while True:
    x = 1
"""
        tree = ast.parse(code)
        transformer = ConditionalRedundancyTransformer()
        new_tree = transformer.visit(tree)
        new_code = ast.unparse(new_tree)
        self.assertIn("x = 1", new_code)

    def test_handles_while_false_condition(self):
        code = """
while False:
    x = 1
"""
        tree = ast.parse(code)
        transformer = ConditionalRedundancyTransformer()
        new_tree = transformer.visit(tree)
        new_code = ast.unparse(new_tree)
        self.assertNotIn("x = 1", new_code)

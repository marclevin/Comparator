import ast
import unittest

from comparison.canonicalize.anonymizer import AnonymizeNames


class TestAnonymizeNames(unittest.TestCase):

    def test_anonymizes_function_names(self):
        code = """
def foo(p1, p2):
        v1 = p1 + p2
        return v1
    """
        tree = ast.parse(code)
        anonymizer = AnonymizeNames()
        anonymized_tree = anonymizer.visit(tree)
        anonymized_code = ast.unparse(anonymized_tree)
        self.assertIn("foo_function0", anonymized_code)
        self.assertIn("foo_param0", anonymized_code)
        self.assertIn("foo_param1", anonymized_code)
        self.assertIn("foo_variable0", anonymized_code)

    def test_anonymizes_variable_names(self):
        code = """
def foo(p1, p2):
        v1 = p1 + p2
        v2 = v1 * 2
        return v2
    """
        tree = ast.parse(code)
        anonymizer = AnonymizeNames()
        anonymized_tree = anonymizer.visit(tree)
        anonymized_code = ast.unparse(anonymized_tree)
        self.assertIn("foo_function0", anonymized_code)
        self.assertIn("foo_param0", anonymized_code)
        self.assertIn("foo_param1", anonymized_code)
        self.assertIn("foo_variable0", anonymized_code)
        self.assertIn("foo_variable1", anonymized_code)

    def test_handles_nested_functions(self):
        code = """
def foo(p1):
        def bar(p2):
            v1 = p1 + p2
            return v1
        return bar
    """
        tree = ast.parse(code)
        anonymizer = AnonymizeNames()
        anonymized_tree = anonymizer.visit(tree)
        anonymized_code = ast.unparse(anonymized_tree)
        self.assertIn("foo_function0", anonymized_code)
        self.assertIn("foo_param0", anonymized_code)
        self.assertIn("bar_function1", anonymized_code)
        self.assertIn("bar_param0", anonymized_code)
        self.assertIn("bar_variable0", anonymized_code)

    def test_handles_global_scope(self):
        code = """
v1 = 10
def foo(p1):
        v2 = p1 + v1
        return v2
    """
        tree = ast.parse(code)
        anonymizer = AnonymizeNames()
        anonymized_tree = anonymizer.visit(tree)
        anonymized_code = ast.unparse(anonymized_tree)
        self.assertIn("global_variable0", anonymized_code)
        self.assertIn("foo_function0", anonymized_code)
        self.assertIn("foo_param0", anonymized_code)
        self.assertIn("foo_variable0", anonymized_code)

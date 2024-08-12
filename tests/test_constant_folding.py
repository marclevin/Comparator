import ast
import unittest

from comparison.canonicalize.ConstantFoldingTransformer import ConstantFoldingTransformer


class TestConstantFoldingTransformer(unittest.TestCase):

    def test_binop_folding(self):
        code = "a = 1 + 2"
        tree = ast.parse(code)
        transformer = ConstantFoldingTransformer()
        transformed_tree = transformer.visit(tree)
        transformed_code = ast.unparse(transformed_tree)
        self.assertIn("a = 3", transformed_code)

    def test_boolop_folding(self):
        code = "a = True and False"
        tree = ast.parse(code)
        transformer = ConstantFoldingTransformer()
        transformed_tree = transformer.visit(tree)
        transformed_code = ast.unparse(transformed_tree)
        self.assertIn("a = False", transformed_code)

    def test_compare_folding(self):
        code = "a = 1 < 2"
        tree = ast.parse(code)
        transformer = ConstantFoldingTransformer()
        transformed_tree = transformer.visit(tree)
        transformed_code = ast.unparse(transformed_tree)
        self.assertIn("a = True", transformed_code)

    def test_ifexp_folding(self):
        code = "a = 1 if True else 2"
        tree = ast.parse(code)
        transformer = ConstantFoldingTransformer()
        transformed_tree = transformer.visit(tree)
        transformed_code = ast.unparse(transformed_tree)
        self.assertIn("a = 1", transformed_code)

    def test_call_folding(self):
        code = "a = len('abc')"
        tree = ast.parse(code)
        transformer = ConstantFoldingTransformer()
        transformed_tree = transformer.visit(tree)
        transformed_code = ast.unparse(transformed_tree)
        self.assertIn("a = 3", transformed_code)

    def test_folding_with_exception(self):
        code = "a = 1 + '2'"
        tree = ast.parse(code)
        transformer = ConstantFoldingTransformer()
        transformed_tree = transformer.visit(tree)
        transformed_code = ast.unparse(transformed_tree)
        self.assertIn("a = 1 + '2'", transformed_code)

    def test_folding_with_variable(self):
        code = "a = 1 + 2 + b"
        tree = ast.parse(code)
        transformer = ConstantFoldingTransformer()
        transformed_tree = transformer.visit(tree)
        transformed_code = ast.unparse(transformed_tree)
        self.assertIn("a = 3 + b", transformed_code)


if __name__ == "__main__":
    unittest.main()

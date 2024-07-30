# Testing file for comparison/comparator.py
import ast
# get_weight tests
import unittest

from comparison.utils.astTools import compareASTs, cmp, apply_to_children, occurs_in, count_occurrences


class TestComparator(unittest.TestCase):
    # compareASTs tests

    def test_compareASTs_return_zero_when_both_none(self):
        result = compareASTs(None, None)
        self.assertEqual(0, result)

    def test_compareASTs_should_return_negative_one_when_first_is_none(self):
        result = compareASTs(None, ast.parse("a = 1"))
        self.assertEqual(result, -1)

    def test_compareASTs_should_return_one_when_second_is_none(self):
        result = compareASTs(ast.parse("a = 1"), None)
        self.assertEqual(result, 1)

    def test_compareASTs_should_return_zero_for_identical_lists(self):
        list_a = [ast.parse("a = 1"), ast.parse("b = 2")]
        list_b = [ast.parse("a = 1"), ast.parse("b = 2")]
        result = compareASTs(list_a, list_b)
        self.assertEqual(result, 0)

    def test_compareASTs_should_return_non_zero_for_different_length_lists(self):
        list_a = [ast.parse("a = 1")]
        list_b = [ast.parse("a = 1"), ast.parse("b = 2")]
        result = compareASTs(list_a, list_b)
        self.assertNotEqual(result, 0)

    def test_compareASTs_should_return_non_zero_for_different_elements_in_lists(self):
        list_a = [ast.parse("a = 1"), ast.parse("b = 2")]
        list_b = [ast.parse("a = 1"), ast.parse("c = 3")]
        result = compareASTs(list_a, list_b)
        self.assertNotEqual(result, 0)

    # cmp tests
    def test_cmp_complex_numbers(self):
        self.assertEqual(cmp(complex(1, 1), complex(1, 1)), 0)
        self.assertEqual(cmp(complex(2, 1), complex(1, 1)), 1)
        self.assertEqual(cmp(complex(1, 1), complex(2, 1)), -1)

    def test_cmp_integers(self):
        self.assertEqual(cmp(1, 1), 0)
        self.assertEqual(cmp(2, 1), 1)
        self.assertEqual(cmp(1, 2), -1)

    def test_cmp_strings(self):
        self.assertEqual(cmp("a", "a"), 0)
        self.assertEqual(cmp("b", "a"), 1)
        self.assertEqual(cmp("a", "b"), -1)

    def test_cmp_mixed_types(self):
        self.assertEqual(cmp(1, "a"), -1)
        self.assertEqual(cmp("a", 1), 1)

    # apply_to_children tests
    def test_apply_to_children_none(self):
        result = apply_to_children(None, lambda x: x)
        self.assertIsNone(result)

    def test_apply_to_children_no_children(self):
        node = ast.Constant(value=1)
        result = apply_to_children(node, lambda x: x)
        self.assertEqual(result, node)

    def test_apply_to_children_non_list_children(self):
        node = ast.BinOp(left=ast.Constant(value=1), op=ast.Add(), right=ast.Constant(value=2))
        result = apply_to_children(node, lambda x: ast.Constant(value=0) if isinstance(x, ast.Constant) else x)
        self.assertIsInstance(result.left, ast.Constant)
        self.assertEqual(result.left.value, 0)
        self.assertIsInstance(result.right, ast.Constant)
        self.assertEqual(result.right.value, 0)

    def test_apply_to_children_list_children(self):
        node = ast.Module(body=[ast.Expr(value=ast.Constant(value=1)), ast.Expr(value=ast.Constant(value=2))],
                          type_ignores=[])
        result = apply_to_children(node, lambda x: ast.Constant(value=0) if isinstance(x, ast.Constant) else x)
        self.assertIsInstance(result.body[0].value, ast.Constant)
        self.assertEqual(result.body[0].value.value, 1)
        self.assertIsInstance(result.body[1].value, ast.Constant)
        self.assertEqual(result.body[1].value.value, 2)

    def test_apply_to_children_function_modifies_children(self):
        node = ast.BinOp(left=ast.Constant(value=1), op=ast.Add(), right=ast.Constant(value=2))
        result = apply_to_children(node,
                                   lambda x: ast.Constant(value=x.value + 1) if isinstance(x, ast.Constant) else x)
        self.assertIsInstance(result.left, ast.Constant)
        self.assertEqual(result.left.value, 2)
        self.assertIsInstance(result.right, ast.Constant)
        self.assertEqual(result.right.value, 3)

    def test_apply_to_children_function_returns_list(self):
        node = ast.Module(body=[ast.Expr(value=ast.Constant(value=1))], type_ignores=[])
        result = apply_to_children(node, lambda x: [x, x] if isinstance(x, ast.Expr) else x)
        self.assertEqual(len(result.body), 2)
        self.assertIsInstance(result.body[0], ast.Expr)
        self.assertIsInstance(result.body[1], ast.Expr)

    # occurs_in tests

    def test_occursIn_sub_not_ast(self):
        super_node = ast.parse("a = 1")
        self.assertFalse(occurs_in("not_ast", super_node))

    def test_occursIn_super_not_ast(self):
        sub_node = ast.parse("a = 1")
        self.assertFalse(occurs_in(sub_node, "not_ast"))

    def test_occursIn_exact_match(self):
        sub_node = ast.parse("a = 1")
        super_node = ast.parse("a = 1")
        self.assertTrue(occurs_in(sub_node, super_node))

    def test_occursIn_subtree(self):
        sub_node = ast.parse("a = 1")
        super_node = ast.parse("b = 2\na = 1")
        self.assertTrue(occurs_in(sub_node, super_node))

    def test_occursIn_not_subtree(self):
        sub_node = ast.parse("a = 1")
        super_node = ast.parse("b = 2")
        self.assertFalse(occurs_in(sub_node, super_node))

    def test_occursIn_statement_in_expression(self):
        sub_node = ast.parse("a = 1")
        super_node = ast.parse("a + 1")
        self.assertFalse(occurs_in(sub_node, super_node))

    # count_occurrences tests
    def test_count_occurrences_not_ast_node(self):
        self.assertEqual(count_occurrences("not_ast", ast.Assign), 0)

    def test_count_occurrences_list_of_ast_nodes(self):
        nodes = [ast.parse("a = 1"), ast.parse("b = 2")]
        self.assertEqual(count_occurrences(nodes, ast.Assign), 2)

    def test_count_occurrences_specific_ast_node_type(self):
        node = ast.parse("a = 1\nb = 2")
        self.assertEqual(count_occurrences(node, ast.Assign), 2)

    def test_count_occurrences_value_not_present(self):
        node = ast.parse("a = 1\nb = 2")
        self.assertEqual(count_occurrences(node, ast.If), 0)

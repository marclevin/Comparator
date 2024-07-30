# Testing file for comparison/comparator.py
import ast
# get_weight tests
import unittest

from comparison.utils.astTools import compareASTs, cmp, apply_to_children, occurs_in, count_occurrences, \
    gather_all_names, gather_all_variables, gather_all_parameters, gather_all_function_names


class TestAstTools(unittest.TestCase):
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

    # count_variables tests
    def test_count_variables_no_variables(self):
        node = ast.parse("1 + 1")
        self.assertEqual(count_occurrences(node, ast.Name), 0)

    def test_count_variables_single_variable(self):
        node = ast.parse("a = 1")
        self.assertEqual(count_occurrences(node, ast.Name), 1)

    def test_count_variables_multiple_variables(self):
        node = ast.parse("a = 1\nb = 2")
        self.assertEqual(count_occurrences(node, ast.Name), 2)

    def test_count_variables_nested_variables(self):
        node = ast.parse("a = 1\nb = a")
        self.assertEqual(count_occurrences(node, ast.Name), 3)

    def test_count_variables_no_variables_in_expression(self):
        node = ast.parse("1 + 1")
        self.assertEqual(count_occurrences(node, ast.Name), 0)

    # gather_all_names tests
    def test_gather_all_names_not_ast_node(self):
        self.assertEqual(gather_all_names("not_ast"), set())

    def test_gather_all_names_list_of_ast_nodes(self):
        nodes = [ast.parse("a = 1"), ast.parse("b = 2")]
        self.assertEqual(gather_all_names(nodes), {("a", None), ("b", None)})

    def test_gather_all_names_ast_node_with_names(self):
        node = ast.parse("a = 1\nb = 2")
        self.assertEqual(gather_all_names(node), {("a", None), ("b", None)})

    def test_gather_all_names_ast_node_with_originalId(self):
        node = ast.parse("a = 1\nb = 2")
        for n in ast.walk(node):
            if isinstance(n, ast.Name):
                n.originalId = f"orig_{n.id}"
        self.assertEqual(gather_all_names(node), {("a", "orig_a"), ("b", "orig_b")})

    def test_gather_all_names_ast_node_with_originalId_keep_orig_false(self):
        node = ast.parse("a = 1\nb = 2")
        for n in ast.walk(node):
            if isinstance(n, ast.Name):
                n.originalId = f"orig_{n.id}"
        self.assertEqual(gather_all_names(node, keep_orig=False), {("a", None), ("b", None)})

    # gather_all_variables tests
    def test_gather_all_variables_not_ast_node(self):
        self.assertEqual(gather_all_variables("not_ast"), set())

    def test_gather_all_variables_list_of_ast_nodes(self):
        nodes = [ast.parse("a = 1"), ast.parse("b = 2")]
        self.assertEqual(gather_all_variables(nodes), {("a", None), ("b", None)})

    def test_gather_all_variables_ast_node_with_names_and_args(self):
        node = ast.parse("def func(a):\n    b = 2")
        self.assertEqual(gather_all_variables(node), {("a", None), ("b", None)})

    def test_gather_all_variables_ast_node_with_originalId(self):
        node = ast.parse("a = 1\nb = 2")
        for n in ast.walk(node):
            if isinstance(n, ast.Name):
                n.originalId = f"orig_{n.id}"
        self.assertEqual(gather_all_variables(node), {("a", "orig_a"), ("b", "orig_b")})

    def test_gather_all_variables_ast_node_with_originalId_keep_orig_false(self):
        node = ast.parse("a = 1\nb = 2")
        for n in ast.walk(node):
            if isinstance(n, ast.Name):
                n.originalId = f"orig_{n.id}"
        self.assertEqual(gather_all_variables(node, keep_orig=False), {("a", None), ("b", None)})

    def test_gather_all_variables_ast_node_with_builtin_names(self):
        node = ast.parse("def func(len):\n    pass")
        self.assertEqual(gather_all_variables(node), set())

    def test_gather_all_variables_ast_node_with_dontChangeName(self):
        node = ast.parse("a = 1\nb = 2")
        for n in ast.walk(node):
            if isinstance(n, ast.Name) and n.id == "a":
                n.dontChangeName = True
        self.assertEqual(gather_all_variables(node), {("b", None)})

    # gather_all_parameters tests
    def test_gather_all_parameters_not_ast_node(self):
        self.assertEqual(gather_all_parameters("not_ast"), set())

    def test_gather_all_parameters_list_of_ast_nodes(self):
        nodes = [ast.parse("def func(a): pass"), ast.parse("def func(b): pass")]
        self.assertEqual(gather_all_parameters(nodes), {("a", None), ("b", None)})

    def test_gather_all_parameters_ast_node_with_parameters(self):
        node = ast.parse("def func(a, b): pass")
        self.assertEqual(gather_all_parameters(node), {("a", None), ("b", None)})

    def test_gather_all_parameters_ast_node_with_originalId(self):
        node = ast.parse("def func(a, b): pass")
        for n in ast.walk(node):
            if isinstance(n, ast.arg):
                n.originalId = f"orig_{n.arg}"
        self.assertEqual(gather_all_parameters(node), {("a", "orig_a"), ("b", "orig_b")})

    def test_gather_all_parameters_ast_node_with_originalId_keep_orig_false(self):
        node = ast.parse("def func(a, b): pass")
        for n in ast.walk(node):
            if isinstance(n, ast.arg):
                n.originalId = f"orig_{n.arg}"
        self.assertEqual(gather_all_parameters(node, keep_orig=False), {("a", None), ("b", None)})

    # gather_all_function tests
    def test_gather_all_helpers_not_ast_module(self):
        self.assertEqual(gather_all_function_names("not_ast"), set())

    def test_gather_all_helpers_ast_module_no_functions(self):
        node = ast.parse("a = 1")
        self.assertEqual(gather_all_function_names(node), set())

    def test_gather_all_helpers_ast_module_with_functions(self):
        node = ast.parse("def func1(): pass\ndef func2(): pass")
        self.assertEqual(gather_all_function_names(node), {("func1", None), ("func2", None)})

    def test_gather_all_helpers_ast_module_with_originalId(self):
        node = ast.parse("def func1(): pass\ndef func2(): pass")
        for n in ast.walk(node):
            if isinstance(n, ast.FunctionDef):
                n.originalId = f"orig_{n.name}"
        self.assertEqual(gather_all_function_names(node), {("func1", "orig_func1"), ("func2", "orig_func2")})

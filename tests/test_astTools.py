# Testing file for comparison/comparator.py
# get_weight tests
import unittest

from comparison.utils.astTools import *


class TestAstTools(unittest.TestCase):
    # compareASTs tests

    def test_compareASTs_return_zero_when_both_none(self):
        result = compare_trees(None, None)
        self.assertEqual(0, result)

    def test_compareASTs_should_return_negative_one_when_first_is_none(self):
        result = compare_trees(None, ast.parse("a = 1"))
        self.assertEqual(result, -1)

    def test_compareASTs_should_return_one_when_second_is_none(self):
        result = compare_trees(ast.parse("a = 1"), None)
        self.assertEqual(result, 1)

    def test_compareASTs_should_return_zero_for_identical_lists(self):
        list_a = [ast.parse("a = 1"), ast.parse("b = 2")]
        list_b = [ast.parse("a = 1"), ast.parse("b = 2")]
        result = compare_trees(list_a, list_b)
        self.assertEqual(result, 0)

    def test_compareASTs_should_return_non_zero_for_different_length_lists(self):
        list_a = [ast.parse("a = 1")]
        list_b = [ast.parse("a = 1"), ast.parse("b = 2")]
        result = compare_trees(list_a, list_b)
        self.assertNotEqual(result, 0)

    def test_compareASTs_should_return_non_zero_for_different_elements_in_lists(self):
        list_a = [ast.parse("a = 1"), ast.parse("b = 2")]
        list_b = [ast.parse("a = 1"), ast.parse("c = 3")]
        result = compare_trees(list_a, list_b)
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
    def test_gather_all_function_not_ast_module(self):
        self.assertEqual(gather_all_function_names("not_ast"), set())

    def test_gather_all_function_ast_module_no_functions(self):
        node = ast.parse("a = 1")
        self.assertEqual(gather_all_function_names(node), set())

    def test_gather_all_function_ast_module_with_functions(self):
        node = ast.parse("def func1(): pass\ndef func2(): pass")
        self.assertEqual(gather_all_function_names(node), {("func1", None), ("func2", None)})

    def test_gather_all_function_ast_module_with_originalId(self):
        node = ast.parse("def func1(): pass\ndef func2(): pass")
        for n in ast.walk(node):
            if isinstance(n, ast.FunctionDef):
                n.originalId = f"orig_{n.name}"
        self.assertEqual(gather_all_function_names(node), {("func1", "orig_func1"), ("func2", "orig_func2")})

    # gather_all_helpers tests
    def test_gather_all_helpers_not_ast_module(self):
        self.assertEqual(gather_all_helpers("not_ast", set()), set())

    def test_gather_all_helpers_ast_module_no_functions(self):
        node = ast.parse("a = 1")
        self.assertEqual(gather_all_helpers(node, set()), set())

    def test_gather_all_helpers_ast_module_with_functions(self):
        node = ast.parse("def func1(): pass\ndef func2(): pass")
        self.assertEqual(gather_all_helpers(node, set()), {("func1", None), ("func2", None)})

    def test_gather_all_helpers_ast_module_with_originalId(self):
        node = ast.parse("def func1(): pass\ndef func2(): pass")
        for n in ast.walk(node):
            if isinstance(n, ast.FunctionDef):
                n.originalId = f"orig_{n.name}"
        self.assertEqual(gather_all_helpers(node, set()), {("func1", "orig_func1"), ("func2", "orig_func2")})

    def test_gather_all_helpers_ast_module_with_dontChangeName(self):
        node = ast.parse("def func1(): pass\ndef func2(): pass")
        for n in ast.walk(node):
            if isinstance(n, ast.FunctionDef) and n.name == "func1":
                n.dontChangeName = True
        self.assertEqual(gather_all_helpers(node, set()), {("func2", None)})

    def test_gather_all_helpers_ast_module_with_restricted_names(self):
        node = ast.parse("def func1(): pass\ndef func2(): pass")
        self.assertEqual(gather_all_helpers(node, {"func1"}), {("func2", None)})

    # gather_assigned_vars tests
    def test_gather_assigned_vars_not_list(self):
        node = ast.parse("a = 1").body[0].targets[0]
        result = gather_assigned_vars(node)
        self.assertEqual(result, [node])

    def test_gather_assigned_vars_list_of_supported_types(self):
        node = ast.parse("a = 1\nb[0] = 2\nc.attr = 3")
        targets = [sub_node.targets[0] for sub_node in node.body]
        result = gather_assigned_vars(targets)
        self.assertEqual(result, targets)

    def test_gather_assigned_vars_list_of_tuples_and_lists(self):
        node = ast.parse("a, b = 1, 2\n[c, d] = [3, 4]")
        targets = [sub_node.targets[0] for sub_node in node.body]
        result = gather_assigned_vars(targets)
        expected = [elt for target in targets for elt in target.elts]
        self.assertEqual(result, expected)

    def test_gather_assigned_vars_unsupported_type(self):
        node = ast.parse("a = 1\nb = 2")
        targets = [sub_node.targets[0] for sub_node in node.body]
        targets.append(ast.Constant(value=3))
        with self.assertRaises(TypeError):
            gather_assigned_vars(targets)

    # get_all_imports tests
    def test_get_all_imports_not_ast(self):
        self.assertEqual(get_all_imports("not_ast"), [])

    def test_get_all_imports_ast_no_imports(self):
        node = ast.parse("a = 1")
        self.assertEqual(get_all_imports(node), [])

    def test_get_all_imports_ast_supported_import(self):
        node = ast.parse("import os")
        self.assertEqual(get_all_imports(node), ["os"])

    def test_get_all_imports_ast_unsupported_import(self):
        node = ast.parse("import turtle")
        with self.assertRaises(Exception) as context:
            get_all_imports(node)
        self.assertIn("Unsupported import name: turtle", str(context.exception))

    def test_get_all_imports_ast_supported_import_from(self):
        node = ast.parse("from os import path")
        self.assertEqual(get_all_imports(node), ["path"])

    def test_get_all_imports_ast_unsupported_import_from_module(self):
        node = ast.parse("from pygame import game")
        with self.assertRaises(Exception) as context:
            get_all_imports(node)
        self.assertIn("Unsupported import module: pygame", str(context.exception))

    def test_get_all_imports_ast_unsupported_import_from_function(self):
        node = ast.parse("from os import walk")
        with self.assertRaises(Exception) as context:
            get_all_imports(node)
        self.assertIn("Unsupported import name: walk", str(context.exception))

    # get_all_global_names tests

    def test_get_all_global_names_not_module(self):
        node = ast.parse("a = 1").body[0]
        self.assertEqual(get_all_global_names(node), [])

    def test_get_all_global_names_one_global_names(self):
        node = ast.parse("a = 1")
        self.assertEqual(get_all_global_names(node), ['a'])

    def test_get_all_global_names_no_global_names(self):
        node = ast.parse("if 1 + 1 == 3: a = 1")
        self.assertEqual(get_all_global_names(node), [])

    def test_get_all_global_names_function_and_class_definitions(self):
        node = ast.parse("def foo(): pass\nclass Bar: pass")
        self.assertEqual(get_all_global_names(node), ["foo", "Bar"])

    def test_get_all_global_names_variable_assignments(self):
        node = ast.parse("a = 1\nb, c = 2, 3\n[d, e] = [4, 5]")
        self.assertEqual(get_all_global_names(node), ["a", "b", "c", "d", "e"])

    def test_get_all_global_names_import_statements(self):
        node = ast.parse("import os\nfrom sys import path as sys_path")
        self.assertEqual(get_all_global_names(node), ["os", "sys_path"])

    # could_crash tests
    def test_could_crash_not_ast(self):
        self.assertFalse(could_crash("not_ast"))

    def test_could_crash_no_crash(self):
        node = ast.parse("a = 1")
        self.assertFalse(could_crash(node))

    def test_could_crash_try_except(self):
        node = ast.parse("try:\n    a = 1\nexcept:\n    pass")
        self.assertTrue(could_crash(node))

    def test_could_crash_function_def_conflicting_args(self):
        node = ast.parse("def foo(a, a): pass")
        self.assertTrue(could_crash(node))

    def test_could_crash_assign_non_name_target(self):
        node = ast.parse("(a, b) = (1, 2)")
        self.assertTrue(could_crash(node))

    def test_could_crash_import_unsupported_library(self):
        node = ast.parse("import random")
        self.assertTrue(could_crash(node))

    def test_could_crash_binop_divide_by_zero(self):
        node = ast.parse("a = 1 / 0")
        self.assertTrue(could_crash(node))

    def test_could_crash_unaryop_invalid_operand(self):
        node = ast.parse("a = ~1.0")
        self.assertTrue(could_crash(node))

    def test_could_crash_compare_invalid_comparison(self):
        node = ast.parse("a = 1 < 'string'")
        self.assertTrue(could_crash(node))

    def test_could_crash_call_unsupported_function(self):
        node = ast.parse("a = unsupported_function()")
        self.assertTrue(could_crash(node))

    def test_could_crash_subscript_invalid_index(self):
        node = ast.parse("a = 'string'[1.0]")
        self.assertFalse(could_crash(node))

    def test_could_crash_name_undefined_variable(self):
        node = ast.parse("a = undefined_var")
        # Set property randomVar to simulate undefined variable
        setattr(node.body[0].value, "randomVar", True)
        self.assertTrue(could_crash(node))

    def test_could_crash_slice_invalid_slice(self):
        node = ast.parse("a = [1, 2, 3][1.0:2]")
        self.assertTrue(could_crash(node))

    def test_could_crash_raise_statement(self):
        node = ast.parse("raise Exception('error')")
        self.assertTrue(could_crash(node))

    # eventual_type tests
    def test_eventual_type_basic_int(self):
        node = ast.parse("1").body[0].value
        self.assertEqual(eventual_type(node), int)

    def test_eventual_type_basic_float(self):
        node = ast.parse("1.0").body[0].value
        self.assertEqual(eventual_type(node), float)

    def test_eventual_type_basic_str(self):
        node = ast.parse("'string'").body[0].value
        self.assertEqual(eventual_type(node), str)

    def test_eventual_type_basic_bool(self):
        node = ast.parse("True").body[0].value
        self.assertEqual(eventual_type(node), bool)

    def test_eventual_type_basic_none(self):
        node = ast.parse("None").body[0].value
        self.assertEqual(eventual_type(node), type(None))

    def test_eventual_type_binop_add_int(self):
        node = ast.parse("1 + 2").body[0].value
        self.assertEqual(eventual_type(node), int)

    def test_eventual_type_binop_add_float(self):
        node = ast.parse("1.0 + 2").body[0].value
        self.assertEqual(eventual_type(node), float)

    def test_eventual_type_binop_mult_str(self):
        node = ast.parse("'a' * 3").body[0].value
        self.assertEqual(eventual_type(node), str)

    def test_eventual_type_unaryop_usub(self):
        node = ast.parse("-1").body[0].value
        self.assertEqual(eventual_type(node), int)

    def test_eventual_type_compare(self):
        node = ast.parse("1 < 2").body[0].value
        self.assertEqual(eventual_type(node), bool)

    def test_eventual_type_call_known_function(self):
        node = ast.parse("len('string')").body[0].value
        self.assertEqual(eventual_type(node), int)

    def test_eventual_type_ifexp_same_type(self):
        node = ast.parse("a if True else a").body[0].value
        self.assertEqual(eventual_type(node), None)  # Assuming 'a' is not defined

    def test_eventual_type_ifexp_different_type(self):
        node = ast.parse("1 if True else 'string'").body[0].value
        self.assertEqual(eventual_type(node), None)

    def test_eventual_type_list(self):
        node = ast.parse("[1, 2, 3]").body[0].value
        self.assertEqual(eventual_type(node), list)

    def test_eventual_type_dict(self):
        node = ast.parse("{'key': 'value'}").body[0].value
        self.assertEqual(eventual_type(node), dict)

    def test_eventual_type_set(self):
        node = ast.parse("{1, 2, 3}").body[0].value
        self.assertEqual(eventual_type(node), set)

    def test_eventual_type_tuple(self):
        node = ast.parse("(1, 2, 3)").body[0].value
        self.assertEqual(eventual_type(node), tuple)

    def test_eventual_type_subscript_list(self):
        node = ast.parse("[1, 2, 3][0]").body[0].value
        self.assertEqual(eventual_type(node), int)

    def test_eventual_type_subscript_str(self):
        node = ast.parse("'string'[0]").body[0].value
        self.assertEqual(eventual_type(node), str)

    # deepcopy_list tests
    def test_deepcopy_list_none(self):
        self.assertIsNone(deepcopy_list(None))

    def test_deepcopy_list_ast_node(self):
        node = ast.parse("a = 1")
        copied_node = deepcopy_list(node)
        setattr(copied_node, "type_ignores", [])
        self.assertEqual(ast.dump(node), ast.dump(copied_node))
        self.assertIsNot(node, copied_node)

    def test_deepcopy_list_non_list(self):
        with self.assertRaises(TypeError):
            deepcopy_list("not a list")

    def test_deepcopy_list_empty_list(self):
        self.assertEqual(deepcopy_list([]), [])

    def test_deepcopy_list_nested_list(self):
        nested_list = [[1, 2], [3, 4]]
        copied_list = deepcopy_list(nested_list)
        self.assertEqual(copied_list, nested_list)
        self.assertIsNot(nested_list, copied_list)
        for original, copied in zip(nested_list, copied_list):
            self.assertIsNot(original, copied)

    def test_deepcopy_list_mixed_types(self):
        mixed_list = [1, "string", [2, 3], {"key": "value"}]
        copied_list = deepcopy_list(mixed_list)
        self.assertEqual(copied_list, mixed_list)
        self.assertIsNot(mixed_list, copied_list)

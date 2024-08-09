# Testing file for comparison/comparator.py
import ast
import os
import os.path
# get_weight tests
import unittest

from comparison.path_construction.comparator import get_weight, match_lists, generate_move_pairs, find_move_vectors, \
    diff_lists, diff_asts, distance, get_changes_weight
from comparison.structures.ChangeVector import ChangeVector, SubVector, SuperVector, SwapVector, DeleteVector, \
    MoveVector, AddVector
from comparison.structures.State import CodeState, IntermediateState
from path_construction.state_creator import create_state


class TestComparator(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        project_root = os.path.dirname(os.path.abspath(__file__))
        resource_path = os.path.join(project_root, "resources")
        with open(resource_path + "/goal_code.py", "r") as file:
            goal_code = file.read()
        with open(resource_path + "/student_code.py", "r") as file:
            student_code = file.read()
        cls.student_code_state = create_state(student_code, goal_code, True)

    # get_weight tests
    def test_get_weight(self):
        weight = get_weight(self.student_code_state.tree)
        self.assertEqual(weight, 34)

    # match_lists tests
    def test_match_list_match_exact_lines(self):
        list_x = ["a", "b", "c"]
        list_y = ["a", "b", "c"]
        result = match_lists(list_x, list_y)
        expected = {0: 0, 1: 1, 2: 2}
        self.assertEqual(expected, result)

    def test_match_list_match_different_types(self):
        list_x = [1, "a", 2.0]
        list_y = [2.0, 1, "a"]
        result = match_lists(list_x, list_y)
        expected = {0: 2, 1: 0, 2: 1}
        self.assertEqual(expected, result)

    def test_match_list_no_matches(self):
        list_x = ["a", "b", "c"]
        list_y = ["d", "e", "f"]
        result = match_lists(list_x, list_y)
        expected = {0: 2, 1: 1, 2: 0}
        self.assertEqual(expected, result)

    # generate_move_pairs tests

    def test_generate_move_pairs_should_return_empty_for_empty_lists(self):
        result = generate_move_pairs([], [])
        self.assertEqual(result, [])

    def test_generate_move_pairs_should_return_empty_for_single_element_identical_lists(self):
        result = generate_move_pairs([1], [1])
        self.assertEqual(result, [])

    def test_generate_move_pairs_should_return_empty_for_single_element_different_lists(self):
        result = generate_move_pairs([1], [2])
        self.assertEqual(result, [])

    def test_generate_move_pairs_should_return_empty_for_identical_lists(self):
        result = generate_move_pairs([1, 2, 3], [1, 2, 3])
        self.assertEqual(result, [])

    def test_generate_move_pairs_should_return_swap_for_reversed_lists(self):
        result = generate_move_pairs([1, 2, 3], [3, 2, 1])
        self.assertEqual(result, [("swap", 1, 3)])

    def test_generate_move_pairs_should_return_moves_for_shifted_lists(self):
        result = generate_move_pairs([1, 2, 3], [3, 1, 2])
        self.assertEqual(result, [("move", 3)])

    def test_generate_move_pairs_should_return_combination_of_moves_and_swaps(self):
        result = generate_move_pairs([1, 2, 3, 4], [4, 3, 2, 1])
        self.assertEqual(result, [("swap", 1, 4), ("swap", 2, 3)])

    # find_move_vector tests

    def test_fmv_should_return_empty_for_empty_lists(self):
        result = find_move_vectors({}, [], [])
        self.assertEqual(result, [])

    def test_fmv_should_return_empty_for_identical_lists(self):
        map_set = {0: 0, 1: 1, 2: 2}
        result = find_move_vectors(map_set, [1, 2, 3], [1, 2, 3])
        self.assertEqual([], result)

    def test_fmv_should_return_moves_for_shifted_lists(self):
        map_set = match_lists([1, 2, 3], [3, 1, 2])
        result = find_move_vectors(map_set, [1, 2, 3], [3, 1, 2])
        expected = [MoveVector([-1], 2, 0)]
        self.assertEqual(expected.__repr__(), result.__repr__())

    def test_fmv_should_return_swaps_for_reversed_lists(self):
        map_set = match_lists([1, 2, 3], [3, 2, 1])
        result = find_move_vectors(map_set, [1, 2, 3], [3, 2, 1])
        expected = [SwapVector([-1], 0, 2)]
        self.assertEqual(expected.__repr__(), result.__repr__())

    def test_fmv_should_handle_added_and_deleted_lines(self):
        map_set = match_lists([1, 2, 3], [1, 2, 3, 5])
        result = find_move_vectors(map_set, [1, 2, 3], [1, 2, 3, 5])
        expected = AddVector([3], None, 5)
        self.assertEqual(expected.__repr__(), result[0].__repr__())
        map_set = match_lists([1, 2, 3, 5], [1, 2, 3])
        result = find_move_vectors(map_set, [1, 2, 3, 5], [1, 2, 3])
        expected = DeleteVector([3], 5, None)
        self.assertEqual(expected.__repr__(), result[0].__repr__())

    # diff_lists tests

    def test_diff_lists_empty(self):
        result = diff_lists([], [])
        self.assertEqual([], result)

    def test_diff_lists_identical(self):
        result = diff_lists([1, 2, 3], [1, 2, 3])
        self.assertEqual([], result)

    def test_diff_lists_additions(self):
        result = diff_lists([1, 2], [1, 2, 3])
        expected = AddVector([2], None, 3)
        self.assertEqual(expected.__repr__(), result[0].__repr__())

    def test_diff_lists_deletions(self):
        result = diff_lists([1, 2, 3], [1, 2])
        expected = DeleteVector([2], 3, None)
        self.assertIn(expected.__repr__(), result.__repr__())

    def test_diff_lists_moves(self):
        result = diff_lists([1, 2, 3], [3, 1, 2])
        expected = MoveVector([-1], 2, 0)
        self.assertEqual(expected.__repr__(), result[0].__repr__())

    def test_diff_lists_combination(self):
        result = diff_lists([1, 2, 3], [3, 4, 1])
        expected = [SwapVector([-1], 0, 2), ChangeVector([1], 2, 4)]
        self.assertEqual(expected.__repr__(), result.__repr__())

    # ast_diff tests
    def test_diff_asts_identical(self):
        ast_x = ast.parse("a = 1")
        ast_y = ast.parse("a = 1")
        result = diff_asts(ast_x, ast_y)
        self.assertEqual([], result)

    def test_diff_asts_different_node_types(self):
        ast_x = ast.parse("a = 1")
        ast_y = ast.parse("a = 'string'")
        result = diff_asts(ast_x, ast_y)
        self.assertTrue(any(isinstance(change, ChangeVector) for change in result))

    def test_diff_asts_different_field_values(self):
        ast_x = ast.parse("a = 1")
        ast_y = ast.parse("a = 2")
        result = diff_asts(ast_x, ast_y)
        self.assertTrue(any(isinstance(change, ChangeVector) for change in result))

    def test_diff_asts_lists_identical(self):
        list_x = [ast.parse("a = 1"), ast.parse("b = 2")]
        list_y = [ast.parse("a = 1"), ast.parse("b = 2")]
        result = diff_asts(list_x, list_y)
        self.assertEqual(result, [])

    def test_diff_asts_lists_different(self):
        list_x = [ast.parse("a = 1"), ast.parse("b = 2")]
        list_y = [ast.parse("a = 1"), ast.parse("c = 3")]
        result = diff_asts(list_x, list_y)
        self.assertTrue(any(isinstance(change, ChangeVector) for change in result))

    def test_diff_asts_primitive_identical(self):
        result = diff_asts(1, 1)
        self.assertEqual(result, [])

    def test_diff_asts_primitive_different(self):
        result = diff_asts(1, 2)
        self.assertTrue(any(isinstance(change, ChangeVector) for change in result))

    def test_diff_asts_occurs_in(self):
        ast_x = ast.parse("b = 2")
        ast_y = ast.parse("if a == 1:\n    b = 2")
        result = diff_asts(ast_x, ast_y)
        self.assertTrue(any(isinstance(change, SubVector) for change in result))

    def test_diff_asts_occurs_in_reverse(self):
        ast_x = ast.parse("if a == 1:\n    b = 2")
        ast_y = ast.parse("b = 2")
        result = diff_asts(ast_x, ast_y)
        self.assertTrue(any(isinstance(change, SuperVector) for change in result))

    # distance tests

    def test_distance_both_none(self):
        result = distance(None, None)
        self.assertEqual(1, result)

    def test_distance_identical_trees(self):
        tree = ast.parse("a = 1")
        state = CodeState(tree=tree, goal=IntermediateState(tree=tree))
        result = distance(state, state.goal)
        self.assertEqual((0, []), result)

    def test_distance_different_trees(self):
        state = CodeState(tree=ast.parse("a = 1"), goal=IntermediateState(tree=ast.parse("b = 2")))
        result = distance(state, state.goal)
        self.assertIsNotNone(result)
        dist, _ = result
        self.assertEqual(0.67, round(dist, 2))

    def test_distance_given_changes(self):
        state = CodeState(tree=ast.parse("a = 1"), goal=IntermediateState(tree=ast.parse("b = 2")))
        mock_change = ChangeVector([-1], 1, 2)
        result = distance(state, state.goal, given_changes=[mock_change])
        self.assertIsNotNone(result)
        dist, _ = result
        self.assertEqual(0.33, round(dist, 2))

    def test_distance_one_none(self):
        state = CodeState(tree=ast.parse("a = 1"), goal=IntermediateState(tree=ast.parse("b = 2")))
        result = distance(state, None)
        self.assertEqual(result, 1)

    def test_distance_force_reweight(self):
        state = CodeState(tree=ast.parse("a = 1"), goal=IntermediateState(tree=ast.parse("b = 2")))
        result = distance(state, state.goal, forceReweight=True)
        self.assertIsNotNone(result)
        dist, _ = result
        self.assertEqual(0.67, round(dist, 2))

    # get_changes_weight tests
    def test_get_changes_weight_no_changes(self):
        changes = []
        result = get_changes_weight(changes)
        self.assertEqual(result, 0)

    def test_get_changes_weight_add_vector(self):
        change = AddVector([-1], 0, 2)
        result = get_changes_weight([change])
        self.assertEqual(1, result)

    def test_get_changes_weight_delete_vector(self):
        change = DeleteVector([-1], 0, 2)
        result = get_changes_weight([change])
        self.assertEqual(1, result)

    def test_get_changes_weight_swap_vector(self):
        change = SwapVector([-1], 0, 2)
        result = get_changes_weight([change])
        self.assertEqual(2, result)

    def test_get_changes_weight_move_vector(self):
        change = MoveVector([-1], 0, 2)
        result = get_changes_weight([change])
        self.assertEqual(1, result)

    def test_get_changes_weight_sub_vector(self):
        change = SubVector([-1], 0, 2)
        result = get_changes_weight([change])
        self.assertEqual(0, result)

    def test_get_changes_weight_super_vector(self):
        change = SuperVector([-1], 2, 0)
        result = get_changes_weight([change])
        self.assertEqual(0, result)

    def test_get_changes_weight_mixed_changes(self):
        changes = [
            AddVector([-1], 0, 1),
            DeleteVector([-1], 2, 3),
            SwapVector([-1], 4, 5),
            MoveVector([-1], 6, 7),
            SubVector([-1], 8, 9),
            SuperVector([-1], 10, 11)
        ]
        result = get_changes_weight(changes)
        self.assertEqual(5, result)

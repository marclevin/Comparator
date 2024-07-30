# Testing file for comparison/comparator.py
import ast
import os
import os.path
# get_weight tests
import unittest
from unittest.mock import MagicMock, patch

from comparison.path_construction.comparator import get_weight, match_lists, generate_move_pairs, find_move_vectors, \
    diff_lists, diff_asts, distance, get_changes_weight
from comparison.structures.ChangeVector import ChangeVector, SubVector, SuperVector, SwapVector, DeleteVector, \
    MoveVector, AddVector
from comparison.structures.State import CodeState, IntermediateState


class TestComparator(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        project_root = os.path.dirname(os.path.abspath(__file__))
        resource_path = os.path.join(project_root, "resources")
        with open(resource_path + "/goal_code.py", "r") as file:
            goal_code = file.read()
        with open(resource_path + "/student_code.py", "r") as file:
            student_code = file.read()
        cls.student_code_state = CodeState(tree=ast.parse(student_code), goal=ast.parse(goal_code))
        cls.compareASTs = MagicMock()
        cls.distance = MagicMock()
        cls.log = MagicMock()
        cls.DeleteVector = MagicMock()
        cls.AddVector = MagicMock()
        cls.match_lists = MagicMock()
        cls.find_move_vectors = MagicMock()
        cls.diff_asts = MagicMock()
        cls.SwapVector = MagicMock()
        cls.MoveVector = MagicMock()
        cls.generate_move_pairs = MagicMock()

    # get_weight tests
    def test_get_weight(self):
        weight = get_weight(self.student_code_state.tree)
        self.assertEqual(weight, 36)

    # match_lists tests
    def test_match_list_match_exact_lines(self):
        list_x = ["a", "b", "c"]
        list_y = ["a", "b", "c"]
        self.compareASTs.side_effect = lambda x, y, check_equality: 0 if x == y else 1
        result = match_lists(list_x, list_y)
        expected = {0: 0, 1: 1, 2: 2}
        self.assertEqual(expected, result)

    def test_match_list_match_different_types(self):
        list_x = [1, "a", 2.0]
        list_y = [2.0, 1, "a"]
        self.compareASTs.side_effect = lambda x, y, check_equality: 0 if x == y else 1
        result = match_lists(list_x, list_y)
        expected = {0: 2, 1: 0, 2: 1}
        self.assertEqual(expected, result)

    def test_match_list_no_matches(self):
        list_x = ["a", "b", "c"]
        list_y = ["d", "e", "f"]
        self.compareASTs.side_effect = lambda x, y, check_equality: 0 if x == y else 1
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

    @patch('comparison.path_construction.comparator.generate_move_pairs')
    @patch('comparison.path_construction.comparator.MoveVector')
    @patch('comparison.path_construction.comparator.SwapVector')
    @patch('comparison.path_construction.comparator.log')
    def test_fmv_should_return_empty_for_empty_lists(self, mock_log, mock_swap_vector, mock_move_vector,
                                                     mock_generate_move_pairs):
        result = find_move_vectors({}, [], [], [], [])
        self.assertEqual(result, [])

    @patch('comparison.path_construction.comparator.generate_move_pairs')
    @patch('comparison.path_construction.comparator.MoveVector')
    @patch('comparison.path_construction.comparator.SwapVector')
    @patch('comparison.path_construction.comparator.log')
    def test_fmv_should_return_empty_for_identical_lists(self, mock_log, mock_swap_vector, mock_move_vector,
                                                         mock_generate_move_pairs):
        map_set = {0: 0, 1: 1, 2: 2}
        result = find_move_vectors(map_set, [1, 2, 3], [1, 2, 3], [], [])
        self.assertEqual(result, [])

    @patch('comparison.path_construction.comparator.generate_move_pairs')
    @patch('comparison.path_construction.comparator.MoveVector')
    @patch('comparison.path_construction.comparator.SwapVector')
    @patch('comparison.path_construction.comparator.log')
    def test_fmv_should_return_moves_for_shifted_lists(self, mock_log, mock_swap_vector, mock_move_vector,
                                                       mock_generate_move_pairs):
        map_set = {0: 2, 1: 0, 2: 1}
        mock_generate_move_pairs.return_value = [("move", 0), ("move", 1)]
        result = find_move_vectors(map_set, [1, 2, 3], [3, 1, 2], [], [])
        expected = [mock_move_vector([-1], 0, 2), mock_move_vector([-1], 1, 0)]
        self.assertEqual(result, expected)

    @patch('comparison.path_construction.comparator.generate_move_pairs')
    @patch('comparison.path_construction.comparator.MoveVector')
    @patch('comparison.path_construction.comparator.SwapVector')
    @patch('comparison.path_construction.comparator.log')
    def test_fmv_should_return_swaps_for_reversed_lists(self, mock_log, mock_swap_vector, mock_move_vector,
                                                        mock_generate_move_pairs):
        map_set = {0: 2, 1: 1, 2: 0}
        mock_generate_move_pairs.return_value = [("swap", 0, 2)]
        result = find_move_vectors(map_set, [1, 2, 3], [3, 2, 1], [], [])
        expected = [mock_swap_vector([-1], 0, 2)]
        self.assertEqual(result, expected)

    @patch('comparison.path_construction.comparator.generate_move_pairs')
    @patch('comparison.path_construction.comparator.MoveVector')
    @patch('comparison.path_construction.comparator.SwapVector')
    @patch('comparison.path_construction.comparator.log')
    def test_fmv_should_handle_added_and_deleted_lines(self, mock_log, mock_swap_vector, mock_move_vector,
                                                       mock_generate_move_pairs):
        map_set = {0: 2, 1: 0, 2: 1}
        mock_generate_move_pairs.return_value = [("move", 0), ("move", 1)]
        result = find_move_vectors(map_set, [1, 2, 3], [3, 1, 2], [1], [2])
        expected = []
        self.assertEqual(result, expected)

    # diff_lists tests
    @patch('comparison.path_construction.comparator.match_lists')
    @patch('comparison.path_construction.comparator.find_move_vectors')
    @patch('comparison.path_construction.comparator.diff_asts')
    @patch('comparison.path_construction.comparator.DeleteVector')
    @patch('comparison.path_construction.comparator.AddVector')
    def test_diff_lists_empty(self, mock_add_vector, mock_delete_vector, mock_diff_asts, mock_find_move_vectors,
                              mock_match_lists):
        mock_match_lists.return_value = {}
        result = diff_lists([], [])
        self.assertEqual(result, [])

    @patch('comparison.path_construction.comparator.match_lists')
    @patch('comparison.path_construction.comparator.find_move_vectors')
    @patch('comparison.path_construction.comparator.diff_asts')
    @patch('comparison.path_construction.comparator.DeleteVector')
    @patch('comparison.path_construction.comparator.AddVector')
    def test_diff_lists_identical(self, mock_add_vector, mock_delete_vector, mock_diff_asts, mock_find_move_vectors,
                                  mock_match_lists):
        mock_match_lists.return_value = {0: 0, 1: 1, 2: 2}
        mock_diff_asts.return_value = []
        result = diff_lists([1, 2, 3], [1, 2, 3])
        self.assertEqual(result, [])

    @patch('comparison.path_construction.comparator.match_lists')
    @patch('comparison.path_construction.comparator.find_move_vectors')
    @patch('comparison.path_construction.comparator.diff_asts')
    @patch('comparison.path_construction.comparator.DeleteVector')
    @patch('comparison.path_construction.comparator.AddVector')
    def test_diff_lists_additions(self, mock_add_vector, mock_delete_vector, mock_diff_asts, mock_find_move_vectors,
                                  mock_match_lists):
        mock_match_lists.return_value = {0: 0, 1: 1, 2: -1}
        mock_find_move_vectors.return_value = []
        mock_diff_asts.return_value = []
        mock_add_vector.side_effect = lambda path, old, new: f"Add({path}, {old}, {new})"
        result = diff_lists([1, 2], [1, 2, 3])
        self.assertIn("Add([2], None, 3)", result)

    @patch('comparison.path_construction.comparator.match_lists')
    @patch('comparison.path_construction.comparator.find_move_vectors')
    @patch('comparison.path_construction.comparator.diff_asts')
    @patch('comparison.path_construction.comparator.DeleteVector')
    @patch('comparison.path_construction.comparator.AddVector')
    def test_diff_lists_deletions(self, mock_add_vector, mock_delete_vector, mock_diff_asts, mock_find_move_vectors,
                                  mock_match_lists):
        mock_match_lists.return_value = {0: 0, 1: 1, -1: [2]}
        mock_find_move_vectors.return_value = []
        mock_diff_asts.return_value = []
        mock_add_vector.side_effect = lambda path, old, new: f"Add({path}, {old}, {new})"
        mock_delete_vector.side_effect = lambda path, old, new: f"Delete({path}, {old}, {new})"
        result = diff_lists([1, 2, 3], [1, 2])
        self.assertIn("Delete([2], 3, None)", result)

    @patch('comparison.path_construction.comparator.match_lists')
    @patch('comparison.path_construction.comparator.find_move_vectors')
    @patch('comparison.path_construction.comparator.diff_asts')
    @patch('comparison.path_construction.comparator.DeleteVector')
    @patch('comparison.path_construction.comparator.AddVector')
    def test_diff_lists_moves(self, mock_add_vector, mock_delete_vector, mock_diff_asts, mock_find_move_vectors,
                              mock_match_lists):
        mock_match_lists.return_value = {0: 2, 1: 0, 2: 1}
        mock_find_move_vectors.return_value = ["Move(0, 2)", "Move(1, 0)"]
        mock_diff_asts.return_value = []
        result = diff_lists([1, 2, 3], [3, 1, 2])
        self.assertIn("Move(0, 2)", result)
        self.assertIn("Move(1, 0)", result)

    @patch('comparison.path_construction.comparator.match_lists')
    @patch('comparison.path_construction.comparator.find_move_vectors')
    @patch('comparison.path_construction.comparator.diff_asts')
    @patch('comparison.path_construction.comparator.DeleteVector')
    @patch('comparison.path_construction.comparator.AddVector')
    def test_diff_lists_combination(self, mock_add_vector, mock_delete_vector, mock_diff_asts, mock_find_move_vectors,
                                    mock_match_lists):
        mock_match_lists.return_value = {0: 2, 1: -1, 2: 0, -1: [1]}
        mock_diff_asts.return_value = []
        mock_add_vector.side_effect = lambda path, old, new: f"Add({path}, {old}, {new})"
        mock_delete_vector.side_effect = lambda path, old, new: f"Delete({path}, {old}, {new})"
        mock_find_move_vectors.return_value = ["Move(0, 2)", "Move(2, 0)"]
        result = diff_lists([1, 2, 3], [3, 4, 1])
        self.assertIn("Add([1], None, 4)", result)
        self.assertIn("Delete([1], 2, None)", result)
        self.assertIn("Move(0, 2)", result)
        self.assertIn("Move(2, 0)", result)

    # ast_diff tests
    @patch('comparison.path_construction.comparator.built_in_name')
    def test_diff_asts_identical(self, mock_built_in_name):
        ast_x = ast.parse("a = 1")
        ast_y = ast.parse("a = 1")
        result = diff_asts(ast_x, ast_y)
        self.assertEqual(result, [])

    @patch('comparison.path_construction.comparator.built_in_name')
    def test_diff_asts_different_node_types(self, mock_built_in_name):
        ast_x = ast.parse("a = 1")
        ast_y = ast.parse("a = 'string'")
        result = diff_asts(ast_x, ast_y)
        self.assertTrue(any(isinstance(change, ChangeVector) for change in result))

    @patch('comparison.path_construction.comparator.built_in_name')
    def test_diff_asts_different_field_values(self, mock_built_in_name):
        ast_x = ast.parse("a = 1")
        ast_y = ast.parse("a = 2")
        result = diff_asts(ast_x, ast_y)
        self.assertTrue(any(isinstance(change, ChangeVector) for change in result))

    @patch('comparison.path_construction.comparator.diff_lists')
    def test_diff_asts_lists_identical(self, mock_diff_lists):
        list_x = [ast.parse("a = 1"), ast.parse("b = 2")]
        list_y = [ast.parse("a = 1"), ast.parse("b = 2")]
        mock_diff_lists.return_value = []
        result = diff_asts(list_x, list_y)
        self.assertEqual(result, [])

    @patch('comparison.path_construction.comparator.diff_lists')
    def test_diff_asts_lists_different(self, mock_diff_lists):
        list_x = [ast.parse("a = 1"), ast.parse("b = 2")]
        list_y = [ast.parse("a = 1"), ast.parse("c = 3")]
        mock_diff_lists.return_value = [ChangeVector([], list_x[1], list_y[1])]
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
    @patch('comparison.path_construction.comparator.get_weight')
    @patch('comparison.path_construction.comparator.get_changes')
    @patch('comparison.path_construction.comparator.get_changes_weight')
    def test_distance_both_none(self, mock_get_changes_weight, mock_get_changes, mock_get_weight):
        result = distance(None, None)
        self.assertEqual(result, 1)

    @patch('comparison.path_construction.comparator.get_weight')
    @patch('comparison.path_construction.comparator.get_changes')
    @patch('comparison.path_construction.comparator.get_changes_weight')
    def test_distance_identical_trees(self, mock_get_changes_weight, mock_get_changes, mock_get_weight):
        tree = ast.parse("a = 1")
        mock_get_weight.side_effect = [1, 1]
        mock_get_changes.return_value = ["change"]
        mock_get_changes_weight.return_value = 1
        state = CodeState(tree=tree, goal=IntermediateState(tree=tree))
        result = distance(state, state.goal)
        self.assertEqual(result, (0, []))

    @patch('comparison.path_construction.comparator.get_weight')
    @patch('comparison.path_construction.comparator.get_changes')
    @patch('comparison.path_construction.comparator.get_changes_weight')
    def test_distance_different_trees(self, mock_get_changes_weight, mock_get_changes, mock_get_weight):
        state = CodeState(tree=ast.parse("a = 1"), goal=IntermediateState(tree=ast.parse("b = 2")))
        mock_get_weight.side_effect = [1, 1]
        mock_get_changes.return_value = ["change"]
        mock_get_changes_weight.return_value = 1
        result = distance(state, state.goal)
        self.assertEqual(result, (1.0, ["change"]))

    @patch('comparison.path_construction.comparator.get_weight')
    @patch('comparison.path_construction.comparator.get_changes')
    @patch('comparison.path_construction.comparator.get_changes_weight')
    def test_distance_given_changes(self, mock_get_changes_weight, mock_get_changes, mock_get_weight):
        state = CodeState(tree=ast.parse("a = 1"), goal=IntermediateState(tree=ast.parse("b = 2")))
        mock_get_weight.side_effect = [1, 1]
        mock_get_changes.return_value = ["change"]
        mock_get_changes_weight.return_value = 1
        result = distance(state, state.goal, given_changes=["change"])
        self.assertEqual(result, (1.0, ["change"]))

    @patch('comparison.path_construction.comparator.get_weight')
    @patch('comparison.path_construction.comparator.get_changes')
    @patch('comparison.path_construction.comparator.get_changes_weight')
    def test_distance_one_none(self, mock_get_changes_weight, mock_get_changes, mock_get_weight):
        state = CodeState(tree=ast.parse("a = 1"), goal=IntermediateState(tree=ast.parse("b = 2")))
        result = distance(state, None)
        self.assertEqual(result, 1)

    @patch('comparison.path_construction.comparator.get_weight')
    @patch('comparison.path_construction.comparator.get_changes')
    @patch('comparison.path_construction.comparator.get_changes_weight')
    def test_distance_force_reweight(self, mock_get_changes_weight, mock_get_changes, mock_get_weight):
        state = CodeState(tree=ast.parse("a = 1"), goal=IntermediateState(tree=ast.parse("b = 2")))
        mock_get_weight.side_effect = [2, 3]
        mock_get_changes.return_value = ["change"]
        mock_get_changes_weight.return_value = 1
        result = distance(state, state.goal, forceReweight=True)
        self.assertEqual(result, (1.0 / 3, ["change"]))

    @patch('comparison.path_construction.comparator.get_weight')
    @patch('comparison.path_construction.comparator.get_changes')
    @patch('comparison.path_construction.comparator.get_changes_weight')
    def test_distance_ignore_variables(self, mock_get_changes_weight, mock_get_changes, mock_get_weight):
        state = CodeState(tree=ast.parse("a = 1"), goal=IntermediateState(tree=ast.parse("b = 2")))
        mock_get_weight.side_effect = [1, 1]
        mock_get_changes.return_value = ["change"]
        mock_get_changes_weight.return_value = 1
        result = distance(state, state.goal, ignoreVariables=True)
        self.assertEqual(result, (1.0, ["change"]))

    # get_changes_weight tests
    @patch('comparison.path_construction.comparator.get_weight')
    def test_no_changes(self, mock_get_weight):
        changes = []
        result = get_changes_weight(changes)
        self.assertEqual(result, 0)

    @patch('comparison.path_construction.comparator.get_weight')
    def test_add_vector(self, mock_get_weight):
        change = AddVector([], None, MagicMock())
        mock_get_weight.return_value = 5
        result = get_changes_weight([change])
        self.assertEqual(result, 5)

    @patch('comparison.path_construction.comparator.get_weight')
    def test_delete_vector(self, mock_get_weight):
        change = DeleteVector([], MagicMock(), None)
        mock_get_weight.return_value = 3
        result = get_changes_weight([change])
        self.assertEqual(result, 3)

    def test_swap_vector(self):
        change = SwapVector([], None, None)
        result = get_changes_weight([change])
        self.assertEqual(result, 2)

    def test_move_vector(self):
        change = MoveVector([], None, None)
        result = get_changes_weight([change])
        self.assertEqual(result, 1)

    @patch('comparison.path_construction.comparator.get_weight')
    def test_sub_vector(self, mock_get_weight):
        change = SubVector([], MagicMock(), MagicMock())
        mock_get_weight.side_effect = [7, 4]
        result = get_changes_weight([change])
        self.assertEqual(result, 3)

    @patch('comparison.path_construction.comparator.get_weight')
    def test_super_vector(self, mock_get_weight):
        change = SuperVector([], MagicMock(), MagicMock())
        mock_get_weight.side_effect = [4, 7]
        result = get_changes_weight([change])
        self.assertEqual(result, 3)

    @patch('comparison.path_construction.comparator.get_weight')
    def test_mixed_changes(self, mock_get_weight):
        changes = [
            AddVector([], None, MagicMock()),
            DeleteVector([], MagicMock(), None),
            SwapVector([], None, None),
            MoveVector([], None, None),
            SubVector([], MagicMock(), MagicMock()),
            SuperVector([], MagicMock(), MagicMock())
        ]
        mock_get_weight.side_effect = [5, 3, 7, 4, 4, 7]
        result = get_changes_weight(changes)
        self.assertEqual(result, 17)

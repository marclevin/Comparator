import ast
import unittest

from comparison.path_construction.state_creator import map_differences


class TestStateCreator(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pass

    # map_differences test
    def test_map_differences_no_changes(self):
        node_a = ast.parse("a = 1")
        node_b = ast.parse("a = 1")
        self.assertEqual(map_differences(node_a, node_b), {"start": {}})

    def test_map_differences_one_change(self):
        node_a = ast.parse("a = 1")
        node_b = ast.parse("a = 2")
        self.assertEqual(map_differences(node_a, node_b), {'start': {'body': {0: {'value': {}}, 'len': 1, 'pos': [0]}}})

    def test_map_differences_multiple_changes(self):
        node_a = ast.parse("a = 1\nb = 2")
        node_b = ast.parse("a = 2\nb = 1")
        self.assertEqual(map_differences(node_a, node_b),
                         {'moved': [0, 1],
                          'start': {'body': {0: {'targets': {0: {}, 'len': 1, 'pos': [0]}},
                                             1: {'targets': {0: {}, 'len': 1, 'pos': [0]}},
                                             'len': 2,
                                             'pos': [1, 0]}}}
                         )

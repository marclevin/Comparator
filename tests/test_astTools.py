# Testing file for comparison/comparator.py
import ast
# get_weight tests
import unittest

from comparison.utils.astTools import compareASTs


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

    #

import os
import unittest

from compare import compare_solutions
from path_construction.state_creator import create_state


class TestSamples(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Get the ../data directory using the OS
        project_root = os.path.dirname(os.path.abspath(__file__))
        cls.resource_path = os.path.join(project_root, "resources")

    def test_multi_func_step_0(self):
        broken_solution = os.path.join(self.resource_path, "multi_func_steps", 'multi_func0.py')
        solution = os.path.join(self.resource_path, 'multi_func_solution.py')
        broken_code = open(broken_solution, "r").read()
        solution_code = open(solution, "r").read()
        hint = compare_solutions(broken_code, solution_code, True)
        expected_hint = ("At line 46, column 46 replace 'something else' with ' ' in the right side of the binary "
                         "operation\n")
        self.assertEqual(hint, expected_hint)

    def test_multi_func_step_1(self):
        broken_solution = os.path.join(self.resource_path, "multi_func_steps", 'multi_func1.py')
        solution = os.path.join(self.resource_path, 'multi_func_solution.py')
        broken_code = open(broken_solution, "r").read()
        solution_code = open(solution, "r").read()
        hint = compare_solutions(broken_code, solution_code, True)
        expected_hint = "At line 13, column 13 replace ' ' with 'way' in the constant value\n"
        self.assertEqual(hint, expected_hint)

    def test_multi_func_step_2(self):
        broken_solution = os.path.join(self.resource_path, "multi_func_steps", 'multi_func2.py')
        solution = os.path.join(self.resource_path, 'multi_func_solution.py')
        broken_code = open(broken_solution, "r").read()
        solution_code = open(solution, "r").read()
        hint = compare_solutions(broken_code, solution_code, True)
        expected_hint = "At line 50, column 50 replace True with False in the constant value\n"
        self.assertEqual(hint, expected_hint)

    def test_multi_func_step_3(self):
        broken_solution = os.path.join(self.resource_path, "multi_func_steps", 'multi_func3.py')
        solution = os.path.join(self.resource_path, 'multi_func_solution.py')
        broken_code = open(broken_solution, "r").read()
        solution_code = open(solution, "r").read()
        hint = compare_solutions(broken_code, solution_code, True)
        expected_hint = "At line 46, column 46 replace 5 with 1 in the right side of the binary operation\n"
        self.assertEqual(hint, expected_hint)

    def test_multi_func_step_4(self):
        broken_solution = os.path.join(self.resource_path, "multi_func_steps", 'multi_func4.py')
        solution = os.path.join(self.resource_path, 'multi_func_solution.py')
        broken_code = open(broken_solution, "r").read()
        solution_code = open(solution, "r").read()
        hint = compare_solutions(broken_code, solution_code, True)
        expected_hint = "At line 18, column 20 replace const with constant in the left side of the assignment\n"
        self.assertEqual(hint, expected_hint)

    def test_multi_func_step_5(self):
        broken_solution = os.path.join(self.resource_path, "multi_func_steps", 'multi_func5.py')
        solution = os.path.join(self.resource_path, 'multi_func_solution.py')
        broken_code = open(broken_solution, "r").read()
        solution_code = open(solution, "r").read()
        hint = compare_solutions(broken_code, solution_code, True)
        expected_hint = "No hint available, student code is identical to the goal code."
        self.assertEqual(hint, expected_hint)

    def test_multi_func_is_goal(self):
        solution = os.path.join(self.resource_path, 'multi_func_solution.py')
        solution_code = open(solution, "r").read()
        hint = compare_solutions(solution_code, solution_code, True)
        expected_hint = "No hint available, student code is identical to the goal code."
        self.assertEqual(hint, expected_hint)

    def test_multi_func_step_5_is_goal(self):
        broken_solution = os.path.join(self.resource_path, "multi_func_steps", 'multi_func5.py')
        solution = os.path.join(self.resource_path, 'multi_func_solution.py')
        broken_code = open(broken_solution, "r").read()
        solution_code = open(solution, "r").read()
        some_state = create_state(broken_code, solution_code, True)
        self.assertEqual(some_state.code, some_state.goal.code)
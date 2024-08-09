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
        broken_code, solution_code = self.open_broken_and_solution(broken_solution, solution)
        hint = compare_solutions(broken_code, solution_code, True)
        expected_hint = "At line 46, column 29 replace 5 with 1 in the integer value"
        self.assertEqual(hint, expected_hint)

    def open_broken_and_solution(self, broken_solution, solution):
        with open(broken_solution, "r") as broken_file:
            broken_code = broken_file.read()
        with open(solution, "r") as solution_file:
            solution_code = solution_file.read()
        return broken_code, solution_code

    def test_multi_func_step_1(self):
        broken_solution = os.path.join(self.resource_path, "multi_func_steps", 'multi_func1.py')
        solution = os.path.join(self.resource_path, 'multi_func_solution.py')
        broken_code, solution_code = self.open_broken_and_solution(broken_solution, solution)
        hint = compare_solutions(broken_code, solution_code, True)
        expected_hint = "At line 50, column 16 replace True with False in the boolean value"
        self.assertEqual(hint, expected_hint)

    def test_multi_func_step_2(self):
        broken_solution = os.path.join(self.resource_path, "multi_func_steps", 'multi_func2.py')
        solution = os.path.join(self.resource_path, 'multi_func_solution.py')
        broken_code, solution_code = self.open_broken_and_solution(broken_solution, solution)
        hint = compare_solutions(broken_code, solution_code, True)
        expected_hint = "At line 13, column 39 replace ' ' with 'way' in the string"
        self.assertEqual(hint, expected_hint)

    def test_multi_func_step_3(self):
        broken_solution = os.path.join(self.resource_path, "multi_func_steps", 'multi_func3.py')
        solution = os.path.join(self.resource_path, 'multi_func_solution.py')
        broken_code, solution_code = self.open_broken_and_solution(broken_solution, solution)

        hint = compare_solutions(broken_code, solution_code, True)
        expected_hint = "At line 18, column 20 replace const with constant in the left side of the assignment"
        self.assertEqual(hint, expected_hint)

    def test_multi_func_step_4(self):
        broken_solution = os.path.join(self.resource_path, "multi_func_steps", 'multi_func4.py')
        solution = os.path.join(self.resource_path, 'multi_func_solution.py')
        broken_code, solution_code = self.open_broken_and_solution(broken_solution, solution)
        hint = compare_solutions(broken_code, solution_code, True)
        expected_hint = "At line 13, column 47 replace 'something else' with ' ' in the string"
        self.assertEqual(hint, expected_hint)

    def test_multi_func_step_5(self):
        broken_solution = os.path.join(self.resource_path, "multi_func_steps", 'multi_func5.py')
        solution = os.path.join(self.resource_path, 'multi_func_solution.py')
        broken_code, solution_code = self.open_broken_and_solution(broken_solution, solution)

        hint = compare_solutions(broken_code, solution_code, True)
        expected_hint = "At line 39, column 11 change english.split(' ') to english in the return statement"
        self.assertEqual(hint, expected_hint)

    def test_multi_func_step_6(self):
        broken_solution = os.path.join(self.resource_path, "multi_func_steps", 'multi_func6.py')
        solution = os.path.join(self.resource_path, 'multi_func_solution.py')
        broken_code, solution_code = self.open_broken_and_solution(broken_solution, solution)

        hint = compare_solutions(broken_code, solution_code, True)
        expected_hint = "At line 13, column 24 change (word + 'way') to word in the left side of the binary operation"
        self.assertEqual(hint, expected_hint)

    def test_multi_func_step_7(self):
        broken_solution = os.path.join(self.resource_path, "multi_func_steps", 'multi_func7.py')
        solution = os.path.join(self.resource_path, 'multi_func_solution.py')
        broken_code, solution_code = self.open_broken_and_solution(broken_solution, solution)
        hint = compare_solutions(broken_code, solution_code, True)
        expected_hint = "No hint available, student code is identical to the goal code."
        self.assertEqual(hint, expected_hint)

    def test_multi_func_is_goal(self):
        solution = os.path.join(self.resource_path, 'multi_func_solution.py')
        with open(solution, "r") as solution_file:
            solution_code = solution_file.read()
        hint = compare_solutions(solution_code, solution_code, True)
        expected_hint = "No hint available, student code is identical to the goal code."
        self.assertEqual(hint, expected_hint)

    def test_multi_func_step_7_is_goal(self):
        broken_solution = os.path.join(self.resource_path, "multi_func_steps", 'multi_func7.py')
        solution = os.path.join(self.resource_path, 'multi_func_solution.py')
        broken_code, solution_code = self.open_broken_and_solution(broken_solution, solution)
        some_state = create_state(broken_code, solution_code, True)
        self.assertEqual(some_state.anonymized_code, some_state.anonymized_code)

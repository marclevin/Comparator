import ast
from typing import List

from comparison.structures.ChangeVector import ChangeVector
from comparison.utils.astTools import deepcopy, cmp
from comparison.utils.display import print_function


# The State class holds all the relevent information for a solution state


class State:
    id = None
    name = None
    score = None
    feedback = None
    code = None

    fun = None
    loadedFun = None
    tree = None
    anonymized_code = None

    count = 0

    def __init__(self):
        self.count = 0
        self.reverse_map = None
        self.change_vectors = None

    def __cmp__(this, other):
        if not isinstance(other, State):
            return -1
        c1 = cmp(this.fun, other.fun)
        c2 = cmp(this.name, other.name)
        c3 = cmp(this.id, other.id)
        return c1 if c1 != 0 else c2 if c2 != 0 else c3

    def deepcopy(this):
        s = State()
        s.id = this.id
        s.name = this.name
        s.score = this.score
        s.fun = this.fun
        s.tree = deepcopy(this.tree)

        properties = [
            "count",
            "goal",
            "goal_id",
            "goalDist",
            "next",
            "next_id",
            "edit",
            "hint",
            "treeWeight",
        ]
        for prop in properties:
            if hasattr(this, prop):
                setattr(s, prop, getattr(this, prop))
        return s


class CanonicalState(State):
    count = 0  # how many students have submitted this state before?

    goal = None  # the eventual goal state for this student
    goal_dist = -1
    goal_id = None

    next = None  # the next state in the solution space
    next_id = None
    edit = None  # the changes on the edge to the next state


class CodeState(State):
    anonymized_code = None
    next: State = None
    original_ast: ast = None
    goal: State = None  # the eventual goal state for this student
    distance_to_goal: int = -1
    edit: List[ChangeVector] = None  # the changes on the edge to the next state
    reverse_map = None

    # Constructor
    def __init__(self, tree, goal=None):
        super().__init__()
        self.reverse_name_map = None
        self.goal = goal
        self.tree = tree
        self.code = print_function(tree)
        self.original_ast = tree


class IntermediateState(State):
    distance_to_goal = -1
    distance_to_original = -1
    change_vectors: list = None
    count = 0
    code = None
    reverse_map = None

    def __init__(self, tree=None, reverse_map=None):
        super().__init__()
        self.tree = tree
        self.reverse_map = reverse_map
        self.code = print_function(tree)


class GoalState(State):
    goal_ast: ast = None

    def __init__(self, goal_ast) -> None:
        self.goal_ast = goal_ast

from typing import Tuple

from comparison.canonicalize.canon import get_canonical_form
from comparison.path_construction.comparator import *
from comparison.utils.tools import *


def desirability(student_state: State, candidate_state: State, goal_state: State):
    score = 0
    d = 0

    # Minimize the distance from current to next
    b = 1 - distance(student_state, candidate_state)[0]
    candidate_state.distance_to_original = b
    score += 4 * b

    # Maximize the performance on test cases
    # c = n.score
    # n.test = c
    # score += 1 * c

    # Minimize the distance from the next state to the final state
    if student_state is not goal_state:
        d = 1 - distance(student_state, goal_state)[0]
    candidate_state.distance_to_goal = d
    score += 2 * d

    score /= 6.0
    return score


def map_differences(start: ast.AST, end: ast.AST):
    diff_map = {"start": {}}
    all_changes = get_changes(start, end)
    start_copy = deepcopy(start)
    for change in all_changes:
        change.update(start_copy, diff_map)
        start_copy = change.apply_change()
    return diff_map


def quick_deep_copy(change_vector):
    # Doesn't copy start because it will get replaced anyway
    # the old subtree and new subtree can be aliases because we never modify them
    path = change_vector.path[:]
    old, new = change_vector.old_subtree, change_vector.new_subtree
    if isinstance(change_vector, AddVector):
        return AddVector(path, old, new)
    elif isinstance(change_vector, DeleteVector):
        return DeleteVector(path, old, new)
    elif isinstance(change_vector, SwapVector):
        tmp = SwapVector(path, old, new)
        if change_vector.old_path is not None:
            tmp.old_path = change_vector.old_path
            tmp.new_path = change_vector.new_path
        return tmp
    elif isinstance(change_vector, MoveVector):
        return MoveVector(path, old, new)
    elif isinstance(change_vector, SubVector):
        return SubVector(path, old, new)
    elif isinstance(change_vector, SuperVector):
        return SuperVector(path, old, new)
    elif isinstance(change_vector, ChangeVector):
        return ChangeVector(path, old, new)
    else:
        raise Exception("Unknown change vector type, can't copy")


def update_change_vectors(changes, old_start, new_start):
    if len(changes) == 0:
        return changes, new_start
    # We need new CVs here because they're going to change
    changes = [quick_deep_copy(change) for change in changes]
    map_dict = map_differences(old_start, new_start)
    new_state = deepcopy(new_start)
    for change in changes:
        change.update(new_state, map_dict)  # map_dict gets updated each time
        new_state = change.apply_change()
    return changes, new_state


def apply_change_vectors(student_state: CodeState, changes: List[ChangeVector]) -> State:
    """Attempt to apply all the changes listed to the solution state s"""
    if len(changes) == 0:
        return student_state
    tup = update_change_vectors(changes, changes[0].start, student_state.tree)
    changes, new_state = tup
    inter_state = IntermediateState(tree=new_state, reverse_map=student_state.goal.reverse_map)
    inter_state.code = print_function(inter_state.tree)
    return inter_state


def optimize_goal(student_state: CodeState, changes: list[ChangeVector]):
    current_goal, current_diff, current_edits = student_state.goal, student_state.distance_to_goal, changes
    all_changes = []

    class Branch:  # use this to hold branches
        def __init__(self, edits, next, state):
            self.edits = edits
            self.next = next
            self.state = state

    tree_level = [Branch([], changes, student_state)]
    # Until you've run out of possible goal states...
    while len(tree_level) != 0:
        next_level = []
        # Look at each number of combinations of edits
        for branch in tree_level:
            # Apply each possible next edit
            for i in range(len(branch.next)):
                new_changes = branch.edits + [branch.next[i]]
                # If our current best is in this, don't bother
                if isStrictSubset(current_edits, new_changes):
                    continue
                # Check to see that the state exists and that it isn't too far away
                new_state = apply_change_vectors(student_state, new_changes)
                new_distance, _ = distance(student_state, new_state, given_changes=new_changes)

                all_changes.append((new_changes, new_state))  # just in case we need the final goal

                if new_distance <= current_diff:  # it's a new goal!
                    # We know that it's closer because we just tested distance
                    current_goal, current_diff, current_edits = new_state, new_distance, new_changes
                else:
                    # Only include changes happening after this one to avoid ordering effects!
                    # We only add a state here if it's closer than the current goal
                    next_level.append(Branch(new_changes, branch.next[i + 1:], new_state))
        tree_level = next_level
    if student_state.code == current_goal.code:
        return all_changes
    if student_state.goal.code == current_goal.code:
        return all_changes
    else:
        student_state.goal, student_state.distance_to_goal, = current_goal, current_diff


def is_valid_next_state(student_state, new_state, goal_state):
    """Checks the three rules for valid next states"""

    # We can't use the state itself!
    if student_state == new_state:
        return False
    # First: is the state well-formed?
    if new_state is None:
        return False

    # Now test loadable
    try:
        ast.parse(new_state.code)
    except Exception as e:
        return False  # didn't load properly

    # Third: is test.test(n) >= test.test(s)?
    # TODO: Figure out if we can use AutoMarker scores here?

    # if n.score < s.score and abs(n.score - s.score) > 0.001:
    # 	return False

    # Loadable technically falls here, but it takes a while
    # so filter with diff first
    # Second: is diff(n, g) < diff(s, g)?

    # We check if the distance is less than the current distance to the goal
    # If it's not, we don't want to use it
    new_distance, _ = distance(student_state, new_state)
    if new_distance > student_state.distance_to_goal:
        return False

    # If we pass all the checks, it's a valid state
    return True


def generate_states_in_path(student_state: CodeState, valid_combinations: list[tuple[list[ChangeVector], CodeState]]):
    best_score, best_state = -1, None
    ideal_changes = None

    for (change_vector, candidate_state) in valid_combinations:
        filtered_changes = [change for change in change_vector if
                            compare_trees(change.old_subtree, change.new_subtree, check_equality=True) != 0]

        if filtered_changes:
            score = desirability(student_state, candidate_state, student_state.goal)
            if score > best_score:
                best_score = score
                best_state = candidate_state
                ideal_changes = filtered_changes

    student_state.change_vectors = ideal_changes
    student_state.next = best_state


def get_all_combinations(student_state: CodeState, changes: list[ChangeVector]):
    all_changes = power_set(changes)
    # Also find the solution states associated with the changes
    all_combinations = []
    for change in all_changes:
        all_combinations.append((change, apply_change_vectors(student_state, change)))
    return all_combinations


# Preamble: We are given the students current state, and the goal state (from Chris)
# Step 1: First, optimize the goal state, by applying possible combinations of edits from the original diff.
# Step 2: If the goal state is not the same as the current goal state, we have a new goal state.
# Step 3: Generate all possible combinations of edits from the current state to the new goal state (power set)
# Step 4: For each combination, apply the changes to the current state and check if the state is valid.
# Step 5: If the state is valid, score it based on the four desirable properties.
# Step 6: If the score is better than the current best, update the best state and the best score.
# Step 7: If we have a best state, set the next state of the current state to the best state.
# Step 8: Finally, we have the next state in the solution space.
# Step 9: We move on to generating the hint.

# Flow:
# In: Student_State and Goal_State
# Out: Student_State with next state set
def get_next_state(student_state: CodeState):
    """Generates the next state in the solution space for the student state"""
    (student_state.distance_to_goal, changes) = distance(student_state,
                                                         student_state.goal)  # now get the actual changes
    # if the distance is 0, we're done
    if student_state.distance_to_goal == 0 or len(changes) == 0:
        student_state.next = None
        return
    # Optimize the goal state
    # all_combinations = optimize_goal(student_state, changes)
    all_combinations = None
    if all_combinations is None:
        changes = get_changes(student_state.tree, student_state.goal.tree)
        all_combinations = get_all_combinations(student_state, changes)
    changes = [change for change in changes if
               compare_trees(change.old_subtree, change.new_subtree, check_equality=True) != 0]

    student_state.changesToGoal = len(changes)

    # Now check for the required properties of a next state. Filter before sorting to save time
    valid_combinations = filter(lambda candidate: is_valid_next_state(student_state, candidate[1], student_state.goal),
                                all_combinations)
    # Order based on the longest-changes first, but with edits in order
    valid_combinations = sorted(valid_combinations, key=lambda x: len(x))

    if len(valid_combinations) == 0:
        # No possible changes
        student_state.next = None
        return

    generate_states_in_path(student_state, valid_combinations)


def create_state(student_code: str, goal_code: str, canonicalize: bool) -> CodeState:
    student_code_state = CodeState(tree=ast.parse(student_code))
    goal_code_state = IntermediateState(tree=ast.parse(goal_code))
    # Canonicalize
    if not canonicalize:
        student_code_state.goal = goal_code_state
        return student_code_state
    # Student imports & names
    student_imports = collect_attributes(student_code_state)
    student_code_state = get_canonical_form(student_code_state, imports=student_imports)
    # Goal imports & names
    goal_imports = collect_attributes(goal_code_state)
    goal_code_state = get_canonical_form(goal_code_state, imports=goal_imports)
    student_code_state.goal = goal_code_state
    return student_code_state


def create_canonical_intermediate_state(code: str) -> State:
    try:
        code_state = IntermediateState(tree=ast.parse(code))
        imports = collect_attributes(code_state)
        return get_canonical_form(code_state, imports=imports)
    except SyntaxError:
        raise SyntaxError("Syntax error in code")


def collect_attributes(given_ast) -> Tuple[List[ast.AST], List[str]]:
    imports = get_all_import_statements(given_ast)
    return imports

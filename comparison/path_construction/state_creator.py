from comparison.path_construction.comparator import *
from comparison.utils.tools import *


def desirability(student_state: CodeState, candidate_state: IntermediateState, goal_state):
    """Scores the state n based on the four desirable properties. Returns a number
        between 0 (not desirable) and 1 (very desirable)."""
    # Original metric: 2 - 4 - 1 - 2
    score = 0
    d = 0
    # First: has the state been visited before?
    a = int(candidate_state.count > 0)
    candidate_state.timesVisted = a
    score += 4 * a

    # Second: minimize the distance from current to next
    b = 1 - distance(student_state, candidate_state)[0]
    candidate_state.distance_to_original = b
    score += 2 * b

    # Third: maximize the performance on test cases
    # c = n.score
    # n.test = c
    # score += 1 * c

    # Forth: minimize the distance from the next state to the final state
    if student_state is not goal_state:
        d = 1 - distance(student_state, goal_state)[0]
    candidate_state.distance_to_goal = d
    score += 2 * d

    score /= 7.0
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
    inter_state = IntermediateState(tree=new_state)
    inter_state.code = print_function(inter_state.tree)
    return inter_state


def chooseGoal(s, goals, states):
    # First, find the closest goal state and the changes required to get to it
    goalDist = 2  # the max dist is 1
    goal = origGoal = None
    changes = None
    # First, find the program whose structure best matches the state
    for g in goals:
        (tempD, tempChanges) = distance(s, g, ignoreVariables=True)
        # prefer more common goals over less common ones
        if (tempD < goalDist) or (tempD == goalDist and g.count > goal.count):
            (goal, goalDist, changes) = (g, tempD, tempChanges)
    # Then do variable matching between the two programs
    if goal != None:
        # First, do helper function mapping, if it's necessary
        helperDistributions = generateHelperDistributions(s, goal, goals, states)
        if len(helperDistributions) > 0:
            goalDist = 2  # reset because now we're going to count variables
            origGoal = goal
            for modG in helperDistributions:
                (tempD, tempChanges) = distance(s, modG)
                # prefer more common goals over less common ones
                if (tempD < goalDist) or (tempD == goalDist and modG.count > goal.count):
                    (goal, goalDist, changes) = (modG, tempD, tempChanges)

        goalDist = 2  # reset because now we're going to count variables
        origGoal = goal
        allDistributions = generateVariableDistributions(s, goal, goals, states)
        for modG in allDistributions:
            (tempD, tempChanges) = distance(s, modG)
            # prefer more common goals over less common ones
            if (tempD < goalDist) or (tempD == goalDist and modG.count > goal.count):
                (goal, goalDist, changes) = (modG, tempD, tempChanges)
    return goal


def generateHelperDistributions(s, g, goals, states):
    restricted_names = list(eval(s.problem.arguments).keys())
    sHelpers = gather_all_helpers(s.tree, restricted_names)
    gHelpers = gather_all_helpers(g.tree, restricted_names)
    nonMappableHelpers = gather_all_function_names(g.tree)
    for pair in gHelpers:  # make sure to remove all matches, regardless of whether the second part matches!
        for item in nonMappableHelpers:
            if pair[0] == item[0]:
                nonMappableHelpers.remove(item)
                break
    randomCount = nCount = newRandomCount = 0
    if len(sHelpers) > len(gHelpers):
        gHelpers |= set([("random_fun" + str(i), None) for i in range(len(sHelpers) - len(gHelpers))])
        randomCount = newRandomCount = len(sHelpers) - len(gHelpers)
    elif len(gHelpers) > len(sHelpers):
        sHelpers |= set([("new_fun" + str(i), None) for i in range(len(gHelpers) - len(sHelpers))])
        nCount = len(gHelpers) - len(sHelpers)

    # First, track down vars which are going to conflict with built-in names in the goal state
    starterPairs = []
    sList, gList, nList = list(sHelpers), list(gHelpers), list(nonMappableHelpers)
    i = 0
    while i < len(sList):
        for j in range(len(nList)):
            if sList[i][1] == nList[j][0]:  # if the variable will conflict with a built-in name
                if randomCount > 0:  # match the last random var to this var
                    starterPairs.append((sList[i][0], "random_fun" + str(randomCount - 1)))
                    sList.pop(i)
                    gList.remove(("random_fun" + str(randomCount - 1), None))
                    randomCount -= 1
                    i -= 1  # since we're popping, make sure to check the next one
                    break
                else:  # generate a new random var and replace the current pos with a new n
                    starterPairs.append((sList[i][0], "random_fun" + str(newRandomCount)))
                    sList[i] = ("new_fun" + str(nCount), None)
                    newRandomCount += 1
                    nCount += 1
                    break
        i += 1
    # Get rid of the original names now
    sList = [x[0] for x in sList]
    gList = [x[0] for x in gList]

    listOfMaps = generateMappings(sList, gList)
    allMaps = []
    for map in listOfMaps:
        d = {}
        for tup in map:
            d[tup[1]] = tup[0]
        allMaps.append(d)
    allFuns = []
    for map in allMaps:
        tmpTree = deepcopy(g.tree)
        tmpTree = applyHelperMap(tmpTree, map)
        tmpCode = print_function(tmpTree)

        matches = list(filter(lambda x: x.code == tmpCode, goals))
        if len(matches) > 0:
            matches = sorted(matches, key=lambda s: getattr(s, "count"))
            tmpG = matches[-1]
            tmpG.tree = str_to_tree(tmpG.tree_source)
            allFuns.append(tmpG)
        else:
            tmpG = CanonicalState(code=tmpCode, problem=s.problem, count=0)
            tmpG.tree = tmpTree
            tmpG.tree_source = tree_to_str(tmpTree)
            tmpG.treeWeight = g.treeWeight
            if tmpG.score != 1:
                log("generateNextStates\tgenerateHelperDistributions\tBad helper remapping: " + str(map), "bug")
                log(s.code, "bug")
                log(print_function(s.orig_tree), "bug")
                log(g.code, "bug")
                log(tmpCode, "bug")
            allFuns.append(tmpG)
            goals.append(tmpG)
            states.append(tmpG)
    return allFuns


def generateVariableDistributions(s, g, goals, states):
    sParameters = gather_all_parameters(s.tree)
    gParameters = gather_all_parameters(g.tree, keep_orig=False)
    restricted_names = list(eval(s.problem.arguments).keys()) + get_all_imports(s.tree) + get_all_imports(g.tree)
    sHelpers = gather_all_helpers(s.tree, restricted_names)
    gHelpers = gather_all_helpers(g.tree, restricted_names)
    sVariables = gather_all_variables(s.tree)
    gVariables = gather_all_variables(g.tree, keep_orig=False)
    # First, just make extra sure none of the restricted names are included
    for name in restricted_names:
        for item in sVariables:
            if name == item[0]:
                sVariables.remove(item)
                break
        for item in gVariables:
            if name == item[0]:
                gVariables.remove(item)
                break
    for pair in sParameters | sHelpers:  # make sure to remove all matches, regardless of whether the second part matches!
        for item in sVariables:
            if pair[0] == item[0]:
                sVariables.remove(item)
                break
    for pair in gParameters | gHelpers:  # make sure to remove all matches, regardless of whether the second part matches!
        for item in gVariables:
            if pair[0] == item[0]:
                gVariables.remove(item)
                break
    nonMappableVariables = gather_all_names(g.tree, keep_orig=False)
    for pair in gVariables | gParameters | gHelpers:  # make sure to remove all matches, regardless of whether the second part matches!
        for item in nonMappableVariables:
            if pair[0] == item[0]:
                nonMappableVariables.remove(item)
                break
    randomCount = nCount = newRandomCount = 0
    if len(sVariables) > len(gVariables):
        randomCount = newRandomCount = len(sVariables) - len(gVariables)
        gVariables |= set([("random" + str(i), None) for i in range(len(sVariables) - len(gVariables))])
    elif len(gVariables) > len(sVariables):
        nCount = len(gVariables) - len(sVariables)
        sVariables |= set([("n" + str(i) + "_global", None) for i in range(len(gVariables) - len(sVariables))])

    # First, track down vars which are going to conflict with built-in names in the goal state
    starterPairs = []
    sList, gList, nList = list(sVariables), list(gVariables), list(nonMappableVariables)
    i = 0
    while i < len(sList):
        for j in range(len(nList)):
            if sList[i][1] == nList[j][0]:  # if the variable will conflict with a built-in name
                if randomCount > 0:  # match the last random var to this var
                    starterPairs.append((sList[i][0], "random" + str(randomCount - 1)))
                    sList.pop(i)
                    gList.remove(("random" + str(randomCount - 1), None))
                    randomCount -= 1
                    i -= 1  # since we're popping, make sure to check the next one
                    break
                else:  # generate a new random var and replace the current pos with a new n
                    starterPairs.append((sList[i][0], "random" + str(newRandomCount)))
                    sList[i] = ("n" + str(nCount) + "_global", None)
                    newRandomCount += 1
                    nCount += 1
                    break
        i += 1
    # Get rid of the original names now
    sList = [x[0] for x in sList]
    gList = [x[0] for x in gList]
    if max(len(sVariables), len(gVariables)) > 6:
        # If it's too large, just do the obvious one-to-one mapping.
        listOfMaps = [[(sList[i], gList[i]) for i in range(len(sList))]]
    else:
        listOfMaps = generateMappings(sList, gList)
    allMaps = []
    placeholdCount = 0
    badMatches = set()
    for map in listOfMaps:
        d = {}
        for pair in starterPairs:  # these apply to all of them
            d[pair[1]] = pair[0]
        for tup in map:
            # Don't allow variable matching across functions!!! This just messes things up.
            if getParentFunction(tup[0]) != getParentFunction(tup[1]) and getParentFunction(
                    tup[0]) != None and getParentFunction(tup[1]) != None:
                badMatches.add(tup[0])
                badMatches.add(tup[1])
                d["z" + str(placeholdCount) + "_newvar"] = tup[0]
                placeholdCount += 1
                d[tup[1]] = "z" + str(placeholdCount) + "_newvar"
                placeholdCount += 1
            else:
                d[tup[1]] = tup[0]
        placeholdCount = 0
        allMaps.append(d)
    allFuns = []
    for map in allMaps:
        tmpTree = deepcopy(g.tree)
        tmpTree = applyVariableMap(tmpTree, map)
        tmpCode = print_function(tmpTree)

        matches = list(filter(lambda x: x.code == tmpCode, goals))
        if len(matches) > 0:
            matches = sorted(matches, key=lambda s: getattr(s, "count"))
            tmpG = matches[-1]
            tmpG.tree = str_to_tree(tmpG.tree_source)
            allFuns.append(tmpG)
        else:
            tmpG = CanonicalState(code=tmpCode, problem=s.problem, count=0)
            tmpG.tree = tmpTree
            tmpG.tree_source = tree_to_str(tmpTree)
            tmpG.treeWeight = g.treeWeight
            if tmpG.score != 1:
                log("generateNextStates\tgenerateVariablesDistributions\tBad variable remapping: " + str(map), "bug")
                log(s.code, "bug")
                log(print_function(s.orig_tree), "bug")
                log(g.code, "bug")
                log(tmpCode, "bug")
            allFuns.append(tmpG)
            goals.append(tmpG)
            states.append(tmpG)
    return allFuns


def generateMappings(s, g):
    if len(s) == 0:
        return [[]]
    allMaps = []
    for i in range(len(g)):
        thisMap = (s[0], g[i])
        restMaps = generateMappings(s[1:], g[:i] + g[i + 1:])
        if s[0] != g[i]:  # only need to include maps that aren't changing the variables
            for map in restMaps:
                map.append(copy.deepcopy(thisMap))
        allMaps += restMaps
    return allMaps


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
    if student_state.goal.code == current_goal.code:
        return all_changes
    else:
        student_state.goal, student_state.distance_to_goal = current_goal, current_diff


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
    all_combinations = optimize_goal(student_state, changes)
    if all_combinations is None:
        changes = get_changes(student_state.tree, student_state.goal.tree)
        all_combinations = get_all_combinations(student_state, changes)

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

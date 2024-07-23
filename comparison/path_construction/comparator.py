from comparison.structures.ChangeVector import *
from comparison.structures.State import *
from comparison.utils.astTools import *


def match_lists(list_x, list_y):
    """For each line in x, determine which line it best maps to in y"""
    list_x = [(list_x[i], i) for i in range(len(list_x))]
    list_y = [(list_y[i], i) for i in range(len(list_y))]
    # First, separate out all the lines based on their types, as we only match between types
    type_map = {}
    for i in range(len(list_x)):
        candidate_type = type(list_x[i][0])
        if candidate_type in type_map:
            pass
        x_subset = list(filter(lambda tmp: type(tmp[0]) is candidate_type, list_x))
        y_subset = list(filter(lambda tmp: type(tmp[0]) is candidate_type, list_y))
        type_map[candidate_type] = (x_subset, y_subset)
    for j in range(len(list_y)):
        candidate_type = type(list_y[j][0])
        if candidate_type in type_map:
            pass
        x_subset = list(filter(lambda tmp: type(tmp[0]) is candidate_type, list_x))
        y_subset = list(filter(lambda tmp: type(tmp[0]) is candidate_type, list_y))
        type_map[candidate_type] = (x_subset, y_subset)

    map_set = {}
    for candidate_type in type_map:
        # For each type, find the optimal matching
        (x_subset, y_subset) = type_map[candidate_type]
        # First, find exact matches and remove them
        # Give preference to items on the same line, then we won't need to do an edit
        i = 0
        while i < len(x_subset):
            j = 0
            while j < len(y_subset):
                if x_subset[i][1] == y_subset[j][1]:
                    if (
                            compareASTs(x_subset[i][0], y_subset[j][0], checkEquality=True)
                            == 0
                    ):
                        map_set[y_subset[j][1]] = x_subset[i][1]
                        x_subset.pop(i)
                        y_subset.pop(j)
                        break
                j += 1
            else:
                i += 1
        # Then look for matches anywhere
        i = 0
        while i < len(x_subset):
            j = 0
            while j < len(y_subset):
                if compareASTs(x_subset[i][0], y_subset[j][0], checkEquality=True) == 0:
                    map_set[y_subset[j][1]] = x_subset[i][1]
                    x_subset.pop(i)
                    y_subset.pop(j)
                    break
                j += 1
            else:
                i += 1  # if we break, don't increment!
        # TODO - check for subsets/supersets in here?
        # Then, look for the 'best we can do' matches
        distance_list = []
        for i in range(len(x_subset)):  # Identify the best matches across all pairs
            candidate_state = State()
            candidate_state.tree = x_subset[i][0]
            for j in range(len(y_subset)):
                inner_candidate_state = State()
                inner_candidate_state.tree = y_subset[j][0]
                inner_distance, _ = distance(candidate_state, inner_candidate_state)
                inner_distance = int(inner_distance * 1000)
                distance_list.append((inner_distance, x_subset[i][1], y_subset[j][1]))
        # Compare first based on distance, then based on how close the lines are to each other
        distance_list.sort(key=lambda x: (x[0], x[1] - x[2]))
        line_distance = min(len(x_subset), len(y_subset))
        # Now pick the best pairs 'til we run out of them
        while line_distance > 0:
            (inner_distance, xLine, yLine) = distance_list[0]
            map_set[yLine] = xLine
            distance_list = list(
                filter(lambda pair: pair[1] != xLine and pair[2] != yLine, distance_list)
            )
            line_distance -= 1
    # Now, look for matches across different types
    leftover_y = list(filter(lambda tmp: tmp not in map_set, range(len(list_y))))
    leftover_x = list(filter(lambda tmp: tmp not in map_set.values(), range(len(list_x))))
    # First, look for exact line matches
    i = 0
    while i < len(leftover_x):
        line = leftover_x[i]
        if line in leftover_y:
            map_set[line] = line
            leftover_x.remove(line)
            leftover_y.remove(line)
        else:
            i += 1
    # Then, just put the rest in place
    for i in range(min(len(leftover_y), len(leftover_x))):  # map together all equal parts
        map_set[leftover_y[i]] = leftover_x[i]
    if len(leftover_x) > len(leftover_y):  # if X greater, map all leftover x's to -1
        map_set[-1] = leftover_x[len(leftover_y):]
    elif len(leftover_y) > len(leftover_x):  # if Y greater, map all leftover y's to -1
        for i in range(len(leftover_x), len(leftover_y)):
            map_set[leftover_y[i]] = -1
    # if equal, there are none left to map!
    return map_set


def findKey(d, val):
    for k in d:
        if d[k] == val:
            return k
    return None


def xOffset(line, deletedLines):
    offset = 0
    for l in deletedLines:
        if l <= line:
            offset += 1
    return offset


def yOffset(line, addedLines):
    offset = 0
    for l in addedLines:
        if l <= line:
            offset += 1
    return offset


def findSwap(startList, endList):
    for i in range(len(startList)):
        if startList[i] == endList[i]:
            pass
        for j in range(i + 1, len(startList)):
            if startList[i] == endList[j] and endList[i] == startList[j]:
                return SwapVector([-1], startList[i], startList[j])
    return None


# Recursively generate all moves by working from the outside of the list inwards.
# This should be optimal for lists of up to size four, and once you get to size five, your program is too
# large and I don't care anymore.
def generate_move_pairs(start_list, end_list):
    # Base case: If either list has 1 or 0 elements, no moves are needed.
    if len(start_list) <= 1:
        return []

    # If the first elements match, no move is needed for the first element.
    if start_list[0] == end_list[0]:
        return generate_move_pairs(start_list[1:], end_list[1:])

    # If the last elements match, no move is needed for the last element.
    if start_list[-1] == end_list[-1]:
        return generate_move_pairs(start_list[:-1], end_list[:-1])

    # If the first element of start_list matches the last of end_list and vice versa, swap them.
    if start_list[0] == end_list[-1] and start_list[-1] == end_list[0]:
        return [("swap", start_list[0], start_list[-1])] + generate_move_pairs(start_list[1:-1], end_list[1:-1])

    # If the first element of start_list is at the end of end_list, move it to the front.
    if start_list[0] == end_list[-1]:
        return [("move", start_list[0])] + generate_move_pairs(start_list[1:], end_list[:-1])

    # If the last element of start_list is at the beginning of end_list, move it to the back.
    if start_list[-1] == end_list[0]:
        return [("move", start_list[-1])] + generate_move_pairs(start_list[:-1], end_list[1:])

    # For other cases, find the position of the first element of start_list in end_list and move it.
    i = end_list.index(start_list[0])
    return [("move", start_list[0])] + generate_move_pairs(start_list[1:], end_list[:i] + end_list[i + 1:])


def find_move_vectors(map_set, list_x, list_y, added_lines, deleted_lines):
    """We'll find all the moved lines by recreating the mapSet from a tmpSet using actions"""
    start_list = list(range(len(list_x)))
    end_list = [map_set[i] for i in range(len(list_y))]
    # Remove deletes from start_list and adds from end_list.
    for line in deleted_lines:
        start_list.remove(line)
    while -1 in end_list:
        end_list.remove(-1)
    if len(start_list) != len(end_list):
        log(
            "diffAsts\tfindMovedLines\tUnequal lists: "
            + str(len(start_list))
            + ","
            + str(len(end_list)),
            "bug",
        )
        return []
    move_actions = []
    if start_list != end_list:
        move_pairs = generate_move_pairs(start_list, end_list)
        for pair in move_pairs:
            if pair[0] == "move":
                move_actions.append(MoveVector([-1], pair[1], end_list.index(pair[1])))
            elif pair[0] == "swap":
                move_actions.append(SwapVector([-1], pair[1], pair[2]))
            else:
                log("Missing movePair type: " + str(pair[0]), "bug")
    # We need to make sure the indices start at the appropriate numbers, since they're referring to the original tree
    if len(deleted_lines) > 0:
        for action in move_actions:
            if isinstance(action, MoveVector):
                add_to_count = 0
                for deleteAction in deleted_lines:
                    if deleteAction <= action.newSubtree:
                        add_to_count += 1
                action.newSubtree += add_to_count
    return move_actions


def diff_lists(list_x, list_y):
    map_set = match_lists(list_x, list_y)
    change_vectors = []

    # First, get all the added and deleted lines
    deleted_lines = map_set[-1] if -1 in map_set else []
    for line in sorted(deleted_lines):
        change_vectors.append(DeleteVector([line], list_x[line], None))

    added_lines = list(filter(lambda tmp: map_set[tmp] == -1, map_set.keys()))
    added_offset = 0  # Because added lines don't start in the list, we need
    # to offset their positions for each new one that's added
    for line in sorted(added_lines):
        change_vectors.append(AddVector([line - added_offset], None, list_y[line]))
        added_offset += 1

    # Now, find all the required moves
    change_vectors += find_move_vectors(map_set, list_x, list_y, added_lines, deleted_lines)

    # Finally, for each pair of lines (which have already been moved appropriately,
    # find if they need a normal ChangeVector
    for j in map_set:
        i = map_set[j]
        # Not a delete move or an add move.
        if j != -1 and i != -1:
            temp_vectors = diff_asts(list_x[i], list_y[j])
            for change in temp_vectors:
                change.path.append(i)
            change_vectors += temp_vectors
    return change_vectors


def diff_asts(ast_x, ast_y):
    """Find all change vectors between x and y"""
    if isinstance(ast_x, ast.AST) and isinstance(ast_y, ast.AST):
        if type(ast_x) is not type(ast_y):  # different node types
            if occursIn(ast_x, ast_y):
                return [SubVector([], ast_x, ast_y)]
            elif occursIn(ast_y, ast_x):
                return [SuperVector([], ast_x, ast_y)]
            else:
                return [ChangeVector([], ast_x, ast_y)]
        elif type(ast_x) is type(ast_y) is ast.Name:
            if not builtInName(ast_x.id) and not builtInName(ast_y.id):
                return []  # ignore the actual IDs

        found_differences = []
        # For every field, like body, or value, etc.
        for field in ast_x.__getattribute__("_fields"):
            try:
                current_diffs = diff_asts(getattr(ast_x, field), getattr(ast_y, field))
                if current_diffs:
                    for change in current_diffs:
                        change.path.append((field, astNames[type(ast_x)]))
                    found_differences += current_diffs
            except AttributeError as e:
                setattr(ast_x, field, None)
        return found_differences
    elif not isinstance(ast_x, ast.AST) and not isinstance(ast_y, ast.AST):
        if type(ast_x) is list and type(ast_y) is list:
            return diff_lists(ast_x, ast_y)
        elif ast_x is not ast_y or type(ast_x) is not type(ast_y):
            # Type check.
            return [ChangeVector([], ast_x, ast_y)]  # they're primitive, so just switch them
        else:  # equal values
            return []
    else:  # Two mismatched types
        return [ChangeVector([], ast_x, ast_y)]


def sumWeight(bases):
    return sum(map(lambda x: get_weight(x), bases))


def get_weight(given_tree, countTokens=True):
    """Get the size of the given tree"""
    if given_tree is None:
        return 0
    elif type(given_tree) is list:
        return sum(map(lambda x: get_weight(x, countTokens), given_tree))
    elif not isinstance(given_tree, ast.AST):
        return 1
    else:  # Otherwise, it's an AST node
        if hasattr(given_tree, "treeWeight"):
            return given_tree.treeWeight
        weight = 0
        if type(given_tree) in [ast.Module, ast.Interactive, ast.Suite]:
            weight = get_weight(given_tree.body, countTokens=countTokens)
        elif type(given_tree) is ast.Expression:
            weight = get_weight(given_tree.body, countTokens=countTokens)
        elif type(given_tree) is ast.FunctionDef:
            # add 1 for function name
            weight = 1 + get_weight(given_tree.args, countTokens=countTokens) + \
                     get_weight(given_tree.body, countTokens=countTokens) + \
                     get_weight(given_tree.decorator_list, countTokens=countTokens) + \
                     get_weight(given_tree.returns, countTokens=countTokens)
        elif type(given_tree) is ast.ClassDef:
            # add 1 for class name
            weight = 1 + sumWeight(given_tree.bases, countTokens=countTokens) + \
                     sumWeight(given_tree.keywords, countTokens=countTokens) + \
                     get_weight(given_tree.body, countTokens=countTokens) + \
                     get_weight(given_tree.decorator_list, countTokens=countTokens)
        elif type(given_tree) in [ast.Return, ast.Yield, ast.Attribute, ast.Starred]:
            # add 1 for action name
            weight = 1 + get_weight(given_tree.value, countTokens=countTokens)
        elif type(given_tree) is ast.Delete:  # add 1 for del
            weight = 1 + get_weight(given_tree.targets, countTokens=countTokens)
        elif type(given_tree) is ast.Assign:  # add 1 for =
            weight = 1 + get_weight(given_tree.targets, countTokens=countTokens) + \
                     get_weight(given_tree.value, countTokens=countTokens)
        elif type(given_tree) is ast.AugAssign:
            weight = get_weight(given_tree.target, countTokens=countTokens) + \
                     get_weight(given_tree.op, countTokens=countTokens) + \
                     get_weight(given_tree.value, countTokens=countTokens)
        elif type(given_tree) is ast.For:  # add 1 for 'for' and 1 for 'in'
            weight = 2 + get_weight(given_tree.target, countTokens=countTokens) + \
                     get_weight(given_tree.iter, countTokens=countTokens) + \
                     get_weight(given_tree.body, countTokens=countTokens) + \
                     get_weight(given_tree.orelse, countTokens=countTokens)
        elif type(given_tree) is [ast.While, ast.If]:
            # add 1 for while/if
            weight = 1 + get_weight(given_tree.test, countTokens=countTokens) + \
                     get_weight(given_tree.body, countTokens=countTokens)
            if len(given_tree.orelse) > 0:  # add 1 for else
                weight += 1 + get_weight(given_tree.orelse, countTokens=countTokens)
        elif type(given_tree) is ast.With:  # add 1 for with
            weight = 1 + get_weight(given_tree.items, countTokens=countTokens) + \
                     get_weight(given_tree.body, countTokens=countTokens)
        elif type(given_tree) is ast.Raise:  # add 1 for raise
            weight = 1 + get_weight(given_tree.exc, countTokens=countTokens) + \
                     get_weight(given_tree.cause, countTokens=countTokens)
        elif type(given_tree) == ast.Try:  # add 1 for try
            weight = 1 + get_weight(given_tree.body, countTokens=countTokens) + \
                     get_weight(given_tree.handlers, countTokens=countTokens)
            if len(given_tree.orelse) > 0:  # add 1 for else
                weight += 1 + get_weight(given_tree.orelse, countTokens=countTokens)
            if len(given_tree.finalbody) > 0:  # add 1 for finally
                weight += 1 + get_weight(given_tree.finalbody, countTokens=countTokens)
        elif type(given_tree) == ast.Assert:  # add 1 for assert
            weight = 1 + get_weight(given_tree.test, countTokens=countTokens) + \
                     get_weight(given_tree.msg, countTokens=countTokens)
        elif type(given_tree) in [ast.Import, ast.Global]:  # add 1 for function name
            weight = 1 + get_weight(given_tree.names, countTokens=countTokens)
        elif type(given_tree) == ast.ImportFrom:  # add 3 for from module import
            weight = 3 + get_weight(given_tree.names, countTokens=countTokens)
        elif type(given_tree) in [ast.Expr, ast.Index]:
            weight = get_weight(given_tree.value, countTokens=countTokens)
            if weight == 0:
                weight = 1
        elif type(given_tree) == ast.BoolOp:  # add 1 for each op
            weight = (len(given_tree.values) - 1) + \
                     get_weight(given_tree.values, countTokens=countTokens)
        elif type(given_tree) == ast.BinOp:  # add 1 for op
            weight = 1 + get_weight(given_tree.left, countTokens=countTokens) + \
                     get_weight(given_tree.right, countTokens=countTokens)
        elif type(given_tree) == ast.UnaryOp:  # add 1 for operator
            weight = 1 + get_weight(given_tree.operand, countTokens=countTokens)
        elif type(given_tree) == ast.Lambda:  # add 1 for lambda
            weight = 1 + get_weight(given_tree.args, countTokens=countTokens) + \
                     get_weight(given_tree.body, countTokens=countTokens)
        elif type(given_tree) == ast.IfExp:  # add 2 for if and else
            weight = 2 + get_weight(given_tree.test, countTokens=countTokens) + \
                     get_weight(given_tree.body, countTokens=countTokens) + \
                     get_weight(given_tree.orelse, countTokens=countTokens)
        elif type(given_tree) == ast.Dict:  # return 1 if empty dictionary
            weight = 1 + get_weight(given_tree.keys, countTokens=countTokens) + \
                     get_weight(given_tree.values, countTokens=countTokens)
        elif type(given_tree) in [ast.Set, ast.List, ast.Tuple]:
            weight = 1 + get_weight(given_tree.elts, countTokens=countTokens)
        elif type(given_tree) in [ast.ListComp, ast.SetComp, ast.GeneratorExp]:
            weight = 1 + get_weight(given_tree.elt, countTokens=countTokens) + \
                     get_weight(given_tree.generators, countTokens=countTokens)
        elif type(given_tree) == ast.DictComp:
            weight = 1 + get_weight(given_tree.key, countTokens=countTokens) + \
                     get_weight(given_tree.value, countTokens=countTokens) + \
                     get_weight(given_tree.generators, countTokens=countTokens)
        elif type(given_tree) == ast.Compare:
            weight = len(given_tree.ops) + get_weight(given_tree.left, countTokens=countTokens) + \
                     get_weight(given_tree.comparators, countTokens=countTokens)
        elif type(given_tree) == ast.Call:
            functionWeight = get_weight(given_tree.func, countTokens=countTokens)
            functionWeight = functionWeight if functionWeight > 0 else 1
            argsWeight = get_weight(given_tree.args, countTokens=countTokens) + \
                         get_weight(given_tree.keywords, countTokens=countTokens)
            argsWeight = argsWeight if argsWeight > 0 else 1
            weight = functionWeight + argsWeight
        elif type(given_tree) == ast.Subscript:
            valueWeight = get_weight(given_tree.value, countTokens=countTokens)
            valueWeight = valueWeight if valueWeight > 0 else 1
            sliceWeight = get_weight(given_tree.slice, countTokens=countTokens)
            sliceWeight = sliceWeight if sliceWeight > 0 else 1
            weight = valueWeight + sliceWeight

        elif type(given_tree) == ast.Slice:
            weight = get_weight(given_tree.lower, countTokens=countTokens) + \
                     get_weight(given_tree.upper, countTokens=countTokens) + \
                     get_weight(given_tree.step, countTokens=countTokens)
            if weight == 0:
                weight = 1
        elif type(given_tree) == ast.ExtSlice:
            weight = get_weight(given_tree.dims, countTokens=countTokens)

        elif type(given_tree) == ast.comprehension:  # add 2 for for and in
            # and each of the if tokens
            weight = 2 + len(given_tree.ifs) + \
                     get_weight(given_tree.target, countTokens=countTokens) + \
                     get_weight(given_tree.iter, countTokens=countTokens) + \
                     get_weight(given_tree.ifs, countTokens=countTokens)
        elif type(given_tree) == ast.ExceptHandler:  # add 1 for except
            weight = 1 + get_weight(given_tree.type, countTokens=countTokens)
            # add 1 for as (if needed)
            weight += (1 if given_tree.name != None else 0) + \
                      get_weight(given_tree.name, countTokens=countTokens)
            weight += get_weight(given_tree.body, countTokens=countTokens)
        elif type(given_tree) == ast.arguments:
            weight = get_weight(given_tree.args, countTokens=countTokens) + \
                     get_weight(given_tree.vararg, countTokens=countTokens) + \
                     get_weight(given_tree.kwonlyargs, countTokens=countTokens) + \
                     get_weight(given_tree.kw_defaults, countTokens=countTokens) + \
                     get_weight(given_tree.kwarg, countTokens=countTokens) + \
                     get_weight(given_tree.posonlyargs, countTokens=countTokens)

        elif type(given_tree) == ast.arg:
            weight = 1 + get_weight(given_tree.annotation, countTokens=countTokens)
        elif type(given_tree) == ast.keyword:  # add 1 for identifier
            weight = 1 + get_weight(given_tree.value, countTokens=countTokens)
        elif type(given_tree) == ast.alias:  # 1 for name, 1 for as, 1 for asname
            weight = 1 + (2 if given_tree.asname != None else 0)
        elif type(given_tree) == ast.withitem:
            weight = get_weight(given_tree.context_expr, countTokens=countTokens) + \
                     get_weight(given_tree.optional_vars, countTokens=countTokens)
        elif type(given_tree) == ast.Str:
            if countTokens:
                weight = 1
            elif len(given_tree.s) >= 2 and given_tree.s[0] == "~" and given_tree.s[-1] == "~":
                weight = 0
            else:
                weight = 1
        elif type(given_tree) in [ast.Pass, ast.Break, ast.Continue,
                                  ast.Constant, ast.Name,
                                  ]:
            weight = 1
        elif type(given_tree) in [ast.And, ast.Or,
                                  ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Mod, ast.Pow,
                                  ast.LShift, ast.RShift, ast.BitOr, ast.BitXor,
                                  ast.BitAnd, ast.FloorDiv,
                                  ast.Invert, ast.Not, ast.UAdd, ast.USub,
                                  ast.Eq, ast.NotEq, ast.Lt, ast.LtE, ast.Gt, ast.GtE,
                                  ast.Is, ast.IsNot, ast.In, ast.NotIn,
                                  ast.Load, ast.Store, ast.Del, ast.AugLoad,
                                  ast.AugStore, ast.Param]:
            weight = 1
        else:
            log("diffAsts\tgetWeight\tMissing type in diffAsts: " + str(type(given_tree)), "bug")
            return 1
        setattr(given_tree, "treeWeight", weight)
        return weight


def getChanges(s, t, ignoreVariables=False):
    changes = diff_asts(s, t)
    for change in changes:
        change.start = s  # WARNING: should maybe have a deepcopy here? It will alias s
    return changes


def getChangesWeight(changes, countTokens=True):
    weight = 0
    for change in changes:
        if isinstance(change, AddVector):
            weight += get_weight(change.newSubtree, countTokens=countTokens)
        elif isinstance(change, DeleteVector):
            weight += get_weight(change.oldSubtree, countTokens=countTokens)
        elif isinstance(change, SwapVector):
            weight += 2  # only changing the positions
        elif isinstance(change, MoveVector):
            weight += 1  # only moving one item
        elif isinstance(change, SubVector):
            weight += abs(get_weight(change.newSubtree, countTokens=countTokens) - \
                          get_weight(change.oldSubtree, countTokens=countTokens))
        elif isinstance(change, SuperVector):
            weight += abs(get_weight(change.oldSubtree, countTokens=countTokens) - \
                          get_weight(change.newSubtree, countTokens=countTokens))
        else:
            weight += max(get_weight(change.oldSubtree, countTokens=countTokens),
                          get_weight(change.newSubtree, countTokens=countTokens))
    return weight


def distance(student_state: State, candidate: State, given_changes=None, forceReweight=False,
             ignoreVariables=False):
    """A method for comparing solution states, which returns a number between
        0 (identical solutions) and 1 (completely different)
  returns a tuple of (distance, changes)
  """
    # First weigh the trees, to propogate metadata
    if student_state is None or candidate is None:
        return 1  # can't compare to a None state
    if forceReweight:
        base_weight = max(get_weight(student_state.tree), get_weight(candidate.tree))
    else:
        if not hasattr(student_state, "treeWeight"):
            student_state.treeWeight = get_weight(student_state.tree)
        if not hasattr(candidate, "treeWeight"):
            candidate.treeWeight = get_weight(candidate.tree)
        base_weight = max(student_state.treeWeight, candidate.treeWeight)

    # Check if equal
    if student_state.tree == candidate.tree:
        return 0, []
    if given_changes is not None:
        changes = given_changes
    else:
        changes = getChanges(student_state.tree, candidate.tree, ignoreVariables=ignoreVariables)

    change_weight = getChangesWeight(changes)
    return 1.0 * change_weight / base_weight, changes

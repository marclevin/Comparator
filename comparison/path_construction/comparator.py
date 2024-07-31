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
                            compare_trees(x_subset[i][0], y_subset[j][0], check_equality=True)
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
                if compare_trees(x_subset[i][0], y_subset[j][0], check_equality=True) == 0:
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
                    if deleteAction <= action.new_subtree:
                        add_to_count += 1
                action.new_subtree += add_to_count
    if len(added_lines) > 0:
        for action in move_actions:
            if isinstance(action, MoveVector):
                add_to_count = 0
                for addAction in added_lines:
                    if addAction <= action.new_subtree:
                        add_to_count += 1
                action.new_subtree += add_to_count
    return move_actions


def diff_lists(list_x, list_y):
    if len(list_x) == 0 and len(list_y) == 0:
        return []
    # Check identical lists
    if list_x == list_y:
        return []
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
            if occurs_in(ast_x, ast_y):
                return [SubVector([], ast_x, ast_y)]
            elif occurs_in(ast_y, ast_x):
                return [SuperVector([], ast_x, ast_y)]
            else:
                return [ChangeVector([], ast_x, ast_y)]
        elif type(ast_x) is type(ast_y) is ast.Name:
            # TODO look into this
            if not built_in_name(ast_x.id) and not built_in_name(ast_y.id):
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
            except AttributeError:
                setattr(ast_x, field, None)
        return found_differences
    elif not isinstance(ast_x, ast.AST) and not isinstance(ast_y, ast.AST):
        if type(ast_x) is list and type(ast_y) is list:
            return diff_lists(ast_x, ast_y)
        elif ast_x == ast_y and type(ast_x) is not type(ast_y):
            # Type check.
            return [ChangeVector([], ast_x, ast_y)]  # they're primitive, so just switch them
        else:  # equal values
            return []
    else:  # Two mismatched types
        return [ChangeVector([], ast_x, ast_y)]


def sum_weight(bases):
    return sum(map(lambda x: get_weight(x), bases))


def get_weight(given_tree, count_tokens=True):
    """Get the size of the given tree"""
    if given_tree is None:
        return 0
    elif type(given_tree) is list:
        return sum(map(lambda token: get_weight(token, count_tokens), given_tree))
    elif not isinstance(given_tree, ast.AST):
        return 1
    else:  # Otherwise, it's an AST node
        if hasattr(given_tree, "treeWeight"):
            return given_tree.treeWeight
        weight = 0
        if type(given_tree) in [ast.Module, ast.Interactive, ast.Suite]:
            weight = get_weight(given_tree.body, count_tokens=count_tokens)
        elif type(given_tree) is ast.Expression:
            weight = get_weight(given_tree.body, count_tokens=count_tokens)
        elif type(given_tree) is ast.FunctionDef:
            # add 1 for function name
            weight = 1 + get_weight(given_tree.args, count_tokens=count_tokens) + \
                     get_weight(given_tree.body, count_tokens=count_tokens) + \
                     get_weight(given_tree.decorator_list, count_tokens=count_tokens) + \
                     get_weight(given_tree.returns, count_tokens=count_tokens)
        elif type(given_tree) is ast.ClassDef:
            # add 1 for class name
            weight = 1 + sum_weight(given_tree.bases) + \
                     sum_weight(given_tree.keywords) + \
                     get_weight(given_tree.body, count_tokens=count_tokens) + \
                     get_weight(given_tree.decorator_list, count_tokens=count_tokens)
        elif type(given_tree) in [ast.Return, ast.Yield, ast.Attribute, ast.Starred]:
            # add 1 for action name
            weight = 1 + get_weight(given_tree.value, count_tokens=count_tokens)
        elif type(given_tree) is ast.Delete:  # add 1 for del
            weight = 1 + get_weight(given_tree.targets, count_tokens=count_tokens)
        elif type(given_tree) is ast.Assign:  # add 1 for =
            weight = 1 + get_weight(given_tree.targets, count_tokens=count_tokens) + \
                     get_weight(given_tree.value, count_tokens=count_tokens)
        elif type(given_tree) is ast.AugAssign:
            weight = get_weight(given_tree.target, count_tokens=count_tokens) + \
                     get_weight(given_tree.op, count_tokens=count_tokens) + \
                     get_weight(given_tree.value, count_tokens=count_tokens)
        elif type(given_tree) is ast.For:  # add 1 for 'for' and 1 for 'in'
            weight = 2 + get_weight(given_tree.target, count_tokens=count_tokens) + \
                     get_weight(given_tree.iter, count_tokens=count_tokens) + \
                     get_weight(given_tree.body, count_tokens=count_tokens) + \
                     get_weight(given_tree.orelse, count_tokens=count_tokens)
        elif type(given_tree) in [ast.While, ast.If]:
            # add 1 for while/if
            weight = 1 + get_weight(given_tree.test, count_tokens=count_tokens) + \
                     get_weight(given_tree.body, count_tokens=count_tokens)
            if len(given_tree.orelse) > 0:  # add 1 for else
                weight += 1 + get_weight(given_tree.orelse, count_tokens=count_tokens)
        elif type(given_tree) is ast.With:  # add 1 for with
            weight = 1 + get_weight(given_tree.items, count_tokens=count_tokens) + \
                     get_weight(given_tree.body, count_tokens=count_tokens)
        elif type(given_tree) is ast.Raise:  # add 1 for raise
            weight = 1 + get_weight(given_tree.exc, count_tokens=count_tokens) + \
                     get_weight(given_tree.cause, count_tokens=count_tokens)
        elif type(given_tree) is ast.Try:  # add 1 for try
            weight = 1 + get_weight(given_tree.body, count_tokens=count_tokens) + \
                     get_weight(given_tree.handlers, count_tokens=count_tokens)
            if len(given_tree.orelse) > 0:  # add 1 for else
                weight += 1 + get_weight(given_tree.orelse, count_tokens=count_tokens)
            if len(given_tree.finalbody) > 0:  # add 1 for finally
                weight += 1 + get_weight(given_tree.finalbody, count_tokens=count_tokens)
        elif type(given_tree) is ast.Assert:  # add 1 for assert
            weight = 1 + get_weight(given_tree.test, count_tokens=count_tokens) + \
                     get_weight(given_tree.msg, count_tokens=count_tokens)
        elif type(given_tree) in [ast.Import, ast.Global]:  # add 1 for function name
            weight = 1 + get_weight(given_tree.names, count_tokens=count_tokens)
        elif type(given_tree) is ast.ImportFrom:  # add 3 for from module import
            weight = 3 + get_weight(given_tree.names, count_tokens=count_tokens)
        elif type(given_tree) in [ast.Expr, ast.Index]:
            weight = get_weight(given_tree.value, count_tokens=count_tokens)
            if weight == 0:
                weight = 1
        elif type(given_tree) is ast.BoolOp:  # add 1 for each op
            weight = (len(given_tree.values) - 1) + \
                     get_weight(given_tree.values, count_tokens=count_tokens)
        elif type(given_tree) is ast.BinOp:  # add 1 for op
            weight = 1 + get_weight(given_tree.left, count_tokens=count_tokens) + \
                     get_weight(given_tree.right, count_tokens=count_tokens)
        elif type(given_tree) is ast.UnaryOp:  # add 1 for operator
            weight = 1 + get_weight(given_tree.operand, count_tokens=count_tokens)
        elif type(given_tree) is ast.Lambda:  # add 1 for lambda
            weight = 1 + get_weight(given_tree.args, count_tokens=count_tokens) + \
                     get_weight(given_tree.body, count_tokens=count_tokens)
        elif type(given_tree) is ast.IfExp:  # add 2 for if and else
            weight = 2 + get_weight(given_tree.test, count_tokens=count_tokens) + \
                     get_weight(given_tree.body, count_tokens=count_tokens) + \
                     get_weight(given_tree.orelse, count_tokens=count_tokens)
        elif type(given_tree) is ast.Dict:  # return 1 if empty dictionary
            weight = 1 + get_weight(given_tree.keys, count_tokens=count_tokens) + \
                     get_weight(given_tree.values, count_tokens=count_tokens)
        elif type(given_tree) in [ast.Set, ast.List, ast.Tuple]:
            weight = 1 + get_weight(given_tree.elts, count_tokens=count_tokens)
        elif type(given_tree) in [ast.ListComp, ast.SetComp, ast.GeneratorExp]:
            weight = 1 + get_weight(given_tree.elt, count_tokens=count_tokens) + \
                     get_weight(given_tree.generators, count_tokens=count_tokens)
        elif type(given_tree) is ast.DictComp:
            weight = 1 + get_weight(given_tree.key, count_tokens=count_tokens) + \
                     get_weight(given_tree.value, count_tokens=count_tokens) + \
                     get_weight(given_tree.generators, count_tokens=count_tokens)
        elif type(given_tree) is ast.Compare:
            weight = len(given_tree.ops) + get_weight(given_tree.left, count_tokens=count_tokens) + \
                     get_weight(given_tree.comparators, count_tokens=count_tokens)
        elif type(given_tree) is ast.Call:
            function_weight = get_weight(given_tree.func, count_tokens=count_tokens)
            function_weight = function_weight if function_weight > 0 else 1
            args_weight = get_weight(given_tree.args, count_tokens=count_tokens) + \
                          get_weight(given_tree.keywords, count_tokens=count_tokens)
            args_weight = args_weight if args_weight > 0 else 1
            weight = function_weight + args_weight
        elif type(given_tree) is ast.Subscript:
            value_weight = get_weight(given_tree.value, count_tokens=count_tokens)
            value_weight = value_weight if value_weight > 0 else 1
            slice_weight = get_weight(given_tree.slice, count_tokens=count_tokens)
            slice_weight = slice_weight if slice_weight > 0 else 1
            weight = value_weight + slice_weight

        elif type(given_tree) is ast.Slice:
            weight = get_weight(given_tree.lower, count_tokens=count_tokens) + \
                     get_weight(given_tree.upper, count_tokens=count_tokens) + \
                     get_weight(given_tree.step, count_tokens=count_tokens)
            if weight == 0:
                weight = 1
        elif type(given_tree) is ast.ExtSlice:
            weight = get_weight(given_tree.dims, count_tokens=count_tokens)

        elif type(given_tree) is ast.comprehension:  # add 2 for for and in
            # and each of the if tokens
            weight = 2 + len(given_tree.ifs) + \
                     get_weight(given_tree.target, count_tokens=count_tokens) + \
                     get_weight(given_tree.iter, count_tokens=count_tokens) + \
                     get_weight(given_tree.ifs, count_tokens=count_tokens)
        elif type(given_tree) is ast.ExceptHandler:  # add 1 for except
            weight = 1 + get_weight(given_tree.type, count_tokens=count_tokens)
            # add 1 for as (if needed)
            weight += (1 if given_tree.name is not None else 0) + \
                      get_weight(given_tree.name, count_tokens=count_tokens)
            weight += get_weight(given_tree.body, count_tokens=count_tokens)
        elif type(given_tree) is ast.arguments:
            weight = get_weight(given_tree.args, count_tokens=count_tokens) + \
                     get_weight(given_tree.vararg, count_tokens=count_tokens) + \
                     get_weight(given_tree.kwonlyargs, count_tokens=count_tokens) + \
                     get_weight(given_tree.kw_defaults, count_tokens=count_tokens) + \
                     get_weight(given_tree.kwarg, count_tokens=count_tokens) + \
                     get_weight(given_tree.posonlyargs, count_tokens=count_tokens)

        elif type(given_tree) is ast.arg:
            weight = 1 + get_weight(given_tree.annotation, count_tokens=count_tokens)
        elif type(given_tree) is ast.keyword:  # add 1 for identifier
            weight = 1 + get_weight(given_tree.value, count_tokens=count_tokens)
        elif type(given_tree) is ast.alias:  # 1 for name, 1 for as, 1 for asname
            weight = 1 + (2 if given_tree.asname is not None else 0)
        elif type(given_tree) is ast.withitem:
            weight = get_weight(given_tree.context_expr, count_tokens=count_tokens) + \
                     get_weight(given_tree.optional_vars, count_tokens=count_tokens)
        elif type(given_tree) is ast.Str:
            if count_tokens:
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


def get_changes(student_code_tree: ast.AST, candidate_code_tree: ast.AST):
    changes = diff_asts(student_code_tree, candidate_code_tree)
    for change in changes:
        change.start = student_code_tree
    return changes


def get_changes_weight(changes, countTokens=True):
    weight = 0
    for change in changes:
        if isinstance(change, AddVector):
            weight += get_weight(change.new_subtree, count_tokens=countTokens)
        elif isinstance(change, DeleteVector):
            weight += get_weight(change.old_subtree, count_tokens=countTokens)
        elif isinstance(change, SwapVector):
            weight += 2  # only changing the positions
        elif isinstance(change, MoveVector):
            weight += 1  # only moving one item
        elif isinstance(change, SubVector):
            weight += abs(get_weight(change.new_subtree, count_tokens=countTokens) - \
                          get_weight(change.old_subtree, count_tokens=countTokens))
        elif isinstance(change, SuperVector):
            weight += abs(get_weight(change.old_subtree, count_tokens=countTokens) - \
                          get_weight(change.new_subtree, count_tokens=countTokens))
        else:
            weight += max(get_weight(change.old_subtree, count_tokens=countTokens),
                          get_weight(change.new_subtree, count_tokens=countTokens))
    return weight


def distance(student_state: State, candidate: State, given_changes=None, forceReweight=False,
             ignoreVariables=False):
    """A method for comparing solution states, which returns a number between
        0 (identical solutions) and 1 (completely different)
  returns a tuple of (distance, changes)
  """
    # First weigh the trees, to propagate metadata
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
    if student_state.tree is candidate.tree:
        return 0, []
    if given_changes is not None:
        changes = given_changes
    else:
        changes = get_changes(student_state.tree, candidate.tree)

    change_weight = get_changes_weight(changes)
    return 1.0 * change_weight / base_weight, changes

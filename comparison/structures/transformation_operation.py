import ast

from comparison.utils.astTools import compare_trees, deepcopy, cmp
from comparison.utils.display import print_function
from comparison.utils.tools import log


def create_map_dict(map_dict, tree_spot):
    # the 'pos' element holds a list where positions map to original positions.
    # so if we have the list [ 0, 3, 4 ], then the first line is in the original place,
    # but the second and third lines were deleted, so 3 and 4 have moved in their palces.

    # Check for None to avoid AttributeError
    if tree_spot is None:
        return None, map_dict

    map_dict["len"] = len(tree_spot)
    map_dict["pos"] = list(range(len(tree_spot)))
    for i in map_dict["pos"]:
        map_dict[i] = {}


class ChangeOperation:
    start = None
    path = None
    old_subtree = None
    new_subtree = None

    def __init__(self, path, old_subtree, new_subtree, start=None):
        self.start = start
        self.path = path
        self.old_subtree = old_subtree
        self.new_subtree = new_subtree

    def __repr__(self):
        old_str = print_function(self.old_subtree, 0) if isinstance(self.old_subtree, ast.AST) else repr(
            self.old_subtree)
        new_str = print_function(self.new_subtree, 0) if isinstance(self.new_subtree, ast.AST) else repr(
            self.new_subtree)
        return old_str + " - " + new_str + " : " + str(self.path)

    def __cmp__(self, other):
        if not isinstance(other, ChangeOperation):
            return -1
        c1 = cmp(self.path, other.path)
        if c1 != 0:
            return c1
        else:
            c2 = compare_trees(self.old_subtree, other.old_subtree)
            if c2 != 0:
                return c2
            else:
                c3 = compare_trees(self.new_subtree, other.new_subtree)
                if c3 != 0:
                    return c3
                else:
                    return compare_trees(self.start, other.start)

    def deepcopy(self):
        path = self.path[:] if self.path is not None else None
        c = ChangeOperation(path, deepcopy(self.old_subtree), deepcopy(self.new_subtree), start=deepcopy(self.start))
        return c

    def update_tree(self, tree_spot, map_dict, path=None):
        # Update the positions in the path to account for the mapDict
        if path is None:
            path = self.path
        cur_key = "start"
        for i in range(len(path) - 1, 0, -1):
            move = path[i]
            map_dict = map_dict[cur_key]
            if type(move) is tuple:
                if move[0] not in map_dict:
                    map_dict[move[0]] = {}
                cur_key = move[0]  # No trouble here
                tree_spot = getattr(tree_spot, move[0])
            elif type(move) is int:
                if "pos" not in map_dict:  # set up data for original position and length
                    create_map_dict(map_dict, tree_spot)
                real_move = map_dict["pos"].index(move)
                path[i] = real_move  # update the change path! This is the key action!
                cur_key = move  # use the original here, as keys aren't changed in the mapDict repr
                tree_spot = tree_spot[real_move]
        map_dict = map_dict[cur_key]
        return tree_spot, map_dict

    def update(self, new_start, map_dict):
        # WARNING: mapDict will be modified!
        self.start = new_start
        tree_spot, map_dict = self.update_tree(new_start, map_dict)

        # Update locations in the last position
        location = self.path[0]
        if type(tree_spot) is list and "pos" not in map_dict:
            create_map_dict(map_dict, tree_spot)

        if type(location) is int and type(tree_spot) is list:
            self.path[0] = map_dict["pos"].index(location)

    def traverse_tree(self, tree, path=None):
        if path is None:
            path = self.path
        tree_spot = tree
        for i in range(len(path) - 1, 0, -1):
            move = path[i]
            if type(move) is tuple:
                if hasattr(tree_spot, move[0]):
                    tree_spot = getattr(tree_spot, move[0])
                else:
                    log("Change Vector\ttraverseTree\t\tMissing attr: " + str(move[0]) + "\n" + print_function(tree),
                        "bug")
                    return -99
            elif type(move) is int:
                if type(tree_spot) is list:
                    if 0 <= move < len(tree_spot):
                        tree_spot = tree_spot[move]
                    else:
                        log("Change Vector\ttraverseTree\t\tMissing position: " + str(move) + "," + str(
                            tree_spot) + "\n" + print_function(tree), "bug")
                        return -99
                else:
                    log("Change Vector\ttraverseTree\t\tNot a list: " + str(tree_spot) + "\n" + print_function(tree),
                        "bug")
                    return -99

            else:  # wat?
                log("Change Vector\ttraverseTree\t\tBad Path: " + str(move) + "\n" + print_function(tree), "bug")
                return -99
        return tree_spot

    def apply_change(self, caller=None):
        tree = deepcopy(self.start)
        tree_spot = self.traverse_tree(tree)
        if tree_spot == -99:
            return None

        # Make the change in the last position
        location = self.path[0]
        if type(location) is tuple and hasattr(tree_spot, location[0]):
            old_spot = getattr(tree_spot, location[0])
            # Make life easier for ourselves when applying multiple changes at once
            if self.new_subtree is not None and old_spot is not None:
                if hasattr(old_spot, "lineno"):
                    self.new_subtree.lineno = old_spot.lineno
                if hasattr(old_spot, "col_offset"):
                    self.new_subtree.col_offset = old_spot.col_offset
            if compare_trees(old_spot, self.old_subtree, check_equality=True) != 0:
                log("ChangeVector\tapplyChange\t" + str(caller) + "\t" + "Change old values don't match: " + str(
                    self) + "\n" + str(print_function(self.start)), "bug")
            setattr(tree_spot, location[0], self.new_subtree)
            # SPECIAL CASE. If we're changing the variable name, get rid of metadata
            if type(tree_spot) is ast.Name and location[0] == "id":
                if hasattr(tree_spot, "originalId"):
                    del tree_spot.originalId
                if hasattr(tree_spot, "dontChangeName"):
                    del tree_spot.dontChangeName
                if hasattr(tree_spot, "randomVar"):
                    del tree_spot.randomVar
            elif type(tree_spot) is ast.arg and location[0] == "arg":
                if hasattr(tree_spot, "originalId"):
                    del tree_spot.originalId
                if hasattr(tree_spot, "dontChangeName"):
                    del tree_spot.dontChangeName
                if hasattr(tree_spot, "randomVar"):
                    del tree_spot.randomVar
        elif type(location) is int and type(tree_spot) is list:
            # Need to swap out whatever is in this location
            if 0 <= location < len(tree_spot):
                if hasattr(tree_spot[location], "lineno"):
                    self.new_subtree.lineno = tree_spot[location].lineno
                if hasattr(tree_spot[location], "col_offset"):
                    self.new_subtree.col_offset = tree_spot[location].col_offset
                tree_spot[location] = self.new_subtree
            else:
                log("ChangeVector\tapplyChange\tDoesn't fit in list: " + str(location) + "\n" + print_function(
                    self.start), "bug")
        else:
            log("ChangeVector\tapplyChange\t\tBroken at: " + str(location), "bug")
        return tree

    def is_replace_vector(self):
        return not (isinstance(self, SubOperation) or isinstance(self, SuperOperation) or isinstance(self,
                                                                                                     AddOperation) or isinstance(
            self, DeleteOperation) or isinstance(self, SwapOperation) or isinstance(self, MoveOperation))


class SubOperation(ChangeOperation):
    # This class represents a vector where the value is a subexpression of the needed value

    def __cmp__(self, other):
        if (not isinstance(other, ChangeOperation)) or isinstance(other, SuperOperation) or \
                isinstance(other, AddOperation) or isinstance(other, DeleteOperation) or \
                isinstance(other, SwapOperation) or isinstance(other, MoveOperation):
            return -1
        if not isinstance(other, SubOperation):
            return 1
        return ChangeOperation.__cmp__(self, other)

    def __repr__(self):
        old_str = print_function(self.old_subtree, 0) if isinstance(self.old_subtree, ast.AST) else repr(
            self.old_subtree)
        new_str = print_function(self.new_subtree, 0) if isinstance(self.new_subtree, ast.AST) else repr(
            self.new_subtree)
        return "Sub: " + old_str + " - " + new_str + " : " + str(self.path)

    def deepcopy(self):
        path = self.path[:] if self.path is not None else None
        c = SubOperation(path, deepcopy(self.old_subtree), deepcopy(self.new_subtree), start=deepcopy(self.start))
        return c


class SuperOperation(ChangeOperation):
    # This class represents a vector where the value contains the needed value as a subexpression

    def __cmp__(self, other):
        if (not isinstance(other, ChangeOperation)) or isinstance(other, AddOperation) or \
                isinstance(other, DeleteOperation) or isinstance(other, SwapOperation) or \
                isinstance(other, MoveOperation):
            return -1
        if not isinstance(other, SuperOperation):
            return 1
        return ChangeOperation.__cmp__(self, other)

    def __repr__(self):
        old_str = print_function(self.old_subtree, 0) if isinstance(self.old_subtree, ast.AST) else repr(
            self.old_subtree)
        new_str = print_function(self.new_subtree, 0) if isinstance(self.new_subtree, ast.AST) else repr(
            self.new_subtree)
        return "Super: " + old_str + " - " + new_str + " : " + str(self.path)

    def deepcopy(self):
        path = self.path[:] if self.path is not None else None
        c = SuperOperation(path, deepcopy(self.old_subtree), deepcopy(self.new_subtree), start=deepcopy(self.start))
        return c


class AddOperation(ChangeOperation):
    # This class represents where lines are added to a list

    def __cmp__(self, other):
        if (not isinstance(other, ChangeOperation)) or isinstance(other, DeleteOperation) or \
                isinstance(other, SwapOperation) or isinstance(other, MoveOperation):
            return -1
        if not isinstance(other, AddOperation):
            return 1
        return ChangeOperation.__cmp__(self, other)

    def __repr__(self):
        old_str = print_function(self.old_subtree, 0) if isinstance(self.old_subtree, ast.AST) else repr(
            self.old_subtree)
        new_str = print_function(self.new_subtree, 0) if isinstance(self.new_subtree, ast.AST) else repr(
            self.new_subtree)
        return "Add: " + old_str + " - " + new_str + " : " + str(self.path)

    def deepcopy(self):
        path = self.path[:] if self.path is not None else None
        c = AddOperation(path, deepcopy(self.old_subtree), deepcopy(self.new_subtree), start=deepcopy(self.start))
        return c

    def apply_change(self, caller=None):
        tree = deepcopy(self.start)
        tree_spot = self.traverse_tree(tree)
        if tree_spot == -99:
            return None

        # Make the change in the last position
        location = self.path[0]
        if type(tree_spot) is list:
            # Add the new line
            tree_spot.insert(location, self.new_subtree)
        else:
            log("AddVector\tapplyChange\t\tBroken at: " + str(location), "bug")
            return None
        return tree

    def update(self, new_start, map_dict):
        # WARNING: mapDict will be modified!
        self.start = new_start
        tree_spot, map_dict = self.update_tree(new_start, map_dict)

        # Update locations in the last position
        location = self.path[0]
        if "pos" not in map_dict:
            create_map_dict(map_dict, tree_spot)

        # Update based on the original position
        if location != map_dict["len"]:
            if location in map_dict["pos"]:
                location = map_dict["pos"].index(location)
            else:
                if location < map_dict["len"]:
                    # Find the previous location and put this after it
                    i = len(map_dict["pos"]) - 1
                    while map_dict["pos"][i] == -1 and i >= 0:
                        i -= 1
                    if i >= 0:
                        i += 1
                        location = i
                    else:
                        log("AddVector\tupdate\t\tMissing position: " + str(location) + "," + str(map_dict["pos"]),
                            "bug")
                        return
        else:  # if it IS equal to the length, put it in the back
            location = len(map_dict["pos"])

        self.path[0] = location  # make sure to update!

        # Add the new line
        map_dict["pos"].insert(location, -1)


class DeleteOperation(ChangeOperation):
    # This class represents a change where lines are removed from a list
    def __cmp__(self, other):
        if (not isinstance(other, ChangeOperation)) or isinstance(other, SwapOperation) or \
                isinstance(other, MoveOperation):
            return -1
        if not isinstance(other, DeleteOperation):
            return 1
        return ChangeOperation.__cmp__(self, other)

    def __repr__(self):
        old_str = print_function(self.old_subtree, 0) if isinstance(self.old_subtree, ast.AST) else repr(
            self.old_subtree)
        new_str = print_function(self.new_subtree, 0) if isinstance(self.new_subtree, ast.AST) else repr(
            self.new_subtree)
        return "Delete: " + old_str + " - " + new_str + " : " + str(self.path)

    def deepcopy(self):
        path = self.path[:] if self.path is not None else None
        c = DeleteOperation(path, deepcopy(self.old_subtree), deepcopy(self.new_subtree), start=deepcopy(self.start))
        return c

    def apply_change(self, caller=None):
        tree = deepcopy(self.start)
        tree_spot = self.traverse_tree(tree)
        if tree_spot == -99:
            return None

        # Make the change in the last position
        location = self.path[0]
        if type(tree_spot) is list:
            # Remove the old line
            if location < len(tree_spot):
                if compare_trees(tree_spot[location], self.old_subtree, check_equality=True) != 0:
                    log("DeleteVector\tapplyChange\t" + str(caller) + "\t" + "Delete old values don't match: " + str(
                        self) + "\n" + str(print_function(self.start)), "bug")
                del tree_spot[location]
            else:
                log("DeleteVector\tapplyChange\t\tBad location: " + str(location) + "\t" + str(self.old_subtree), "bug")
                return None
        else:
            log("DeleteVector\tapplyChange\t\tBroken at: " + str(location), "bug")
            return None
        return tree

    def update(self, new_start, map_dict):
        # WARNING: mapDict will be modified!
        self.start = new_start
        tree_spot, map_dict = self.update_tree(new_start, map_dict)

        # Update locations in the last position
        location = self.path[0]
        if "pos" not in map_dict:
            create_map_dict(map_dict, tree_spot)

        # Update based on the original position
        location = map_dict["pos"].index(location)

        self.path[0] = location  # make sure to update!

        # Remove the old line
        map_dict["pos"].pop(location)


class SwapOperation(ChangeOperation):
    # This class represents a change where two lines are swapped
    old_path = new_path = None

    def __cmp__(self, other):
        if (not isinstance(other, ChangeOperation)) or isinstance(other, MoveOperation):
            return -1
        if not isinstance(other, SwapOperation):
            return 1
        return ChangeOperation.__cmp__(self, other)

    def __repr__(self):
        old_str = print_function(self.old_subtree, 0) if isinstance(self.old_subtree, ast.AST) else repr(
            self.old_subtree)
        new_str = print_function(self.new_subtree, 0) if isinstance(self.new_subtree, ast.AST) else repr(
            self.new_subtree)
        if self.old_path is not None:
            return "Swap: " + old_str + " : " + str(self.old_path) + "\n" + \
                new_str + " : " + str(self.new_path)
        else:
            return "Swap: " + old_str + " - " + new_str + " : " + str(self.path)

    def deepcopy(self):
        path = self.path[:] if self.path is not None else None
        c = SwapOperation(path, deepcopy(self.old_subtree), deepcopy(self.new_subtree), start=deepcopy(self.start))
        c.old_path = self.old_path[:] if self.old_path is not None else None
        c.new_path = self.new_path[:] if self.new_path is not None else None
        return c

    def apply_change(self, caller=None):
        tree = deepcopy(self.start)

        if self.old_path is None:
            tree_spot = self.traverse_tree(tree)
            if tree_spot == -99:
                return None

            if type(tree_spot) is list and self.old_subtree < len(tree_spot) and \
                    self.new_subtree < len(tree_spot):
                (tree_spot[self.old_subtree], tree_spot[self.new_subtree]) = (
                    tree_spot[self.new_subtree], tree_spot[self.old_subtree])
            else:
                log("SwapVector\tapplyChange\t\tBroken at: " + str(tree_spot), "bug")
                return None
        else:
            old_tree_spot = self.traverse_tree(tree, path=self.old_path)
            new_tree_spot = self.traverse_tree(tree, path=self.new_path)
            if old_tree_spot == -99 or new_tree_spot == -99:
                return None

            if type(self.old_path[0]) is int:
                tmp_old_value = old_tree_spot[self.old_path[0]]
            else:
                tmp_old_value = getattr(old_tree_spot, self.old_path[0][0])

            if type(self.new_path[0]) is int:
                tmp_new_value = new_tree_spot[self.new_path[0]]
            else:
                tmp_new_value = getattr(new_tree_spot, self.new_path[0][0])

            if type(self.old_path[0]) is int:
                old_tree_spot[self.old_path[0]] = tmp_new_value
            else:
                setattr(old_tree_spot, self.old_path[0][0], tmp_new_value)

            if type(self.new_path[0]) is int:
                new_tree_spot[self.new_path[0]] = tmp_old_value
            else:
                setattr(new_tree_spot, self.new_path[0][0], tmp_old_value)
        return tree

    def update(self, new_start, map_dict):
        # WARNING: mapDict will be modified!
        self.start = new_start

        if "moved" in map_dict:
            map_dict["moved"] += [self.old_subtree, self.new_subtree]
        else:
            map_dict["moved"] = [self.old_subtree, self.new_subtree]

        if self.old_path is None:
            tree_spot, map_dict = self.update_tree(new_start, map_dict)
            if "pos" not in map_dict:
                create_map_dict(map_dict, tree_spot)

            # Update based on the original position
            self.old_subtree = map_dict["pos"].index(self.old_subtree)
            self.new_subtree = map_dict["pos"].index(self.new_subtree)

            (map_dict["pos"][self.old_subtree], map_dict["pos"][self.new_subtree]) = (
                map_dict["pos"][self.new_subtree], map_dict["pos"][self.old_subtree])
        else:
            old_tree_spot, old_map_dict = self.update_tree(new_start, map_dict, path=self.old_path)
            new_tree_spot, new_map_dict = self.update_tree(new_start, map_dict, path=self.new_path)
            if type(old_tree_spot) is int:
                if "pos" not in old_map_dict:
                    create_map_dict(old_map_dict, old_tree_spot)
                self.old_subtree = old_map_dict["pos"].index(self.old_subtree)
            if type(new_tree_spot) is int:
                if "pos" not in new_map_dict:
                    create_map_dict(new_map_dict, new_tree_spot)
                self.new_subtree = new_map_dict["pos"].index(self.new_subtree)
            if type(old_tree_spot) is type(new_tree_spot) is int:
                (old_map_dict["pos"][self.old_subtree], new_map_dict["pos"][self.new_subtree]) = (
                    new_map_dict["pos"][self.new_subtree], old_map_dict["pos"][self.old_subtree])

    def get_swaps(self):
        if self.old_path is None:
            tree_spot = self.traverse_tree(self.start)
            if type(tree_spot) is list and self.old_subtree < len(tree_spot) and \
                    self.new_subtree < len(tree_spot):
                return tree_spot[self.old_subtree], tree_spot[self.new_subtree]
            else:
                log("SwapVector\tgetSwaps\tBroken: \n" + print_function(tree_spot, 0) + "," + print_function(
                    self.old_subtree, 0) + "," + print_function(self.new_subtree, 0) + "\n" + print_function(self.start,
                                                                                                             0),
                    "bug")
        else:
            old_tree_spot = self.traverse_tree(self.start, path=self.old_path)
            new_tree_spot = self.traverse_tree(self.start, path=self.new_path)
            if type(self.old_path[0]) is int and type(old_tree_spot) is list and self.old_path[0] < len(old_tree_spot):
                old_value = old_tree_spot[self.old_path[0]]
            elif type(self.old_path[0]) == tuple and hasattr(old_tree_spot, self.old_path[0][0]):
                old_value = getattr(old_tree_spot, self.old_path[0][0])
            else:
                log("SwapVector\tgetSwaps\tBroken oldValue")
                old_value = None

            if type(self.new_path[0]) is int and type(new_tree_spot) is list and self.new_path[0] < len(new_tree_spot):
                new_value = new_tree_spot[self.new_path[0]]
            elif type(self.new_path[0]) is tuple and hasattr(new_tree_spot, self.new_path[0][0]):
                new_value = getattr(new_tree_spot, self.new_path[0][0])
            else:
                log("SwapVector\tgetSwaps\tBroken newValue")
                new_value = None

            return old_value, new_value
        return None, None

    def get_swapped_paths(self):
        if self.old_path is None:
            return self.path, self.path
        else:
            return self.old_path, self.new_path


class MoveOperation(ChangeOperation):
    # This class represents a change where one line is moved somewhere else in the list

    def __cmp__(self, other):
        if not isinstance(other, ChangeOperation):
            return -1
        if not isinstance(other, MoveOperation):
            return 1
        return ChangeOperation.__cmp__(self, other)

    def __repr__(self):
        old_str = print_function(self.old_subtree, 0) if isinstance(self.old_subtree, ast.AST) else repr(
            self.old_subtree)
        new_str = print_function(self.new_subtree, 0) if isinstance(self.new_subtree, ast.AST) else repr(
            self.new_subtree)
        return "Move: " + old_str + " - " + new_str + " : " + str(self.path)

    def deepcopy(self):
        path = self.path[:] if self.path is not None else None
        c = MoveOperation(path, deepcopy(self.old_subtree), deepcopy(self.new_subtree), start=deepcopy(self.start))
        return c

    def apply_change(self, caller=None):
        tree = deepcopy(self.start)
        tree_spot = self.traverse_tree(tree)
        if tree_spot == -99:
            return None

        if type(tree_spot) is list and self.old_subtree < len(tree_spot) and self.new_subtree < len(tree_spot):
            # We'll remove the item from the tree, then put it back in
            item = tree_spot.pop(self.old_subtree)
            tree_spot.insert(self.new_subtree, item)
        else:
            log("MoveVector\tapplyChange\t\tBroken at: " + str(tree_spot), "bug")
            return None
        return tree

    def update(self, new_start, map_dict):
        # WARNING: mapDict will be modified!
        self.start = new_start
        tree_spot, map_dict = self.update_tree(new_start, map_dict)

        if "moved" in map_dict:
            map_dict["moved"].append(self.old_subtree)
        else:
            map_dict["moved"] = [self.old_subtree]

        if "pos" not in map_dict:
            create_map_dict(map_dict, tree_spot)

        # Update based on the original position.
        if self.old_subtree not in map_dict["pos"]:
            log("MoveVector\tupdate\t\tCan't find old subtree: " + str(self.old_subtree) + "," + str(map_dict["pos"]),
                "bug")
            return

        if self.new_subtree in map_dict["moved"]:
            next_pos = self.new_subtree + 1
            while (map_dict["len"] < next_pos) and (next_pos in map_dict["moved"] or next_pos not in map_dict["pos"]):
                next_pos += 1
            if next_pos >= map_dict["len"]:
                log("ChangeVector\tMoveVector\tupdate\tBad Position!! " + str(self) + ";" + str(map_dict), "bug")
            else:
                self.new_subtree = next_pos
        else:
            if self.new_subtree not in map_dict["pos"]:
                if self.new_subtree < min(map_dict["pos"]):
                    self.new_subtree = min(map_dict["pos"])  # just go to the lowest position
                elif self.new_subtree > max(map_dict["pos"]):
                    self.new_subtree = max(map_dict["pos"])  # go to the highest position
                else:
                    higher = self.new_subtree
                    while higher not in map_dict["pos"]:
                        higher += 1
                    self.new_subtree = higher  # go to the next line, as the better place to insert
        self.old_subtree = map_dict["pos"].index(self.old_subtree)
        self.new_subtree = map_dict["pos"].index(self.new_subtree)
        index = map_dict["pos"].pop(self.old_subtree)
        map_dict["pos"].insert(self.new_subtree, index)

    def getItems(self):
        tree_spot = self.traverse_tree(self.start)
        return tree_spot[self.old_subtree], tree_spot[self.new_subtree]

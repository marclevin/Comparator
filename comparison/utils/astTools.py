import copy
import pickle

from comparison.structures.namesets import *
from comparison.utils.display import *
from comparison.utils.tools import *


def cmp(a, b):
    if type(a) is type(b) is complex:
        return (a.real > b.real) - (a.real < b.real)
    if type(a) is type(b) is range:
        return (a.start > b.start) - (a.start < b.start) or \
            (a.stop > b.stop) - (a.stop < b.stop) or \
            (a.step > b.step) - (a.step < b.step)
    if type(a) is not type(b):
        return (str(type(a)) > str(type(b))) - (str(type(a)) < str(type(b)))
    return (a > b) - (a < b)


def tree_to_str(a):
    return repr(pickle.dumps(a))


def str_to_tree(s):
    return pickle.loads(eval(s))


def built_in_name(name_id):
    """Determines whether the given id is a built-in name"""
    if name_id in built_in_names + exception_classes:
        return True
    elif name_id in built_in_functions.keys():
        return True
    elif name_id in list(all_python_functions.keys()) + supported_libraries:
        return False


def imported_name(id, importList):
    for imp in importList:
        if type(imp) is ast.Import:
            for name in imp.names:
                if hasattr(name, "asname") and name.asname is not None:
                    if id == name.asname:
                        return True
                else:
                    if id == name.name:
                        return True
        elif type(imp) is ast.ImportFrom:
            if hasattr(imp, "module"):
                if imp.module in supported_libraries:
                    lib_map = libraryMap[imp.module]
                    for name in imp.names:
                        if hasattr(name, "asname") and name.asname is not None:
                            if id == name.asname:
                                return True
                        else:
                            if id == name.name:
                                return True
                else:
                    log("astTools\timportedName\tUnsupported library: " + print_function(imp), "bug")

            else:
                log("astTools\timportedName\tWhy no module? " + print_function(imp), "bug")
    return False


def is_iterable_type(node):
    """Can the given type be iterated over"""
    return node in [dict, list, set, str, bytes, tuple]


def is_statement(node):
    """Determine whether the given node is a statement (vs an expression)"""
    return type(node) in [
        ast.Module, ast.Interactive, ast.Expression, ast.Suite,
        ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Return,
        ast.Delete, ast.Assign, ast.AugAssign, ast.AnnAssign, ast.For,
        ast.AsyncFor, ast.While, ast.If, ast.With, ast.AsyncWith, ast.Raise,
        ast.Try, ast.Assert, ast.Import, ast.ImportFrom, ast.Global,
        ast.Nonlocal, ast.Expr, ast.Pass, ast.Break, ast.Continue, ast.Match
    ]


def code_length(node):
    """Returns the number of characters in this AST"""
    if type(node) is list:
        return sum([code_length(inner_node) for inner_node in node])
    return len(print_function(node))


def apply_to_children(node, func):
    """Apply the given function to all the children of a node"""
    if node is None:
        return node
    for field_name in node.__getattribute__("_fields"):
        if not hasattr(node, field_name):
            continue
        child_node = getattr(node, field_name)
        if isinstance(child_node, list):
            new_child_list = []
            for item in child_node:
                new_child = func(item)
                if isinstance(new_child, list):
                    new_child_list.extend(new_child)
                else:
                    new_child_list.append(new_child)
            setattr(node, field_name, new_child_list)
        else:
            setattr(node, field_name, func(child_node))
    return node


def occurs_in(sub, parent):
    """Does the first AST occur as a subtree of the second?"""
    if not isinstance(parent, ast.AST):
        return False
    if isinstance(sub, ast.Module) and isinstance(parent, ast.Module):
        return any(occurs_in(sub_node, parent) for sub_node in sub.body)
    if type(sub) is type(parent) and compare_trees(sub, parent, check_equality=True) == 0:
        return True
    # we know that a statement can never occur in an expression
    # (or in a non-statement-holding statement), so cut the search off now to save time.
    if is_statement(sub) and not is_statement(parent):
        return False
    return any(occurs_in(sub, child) for child in ast.iter_child_nodes(parent))


def count_occurrences(node, value):
    """How many instances of this node type appear in the AST?"""
    if type(node) is list:
        return sum([count_occurrences(x, value) for x in node])
    if not isinstance(node, ast.AST):
        return 0

    count = 0
    for node in ast.walk(node):
        if isinstance(node, value):
            count += 1
    return count


def count_variables(node, var_id):
    """Count the number of times the given variable appears in the AST"""
    if type(node) is list:
        return sum([count_variables(x, var_id) for x in node])
    if not isinstance(node, ast.AST):
        return 0

    count = 0
    for node in ast.walk(node):
        if type(node) is ast.Name and node.id == var_id:
            count += 1
    return count


def gather_all_names(node, keep_orig=True):
    """Gather all names in the tree (variable or otherwise).
        Names are returned along with their original names
        (which are used in variable mapping)"""
    if isinstance(node, list):
        return {name for line in node for name in gather_all_names(line, keep_orig)}

    if not isinstance(node, ast.AST):
        return set()

    return {
        (inner_node.id, inner_node.originalId if (keep_orig and hasattr(inner_node, "originalId")) else None)
        for inner_node in ast.walk(node) if isinstance(inner_node, ast.Name)
    }


def gather_all_variables(node, keep_orig=True):
    """Gather all variable names in the tree. Names are returned along
        with their original names (which are used in variable mapping)"""
    if isinstance(node, list):
        return {var for line in node for var in gather_all_variables(line, keep_orig)}

    if not isinstance(node, ast.AST):
        return set()

    all_ids = set()
    for n in ast.walk(node):
        if isinstance(n, (ast.Name, ast.arg)):
            current_id = n.id if isinstance(n, ast.Name) else n.arg
            if not (built_in_name(current_id) or hasattr(n, "dontChangeName")):
                orig_name = n.originalId if (keep_orig and hasattr(n, "originalId")) else None
                existing = next((pair for pair in all_ids if pair[0] == current_id), None)
                if existing:
                    if existing[1] is None:
                        all_ids.remove(existing)
                        all_ids.add((current_id, orig_name))
                    elif orig_name is not None:
                        log(f"astTools\\gatherAllVariables\\tConflicting originalIds? {existing[0]} : {existing[1]} , {orig_name}\n{print_function(node)}",
                            "bug")
                else:
                    all_ids.add((current_id, orig_name))
    return all_ids


def gather_all_parameters(node, keep_orig=True):
    """Gather all parameters in the tree. Names are returned along
        with their original names (which are used in variable mapping)"""
    if isinstance(node, list):
        return {param for line in node for param in gather_all_parameters(line, keep_orig)}

    if not isinstance(node, ast.AST):
        return set()

    return {
        (inner_node.arg, inner_node.originalId if (keep_orig and hasattr(inner_node, "originalId")) else None)
        for inner_node in ast.walk(node) if isinstance(inner_node, ast.arg)
    }


def gather_all_helpers(node, restricted_names):
    """Gather all helper function names in the tree that have been anonymized"""
    if not isinstance(node, ast.Module):
        return set()

    return {
        (item.name, item.originalId if hasattr(item, "originalId") else None)
        for item in node.body if
        isinstance(item, ast.FunctionDef) and not hasattr(item, "dontChangeName") and item.name not in restricted_names
    }


def gather_all_function_names(node):
    """Gather all helper function names in the tree that have been anonymized"""
    if not isinstance(node, ast.Module):
        return set()

    return {
        (item.name, item.originalId if hasattr(item, "originalId") else None)
        for item in node.body if isinstance(item, ast.FunctionDef)
    }


def gather_assigned_vars(nodes):
    """Take a list of assigned variables and extract the names/subscripts/attributes"""
    if not isinstance(nodes, list):
        nodes = [nodes]

    new_targets = []
    for node in nodes:
        if isinstance(node, (ast.Tuple, ast.List)):
            new_targets.extend(gather_assigned_vars(node.elts))
        elif isinstance(node, (ast.Name, ast.Subscript, ast.Attribute)):
            new_targets.append(node)
        else:
            raise TypeError(f"Unknown target type: {type(node)}")
    return new_targets


def gather_assigned_var_ids(targets):
    """Just get the ids of Names"""
    nodes = gather_assigned_vars(targets)
    return [y.id for y in filter(lambda inner_node: type(inner_node) is ast.Name, nodes)]


def get_all_assigned_var_ids(node):
    if not isinstance(node, ast.AST):
        return []
    ids = []
    for child in ast.walk(node):
        if type(child) is ast.Assign:
            ids += gather_assigned_var_ids(child.targets)
        elif type(child) is ast.AugAssign:
            ids += gather_assigned_var_ids([child.target])
        elif type(child) is ast.For:
            ids += gather_assigned_var_ids([child.target])
    return ids


def get_all_assigned_vars(node):
    if not isinstance(node, ast.AST):
        return []
    nodes = []
    for child in ast.walk(node):
        if type(child) is ast.Assign:
            nodes += gather_assigned_vars(child.targets)
        elif type(child) is ast.AugAssign:
            nodes += gather_assigned_vars([child.target])
        elif type(child) is ast.For:
            nodes += gather_assigned_vars([child.target])
    return nodes


def get_all_imports(a):
    """Gather all imported module names"""
    if not isinstance(a, ast.AST):
        return []
    imports = []
    for child in ast.walk(a):
        if type(child) is ast.Import:
            for alias in child.names:
                if alias.name in supported_libraries:
                    imports.append(alias.asname if alias.asname is not None else alias.name)
                else:
                    raise Exception(
                        f"Unsupported import name: {alias.name}. Supported libraries are {supported_libraries}")
        elif type(child) is ast.ImportFrom:
            if child.module in supported_libraries:
                for alias in child.names:  # these are all functions
                    if alias.name in libraryMap[child.module]:
                        imports.append(alias.asname if alias.asname is not None else alias.name)
                    else:
                        raise Exception(
                            f"Unsupported import name: {alias.name}. Supported functions are {libraryMap[child.module]}")
            else:
                raise Exception(
                    f"Unsupported import module: {child.module}. Supported libraries are {supported_libraries}")
    return imports


def get_all_import_statements(node):
    if not isinstance(node, ast.AST):
        return []
    imports = []
    for child in ast.walk(node):
        if type(child) is ast.Import:
            imports.append(child)
        elif type(child) is ast.ImportFrom:
            imports.append(child)
    return imports


def get_all_global_names(node):
    # Finds all names that can be accessed at the global level in the AST
    if type(node) is not ast.Module:
        return []
    names = []
    for obj in node.body:
        if type(obj) in [ast.FunctionDef, ast.ClassDef]:
            names.append(obj.name)
        elif type(obj) in [ast.Assign, ast.AugAssign]:
            targets = obj.targets if type(obj) is ast.Assign else [obj.target]
            for target in obj.targets:
                if type(target) == ast.Name:
                    names.append(target.id)
                elif type(target) in [ast.Tuple, ast.List]:
                    for elt in target.elts:
                        if type(elt) == ast.Name:
                            names.append(elt.id)
        elif type(obj) in [ast.Import, ast.ImportFrom]:
            for module in obj.names:
                names.append(module.asname if module.asname is not None else module.name)
    return names


def do_binary_op(operation, left, right):
    """Perform the given AST binary operation on the values"""
    top = type(operation)
    if top is ast.Add:
        return left + right
    elif top is ast.Sub:
        return left - right
    elif top is ast.Mult:
        return left * right
    elif top is ast.Div:
        # Don't bother if this will be a really long float- it won't work properly!
        # Also, in Python 3 this is floating division, so perform it accordingly.
        val = 1.0 * left / right
        if (val * 1e10 % 1.0) != 0:
            raise Exception("Repeating Float")
        return val
    elif top is ast.Mod:
        return left % right
    elif top is ast.Pow:
        return left ** right
    elif top is ast.LShift:
        return left << right
    elif top is ast.RShift:
        return left >> right
    elif top is ast.BitOr:
        return left | right
    elif top is ast.BitXor:
        return left ^ right
    elif top is ast.BitAnd:
        return left & right
    elif top is ast.FloorDiv:
        return left // right


def do_unary_op(operation, val):
    """Perform the given AST unary operation on the value"""
    top = type(operation)
    if top is ast.Invert:
        return ~ val
    elif top is ast.Not:
        return not val
    elif top is ast.UAdd:
        return val
    elif top is ast.USub:
        return -val


def do_compare(operation, left, right):
    """Perform the given AST comparison on the values"""
    top = type(operation)
    if top is ast.Eq:
        return left == right
    elif top is ast.NotEq:
        return left != right
    elif top is ast.Lt:
        return left < right
    elif top is ast.LtE:
        return left <= right
    elif top is ast.Gt:
        return left > right
    elif top is ast.GtE:
        return left >= right
    elif top is ast.Is:
        return left is right
    elif top is ast.IsNot:
        return left is not right
    elif top is ast.In:
        return left in right
    elif top is ast.NotIn:
        return left not in right


def num_negate(op):
    top = type(op)
    new_op = None
    neg = not op.num_negated if hasattr(op, "num_negated") else True
    if top == ast.Add:
        new_op = ast.Sub()
    elif top == ast.Sub:
        new_op = ast.Add()
    elif top in [ast.Mult, ast.Div, ast.Mod, ast.Pow, ast.LShift,
                 ast.RShift, ast.BitOr, ast.BitXor, ast.BitAnd, ast.FloorDiv]:
        return None  # can't negate this
    elif top in [ast.Num, ast.Name]:
        # this is a normal value, so put a - in front of it
        new_op = ast.UnaryOp(ast.USub(addedNeg=True), op)
    else:
        raise Exception("Unknown operator type")
    transferMetaData(op, new_op)
    new_op.num_negated = neg
    return new_op


def negate(op):
    """Return the negation of the provided operator"""
    if op is None:
        return None
    top = type(op)
    neg = not op.negated if hasattr(op, "negated") else True
    if top == ast.And:
        new_op = ast.Or()
    elif top == ast.Or:
        new_op = ast.And()
    elif top == ast.Eq:
        new_op = ast.NotEq()
    elif top == ast.NotEq:
        new_op = ast.Eq()
    elif top == ast.Lt:
        new_op = ast.GtE()
    elif top == ast.GtE:
        new_op = ast.Lt()
    elif top == ast.Gt:
        new_op = ast.LtE()
    elif top == ast.LtE:
        new_op = ast.Gt()
    elif top == ast.Is:
        new_op = ast.IsNot()
    elif top == ast.IsNot:
        new_op = ast.Is()
    elif top == ast.In:
        new_op = ast.NotIn()
    elif top == ast.NotIn:
        new_op = ast.In()
    elif top == ast.NameConstant and op.value in [True, False]:
        op.value = not op.value
        op.negated = neg
        return op
    elif top == ast.Compare:
        if len(op.ops) == 1:
            op.ops[0] = negate(op.ops[0])
            op.negated = neg
            return op
        else:
            values = []
            all_operands = [op.left] + op.comparators
            for i in range(len(op.ops)):
                values.append(ast.Compare(all_operands[i], [negate(op.ops[i])],
                                          [all_operands[i + 1]], multiCompPart=True))
            new_op = ast.BoolOp(ast.Or(multiCompOp=True), values, multiComp=True)
    elif top == ast.UnaryOp and type(op.op) == ast.Not and \
            eventual_type(op.operand) == bool:  # this can mess things up type-wise
        return op.operand
    else:
        # this is a normal value, so put a not around it
        new_op = ast.UnaryOp(ast.Not(addedNot=True), op)
    transferMetaData(op, new_op)
    new_op.negated = neg
    return new_op


def could_crash(node):
    """Determines whether the given AST could possibly crash"""
    type_crashes = True  # toggle based on whether you care about potential crashes caused by types
    if not isinstance(node, ast.AST):
        return False

    if isinstance(node, ast.Try):
        for part in (node.handlers, node.orelse, node.finalbody):
            for item in part:
                for child in ast.iter_child_nodes(item):
                    if could_crash(child):
                        return True
        return False

    for child in ast.iter_child_nodes(node):
        if could_crash(child):
            return True

    if isinstance(node, ast.FunctionDef):
        arg_names = set()
        for arg in node.args.args:
            if arg.arg in arg_names:
                return True
            arg_names.add(arg.arg)
    elif isinstance(node, ast.Assign):
        for target in node.targets:
            if not isinstance(target, ast.Name):
                return True
    elif isinstance(node, (ast.For, ast.comprehension)):
        if not isinstance(node.target, (ast.Name, ast.Tuple, ast.List)):
            return True
        if isinstance(node.target, (ast.Tuple, ast.List)):
            for elt in node.target.elts:
                if not isinstance(elt, ast.Name):
                    return True
        if is_iterable_type(eventual_type(node.iter)):
            return True
    elif isinstance(node, ast.Import):
        for name in node.names:
            if name not in supported_libraries:
                return True
    elif isinstance(node, ast.ImportFrom):
        if node.module not in supported_libraries or node.level is not None:
            return True
        for name in node.names:
            if name not in libraryMap[node.module]:
                return True
    elif isinstance(node, ast.BinOp):
        l, r = eventual_type(node.left), eventual_type(node.right)
        if isinstance(node.op, ast.Add):
            if not ((l == r == str) or (l in [int, float] and r in [int, float])):
                return type_crashes
        elif isinstance(node.op, ast.Mult):
            if not ((l == str and r == int) or (l == int and r == str) or (l in [int, float] and r in [int, float])):
                return type_crashes
        elif isinstance(node.op, (ast.Sub, ast.LShift, ast.RShift, ast.BitOr, ast.BitXor, ast.BitAnd)):
            if not (l in [int, float] and r in [int, float]):
                return type_crashes
        elif isinstance(node.op, ast.Pow):
            if not ((l in [int, float] and r == int) or (l in [int, float] and isinstance(node.right, ast.Num) and
                                                         not isinstance(node.right.n, complex) and (
                                                                 node.right.n >= 1 or node.right.n == 0 or node.right.n <= -1))):
                return True
        else:  # ast.Div, ast.FloorDiv, ast.Mod
            if isinstance(node.right, ast.Num) and node.right.n != 0:
                if l not in [int, float]:
                    return type_crashes
            else:
                return True  # Divide by zero error
    elif isinstance(node, ast.UnaryOp):
        if isinstance(node.op, (ast.UAdd, ast.USub)):
            if eventual_type(node.operand) not in [int, float]:
                return type_crashes
        elif isinstance(node.op, ast.Invert):
            if eventual_type(node.operand) != int:
                return type_crashes
    elif isinstance(node, ast.Compare):
        if len(node.ops) != len(node.comparators):
            return True
        if isinstance(node.ops[0], (ast.In, ast.NotIn)):
            if not is_iterable_type(eventual_type(node.comparators[0])):
                return True
            if eventual_type(node.comparators[0]) in [str, bytes] and eventual_type(node.left) not in [str, bytes]:
                return True
        elif isinstance(node.ops[0], (ast.Lt, ast.LtE, ast.Gt, ast.GtE)):
            first_type = eventual_type(node.left)
            if first_type is None:
                return True
            for comp in node.comparators:
                if eventual_type(comp) != first_type:
                    return True
    elif isinstance(node, ast.Call):
        if isinstance(node.func, ast.Name):
            funct_name = node.func.id
            if funct_name not in builtInSafeFunctions:
                return True
            funct_dict = built_in_functions
        elif isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Name) and not hasattr(node.func.value,
                                                                     "varID") and node.func.value.id in supported_libraries:
                funct_name = node.func.attr
                if funct_name not in safeLibraryMap(node.func.value.id):
                    return True
                funct_dict = libraryMap[node.func.value.id]
            elif eventual_type(node.func.value) == str:
                funct_name = node.func.attr
                if funct_name not in safeStringFunctions:
                    return True
                funct_dict = builtInStringFunctions
            else:
                return True
        else:
            return True

        if funct_name in ["max", "min"]:
            return False

        arg_types = [eventual_type(arg) for arg in node.args]
        if any(arg is None and type_crashes for arg in arg_types):
            return True

        if funct_dict[funct_name] is not None:
            for argSet in funct_dict[funct_name]:
                if len(argSet) != len(arg_types):
                    continue
                if not type_crashes:
                    return False
                if all(argSet[i] == arg_types[i] or issubclass(arg_types[i], argSet[i]) for i in range(len(argSet))):
                    return False
            return True
    elif isinstance(node, ast.Subscript):
        return eventual_type(node.value) not in [str, list, tuple]
    elif isinstance(node, ast.Name):
        if hasattr(node, "randomVar"):
            return True
    elif isinstance(node, ast.Slice):
        if node.lower is not None and eventual_type(node.lower) != int:
            return True
        if node.upper is not None and eventual_type(node.upper) != int:
            return True
        if node.step is not None and eventual_type(node.step) != int:
            return True
    elif isinstance(node, (
            ast.Raise, ast.Assert, ast.Pass, ast.Break, ast.Continue, ast.Yield, ast.Attribute, ast.ExtSlice, ast.Index,
            ast.Starred)):
        return True

    return False


def eventual_type(node):
    """Get the type the expression will eventually be, if possible
        The expression might also crash! But we don't care about that here,
        we'll deal with it elsewhere.
        Returning 'None' means that we cannot say at the moment"""
    if type(node) in builtInTypes:
        return type(node)
    if not isinstance(node, ast.AST):
        return None

    if isinstance(node, ast.BoolOp):
        target = eventual_type(node.values[0])
        for value in node.values[1:]:
            if eventual_type(value) != target:
                return None
        return target

    if isinstance(node, ast.BinOp):
        left = eventual_type(node.left)
        right = eventual_type(node.right)
        if isinstance(node.op, (ast.Add, ast.Mult)):
            if is_iterable_type(left):
                return left
            if is_iterable_type(right):
                return right
            if left == float or right == float:
                return float
            if left == int and right == int:
                return int
            return None
        if isinstance(node.op, ast.Div):
            return float
        if isinstance(node.op, (ast.FloorDiv, ast.LShift, ast.RShift, ast.BitOr, ast.BitAnd, ast.BitXor)):
            return int
        if float in [left, right]:
            return float
        if left == int and right == int:
            return int
        return None

    if isinstance(node, ast.UnaryOp):
        if isinstance(node.op, ast.Invert):
            return int
        if isinstance(node.op, (ast.UAdd, ast.USub)):
            return eventual_type(node.operand)
        return bool

    if isinstance(node, ast.Lambda):
        return None

    if isinstance(node, ast.IfExp):
        left = eventual_type(node.body)
        right = eventual_type(node.orelse)
        return left if left == right else None

    if isinstance(node, (ast.Dict, ast.DictComp)):
        return dict

    if isinstance(node, (ast.Set, ast.SetComp)):
        return set

    if isinstance(node, (ast.List, ast.ListComp)):
        return list

    if isinstance(node, ast.GeneratorExp):
        return None

    if isinstance(node, ast.Yield):
        return None

    if isinstance(node, ast.Compare):
        return bool

    if isinstance(node, ast.Call):
        arg_types = [eventual_type(inner_node) for inner_node in node.args]
        if isinstance(node.func, ast.Name):
            funct_dict = built_in_functions
            funct_name = node.func.id
        elif isinstance(node.func, ast.Attribute):
            funct_name = node.func.attr
            if isinstance(node.func.value, ast.Name) and not hasattr(node.func.value,
                                                                     "varID") and node.func.value.id in supported_libraries:
                funct_dict = libraryDictMap[node.func.value.id]
                if node.func.value.id in ["string", "str", "list", "dict"] and len(arg_types) > 0:
                    arg_types.pop(0)
            elif eventual_type(node.func.value) == str:
                funct_dict = builtInStringFunctions
            elif eventual_type(node.func.value) == list:
                funct_dict = builtInListFunctions
            elif eventual_type(node.func.value) == dict:
                funct_dict = builtInDictFunctions
            else:
                return None
        else:
            return None

        if funct_name in ["max", "min"]:
            unique_types = set(arg_types)
            return unique_types.pop() if len(unique_types) == 1 else None

        if funct_name in funct_dict and funct_dict[funct_name] is not None:
            possible_types = []
            for argSet in funct_dict[funct_name]:
                if len(argSet) == len(arg_types):
                    for i in range(len(argSet)):
                        if argSet[i] is None or arg_types[i] is None:
                            continue
                        if not (argSet[i] == arg_types[i] or (issubclass(arg_types[i], argSet[i]))):
                            break
                    else:
                        possible_types.append(funct_dict[funct_name][argSet])
            possible_types = set(possible_types)
            if len(possible_types) == 1:
                return possible_types.pop()
        return None

    if isinstance(node, (ast.Str, ast.Bytes)):
        if contains_token_step_string(node):
            return None
        return str

    if isinstance(node, ast.Num):
        return type(node.n)

    if isinstance(node, ast.Attribute):
        return None

    if isinstance(node, ast.Subscript):
        t = eventual_type(node.value)
        if t is None:
            return None
        if t == str:
            return str
        if t in [list, tuple]:
            if isinstance(node.slice, ast.Slice):
                return t
            if isinstance(node.value, (ast.List, ast.Tuple)):
                if len(node.value.elts) == 0:
                    return None
                else:
                    eltType = eventual_type(node.value.elts[0])
                    for elt in node.value.elts:
                        if eventual_type(elt) != eltType:
                            return None
                    return eltType
        if t in [dict, int]:
            return None
        raise Exception("Unknown type in Subscript")

    if isinstance(node, ast.NameConstant):
        if node.value in [True, False]:
            return bool
        if node.value is None:
            return type(None)
        return None

    if isinstance(node, ast.Constant):
        return type(node.value)

    if isinstance(node, ast.Name):
        if hasattr(node, "type"):
            return node.type
        return None

    if isinstance(node, ast.Tuple):
        return tuple

    if isinstance(node, ast.Starred):
        return None

    raise Exception("Unknown type in eventual_type, " + str(type(node)), " not implemented yet")


def depth_of_ast(node):
    """Determine the depth of the AST"""
    if not isinstance(node, ast.AST):
        return 0
    current_deepest = 0
    for child in ast.iter_child_nodes(node):
        candidate_node_depth = depth_of_ast(child)
        if candidate_node_depth > current_deepest:
            current_deepest = candidate_node_depth
    return current_deepest + 1


def compare_trees(node_a, node_b, check_equality=False):
    """A comparison function for ASTs"""
    if node_a == node_b is None:
        return 0
    elif node_a is None or node_b is None:
        return -1 if node_a is None else 1

    if isinstance(node_a, list) and isinstance(node_b, list):
        if len(node_a) != len(node_b):
            return len(node_a) - len(node_b)
        for i in range(len(node_a)):
            result = compare_trees(node_a[i], node_b[i], check_equality=check_equality)
            if result != 0:
                return result
        return 0

    if not isinstance(node_a, ast.AST) and not isinstance(node_b, ast.AST):
        if type(node_a) is not type(node_b):
            builtins = [bool, int, float, str, bytes, complex]
            if type(node_a) not in builtins or type(node_b) not in builtins:
                log("MISSING BUILT-IN TYPE: " + str(type(node_a)) + "," + str(type(node_b)), "bug")
            return builtins.index(type(node_a)) - builtins.index(type(node_b))
        return cmp(node_a, node_b)
    elif not isinstance(node_a, ast.AST) or not isinstance(node_b, ast.AST):
        return -1 if isinstance(node_a, ast.AST) else 1

    if type(node_a) is not type(node_b):
        important_types = [ast.Load, ast.Store, ast.Del, ast.AugLoad, ast.AugStore, ast.Param]
        if type(node_a) in important_types and type(node_b) in important_types:
            return 0
        elif type(node_a) in important_types or type(node_b) in important_types:
            return -1 if type(node_a) in important_types else 1

        types = [ast.Module, ast.Interactive, ast.Expression, ast.Suite,
                 ast.Break, ast.Continue, ast.Pass, ast.Global,
                 ast.Expr, ast.Assign, ast.AugAssign, ast.Return,
                 ast.Assert, ast.Delete, ast.If, ast.For, ast.While,
                 ast.With, ast.Import, ast.ImportFrom, ast.Raise,
                 ast.Try, ast.FunctionDef, ast.ClassDef,
                 ast.BinOp, ast.BoolOp, ast.Compare, ast.UnaryOp,
                 ast.DictComp, ast.ListComp, ast.SetComp, ast.GeneratorExp,
                 ast.Yield, ast.Lambda, ast.IfExp, ast.Call, ast.Subscript,
                 ast.Attribute, ast.Dict, ast.List, ast.Tuple,
                 ast.Set, ast.Name, ast.Str, ast.Bytes, ast.Num,
                 ast.NameConstant, ast.Starred, ast.Constant,
                 ast.Ellipsis, ast.Index, ast.Slice, ast.ExtSlice,
                 ast.And, ast.Or, ast.Add, ast.Sub, ast.Mult, ast.Div,
                 ast.Mod, ast.Pow, ast.LShift, ast.RShift, ast.BitOr,
                 ast.BitXor, ast.BitAnd, ast.FloorDiv, ast.Invert, ast.Not,
                 ast.UAdd, ast.USub, ast.Eq, ast.NotEq, ast.Lt, ast.LtE,
                 ast.Gt, ast.GtE, ast.Is, ast.IsNot, ast.In, ast.NotIn,
                 ast.alias, ast.keyword, ast.arguments, ast.arg, ast.comprehension,
                 ast.ExceptHandler, ast.withitem, ast.JoinedStr, ast.FormattedValue]
        if type(node_a) not in types or type(node_b) not in types:
            log("astTools\tcompareASTs\tmissing type:" + str(type(node_a)) + "," + str(type(node_b)), "bug")
            return 0
        return types.index(type(node_a)) - types.index(type(node_b))

    if not check_equality:
        depth_a = depth_of_ast(node_a)
        depth_b = depth_of_ast(node_b)
        if depth_a != depth_b:
            return depth_b - depth_a

    if isinstance(node_a, ast.Constant):
        if hasattr(node_a, 'value') and hasattr(node_b, 'value'):
            if type(node_a.value) is not type(node_b.value):
                return -1 if type(node_a.value).__name__ < type(node_b.value).__name__ else 1
            else:
                if isinstance(node_a.value, ast.Constant) and isinstance(node_b.value, ast.Constant):
                    return compare_trees(node_a.value, node_b.value, check_equality=check_equality)
        else:
            return 0

    if isinstance(node_a, ast.NameConstant):
        if node_a.value is None or node_b.value is None:
            return 1 if node_a.value is not None else (0 if node_b.value is None else -1)
        if node_a.value in [True, False] or node_b.value in [True, False]:
            return 1 if node_a.value not in [True, False] else (
                cmp(node_a.value, node_b.value) if node_b.value in [True, False] else -1)

    if isinstance(node_a, ast.Name):
        return cmp(node_a.id, node_b.id)

    if isinstance(node_a, (ast.And, ast.Or, ast.Add, ast.Sub, ast.Mult, ast.Div,
                           ast.Mod, ast.Pow, ast.LShift, ast.RShift, ast.BitOr,
                           ast.BitXor, ast.BitAnd, ast.FloorDiv, ast.Invert,
                           ast.Not, ast.UAdd, ast.USub, ast.Eq, ast.NotEq, ast.Lt,
                           ast.LtE, ast.Gt, ast.GtE, ast.Is, ast.IsNot, ast.In,
                           ast.NotIn, ast.Load, ast.Store, ast.Del, ast.AugLoad,
                           ast.AugStore, ast.Param, ast.Ellipsis, ast.Pass,
                           ast.Break, ast.Continue)):
        return 0

    attr_map = {
        ast.Module: ["body"], ast.Interactive: ["body"], ast.Expression: ["body"], ast.Suite: ["body"],
        ast.FunctionDef: ["name", "args", "body", "decorator_list", "returns"],
        ast.ClassDef: ["name", "bases", "keywords", "body", "decorator_list"],
        ast.Return: ["value"], ast.Delete: ["targets"], ast.Assign: ["targets", "value"],
        ast.AugAssign: ["target", "op", "value"], ast.For: ["target", "iter", "body", "orelse"],
        ast.While: ["test", "body", "orelse"], ast.If: ["test", "body", "orelse"],
        ast.With: ["items", "body"], ast.Raise: ["exc", "cause"], ast.Try: ["body", "handlers", "orelse", "finalbody"],
        ast.Assert: ["test", "msg"], ast.Import: ["names"], ast.ImportFrom: ["module", "names", "level"],
        ast.Global: ["names"], ast.Expr: ["value"], ast.BoolOp: ["op", "values"], ast.BinOp: ["left", "op", "right"],
        ast.UnaryOp: ["op", "operand"], ast.Lambda: ["args", "body"], ast.IfExp: ["test", "body", "orelse"],
        ast.Dict: ["keys", "values"], ast.Set: ["elts"], ast.ListComp: ["elt", "generators"],
        ast.SetComp: ["elt", "generators"], ast.DictComp: ["key", "value", "generators"],
        ast.GeneratorExp: ["elt", "generators"], ast.Yield: ["value"], ast.Compare: ["left", "ops", "comparators"],
        ast.Call: ["func", "args", "keywords"], ast.Num: ["n"], ast.Str: ["s"], ast.Bytes: ["s"],
        ast.NameConstant: ["value"], ast.Constant: ["value"], ast.Attribute: ["value", "attr"],
        ast.Subscript: ["value", "slice"], ast.List: ["elts"], ast.Tuple: ["elts"], ast.Starred: ["value"],
        ast.Slice: ["lower", "upper", "step"], ast.ExtSlice: ["dims"], ast.Index: ["value"],
        ast.comprehension: ["target", "iter", "ifs"], ast.ExceptHandler: ["type", "name", "body"],
        ast.arguments: ["posonlyargs", "args", "vararg", "kwonlyargs", "kw_defaults", "kwarg", "defaults"],
        ast.arg: ["arg", "annotation"], ast.keyword: ["arg", "value"], ast.alias: ["name", "asname"],
        ast.withitem: ["context_expr", "optional_vars"], ast.JoinedStr: ["values"], ast.FormattedValue: ["value"],
    }

    for attr in attr_map[type(node_a)]:
        result = compare_trees(getattr(node_a, attr), getattr(node_b, attr), check_equality=check_equality)
        if result != 0:
            return result

    return 0


def deepcopy_list(target_list):
    """Deepcopy of a list"""
    if target_list is None:
        return None
    if isinstance(target_list, ast.AST):
        return deepcopy(target_list)
    if type(target_list) is not list:
        raise TypeError("Expected a list, got " + str(type(target_list)))
    new_list = []
    # At this point we know it's a list
    target_list = list(target_list)
    for line in target_list:
        new_list.append(deepcopy(line))
    return new_list


def deepcopy(node):
    """Let's try to keep this as quick as possible"""
    if node is None:
        return None
    if isinstance(node, list):
        return deepcopy_list(node)
    if isinstance(node, (int, float, str, bool)):
        return node
    if not isinstance(node, ast.AST):
        return copy.deepcopy(node)

    global_id = getattr(node, "global_id", None)
    cp = None

    if isinstance(node, (ast.And, ast.Or, ast.Add, ast.Sub, ast.Mult, ast.Div,
                         ast.Mod, ast.Pow, ast.LShift, ast.RShift, ast.BitOr,
                         ast.BitXor, ast.BitAnd, ast.FloorDiv, ast.Invert,
                         ast.Not, ast.UAdd, ast.USub, ast.Eq, ast.NotEq, ast.Lt,
                         ast.LtE, ast.Gt, ast.GtE, ast.Is, ast.IsNot, ast.In,
                         ast.NotIn, ast.Load, ast.Store, ast.Del, ast.AugLoad,
                         ast.AugStore, ast.Param)):
        return node

    if isinstance(node, ast.Module):
        cp = ast.Module(deepcopy_list(node.body))
    elif isinstance(node, ast.Interactive):
        cp = ast.Interactive(deepcopy_list(node.body))
    elif isinstance(node, ast.Expression):
        cp = ast.Expression(deepcopy(node.body))
    elif isinstance(node, ast.Suite):
        cp = ast.Suite(deepcopy_list(node.body))
    elif isinstance(node, ast.FunctionDef):
        cp = ast.FunctionDef(node.name, deepcopy(node.args), deepcopy_list(node.body),
                             deepcopy_list(node.decorator_list), deepcopy(node.returns))
    elif isinstance(node, ast.ClassDef):
        cp = ast.ClassDef(node.name, deepcopy_list(node.bases), deepcopy_list(node.keywords),
                          deepcopy_list(node.body), deepcopy_list(node.decorator_list))
    elif isinstance(node, ast.Return):
        cp = ast.Return(deepcopy(node.value))
    elif isinstance(node, ast.Delete):
        cp = ast.Delete(deepcopy_list(node.targets))
    elif isinstance(node, ast.Assign):
        cp = ast.Assign(deepcopy_list(node.targets), deepcopy(node.value))
    elif isinstance(node, ast.AugAssign):
        cp = ast.AugAssign(deepcopy(node.target), deepcopy(node.op), deepcopy(node.value))
    elif isinstance(node, ast.For):
        cp = ast.For(deepcopy(node.target), deepcopy(node.iter), deepcopy_list(node.body), deepcopy_list(node.orelse))
    elif isinstance(node, ast.While):
        cp = ast.While(deepcopy(node.test), deepcopy_list(node.body), deepcopy_list(node.orelse))
    elif isinstance(node, ast.If):
        cp = ast.If(deepcopy(node.test), deepcopy_list(node.body), deepcopy_list(node.orelse))
    elif isinstance(node, ast.With):
        cp = ast.With(deepcopy_list(node.items), deepcopy_list(node.body))
    elif isinstance(node, ast.Raise):
        cp = ast.Raise(deepcopy(node.exc), deepcopy(node.cause))
    elif isinstance(node, ast.Try):
        cp = ast.Try(deepcopy_list(node.body), deepcopy_list(node.handlers), deepcopy_list(node.orelse),
                     deepcopy_list(node.finalbody))
    elif isinstance(node, ast.Assert):
        cp = ast.Assert(deepcopy(node.test), deepcopy(node.msg))
    elif isinstance(node, ast.Import):
        cp = ast.Import(deepcopy_list(node.names))
    elif isinstance(node, ast.ImportFrom):
        cp = ast.ImportFrom(node.module, deepcopy_list(node.names), node.level)
    elif isinstance(node, ast.Global):
        cp = ast.Global(node.names[:])
    elif isinstance(node, ast.Expr):
        cp = ast.Expr(deepcopy(node.value))
    elif isinstance(node, ast.Pass):
        cp = ast.Pass()
    elif isinstance(node, ast.Break):
        cp = ast.Break()
    elif isinstance(node, ast.Continue):
        cp = ast.Continue()
    elif isinstance(node, ast.BoolOp):
        cp = ast.BoolOp(node.op, deepcopy_list(node.values))
    elif isinstance(node, ast.BinOp):
        cp = ast.BinOp(deepcopy(node.left), node.op, deepcopy(node.right))
    elif isinstance(node, ast.UnaryOp):
        cp = ast.UnaryOp(node.op, deepcopy(node.operand))
    elif isinstance(node, ast.Lambda):
        cp = ast.Lambda(deepcopy(node.args), deepcopy(node.body))
    elif isinstance(node, ast.IfExp):
        cp = ast.IfExp(deepcopy(node.test), deepcopy(node.body), deepcopy(node.orelse))
    elif isinstance(node, ast.Dict):
        cp = ast.Dict(deepcopy_list(node.keys), deepcopy_list(node.values))
    elif isinstance(node, ast.Set):
        cp = ast.Set(deepcopy_list(node.elts))
    elif isinstance(node, ast.ListComp):
        cp = ast.ListComp(deepcopy(node.elt), deepcopy_list(node.generators))
    elif isinstance(node, ast.SetComp):
        cp = ast.SetComp(deepcopy(node.elt), deepcopy_list(node.generators))
    elif isinstance(node, ast.DictComp):
        cp = ast.DictComp(deepcopy(node.key), deepcopy(node.value), deepcopy_list(node.generators))
    elif isinstance(node, ast.GeneratorExp):
        cp = ast.GeneratorExp(deepcopy(node.elt), deepcopy_list(node.generators))
    elif isinstance(node, ast.Yield):
        cp = ast.Yield(deepcopy(node.value))
    elif isinstance(node, ast.Compare):
        cp = ast.Compare(deepcopy(node.left), node.ops[:], deepcopy_list(node.comparators))
    elif isinstance(node, ast.Call):
        cp = ast.Call(deepcopy(node.func), deepcopy_list(node.args), deepcopy_list(node.keywords))
    elif isinstance(node, ast.Num):
        cp = ast.Num(node.n)
    elif isinstance(node, ast.Str):
        cp = ast.Str(node.s)
    elif isinstance(node, ast.Bytes):
        cp = ast.Bytes(node.s)
    elif isinstance(node, ast.NameConstant):
        cp = ast.NameConstant(node.value)
    elif isinstance(node, ast.Attribute):
        cp = ast.Attribute(deepcopy(node.value), node.attr, node.ctx)
    elif isinstance(node, ast.Subscript):
        cp = ast.Subscript(deepcopy(node.value), deepcopy(node.slice), node.ctx)
    elif isinstance(node, ast.Name):
        cp = ast.Name(node.id, node.ctx)
    elif isinstance(node, ast.List):
        cp = ast.List(deepcopy_list(node.elts), node.ctx)
    elif isinstance(node, ast.Tuple):
        cp = ast.Tuple(deepcopy_list(node.elts), node.ctx)
    elif isinstance(node, ast.Starred):
        cp = ast.Starred(deepcopy(node.value), node.ctx)
    elif isinstance(node, ast.Slice):
        cp = ast.Slice(deepcopy(node.lower), deepcopy(node.upper), deepcopy(node.step))
    elif isinstance(node, ast.ExtSlice):
        cp = ast.ExtSlice(deepcopy_list(node.dims))
    elif isinstance(node, ast.Index):
        cp = ast.Index(deepcopy(node.value))
    elif isinstance(node, ast.comprehension):
        cp = ast.comprehension(deepcopy(node.target), deepcopy(node.iter), deepcopy_list(node.ifs))
    elif isinstance(node, ast.ExceptHandler):
        cp = ast.ExceptHandler(deepcopy(node.type), node.name, deepcopy_list(node.body))
    elif isinstance(node, ast.arguments):
        cp = ast.arguments(deepcopy_list(node.posonlyargs), deepcopy(node.args), deepcopy_list(node.vararg),
                           deepcopy_list(node.kwonlyargs), deepcopy(node.kw_defaults), deepcopy_list(node.kwarg),
                           deepcopy_list(node.defaults))
    elif isinstance(node, ast.arg):
        cp = ast.arg(node.arg, deepcopy(node.annotation))
    elif isinstance(node, ast.keyword):
        cp = ast.keyword(node.arg, deepcopy(node.value))
    elif isinstance(node, ast.alias):
        cp = ast.alias(node.name, node.asname)
    elif isinstance(node, ast.withitem):
        cp = ast.withitem(deepcopy(node.context_expr), deepcopy(node.optional_vars))
    elif isinstance(node, ast.Constant):
        cp = ast.Constant(node.value, node.kind)
    elif isinstance(node, ast.JoinedStr):
        cp = ast.JoinedStr(deepcopy_list(node.values))
    elif isinstance(node, ast.FormattedValue):
        cp = ast.FormattedValue(deepcopy(node.value), node.conversion, deepcopy(node.format_spec))
    else:
        raise TypeError("Unknown type in deepcopy: " + str(type(node)))

    transferMetaData(node, cp)
    return cp


### ITAP/Canonicalization Functions ###

def isTokenStepString(s):
    """Determine whether this is a placeholder string"""
    if len(s) < 2:
        return False
    return s[0] == "~" and s[-1] == "~"


def getParentFunction(s):
    underscoreSep = s.split("_")
    if len(underscoreSep) == 1:
        return None
    result = "_".join(underscoreSep[1:])
    if result == "newvar" or result == "global":
        return None
    return result


def isAnonVariable(s):
    """Specificies whether the given string is an anonymized variable name"""
    preUnderscore = s.split("_")[0]  # the part before the function name
    return len(preUnderscore) > 1 and \
        preUnderscore[0] in ["g", "p", "v", "r", "n", "z"] and \
        preUnderscore[1:].isdigit()


def transferMetaData(a, b):
    """Transfer the metadata of a onto b"""
    properties = ["global_id", "second_global_id", "lineno", "col_offset",
                  "originalId", "varID", "variableGlobalId",
                  "randomVar", "propagatedVariable", "loadedVariable", "dontChangeName",
                  "reversed", "negated", "inverted",
                  "augAssignVal", "augAssignBinOp",
                  "combinedConditional", "combinedConditionalOp",
                  "multiComp", "multiCompPart", "multiCompMiddle", "multiCompOp",
                  "addedNot", "addedNotOp", "addedOther", "addedOtherOp", "addedNeg",
                  "collapsedExpr", "removedLines",
                  "helperVar", "helperReturnVal", "helperParamAssign", "helperReturnAssign",
                  "orderedBinOp", "typeCastFunction", "moved_line"]
    for prop in properties:
        if hasattr(a, prop):
            setattr(b, prop, getattr(a, prop))


def assignPropertyToAll(a, prop):
    """Assign the provided property to all children"""
    if type(a) == list:
        for child in a:
            assignPropertyToAll(child, prop)
    elif isinstance(a, ast.AST):
        for node in ast.walk(a):
            setattr(node, prop, True)


def removePropertyFromAll(a, prop):
    if type(a) == list:
        for child in a:
            removePropertyFromAll(child, prop)
    elif isinstance(a, ast.AST):
        for node in ast.walk(a):
            if hasattr(node, prop):
                delattr(node, prop)


def contains_token_step_string(a):
    """This is used to keep token-level hint chaining from breaking."""
    if not isinstance(a, ast.AST):
        return False

    for node in ast.walk(a):
        if type(node) == ast.Str and isTokenStepString(node.s):
            return True
    return False


def applyVariableMap(a, variableMap):
    if not isinstance(a, ast.AST):
        return a
    if type(a) == ast.Name:
        if a.id in variableMap:
            a.id = variableMap[a.id]
    elif type(a) in [ast.FunctionDef, ast.ClassDef]:
        if a.name in variableMap:
            a.name = variableMap[a.name]
    return apply_to_children(a, lambda x: applyVariableMap(x, variableMap))


def applyHelperMap(a, helperMap):
    if not isinstance(a, ast.AST):
        return a
    if type(a) == ast.Name:
        if a.id in helperMap:
            a.id = helperMap[a.id]
    elif type(a) == ast.FunctionDef:
        if a.name in helperMap:
            a.name = helperMap[a.name]
    return apply_to_children(a, lambda x: applyHelperMap(x, helperMap))


def astFormat(x, gid=None):
    """Given a value, turn it into an AST if it's a constant; otherwise, leave it alone."""
    if type(x) in [int, float, complex]:
        return ast.Num(x)
    elif type(x) == bool or x == None:
        return ast.NameConstant(x)
    elif type(x) == type:
        types = {bool: "bool", int: "int", float: "float",
                 complex: "complex", str: "str", bytes: "bytes", unicode: "unicode",
                 list: "list", tuple: "tuple", dict: "dict"}
        return ast.Name(types[x], ast.Load())
    elif type(x) == str:  # str or unicode
        return ast.Str(x)
    elif type(x) == bytes:
        return ast.Bytes(x)
    elif type(x) == list:
        elts = [astFormat(val) for val in x]
        return ast.List(elts, ast.Load())
    elif type(x) == dict:
        keys = []
        vals = []
        for key in x:
            keys.append(astFormat(key))
            vals.append(astFormat(x[key]))
        return ast.Dict(keys, vals)
    elif type(x) == tuple:
        elts = [astFormat(val) for val in x]
        return ast.Tuple(elts, ast.Load())
    elif type(x) == set:
        elts = [astFormat(val) for val in x]
        if len(elts) == 0:  # needs to be a call instead
            return ast.Call(ast.Name("set", ast.Load()), [], [])
        else:
            return ast.Set(elts)
    elif type(x) == slice:
        return ast.Slice(astFormat(x.start), astFormat(x.stop), astFormat(x.step))
    elif isinstance(x, ast.AST):
        return x  # Do not change if it's not constant!
    else:
        log("astTools\tastFormat\t" + str(type(x)) + "," + str(x), "bug")
        return None


def structureTree(a):
    if type(a) == list:
        for i in range(len(a)):
            a[i] = structureTree(a[i])
        return a
    elif not isinstance(a, ast.AST):
        return a
    else:
        if type(a) == ast.FunctionDef:
            a.name = "~name~"
            a.args = structureTree(a.args)
            a.body = structureTree(a.body)
            a.decorator_list = structureTree(a.decorator_list)
            a.returns = structureTree(a.returns)
        elif type(a) == ast.ClassDef:
            a.name = "~name~"
            a.bases = structureTree(a.bases)
            a.keywords = structureTree(a.keywords)
            a.body = structureTree(a.body)
            a.decorator_list = structureTree(a.decorator_list)
        elif type(a) == ast.AugAssign:
            a.target = structureTree(a.target)
            a.op = ast.Str("~op~")
            a.value = structureTree(a.value)
        elif type(a) == ast.Import:
            a.names = [ast.Str("~module~")]
        elif type(a) == ast.ImportFrom:
            a.module = "~module~"
            a.names = [ast.Str("~names~")]
        elif type(a) == ast.Global:
            a.names = ast.Str("~var~")
        elif type(a) == ast.BoolOp:
            a.op = ast.Str("~op~")
            a.values = structureTree(a.values)
        elif type(a) == ast.BinOp:
            a.op = ast.Str("~op~")
            a.left = structureTree(a.left)
            a.right = structureTree(a.right)
        elif type(a) == ast.UnaryOp:
            a.op = ast.Str("~op~")
            a.operand = structureTree(a.operand)
        elif type(a) == ast.Dict:
            return ast.Str("~dictionary~")
        elif type(a) == ast.Set:
            return ast.Str("~set~")
        elif type(a) == ast.Compare:
            a.ops = [ast.Str("~op~")] * len(a.ops)
            a.left = structureTree(a.left)
            a.comparators = structureTree(a.comparators)
        elif type(a) == ast.Call:
            # leave the function alone
            a.args = structureTree(a.args)
            a.keywords = structureTree(a.keywords)
        elif type(a) == ast.Num:
            return ast.Str("~number~")
        elif type(a) == ast.Str:
            return ast.Str("~string~")
        elif type(a) == ast.Bytes:
            return ast.Str("~bytes~")
        elif type(a) == ast.Attribute:
            a.value = structureTree(a.value)
        elif type(a) == ast.Name:
            a.id = "~var~"
        elif type(a) == ast.List:
            return ast.Str("~list~")
        elif type(a) == ast.Tuple:
            return ast.Str("~tuple~")
        elif type(a) in [ast.And, ast.Or, ast.Add, ast.Sub, ast.Mult, ast.Div,
                         ast.Mod, ast.Pow, ast.LShift, ast.RShift, ast.BitOr,
                         ast.BitXor, ast.BitAnd, ast.FloorDiv, ast.Invert,
                         ast.Not, ast.UAdd, ast.USub, ast.Eq, ast.NotEq,
                         ast.Lt, ast.LtE, ast.Gt, ast.GtE, ast.Is, ast.IsNot,
                         ast.In, ast.NotIn]:
            return ast.Str("~op~")
        elif type(a) == ast.arguments:
            a.args = structureTree(a.args)
            a.vararg = ast.Str("~arg~") if a.vararg != None else None
            a.kwonlyargs = structureTree(a.kwonlyargs)
            a.kw_defaults = structureTree(a.kw_defaults)
            a.kwarg = ast.Str("~keyword~") if a.kwarg != None else None
            a.defaults = structureTree(a.defaults)
        elif type(a) == ast.arg:
            a.arg = "~arg~"
            a.annotation = structureTree(a.annotation)
        elif type(a) == ast.keyword:
            a.arg = "~keyword~"
            a.value = structureTree(a.value)
        elif type(a) == ast.alias:
            a.name = "~name~"
            a.asname = "~asname~" if a.asname != None else None
        else:
            for field in a._fields:
                setattr(a, field, structureTree(getattr(a, field)))
        return a

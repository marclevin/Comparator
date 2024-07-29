import ast

from comparison.utils.tools import log


# ===============================================================================
# These functions are used for displaying ASTs. printAst displays the tree,
# while printFunction displays the syntax
# ===============================================================================

def print_function(unit, indent=0):
    output_string = ""
    if unit is None:
        return ""
    if not isinstance(unit, ast.AST):
        log("display\tprintFunction\tNot AST: " + str(type(unit)) + "," + str(unit), "bug")
        return str(unit)

    unit_type = type(unit)
    if unit_type in [ast.Module, ast.Interactive, ast.Suite]:
        for line in unit.body:
            output_string += print_function(line, indent)
    elif unit_type is ast.Expression:
        output_string += print_function(unit.body, indent)
    elif unit_type is ast.FunctionDef:
        for dec in unit.decorator_list:
            output_string += (indent * 4 * " ") + "@" + print_function(dec, indent) + "\n"
        output_string += (indent * 4 * " ") + "def " + unit.name + "(" + \
                         print_function(unit.args, indent) + "):\n"
        for stmt in unit.body:
            output_string += print_function(stmt, indent + 1)
    elif unit_type is ast.ClassDef:
        for dec in unit.decorator_list:
            output_string += (indent * 4 * " ") + "@" + print_function(dec, indent) + "\n"
        output_string += (indent * 4 * " ") + "class " + unit.name
        if len(unit.bases) > 0 or len(unit.keywords) > 0:
            output_string += "("
            for base in unit.bases:
                output_string += print_function(base, indent) + ", "
            for keyword in unit.keywords:
                output_string += print_function(keyword, indent) + ", "
            output_string += output_string[:-2] + ")"
        output_string += ":\n"
        for stmt in unit.body:
            output_string += print_function(stmt, indent + 1)
    elif unit_type is ast.Return:
        output_string += (indent * 4 * " ") + "return " + \
                         print_function(unit.value, indent) + "\n"
    elif unit_type is ast.Delete:
        output_string += (indent * 4 * " ") + "del "
        for target in unit.targets:
            output_string += print_function(target, indent) + ", "
        if len(unit.targets) >= 1:
            output_string = output_string[:-2]
        output_string += "\n"
    elif unit_type is ast.Assign:
        output_string += (indent * 4 * " ")
        for target in unit.targets:
            output_string += print_function(target, indent) + " = "
        output_string += print_function(unit.value, indent) + "\n"
    elif unit_type is ast.AugAssign:
        output_string += (indent * 4 * " ")
        output_string += print_function(unit.target, indent) + " " + \
                         print_function(unit.op, indent) + "= " + \
                         print_function(unit.value, indent) + "\n"
    elif unit_type is ast.For:
        output_string += (indent * 4 * " ")
        output_string += "for " + \
                         print_function(unit.target, indent) + " in " + \
                         print_function(unit.iter, indent) + ":\n"
        for line in unit.body:
            output_string += print_function(line, indent + 1)
        if len(unit.orelse) > 0:
            output_string += (indent * 4 * " ")
            output_string += "else:\n"
            for line in unit.orelse:
                output_string += print_function(line, indent + 1)
    elif unit_type is ast.While:
        output_string += (indent * 4 * " ")
        output_string += "while " + print_function(unit.test, indent) + ":\n"
        for line in unit.body:
            output_string += print_function(line, indent + 1)
        if len(unit.orelse) > 0:
            output_string += (indent * 4 * " ")
            output_string += "else:\n"
            for line in unit.orelse:
                output_string += print_function(line, indent + 1)
    elif unit_type is ast.If:
        output_string += (indent * 4 * " ")
        output_string += "if " + print_function(unit.test, indent) + ":\n"
        for line in unit.body:
            output_string += print_function(line, indent + 1)
        branch = unit.orelse
        while len(branch) == 1 and type(branch[0]) is ast.If:
            output_string += (indent * 4 * " ")
            output_string += "elif " + print_function(branch[0].test, indent) + ":\n"
            for line in branch[0].body:
                output_string += print_function(line, indent + 1)
            branch = branch[0].orelse
        if len(branch) > 0:
            output_string += (indent * 4 * " ")
            output_string += "else:\n"
            for line in branch:
                output_string += print_function(line, indent + 1)
    elif unit_type is ast.With:
        output_string += (indent * 4 * " ")
        output_string += "with "
        for item in unit.items:
            output_string += print_function(item, indent) + ", "
        if len(unit.items) > 0:
            output_string = output_string[:-2]
        output_string += ":\n"
        for line in unit.body:
            output_string += print_function(line, indent + 1)
    elif unit_type is ast.Raise:
        output_string += (indent * 4 * " ")
        output_string += "raise"
        if unit.exc is not None:
            output_string += " " + print_function(unit.exc, indent)
        output_string += "\n"
    elif type(unit) is ast.Try:
        output_string += (indent * 4 * " ") + "try:\n"
        for line in unit.body:
            output_string += print_function(line, indent + 1)
        for handler in unit.handlers:
            output_string += print_function(handler, indent)
        if len(unit.orelse) > 0:
            output_string += (indent * 4 * " ") + "else:\n"
            for line in unit.orelse:
                output_string += print_function(line, indent + 1)
        if len(unit.finalbody) > 0:
            output_string += (indent * 4 * " ") + "finally:\n"
            for line in unit.finalbody:
                output_string += print_function(line, indent + 1)
    elif unit_type is ast.Assert:
        output_string += (indent * 4 * " ")
        output_string += "assert " + print_function(unit.test, indent)
        if unit.msg is not None:
            output_string += ", " + print_function(unit.msg, indent)
        output_string += "\n"
    elif unit_type is ast.Import:
        output_string += (indent * 4 * " ") + "import "
        for n in unit.names:
            output_string += print_function(n, indent) + ", "
        if len(unit.names) > 0:
            output_string = output_string[:-2]
        output_string += "\n"
    elif unit_type is ast.ImportFrom:
        output_string += (indent * 4 * " ") + "from "
        output_string += ("." * unit.level if unit.level is not None else "") + unit.module + " import "
        for name in unit.names:
            output_string += print_function(name, indent) + ", "
        if len(unit.names) > 0:
            output_string = output_string[:-2]
        output_string += "\n"
    elif unit_type is ast.Global:
        output_string += (indent * 4 * " ") + "global "
        for name in unit.names:
            output_string += name + ", "
        output_string = output_string[:-2] + "\n"
    elif unit_type is ast.Expr:
        output_string += (indent * 4 * " ") + print_function(unit.value, indent) + "\n"
    elif unit_type is ast.Pass:
        output_string += (indent * 4 * " ") + "pass\n"
    elif unit_type is ast.Break:
        output_string += (indent * 4 * " ") + "break\n"
    elif unit_type is ast.Continue:
        output_string += (indent * 4 * " ") + "continue\n"

    elif unit_type is ast.BoolOp:
        output_string += "(" + print_function(unit.values[0], indent)
        for i in range(1, len(unit.values)):
            output_string += " " + print_function(unit.op, indent) + " " + \
                             print_function(unit.values[i], indent)
        output_string += ")"
    elif unit_type is ast.BinOp:
        output_string += "(" + print_function(unit.left, indent)
        output_string += " " + print_function(unit.op, indent) + " "
        output_string += print_function(unit.right, indent) + ")"
    elif unit_type is ast.UnaryOp:
        output_string += "(" + print_function(unit.op, indent) + " "
        output_string += print_function(unit.operand, indent) + ")"
    elif unit_type is ast.Lambda:
        output_string += "lambda "
        output_string += print_function(unit.arguments, indent) + ": "
        output_string += print_function(unit.body, indent)
    elif unit_type is ast.IfExp:
        output_string += "(" + print_function(unit.body, indent)
        output_string += " if " + print_function(unit.test, indent)
        output_string += " else " + print_function(unit.orelse, indent) + ")"
    elif unit_type is ast.Dict:
        output_string += "{ "
        for i in range(len(unit.keys)):
            output_string += print_function(unit.keys[i], indent)
            output_string += " : "
            output_string += print_function(unit.values[i], indent)
            output_string += ", "
        if len(unit.keys) >= 1:
            output_string = output_string[:-2]
        output_string += " }"
    elif unit_type is ast.Set:
        # Empty sets must be initialized in a special way
        if len(unit.elts) == 0:
            output_string += "set()"
        else:
            output_string += "{"
            for elt in unit.elts:
                output_string += print_function(elt, indent) + ", "
            output_string = output_string[:-2]
            output_string += "}"
    elif unit_type is ast.ListComp:
        output_string += "["
        output_string += print_function(unit.elt, indent) + " "
        for gen in unit.generators:
            output_string += print_function(gen, indent) + " "
        output_string = output_string[:-1]
        output_string += "]"
    elif unit_type is ast.SetComp:
        output_string += "{"
        output_string += print_function(unit.elt, indent) + " "
        for gen in unit.generators:
            output_string += print_function(gen, indent) + " "
        output_string = output_string[:-1]
        output_string += "}"
    elif unit_type is ast.DictComp:
        output_string += "{"
        output_string += print_function(unit.key, indent) + " : " + \
                         print_function(unit.value, indent) + " "
        for gen in unit.generators:
            output_string += print_function(gen, indent) + " "
        output_string = output_string[:-1]
        output_string += "}"
    elif unit_type is ast.GeneratorExp:
        output_string += "("
        output_string += print_function(unit.elt, indent) + " "
        for gen in unit.generators:
            output_string += print_function(gen, indent) + " "
        output_string = output_string[:-1]
        output_string += ")"
    elif unit_type is ast.Yield:
        output_string += "yield " + print_function(unit.value, indent)
    elif unit_type is ast.Compare:
        output_string += "(" + print_function(unit.left, indent)
        for i in range(len(unit.ops)):
            output_string += " " + print_function(unit.ops[i], indent)
            if i < len(unit.comparators):
                output_string += " " + print_function(unit.comparators[i], indent)
        if len(unit.comparators) > len(unit.ops):
            for i in range(len(unit.ops), len(unit.comparators)):
                output_string += " " + print_function(unit.comparators[i], indent)
        output_string += ")"
    elif unit_type is ast.Call:
        output_string += print_function(unit.func, indent) + "("
        for arg in unit.args:
            output_string += print_function(arg, indent) + ", "
        for key in unit.keywords:
            output_string += print_function(key, indent) + ", "
        if len(unit.args) + len(unit.keywords) >= 1:
            output_string = output_string[:-2]
        output_string += ")"
    elif unit_type is ast.Num:
        if unit.n is not None:
            if (type(unit.n) is complex) or (type(unit.n) is not complex and unit.n < 0):
                output_string += '(' + str(unit.n) + ')'
            else:
                output_string += str(unit.n)
    elif unit_type is ast.Str:
        if unit.s is not None:
            val = repr(unit.s)
            if val[0] == '"':  # There must be a single quote in there...
                val = "'''" + val[1:len(val) - 1] + "'''"
            output_string += val
    # s += "'" + a.s.replace("'", "\\'").replace('"', "\\'").replace("\n","\\n") + "'"
    elif unit_type is ast.Bytes:
        output_string += str(unit.s)
    elif unit_type is ast.NameConstant:
        output_string += str(unit.value)
    elif unit_type is ast.Constant:
        output_string += print_function(unit.value, indent)
    elif unit_type is ast.Attribute:
        output_string += print_function(unit.value, indent) + "." + str(unit.attr)
    elif unit_type is ast.Subscript:
        output_string += print_function(unit.value, indent) + "[" + print_function(unit.slice, indent) + "]"
    elif unit_type is ast.Name:
        output_string += unit.id
    elif unit_type is ast.List:
        output_string += "["
        for elt in unit.elts:
            output_string += print_function(elt, indent) + ", "
        if len(unit.elts) >= 1:
            output_string = output_string[:-2]
        output_string += "]"
    elif unit_type is ast.Tuple:
        output_string += "("
        for elt in unit.elts:
            output_string += print_function(elt, indent) + ", "
        if len(unit.elts) > 1:
            output_string = output_string[:-2]
        elif len(unit.elts) == 1:
            output_string = output_string[:-1]  # don't get rid of the comma! It clarifies that this is a tuple
        output_string += ")"
    elif unit_type is ast.Starred:
        output_string += "*" + print_function(unit.value, indent)
    elif unit_type is ast.Ellipsis:
        output_string += "..."
    elif unit_type is ast.Slice:
        if unit.lower is not None:
            output_string += print_function(unit.lower, indent)
        output_string += ":"
        if unit.upper is not None:
            output_string += print_function(unit.upper, indent)
        if unit.step is not None:
            output_string += ":" + print_function(unit.step, indent)
    elif unit_type is ast.ExtSlice:
        for dim in unit.dims:
            output_string += print_function(dim, indent) + ", "
        if len(unit.dims) > 0:
            output_string = output_string[:-2]
    elif unit_type is ast.Index:
        output_string += print_function(unit.value, indent)

    elif unit_type is ast.comprehension:
        output_string += "for "
        output_string += print_function(unit.target, indent) + " "
        output_string += "in "
        output_string += print_function(unit.iter, indent) + " "
        for cond in unit.ifs:
            output_string += "if "
            output_string += print_function(cond, indent) + " "
        output_string = output_string[:-1]
    elif unit_type is ast.ExceptHandler:
        output_string += (indent * 4 * " ") + "except"
        if unit.type is not None:
            output_string += " " + print_function(unit.type, indent)
            if unit.name is not None:
                output_string += " as " + unit.name
        output_string += ":\n"
        for line in unit.body:
            output_string += print_function(line, indent + 1)
    elif unit_type is ast.arguments:
        default_start = len(unit.args) - len(unit.defaults)
        for i in range(len(unit.args)):
            output_string += print_function(unit.args[i], indent)
            if i >= default_start:
                output_string += "=" + print_function(unit.defaults[i - default_start], indent)
            output_string += ", "
        if unit.vararg is not None:
            output_string += "*" + print_function(unit.vararg, indent) + ", "
        if unit.kwarg is not None:
            output_string += "**" + print_function(unit.kwarg, indent) + ", "
        if unit.vararg is None and unit.kwarg is None and len(unit.kwonlyargs) > 0:
            output_string += "*, "
        if len(unit.kwonlyargs) > 0:
            for i in range(len(unit.kwonlyargs)):
                output_string += print_function(unit.kwonlyargs[i], indent)
                output_string += "=" + print_function(unit.kw_defaults, indent) + ", "
        if len(unit.args) > 0 or unit.vararg is not None or unit.kwarg is not None or len(unit.kwonlyargs) > 0:
            output_string = output_string[:-2]
    elif unit_type is ast.arg:
        output_string += unit.arg
        if unit.annotation is not None:
            output_string += ": " + print_function(unit.annotation, indent)
    elif unit_type is ast.keyword:
        output_string += unit.arg + "=" + print_function(unit.value, indent)
    elif unit_type is ast.alias:
        output_string += unit.name
        if unit.asname is not None:
            output_string += " as " + unit.asname
    elif unit_type is ast.withitem:
        output_string += print_function(unit.context_expr, indent)
        if unit.optional_vars is not None:
            output_string += " as " + print_function(unit.optional_vars, indent)
    else:
        ops = {ast.And: "and", ast.Or: "or",
               ast.Add: "+", ast.Sub: "-", ast.Mult: "*", ast.Div: "/", ast.Mod: "%",
               ast.Pow: "**", ast.LShift: "<<", ast.RShift: ">>", ast.BitOr: "|",
               ast.BitXor: "^", ast.BitAnd: "&", ast.FloorDiv: "//",
               ast.Invert: "~", ast.Not: "not", ast.UAdd: "+", ast.USub: "-",
               ast.Eq: "==", ast.NotEq: "!=", ast.Lt: "<", ast.LtE: "<=",
               ast.Gt: ">", ast.GtE: ">=", ast.Is: "is", ast.IsNot: "is not",
               ast.In: "in", ast.NotIn: "not in"}
        if type(unit) in ops:
            return ops[type(unit)]
        if type(unit) in [ast.Load, ast.Store, ast.Del, ast.AugLoad, ast.AugStore, ast.Param]:
            return ""
        log("display\tMissing type: " + str(unit_type), "bug")
    return output_string


def formatContext(trace, verb):
    trace_d = {
        "value": {"Return": ("return statement"),
                  "Assign": ("right side of the assignment"),
                  "AugAssign": ("right side of the assignment"),
                  "Expression": ("expression"),
                  "Dict Comprehension": ("left value of the dict comprehension"),
                  "Yield": ("yield expression"),
                  "Repr": ("repr expression"),
                  "Attribute": ("attribute value"),
                  "Subscript": ("outer part of the subscript"),
                  "Index": ("inner part of the subscript"),
                  "Keyword": ("right side of the keyword"),
                  "Starred": ("value of the starred expression"),
                  "Name Constant": ("constant value"),
                  "Constant": ("constant value")},
        "values": {"Print": ("print statement"),
                   "Boolean Operation": ("boolean operation"),
                   "Dict": ("values of the dictionary")},
        "name": {"Function Definition": ("function name"),
                 "Class Definition": ("class name"),
                 "Except Handler": ("name of the except statement"),
                 "Alias": ("alias")},
        "names": {"Import": ("import"),
                  "ImportFrom": ("import"),
                  "Global": ("global variables")},
        "elt": {"List Comprehension": ("left element of the list comprehension"),
                "Set Comprehension": ("left element of the set comprehension"),
                "Generator": ("left element of the generator")},
        "elts": {"Set": ("set"),
                 "List": ("list"),
                 "Tuple": ("tuple")},
        "target": {"AugAssign": ("left side of the assignment"),
                   "For": ("target of the for loop"),
                   "Comprehension": ("target of the comprehension")},
        "targets": {"Delete": ("delete statement"),
                    "Assign": ("left side of the assignment")},
        "op": {"AugAssign": ("assignment"),
               "Boolean Operation": ("boolean operation"),
               "Binary Operation": ("binary operation"),
               "Unary Operation": ("unary operation")},
        "ops": {"Compare": ("comparison operation")},
        "arg": {"Keyword": ("left side of the keyword"),
                "Argument": ("argument")},
        "args": {"Function Definition": ("function arguments"),  # single item
                 "Lambda": ("lambda arguments"),  # single item
                 "Call": ("arguments of the function call"),
                 "Arguments": ("function arguments")},
        "key": {"Dict Comprehension": ("left key of the dict comprehension")},
        "keys": {"Dict": ("keys of the dictionary")},
        "kwarg": {"Arguments": ("keyword arg")},
        "kwargs": {"Call": ("keyword args of the function call")},  # single item
        "body": {"Module": ("main codebase"),  # list
                 "Interactive": ("main codebase"),  # list
                 "Expression": ("main codebase"),
                 "Suite": ("main codebase"),  # list
                 "Function Definition": ("function body"),  # list
                 "Class Definition": ("class body"),  # list
                 "For": ("lines of the for loop"),  # list
                 "While": ("lines of the while loop"),  # list
                 "If": ("main lines of the if statement"),  # list
                 "With": ("lines of the with block"),  # list
                 "Try": ("lines of the try block"),  # list
                 "Execute": ("exec expression"),
                 "Lambda": ("lambda body"),
                 "Ternary": ("ternary body"),
                 "Except Handler": ("lines of the except block")},  # list
        "orelse": {"For": ("else part of the for loop"),  # list
                   "While": ("else part of the while loop"),  # list
                   "If": ("lines of the else statement"),  # list
                   "Try": ("lines of the else statement"),  # list
                   "Ternary": ("ternary else value")},
        "test": {"While": ("test case of the while statement"),
                 "If": ("test case of the if statement"),
                 "Assert": ("assert expression"),
                 "Ternary": ("test case of the ternary expression")},
        "generators": {"List Comprehension": ("list comprehension"),
                       "Set Comprehension": ("set comprehension"),
                       "Dict Comprehension": ("dict comprehension"),
                       "Generator": ("generator")},
        "decorator_list": {"Function Definition": ("function decorators"),  # list
                           "Class Definition": ("class decorators")},  # list
        "iter": {"For": ("iterator of the for loop"),
                 "Comprehension": ("iterator of the comprehension")},
        "type": {"Raise": ("raised type"),
                 "Except Handler": ("type of the except statement")},
        "left": {"Binary Operation": ("left side of the binary operation"),
                 "Compare": ("left side of the comparison")},
        "bases": {"Class Definition": ("class bases")},
        "dest": {"Print": ("print destination")},
        "nl": {"Print": ("comma at the end of the print statement")},
        "context_expr": {"With item": ("context of the with statement")},
        "optional_vars": {"With item": ("context of the with statement")},  # single item
        "inst": {"Raise": ("raise expression")},
        "tback": {"Raise": ("raise expression")},
        "handlers": {"Try": ("except block")},
        "finalbody": {"Try": ("finally block")},  # list
        "msg": {"Assert": ("assert message")},
        "module": {"Import From": ("import module")},
        "level": {"Import From": ("import module")},
        "globals": {"Execute": ("exec global value")},  # single item
        "locals": {"Execute": ("exec local value")},  # single item
        "right": {"Binary Operation": ("right side of the binary operation")},
        "operand": {"Unary Operation": ("value of the unary operation")},
        "comparators": {"Compare": ("right side of the comparison")},
        "func": {"Call": ("function call")},
        "keywords": {"Call": ("keywords of the function call")},
        "starargs": {"Call": ("star args of the function call")},  # single item
        "attr": {"Attribute": ("attribute of the value")},
        "slice": {"Subscript": ("inner part of the subscript")},
        "lower": {"Slice": ("left side of the subscript slice")},
        "upper": {"Slice": ("right side of the subscript slice")},
        "step": {"Step": ("rightmost side of the subscript slice")},
        "dims": {"ExtSlice": ("slice")},
        "ifs": {"Comprehension": ("if part of the comprehension")},
        "vararg": {"Arguments": ("vararg")},
        "defaults": {"Arguments": ("default values of the arguments")},
        "asname": {"Alias": ("new name")},
        "items": {"With": ("context of the with statement")}
    }

    # Find what type this is by trying to find the closest container in the path
    i = 0
    while i < len(trace):
        if type(trace[i]) is tuple:
            if trace[i][0] == "value" and trace[i][1] == "Attribute":
                pass
            elif trace[i][0] in trace_d:
                break
            elif trace[i][0] in ["id", "n", "s"]:
                pass
            else:
                log("display\tformatContext\tSkipped field: " + str(trace[i]), "bug")
        i += 1
    else:
        return ""  # this is probably covered by the line number

    field, typ = trace[i]
    if field in trace_d and typ in trace_d[field]:
        context = trace_d[field][typ]
        return verb + "the " + context
    else:
        log("display\tformatContext\tMissing field: " + str(field) + "," + str(typ), "bug")
        return ""


def formatList(node, field):
    if type(node) != list:
        return None
    s = ""
    nameMap = {"body": "line", "targets": "value", "values": "value", "orelse": "line",
               "names": "name", "keys": "key", "elts": "value", "ops": "operator",
               "comparators": "value", "args": "argument", "keywords": "keyword"}

    # Find what type this is
    itemType = nameMap[field] if field in nameMap else "line"

    if len(node) > 1:
        s = "the " + itemType + "s: "
        for line in node:
            s += formatNode(line) + ", "
    elif len(node) == 1:
        s = "the " + itemType + " "
        f = formatNode(node[0])
        if itemType == "line":
            f = "[" + f + "]"
        s += f
    return s


def formatNode(node):
    """Create a string version of the given node"""
    if node is None:
        return ""
    t = type(node)
    if t is str:
        return "'" + node + "'"
    elif t is int or t is float:
        return str(node)
    elif t is list:
        return formatList(node, None)
    else:
        return print_function(node, 0)

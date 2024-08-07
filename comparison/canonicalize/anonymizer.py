import ast


class AnonymizeNames(ast.NodeTransformer):
    def __init__(self):
        self.name_map = {}
        self.reverse_name_map = {}
        self.var_counter = 0
        self.func_counter = 0
        self.param_counter = 0
        self.scope_stack = []

    def anonymize_name(self, name, prefix):
        scope = self.scope_stack[-1] if self.scope_stack else "global"
        scoped_name = f"{scope}_{name}"
        new_name = None
        if scoped_name not in self.name_map:
            if prefix == "var":
                new_name = f"{scope}_variable{self.var_counter}"
                self.var_counter += 1
            elif prefix == "func":
                new_name = f"{scope}_function{self.func_counter}"
                self.func_counter += 1
            elif prefix == "param":
                new_name = f"{scope}_param{self.param_counter}"
                self.param_counter += 1
            self.name_map[scoped_name] = new_name
            self.reverse_name_map[new_name] = name
        return self.name_map[scoped_name]

    def visit_FunctionDef(self, node):
        self.scope_stack.append(node.name)
        self.var_counter = 0
        self.param_counter = 0
        node.name = self.anonymize_name(node.name, "func")

        # Anonymize function parameters
        for arg in node.args.args:
            arg.arg = self.anonymize_name(arg.arg, "param")

        # Visit the body of the function to handle nested functions and variables
        self.generic_visit(node)

        # Update return statements to use anonymized function names
        for stmt in node.body:
            if isinstance(stmt, ast.Return) and isinstance(stmt.value, ast.Name):
                if stmt.value.id not in self.name_map.values():
                    if stmt.value.id in self.reverse_name_map.values():
                        # The value to use here is the key that maps to the value
                        stmt.value.id = list(self.reverse_name_map.keys())[
                            list(self.reverse_name_map.values()).index(stmt.value.id)]
                    else:
                        stmt.value.id = self.anonymize_name(stmt.value.id, "func")
        self.scope_stack.pop()
        return node

    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Store):
            node.id = self.anonymize_name(node.id, "var")
        elif isinstance(node.ctx, ast.Load):
            scope = self.scope_stack[-1] if self.scope_stack else "global"
            scoped_name = f"{scope}_{node.id}"
            if scoped_name in self.name_map:
                node.id = self.name_map[scoped_name]
            else:
                flag = True
                # Check if the variable is from an outer scope
                for outer_scope in reversed(self.scope_stack[:-1]):
                    flag = False
                    scoped_name = f"{outer_scope}_{node.id}"
                    if scoped_name in self.name_map:
                        node.id = self.name_map[scoped_name]
                        break
                if flag:
                    scoped_name = f"global_{node.id}"
                    if scoped_name in self.name_map:
                        node.id = self.name_map[scoped_name]
        return node

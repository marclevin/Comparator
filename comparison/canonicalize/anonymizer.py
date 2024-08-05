import ast


class AnonymizeNames(ast.NodeTransformer):
    def __init__(self):
        self.name_map = {}
        self.reverse_name_map = {}
        self.var_counter = 0
        self.func_counter = 0
        self.param_counter = 0

    def anonymize_name(self, name, prefix):
        if name not in self.name_map:
            if prefix == "var":
                new_name = f"variable{self.var_counter}"
                self.var_counter += 1
            elif prefix == "func":
                new_name = f"function{self.func_counter}"
                self.func_counter += 1
            elif prefix == "param":
                new_name = f"param{self.param_counter}"
                self.param_counter += 1
            self.name_map[name] = new_name
            self.reverse_name_map[new_name] = name
        return self.name_map[name]

    def visit_FunctionDef(self, node):
        node.name = self.anonymize_name(node.name, "func")
        for arg in node.args.args:
            arg.arg = self.anonymize_name(arg.arg, "param")
        self.generic_visit(node)
        return node

    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Store):
            node.id = self.anonymize_name(node.id, "var")
        elif isinstance(node.ctx, ast.Load):
            if node.id in self.name_map:
                node.id = self.name_map[node.id]
        return node

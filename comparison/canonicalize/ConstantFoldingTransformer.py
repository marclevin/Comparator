import ast


class ConstantFoldingTransformer(ast.NodeTransformer):
    def visit_BinOp(self, node):
        self.generic_visit(node)
        if isinstance(node.left, ast.Constant) and isinstance(node.right, ast.Constant):
            try:
                return ast.Constant(eval(compile(ast.Expression(node), '', 'eval')))
            except:
                pass
        return node

    def visit_BoolOp(self, node):
        self.generic_visit(node)
        if all(isinstance(value, ast.Constant) for value in node.values):
            try:
                return ast.Constant(eval(compile(ast.Expression(node), '', 'eval')))
            except:
                pass
        return node

    def visit_Compare(self, node):
        self.generic_visit(node)
        if isinstance(node.left, ast.Constant) and all(isinstance(comp, ast.Constant) for comp in node.comparators):
            try:
                return ast.Constant(eval(compile(ast.Expression(node), '', 'eval')))
            except:
                pass
        return node

    def visit_IfExp(self, node):
        self.generic_visit(node)
        if isinstance(node.test, ast.Constant):
            return node.body if node.test.value else node.orelse
        return node

    def visit_Call(self, node):
        self.generic_visit(node)
        if all(isinstance(arg, ast.Constant) for arg in node.args):
            try:
                return ast.Constant(eval(compile(ast.Expression(node), '', 'eval')))
            except:
                pass
        return node

    def visit_Attribute(self, node):
        self.generic_visit(node)
        return node

    def visit_Slice(self, node):
        self.generic_visit(node)
        return node

    def visit_Constant(self, node):
        return node

    def visit_Name(self, node):
        return node

    def generic_visit(self, node):
        return super().generic_visit(node)

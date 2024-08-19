import ast


class ConditionalRedundancyTransformer(ast.NodeTransformer):
    def visit_If(self, node):
        self.generic_visit(node)
        if isinstance(node.test, ast.Constant):
            return node.body if node.test.value else node.orelse
        return node

    def visit_IfExp(self, node):
        self.generic_visit(node)
        if isinstance(node.test, ast.Constant):
            return node.body if node.test.value else node.orelse
        return node

    def visit_While(self, node):
        self.generic_visit(node)
        if isinstance(node.test, ast.Constant):
            return node.body if node.test.value else []
        return node

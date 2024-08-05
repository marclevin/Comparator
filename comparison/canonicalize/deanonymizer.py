import ast


class DeanonymizeNames(ast.NodeTransformer):
    reverse_name_map = {}

    def __init__(self, reverse_name_map):
        self.reverse_name_map = reverse_name_map

    def visit_FunctionDef(self, node):
        if node.name in self.reverse_name_map:
            node.name = self.reverse_name_map[node.name]
        self.generic_visit(node)
        return node

    def visit_Name(self, node):
        if node.id in self.reverse_name_map:
            node.id = self.reverse_name_map[node.id]
        return node

    def visit_Param(self, node):
        if node.id in self.reverse_name_map:
            node.id = self.reverse_name_map[node.id]
        return node

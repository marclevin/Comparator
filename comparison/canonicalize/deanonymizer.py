import ast


class DeanonymizeNames(ast.NodeTransformer):
    def __init__(self, original_tree=None, reverse_map=None):
        self.original_tree = original_tree
        self.reverse_map = reverse_map
        self.global_id_map = self._create_global_id_map(original_tree) if original_tree else {}

    @staticmethod
    def _create_global_id_map(tree):
        global_id_map = {}
        for node in ast.walk(tree):
            if hasattr(node, 'global_id'):
                global_id_map[node.global_id] = node
        return global_id_map

    def _get_original_name(self, node):
        if hasattr(node, 'global_id') and node.global_id in self.global_id_map:
            original_node = self.global_id_map[node.global_id]
            if isinstance(original_node, ast.FunctionDef):
                return original_node.name
            elif isinstance(original_node, ast.Name):
                return original_node.id
            elif isinstance(original_node, ast.arg):
                return original_node.arg
        return None

    def visit_FunctionDef(self, node):
        if self.reverse_map and node.name in self.reverse_map.keys():
            node.name = self.reverse_map[node.name]
            for arg in node.args.args:
                if arg.arg in self.reverse_map:
                    arg.arg = self.reverse_map.get(arg.arg, arg.arg)
        else:
            original_name = self._get_original_name(node)
            if original_name:
                node.name = original_name
                for arg in node.args.args:
                    original_arg_name = self._get_original_name(arg)
                    if original_arg_name:
                        arg.arg = original_arg_name
        self.generic_visit(node)
        return node

    def visit_Name(self, node):
        if self.reverse_map and node.id in self.reverse_map.keys():
            node.id = self.reverse_map[node.id]
        else:
            original_name = self._get_original_name(node)
            if original_name:
                node.id = original_name
        return node

    def visit_Param(self, node):
        if self.reverse_map and node.id in self.reverse_map.keys():
            node.id = self.reverse_map[node.id]
        else:
            original_name = self._get_original_name(node)
            if original_name:
                node.id = original_name
        return node

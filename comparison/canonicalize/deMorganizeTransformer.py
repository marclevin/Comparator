import ast


class DeMorganizeTransformer(ast.NodeTransformer):
    def visit_UnaryOp(self, node):
        if isinstance(node.op, ast.Not):
            if isinstance(node.operand, ast.BoolOp):
                # Apply De Morgan's law based on the type of BoolOp
                if isinstance(node.operand.op, ast.And):
                    # not (a and b) -> not a or not b
                    return ast.BoolOp(
                        op=ast.Or(),
                        values=[self.visit(ast.UnaryOp(op=ast.Not(), operand=value))
                                for value in node.operand.values]
                    )
                elif isinstance(node.operand.op, ast.Or):
                    # not (a or b) -> not a and not b
                    return ast.BoolOp(
                        op=ast.And(),
                        values=[self.visit(ast.UnaryOp(op=ast.Not(), operand=value))
                                for value in node.operand.values]
                    )
        # Visit other nodes normally
        return self.generic_visit(node)

    def visit_BoolOp(self, node):
        # Recursively visit BoolOp children to ensure all nested operations are transformed
        node.values = [self.visit(value) for value in node.values]
        return node

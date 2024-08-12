import ast


class DeadCodeEliminationTransformer(ast.NodeTransformer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._live_vars = set()
        self._live_vars_stack = []
        self._global_vars = set()
        self._reachable = True

    def visit_FunctionDef(self, node):
        self._live_vars_stack.append(set())
        self._reachable = True
        self.generic_visit(node)
        self._live_vars_stack.pop()
        return node

    def visit_Assign(self, node):
        self.generic_visit(node)
        if not node.targets:
            return node  # No targets to process
        target = node.targets[0]
        if isinstance(target, ast.Name):
            if self._reachable:
                if self._live_vars_stack:
                    self._live_vars_stack[-1].add(target.id)
                else:
                    self._global_vars.add(target.id)
            else:
                return None  # Remove unreachable assignment
        return node

    def visit_Return(self, node):
        self.generic_visit(node)
        self._reachable = False
        return node

    def visit_If(self, node):
        self._live_vars_stack.append(set(self._live_vars_stack[-1]))
        self._reachable = True
        node.body = [self.visit(n) for n in node.body if self.visit(n) is not None]
        node.orelse = [self.visit(n) for n in node.orelse if self.visit(n) is not None]
        self._live_vars_stack.pop()
        return node

    def visit_While(self, node):
        self._live_vars_stack.append(set(self._live_vars_stack[-1]))
        self._reachable = True
        self.visit(node.test)
        node.body = [self.visit(n) for n in node.body if self.visit(n) is not None]
        node.orelse = [self.visit(n) for n in node.orelse if self.visit(n) is not None]
        self._live_vars_stack.pop()
        return node

    def visit_For(self, node):
        self._live_vars_stack.append(set(self._live_vars_stack[-1]))
        self._reachable = True
        node.body = [self.visit(n) for n in node.body if self.visit(n) is not None]
        node.orelse = [self.visit(n) for n in node.orelse if self.visit(n) is not None]
        self._live_vars_stack.pop()
        return node

    def visit_With(self, node):
        self._live_vars_stack.append(set(self._live_vars_stack[-1]))
        self._reachable = True
        node.body = [self.visit(n) for n in node.body if self.visit(n) is not None]
        self._live_vars_stack.pop()
        return node

    def visit_ExceptHandler(self, node):
        self._live_vars_stack.append(set(self._live_vars_stack[-1]))
        self._reachable = True
        node.body = [self.visit(n) for n in node.body if self.visit(n) is not None]
        self._live_vars_stack.pop()
        return node

    def visit_Try(self, node):
        self._live_vars_stack.append(set(self._live_vars_stack[-1]))
        self._reachable = True
        node.body = [self.visit(n) for n in node.body if self.visit(n) is not None]
        node.orelse = [self.visit(n) for n in node.orelse if self.visit(n) is not None]
        node.finalbody = [self.visit(n) for n in node.finalbody if self.visit(n) is not None]
        self._live_vars_stack.pop()
        return node

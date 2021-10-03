class Or:
    def __init__(self, left, right):
        self.left = left
        self.right = right


class Not:
    def __init__(self, expr):
        self.expr = expr


class Var:
    def __init__(self, name, is_bool):
        self.name = name
        self.isBool = is_bool


class And:
    def __init__(self, left, right):
        self.left = left
        self.right = right


class Eq:
    def __init__(self, left, right):
        self.left = left
        self.right = right


class Call:
    def __init__(self, fun, args):
        self.fun = fun
        self.args = args


def stringify(ast_node):
    if isinstance(ast_node, Or):
        return "(%s) | (%s)" % (stringify(ast_node.left), stringify(ast_node.right))
    if isinstance(ast_node, And):
        return "(%s) & (%s)" % (stringify(ast_node.left), stringify(ast_node.right))
    if isinstance(ast_node, Eq):
        return "%s = %s" % (stringify(ast_node.left), stringify(ast_node.right))
    if isinstance(ast_node, Not):
        return "!(%s)" % (stringify(ast_node.expr))
    if isinstance(ast_node, Var):
        return ast_node.name
    if isinstance(ast_node, Call):
        return "%s(%s)" % (ast_node.fun, ", ".join(map(stringify, ast_node.args)))
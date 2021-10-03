from Ast import stringify, Var, Call


def solve_equalities(equalities):
    graph = TermGraph()
    term_graph_nodes = []
    for equality in equalities:
        term_graph_nodes.append((graph.add_term(equality[0].left), graph.add_term(equality[0].right)))
    for index in range(len(equalities)):
        if equalities[index][1]:
            graph.merge(term_graph_nodes[index][0], term_graph_nodes[index][1])
    for index in range(len(equalities)):
        if not equalities[index][1]:
            if term_graph_nodes[index][0].repr() == term_graph_nodes[index][1].repr():
                return False, None
    values = {}
    counter = [0]
    for node in term_graph_nodes:
        _assign_values(node[0], values, counter)
        _assign_values(node[1], values, counter)
    return True, values


def _assign_values(v, values, counter):
    r = v.repr()
    if r.ast_node not in values:
        values[r.ast_node] = counter[0]
        counter[0] += 1
    values[v.ast_node] = values[r.ast_node]
    for arg in v.args:
        _assign_values(arg, values, counter)


class Vertex:
    def __init__(self, fun, args, ast_node):
        self.fun = fun
        self.args = args
        self.find = self
        self.ccpar = set()
        self.ast_node = ast_node

    def repr(self):
        if self.find == self:
            return self
        return self.find.repr()


class TermGraph:
    def __init__(self):
        self._vertices = {}

    def congruent(self, v1, v2):
        if v1.fun != v2.fun:
            return False
        for arg1, arg2 in zip(v1.args, v2.args):
            if arg1.repr() != arg2.repr():
                return False
        return True

    def ccpar(self, v):
        return v.repr().ccpar

    def merge(self, v1, v2):
        cc1, cc2 = v1.repr(), v2.repr()
        if cc1 != cc2:
            ccpar1, ccpar2 = self.ccpar(v1), self.ccpar(v2)
            self.union(cc1, cc2)
            for t1 in ccpar1:
                for t2 in ccpar2:
                    if t1.repr() != t2.repr() and self.congruent(t1, t2):
                        self.merge(t1, t2)

    def union(self, v1, v2):
        r1, r2 = v1.repr(), v2.repr()
        r2.find = r1
        r1.ccpar = r1.ccpar.union(r2.ccpar)
        r2.ccpar = set()

    def add_term(self, term, pred=None):
        str_repr = stringify(term)
        if str_repr in self._vertices:
            v = self._vertices[str_repr]
            if not pred is None:
                v.ccpar.add(pred)
            return v
        if isinstance(term, Var):
            vertex = Vertex(term.name, [], term)
            self._vertices[str_repr] = vertex
            return vertex
        if isinstance(term, Call):
            vertex = Vertex(term.fun, [], term)
            for arg in term.args:
                vertex.args.append(self.add_term(arg, vertex))
            self._vertices[str_repr] = vertex
            return vertex
        raise AssertionError("term must be variable or call")

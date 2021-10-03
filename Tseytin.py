from Ast import Or, Not, Var, And, Eq


class TseytinTransformer:
    def __init__(self):
        self._counter = 1
        self._clauses = []
        self._original_vars = {}
        self._eq_vars = {}

    def _transform(self, formula):
        if isinstance(formula, Or):
            # c = a | b
            a = self._transform(formula.left)
            b = self._transform(formula.right)
            c = self._counter
            self._counter += 1
            self._clauses.append([a, b, -c])
            self._clauses.append([-a, c])
            self._clauses.append([-b, c])
            return c
        if isinstance(formula, And):
            # c = a & b
            a = self._transform(formula.left)
            b = self._transform(formula.right)
            c = self._counter
            self._counter += 1
            self._clauses.append([-a, -b, c])
            self._clauses.append([a, -c])
            self._clauses.append([b, -c])
            return c
        if isinstance(formula, Not):
            # c = !a
            a = self._transform(formula.expr)
            c = self._counter
            self._counter += 1
            self._clauses.append([-a, -c])
            self._clauses.append([a, c])
            return c
        if isinstance(formula, Eq):
            self._eq_vars[formula] = self._counter
            self._counter += 1
            return self._counter - 1
        if isinstance(formula, Var):
            var_name = formula.name
            if var_name in self._original_vars:
                return self._original_vars[var_name]
            self._original_vars[var_name] = self._counter
            self._counter += 1
            return self._counter - 1


def convert_to_cnf(formula):
    transformer = TseytinTransformer()
    root_var = transformer._transform(formula)
    transformer._clauses.append([root_var])
    return transformer._clauses, transformer._counter - 1, transformer._original_vars, transformer._eq_vars

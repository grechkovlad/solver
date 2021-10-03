from Ast import Or, Not, Var, And, Eq, Call


class Tokenizer:
    def __init__(self, text):
        self._str = text.replace(" ", "")
        self._pos = -1
        self._current = []
        self.advance()

    def _set_current(self):
        if self._pos == len(self._str):
            self._current = "\0"
            return
        if self._str[self._pos] in operators:
            self._current = [str(self._str[self._pos])]
            return
        name = ""
        while self._pos < len(self._str) and not (self._str[self._pos] in operators):
            name = name + self._str[self._pos]
            self._pos += 1
        self._pos -= 1
        self._current = [name]

    def current(self):
        return self._current[0]

    def rollback(self, val):
        self._current = [val, self._current[0]]

    def advance(self):
        if len(self._current) == 2:
            self._current = [self._current[1]]
            return
        self._pos += 1
        self._set_current()


def parse_call(tokenizer):
    fun_name = tokenizer.current()
    tokenizer.advance()
    args = []
    while tokenizer.current() != ")":
        tokenizer.advance()
        args.append(parse_expr(tokenizer))
    tokenizer.advance()
    return Call(fun_name, args)


def parse_expr(tokenizer):
    name = tokenizer.current()
    tokenizer.advance()
    if tokenizer.current() == "(":
        tokenizer.rollback(name)
        return parse_call(tokenizer)
    else:
        return Var(name, is_bool=False)


def parse_eq(tokenizer):
    left_expr = parse_expr(tokenizer)
    tokenizer.advance()
    right_expr = parse_expr(tokenizer)
    return Eq(left_expr, right_expr)


def parse_conj(tokenizer):
    negate = False
    if tokenizer.current() == "!":
        negate = True
        tokenizer.advance()
    if tokenizer.current() == "(":
        tokenizer.advance()
        expr = parse_bool_expr(tokenizer)
        tokenizer.advance()
        return Not(expr) if negate else expr
    else:
        name = tokenizer.current()
        tokenizer.advance()
        if tokenizer.current() in ["(", "="]:
            tokenizer.rollback(name)
            return parse_eq(tokenizer)
        else:
            var = Var(name, is_bool=True)
            return Not(var) if negate else var


def parse_disj(tokenizer):
    res = parse_conj(tokenizer)
    while tokenizer.current() == "&":
        tokenizer.advance()
        res = And(res, parse_conj(tokenizer))
    return res


def parse_bool_expr(tokenizer):
    res = parse_disj(tokenizer)
    while tokenizer.current() == "|":
        tokenizer.advance()
        res = Or(res, parse_disj(tokenizer))
    return res


def parse(formula):
    tokenizer = Tokenizer(formula)
    return parse_bool_expr(tokenizer)


operators = ['!', '&', '|', '(', ')', ',', '=']

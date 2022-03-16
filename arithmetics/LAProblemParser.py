import re


class Tokenizer:
    def __init__(self, str):
        self._text = str
        self._current = "SOF"
        self._pos = -1

    def current(self):
        return self._current

    def advance(self):
        if self._current == "EOF":
            raise EOFError()
        self._pos += 1
        while self._pos < len(self._text) and self._text[self._pos] == ' ':
            self._pos += 1
        if self._pos == len(self._text):
            self._current = "EOF"
            return
        if self._text[self._pos] in ["+", "-", "="]:
            self._current = self._text[self._pos]
            return
        if self._text[self._pos] in ["<", ">"]:
            self._current = self._text[self._pos: self._pos + 2]
            self._pos += 1
            return
        num_match = re.match(r"\d+", self._text[self._pos:])
        if num_match:
            matched = num_match.group(0)
            self._current = int(matched)
            self._pos += len(matched) - 1
            return
        word_match = re.match("[a-zA-Z][a-zA-Z0-9]*", self._text[self._pos:])
        if word_match:
            matched = word_match.group(0)
            self._current = matched
            self._pos += len(matched)
            return
        raise ValueError(self._text[self._pos:])


class VarNamesStorage:
    def __init__(self):
        self._names = dict()
        self._counter = 0

    def numerate(self, var_name: str):
        if var_name not in self._names:
            self._names[var_name] = self._counter
            self._counter += 1
        return self._names[var_name]

    def get_var_count(self):
        return self._counter

    def get_names_dict(self):
        return self._names


def parse(constraints):
    names = VarNamesStorage()
    constraints_intermediate = []
    for constraint in constraints:
        tokenizer = Tokenizer(constraint)
        tokenizer.advance()
        var_name, coeff = _read_monom(tokenizer)
        monoms = [(names.numerate(var_name), coeff)]
        while tokenizer.current() in ["+", "-"]:
            negate = tokenizer.current() == "-"
            tokenizer.advance()
            var_name, coeff = _read_monom(tokenizer)
            if negate:
                coeff = -coeff
            monoms.append((names.numerate(var_name), coeff))
        sign = tokenizer.current()
        tokenizer.advance()
        if tokenizer.current() == "-":
            tokenizer.advance()
            rhs = -tokenizer.current()
        else:
            rhs = tokenizer.current()
        constraints_intermediate.append((monoms, sign, rhs))

    result = []

    for monoms, sign, rhs in constraints_intermediate:
        coeffs = [0] * names.get_var_count()
        for var_index, coeff in monoms:
            coeffs[var_index] += coeff
        result.append((coeffs, sign, rhs))

    return result, names.get_names_dict()


def _read_monom(tokenizer: Tokenizer):
    negate = False
    if tokenizer.current() == "-":
        negate = True
        tokenizer.advance()
    coeff = -1 if negate else 1
    if isinstance(tokenizer.current(), int):
        coeff *= tokenizer.current()
        tokenizer.advance()
    var_name = tokenizer.current()
    tokenizer.advance()
    return var_name, coeff

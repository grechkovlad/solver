from copy import deepcopy
from functools import reduce


class DPLL:
    def __init__(self, clauses, var_num):
        self._var_num = var_num
        self._clauses = deepcopy(clauses)
        self._values = [None] * (var_num + 1)
        self._is_clause_alive = [True] * len(clauses)
        self._is_literal_alive = []
        for clause in clauses:
            self._is_literal_alive.append([True] * len(clause))

    def _alive_clauses(self):
        for clause_index in range(len(self._clauses)):
            if not self._is_clause_alive[clause_index]:
                continue
            yield clause_index

    def _alive_literals(self, clause_index):
        for literal_index in range(len(self._clauses[clause_index])):
            if not self._is_literal_alive[clause_index][literal_index]:
                continue
            yield literal_index

    def solve(self):
        return (True, self._values) if self._brute() else (False, None)

    def add_clause(self, clause):
        self._clauses.append(clause)
        self._values = [None] * (self._var_num + 1)
        self._is_clause_alive = [True] * len(self._clauses)
        self._is_literal_alive = []
        for clause in self._clauses:
            self._is_literal_alive.append([True] * len(clause))

    def _find_alone_literal(self):
        for clause_index in self._alive_clauses():
            candidate = 0
            for literal_index in self._alive_literals(clause_index):
                if candidate == 0:
                    candidate = self._clauses[clause_index][literal_index]
                else:
                    candidate = 0
                    break
            if candidate != 0:
                return candidate
        return 0

    def _is_dead_propagation(self, literal):
        for clause_index in self._alive_clauses():
            if self._is_literal_alive[clause_index].count(True) == 1 and self._clauses[clause_index].count(
                    -literal) == 1:
                return True
        return False

    def _rollback_propagation(self, literal, killed_clauses):
        self._values[abs(literal)] = None
        for clause_index in self._alive_clauses():
            for literal_index in range(len(self._clauses[clause_index])):
                if self._clauses[clause_index][literal_index] == -literal:
                    self._is_literal_alive[clause_index][literal_index] = True
        for killed_clause in killed_clauses:
            self._is_clause_alive[killed_clause] = True

    def _propagate(self, literal):
        self._values[abs(literal)] = literal > 0
        killed_clauses = []
        for clause_index in self._alive_clauses():
            for literal_index in self._alive_literals(clause_index):
                if self._clauses[clause_index][literal_index] == literal:
                    killed_clauses.append(clause_index)
                    self._is_clause_alive[clause_index] = False
                    break
                if self._clauses[clause_index][literal_index] == -literal:
                    self._is_literal_alive[clause_index][literal_index] = False
                    break
        return killed_clauses

    def _find_homogenious_literal(self):
        homogenity = [None] * (self._var_num + 1)
        for clause_index in self._alive_clauses():
            for literal_index in self._alive_literals(clause_index):
                var = abs(self._clauses[clause_index][literal_index])
                if homogenity[var] == 0:
                    continue
                if homogenity[var] == None:
                    homogenity[var] = 1 if self._clauses[clause_index][literal_index] > 0 else -1
                    continue
                if homogenity[var] * self._clauses[clause_index][literal_index] < 0:
                    homogenity[var] = 0
        for var in range(1, self._var_num + 1):
            if homogenity[var] == 1 or homogenity[var] == -1:
                return var * homogenity[var]
        return 0

    def _find_any_var(self):
        for clause_index in self._alive_clauses():
            for literal_index in self._alive_literals(clause_index):
                return self._clauses[clause_index][literal_index]
        raise AssertionError("Illegal state: no alive var found")

    def _brute(self):
        if not any(self._is_clause_alive):
            return True
        alone_literal = self._find_alone_literal()
        if alone_literal != 0:
            if self._is_dead_propagation(alone_literal):
                return False
            killed_clauses = self._propagate(alone_literal)
            if self._brute():
                return True
            else:
                self._rollback_propagation(alone_literal, killed_clauses)
                return False
        homogenious_literal = self._find_homogenious_literal()
        if homogenious_literal != 0:
            killed_clauses = self._propagate(homogenious_literal)
            if self._brute():
                return True
            else:
                self._rollback_propagation(alone_literal, killed_clauses)
                return False
        any_var = self._find_any_var()
        killed_clauses = self._propagate(-any_var)
        if self._brute():
            return True
        self._rollback_propagation(-any_var, killed_clauses)
        killed_clauses = self._propagate(any_var)
        if self._brute():
            return True
        self._rollback_propagation(any_var, killed_clauses)
        return False

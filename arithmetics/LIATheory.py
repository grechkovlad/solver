from arithmetics.LRATheory import solve as solve_rational
from fractions import Fraction as Q


def solve(constraints):
    rational_solution = solve_rational(constraints)
    if rational_solution is None:
        return None
    fractional_var_ind = -1
    for var_ind in range(len(rational_solution)):
        if rational_solution[var_ind].__round__() != rational_solution[var_ind]:
            fractional_var_ind = var_ind
            break
    if fractional_var_ind == -1:
        return list(map(lambda f: f.__round__(), rational_solution))
    floor, ceil = rational_solution[fractional_var_ind].__floor__(), rational_solution[fractional_var_ind].__ceil__()
    var_count = len(constraints[0][0])
    floor_constraint = (
        [Q(0)] * fractional_var_ind + [Q(1)] + [Q(0)] * (var_count - fractional_var_ind - 1), "<=", floor)
    ceil_constraint = (
        [Q(0)] * fractional_var_ind + [Q(1)] + [Q(0)] * (var_count - fractional_var_ind - 1), ">=", ceil)
    floor_branch_solution = solve(constraints + [floor_constraint])
    if floor_branch_solution is not None:
        return floor_branch_solution
    ceil_branch_solution = solve(constraints + [ceil_constraint])
    return ceil_branch_solution

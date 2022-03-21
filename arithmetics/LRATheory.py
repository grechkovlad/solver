import copy
from fractions import Fraction as Q


def solve(constraints):
    if len(constraints) == 0:
        return []
    obj_func_coeffs, a, c, base_vars, original_to_new = _create_aux_problem_canonical_repr(constraints)
    total_var_count = len(obj_func_coeffs)
    obj_fun_bias = 0
    original_var_count = len(constraints[0][0])
    if all(map(lambda x: x >= 0, c)):
        return [0] * original_var_count

    min_c_ind = 0
    for constraint_ind in range(len(a)):
        if c[constraint_ind] < c[min_c_ind]:
            min_c_ind = constraint_ind

    obj_func_coeffs, obj_fun_bias, a, c, base_vars = _pivot(obj_func_coeffs, obj_fun_bias, a, c, base_vars, min_c_ind,
                                                            total_var_count - 1)

    while True:
        in_var = -1
        for var_ind in range(total_var_count):
            if obj_func_coeffs[var_ind] > 0:
                in_var = var_ind
                break
        if in_var == -1:
            break
        increase_limit_val = 0
        limiting_constraint_ind = -1
        for constraint_ind in range(len(a)):
            if a[constraint_ind][in_var] >= 0:
                continue
            current_increase_limit = -c[constraint_ind] / a[constraint_ind][in_var]
            if limiting_constraint_ind == -1 or current_increase_limit < increase_limit_val:
                increase_limit_val = current_increase_limit
                limiting_constraint_ind = constraint_ind
        obj_func_coeffs, obj_fun_bias, a, c, base_vars = _pivot(obj_func_coeffs, obj_fun_bias, a, c, base_vars,
                                                                limiting_constraint_ind, in_var)

    if obj_fun_bias != 0:
        return None

    internal_valuation = [0] * total_var_count
    for constraint_ind in range(len(a)):
        internal_valuation[base_vars[constraint_ind]] = c[constraint_ind]

    valuation = [0] * original_var_count
    for var_ind in range(len(valuation)):
        valuation[var_ind] = internal_valuation[original_to_new[var_ind][0]] - internal_valuation[
            original_to_new[var_ind][1]]

    return valuation


def _pivot(obj_func_coeffs, obj_fun_bias, a, c, base_vars, out_constraint_index, in_var):
    total_var_count = len(obj_func_coeffs)
    out_var = base_vars[out_constraint_index]
    in_var_coff = a[out_constraint_index][in_var]
    obj_fun_bias_new = obj_fun_bias - obj_func_coeffs[in_var] * c[out_constraint_index] / in_var_coff
    obj_func_coeffs_new = copy.deepcopy(obj_func_coeffs)
    for var_ind in range(total_var_count):
        delta = - obj_func_coeffs[in_var] * a[out_constraint_index][var_ind] / in_var_coff
        obj_func_coeffs_new[var_ind] += delta
    obj_func_coeffs_new[out_var] += obj_func_coeffs[in_var] / in_var_coff
    a_new = [[]]
    c_new = []
    base_vars_new = [in_var]
    c_new.append(-c[out_constraint_index] / in_var_coff)
    for var_ind in range(total_var_count):
        a_new[0].append(-a[out_constraint_index][var_ind] / in_var_coff)
    a_new[0][out_var] = 1 / in_var_coff
    a_new[0][in_var] = 0
    for constraint_ind in range(len(a)):
        if constraint_ind == out_constraint_index:
            continue
        base_vars_new.append(base_vars[constraint_ind])
        c_new.append(c[constraint_ind] + a[constraint_ind][in_var] * c_new[0])
        a_new_row = []
        for var_ind in range(total_var_count):
            a_new_row.append(a[constraint_ind][var_ind] + a[constraint_ind][in_var] * a_new[0][var_ind])
        a_new_row[in_var] = 0
        a_new.append(a_new_row)
    return obj_func_coeffs_new, obj_fun_bias_new, a_new, c_new, base_vars_new


def _add_constraint(lhs, sign, rhs, total_var_count, A, c):
    match sign:
        case "<=":
            row = [Q(-1 * coeff) for coeff in lhs] + [Q(val) for val in lhs] + [Q(0)] * (
                    total_var_count - 2 * len(lhs) - 1) + [Q(1)]
            A.append(row)
            c.append(Q(rhs))
        case ">=":
            _add_constraint([-1 * coeff for coeff in lhs], "<=", -rhs, total_var_count, A, c)
        case "=":
            _add_constraint(lhs, "<=", rhs, total_var_count, A, c)
            _add_constraint(lhs, ">=", rhs, total_var_count, A, c)


def _create_aux_problem_canonical_repr(constraints):
    original_var_count = len(constraints[0][0])
    slack_var_count = len(constraints) + [sign for _, sign, _ in constraints].count("=")
    original_to_new = {ind: (ind, ind + original_var_count) for ind in range(original_var_count)}
    total_var_count = original_var_count * 2 + slack_var_count + 1
    A = []
    c = []
    for lhs, sign, rhs in constraints:
        _add_constraint(lhs, sign, rhs, total_var_count, A, c)
    base_vars = list(range(2 * original_var_count, total_var_count - 1))
    obj_func = [Q(0)] * (total_var_count - 1) + [Q(-1)]
    return obj_func, A, c, base_vars, original_to_new

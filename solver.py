from DPLL import DPLL

from Parser import parse
from Tseytin import convert_to_cnf
from Ast import stringify
from EqualityTheory import solve_equalities

formula = open("formula.txt").readline().strip()

ast = parse(formula)
clauses, var_num, original_vars, eq_vars = convert_to_cnf(ast)

dpll = DPLL(clauses, var_num)
while True:
    skeleton_sat, skeleton_values = dpll.solve()
    if skeleton_sat:
        equalities = []
        eq_clause_negated = []
        for eq, index in eq_vars.items():
            if not skeleton_values[index] is None:
                equalities.append((eq, skeleton_values[index]))
                eq_clause_negated.append(-index if skeleton_values[index] else index)
        eq_sat, eq_values = solve_equalities(equalities)
        if eq_sat:
            print("SAT")
            for var in original_vars:
                print("%s = %s" % (var, "Any" if skeleton_values[original_vars[var]] is None else str(
                    skeleton_values[original_vars[var]])))
            for term, val in eq_values.items():
                print("%s = v%d" % (stringify(term), val))
            break
        else:
            dpll.add_clause(eq_clause_negated)
    else:
        print("UNSAT")
        break

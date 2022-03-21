from arithmetics.LAProblemParser import parse
from arithmetics.LIATheory import solve

lines = open("lia_problem.txt").readlines()
constraints, names = parse(lines)
solution = solve(constraints)

if solution is None:
    print("UNSAT")
else:
    print("SAT")
    print("\n".join(["%s = %d" % (name, solution[index]) for name, index in names.items()]))

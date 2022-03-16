from arithmetics.LAProblemParser import parse
from arithmetics.LRATheory import solve

lines = open("lra_problem.txt").readlines()
constraints, names = parse(lines)
solution = solve(constraints)

if solution is None:
    print("UNSAT")
else:
    print("SAT")
    print("\n".join(["%s = %f" % (name, solution[index]) for name, index in names.items()]))

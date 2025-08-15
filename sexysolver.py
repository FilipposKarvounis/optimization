import os
import pyomo.environ as pyomo

# Function to read data from a file
def read_data(filename):
    with open(filename, "r") as f:
        lines = [line.strip() for line in f.readlines() if line.strip()]

    num_pms = int(lines[0].split()[1])
    num_vms = int(lines[0].split()[2])

    # Parse VM demands
    vms = []
    start = lines.index("VM demands:") + 1
    for i in range(start, start + num_vms):
        parts = lines[i].split()
        vms.append((float(parts[1]), float(parts[2])))

    # Parse PM capacities
    pms = []
    start = lines.index("PM capacities:") + 1
    for i in range(start, start + num_pms):
        parts = lines[i].split()
        pms.append((float(parts[1]), float(parts[2]), int(parts[3])))

    # Parse OS compatibility
    os_compatibility = [[0 for _ in range(num_pms)] for _ in range(num_vms)]
    start = lines.index("OS compatibility:") + 1
    for i in range(start, len(lines)):
        vm, pm, compatible = map(int, lines[i].split())
        os_compatibility[vm][pm] = compatible

    return num_vms, num_pms, vms, pms, os_compatibility

# Solver function
def solve_problem(filename):
    num_vms, num_pms, vms, pms, os_compatibility = read_data(filename)

    model = pyomo.ConcreteModel()

    model.VMs = pyomo.RangeSet(0, num_vms - 1)
    model.PMs = pyomo.RangeSet(0, num_pms - 1)

    model.x = pyomo.Var(model.VMs, model.PMs, domain=pyomo.Binary)
    model.y = pyomo.Var(model.PMs, domain=pyomo.Binary)

    # Load balancing variables
    model.Umax = pyomo.Var(domain=pyomo.NonNegativeReals)
    model.Umin = pyomo.Var(domain=pyomo.NonNegativeReals)
    epsilon = 0.1  # Μπορείς να το κάνεις parameter αν θέλεις

    def objective_function(m):
        return sum(m.y[j] for j in m.PMs)

    model.objective = pyomo.Objective(rule=objective_function, sense=pyomo.minimize)

    def vm_assignment_rule(m, i):
        return sum(m.x[i, j] for j in m.PMs) == 1

    model.vm_assignment = pyomo.Constraint(model.VMs, rule=vm_assignment_rule)

    # Constraint: Μέγιστος αριθμός VMs ανά PM
    def max_vms_per_pm_rule(m, j):
        return sum(m.x[i, j] for i in m.VMs) <= pms[j][2]
    model.max_vms_per_pm = pyomo.Constraint(model.PMs, rule=max_vms_per_pm_rule)

    def resource_constraints(m, j):
        return (
            sum(vms[i][0] * m.x[i, j] for i in m.VMs) <= pms[j][0] * m.y[j],
            sum(vms[i][1] * m.x[i, j] for i in m.VMs) <= pms[j][1] * m.y[j]
        )

    model.cpu_constraints = pyomo.Constraint(model.PMs, rule=lambda m, j: resource_constraints(m, j)[0])
    model.mem_constraints = pyomo.Constraint(model.PMs, rule=lambda m, j: resource_constraints(m, j)[1])

    def compatibility_rule(m, i, j):
        return m.x[i, j] <= os_compatibility[i][j]

    model.os_constraints = pyomo.Constraint(model.VMs, model.PMs, rule=compatibility_rule)

    # Load balancing constraints
    def umax_rule(m, j):
        return m.Umax >= sum(vms[i][0] * m.x[i, j] for i in m.VMs) / pms[j][0]
    model.umax_constraint = pyomo.Constraint(model.PMs, rule=umax_rule)

    def umin_rule(m, j):
        return m.Umin <= sum(vms[i][0] * m.x[i, j] for i in m.VMs) / pms[j][0]
    model.umin_constraint = pyomo.Constraint(model.PMs, rule=umin_rule)

    def epsilon_rule(m):
        return m.Umax - m.Umin <= epsilon
    model.epsilon_constraint = pyomo.Constraint(rule=epsilon_rule)

    solver = pyomo.SolverFactory('gurobi')
    results = solver.solve(model, tee=True)

    return results, model

# Main script to process all problems
results_dir = "results"
os.makedirs(results_dir, exist_ok=True)

problem_dir = "problems"
for root, _, files in os.walk(problem_dir):
    for file in files:
        if file.endswith(".txt"):
            filepath = os.path.join(root, file)
            print(f"Solving: {filepath}")
            results, model = solve_problem(filepath)

            # Save results
            with open(os.path.join(results_dir, f"{file}_results.txt"), "w") as f:
                for i in model.VMs:
                    for j in model.PMs:
                        if pyomo.value(model.x[i, j]) > 0.5:
                            f.write(f"VM {i} -> PM {j}\n")
                f.write(f"Active PMs: {sum(pyomo.value(model.y[j]) for j in model.PMs)}\n")

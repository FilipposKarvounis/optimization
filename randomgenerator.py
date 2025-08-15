import random
import os

# Constants for problem generation
CLASSES = 10
INSTANCES_PER_CLASS = 10

# Class-specific configurations
CLASS_CONFIGS = [
    {"num_vms": 10, "num_pms": 5, "cpu_demand_strictness": 0.5, "mem_demand_strictness": 0.5},
    {"num_vms": 20, "num_pms": 10, "cpu_demand_strictness": 0.6, "mem_demand_strictness": 0.6},
    {"num_vms": 30, "num_pms": 15, "cpu_demand_strictness": 0.7, "mem_demand_strictness": 0.7},
    {"num_vms": 40, "num_pms": 20, "cpu_demand_strictness": 0.8, "mem_demand_strictness": 0.8},
    {"num_vms": 50, "num_pms": 25, "cpu_demand_strictness": 0.9, "mem_demand_strictness": 0.9},
    {"num_vms": 60, "num_pms": 30, "cpu_demand_strictness": 1.0, "mem_demand_strictness": 1.0},
    {"num_vms": 70, "num_pms": 35, "cpu_demand_strictness": 1.1, "mem_demand_strictness": 1.1},
    {"num_vms": 80, "num_pms": 40, "cpu_demand_strictness": 1.2, "mem_demand_strictness": 1.2},
    {"num_vms": 90, "num_pms": 45, "cpu_demand_strictness": 1.3, "mem_demand_strictness": 1.3},
    {"num_vms": 100, "num_pms": 50, "cpu_demand_strictness": 1.4, "mem_demand_strictness": 1.4}
]

class VM:
    def __init__(self, cpu_demand, mem_demand):
        self.cpu_demand = cpu_demand
        self.mem_demand = mem_demand

class PM:
    def __init__(self, cpu_capacity, mem_capacity, max_vms):
        self.cpu_capacity = cpu_capacity
        self.mem_capacity = mem_capacity
        self.max_vms = max_vms

# Function to initialize VMs and PMs
def initialize_entities(vms, pms, config):
    for i in range(config["num_vms"]):
        vms.append(VM(
            cpu_demand=random.randint(1, 10) * config["cpu_demand_strictness"],
            mem_demand=random.randint(1, 10) * config["mem_demand_strictness"]
        ))
    for j in range(config["num_pms"]):
        pms.append(PM(
            cpu_capacity=random.randint(1, 50),
            mem_capacity=random.randint(1, 50),
            max_vms=max(1, random.randint(1, config["num_vms"]))
        ))

# Function to generate OS compatibility matrix
def generate_os_compatibility(num_vms, num_pms):
    return [[1 if random.random() < 0.8 else 0 for _ in range(num_pms)] for _ in range(num_vms)]

# Function to save problem to disk
def save_problem(vms, pms, os_compatibility, class_id, instance_id):
    folder_name = f"problems/class_{class_id}"
    os.makedirs(folder_name, exist_ok=True)
    file_path = f"{folder_name}/instance_{instance_id}.txt"

    with open(file_path, "w") as f:
        f.write(f"{len(vms) + len(pms)} {len(pms)} {len(vms)}\n")
        f.write("VM demands:\n")
        for i, vm in enumerate(vms):
            f.write(f"{i} {vm.cpu_demand} {vm.mem_demand}\n")
        f.write("PM capacities:\n")
        for j, pm in enumerate(pms):
            f.write(f"{j} {pm.cpu_capacity} {pm.mem_capacity} {pm.max_vms}\n")
        f.write("OS compatibility:\n")
        for i, row in enumerate(os_compatibility):
            for j, compatible in enumerate(row):
                if compatible:
                    f.write(f"{i} {j} {compatible}\n")

# Main problem generation loop
for class_id, config in enumerate(CLASS_CONFIGS, start=1):
    for instance_id in range(1, INSTANCES_PER_CLASS + 1):
        vms = []
        pms = []
        initialize_entities(vms, pms, config)
        os_compatibility = generate_os_compatibility(config["num_vms"], config["num_pms"])
        save_problem(vms, pms, os_compatibility, class_id, instance_id)

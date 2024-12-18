# Efe Kaan Fidancı - 22102589
# Görkem Kadir Solun - 22003214
# Cahit Ediz Civan - 22003206

import time

import gurobipy as gp
from gurobipy import GRB

# Set the start time
start_time = time.time()

# Parameters
items = [
    "Granola Bars",
    "Trail Mix",
    "Dried Fruit",
    "Canned Beans",
    "Rice",
    "Energy Drink",
    "Pasta",
    "Jerky",
]
weights = [2, 1, 2, 6, 4, 6, 5, 2]  # in kgs
calories = [300, 800, 200, 800, 1100, 150, 1200, 500]  # in cals
costs = [5, 10, 4, 7, 8, 3, 9, 6]  # in dollars

ece_capacity = 10
arda_capacity = 8

ece_calories_requirement = 2000
arda_calories_requirement = 1500
total_calories_requirement = ece_calories_requirement + arda_calories_requirement

model = gp.Model("Optimal Meal Planning for Hiking")
model.setParam(GRB.Param.OutputFlag, 0)

# Decision Variables
x = {}
y = {}
for i in range(len(items)):
    x[i] = model.addVar(
        vtype=GRB.BINARY, name=f"x_{i}"
    )  # x_i: item i is included in Ece's bag
    y[i] = model.addVar(
        vtype=GRB.BINARY, name=f"y_{i}"
    )  # y_i: item i is included in Arda's bag

# Constraints
# Capacity (Weight) Constraint for Ece's Bag
ece_weight_constraint = sum(weights[i] * x[i] for i in range(len(items)))
model.addConstr(ece_weight_constraint <= ece_capacity)

# Capacity (Weight) Constraint for Arda's Bag
arda_weight_constraint = sum(weights[i] * y[i] for i in range(len(items)))
model.addConstr(arda_weight_constraint <= arda_capacity)

# Total Calories Constraint
total_calories_constraint = sum(calories[i] * (x[i] + y[i]) for i in range(len(items)))
model.addConstr(total_calories_constraint >= total_calories_requirement)

model.addConstrs((x[i] + y[i] <= 1 for i in range(len(items))))

# Objective Function
total_cost = sum(costs[i] * (x[i] + y[i]) for i in range(len(items)))
model.setObjective(total_cost, GRB.MINIMIZE)

# Solve the second question
model.optimize()

# Results
if model.status == GRB.OPTIMAL:
    print("Optimal solution found:")

    ece_bag = []
    arda_bag = []
    for i in range(len(items)):
        if x[i].x > 0.5:
            ece_bag.append(items[i])
        if y[i].x > 0.5:
            arda_bag.append(items[i])

    print("Ece's bag contains:", ece_bag)
    print("Arda's bag contains:", arda_bag)
    print(f"Total cost: ${model.objVal}")
else:
    print("No optimal solution found.")

# Print the runtime
print(f"Runtime: {time.time() - start_time:.2f} seconds")

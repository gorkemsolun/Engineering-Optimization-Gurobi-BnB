# Efe Kaan Fidancı - 22102589
# Görkem Kadir Solun - 22003214
# Cahit Ediz Civan - NOTE DOLDUR NOTE

# Use python 3.12.8 64-bit

import gurobipy as gp
import pandas as pd
from gurobipy import GRB

# Define the cities and costs
cities = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"]
city_travel_costs = {
    "A": {
        "A": 0,
        "B": 300,
        "C": 450,
        "D": 150,
        "E": 225,
        "F": 330,
        "G": 495,
        "H": 600,
        "I": 315,
        "J": 405,
    },
    "B": {
        "A": 300,
        "B": 0,
        "C": 180,
        "D": 330,
        "E": 315,
        "F": 375,
        "G": 510,
        "H": 195,
        "I": 420,
        "J": 240,
    },
    "C": {
        "A": 450,
        "B": 180,
        "C": 0,
        "D": 210,
        "E": 495,
        "F": 135,
        "G": 240,
        "H": 435,
        "I": 180,
        "J": 345,
    },
    "D": {
        "A": 150,
        "B": 330,
        "C": 210,
        "D": 0,
        "E": 360,
        "F": 195,
        "G": 300,
        "H": 405,
        "I": 270,
        "J": 285,
    },
    "E": {
        "A": 225,
        "B": 315,
        "C": 495,
        "D": 360,
        "E": 0,
        "F": 240,
        "G": 465,
        "H": 180,
        "I": 285,
        "J": 225,
    },
    "F": {
        "A": 330,
        "B": 375,
        "C": 135,
        "D": 195,
        "E": 240,
        "F": 0,
        "G": 270,
        "H": 300,
        "I": 345,
        "J": 390,
    },
    "G": {
        "A": 495,
        "B": 510,
        "C": 240,
        "D": 300,
        "E": 465,
        "F": 270,
        "G": 0,
        "H": 135,
        "I": 255,
        "J": 210,
    },
    "H": {
        "A": 600,
        "B": 195,
        "C": 435,
        "D": 405,
        "E": 180,
        "F": 300,
        "G": 135,
        "H": 0,
        "I": 285,
        "J": 315,
    },
    "I": {
        "A": 315,
        "B": 420,
        "C": 180,
        "D": 270,
        "E": 285,
        "F": 345,
        "G": 255,
        "H": 285,
        "I": 0,
        "J": 150,
    },
    "J": {
        "A": 405,
        "B": 240,
        "C": 345,
        "D": 285,
        "E": 225,
        "F": 390,
        "G": 210,
        "H": 315,
        "I": 150,
        "J": 0,
    },
}
city_benefit_points = {
    "A": 350,
    "B": 420,
    "C": 270,
    "D": 300,
    "E": 380,
    "F": 410,
    "G": 320,
    "H": 450,
    "I": 330,
    "J": 400,
}

# Create the model
model = gp.Model("TanTechTour")

# Decision variables
# xij{0,1}: binary variable that determines if the tour travels from city i to city j.
# yi{0,1}: binary variable that determines if city i is visited.
# ui: Auxiliary continuous variable used to eliminate sub-tours. Represents the order of visiting each city.
x = model.addVars(cities, cities, vtype=GRB.BINARY, name="x")
y = model.addVars(cities, vtype=GRB.BINARY, name="y")
u = model.addVars(cities, vtype=GRB.CONTINUOUS, name="u")

# Constants
max_cities_to_visit = 7  # Maximum number of cities to visit is 7
max_travel_cost = 1500  # Maximum travel cost is $1,500
# NOTE: Check this value
n = min(len(cities), max_cities_to_visit)  # Number of cities to visit


# Objective function
model.setObjective(
    gp.quicksum(
        city_benefit_points[i] * y[i] for i in cities
    ),  # Maximize the total benefit points
    GRB.MAXIMIZE,
)

# Constraints
# Budget constraint: The total travel cost cannot exceed $1,500.
model.addConstr(
    gp.quicksum(city_travel_costs[i][j] * x[i, j] for i in cities for j in cities)
    <= max_travel_cost
)

# Start and end in city A: The tour starts and ends at city A.
model.addConstr(gp.quicksum(x["A", j] for j in cities) == 1)  # Start at A
model.addConstr(gp.quicksum(x[i, "A"] for i in cities) == 1)  # End at A

# Cannot visit the a city from itself: The tour cannot visit the same city twice.
for i in cities:
    model.addConstr(x[i, i] == 0)

# City visit limit: The total number of cities visited is at most max_cities_to_visit.
model.addConstr(gp.quicksum(y[i] for i in cities) <= max_cities_to_visit)

# Inbound and outbound conservation: For each city i, ensure that if a city is visited, there is an inbound and outbound connection.
for i in cities:
    model.addConstr(
        gp.quicksum(x[i, j] for j in cities) == y[i]
    )  # If city i is visited, there must be an outbound connection
    model.addConstr(
        gp.quicksum(x[j, i] for j in cities) == y[i]
    )  # If city i is visited, there must be an inbound connection

# Subtour elimination: To avoid subtours, use the Miller-Tucker-Zemlin (MTZ) formulation.
for i in cities[1:]:
    for j in cities[1:]:
        if i != j and i != "A" and j != "A":
            model.addConstr(
                u[i] - u[j] + (n - 1) * x[i, j] <= (n - 2)
            )  # MTZ formulation


# Optimize the model
model.optimize()

# Print the x[i, j] values as matrix using pandas
print("Tour matrix (Xij): ")
x_values = {i: {j: int(abs(x[i, j].x)) for j in cities} for i in cities}
x_df = pd.DataFrame(x_values)
print(x_df)


print(f"Total benefit points: {model.objVal}")
# Calculate the total travel cost
total_travel_cost = sum(
    city_travel_costs[i][j] * x[i, j].x for i in cities for j in cities
)
print(f"Total travel cost: {total_travel_cost}")

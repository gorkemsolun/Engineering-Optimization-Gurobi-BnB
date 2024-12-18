import time as time

from scipy.optimize import linprog

# Start the timer
start_time = time.time()


class Item:

    def __init__(self, name, weight, calories, cost):
        self.name = name
        self.weight = weight
        self.calories = calories
        self.cost = cost

    def __repr__(self):
        return (
            f"{self.name}: weight={self.weight}, "
            f"calories={self.calories}, cost=${self.cost:.2f}"
        )


class Branch_And_Bound:

    def __init__(self, items, capacity1, capacity2, total_calories_req):
        self.items = items
        self.n_items = len(items)
        self.capacity1 = capacity1
        self.capacity2 = capacity2
        self.total_calories_req = total_calories_req
        self.best_cost = float("inf")
        self.best_x = [0] * self.n_items
        self.best_y = [0] * self.n_items
        self.feasible = False
        self.iterations = 0

    def is_feasible(self, x, y):
        total_weight_ece = sum(
            self.items[i].weight for i in range(self.n_items) if x[i] == 1
        )
        total_weight_arda = sum(
            self.items[i].weight for i in range(self.n_items) if y[i] == 1
        )

        return (
            total_weight_ece <= self.capacity1 and total_weight_arda <= self.capacity2
        )

    def calculate_cost(self, x, y):
        return sum(
            self.items[i].cost for i in range(self.n_items) if x[i] == 1 or y[i] == 1
        )

    def calories_met(self, x, y):
        total_calories = sum(
            self.items[i].calories
            for i in range(self.n_items)
            if x[i] == 1 or y[i] == 1
        )
        return total_calories >= self.total_calories_req

    def display_bag(self, x, y):
        ece_bag = []
        arda_bag = []
        for i in range(self.n_items):
            if x[i] == 1:
                ece_bag.append(self.items[i])
            elif y[i] == 1:
                arda_bag.append(self.items[i])
        print("----------------------------------------")
        print(f"Ece's bag contains items: {ece_bag}")
        print(f"Arda's bag contains items: {arda_bag}")
        print(f"Total Cost: {self.best_cost}")
        print(f"Total iterations: {self.iterations}")
        print("----------------------------------------")

    from scipy.optimize import linprog

    def linear_relaxation(self, x, y, level):
        # Total number of items
        n = len(self.items)

        # Derive the current range of indices to consider based on the level
        current_indices = list(range(n - level - 1, n))

        # Objective function: minimize cost
        costs = [self.items[i].cost for i in current_indices]

        # We need to double the variables to represent x and y
        c = costs + costs  # Costs for x and y

        # Constraints
        # Capacity constraints for bag x and y
        weights = [self.items[i].weight for i in current_indices]
        A_ub = [
            weights + [0] * len(weights),  # x capacity constraint
            [0] * len(weights) + weights,  # y capacity constraint
        ]
        x_capacity = self.capacity1 - sum(
            self.items[i].weight for i in range(self.n_items) if x[i] == 1
        )
        y_capacity = self.capacity2 - sum(
            self.items[i].weight for i in range(self.n_items) if y[i] == 1
        )
        b_ub = [x_capacity, y_capacity]

        # Calorie constraint
        calories = [self.items[i].calories for i in current_indices]
        A_ub.append(
            [-c for c in calories] + [-c for c in calories]
        )  # Total calories constraint (at least threshold)
        total_calories = sum(
            self.items[i].calories
            for i in range(self.n_items)
            if x[i] == 1 or y[i] == 1
        )
        b_ub.append(-(self.total_calories_req - total_calories))

        # Add constraint to ensure sum of x[i] and y[i] cannot exceed 1
        for i in range(len(current_indices)):
            constraint = [0] * (2 * len(current_indices))
            constraint[i] = 1  # x[i]
            constraint[len(current_indices) + i] = 1  # y[i]
            A_ub.append(constraint)
            b_ub.append(1)

        # Bounds for each variable (fractions between 0 and 1)
        bounds = [(0, 1)] * (2 * len(current_indices))

        # Solve the linear programming problem
        result = linprog(c, A_ub=A_ub, b_ub=b_ub, bounds=bounds, method="highs")

        if result.success:
            # Extract the solutions for x and y
            solution = {
                "x": result.x[: len(current_indices)],
                "y": result.x[len(current_indices) :],
                "total_cost": result.fun,
            }
            return result.fun
        else:
            solution = {"error": "No feasible solution found"}
            return float("inf")

    def branch_and_bound(self, level, x, y):
        self.iterations += 1
        cost = self.calculate_cost(x, y)
        # Pruning: If the current solution is infeasible or suboptimal (Cannot keep adding and beat the current optimal) stop branching
        if not self.is_feasible(x, y) or (cost >= self.best_cost):
            return

        if cost < self.best_cost and self.calories_met(x, y):
            self.best_x = x[:]
            self.best_y = y[:]
            self.best_cost = cost
            self.feasible = True
            print("Current best:")
            self.display_bag(x, y)

        if level == self.n_items:
            return

        linear_solution = self.linear_relaxation(x, y, level)
        if linear_solution > self.best_cost:
            # cannot find a better  solution, prune
            return

        x_state = x[:]
        y_state = y[:]

        # Branch for not including the item
        self.branch_and_bound(level + 1, x, y)

        # Branch for including the item in Ece's bag
        x[:] = x_state
        y[:] = y_state
        x[level] = 1
        self.branch_and_bound(level + 1, x, y)

        # Branch for including the item in Arda's bag
        x[:] = x_state
        y[:] = y_state
        y[level] = 1
        self.branch_and_bound(level + 1, x, y)

        return

    def solve(self):
        x = [0] * self.n_items
        y = [0] * self.n_items
        self.branch_and_bound(0, x, y)
        # Display the results
        if self.feasible:
            x_sol = self.best_x
            y_sol = self.best_y
            print("Optimal Solution Found:")
            self.display_bag(x_sol, y_sol)
        else:
            print("No feasible solution found.")


def main():
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

    # Create a list to hold Item objects
    Items = []

    # Populate the Items list
    for i in range(len(items)):
        Items.append(Item(items[i], weights[i], calories[i], costs[i]))

    ece_capacity = 10
    arda_capacity = 8

    ece_calories_requirement = 2000
    arda_calories_requirement = 1500
    total_calories_requirement = ece_calories_requirement + arda_calories_requirement

    bnb = Branch_And_Bound(
        Items,
        capacity1=ece_capacity,
        capacity2=arda_capacity,
        total_calories_req=total_calories_requirement,
    )
    bnb.solve()


if __name__ == "__main__":
    main()

# Print the time taken to run the script
print(f"Time taken: {time.time() - start_time:.2f} seconds.")

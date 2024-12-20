import time


class Item:
    
    def __init__(self, name, weight, calories, cost):
        self.name = name
        self.weight = weight
        self.calories = calories
        self.cost = cost
    def __repr__(self):
        return (f"{self.name}: weight={self.weight}, "
                f"calories={self.calories}, cost=${self.cost:.2f}")

class Branch_And_Bound:
    def __init__(self, items, capacity1, capacity2, total_calories_req):
        self.items = items
        self.n_items = len(items)
        self.capacity1 = capacity1
        self.capacity2 = capacity2
        self.total_calories_req = total_calories_req
        self.best_cost = float('inf')
        self.best_x = [0] * self.n_items
        self.best_y = [0] * self.n_items
        self.feasible = False
        self.iterations = 0
    
    def is_feasible(self, x, y):
        total_weight_ece = sum(self.items[i].weight for i in range(self.n_items) if x[i] == 1)
        total_weight_arda = sum(self.items[i].weight for i in range(self.n_items) if y[i] == 1)

        return (total_weight_ece <= self.capacity1 and
                total_weight_arda <= self.capacity2 )

    def calculate_cost(self, x, y):
        return sum(self.items[i].cost for i in range(self.n_items) if x[i] == 1 or y[i] == 1)
    
    def calories_met(self, x, y):
        total_calories = sum(self.items[i].calories for i in range(self.n_items) if x[i] == 1 or y[i] == 1)
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
        print("----------------------------------------")
    
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
            
        
        if level == self.n_items:
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
    items = ["Granola Bars", "Trail Mix", "Dried Fruit", "Canned Beans", "Rice", "Energy Drink", "Pasta", "Jerky"]
    weights = [2, 1, 2, 6, 4, 6, 5, 2] # in kgs
    calories = [300, 800, 200, 800, 1100, 150, 1200, 500] # in cals
    costs = [5, 10, 4, 7, 8, 3, 9, 6] # in dollars

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

    start_time = time.time()
    bnb = Branch_And_Bound(Items, capacity1=ece_capacity, capacity2=arda_capacity, total_calories_req=total_calories_requirement)
    bnb.solve()
    end_time = time.time()

    print(f'Total time elapsed: {end_time - start_time}')
  
if __name__ == "__main__":
    main()
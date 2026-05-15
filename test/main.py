from ortools.sat.python import cp_model
import math
from symCords import manualProblem


def getDistMatrix(node_coords,all_nodes):
    # Pre-calculate Euclidean distances
    dist_matrix = {}
    for i in all_nodes:
        for j in all_nodes:
            d = math.sqrt((node_coords[i][0] - node_coords[j][0])**2 + 
                          (node_coords[i][1] - node_coords[j][1])**2)
            dist_matrix[i, j] = int(d * 100000) # CP-SAT works with integers
    return dist_matrix
    



def solve_gtsp():
    model = cp_model.CpModel()

    node_coords,clusters = manualProblem("4ulysses16","symmetric")
    
    
    all_nodes = list(node_coords.keys())
    num_nodes = len(all_nodes)
    depot = 0
    dist_matrix = getDistMatrix(node_coords,all_nodes)


        # 2. Decision Variables
    # edges[i, j] is 1 if we travel from node i to node j
    edges = {}
    for i in all_nodes:
        for j in all_nodes:
            if i != j:
                edges[i, j] = model.NewBoolVar(f'edge_{i}_{j}')

    # nodes_present[i] is 1 if node i is visited
    nodes_present = {i: model.NewBoolVar(f'node_{i}') for i in all_nodes}

    # 3. Constraints
    
    # Rule 1: Always visit the depot
    model.Add(nodes_present[depot] == 1)

    # Rule 2: Exactly one node per cluster must be visited
    for c_id, members in clusters.items():
        model.Add(sum(nodes_present[m] for m in members) == 1)

    # Rule 3: Flow Conservation (In-degree == Out-degree == nodes_present)
    for i in all_nodes:
        model.Add(sum(edges[i, j] for j in all_nodes if i != j) == nodes_present[i])
        model.Add(sum(edges[j, i] for j in all_nodes if i != j) == nodes_present[i])

    # Rule 4: Subtour Elimination (MTZ Constraints)
    # rank[i] is the order in which node i is visited
    ranks = {i: model.NewIntVar(0, num_nodes, f'rank_{i}') for i in all_nodes}
    for i in all_nodes:
        for j in all_nodes:
            if i != j and i != depot and j != depot:
                # If edge(i,j) is active, then rank[j] >= rank[i] + 1
                model.Add(ranks[j] >= ranks[i] + 1).OnlyEnforceIf(edges[i, j])

    # 4. Objective: Minimize Total Distance
    total_distance = sum(edges[i, j] * dist_matrix[i, j] for i, j in edges)
    model.Minimize(total_distance)

    # 5. Solve
    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        print(f"Total Distance: {solver.ObjectiveValue() / 100000.0}")
        # Reconstruct Route
        curr = depot
        route = [depot]
        while True:
            for j in all_nodes:
                if curr != j and solver.Value(edges[curr, j]):
                    route.append(j)
                    curr = j
                    break
            if curr == depot: break
        print("Optimal Route:", route)
        return dist_matrix
    else:
        print("No solution found.")


def getManualRouteDistance(routeString,distmatrix):
    print(distmatrix)
    route = routeString
    total_dist = 0
    for i,point in enumerate(route):
        if i+1 is len(route):
            dist = distmatrix[int(point),int(route[0])]
            print(distmatrix[int(point),int(route[0])])
            total_dist +=dist
            break
        else: 
            total_dist += distmatrix[int(point),int(route[i+1])]
    print("results gemini")
    print(total_dist/100000.0)
    print(route)


#node_coords,clusters = manualProblem("31pr152","symmetric")
#distmatrix = getDistMatrix(node_coords,node_coords.keys())
#getManualRouteDistance([
    #0, 36, 14, 2, 28, 3, 12, 4, 11, 5, 
    #10, 6, 18, 9, 7, 16, 40, 64, 43, 80, 
    #87, 111, 103, 116, 118, 143, 133, 119, 146, 121, 
    #150, 0
#],distmatrix)
distmatrix = solve_gtsp()


# optimal: [0, 4, 6, 12, 0]
# gemini-thinking: [0, 4, 6, 12, 0]

#gemini-fast first try: [0, 13, 4, 5, 0] = 18.71
#gemini-fast second try: [0, 11, 5, 4, 0] = 18.02
#shortest path greedy: [0, 1, 13, 4, 0] = 19.91


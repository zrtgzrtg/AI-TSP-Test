from ortools.sat.python import cp_model
import math
from symCords import manualProblem




def getDistMatrix(node_coords, all_nodes):
    dist_matrix = {}

    for i in all_nodes:
        for j in all_nodes:
            dx = node_coords[i][0] - node_coords[j][0]
            dy = node_coords[i][1] - node_coords[j][1]
            d = math.sqrt(dx * dx + dy * dy)

            # TSPLIB EUC_2D rounding
            dist_matrix[i, j] = int(d + 0.5)

    return dist_matrix


def route_distance(route, dist_matrix):
    """Compute cyclic route distance for a GTSP tour."""
    total = 0
    for idx, node in enumerate(route):
        next_node = route[(idx + 1) % len(route)]
        total += dist_matrix[node, next_node]
    return total


def reconstruct_cycle_from_edges(selected_nodes, edges, solver):
    """
    Reconstruct one cycle over the selected GTSP nodes.

    The returned route is depot-free. Its first node is arbitrary because GTSP/TSP tours
    are cycles, not paths.
    """
    if not selected_nodes:
        return []

    start = selected_nodes[0]
    route = [start]
    current = start

    while True:
        next_node = None
        for j in selected_nodes:
            if current != j and solver.Value(edges[current, j]) == 1:
                next_node = j
                break

        if next_node is None:
            raise RuntimeError(f"Could not reconstruct route from node {current}.")

        if next_node == start:
            break

        route.append(next_node)
        current = next_node

    return route


def solve_gtsp(filename="4ulysses16", instance_type="symmetric", time_limit_seconds=None):
    """
    Solve standard equality-GTSP with CP-SAT.

    Interpretation:
    - choose exactly one node from each cluster
    - build one cycle through the chosen nodes
    - no fixed depot / no fixed start node

    This matches the usual GTSPLIB/GLKH interpretation.
    """
    model = cp_model.CpModel()

    node_coords, clusters = manualProblem(filename, instance_type)
    all_nodes = list(node_coords.keys())
    dist_matrix = getDistMatrix(node_coords, all_nodes)

    # nodes_present[i] = 1 iff node i is selected as the representative of its cluster.
    nodes_present = {
        i: model.NewBoolVar(f"node_{i}")
        for i in all_nodes
    }

    # edges[i, j] = 1 iff the GTSP cycle travels directly from selected node i to selected node j.
    edges = {}
    arcs = []

    for i in all_nodes:
        for j in all_nodes:
            if i == j:
                continue
            edge_var = model.NewBoolVar(f"edge_{i}_{j}")
            edges[i, j] = edge_var
            arcs.append([i, j, edge_var])

    # AddCircuit needs every node to have exactly one incoming and outgoing arc.
    # For nodes that are NOT selected, we use a self-loop i -> i.
    # For selected nodes, the self-loop is false, so they must be part of the real cycle.
    for i in all_nodes:
        arcs.append([i, i, nodes_present[i].Not()])

    # One single cycle over all selected nodes. Non-selected nodes take self-loops.
    model.AddCircuit(arcs)

    # Equality-GTSP: exactly one node from every cluster is selected.
    for c_id, members in clusters.items():
        model.Add(sum(nodes_present[m] for m in members) == 1)

    # Minimize cyclic travel cost over selected representatives.
    total_distance = sum(edges[i, j] * dist_matrix[i, j] for (i, j) in edges)
    model.Minimize(total_distance)

    solver = cp_model.CpSolver()

    if time_limit_seconds is not None:
        solver.parameters.max_time_in_seconds = time_limit_seconds

    status = solver.Solve(model)
    status_name = solver.StatusName(status)

    print("Status:", status_name)

    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        print("No feasible solution found.")
        return None

    selected_nodes = [i for i in all_nodes if solver.Value(nodes_present[i]) == 1]
    route = reconstruct_cycle_from_edges(selected_nodes, edges, solver)

    objective_scaled = int(solver.ObjectiveValue())
    objective = objective_scaled 

    print(f"Total Distance: {objective}")
    print("GTSP Route, 0-based:", route)
    print("GTSP Route, 1-based:", [node + 1 for node in route])
    print("Selected nodes:", selected_nodes)
    print("Number of selected nodes:", len(selected_nodes))
    print("Number of clusters:", len(clusters))

    if status == cp_model.OPTIMAL:
        print("This solution is proven optimal.")
    else:
        bound = solver.BestObjectiveBound() 
        gap = (objective - bound) / max(1.0, abs(objective))
        print("Feasible solution found, but not proven optimal.")
        print(f"Best bound: {bound}")
        print(f"Relative gap: {gap}")

    return {
        "status": status_name,
        "objective_scaled": objective_scaled,
        "objective": objective,
        "route_0_based": route,
        "route_1_based": [node + 1 for node in route],
        "selected_nodes": selected_nodes,
        "dist_matrix": dist_matrix,
        "clusters": clusters,
        "node_coords": node_coords,
    }


def getManualRouteDistance(route, dist_matrix):
    """Keep your old helper name, but fix the cycle logic and the `is` bug."""
    total_dist = route_distance(route, dist_matrix)
    print("Manual route distance:")
    print(total_dist )
    print(route)
    return total_dist


if __name__ == "__main__":
    result = None
    result = solve_gtsp("M11berlin52", "manual")

    if result is not None:
        dist_matrix = result["dist_matrix"]
    coords,clusters = manualProblem("M11berlin52", "manual")
    dist_matrix = getDistMatrix(coords,list(coords.keys()))

        # GLKH output for your example was 1-based: [6, 14, 16, 11]
        # Therefore in your Python 0-based indexing it is:
    glkh_route_0_based = [42, 21, 31, 18, 22, 45, 19, 33, 51, 12, 13, 47]
    getManualRouteDistance(glkh_route_0_based, dist_matrix)


import math
from symCords import read_gtsp_problem,manualProblem

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

def getManualRouteDistance(route, dist_matrix):
    """Keep your old helper name, but fix the cycle logic and the `is` bug."""
    total_dist = route_distance(route, dist_matrix)
    print("Manual route distance:")
    print(total_dist )
    print(route)
    return total_dist




def compare1(route1,route2,problem,type):
    coords,clusters = manualProblem(problem,type)
    distmatrix = getDistMatrix(coords,coords.keys())
    print(distmatrix)
    for i in range(len(route1)):
        route1[i] -=1
    for i in range(len(route2)):
        route2[i] -=1

    dist1 = getManualRouteDistance(route1,distmatrix) 
    dist2 = getManualRouteDistance(route2,distmatrix) 
    print(f"Distance LKH/OR: {dist1}")
    print(f"Distance Api: {dist2}")
    print(f"Difference: {dist2-dist1}")

compare1([
    2, 5, 6, 7, 43, 44, 13, 48, 49, 50,
    84, 85, 21, 56, 57, 26, 27, 30, 31, 65,
    379, 125, 135, 134, 124, 123, 132, 145, 169, 182,
    198, 209, 226, 414, 416, 420, 275, 336, 373, 432,
    333, 332, 345, 431, 326, 300, 429, 344, 360, 435,
    296, 278, 255, 258, 259, 408, 225, 215, 203, 178,
    155, 142, 129, 118, 117, 128, 138, 175, 212, 200,
    213, 231, 248, 247, 425, 290, 316, 315, 352, 351,
    433, 348, 428, 282, 426, 241, 240, 239, 234, 406,
    401, 186, 173, 161, 149, 441, 102, 66, 442
],[373, 442, 348, 92, 397, 299, 226, 405, 74, 205, 108, 387, 425, 268, 125, 169, 365, 355, 253, 179, 273, 68, 174, 117, 243, 31, 16, 53, 138, 222, 285, 131, 185, 432, 206, 203, 325, 294, 165, 289, 259, 124, 414, 171, 435, 344, 336, 212, 73, 145, 170, 240, 305, 258, 413, 52, 390, 278, 428, 349, 152, 192, 175, 101, 107, 123, 140, 159, 209, 407, 244, 239, 359, 248, 67, 75, 88, 215, 231, 311, 401, 114, 126, 307, 275, 431, 97, 85, 82, 95, 324, 398, 300, 291, 25, 7, 2, 12, 20],"99pcb442_added10","manual")





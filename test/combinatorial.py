
import math
import pandas as pd
from pyCombinatorial.algorithm import nearest_neighbour,cheapest_insertion,genetic_algorithm,farthest_insertion,local_search_2_opt,local_search_3_opt
from pyCombinatorial.utils import util,graphs
from adapt import tspCombinatorialCsv




algoIndex = {
    "NN": (nearest_neighbour, {"local_search": False, "verbose": False}),
    "CI": (cheapest_insertion, {"local_search": False, "verbose": False}),
    "FI": (farthest_insertion, {"local_search": False, "verbose": False}),
    "NN2opt": (nearest_neighbour, {"local_search": True, "verbose": False}),
    "CI2opt": (cheapest_insertion, {"local_search": True, "verbose": False}),
    "FI2opt": (farthest_insertion, {"local_search": True, "verbose": False}),
}

def runTspHeuristic(filepath, exclude=None):
    if exclude is None:
        exclude = ["GA"]

    coords = pd.read_csv(filepath).values.astype(float)
    distance_matrix = util.build_distance_matrix(coords)

    results = {}
    parameters = {
            'recursive_seeding': -1, # Total Number of Iterations. If This Value is Negative Then the Algorithm Only Stops When Convergence is Reached
            'verbose': True
             }

    for name, (func, params) in algoIndex.items():

        if name in exclude:
            continue

        route, distance = func(distance_matrix, **params)

        route = [int(x) for x in route]
        distance = float(distance)

        results[name] = {
            "route": route,
            "distance": distance
        }
        print(f"done: {name} for {filepath}")

    return results

def storeResults(results,filepath,instancePath):
    print(results)
    content = ""
    for name in algoIndex:
        content += f"Heuristic: {name}\n"
        content += f"Distance: {results[name]['distance']}\n"
        content += f"Route: {results[name]['route']}\n"
        content += "\n"
    
    with open(filepath, "w") as f:
        f.write(content)
        
        


def printRes(results):
    for i,data in results.items():
        print(i)
        print(data["route"])
        print(data["distance"])

       



if __name__ == "__main__":
    filepath = "instances/g/tspCsvtest.csv"
    results = runTspHeuristic(filepath)
    storeResults(results,"TSPRESULTS/a.txt",filepath)



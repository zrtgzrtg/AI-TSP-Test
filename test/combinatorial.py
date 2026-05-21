
import pandas as pd
from pyCombinatorial.algorithm import nearest_neighbour,cheapest_insertion,genetic_algorithm
from pyCombinatorial.utils import util,graphs
from randomInst import randomTSPInstance
from general import getDistMatrix

def tspCombinatorial(name):
    instance = randomTSPInstance(30)
    data = {
        "x": [],
        "y": []
    }
    for index, tup in instance.items():
        data["x"].append(tup[0])
        data["y"].append(tup[1])
    
    print("start")
    df = pd.DataFrame(data)
    filepath = f"instances/g/tspCsv{name}.csv"
    df.to_csv(filepath, index=False)
    return filepath

algoIndex = {
    "NN":(nearest_neighbour,{}),
    "CI":(cheapest_insertion,{}),
    "GA":(genetic_algorithm,{
            "population_size": 15,
            "elite": 1,
            "mutation_rate": 0.1,
            "mutation_search": 8,
            "generations": 1000,
            "verbose": False,
            })
}
def runTspHeuristic(filepath):
    coords = pd.read_csv(filepath).values.astype(float)
    distance_matrix = util.build_distance_matrix(coords)
    results = {}
    for i,(func,params) in algoIndex.items():
        route, distance = func(distance_matrix, **params)
        results[i] = {
            "route": route,
            "distance": distance
        }
    return results
        



if __name__ == "__main__":
    filepath = tspCombinatorial("test")
    print(runTspHeuristic(filepath))



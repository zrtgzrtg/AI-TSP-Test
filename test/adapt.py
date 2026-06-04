
from pathlib import Path
import os
import json
import numpy as np
import math
import pandas as pd
from randomInst import randomTSPInstance

import math
import numpy as np


def read_xy_coords(filepath: str) -> dict[int, tuple[float, float]]:
    """
    Read x,y coordinates from a CSV-like file and return a 1-based dictionary.

    Example return:
        {
            1: (85.0, 1.0),
            2: (30.0, 72.0),
            3: (92.0, 25.0),
            ...
        }
    """
    coords = {}

    with open(filepath, "r", encoding="utf-8") as file:
        node_id = 1

        for line_number, line in enumerate(file, start=1):
            line = line.strip()

            if not line:
                continue

            if line_number == 1 and line.lower() == "x,y":
                continue

            x_str, y_str = line.split(",")

            x = float(x_str)
            y = float(y_str)

            coords[node_id] = (x, y)
            node_id += 1

    return coords


def euc_2d_distance(a, b) -> int:
    """
    TSPLIB EUC_2D distance:
    nearest integer Euclidean distance.
    """
    dx = a[0] - b[0]
    dy = a[1] - b[1]

    return int(math.sqrt(dx * dx + dy * dy) + 0.5)


def build_distance_matrix(coords: dict[int, tuple[float, float]]) -> np.ndarray:
    """
    Build a 1-based symmetric TSPLIB EUC_2D integer distance matrix.

    Index 0 is unused.

    Example:
        D[1, 2] gives the distance between node 1 and node 2.
    """
    n = len(coords)

    # +1 because index 0 is unused
    D = np.zeros((n + 1, n + 1), dtype=int)

    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            d = euc_2d_distance(coords[i], coords[j])
            D[i, j] = d
            D[j, i] = d

    return D


def route_length(cycle: list[int], D: np.ndarray) -> int:
    """
    Calculate the length of a TSP cycle using 1-based node indices.

    Example:
        cycle = [1, 2, 3, 4]

    This automatically includes the return edge from the last node
    back to the first node.
    """
    total = 0

    for k in range(len(cycle)):
        current_node = cycle[k]
        next_node = cycle[(k + 1) % len(cycle)]
        total += D[current_node, next_node]

    return total

def tspCombinatorialCsv(name,instance):
    data = {
        "x": [],
        "y": []
    }
    for index, tup in instance.items():
        data["x"].append(tup[0])
        data["y"].append(tup[1])
    
    print("start")
    df = pd.DataFrame(data)
    filepath = f"instances/g/{name}.csv"
    df.to_csv(filepath, index=False)
    return filepath

def tspCombinatorialTsplib(name,instance):

    filepath = f"instances/g/{name}.tsp"

    with open(filepath, "w") as f:
        f.write(f"NAME : tsp{name}\n")
        f.write("TYPE : TSP\n")
        f.write(f"DIMENSION : {len(instance)}\n")
        f.write("EDGE_WEIGHT_TYPE : EUC_2D\n")
        f.write("\n")
        f.write("NODE_COORD_SECTION\n")

        for node_id, tup in enumerate(instance.values(), start=1):
            x = tup[0]
            y = tup[1]
            f.write(f"{node_id} {x} {y}\n")
        f.write("EOF\n")

    return filepath

def genCombandLKH(size,name):
    instance = randomTSPInstance(size)
    filepathCsv = tspCombinatorialCsv(name,instance)
    filepathTsplib = tspCombinatorialTsplib(name,instance)
    return filepathCsv,filepathTsplib

def readInstancesCombandLKH(name):
    instdir = "instances/g/"
    return  f"{instdir}{name}.csv",f"{instdir}{name}.tsp"


def transformDistances(results,filepathProblem,resultStructure=True):
    coords = read_xy_coords(filepathProblem)
    dm = build_distance_matrix(coords)
    if resultStructure:
        for name in results:
            results[name]["distance"] = route_length(results[name]["route"],dm)
            print(results[name]["distance"])
            print("test")
        return results
    else:
        return route_length(results,dm)



def addAIresults(aiResultPath,heurDir):
    aiRes = {}
    with open(aiResultPath, "r") as f:
        aiRes = json.load(f)
    for resFile in os.listdir(heurDir):
        resF = Path(resFile).stem
        
    


if __name__ == "__main__":
    f1,f2 = genCombandLKH(30,"test")
    print(f1)
    print(f2)

from readResultsFunc import summarize_ai_improvement_all,print_ai_improvement_summary
import json
import re
import ast
import os
from pathlib import Path

def transferJson(resDir,problem,makeJson=False):
    resDict = {}
    dirpath = f"{resDir}{problem}"
    for file in os.listdir(dirpath):
        filepath = f"{dirpath}/{file}"
        tx = ""
        with open(filepath) as f:
            tx = f.read()
            res = parse_heuristics(tx)
            resDict[file] = res
    if makeJson:
        with open(f"resultJson/{problem}.json","w") as f2:
            json.dump(resDict,f2,indent=4)
    else:
        return resDict

def parse_heuristics(text: str) -> dict:
    pattern = re.compile(
        r"Heuristic:\s*(?P<heuristic>\S+)\s*"
        r"Distance:\s*(?P<distance>[^\n]+)\s*"
        r"Route:\s*(?P<route>(?:\[[^\]]*\])|failed)",
        re.MULTILINE
    )

    result = {}

    for match in pattern.finditer(text):
        heuristic = match.group("heuristic")
        distance_raw = match.group("distance").strip()
        route_raw = match.group("route").strip()

        if distance_raw.lower() == "failed" and route_raw.lower() == "failed":
            distance = "failed"
            route = "failed"
        else:
            distance = float(distance_raw) if "." in distance_raw else int(distance_raw)
            route = ast.literal_eval(route_raw)

        result[heuristic] = {
            "distance": distance,
            "route": route
        }

    return result        


if __name__ == "__main__":
    res = "TSPRESULTS/"
    problem = "size85"
    results = transferJson(res,problem)
    print(results)
    results2 = summarize_ai_improvement_all(results,"AI",25)
    with open("FinalResults/results85.txt", "w") as f:
        print_ai_improvement_summary(results2,file=f)

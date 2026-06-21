
import json
from pathlib import Path
import os
from adapt import transformDistances

def addAIresults(aiResultPath,heurDir,size):
    aiRes = {}
    with open(aiResultPath, "r") as f:
        aiRes = json.load(f)
    for resFile in os.listdir(heurDir):
        resF = Path(resFile).stem
        distanceOrg = aiRes[resF]["distance"]
        print(distanceOrg)
        content = ""
        if distanceOrg == "-1":
            print("check hit")
            content += f"Heuristic: {name}\n"
            content += f"Distance: failed\n"
            content += f"Route: failed\n"
            content += "\n"
        else:
            route = aiRes[resF]["route"]
            check_route(route, resF)
            route = fixRoute(route,size)
            name = "AI"
            distance = transformDistances(route,f"instances/g/{resF}.csv",False)
            content += f"Heuristic: {name}\n"
            content += f"Distance: {distance}\n"
            content += f"Route: {aiRes[resF]['route']}\n"
            content += "\n"
        with open(f"{heurDir}/{resFile}", "a") as f2:
            f2.write(content)

def fixRoute(route,size):
    if min(route) == 0:
        for i in range(len(route)):
            route[i] += 1
    if len(route) is not size+1:
        start = route[0]
        route.append(start)
    return route
        
    

def check_route(route, instance_name):
    print("INSTANCE:", instance_name)
    print("route length:", len(route))
    print("min node:", min(route))
    print("max node:", max(route))
    print("unique nodes:", len(set(route)))
    print("duplicates:", len(route) - len(set(route)))
    print("first:", route[0])
    print("last:", route[-1])
    print()

if __name__ == "__main__":
    resDir = "TSPRESULTS"
    addAIresults(f"{resDir}/size20.json",f"{resDir}/size20/",20)


import json
from pathlib import Path
import os
from adapt import transformDistances
def printaddAIresults(aiResultPath,heurDir,size,checkFile):
    aiRes = {}
    with open(aiResultPath, "r") as f:
        aiRes = json.load(f)
    for resFile in os.listdir(heurDir):
        print(resFile)
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
            route,err = fixRoute(route,size)
            name = "AI"
            content += f"Heuristic: {name}\n"
            if err != None:
                content += f"Distance: routeError\n"
                content += f"Route: routeError\n"
            else:
                distance = transformDistances(route,f"instances/g/{resF}.csv",False)
                content += f"Distance: {distance}\n"
                content += f"Route: {aiRes[resF]['route']}\n"
        if resFile == checkFile:
            break
            content += "\n"

def fixRoute(route,size):
    if min(route) == 0:
        for i in range(len(route)):
            route[i] += 1
    if len(route) != size+1:
        start = route[0]
        route.append(start)
    if max(route) > size:
        return [],-1
    if min(route) < 1:
        return [], -1
    
    if route[0] != route[-1]:
        return [],-1
    inner_route = route[:-1]
    for i in range(1,size+1):
        if i not in inner_route:
            return [], -1
    if len(set(inner_route)) != size:
        return [],-1
    return route,None
        
    

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
    for i in range(15,61,5):
        size = i
        checkFile = "size35_5.txt"
        printaddAIresults(f"{resDir}/size{size}.json",f"{resDir}/size{size}/",size,checkFile)

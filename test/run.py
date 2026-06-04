
import json
from dpCall import callWrapper
import os
from helplkh import createParFileTsp
from adapt import genCombandLKH,readInstancesCombandLKH
from combinatorial import runTspHeuristic,storeResults
from adapt import transformDistances
import subprocess
from pathlib import Path

def parse_lkh_tour(tour_file):
    tour_file = Path(tour_file)

    distance = None
    route = []
    in_tour_section = False

    with tour_file.open("r") as f:
        for line in f:
            line = line.strip()

            if line.startswith("COMMENT") and "Length" in line:
                # Example: COMMENT : Length = 512
                distance = float(line.split("=")[1].strip())

            elif line == "TOUR_SECTION":
                in_tour_section = True

            elif in_tour_section:
                if line in {"-1", "EOF"}:
                    break
                route.append(int(line))

    # Close the route
    if route and route[0] != route[-1]:
        route.append(route[0])

    results = {}
    results["LKH"] ={
        "distance": distance,
        "route": route
    }
    return results
def storeResultsLKH(results,filepath,instancePath):
    content = ""
    name = "LKH"
    content += f"Heuristic: {name}\n"
    content += f"Distance: {results[name]['distance']}\n"
    content += f"Route: {results[name]['route']}\n"
    content += "\n"
    
    with open(filepath, "a") as f:
        f.write(content)
def addAIresults(aiResultPath,heurDir):
    aiRes = {}
    with open(aiResultPath, "r") as f:
        aiRes = json.load(f)
    for resFile in os.listdir(heurDir):
        resF = Path(resFile).stem
        with open(f"{heurDir}/{resFile}", "a") as f2:
            continue



    
def storeFullResults(resultsComb,resultsLKH,filepath,instancePathComb,instancePathLKH):
    storeResults(resultsComb,filepath,instancePathComb)
    storeResultsLKH(resultsLKH,filepath,instancePathLKH)
 

def run(name,projectName,size,randomRun=True):
    if randomRun:
        fcsv,ftsp = genCombandLKH(size,name)
    else:
        fcsv,ftsp = readInstancesCombandLKH(name)
    resultsComb = runTspHeuristic(fcsv)

    filepathLKHTour = createParFileTsp(name)
    lkhdir = "LKH-3.0.14/"
    result = subprocess.run([f"{lkhdir}LKH", filepathLKHTour],
                            capture_output=True,
                            text=True)
    
    os.makedirs(f"TSPRESULTS/{projectName}",exist_ok=True)
    resultsLKH = parse_lkh_tour(f"{lkhdir}tmp/{name}.tour")
    resultsComb = transformDistances(resultsComb,fcsv)
    resultsLKH = transformDistances(resultsLKH,fcsv)
    storeFullResults(resultsComb,resultsLKH,f"TSPRESULTS/{projectName}/{name}.txt",fcsv,ftsp)
    if randomRun:  
        callWrapper(fcsv,projectName)
    
    print(result.stdout)
    print(result.stderr)

if __name__ == "__main__":
    for i in range(30):
        run(f"size15_{i}","size15",15)
        print(f"done: {i}")

    

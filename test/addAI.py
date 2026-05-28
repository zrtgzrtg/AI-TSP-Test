
import json
from pathlib import Path
import os

def addAIresults(aiResultPath,heurDir):
    aiRes = {}
    with open(aiResultPath, "r") as f:
        aiRes = json.load(f)
    for resFile in os.listdir(heurDir):
        resF = Path(resFile).stem
        content = ""
        name = "AI"
        content += f"Instance File: {resFile}\n"
        content += f"Heuristic: {name}\n"
        content += f"Distance: {aiRes[resF]['distance']}\n"
        content += f"Route: {aiRes[resF]['route']}\n"
        content += "\n"
        with open(f"{heurDir}/{resFile}", "a") as f2:
            f2.write(content)

if __name__ == "__main__":
    resDir = "TSPRESULTS"
    addAIresults(f"{resDir}/size30.json",f"{resDir}/size30/")


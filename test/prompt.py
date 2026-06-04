
from pathlib import Path
import os
import json
def genPromptFromText(pathSystem,pathUserDir,outputPath):
    collection = []
    systemPart = retPartPrompt(pathSystem,"system")
    collection.append(systemPart)
    for path in os.listdir(pathUserDir):
        collection.append(retPartPrompt(f"{pathUserDir}/{path}","user"))
    with open(outputPath,"w") as f:
        json.dump(collection,f,indent=4)


    

def retPartPrompt(path,role):
    with open(path,"r") as f:
        txt = f.read()
    return {
        "role": role,
        "content": txt
    }
def addProblemFile(filepath,pathUserDir):
    problem = ""
    with open(filepath, "r") as f:
        problem = f.read()
    with open(f"{pathUserDir}/tsp.txt", "w") as f2:
        f2.write(f"here is the tsp file to solve {Path(filepath).stem}:\n")
        f2.write(problem)

def genFullPrompt(OutputPath,filepath,pathSystem="prompts/text/system.txt",pathUserDir="prompts/text/userInput"):
    addProblemFile(filepath,pathUserDir)
    genPromptFromText(pathSystem,pathUserDir,OutputPath)
    return OutputPath



if __name__ == "__main__":
    genFullPrompt("prompts/text/output/test.json","instances/g/size15_0.csv","prompts/text/system.txt","prompts/text/userInput")


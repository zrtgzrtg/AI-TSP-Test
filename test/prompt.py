
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



genPromptFromText("prompts/text/system.txt","prompts/text/userInput","prompts/text/output/test.json")

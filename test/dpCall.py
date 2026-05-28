from openai import OpenAI
from pathlib import Path
from prompt import genFullPrompt
import subprocess
from dotenv import load_dotenv
import json
import os


def makeCall(filepath):
    load_dotenv()

    client = OpenAI(
        api_key=os.getenv("DEEPSEEK_API_KEY"),
        base_url="https://api.deepseek.com"
    )

    with open(filepath,"r") as f:
        messages = json.load(f)

    response = client.chat.completions.create(
        model="deepseek-reasoner",
        messages=messages,
        reasoning_effort="high"
    )
    return response.choices[0].message.content

def writeOutput(response,name):
    lines = response.splitlines()

    # remove first and last line
    cleaned = "\n".join(lines[1:-1])
    with open(f"outputs/{name}.py","w") as f:
        f.write(cleaned)

def callWrapper(filepath,projectName):
    outputPath = genFullPrompt(f"prompts/text/output/{projectName}.json",filepath)
    response = makeCall(outputPath)
    writeOutput(response,Path(filepath).stem)



if __name__ == "__main__":
    response = makeCall("prompts/text/output/test.json")
    writeOutput(response,"test")

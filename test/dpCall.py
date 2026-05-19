from openai import OpenAI
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
    with open(f"outputs/{name}.py","w") as f:
        f.write(response)


def callDocker():
    subprocess.run(
    [
        "docker", "run", "--rm",
        "--network", "none",
        "--memory", "512m",
        "--cpus", "1",
        "--pids-limit", "128",
        "--read-only",
        "--tmpfs", "/tmp:rw,size=64m",
        "python-runner",
    ],
    capture_output=True,
    text=True,
    timeout=15,
    )

response = makeCall("prompts/text/output/test.json")
writeOutput(response,"test")

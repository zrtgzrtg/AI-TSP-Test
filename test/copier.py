
from pathlib import Path
import shutil
import os

def copyRes(name):
    dir = "outputs/"
    count = 0
    pathList = []
    for path in os.listdir(dir):
        if name in Path(path).stem:
            pathList.append(f"{path}")
            count += 1

    print(count)
    copyDir = "../airun/aiInputNotUsed/"
    os.makedirs(f"{copyDir}{name}",exist_ok=True)
    for x in pathList:
        shutil.copy(f"{dir}{x}",f"{copyDir}{name}/{x}")
    



if __name__ == "__main__":
    size = 80
    copyRes(f"size{size}")


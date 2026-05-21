
from outputs.test import solve
from compare import compare1
from symCords import manualProblem,returnFilePath
from pathlib import Path
import subprocess
import shutil

def runGLKH(filename,type):
    glkhPath = Path("GLKH-1.1")
    filepath = returnFilePath(filename,type)
    shutil.copy(filepath,f"{glkhPath}/GTSPLIB/{filename}.gtsp")
    result = subprocess.run(["bash","runGLKH", f"{filename}"],
                            cwd = glkhPath,
                            capture_output=True,
                            text=True)

    
    print(result.stdout)
    print(result.stderr)
    print(result.returncode)
    tour = extractTour(f"glkhTours/{filename}.tour")
    return tour

def extractTour(tour_file,zero_based=False):
    tour = []
    in_tour_section = False

    with open(tour_file, "r") as f:
        for line in f:
            line = line.strip()

            if not line:
                continue

            if line.startswith("TOUR_SECTION"):
                in_tour_section = True
                continue

            if in_tour_section:
                if line == "-1" or line == "EOF":
                    break

                node = int(line)

                if zero_based:
                    node -= 1

                tour.append(node)

    return tour

if __name__ == "__main__":
    filename = "M12berlin52"
    tourAI = solve(f"instances/m/{filename}.gtsp")
    tourglkh = runGLKH(filename,"manual")
    compare1(tourglkh,tourAI["route"],filename,"manual","plots")


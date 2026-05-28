
def createParFileTsp(name):
    dir = "LKH-3.0.14/"
    problemDir = "instances/g/"
    filename = f"{problemDir}{name}"
    with open(f"{dir}tmp/{name}.par","w") as f:
        f.write(f"PROBLEM_FILE = {filename}.tsp\n")
        f.write(f"OUTPUT_TOUR_FILE = {dir}tmp/{name}.tour\n")
    return f"{dir}tmp/{name}.par"





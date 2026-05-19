import tsplib95
path = "instances/"

def manualProblem(filename, type):
    # The raw data from your 3burma14 example
    gtsp_raw_string = """
    NODE_COORD_SECTION
    1  16.47       96.10
    2  16.47       94.44
    3  20.09       92.54
    4  22.39       93.37
    5  25.23       97.24
    6  22.00       96.05
    7  20.47       97.02
    8  17.20       96.29
    9  16.30       97.38
    10  14.05       98.12
    11  16.53       97.38
    12  21.52       95.59
    13  19.41       97.13
    14  20.09       94.55
    GTSP_SET_SECTION
    1 5 -1
    2 1 8 9 10 11 -1
    3 2 3 4 6 7 -1
    4 12 13 14 -1
    """
    problemType = path
    if type == "symmetric":
        problemType = f"{problemType}s/"
    elif type == "asymmetric":
        problemType = f"{problemType}a/"
    elif type == "manual":
        problemType = f"{problemType}m/"
    else:
        return ValueError("choose appropriate type!")
    filepath = f"{problemType}{filename}.gtsp"
    
    content = ""
    with open(filepath, "r") as f:
        content = f.read()

    # Manual extraction for your test case
    coords = {}
    clusters = {}
    current_section = None

    for line in content.strip().split('\n'):
        line = line.strip()
        if "EOF" in line:
            break
        if "NODE_COORD_SECTION" in line:
            current_section = "coords"
            continue
        if "GTSP_SET_SECTION" in line:
            current_section = "sets"
            continue
    
        parts = line.split()
        if current_section == "coords":
            # Convert to 0-based: Node 1 becomes 0, Node 2 becomes 1, etc.
            node_id = int(parts[0]) - 1
            coords[node_id] = (float(parts[1]), float(parts[2]))
        
        elif current_section == "sets":
            # Convert to 0-based: Cluster 1 nodes [5] become [4]
            cluster_id = int(parts[0])
            # Skip the cluster_id (parts[0]) and the -1 (last element)
            node_list = [int(x) - 1 for x in parts[1:-1]]
            clusters[cluster_id] = node_list

    # Resulting Dictionaries
    print(f"coords = {coords}")
    print(f"clusters = {clusters}")
    
    return coords,clusters



def read_gtsp_problem(filename, type):
    path = "instances/"
    """
    Reads a GTSP file and returns:
        distance_matrix, coords, clusters

    - distance_matrix: list[list[float]]
    - coords: dict[int, tuple[float, float]]
    - clusters: dict[int, list[int]]

    Node ids are converted to 0-based indexing.
    Cluster ids are kept as they are in the file.
    """

    if type == "symmetric":
        folder = f"{path}s/"
    elif type == "asymmetric":
        folder = f"{path}a/"
    elif type == "manual":
        folder = f"{path}m/"
    else:
        raise ValueError("choose appropriate type: symmetric, asymmetric, or manual")

    filepath = f"{folder}{filename}.gtsp"

    with open(filepath, "r") as f:
        lines = f.readlines()

    coords = {}
    clusters = {}
    distance_matrix = []

    dimension = None
    current_section = None

    for line in lines:
        line = line.strip()

        if not line:
            continue

        if line == "EOF":
            break

        # Header values
        if line.startswith("DIMENSION"):
            # Handles both "DIMENSION: 42" and "DIMENSION = 42"
            parts = line.replace(":", " ").replace("=", " ").split()
            dimension = int(parts[-1])
            continue

        # Section starts
        if line.startswith("NODE_COORD_SECTION"):
            current_section = "coords"
            continue

        if line.startswith("EDGE_WEIGHT_SECTION"):
            current_section = "matrix"
            continue

        if line.startswith("GTSP_SET_SECTION"):
            current_section = "clusters"
            continue

        parts = line.split()

        # Coordinates section
        if current_section == "coords":
            node_id = int(parts[0]) - 1
            x = float(parts[1])
            y = float(parts[2])
            coords[node_id] = (x, y)

        # Full distance matrix section
        elif current_section == "matrix":
            row = [float(x) for x in parts]
            distance_matrix.append(row)

            # Stop reading matrix once we have DIMENSION rows
            if dimension is not None and len(distance_matrix) == dimension:
                current_section = None

        # Cluster section
        elif current_section == "clusters":
            cluster_id = int(parts[0])

            # Everything after cluster_id until -1 are node ids
            node_list = []
            for x in parts[1:]:
                if x == "-1":
                    break
                node_list.append(int(x) - 1)

            clusters[cluster_id] = node_list

    return distance_matrix, coords, clusters
    

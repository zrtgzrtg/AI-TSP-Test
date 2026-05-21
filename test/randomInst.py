
from plot import plot_points
import random
from general import getDistMatrix

def randomTSPInstance(n, x_min=0, x_max=100, y_min=0, y_max=100, seed=None):
    if seed is not None:
        random.seed(seed)

    coords = {}

    for node in range(n):
        x = random.randint(x_min, x_max)
        y = random.randint(y_min, y_max)
        coords[node] = (x, y)

    return coords

if __name__ == "__main__":
    coords = randomTSPInstance(100)
    print(getDistMatrix(coords,coords.keys()))
    plot_points(coords,"plots","random")

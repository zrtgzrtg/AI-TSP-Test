import matplotlib.pyplot as plt
from pathlib import Path


def plot_tsp_instance(source, save_dir=None, name="tsp_instance", show_labels=False):
    """
    Plots a TSP instance from either:
    - a file path to a CSV-like text file with format:
          x,y
          10,36
          76,99
          ...
    - or a raw string containing that same content.

    Parameters
    ----------
    source : str or Path
        File path or raw text containing the coordinates.
    save_dir : str or Path or None
        If given, saves the plot there as <name>.png.
    name : str
        File name for saving.
    show_labels : bool
        If True, shows node indices next to points.

    Returns
    -------
    coords : dict
        Dictionary of form {node_id: (x, y)}.
    """

    # Decide whether source is a file path or raw text
    if isinstance(source, (str, Path)) and Path(str(source)).exists():
        with open(source, "r") as f:
            lines = f.read().strip().splitlines()
    else:
        lines = str(source).strip().splitlines()

    # Remove empty lines
    lines = [line.strip() for line in lines if line.strip()]

    # Skip header if present
    if lines[0].lower() == "x,y":
        lines = lines[1:]

    coords = {}

    for idx, line in enumerate(lines):
        x_str, y_str = line.split(",")
        x = float(x_str.strip())
        y = float(y_str.strip())
        coords[idx] = (x, y)

    x_vals = [coords[i][0] for i in coords]
    y_vals = [coords[i][1] for i in coords]

    plt.figure(figsize=(8, 8))
    plt.scatter(x_vals, y_vals)

    if show_labels:
        for i, (x, y) in coords.items():
            plt.text(x, y, str(i), fontsize=8)

    plt.xlabel("x")
    plt.ylabel("y")
    plt.title(name)
    plt.axis("equal")
    plt.grid(True)

    if save_dir is not None:
        save_dir = Path(save_dir)
        save_dir.mkdir(parents=True, exist_ok=True)
        plt.savefig(save_dir / f"{name}.png", dpi=300, bbox_inches="tight")

    plt.show()

    return coords

def plot_tsp_instance_wrapper(size,num):
    dir = "instances/g/size"

    plot_tsp_instance(f"{dir}{size}_{num}.csv",save_dir="zplots",name=f"{size}_{num}",show_labels=False)

if __name__ == "__main__":

    plot_tsp_instance_wrapper(20,0)
import os
import matplotlib.pyplot as plt


def plot_route(
    coords,
    route,
    savedir,
    name,
    problem_type="tsp",
    clusters=None,
    show_node_labels=False,
    show_cluster_labels=True,
    show_all_cluster_nodes=True,
    show_cluster_circles=True,
    node_size=18,
    route_node_size=60,
    route_width=1.5,
):
    """
    Plot either a TSP or GTSP solution.

    Parameters
    ----------
    coords : dict[int, tuple[float, float]]
        Node coordinates, e.g. {0: (x, y), 1: (x, y), ...}

    route : list[int]
        Tour as node ids. The function closes the cycle automatically.

    savedir : str
        Directory where the plot should be saved.

    name : str
        Output filename without .png.

    problem_type : str
        Either "tsp" or "gtsp".

    clusters : dict[int, list[int]] or None
        Required only for GTSP.
        Example: {1: [0, 1], 2: [2, 3, 4]}
    """

    if problem_type not in {"tsp", "gtsp"}:
        raise ValueError("problem_type must be either 'tsp' or 'gtsp'.")

    if problem_type == "gtsp" and clusters is None:
        raise ValueError("clusters must be provided when problem_type='gtsp'.")

    os.makedirs(savedir, exist_ok=True)

    fig, ax = plt.subplots(figsize=(10, 8))

    # Ensure cyclic route
    if route[0] != route[-1]:
        route = route + [route[0]]

    # -------------------------
    # TSP plotting
    # -------------------------
    if problem_type == "tsp":
        xs = [coords[node][0] for node in coords]
        ys = [coords[node][1] for node in coords]

        ax.scatter(
            xs,
            ys,
            s=node_size,
            color="blue",
            alpha=0.45,
            label="Nodes",
            zorder=2,
        )

        route_nodes_without_duplicate_end = route[:-1]

        route_node_x = [coords[node][0] for node in route_nodes_without_duplicate_end]
        route_node_y = [coords[node][1] for node in route_nodes_without_duplicate_end]

        ax.scatter(
            route_node_x,
            route_node_y,
            s=route_node_size,
            color="black",
            alpha=0.9,
            label="Tour nodes",
            zorder=5,
        )

        title = "TSP Route"
        route_label = "TSP tour"

    # -------------------------
    # GTSP plotting
    # -------------------------
    else:
        cluster_ids = sorted(clusters.keys())
        cmap = plt.colormaps.get_cmap("tab20").resampled(len(clusters))

        cluster_to_color_idx = {
            cluster_id: i for i, cluster_id in enumerate(cluster_ids)
        }

        if show_all_cluster_nodes:
            for cluster_id in cluster_ids:
                nodes = clusters[cluster_id]

                xs = [coords[node][0] for node in nodes]
                ys = [coords[node][1] for node in nodes]

                ax.scatter(
                    xs,
                    ys,
                    s=node_size,
                    color=cmap(cluster_to_color_idx[cluster_id]),
                    alpha=0.45,
                    zorder=2,
                )

        route_nodes_without_duplicate_end = route[:-1]

        selected_x = [coords[node][0] for node in route_nodes_without_duplicate_end]
        selected_y = [coords[node][1] for node in route_nodes_without_duplicate_end]

        ax.scatter(
            selected_x,
            selected_y,
            s=route_node_size,
            color="black",
            alpha=0.9,
            label="Selected GTSP nodes",
            zorder=5,
        )

        if show_cluster_labels:
            for cluster_id, nodes in clusters.items():
                xs = [coords[node][0] for node in nodes]
                ys = [coords[node][1] for node in nodes]

                cx = sum(xs) / len(xs)
                cy = sum(ys) / len(ys)

                ax.text(
                    cx,
                    cy,
                    f"C{cluster_id}",
                    fontsize=9,
                    fontweight="bold",
                    ha="center",
                    va="center",
                    zorder=7,
                )

        if show_cluster_circles:
            for cluster_id, nodes in clusters.items():
                xs = [coords[node][0] for node in nodes]
                ys = [coords[node][1] for node in nodes]

                cx = sum(xs) / len(xs)
                cy = sum(ys) / len(ys)

                radius = max(
                    ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5
                    for x, y in zip(xs, ys)
                )

                circle = plt.Circle(
                    (cx, cy),
                    radius * 1.15,
                    fill=False,
                    linewidth=1.0,
                    alpha=0.35,
                    color=cmap(cluster_to_color_idx[cluster_id]),
                    zorder=1,
                )

                ax.add_patch(circle)

        title = "GTSP Route"
        route_label = "GTSP tour"

    # -------------------------
    # Shared route line
    # -------------------------
    route_x = [coords[node][0] for node in route]
    route_y = [coords[node][1] for node in route]

    ax.plot(
        route_x,
        route_y,
        linewidth=route_width,
        color="green",
        alpha=0.9,
        label=route_label,
        zorder=4,
    )

    # Optional node labels for both TSP and GTSP
    if show_node_labels:
        for node, (x, y) in coords.items():
            ax.text(
                x,
                y,
                str(node),
                fontsize=6,
                zorder=6,
            )

    ax.set_title(title)
    ax.set_xlabel("x-coordinate")
    ax.set_ylabel("y-coordinate")
    ax.grid(True, alpha=0.25)
    ax.axis("equal")
    ax.legend()

    filepath = os.path.join(savedir, f"{name}.png")
    plt.savefig(filepath, dpi=300, bbox_inches="tight")
    plt.close()

    return filepath


def plot_points(
    coords,
    savedir,
    name,
    show_node_labels=False,
    node_size=18,
):
    os.makedirs(savedir, exist_ok=True)

    fig, ax = plt.subplots(figsize=(10, 8))

    xs = [coords[node][0] for node in coords]
    ys = [coords[node][1] for node in coords]

    ax.scatter(
        xs,
        ys,
        s=node_size,
        color="blue",
        alpha=0.45,
        label="Nodes",
        zorder=2,
    )

    if show_node_labels:
        for node, (x, y) in coords.items():
            ax.text(
                x,
                y,
                str(node),
                fontsize=6,
                zorder=6,
            )

    ax.set_title("TSP Points")
    ax.set_xlabel("x-coordinate")
    ax.set_ylabel("y-coordinate")
    ax.grid(True, alpha=0.25)
    ax.axis("equal")
    ax.legend()

    filepath = os.path.join(savedir, f"{name}.png")
    plt.savefig(filepath, dpi=300, bbox_inches="tight")
    plt.close()

    return filepath
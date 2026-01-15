from typing import Dict, List

import matplotlib.pyplot as plt


def generate_graph():
    # Data from latest run (approximate)
    results = [
        # BustAPI
        {"framework": "BustAPI", "endpoint": "/", "requests_sec": 24680},
        {"framework": "BustAPI", "endpoint": "/json", "requests_sec": 20964},
        {"framework": "BustAPI", "endpoint": "/user/10", "requests_sec": 14621},
        # Catzilla
        {"framework": "Catzilla", "endpoint": "/", "requests_sec": 9641},
        {"framework": "Catzilla", "endpoint": "/json", "requests_sec": 10046},
        {"framework": "Catzilla", "endpoint": "/user/10", "requests_sec": 10659},
        # Sanic
        {"framework": "Sanic", "endpoint": "/", "requests_sec": 26325},
        {"framework": "Sanic", "endpoint": "/json", "requests_sec": 27858},
        {"framework": "Sanic", "endpoint": "/user/10", "requests_sec": 29871},
        # Flask
        {"framework": "Flask", "endpoint": "/", "requests_sec": 3194},
        {"framework": "Flask", "endpoint": "/json", "requests_sec": 2935},
        {"framework": "Flask", "endpoint": "/user/10", "requests_sec": 2825},
        # FastAPI
        {"framework": "FastAPI", "endpoint": "/", "requests_sec": 6404},
        {"framework": "FastAPI", "endpoint": "/json", "requests_sec": 7969},
        {"framework": "FastAPI", "endpoint": "/user/10", "requests_sec": 6517},
        # Falcon
        {"framework": "Falcon", "endpoint": "/", "requests_sec": 8631},
        {"framework": "Falcon", "endpoint": "/json", "requests_sec": 9092},
        {"framework": "Falcon", "endpoint": "/user/10", "requests_sec": 7159},
        # Bottle
        {"framework": "Bottle", "endpoint": "/", "requests_sec": 7571},
        {"framework": "Bottle", "endpoint": "/json", "requests_sec": 7813},
        {"framework": "Bottle", "endpoint": "/user/10", "requests_sec": 7124},
        # Django
        {"framework": "Django", "endpoint": "/", "requests_sec": 3856},
        {"framework": "Django", "endpoint": "/json", "requests_sec": 2389},
        {"framework": "Django", "endpoint": "/user/10", "requests_sec": 2214},
        # BlackSheep
        {"framework": "BlackSheep", "endpoint": "/", "requests_sec": 0},  # Failed run
        {"framework": "BlackSheep", "endpoint": "/json", "requests_sec": 0},
        {"framework": "BlackSheep", "endpoint": "/user/10", "requests_sec": 0},
    ]

    # Mock Sys Info
    sys_info = {
        "cpu_model": "Intel(R) Core(TM) i5-8365U CPU @ 1.60GHz",
        "cpu_count": 8,
        "ram_total_gb": 15.4,
        "os": "Linux 6.14.0-37-generic",
        "python": "3.13.11",
    }

    endpoints = ["/", "/json", "/user/10"]
    frameworks = sorted({r["framework"] for r in results})

    # Setup Colors
    color_map = {
        "BustAPI": "#009688",  # green
        "Sanic": "#ff007f",  # Bright Pink
        "BlackSheep": "#333333",  # Dark Grey
        "FastAPI": "#009688",  # Teal
        "Falcon": "#607d8b",  # Blue Grey
        "Bottle": "#9e9e9e",  # Grey
        "Flask": "#34495e",  # Midnight Blue
        "Django": "#0c4b33",  # Django Green
        "Catzilla": "#e67e22",  # Orange
    }

    # Create subplots (one for each endpoint)
    fig, axes = plt.subplots(len(endpoints), 1, figsize=(10, 4 * len(endpoints)))
    if len(endpoints) == 1:
        axes = [axes]

    for i, ep in enumerate(endpoints):
        ax = axes[i]

        # Get data for this endpoint, sorted by RPS ascending
        ep_data = [r for r in results if r["endpoint"] == ep]
        ep_data.sort(key=lambda x: x["requests_sec"])

        names = [r["framework"] for r in ep_data]
        values = [r["requests_sec"] for r in ep_data]
        colors = [color_map.get(n, "#999999") for n in names]

        y_pos = range(len(names))

        bars = ax.barh(
            y_pos, values, align="center", color=colors, alpha=0.9, height=0.6
        )
        ax.set_yticks(y_pos)
        ax.set_yticklabels(names, fontsize=10, fontweight="medium")
        # ax.invert_yaxis() # Not needed if sorted ascending -> Highest on Top

        ax.set_xlabel("Requests Per Second (RPS)")
        ax.set_title(f"Endpoint: {ep}", fontsize=12, fontweight="bold", pad=10)
        ax.grid(axis="x", linestyle="--", alpha=0.3)

        # Add values on bars
        for bar in bars:
            width = bar.get_width()
            ax.text(
                width + (max(values) * 0.01),
                bar.get_y() + bar.get_height() / 2,
                f"{int(width):,}",
                ha="left",
                va="center",
                fontsize=9,
                fontweight="bold",
                color="#444",
            )

    plt.tight_layout()

    # Add System Info & Config Note
    # Mock Workers string
    workers_str = "BustAPI:1, Catzilla:1, Flask:4, FastAPI:4, Sanic:4, Falcon:4, Bottle:4, Django:4, BlackSheep:4"
    info_text = (
        f"Device: {sys_info['cpu_model']} | {sys_info['cpu_count']} Cores | {sys_info['ram_total_gb']}GB RAM\n"
        f"OS: {sys_info['os']} | Python: {sys_info['python']}\n"
        f"Workers: {workers_str}"
    )

    # Make room for footer
    plt.subplots_adjust(bottom=0.15)

    fig.text(
        0.5,
        0.02,
        info_text,
        ha="center",
        fontsize=9,
        bbox={
            "facecolor": "white",
            "alpha": 0.9,
            "edgecolor": "#ccc",
            "boxstyle": "round,pad=0.5",
        },
    )

    # Save graph
    output_path = "benchmarks/rps_comparison.png"
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    print(f"✅ Graph saved to {output_path}")


if __name__ == "__main__":
    generate_graph()

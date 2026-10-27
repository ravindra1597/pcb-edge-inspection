from pathlib import Path

import matplotlib.pyplot as plt


OUTPUT_PATH = Path("git_assets/latency_comparison.png")

BACKENDS = [
    "PyTorch GPU\nRaw Inference",
    "TensorRT FP16\nRaw Inference",
    "PyTorch GPU\nFull API",
    "TensorRT FP16\nFull API",
]

LATENCIES_MS = [
    20.60,
    6.65,
    40.20,
    23.69,
]


def main():
    fig, ax = plt.subplots(figsize=(10, 6))

    bars = ax.bar(BACKENDS, LATENCIES_MS)

    ax.set_title(
        "Jetson Orin Nano Inference Performance",
        fontsize=16,
        fontweight="bold",
    )

    ax.set_ylabel("Latency (ms)")
    ax.set_ylim(0, 45)

    ax.grid(
        axis="y",
        linestyle="--",
        alpha=0.3,
    )

    for bar, latency in zip(bars, LATENCIES_MS):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.8,
            f"{latency:.2f} ms",
            ha="center",
            va="bottom",
            fontsize=11,
            fontweight="bold",
        )

    fig.text(
        0.5,
        0.01,
        "TensorRT FP16 reduced raw model latency by ~68% "
        "and warm end-to-end API latency by ~41%.",
        ha="center",
        fontsize=10,
    )

    plt.tight_layout(rect=[0, 0.04, 1, 1])

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    plt.savefig(
        OUTPUT_PATH,
        dpi=180,
        bbox_inches="tight",
    )

    plt.close()

    print(
        f"Saved latency comparison chart to: {OUTPUT_PATH}"
    )


if __name__ == "__main__":
    main()
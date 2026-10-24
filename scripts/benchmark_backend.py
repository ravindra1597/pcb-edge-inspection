from pathlib import Path
from statistics import mean

import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from backend import PCBInspectionBackend


def main():
    backend = PCBInspectionBackend()

    images = list(
        Path("data/pcb_defects/valid/images").glob("*")
    )

    if not images:
        raise FileNotFoundError("No validation images found.")

    test_image = images[0]

    timings = []

    print(f"Benchmark image: {test_image}\n")

    for run_number in range(1, 7):
        result = backend.inspect(test_image)

        latency = result["inference_pipeline_ms"]
        timings.append(latency)

        print(
            f"Run {run_number}: "
            f"{latency:.2f} ms "
            f"| status={result['status']} "
            f"| defects={result['defect_count']}"
        )

    warm_timings = timings[1:]

    print("\n=== LATENCY SUMMARY ===")
    print(f"Cold first run: {timings[0]:.2f} ms")
    print(f"Average warm latency: {mean(warm_timings):.2f} ms")
    print(f"Fastest warm latency: {min(warm_timings):.2f} ms")
    print(f"Slowest warm latency: {max(warm_timings):.2f} ms")


if __name__ == "__main__":
    main()
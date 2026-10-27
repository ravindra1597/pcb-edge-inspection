from pathlib import Path

import cv2
import matplotlib.pyplot as plt
from ultralytics import YOLO


MODEL_PATH = Path(
    "runs/detect/training_runs/yolov8n_pcb_baseline/weights/best.pt"
)

IMAGE_DIR = Path("data/pcb_defects/test/images")

OUTPUT_PATH = Path("git_assets/sample_detections.png")

IMAGES = [
    (
        "Missing Hole",
        IMAGE_DIR
        / "l_light_01_missing_hole_01_2_600_jpg.rf.74207dd03d00e5abe8b04b142a632e84.jpg",
    ),
    (
        "Mouse Bite",
        IMAGE_DIR
        / "l_light_01_mouse_bite_07_3_600_jpg.rf.ec8170e989773bfaf2f2fe886ee9cffb.jpg",
    ),
    (
        "Open Circuit",
        IMAGE_DIR
        / "l_light_01_open_circuit_14_2_600_jpg.rf.bc80119d8c20aba52ac90da53dd40e0d.jpg",
    ),
]


def main():
    model = YOLO(str(MODEL_PATH))

    fig, axes = plt.subplots(1, 3, figsize=(15, 5))

    for ax, (title, image_path) in zip(axes, IMAGES):
        results = model.predict(
            source=str(image_path),
            imgsz=416,
            conf=0.25,
            device="cpu",
            verbose=False,
        )

        plotted = results[0].plot()

        plotted_rgb = cv2.cvtColor(plotted, cv2.COLOR_BGR2RGB)

        ax.imshow(plotted_rgb)
        ax.set_title(title, fontsize=14, fontweight="bold")
        ax.axis("off")

    fig.suptitle(
        "PCB Defect Detection Examples",
        fontsize=18,
        fontweight="bold",
    )

    plt.tight_layout()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    plt.savefig(
        OUTPUT_PATH,
        dpi=180,
        bbox_inches="tight",
    )

    plt.close()

    print(f"Saved detection visualization to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
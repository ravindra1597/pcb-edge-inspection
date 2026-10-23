from ultralytics import YOLO


def main():
    # Start from pretrained YOLOv8 Nano weights
    model = YOLO("yolov8n.pt")

    model.train(
        data="data/pcb_defects/data.yaml",

        # Training configuration
        epochs=30,
        imgsz=416,
        batch=8,

        # Current laptop environment is CPU-only
        device="cpu",
        workers=0,

        # Reproducibility
        seed=42,
        deterministic=True,

        # Save outputs
        project="training_runs",
        name="yolov8n_pcb_baseline",
        exist_ok=True,

        # Validate after each epoch
        val=True,
        plots=True,
    )


if __name__ == "__main__":
    main()
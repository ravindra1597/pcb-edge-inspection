from ultralytics import YOLO


def main():
    model = YOLO(
        # The model that we trained and saved.
        "runs/detect/training_runs/yolov8n_pcb_baseline/weights/best.pt"
    )

    metrics = model.val(
        data="data/pcb_defects/data.yaml",
        split="test",
        imgsz=416,
        batch=8,
        device="cpu",
        workers=0,
        plots=True,
        project="evaluation_runs",
        name="yolov8n_pcb_test",
        exist_ok=True,
    )

    print("\n=== FINAL HELD-OUT TEST RESULTS ===")
    print(f"mAP@0.50:      {metrics.box.map50:.4f}")
    print(f"mAP@0.50:0.95: {metrics.box.map:.4f}")
    print(f"Precision:     {metrics.box.mp:.4f}")
    print(f"Recall:        {metrics.box.mr:.4f}")


if __name__ == "__main__":
    main()
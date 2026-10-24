from pathlib import Path
from ultralytics import YOLO

# import from decision_engine.py
from .decision_engine import make_decision


MODEL_PATH = Path(
    "runs/detect/training_runs/"
    "yolov8n_pcb_baseline/weights/best.pt"
)


class PCBDefectDetector:
    """
    Runs YOLO inference on PCB images and returns
    structured defect detections.
    """

    def __init__(self, model_path=MODEL_PATH, confidence_threshold=0.25):
        self.model_path = Path(model_path)
        self.confidence_threshold = confidence_threshold

        if not self.model_path.exists():
            raise FileNotFoundError(
                f"Model not found: {self.model_path}"
            )

        self.model = YOLO(str(self.model_path))

    def predict(self, image_path):
        image_path = Path(image_path)

        if not image_path.exists():
            raise FileNotFoundError(
                f"Image not found: {image_path}"
            )

        results = self.model.predict(
            source=str(image_path),
            conf=self.confidence_threshold,
            verbose=False,
        )

        result = results[0]

        detections = []

        for box in result.boxes:
            class_id = int(box.cls[0])
            confidence = float(box.conf[0])

            x1, y1, x2, y2 = [
                float(value)
                for value in box.xyxy[0].tolist()
            ]

            detections.append(
                {
                    "class_id": class_id,
                    "class_name": result.names[class_id],
                    "confidence": round(confidence, 4),
                    "bbox": [
                        round(x1, 2),
                        round(y1, 2),
                        round(x2, 2),
                        round(y2, 2),
                    ],
                }
            )

        return {
            "image": str(image_path),
            "image_width": result.orig_shape[1],
            "image_height": result.orig_shape[0],
            "defect_count": len(detections),
            "detections": detections,
        }


if __name__ == "__main__":
    detector = PCBDefectDetector()

    test_images = list(
        Path("data/pcb_defects/valid/images").glob("*")
    )

    if not test_images:
        raise FileNotFoundError("No validation images found.")

    output = detector.predict(test_images[0])

    decision = make_decision(output["detections"])

    output["status"] = decision["status"]
    output["reason"] = decision["reason"]

    print("\n=== PCB INSPECTION RESULT ===")
    print(output)
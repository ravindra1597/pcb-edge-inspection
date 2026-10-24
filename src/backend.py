from pathlib import Path
from time import perf_counter

from .inference import PCBDefectDetector
from .decision_engine import make_decision


class PCBInspectionBackend:
    """
    End-to-end PCB inspection backend.

    Pipeline:
        image
        -> YOLO inference
        -> structured detections
        -> decision engine
        -> structured inspection result
    """

    def __init__(
        self,
        confidence_threshold=0.25,
        fail_threshold=0.60,
        uncertain_threshold=0.40,
    ):
        self.detector = PCBDefectDetector(
            confidence_threshold=confidence_threshold
        )

        self.fail_threshold = fail_threshold
        self.uncertain_threshold = uncertain_threshold

    def inspect(self, image_path):
        start_time = perf_counter()

        detection_result = self.detector.predict(image_path)

        decision = make_decision(
            detection_result["detections"],
            fail_threshold=self.fail_threshold,
            uncertain_threshold=self.uncertain_threshold,
        )

        elapsed_ms = (perf_counter() - start_time) * 1000

        return {
            "image": detection_result["image"],
            "image_width": detection_result["image_width"],
            "image_height": detection_result["image_height"],
            "status": decision["status"],
            "reason": decision["reason"],
            "defect_count": detection_result["defect_count"],
            "detections": detection_result["detections"],
            "inference_pipeline_ms": round(elapsed_ms, 2),
        }


if __name__ == "__main__":
    backend = PCBInspectionBackend()

    test_images = list(
        Path("data/pcb_defects/valid/images").glob("*")
    )

    if not test_images:
        raise FileNotFoundError("No validation images found.")

    result = backend.inspect(test_images[0])

    print("\n=== PCB BACKEND RESULT ===")

    for key, value in result.items():
        print(f"{key}: {value}")
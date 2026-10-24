from pathlib import Path
import sys

# Allow imports from src/
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from decision_engine import make_decision


def test_fail():
    detections = [
        {
            "class_id": 0,
            "class_name": "missing_hole",
            "confidence": 0.82,
            "bbox": [10, 20, 30, 40],
        }
    ]

    result = make_decision(detections)

    assert result["status"] == "FAIL"
    print("FAIL case passed")


def test_uncertain_low_confidence():
    detections = [
        {
            "class_id": 2,
            "class_name": "open_circuit",
            "confidence": 0.50,
            "bbox": [10, 20, 30, 40],
        }
    ]

    result = make_decision(detections)

    assert result["status"] == "UNCERTAIN"
    print("Low-confidence UNCERTAIN case passed")


def test_uncertain_no_detection():
    result = make_decision([])

    assert result["status"] == "UNCERTAIN"
    print("No-detection UNCERTAIN case passed")


if __name__ == "__main__":
    test_fail()
    test_uncertain_low_confidence()
    test_uncertain_no_detection()

    print("\nAll decision-engine tests passed.")
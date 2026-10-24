def make_decision(
    detections,
    fail_threshold=0.60,
    uncertain_threshold=0.40,
):
    """
    Convert PCB defect detections into an inspection decision.

    Current dataset contains only defective PCB images.
    Therefore, absence of a detection cannot yet be treated
    as evidence that a PCB is defect-free.

    Rules:
    - Any defect with confidence >= fail_threshold -> FAIL
    - Only detections between uncertain_threshold and
      fail_threshold -> UNCERTAIN
    - No reliable detections -> UNCERTAIN
    """

    reliable_defects = []
    uncertain_defects = []

    for detection in detections:
        confidence = detection["confidence"]

        if confidence >= fail_threshold:
            reliable_defects.append(detection)

        elif confidence >= uncertain_threshold:
            uncertain_defects.append(detection)

    if reliable_defects:
        defect_names = [
            detection["class_name"]
            for detection in reliable_defects
        ]

        return {
            "status": "FAIL",
            "reason": (
                "Reliable defect detection(s): "
                f"{', '.join(defect_names)}"
            ),
            "reliable_defects": reliable_defects,
            "uncertain_defects": uncertain_defects,
        }

    if uncertain_defects:
        return {
            "status": "UNCERTAIN",
            "reason": (
                "Only low-confidence defect predictions were found. "
                "Manual review recommended."
            ),
            "reliable_defects": [],
            "uncertain_defects": uncertain_defects,
        }

    return {
        "status": "UNCERTAIN",
        "reason": (
            "No defect was detected, but the current model has not "
            "been validated on defect-free PCB images. "
            "Manual review recommended."
        ),
        "reliable_defects": [],
        "uncertain_defects": [],
    }
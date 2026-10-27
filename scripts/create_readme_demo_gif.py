from pathlib import Path

import cv2
from PIL import Image
from ultralytics import YOLO


MODEL_PATH = Path(
    "runs/detect/training_runs/yolov8n_pcb_baseline/weights/best.pt"
)

IMAGE_DIR = Path("data/pcb_defects/test/images")
OUTPUT_PATH = Path("git_assets/pcb_detection_demo.gif")

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


def add_banner(image, title, subtitle):
    canvas = cv2.copyMakeBorder(
        image,
        85,
        0,
        0,
        0,
        cv2.BORDER_CONSTANT,
        value=(245, 245, 245),
    )

    cv2.putText(
        canvas,
        title,
        (22, 34),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.85,
        (25, 25, 25),
        2,
        cv2.LINE_AA,
    )

    cv2.putText(
        canvas,
        subtitle,
        (22, 67),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        (70, 70, 70),
        1,
        cv2.LINE_AA,
    )

    return canvas


def prepare_frame(image):
    target_width = 720

    height, width = image.shape[:2]
    scale = target_width / width
    target_height = int(height * scale)

    image = cv2.resize(
        image,
        (target_width, target_height),
        interpolation=cv2.INTER_AREA,
    )

    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    return Image.fromarray(image)


def main():
    model = YOLO(str(MODEL_PATH))

    frames = []
    durations = []

    for display_name, image_path in IMAGES:
        original = cv2.imread(str(image_path))

        if original is None:
            raise FileNotFoundError(
                f"Unable to load image: {image_path}"
            )

        # Original image frame
        input_frame = add_banner(
            original,
            f"Input: {display_name}",
            "Held-out PCB test image",
        )

        frames.append(prepare_frame(input_frame))
        durations.append(900)

        # Model inference
        result = model.predict(
            source=str(image_path),
            imgsz=416,
            conf=0.25,
            device="cpu",
            verbose=False,
        )[0]

        annotated = result.plot()

        if len(result.boxes) > 0:
            confidences = [
                float(conf)
                for conf in result.boxes.conf.cpu().tolist()
            ]

            max_confidence = max(confidences)

            detected_classes = sorted(
                {
                    result.names[int(cls)]
                    for cls in result.boxes.cls.cpu().tolist()
                }
            )

            detected_text = ", ".join(detected_classes)

            subtitle = (
                f"{detected_text} | "
                f"max confidence {max_confidence:.3f} | FAIL"
            )
        else:
            subtitle = "No reliable defect detected | UNCERTAIN"

        result_frame = add_banner(
            annotated,
            f"Inspection Result: {display_name}",
            subtitle,
        )

        frames.append(prepare_frame(result_frame))
        durations.append(1600)

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    frames[0].save(
        OUTPUT_PATH,
        save_all=True,
        append_images=frames[1:],
        duration=durations,
        loop=0,
        optimize=True,
    )

    print(f"Saved README demo GIF to: {OUTPUT_PATH}")
    print(f"Frames: {len(frames)}")
    print(
        f"Approximate duration: "
        f"{sum(durations) / 1000:.1f} seconds"
    )


if __name__ == "__main__":
    main()
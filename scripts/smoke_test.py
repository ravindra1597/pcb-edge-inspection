from pathlib import Path
from ultralytics import YOLO


# Locate one validation image automatically
image_dir = Path("data/pcb_defects/valid/images")
images = list(image_dir.glob("*"))

if not images:
    raise FileNotFoundError("No validation images found.")

test_image = images[0]

print(f"Using image: {test_image}")

# Load pretrained YOLOv8 Nano model
model = YOLO("yolov8n.pt")

# Run inference
results = model(test_image)

print("\nInference completed successfully.")

for result in results:
    print(f"Image shape: {result.orig_shape}")
    print(f"Number of detections: {len(result.boxes)}")
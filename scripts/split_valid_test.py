from pathlib import Path
import random
import shutil

# Reproducible random selection
random.seed(42)

# Your dataset folder
dataset_dir = Path("data/pcb_defects")

valid_images = dataset_dir / "valid" / "images"
valid_labels = dataset_dir / "valid" / "labels"

test_images = dataset_dir / "test" / "images"
test_labels = dataset_dir / "test" / "labels"

# Number of images to move to the final test set
test_counts = {
    "missing_hole": 39,
    "mouse_bite": 38,
    "open_circuit": 39,
}

for class_name, count in test_counts.items():

    images = [
        p for p in valid_images.glob("*")
        if p.is_file() and class_name in p.name
    ]

    print(f"{class_name}: found {len(images)} validation images")

    if len(images) < count:
        raise ValueError(
            f"Not enough {class_name} images. "
            f"Requested {count}, found {len(images)}."
        )

    selected = random.sample(images, count)

    # Verify every selected image has a matching YOLO label
    for image_path in selected:
        label_path = valid_labels / f"{image_path.stem}.txt"

        if not label_path.exists():
            raise FileNotFoundError(
                f"Missing label for {image_path.name}"
            )

    # Move image + corresponding label together
    for image_path in selected:
        label_path = valid_labels / f"{image_path.stem}.txt"

        shutil.move(str(image_path), str(test_images / image_path.name))
        shutil.move(str(label_path), str(test_labels / label_path.name))

print("\nSplit completed successfully.")
print("Validation and test sets are now separate.")
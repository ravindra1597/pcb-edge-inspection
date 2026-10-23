# PCB Edge Inspection

Edge AI system for PCB defect detection and quality inspection using a fine-tuned YOLO object detection model.

## Project Overview

This project develops a computer vision backend for automated PCB manufacturing defect inspection.

A fine-tuned YOLO model detects defects in PCB images and provides the perception layer for a quality-inspection application. The next backend stage will convert these detections into structured quality decisions such as:

- `PASS`
- `FAIL`
- `UNCERTAIN`

The system currently focuses on three PCB defect classes:

- `missing_hole`
- `mouse_bite`
- `open_circuit`

The project is being developed as an edge-AI application with planned deployment on NVIDIA Jetson hardware.

## System Pipeline

```text
PCB Image
    ↓
Fine-Tuned YOLOv8n
    ↓
Defect Detection
    ↓
Class + Bounding Box + Confidence
    ↓
Decision Engine
    ↓
PASS / FAIL / UNCERTAIN
    ↓
Structured Backend Output
    ↓
Frontend / Operator Interface
```

## Dataset

The project uses the **PCB Error Detection** dataset from Roboflow Universe.

Dataset information:

- Workspace: `pcb-error-detection`
- Project: `defect-vtuov`
- Version used: `5`
- License: `CC BY 4.0`
- Task: Object Detection

The dataset itself is not stored in this GitHub repository.

### Defect Classes

The dataset contains three classes:

1. `missing_hole`
2. `mouse_bite`
3. `open_circuit`

### Dataset Split

The downloaded training set contained augmented copies of the original training images. The final split used for this project is:

| Split | Images |
| --- | ---: |
| Training | 1,938 |
| Validation | 115 |
| Held-out Test | 116 |

The 1,938 training images are derived from **969 unique source training images**, with two generated versions per source image.

The original validation pool contained 231 images and was divided reproducibly into validation and test sets using a fixed random seed.

The held-out test set was kept separate from training and model selection.

## Model

### Baseline Model

The current baseline model is:

`YOLOv8n`

The model was initialized with pretrained YOLO weights and fine-tuned for the three PCB defect classes.

### Training Configuration

| Parameter | Value |
| --- | --- |
| Model | YOLOv8n |
| Epochs | 30 |
| Image size | 416 × 416 |
| Batch size | 8 |
| Device | CPU |
| Python | 3.11 |
| Random seed | 42 |
| Training images | 1,938 |
| Validation images | 115 |
| Test images | 116 |

The training environment currently uses CPU-based PyTorch.

## Baseline Evaluation Results

### Held-Out Test Results

The final baseline model was evaluated on the separate 116-image held-out test set.

| Metric | Result |
| --- | ---: |
| Precision | **96.2%** |
| Recall | **95.7%** |
| mAP@0.50 | **96.6%** |
| mAP@0.50:0.95 | **54.9%** |

The test set contained 248 labeled defect instances.

### Per-Class Test Results

| Defect Class | Precision | Recall | mAP@0.50 | mAP@0.50:0.95 |
| --- | ---: | ---: | ---: | ---: |
| `missing_hole` | 98.8% | 93.9% | 97.1% | 60.3% |
| `mouse_bite` | 93.1% | 97.2% | 95.7% | 55.9% |
| `open_circuit` | 96.7% | 96.2% | 96.9% | 48.6% |

The results indicate strong defect detection performance across all three classes.

The lower mAP@0.50:0.95 values, particularly for `open_circuit`, indicate that precise bounding-box localization is more difficult than identifying the presence and approximate location of a defect.

## Validation Results

The final validation results were:

| Metric | Result |
| --- | ---: |
| Precision | 97.8% |
| Recall | 96.6% |
| mAP@0.50 | 97.7% |
| mAP@0.50:0.95 | 58.0% |

The relatively small difference between validation and held-out test performance suggests that the baseline model generalizes well to unseen PCB images.

## Inference Performance

During held-out test evaluation on an Intel Core i5-13420H CPU, Ultralytics reported approximately:

```text
Preprocessing:   0.4 ms/image
Inference:      18.0 ms/image
Postprocessing:  0.7 ms/image
```

These numbers represent model-evaluation timing and are not yet treated as final end-to-end backend latency.

A separate application-level benchmark will be performed after the inference and decision-engine backend is complete.

## Project Structure

```text
pcb-edge-inspection/
│
├── data/
│   └── pcb_defects/
│       ├── train/
│       ├── valid/
│       ├── test/
│       └── data.yaml
│
├── models/
│
├── scripts/
│   ├── smoke_test.py
│   ├── split_valid_test.py
│   ├── train.py
│   └── evaluate.py
│
├── src/
│
├── tests/
│
├── requirements.txt
├── .gitignore
└── README.md
```

Dataset images are excluded from Git tracking.

Generated training runs and model weight files are also excluded from Git tracking.

## Python Environment

Recommended environment:

```text
Python 3.11
```

Install project dependencies using:

```bash
pip install -r requirements.txt
```

Current primary dependency:

```text
ultralytics==8.4.184
```

## Training

Run baseline training from the repository root:

```bash
python scripts/train.py
```

The current training script:

- loads pretrained YOLOv8n weights
- fine-tunes the model for the three PCB defect classes
- trains for 30 epochs
- uses 416 × 416 images
- validates during training
- saves the best and final model weights

Training outputs are generated under the Ultralytics run directory.

The trained model weights are intentionally excluded from Git tracking.

## Evaluation

Run held-out test evaluation using:

```bash
python scripts/evaluate.py
```

The evaluation script loads the selected `best.pt` model and evaluates it using:

```text
split="test"
```

This ensures that final baseline metrics are calculated on the held-out test set rather than the validation set.

## Backend Goal

The final backend will accept a PCB image and return structured defect information.

Example planned output:

```json
{
  "status": "FAIL",
  "defects": [
    {
      "class": "open_circuit",
      "confidence": 0.91,
      "bbox": [120, 85, 240, 190]
    }
  ],
  "defect_count": 1,
  "inference_ms": 47
}
```

The backend will separate:

1. **Perception** — YOLO defect detection
2. **Decision making** — PASS / FAIL / UNCERTAIN logic
3. **Presentation** — structured output for the frontend

## Planned Decision Logic

The backend decision engine will use model predictions to determine the PCB inspection result.

Initial intended behavior:

```text
No reliable defect detected
→ PASS

One or more reliable defects detected
→ FAIL

Low-confidence or ambiguous prediction
→ UNCERTAIN / MANUAL REVIEW
```

Confidence thresholds and decision rules will be tested before being finalized.

## Backend Progress

- [x] GitHub repository created
- [x] project structure created
- [x] isolated Python environment created
- [x] dataset downloaded and inspected
- [x] dataset class distribution inspected
- [x] data augmentation structure identified
- [x] reproducible validation/test split created
- [x] dataset configuration verified
- [x] YOLO inference smoke test completed
- [x] one-epoch training dry run completed
- [x] full YOLOv8n baseline training completed
- [x] held-out baseline evaluation completed
- [ ] production inference module
- [ ] PASS / FAIL / UNCERTAIN decision engine
- [ ] structured backend response
- [ ] backend API/interface
- [ ] automated backend tests
- [ ] NVIDIA Jetson deployment
- [ ] frontend integration

## Docker

Docker container image:

```text
TBD
```

The deployment container will be selected after the backend runtime and NVIDIA Jetson environment are finalized.

The final repository documentation will include the exact Docker container image used for deployment.

## Planned Edge Deployment

The trained model will later be deployed on NVIDIA Jetson hardware.

Planned deployment work includes:

- Jetson environment verification
- model transfer
- inference testing
- latency benchmarking
- FPS measurement
- possible TensorRT optimization
- integration with the backend decision engine

## Current Status

The baseline computer vision model has been successfully trained and evaluated.

The next development milestone is to build the application backend around the trained detector:

```text
Image Input
    ↓
YOLO Inference
    ↓
Detection Parsing
    ↓
Decision Engine
    ↓
PASS / FAIL / UNCERTAIN
    ↓
Structured Result
```

This backend will later provide the data and decisions required by the frontend interface.
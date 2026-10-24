# PCB Edge Inspection

Edge AI system for PCB defect detection and quality inspection using a fine-tuned YOLO object detection model.

## Project Overview

This project develops a computer vision backend for automated PCB manufacturing defect inspection.

A fine-tuned YOLOv8n model detects manufacturing defects in PCB images. The model predictions are then processed by a decision engine that converts raw detections into an application-level inspection result.

The system currently detects three PCB defect classes:

- `missing_hole`
- `mouse_bite`
- `open_circuit`

The backend exposes the inspection pipeline through a FastAPI service so that a frontend application can later upload PCB images and receive structured inspection results.

The project is being developed with planned deployment on NVIDIA Jetson hardware.

---

## System Architecture

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
FAIL / UNCERTAIN
    ↓
Structured JSON Response
    ↓
FastAPI Backend
    ↓
Frontend / Operator Interface
```

The architecture separates three responsibilities:

1. **Perception** — detect PCB defects using YOLO.
2. **Decision making** — convert detections into an inspection decision.
3. **Presentation** — provide structured results to a frontend through an API.

---

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

The downloaded training set contained augmented copies of the original training images.

The final split used for this project is:

| Split | Images |
| --- | ---: |
| Training | 1,938 |
| Validation | 115 |
| Held-out Test | 116 |

The 1,938 training images were generated from **969 unique source training images**, with two generated versions for each source image.

The original validation pool contained 231 images. It was reproducibly divided into validation and test sets using a fixed random seed.

The held-out test set was kept separate from model training and model selection.

### Dataset Limitation

All available training, validation, and test images contain at least one annotated defect.

There are currently **no confirmed defect-free PCB images** in the dataset.

Because of this limitation, the system cannot yet scientifically validate the rule:

```text
No detected defect → PASS
```

A missing detection could represent either:

- a genuinely defect-free PCB, or
- a defect that the model failed to detect.

Therefore, the current backend conservatively returns:

```text
Reliable defect detected
→ FAIL

Only medium-confidence detections
→ UNCERTAIN

No defect detected
→ UNCERTAIN
```

Defect-free PCB images will be needed before a reliable `PASS` decision can be validated.

---

## Model

### Baseline Model

The current baseline model is:

```text
YOLOv8n
```

The model was initialized using pretrained YOLO weights and fine-tuned for the three PCB defect classes.

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

The current development environment uses CPU-based PyTorch.

---

## Baseline Evaluation Results

### Held-Out Test Results

The selected baseline model was evaluated on the separate 116-image held-out test set.

The test set contained **248 labeled defect instances**.

| Metric | Result |
| --- | ---: |
| Precision | **96.2%** |
| Recall | **95.7%** |
| mAP@0.50 | **96.6%** |
| mAP@0.50:0.95 | **54.9%** |

### Per-Class Test Results

| Defect Class | Precision | Recall | mAP@0.50 | mAP@0.50:0.95 |
| --- | ---: | ---: | ---: | ---: |
| `missing_hole` | 98.8% | 93.9% | 97.1% | 60.3% |
| `mouse_bite` | 93.1% | 97.2% | 95.7% | 55.9% |
| `open_circuit` | 96.7% | 96.2% | 96.9% | 48.6% |

The results show strong defect-detection performance across all three classes.

The lower mAP@0.50:0.95 values indicate that exact bounding-box localization is more difficult than determining whether a defect exists and approximately where it is located.

---

## Validation Results

The final validation results were:

| Metric | Result |
| --- | ---: |
| Precision | 97.8% |
| Recall | 96.6% |
| mAP@0.50 | 97.7% |
| mAP@0.50:0.95 | 58.0% |

The relatively small difference between validation and held-out test performance suggests that the baseline detector generalizes well to unseen PCB defect images.

---

## Backend Inference Performance

The complete backend pipeline was benchmarked on an Intel Core i5-13420H CPU.

A six-run benchmark produced:

```text
Run 1: 2124.68 ms
Run 2:   96.53 ms
Run 3:   35.82 ms
Run 4:   38.52 ms
Run 5:   36.15 ms
Run 6:   35.76 ms
```

Summary:

| Measurement | Latency |
| --- | ---: |
| Cold first inference | 2124.68 ms |
| Average warm latency | 48.56 ms |
| Fastest warm latency | 35.76 ms |
| Slowest warm latency | 96.53 ms |

The large first-request latency is caused by model and runtime warm-up.

Once the model is loaded and warmed up, backend inspection runs in approximately **36–50 ms per image** on the current CPU development environment.

The backend therefore loads the YOLO model once when the service starts rather than reloading it for each request.

---

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
│   ├── evaluate.py
│   └── benchmark_backend.py
│
├── src/
│   ├── __init__.py
│   ├── inference.py
│   ├── decision_engine.py
│   ├── backend.py
│   └── api.py
│
├── tests/
│   └── test_decision_engine.py
│
├── requirements.txt
├── .gitignore
└── README.md
```

Dataset images are excluded from Git tracking.

Generated training outputs and model weight files are also excluded from Git tracking.

---

## Python Environment

Recommended Python version:

```text
Python 3.11
```

Install dependencies using:

```bash
pip install -r requirements.txt
```

Current direct project dependencies:

```text
ultralytics==8.4.184
fastapi==0.162.0
uvicorn==0.54.0
python-multipart==0.0.32
```

---

## Training

Run baseline training from the repository root:

```bash
python scripts/train.py
```

The current training script:

- loads pretrained YOLOv8n weights
- fine-tunes the model for three PCB defect classes
- trains for 30 epochs
- uses 416 × 416 images
- validates during training
- saves the best and final model weights

Model weights and generated training outputs are intentionally excluded from Git tracking.

---

## Evaluation

Run held-out test evaluation using:

```bash
python scripts/evaluate.py
```

The evaluation script loads the selected `best.pt` model and evaluates it using:

```text
split="test"
```

This ensures that final baseline performance is measured using the held-out test set instead of the validation set.

---

## Inference Module

The inference layer is implemented in:

```text
src/inference.py
```

It loads the fine-tuned YOLO model and converts Ultralytics prediction objects into structured Python data.

Example detection:

```json
{
  "class_id": 0,
  "class_name": "missing_hole",
  "confidence": 0.8161,
  "bbox": [
    188.18,
    266.28,
    222.50,
    303.17
  ]
}
```

The inference layer is intentionally separate from application decision logic.

---

## Decision Engine

Inspection decision logic is implemented in:

```text
src/decision_engine.py
```

Current thresholds:

```text
Reliable defect threshold: 0.60
Uncertain threshold:       0.40
```

Current logic:

```text
Confidence >= 0.60
→ FAIL

Confidence >= 0.40 and < 0.60
→ UNCERTAIN

No qualifying detection
→ UNCERTAIN
```

The no-detection case is currently treated as `UNCERTAIN` because the available dataset does not contain verified defect-free PCB images.

The decision engine has independent tests covering:

- reliable defect detection
- low-confidence detection
- no-detection behavior

---

## Unified Backend

The end-to-end inspection pipeline is implemented in:

```text
src/backend.py
```

The backend combines:

```text
Image
   ↓
PCBDefectDetector
   ↓
Structured detections
   ↓
Decision Engine
   ↓
Structured inspection result
```

Example backend result:

```json
{
  "image": "pcb_image.jpg",
  "image_width": 600,
  "image_height": 600,
  "status": "FAIL",
  "reason": "Reliable defect detection(s): missing_hole",
  "defect_count": 1,
  "detections": [
    {
      "class_id": 0,
      "class_name": "missing_hole",
      "confidence": 0.8161,
      "bbox": [
        188.18,
        266.28,
        222.50,
        303.17
      ]
    }
  ],
  "inference_pipeline_ms": 47.26
}
```

---

## Backend API

The backend is exposed through FastAPI.

Start the API from the repository root:

```bash
python -m uvicorn src.api:app --reload
```

Available endpoints:

```text
GET  /
GET  /health
POST /inspect
```

### Health Endpoint

Example:

```text
GET /health
```

Response:

```json
{
  "status": "ok",
  "model_loaded": true
}
```

### Inspection Endpoint

The inspection endpoint accepts an uploaded PCB image:

```text
POST /inspect
```

Supported image formats:

- JPG
- JPEG
- PNG
- BMP

The endpoint returns structured JSON containing:

- original image filename
- image dimensions
- inspection status
- explanation
- number of detected defects
- detected defect classes
- confidence scores
- bounding boxes
- backend pipeline latency

Example:

```json
{
  "image": "pcb_example.jpg",
  "image_width": 600,
  "image_height": 600,
  "status": "FAIL",
  "reason": "Reliable defect detection(s): missing_hole, missing_hole",
  "defect_count": 2,
  "detections": [
    {
      "class_id": 0,
      "class_name": "missing_hole",
      "confidence": 0.7894,
      "bbox": [
        213.26,
        477.04,
        244.02,
        512.13
      ]
    },
    {
      "class_id": 0,
      "class_name": "missing_hole",
      "confidence": 0.7759,
      "bbox": [
        546.88,
        393.94,
        575.51,
        427.47
      ]
    }
  ],
  "inference_pipeline_ms": 47.26
}
```

### Interactive API Documentation

When the FastAPI server is running, Swagger documentation is available at:

```text
http://127.0.0.1:8000/docs
```

### Invalid File Handling

Unsupported files are rejected with:

```text
HTTP 400 Bad Request
```

Example response:

```json
{
  "detail": "Unsupported file type. Please upload JPG, JPEG, PNG, or BMP."
}
```

---

## Backend Tests

The decision engine can be tested using:

```bash
python tests/test_decision_engine.py
```

Current tests verify:

- high-confidence defects produce `FAIL`
- medium-confidence detections produce `UNCERTAIN`
- no detections produce `UNCERTAIN`

Additional automated API and inference tests are planned.

---

## Backend Progress

- [x] GitHub repository created
- [x] project structure created
- [x] isolated Python environment created
- [x] dataset downloaded and inspected
- [x] dataset class distribution inspected
- [x] augmentation structure identified
- [x] reproducible validation/test split created
- [x] dataset configuration verified
- [x] YOLO inference smoke test completed
- [x] one-epoch training dry run completed
- [x] full YOLOv8n baseline training completed
- [x] held-out baseline evaluation completed
- [x] production inference module
- [x] decision engine
- [x] structured backend response
- [x] backend API/interface
- [x] invalid upload handling
- [x] basic decision-engine tests
- [x] backend latency benchmark
- [ ] automated API tests
- [ ] defect-free PCB validation
- [ ] NVIDIA Jetson deployment
- [ ] frontend integration

---

## Docker

Docker container image:

```text
TBD
```

The deployment container will be selected after the NVIDIA Jetson runtime requirements are finalized.

The final repository documentation will include the exact Docker container image used for deployment.

---

## Planned Edge Deployment

The trained model will later be deployed on NVIDIA Jetson hardware.

Planned deployment work includes:

- Jetson environment verification
- model transfer
- Jetson inference testing
- latency benchmarking
- FPS measurement
- possible TensorRT optimization
- integration with the existing backend
- comparison between development-machine and Jetson performance

---

## Current Status

The baseline computer vision model has been successfully trained and evaluated.

The core backend pipeline is also operational:

```text
Image Upload
    ↓
FastAPI
    ↓
YOLOv8n Inference
    ↓
Structured Defect Detection
    ↓
Decision Engine
    ↓
FAIL / UNCERTAIN
    ↓
JSON Response
```

The backend currently provides:

- trained PCB defect detector
- structured inference results
- inspection decision logic
- API-based image upload
- input validation
- backend latency measurement
- interactive Swagger documentation

The next development stages are automated API testing, NVIDIA Jetson deployment, and frontend integration.
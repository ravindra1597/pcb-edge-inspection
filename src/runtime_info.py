"""
Report what the backend is actually running on.

Most values are detected, not typed in:
- engine format comes from the model file extension,
- precision and input size come from the metadata header that
  Ultralytics writes at the start of a TensorRT .engine file,
- the board name comes from PCB_BOARD (passed in by `docker run`,
  because /proc/device-tree is not visible inside the container),
  falling back to the CUDA device name.

The model label (for example "YOLOv8n") is NOT stored in the engine
file, so it is a configured value: PCB_MODEL_LABEL, default "YOLOv8n".
"""

import json
import os
import platform
from pathlib import Path


_ENGINE_NAMES = {
    ".engine": "TensorRT",
    ".pt": "PyTorch",
    ".onnx": "ONNX",
}


def read_engine_metadata(model_path):
    """
    Read the JSON metadata header at the start of an Ultralytics
    TensorRT engine file: a 4-byte little-endian length, then JSON.
    Returns None if the file does not have that header.
    """
    try:
        with open(model_path, "rb") as engine_file:
            length = int.from_bytes(
                engine_file.read(4),
                "little",
                signed=True,
            )

            if not 0 < length < 1_000_000:
                return None

            return json.loads(
                engine_file.read(length).decode("utf-8")
            )

    except (OSError, ValueError):
        return None


def _precision(metadata):
    args = (metadata or {}).get("args") or {}

    quantize = args.get("quantize")

    if quantize == 16:
        return "FP16"

    if quantize == 8:
        return "INT8"

    # Older Ultralytics versions used boolean flags instead.
    if args.get("half") is True:
        return "FP16"

    if args.get("int8") is True:
        return "INT8"

    return None


def _describe_device(device):
    """Return (short label, detailed label, accelerator kind)."""
    device = str(device).lower()

    if device == "cpu":
        label = f"CPU ({platform.machine() or 'unknown'})"
        return label, label, "CPU"

    board = os.getenv("PCB_BOARD", "").strip()

    gpu_name = None

    try:
        import torch

        if torch.cuda.is_available():
            gpu_name = torch.cuda.get_device_name(0)

    except Exception:
        gpu_name = None

    if board:
        detail = board
    elif gpu_name:
        detail = f"GPU: {gpu_name}"
    else:
        detail = f"CUDA device {device}"

    short = (
        detail
        .replace("NVIDIA ", "", 1)
        .replace(" Developer Kit", "")
    )

    return short, detail, "GPU (CUDA)"


def get_runtime_info(model_path, device):
    model_path = Path(model_path)
    suffix = model_path.suffix.lower()

    metadata = (
        read_engine_metadata(model_path)
        if suffix == ".engine"
        else None
    )

    input_size = None

    if metadata:
        imgsz = metadata.get("imgsz")

        if isinstance(imgsz, (list, tuple)) and len(imgsz) == 2:
            input_size = [int(imgsz[0]), int(imgsz[1])]

    short, detail, accelerator = _describe_device(device)

    return {
        "device": short,
        "device_detail": detail,
        "accelerator": accelerator,
        "engine": _ENGINE_NAMES.get(
            suffix,
            suffix.lstrip(".").upper() or "Unknown",
        ),
        "precision": _precision(metadata),
        "input_size": input_size,
        # Configured label: not stored in the model file.
        "model": os.getenv("PCB_MODEL_LABEL", "YOLOv8n"),
        "model_file": model_path.name,
    }

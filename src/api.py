from pathlib import Path
import shutil
import tempfile

from fastapi import FastAPI, File, HTTPException, UploadFile

from .backend import PCBInspectionBackend


app = FastAPI(
    title="PCB Edge Inspection API",
    description="Backend API for PCB defect detection and inspection decisions.",
    version="1.0.0",
)

# Load model once when the API process starts.
backend = PCBInspectionBackend()


@app.get("/")
def root():
    return {
        "message": "PCB Edge Inspection API is running."
    }


@app.get("/health")
def health():
    return {
        "status": "ok",
        "model_loaded": True,
    }


@app.post("/inspect")
async def inspect_pcb(file: UploadFile = File(...)):
    allowed_extensions = {".jpg", ".jpeg", ".png", ".bmp"}

    suffix = Path(file.filename or "").suffix.lower()

    if suffix not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=(
                "Unsupported file type. "
                "Please upload JPG, JPEG, PNG, or BMP."
            ),
        )

    temp_path = None

    try:
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=suffix,
        ) as temp_file:
            shutil.copyfileobj(file.file, temp_file)
            temp_path = Path(temp_file.name)

        result = backend.inspect(temp_path)

        # Replace temporary local filename with the original upload name.
        result["image"] = file.filename

        return result

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Inspection failed: {str(exc)}",
        )

    finally:
        await file.close()

        if temp_path and temp_path.exists():
            temp_path.unlink()
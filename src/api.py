from contextlib import asynccontextmanager
from pathlib import Path
import shutil
import tempfile

from fastapi import FastAPI, File, HTTPException, Response, UploadFile
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

from .backend import PCBInspectionBackend
from .camera import CameraService


# The camera is opened lazily on first use, so the API still starts
# normally on machines without a camera (for example the Windows laptop).
camera = CameraService()


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    camera.stop()


app = FastAPI(
    title="PCB Edge Inspection API",
    description="Backend API for PCB defect detection and inspection decisions.",
    version="1.0.0",
    lifespan=lifespan,
)

BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"

app.mount(
    "/static",
    StaticFiles(directory=FRONTEND_DIR),
    name="static",
)

# Load model once when the API process starts.
backend = PCBInspectionBackend()


@app.get("/")
def root():
    return FileResponse(
        FRONTEND_DIR / "index.html"
    )


@app.get("/health")
def health():
    return {
        "status": "ok",
        "model_loaded": True,
    }


# ---------------------------------------------------------------
# Camera
# ---------------------------------------------------------------

def _start_camera_or_503():
    try:
        camera.ensure_started()
    except RuntimeError as exc:
        raise HTTPException(
            status_code=503,
            detail=str(exc),
        )


@app.get("/camera/status")
def camera_status():
    return camera.status()


@app.get("/camera/stream")
def camera_stream():
    """Live MJPEG preview for the browser."""
    _start_camera_or_503()

    return StreamingResponse(
        camera.mjpeg_stream(),
        media_type="multipart/x-mixed-replace; boundary=frame",
    )


@app.get("/camera/snapshot")
def camera_snapshot():
    """
    Return the current camera frame as a single JPEG.

    The frontend shows this exact frame and then sends it to
    /inspect, so the frame inspected is the frame the user saw.
    """
    _start_camera_or_503()

    if not camera.wait_until_ready(timeout=5.0):
        raise HTTPException(
            status_code=503,
            detail="Camera is not ready yet. Try again in a moment.",
        )

    jpeg = camera.get_jpeg(quality=95)

    if jpeg is None:
        raise HTTPException(
            status_code=503,
            detail="Could not capture a frame from the camera.",
        )

    return Response(
        content=jpeg,
        media_type="image/jpeg",
        headers={"Cache-Control": "no-store"},
    )


# ---------------------------------------------------------------
# Inspection
# ---------------------------------------------------------------

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
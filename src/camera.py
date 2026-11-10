import os
import threading
import time

import cv2


class CameraService:
    """
    Owns the USB camera and always keeps the most recent frame available.

    A background thread reads frames continuously so that:
    - V4L2 buffers never hand back stale frames, and
    - the camera's auto-exposure has settled by the time a request
      asks for a frame (the first frames are dark/underexposed).
    """

    def __init__(
        self,
        index=None,
        width=1280,
        height=720,
        warmup_frames=15,
    ):
        if index is None:
            index = int(os.getenv("PCB_CAMERA_INDEX", "0"))

        self.index = index
        self.width = width
        self.height = height
        self.warmup_frames = warmup_frames

        self._cap = None
        self._thread = None
        self._lock = threading.Lock()
        self._frame = None
        self._frames_read = 0
        self._running = False
        self.error = None

    # ---------- lifecycle ----------

    def start(self):
        if self._running:
            return

        cap = cv2.VideoCapture(self.index, cv2.CAP_V4L2)
        cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

        if not cap.isOpened():
            cap.release()
            self.error = f"Camera {self.index} could not be opened."
            raise RuntimeError(self.error)

        self._cap = cap
        self.error = None
        self._frame = None
        self._frames_read = 0
        self._running = True

        self._thread = threading.Thread(
            target=self._reader,
            daemon=True,
        )
        self._thread.start()

    def stop(self):
        self._running = False

        if self._thread is not None:
            self._thread.join(timeout=2)
            self._thread = None

        if self._cap is not None:
            self._cap.release()
            self._cap = None

        with self._lock:
            self._frame = None
            self._frames_read = 0

    def ensure_started(self):
        if not self._running:
            self.start()

    # ---------- background reader ----------

    def _reader(self):
        while self._running:
            ok, frame = self._cap.read()

            if not ok:
                self.error = "Camera read failed."
                time.sleep(0.1)
                continue

            self.error = None

            with self._lock:
                self._frame = frame
                self._frames_read += 1

    # ---------- public API ----------

    @property
    def is_ready(self):
        with self._lock:
            return (
                self._running
                and self._frame is not None
                and self._frames_read >= self.warmup_frames
            )

    def wait_until_ready(self, timeout=5.0):
        deadline = time.time() + timeout

        while time.time() < deadline:
            if self.is_ready:
                return True
            time.sleep(0.05)

        return False

    def get_frame(self):
        """Return a copy of the latest frame (BGR), or None."""
        with self._lock:
            if self._frame is None:
                return None
            return self._frame.copy()

    def get_jpeg(self, quality=90):
        """Return the latest frame encoded as JPEG bytes, or None."""
        frame = self.get_frame()

        if frame is None:
            return None

        ok, buffer = cv2.imencode(
            ".jpg",
            frame,
            [int(cv2.IMWRITE_JPEG_QUALITY), quality],
        )

        return buffer.tobytes() if ok else None

    def mjpeg_stream(self, fps=10):
        """Yield multipart MJPEG chunks for a browser <img> preview."""
        delay = 1.0 / fps

        while self._running:
            jpeg = self.get_jpeg(quality=80)

            if jpeg is not None:
                yield (
                    b"--frame\r\n"
                    b"Content-Type: image/jpeg\r\n\r\n"
                    + jpeg
                    + b"\r\n"
                )

            time.sleep(delay)

    def status(self):
        return {
            "running": self._running,
            "ready": self.is_ready,
            "index": self.index,
            "resolution": [self.width, self.height],
            "error": self.error,
        }
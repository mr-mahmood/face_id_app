from app.config import YOLO_MODEL_PATH
from ultralytics import YOLO
import torch

# Select device
device = "cuda" if torch.cuda.is_available() else "cpu"

# Load model and move to selected device
if YOLO_MODEL_PATH is None:
    raise ValueError("YOLO_MODEL_PATH is not set or is None")

model = YOLO(YOLO_MODEL_PATH).to(device)

def get_model():
    """
    Get the loaded YOLO face detection model on the appropriate device.

    Returns
    -------
    model : YOLO
        Loaded YOLO model for face detection, moved to CUDA if available.
    """
    return model

# Expose API
from .detector import detect_faces

__all__ = ["detect_faces"]

from app.config import YOLO_MODEL_PATH
from ultralytics import YOLO
import torch

# Select device
device = "cuda" if torch.cuda.is_available() else "cpu"

# Load model and move to selected device
model = YOLO(YOLO_MODEL_PATH).to(device)

def get_model():
    """
    Returns the loaded YOLO model on the correct device.
    """
    return model

# Expose API
from .detector import detect_faces

__all__ = ["detect_faces"]

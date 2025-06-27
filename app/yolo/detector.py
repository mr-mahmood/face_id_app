import time
from . import get_model
import numpy as np

def detect_faces(image: np.ndarray) -> tuple[np.ndarray, float]:
    """
    Detect faces in a given 640x640 RGB image using YOLO.

    Parameters
    ----------
    image : np.ndarray
        RGB image as NumPy array, shape (H, W, 3), dtype: uint8.

    Returns
    -------
    boxes : np.ndarray
        Bounding boxes as (N, 4) array: [x1, y1, x2, y2].
    used_time : float
        Inference time in milliseconds.
    
    Raises
    ------
    RuntimeError
        If extract Bounding boxes fails due to model or image issues.
    """
    try:
        model = get_model()
        start = time.time()
        results = model(image, verbose=False)[0]
        boxes = results.boxes.xyxy.cpu().numpy()
        used_time = (time.time() - start) * 1000  # milliseconds
        return boxes, used_time
    
    except Exception as e:
        raise RuntimeError(f"Failed to extract Bounding boxes: {e}")

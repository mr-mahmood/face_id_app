import time
from . import get_model
import numpy as np

def detect_faces(image: np.ndarray, conf_threshold: float = 0.7) -> tuple[np.ndarray, float]:
    """
    Detect faces in a given RGB image using YOLO and filter by confidence.

    Parameters
    ----------
    image : np.ndarray
        RGB image as NumPy array, shape (H, W, 3), dtype: uint8.

    conf_threshold : float, optional
        Minimum confidence required to accept a detection (default: 0.5).

    Returns
    -------
    boxes : np.ndarray
        Bounding boxes as (N, 4) array: [x1, y1, x2, y2].

    used_time : float
        Inference time in milliseconds.

    Raises
    ------
    RuntimeError
        If detection or post-processing fails.
    """
    try:
        model = get_model()
        results = model(image, verbose=False)[0]
        all_boxes = results.boxes.xyxy.cpu().numpy()
        confidences = results.boxes.conf.cpu().numpy()
        total_time = results.speed['preprocess'] + results.speed['inference'] + results.speed['postprocess']
        time_per_face = total_time / len(all_boxes)
        filtered_boxes = all_boxes[confidences >= conf_threshold]
        return filtered_boxes, time_per_face

    except Exception as e:
        raise RuntimeError(f"Failed to extract bounding boxes: {e}")

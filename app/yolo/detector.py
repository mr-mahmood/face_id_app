import time
from . import get_model
import numpy as np

def detect_faces(image: np.ndarray, conf_threshold: float = 0.7) -> tuple[np.ndarray, float]:
    """
    Detect faces in an image using YOLO model and filter by confidence threshold.

    Parameters
    ----------
    image : np.ndarray
        Input image in BGR format. Shape: (H, W, 3), dtype: uint8.

    conf_threshold : float, optional
        Minimum confidence threshold for face detection. Default: 0.7.

    Returns
    -------
    boxes : np.ndarray
        Bounding boxes of detected faces. Shape: (N, 4), format: [x1, y1, x2, y2].

    used_time : float
        Average inference time per detected face in milliseconds.

    Raises
    ------
    RuntimeError
        If face detection or post-processing fails.
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

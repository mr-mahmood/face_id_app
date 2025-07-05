import numpy as np
import time
import cv2

def resize_face(face: np.ndarray, size=(160, 160)) -> tuple[np.ndarray, float]:
    """
    Resize a face image to the specified dimensions for embedding model input.

    Parameters
    ----------
    face : np.ndarray
        Input face image. Shape: (H, W, 3), dtype: uint8.

    size : tuple, optional
        Target size (width, height) for the face embedding model. Default: (160, 160).

    Returns
    -------
    face_resized : np.ndarray
        Resized face image. Shape: (size[1], size[0], 3), dtype: uint8.

    resize_time : float
        Time taken for resize operation in milliseconds.

    Raises
    ------
    RuntimeError
        If resize operation fails.
    """
    try:
        start = time.time()
        face_resized = cv2.resize(face, size)
        resize_time = (time.time() - start) * 1000  # milliseconds
        return face_resized, resize_time
    
    except Exception as e:
        raise RuntimeError(f"Failed to resize face: {e}")
    

def crop_face(frame: np.ndarray, box) -> tuple[np.ndarray, float]:
    """
    Crop a face region from the input frame using bounding box coordinates.

    Parameters
    ----------
    frame : np.ndarray
        Original image frame in BGR format. Shape: (H, W, 3), dtype: uint8.

    box : list or np.ndarray
        Face bounding box coordinates [x1, y1, x2, y2] as pixel coordinates.

    Returns
    -------
    face_cropped : np.ndarray
        Cropped face image in BGR format. Shape: (y2-y1, x2-x1, 3), dtype: uint8.

    crop_time : float
        Time taken for crop operation in milliseconds.
    
    Raises
    ------
    RuntimeError
        If crop operation fails.
    """
    try:
        start = time.time()
        x1, y1, x2, y2 = map(int, box)
        h, w = frame.shape[:2]
        x1, y1 = max(0, x1), max(0, y1)
        x2, y2 = min(w, x2), min(h, y2)
        face = frame[y1:y2, x1:x2]
        crop_time = (time.time() - start) * 1000  # milliseconds
        return face, crop_time
    
    except Exception as e:
        raise RuntimeError(f"Failed to crop face from frame: {e}")
    

def normalize(embedding: np.ndarray) -> np.ndarray:
    """
    Normalize a face embedding vector using L2 norm for consistent similarity calculations.

    Parameters
    ----------
    embedding : np.ndarray
        A 1D face embedding vector. Shape: (N,), dtype: float32 or float64.

    Returns
    -------
    normalized : np.ndarray
        L2-normalized embedding vector. Shape: (N,), same dtype as input.

    Raises
    ------
    RuntimeError
        If the embedding norm is zero or invalid input is provided.
    """
    try:
        norm = np.linalg.norm(embedding)
        if norm == 0:
            raise ValueError("Cannot normalize zero-vector.")
        return embedding / norm
    except Exception as e:
        raise RuntimeError(f"Failed to normalize embedding: {e}")

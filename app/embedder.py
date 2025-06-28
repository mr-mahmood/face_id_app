from app.config import EMBEDDING_MODEL
from app import normalize
from deepface import DeepFace
import numpy as np
import time

def embbeding_face(face: np.ndarray) -> tuple[np.ndarray, float]:
    """
    Generate a normalized facial embedding for a given face image using DeepFace.

    Parameters
    ----------
    face : np.ndarray
        A cropped RGB face image as a NumPy array.
        Shape: (H, W, 3), dtype: uint8

    Returns
    -------
    embedding : np.ndarray
        The L2-normalized facial embedding vector.
        Shape: (128,), dtype: float32 (assuming SFace returns 128-dim)

    embed_time : float
        Time taken to generate the embedding in milliseconds.

    Raises
    ------
    RuntimeError
        If embedding generation fails due to model or image issues.
    """
    try:
        start_embed = time.time()
        result = DeepFace.represent(img_path=face, model_name=EMBEDDING_MODEL, enforce_detection=False)[0]
        embedding = normalize(np.array(result["embedding"]).astype(np.float32))
        embed_time = (time.time() - start_embed) * 1000  # milliseconds
        return embedding, embed_time

    except Exception as e:
        raise RuntimeError(f"Failed to extract embedding: {e}")


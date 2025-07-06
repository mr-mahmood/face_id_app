import numpy as np
from app.model_manager import get_model_manager

async def embbeding_face(face: np.ndarray) -> tuple[np.ndarray, float]:
    """
    Generate a normalized facial embedding for a given face image using DeepFace.

    Parameters
    ----------
    face : np.ndarray
        A cropped face image as a NumPy array. Shape: (H, W, 3), dtype: uint8.

    Returns
    -------
    embedding : np.ndarray
        The L2-normalized facial embedding vector. Shape: (128,), dtype: float32.

    embed_time : float
        Time taken to generate the embedding in milliseconds.

    Raises
    ------
    RuntimeError
        If embedding generation fails due to model or image issues.
    """
    try:
        model_manager = await get_model_manager()
        return model_manager.generate_embedding(face)

    except Exception as e:
        raise RuntimeError(f"Failed to extract embedding: {e}")


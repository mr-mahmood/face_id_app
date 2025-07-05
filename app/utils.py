import os
import faiss
import pickle
import numpy as np
import cv2
from fastapi import UploadFile
from app.config import EMBEDDING_DIM

def load_faiss(faiss_path, label_path):
    """
    Load or initialize FAISS index and labels for face similarity search.

    Parameters
    ----------
    faiss_path : str
        Path to the FAISS index file.

    label_path : str
        Path to the labels pickle file.

    Returns
    -------
    index : faiss.IndexFlatIP
        FAISS index object for inner product similarity search.

    labels : list
        List of identity labels corresponding to each embedding in the FAISS index.

    Raises
    ------
    RuntimeError
        If fail to load or initialize FAISS index and labels.
    """
    try:
        # Load or initialize FAISS index and labels
        if os.path.exists(faiss_path) and os.path.exists(label_path):
            index = faiss.read_index(faiss_path)
            with open(label_path, "rb") as f:
                labels = pickle.load(f)
        else:
            index = faiss.IndexFlatIP(EMBEDDING_DIM)   
            faiss.write_index(index, faiss_path)
            labels = []
            with open(label_path, "wb") as f:
                pickle.dump(labels, f)

        return index, labels

    except Exception as e:
        raise RuntimeError(f"Failed to load faiss and labels: {e}")

async def read_image(image: UploadFile) -> np.ndarray | None:
    """
    Read and decode an image from an UploadFile object to numpy array.

    Parameters
    ----------
    image : UploadFile
        The uploaded image file from FastAPI.

    Returns
    -------
    np.ndarray | None
        Decoded image array in BGR format, or None if decoding fails.
        Shape: (H, W, 3), dtype: uint8.
    """
    try:
        image_bytes = await image.read()
        np_arr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        return img if img is not None else None
    except Exception as e:
        print(f"[read_image] Error reading image: {e}")
        return None
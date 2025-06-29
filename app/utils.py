import os
import faiss
import pickle
import numpy as np
import cv2
from fastapi import UploadFile, HTTPException, status

from app.config import FAISS_INDEX_PATH, LABELS_PATH, EMBEDDING_DIM, DATASET_DIR

def start_add_refrence_images(label_id: str):
    """
    Initialize directories and FAISS index for a new reference identity.

    This function:
    - Ensures dataset and FAISS directories exist
    - Creates a folder for the new identity under the dataset
    - Loads or creates a FAISS index for storing face embeddings
    - Loads or initializes the list of corresponding labels

    Parameters
    ----------
    label_id : str
        The identity name (label) used to create a subfolder and associate with embeddings.

    Returns
    -------
    index : faiss.IndexFlatIP
        FAISS index object (either newly created or loaded from disk).

    labels : list[str]
        List of identity labels corresponding to each embedding in the FAISS index.

    person_folder : str
        Absolute path to the identity's dataset folder.

    Raises
    ------
    RuntimeError
        If any directory or file operations fail.
    """
    try:
        # Ensure all directories exist
        os.makedirs(DATASET_DIR, exist_ok=True)
        os.makedirs(os.path.dirname(FAISS_INDEX_PATH), exist_ok=True)
        person_folder = os.path.join(DATASET_DIR, f"id_{label_id}")
        os.makedirs(person_folder, exist_ok=True)


        # Load or initialize FAISS index and labels
        if os.path.exists(FAISS_INDEX_PATH) and os.path.exists(LABELS_PATH):
            index = faiss.read_index(FAISS_INDEX_PATH)
            with open(LABELS_PATH, "rb") as f:
                labels = pickle.load(f)
        else:
            index = faiss.IndexFlatIP(EMBEDDING_DIM)
            labels = []

        return index, labels, person_folder

    except Exception as e:
        raise RuntimeError(f"Failed to initialize identity data for '{label_id}': {e}")

def load_faiss():
    """
    Load FAISS for identity.

    Returns
    -------
    index : faiss.IndexFlatIP
        FAISS index object (either newly created or loaded from disk).

    labels : list[str]
        List of identity labels corresponding to each embedding in the FAISS index.

    Raises
    ------
    RuntimeError
        If fail to load labels or faiss.
    """
    try:
        # Load or initialize FAISS index and labels
        if os.path.exists(FAISS_INDEX_PATH) and os.path.exists(LABELS_PATH):
            index = faiss.read_index(FAISS_INDEX_PATH)
            with open(LABELS_PATH, "rb") as f:
                labels = pickle.load(f)
        else:
            raise RuntimeError("Failed to load faiss and labels because it is not created yet.")

        return index, labels

    except Exception as e:
        raise RuntimeError(f"Failed to load faiss and labels: {e}")

async def read_image(image: UploadFile) -> np.ndarray | None:
    """
    Reads and decodes an image from an UploadFile object.

    Parameters
    ----------
    image : UploadFile
        The uploaded image file.

    Returns
    -------
    np.ndarray | None
        Decoded image array, or None if decoding fails.
    """
    try:
        image_bytes = await image.read()
        np_arr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        return img if img is not None else None
    except Exception as e:
        print(f"[read_image] Error reading image: {e}")
        return None
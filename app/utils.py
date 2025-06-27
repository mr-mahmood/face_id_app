import os
import faiss
import pickle

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
        person_folder = os.path.join(DATASET_DIR, label_id)
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

import numpy as np
import datetime
import pickle
import faiss
import cv2
import os

from app.config import LABELS_PATH, FAISS_INDEX_PATH
from app import detect_faces, embbeding_face, crop_face, resize_face, start_add_refrence_images

def add_reference_image(image: np.ndarray, new_id: str) -> dict:
    """
    Add a single reference image for a new identity.
    
    Parameters
    ----------
    image : np.ndarray
        Input image (BGR) from camera or upload.
    
    new_id : str
        Label or name to associate with the new identity.
    
    Returns
    -------
    result : dict
        Result info (message, timings, embedding shape, etc.)
    
    Raises
    ------
    RuntimeError
        If no face or multiple faces are detected.
    """
    faiss_index, labels, new_id_folder = start_add_refrence_images(new_id)
    boxes, rec_time = detect_faces(image)

    if len(boxes) != 1:
        raise RuntimeError(f"Expected 1 face, found {len(boxes)}.")

    # === Face processing ===
    cropped_face, _ = crop_face(image, boxes[0])
    resized_face, _ = resize_face(cropped_face)

    # === Save reference image ===
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    img_name = f"{new_id}_{timestamp}.jpg"
    img_path = os.path.join(new_id_folder, img_name)
    cv2.imwrite(img_path, resized_face)
    total_reference_number = len(os.listdir(new_id_folder))

    # === Embedding + indexing ===
    embedding, emb_time = embbeding_face(resized_face)
    faiss_index.add(np.expand_dims(embedding, axis=0))
    labels.append(new_id)

    # Save updated index and labels
    faiss.write_index(faiss_index, FAISS_INDEX_PATH)
    with open(LABELS_PATH, "wb") as f:
        pickle.dump(labels, f)

    return {
        "status": "success",
        "message": f"User '{new_id}' added with 1 reference image, total reference images: {total_reference_number}",
        "label": new_id,
        "image_path": img_path,
        "rec_time": rec_time,
        "emb_time": emb_time
    }

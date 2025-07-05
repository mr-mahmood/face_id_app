import os
import time
import cv2
import numpy as np

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

from app.config import CLIENT_FOLDER
from app import detect_faces, resize_face, crop_face, faiss_search, embbeding_face

async def get_id(image: np.ndarray, organization_id: int) -> dict:
    """
    Perform complete face detection, embedding, and identity recognition pipeline.

    Parameters
    ----------
    image : np.ndarray
        Input image in BGR format. Shape: (H, W, 3), dtype: uint8.

    organization_id : int
        Organization ID to search against their specific FAISS index.

    Returns
    -------
    results : dict
        Complete recognition results containing:
        - status: str - "success" or "error"
        - message: str - Description of results or error
        - faces: list - List of face recognition results, each containing:
            - status: str - "ok" or "unconfident"
            - label: str - Predicted identity or "unknown"
            - confidence: float - Recognition confidence score
            - bounding_box: tuple - Face coordinates (x1, y1, x2, y2)
            - detection_time: str - Face detection processing time
            - embbeding_time: str - Feature extraction time
            - total_time: str - Total processing time

    Raises
    ------
    RuntimeError
        If any step in the pipeline fails.
    """
    try:

        if CLIENT_FOLDER is None:
            raise ValueError("CLIENT_FOLDER is not set or is None")
        
        faiss_path = os.path.join(CLIENT_FOLDER, str(organization_id), "weights", f"client_{organization_id}.faiss")
        label_path = os.path.join(CLIENT_FOLDER, str(organization_id), "weights", f"client_{organization_id}.pkl")

        boxes, detect_time = detect_faces(image)
        if len(boxes) == 0:
            return {
                "status": "error",
                "message": "No faces detected in image.",
                "faces": [],
            }

        all_result = []
        for box in boxes:
            start_total = time.time()
            x1, y1, x2, y2 = map(int, box)
            cropped_face, _ = crop_face(image, box)
            resized_face, _ = resize_face(cropped_face, (112, 112))
            embedding, emb_time = embbeding_face(resized_face)
            result = await faiss_search(embedding, faiss_path, label_path)
            total_time = (time.time() - start_total) * 1000
            total_time += detect_time
            result.update({
                "bounding_box": (x1, y1, x2, y2),
                "detection_time": f"{detect_time:.2f} ms",
                "embbeding_time": f"{emb_time:.2f} ms",
                "total_time": f"{total_time:.2f} ms"
            })
            all_result.append(result)

        return {
            "status": "success",
            "message": f"{len(boxes)} face(s) processed.",
            "faces": all_result
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Unhandled error during face recognition: {str(e)}",
            "faces": []
        }
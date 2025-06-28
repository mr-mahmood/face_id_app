import os
import time
import cv2
import numpy as np

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
from app import detect_faces, resize_face, crop_face, faiss_search, embbeding_face

def get_id(image: np.ndarray) -> dict:
    """
    Perform face detection, embedding, and identity recognition on a given image.

    Parameters
    ----------
    image : np.ndarray
        Input image in BGR format as read by OpenCV.

    Returns
    -------
    result : dict
        Recognition result for the most confident face detected. Contains:
            - label: str - predicted identity or 'unknown'
            - confidence: float - scaled vote score
            - vote_ratio: float - top label score over total
            - mean_distance: float - avg. distance to top_k neighbors
            - faiss_time: float - time taken for FAISS search (ms)
            - detect_time: float - time taken for YOLO detection (ms)
            - emb_time: float - time taken for embedding (ms)
            - total_time: float - total time for processing (ms)
            - status: str - ok / error
    """
    try:
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
            resized_face, _ = resize_face(cropped_face)
            embedding, emb_time = embbeding_face(resized_face)
            result = faiss_search(embedding)
            total_time = (time.time() - start_total) * 1000
            result.update({
                "bounding_box": (x1, y1, x2, y2),
                "detect_time": detect_time / len(boxes),
                "emb_time": emb_time,
                "total_time": total_time
            })
            all_result.append(result)

        return {
            "status": "ok",
            "message": f"{len(boxes)} face(s) processed.",
            "faces": all_result
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Unhandled error during face recognition: {str(e)}",
            "faces": all_result
        }
from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import JSONResponse
import faiss
import pickle
import datetime
import numpy as np
import cv2
import os

from app.config import CLIENT_FOLDER
from app import detect_faces, embbeding_face, crop_face, resize_face, load_faiss, read_image
from api.models import Enroll
from database.connection import get_pool

router = APIRouter()

@router.post("/enroll_refrence_iamge", response_model=Enroll)
async def identify_image(
    organization_name: str = Form(...),
    identity_name: str = Form(...),
    image: UploadFile = File(...)
):
    """
    Enroll a reference image for an existing identity in the organization.

    This endpoint adds a reference image for an existing identity to improve
    face recognition accuracy. It validates the organization and identity exist,
    processes the image through face detection and embedding, and updates the
    organization's FAISS index with the new reference.

    Parameters
    ----------
    organization_name : str
        Name of the organization the identity belongs to.
    
    identity_name : str
        Full name of the identity to add reference image for.
    
    image : UploadFile
        Reference image containing exactly one face. Supported formats: JPEG, PNG.

    Returns
    -------
    Enroll
        Response containing:
        - status: str - "success" or "error"
        - message: str - Description of enrollment result or error details

    Raises
    ------
    HTTPException
        If organization or identity not found, or image processing fails.
    """
    if not CLIENT_FOLDER:
        raise ValueError("CLIENT_FOLDER is not set or is None")

    pool = await get_pool()
    if pool is None:
        raise ValueError("Database connection pool is not available")

    async with pool.acquire() as conn:
        row = await conn.fetchrow("""
            SELECT id
            FROM clients
            WHERE organization_name = $1
        """, organization_name)
    
    if row is None:
        return JSONResponse(status_code=400, content={
            "status": "error",
            "message": f"organization '{organization_name}' is not enrolled, please enroll organization and then try again",
        })
    organization_id = int(row["id"])

    async with pool.acquire() as conn:
        row = await conn.fetchrow("""
            SELECT id
            FROM identities
            WHERE full_name = $1 and client_id = $2
        """, identity_name, organization_id)
    
    if row is None:
        return JSONResponse(status_code=400, content={
            "status": "error",
            "message": f"identity '{identity_name}' is not in organization '{organization_name}'.",
            "faces": []
        })
    identity_id = row["id"]

    img = await read_image(image)
    if img is None:
        return JSONResponse(status_code=400, content={
            "status": "error",
            "message": "Failed to decode the image. File may be corrupted or unsupported.",
            "faces": []
        })

    try:
        if CLIENT_FOLDER is None:
            raise ValueError("CLIENT_FOLDER environment variable is not set")
        
        faiss_path = os.path.join(CLIENT_FOLDER, str(organization_id), "weights", f"client_{organization_id}.faiss")
        label_path = os.path.join(CLIENT_FOLDER, str(organization_id), "weights", f"client_{organization_id}.pkl")
        faiss_index, labels = load_faiss(faiss_path, label_path)
        boxes, rec_time = detect_faces(img)

        if len(boxes) != 1:
            return {
                "status": "error",
                "message": f"Expected 1 face, but found {len(boxes)}",
                "label": identity_name
            }

        # === Face preprocessing ===
        box = boxes[0]
        x1, y1, x2, y2 = map(int, box)
        cropped_face, _ = crop_face(img, box)
        resized_face, _ = resize_face(cropped_face)

        # === Save reference image ===
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S-%f")
        img_name = f"{timestamp}.jpg"
        img_path = os.path.join(CLIENT_FOLDER, str(organization_id), "images", str(identity_id), img_name)
        cv2.imwrite(img_path, resized_face)

        # === Embedding and Indexing ===
        embedding, emb_time = embbeding_face(resized_face)
        faiss_index.add(x=np.expand_dims(embedding, axis=0))
        labels.append(identity_id)

        faiss.write_index(faiss_index, faiss_path)
        with open(label_path, "wb") as f:
            pickle.dump(labels, f)

        return Enroll(
            status="success",
            message=f"User '{identity_name}' enrolled successfully.",
        )

    except Exception as e:
        return {
            "status": "failed",
            "message": f"Enrollment failed: {e}",
            "label": identity_name
        }

from fastapi import APIRouter, UploadFile, File, Form, Header
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
from fastapi import APIRouter, UploadFile, Form, Request, Depends, Header
from api.utils import get_organization_name_from_request
from api.dependencies import get_api_key

router = APIRouter()

@router.post("/enroll_refrence_iamge", response_model=Enroll)
async def identify_image(
    request: Request,
    x_organization_id: str = Header(...),
    x_api_key: str = Depends(get_api_key),
    identity_name: str = Form(...),
    image: UploadFile = File(...)
):
    """
    Enroll a reference image for an existing identity with face detection and FAISS indexing.

    This endpoint adds a reference image for an existing identity to improve face recognition
    accuracy. It validates the organization and identity exist, processes the image through
    face detection and embedding, and updates the organization's FAISS index with the new
    reference. API key authentication is required to ensure only authorized organizations
    can add reference images.

    Parameters
    ----------
    x_api_key : str
        API key for authentication. Must match the organization's active API key.
    
    organization_id : str
        UUID of the organization the identity belongs to.
    
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
        If API key is invalid, organization or identity not found, organization is inactive,
        image contains wrong number of faces, or image processing fails.
    
    Notes
    -----
    - API key must be provided in the X-API-Key header
    - Organization must be active (is_active = True) to add reference images
    - Image must contain exactly one face for enrollment
    - Face is automatically cropped, resized, and embedded using ML models
    - Reference image is saved with timestamp in organization's image directory
    - FAISS index is updated with new face embedding for faster recognition
    - Processing includes face detection, cropping, resizing, and embedding generation
    """
    pool = await get_pool()
    if pool is None:
        raise ValueError("Database connection pool is not available")

    # API key validation is now handled by middleware
    # Get organization name from request state (set by middleware)
    organization_name = get_organization_name_from_request(request)

    async with pool.acquire() as conn:
        row = await conn.fetchrow("""
            SELECT id
            FROM identities
            WHERE full_name = $1 and client_id = $2
        """, identity_name, x_organization_id)
    
    if row is None:
        return JSONResponse(status_code=400, content={
            "status": "error",
            "message": f"identity '{identity_name}' is not enrolled in organization '{organization_name}'.",
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
        
        faiss_path = os.path.join(CLIENT_FOLDER, str(x_organization_id), "weights", f"client_{x_organization_id}.faiss")
        label_path = os.path.join(CLIENT_FOLDER, str(x_organization_id), "weights", f"client_{x_organization_id}.pkl")
        faiss_index, labels = load_faiss(faiss_path, label_path)
        boxes, rec_time = await detect_faces(img)

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
        img_path = os.path.join(CLIENT_FOLDER, str(x_organization_id), "images", str(identity_id), img_name)
        cv2.imwrite(img_path, resized_face)

        # === Embedding and Indexing ===
        embedding, emb_time = await embbeding_face(resized_face)
        faiss_index.add(x=np.expand_dims(embedding, axis=0))
        labels.append(identity_id)

        faiss.write_index(faiss_index, faiss_path)
        with open(label_path, "wb") as f:
            pickle.dump(labels, f)

        return Enroll(
            status="success",
            message=f"User '{identity_name}' reference images, enrolled successfully.",
        )

    except Exception as e:
        return {
            "status": "failed",
            "message": f"Enrollment failed: {e}",
            "label": identity_name
        }

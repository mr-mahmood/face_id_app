# api/endpoints/identify.py

from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import JSONResponse
import numpy as np
import cv2

from app import get_id, read_image
from api.models import IdentifyResponse, FaceInfo

router = APIRouter()

@router.post("/identify", response_model=IdentifyResponse)
async def identify_image(
    company_id: str = Form(...),
    camera_id: str = Form(...),
    image: UploadFile = File(...)
):
    """
    Identify faces in an uploaded image and return their associated identities.

    This endpoint accepts an image, detects all faces, extracts their embeddings, 
    and matches them against the reference database using FAISS. Returns a list 
    of identities with confidence scores and timing info per face.

    Parameters
    ----------
    company_id : str
        The identifier for the company submitting the image (for future multi-tenant support).

    camera_id : str
        Identifier of the camera from which the image was captured.

    image : UploadFile
        Image file containing one or more faces. Supported formats: JPEG, PNG.

    Returns
    -------
    IdentifyResponse
        Response model containing:
        - status: "success" or "error"
        - message: Explanation or error details
        - faces: List of detected faces with label, confidence, and processing times
    """
    img = await read_image(image)

    if img is None:
        return JSONResponse(status_code=400, content={
            "status": "error",
            "message": "Failed to decode the image. File may be corrupted or unsupported.",
            "faces": []
        })

    result = get_id(img)

    if result["status"] != "success":
        return JSONResponse(status_code=500, content=result["message"])

    face_outputs = [
        FaceInfo(
            status=face.get("status", "unknown"),
            label=face.get("label", "unknown"),
            confidence=float(face.get("confidence", 0.0)),
            detection_time=face.get("detection_time"),
            embbeding_time=face.get("embbeding_time"),
            total_time=face.get("total_time")
        ) for face in result["faces"]
    ]

    return IdentifyResponse(
        status=result["status"],
        message=result["message"],
        faces=face_outputs
    )

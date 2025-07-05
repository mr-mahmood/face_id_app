# api/endpoints/identify.py

from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import JSONResponse
import numpy as np
import cv2

from app import get_id, read_image
from api.models import IdentifyResponse, FaceInfo
from database.connection import get_pool

router = APIRouter()

@router.post("/identify", response_model=IdentifyResponse)
async def identify_image(
    organization_name: str = Form(...),
    camera_gate: str = Form(...),
    camera_roll: str = Form(...),
    image: UploadFile = File(...)
):
    """
    Identify faces in an uploaded image and log access events.

    This endpoint performs face detection, recognition, and access logging for
    a specific organization and camera location. It validates the organization
    and camera exist, processes the image through the face recognition pipeline,
    and logs successful identifications to the access logs.

    Parameters
    ----------
    organization_name : str
        Name of the organization to search against.
    
    camera_gate : str
        Gate identifier where the camera is located.
    
    camera_roll : str
        Camera role ("entry" or "exit") for access logging.
    
    image : UploadFile
        Image file containing faces to identify. Supported formats: JPEG, PNG.

    Returns
    -------
    IdentifyResponse
        Response containing:
        - status: str - "success" or "error"
        - message: str - Description of results or error details
        - faces: List[FaceInfo] - List of identified faces with confidence scores

    Raises
    ------
    HTTPException
        If organization or camera not found, or image processing fails.
    """
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
            "faces": []
        })
    organization_id = int(row["id"])

    async with pool.acquire() as conn:
        row = await conn.fetchrow("""
            SELECT id
            FROM cameras
            WHERE client_id = $1 and gate = $2 and roll = $3
        """, organization_id, camera_gate, camera_roll)
    
    if row is None:
        return JSONResponse(status_code=400, content={
            "status": "error",
            "message": f"organization '{organization_name}' don`t have any camera in gate: '{camera_gate}' for roll: '{camera_roll}'.",
            "faces": []
        })
    camera_id = row["id"]

    img = await read_image(image)
    if img is None:
        return JSONResponse(status_code=400, content={
            "status": "error",
            "message": "Failed to decode the image. File may be corrupted or unsupported.",
            "faces": []
        })

    result = await get_id(img, organization_id)
    if result["status"] != "success":
        return JSONResponse(status_code=500, content=result["message"])

    face_outputs = []
    async with pool.acquire() as conn:
        for face in result["faces"]:
            if face.get("status") == "ok":
                row = await conn.fetchrow("SELECT id FROM identities WHERE full_name = $1", face.get("label"))
                person_id = row["id"]
                info = FaceInfo(
                    status=face.get("status", "unknown"),
                    label=face.get("label", "unknown"),
                    confidence=float(face.get("confidence", 0.0)),
                    detection_time=face.get("detection_time"),
                    embbeding_time=face.get("embbeding_time"),
                    total_time=face.get("total_time")
                )
                face_outputs.append(info)
                row = await conn.execute("""
                    INSERT INTO access_logs (identity_id, camera_id, detection_confidence, processing_time_ms)
                    VALUES ($1, $2, $3, $4)
                """, person_id, camera_id, float(info.confidence), float(info.total_time.split(' ')[0]))

    return IdentifyResponse(
        status=result["status"],
        message=result["message"],
        faces=face_outputs
    )

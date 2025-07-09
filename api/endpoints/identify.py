from fastapi import APIRouter, UploadFile, File, Form, Header
from fastapi.responses import JSONResponse
from app import get_id, read_image
from api.models import IdentifyResponse, FaceInfo
from database.connection import get_pool
from fastapi import APIRouter, UploadFile, Form, Request, Depends, Header
from api.utils import get_organization_name_from_request, validate_gate_and_roll
from api.dependencies import get_api_key

router = APIRouter()

@router.post("/identify", response_model=IdentifyResponse)
async def identify_image(
    request: Request,
    x_organization_id: str = Header(...),
    x_api_key: str = Depends(get_api_key),
    camera_gate: str = Form(...),
    camera_roll: str = Form(...),
    image: UploadFile = File(...)
):
    """
    Identify faces in an uploaded image and log access events with API key authentication.

    This endpoint performs face detection, recognition, and access logging for a specific
    organization and camera location. It validates the organization and camera exist,
    processes the image through the face recognition pipeline, and logs successful
    identifications to the access logs. API key authentication is required to ensure
    only authorized organizations can perform identification.

    Parameters
    ----------
    x_api_key : str
        API key for authentication. Must match the organization's active API key.
    
    organization_id : str
        UUID of the organization to search against.
    
    camera_gate : str
        Gate identifier where the camera is located. Will be converted to lowercase.
    
    camera_roll : str
        Camera role ("entry" or "exit") for access logging. Will be converted to lowercase.
    
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
        If API key is invalid, organization doesn't exist, organization is inactive,
        camera not found, or image processing fails.
    
    Notes
    -----
    - API key must be provided in the X-API-Key header
    - Organization must be active (is_active = True) to perform identification
    - Camera must be enrolled for the specified organization, gate, and role
    - Face recognition uses FAISS index for fast similarity search
    - Access logs are automatically created for each identified face
    - Processing includes face detection, embedding, and similarity matching
    - Confidence scores and processing times are recorded for each face
    """
    # Validate gate and roll
    is_valid, error_message = validate_gate_and_roll(camera_gate, camera_roll)
    if not is_valid:
        return JSONResponse(status_code=400, content={
            "status": "error",
            "message": error_message,
            "faces": []
        })
    camera_gate = camera_gate.lower()
    camera_roll = camera_roll.lower()
    pool = await get_pool()
    if pool is None:
        raise ValueError("Database connection pool is not available")

    # API key validation is now handled by middleware
    # Get organization name from request state (set by middleware)
    organization_name = get_organization_name_from_request(request)
    
    async with pool.acquire() as conn:
        row = await conn.fetchrow("""
            SELECT id
            FROM cameras
            WHERE client_id = $1 and gate = $2 and roll = $3
        """, x_organization_id, camera_gate, camera_roll)
    
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

    result = await get_id(img, x_organization_id)
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

from typing import Optional
from fastapi import APIRouter, Form, Header
from fastapi.responses import JSONResponse
from api.models import Enroll
from database.connection import get_pool

router = APIRouter()

@router.post("/enroll_camera", response_model=Enroll)
async def enroll_identity(
    x_api_key: str = Header(...),
    organization_id: str = Form(...),
    gate: str = Form(...),
    roll: str = Form(...),
    location: Optional[str] = Form(None),
):
    """
    Enroll a camera for an organization at a specific gate and role with API key authentication.

    This endpoint creates a new camera record in the database for a specific organization,
    gate, and role (entry/exit). The camera can then be used for face identification and
    access logging. API key authentication is required to ensure only authorized
    organizations can enroll cameras.

    Parameters
    ----------
    x_api_key : str
        API key for authentication. Must match the organization's active API key.
    
    organization_id : str
        UUID of the organization the camera belongs to.
    
    gate : str
        Gate identifier where the camera is located (e.g., "Main Gate", "North Gate").
        Will be converted to lowercase.
    
    roll : str
        Camera role, must be either "entry" or "exit". Will be converted to lowercase.
    
    location : str, optional
        Physical location description of the camera. Default: None.

    Returns
    -------
    Enroll
        Response containing:
        - status: str - "success" or "error"
        - message: str - Description of enrollment result or error details

    Raises
    ------
    HTTPException
        If API key is invalid, organization doesn't exist, organization is inactive,
        camera already exists, or database operation fails.
    
    Notes
    -----
    - API key must be provided in the X-API-Key header
    - Organization must be active (is_active = True) to enroll cameras
    - Gate and roll are converted to lowercase for consistency
    - Camera uniqueness is enforced per organization, gate, and role combination
    """
    try:
        pool = await get_pool()
        gate = gate.lower()
        roll = roll.lower()
        if pool is None:
            raise ValueError("Database connection pool is not available")

        async with pool.acquire() as conn:
            row = await conn.fetchrow("""
                SELECT organization_name
                FROM clients 
                WHERE id = $1
            """, organization_id)

        if row is None:
            return JSONResponse(status_code=400, content={
                "status": "error",
                "message": f"organization '{organization_id}' is not enrolled, please enroll organization and then try enroll cameras for that organization",
            })
        organization_name = row["organization_name"]

        async with pool.acquire() as conn:
            row = await conn.fetchrow("""
                SELECT api_key, is_active
                FROM api_keys
                WHERE client_id = $1
                """, organization_id)

        if row is None:
            return JSONResponse(status_code=400, content={
                "status": "error",
                "message": f"organization '{organization_name}' is not enrolled, please enroll organization and then try enroll cameras for that organization",
            })
        
        if row["api_key"] != x_api_key: 
            return JSONResponse(status_code=400, content={
                "status": "error",
                "message": f"invalid api key, please use the correct api key for organization '{organization_name}'",
            })

        if row["is_active"] == False:
            return JSONResponse(status_code=400, content={
                "status": "error",
                "message": f"organization '{organization_name}' is not active, please activate organization and then try enroll cameras for that organization",
            })
        
        async with pool.acquire() as conn:
            row = await conn.fetchrow("""
                SELECT id 
                FROM cameras 
                WHERE client_id = $1 and gate = $2 and roll = $3
            """, organization_id, gate, roll)
        
        if row is not None:
            return JSONResponse(status_code=400, content={
                "status": "error",
                "message": f"this camera in gate: '{gate}' for roll: '{roll}' is already enrolled for organization '{organization_name}'.",
            })

        async with pool.acquire() as conn:
            row = await conn.fetchrow("""
                INSERT INTO cameras (roll, client_id, gate, camera_location)
                VALUES ($1, $2, $3, $4)
                RETURNING id
            """, roll, organization_id, gate, location)

        return Enroll(
            status="success",
            message=f"camera in gate: '{gate}' for roll: '{roll}', enrolled for organization '{organization_name}'.",
        )

    except Exception as e:
        return JSONResponse(status_code=500, content={
            "status": "error",
            "message": f"Internal server error during enrollment: {e}",
        })

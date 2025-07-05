from typing import Optional
from fastapi import APIRouter, Form
from fastapi.responses import JSONResponse
from api.models import Enroll
from database.connection import get_pool

router = APIRouter()

@router.post("/enroll_camera", response_model=Enroll)
async def enroll_identity(
    organization_name: str = Form(...),
    gate: str = Form(...),
    roll: str = Form(...),
    location: Optional[str] = Form(None),
):
    """
    Enroll a camera for an organization at a specific gate and role.

    This endpoint creates a new camera record in the database for a specific
    organization, gate, and role (entry/exit). The camera can then be used
    for face identification and access logging.

    Parameters
    ----------
    organization_name : str
        Name of the organization the camera belongs to. Will be converted to lowercase.
    
    roll : str
        Camera role, must be either "entry" or "exit".
    
    gate : str
        Gate identifier where the camera is located (e.g., "Main Gate", "North Gate").
    
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
        If organization doesn't exist, camera already exists, or database operation fails.
    """
    try:
        organization_name = organization_name.lower()
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
                "message": f"organization '{organization_name}' is not enrolled, please enroll organization and then try enroll cameras for that organization",
            })
        organization_id = str(row["id"])
        
        async with pool.acquire() as conn:
            row = await conn.fetchrow("""
                SELECT id 
                FROM cameras 
                WHERE client_id = $1 and gate = $2 and roll = $3
            """, int(organization_id), gate, roll)
        
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
            """, roll, int(organization_id), gate, location)

        return Enroll(
            status="success",
            message=f"camera in gate: '{gate}' for roll: '{roll}', enrolled for organization '{organization_name}'.",
        )

    except Exception as e:
        return JSONResponse(status_code=500, content={
            "status": "error",
            "message": "Internal server error during enrollment.",
        })

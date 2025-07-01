from typing import Optional
from fastapi import APIRouter, Form
from fastapi.responses import JSONResponse
from api.models import Enroll
from database.connection import get_pool

router = APIRouter()

@router.post("/enroll_camera", response_model=Enroll)
async def enroll_identity(
    organization_name: str = Form(...),
    roll: str = Form(...),
    gate: str = Form(...),
    location: Optional[str] = Form(None),
):
    """
    Enroll a face image for a given identity.

    This endpoint receives a face image and an identity ID, processes the image 
    (detects face, extracts embedding), and stores it as a reference for later 
    identification.

    Parameters
    ----------
    id : str
        The identifier to associate with the uploaded face image.
        Example: "id_mahmood"

    image : UploadFile
        The image file containing a face to enroll.
        Supported formats: JPEG, PNG.

    Returns
    -------
    EnrollResponse : dict
        A response indicating success or failure:
        - status: "success" or "error"
        - message: Explanation of the result
    """
    try:
        organization_name = organization_name.lower()
        pool = await get_pool()

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
        print(e)
        return JSONResponse(status_code=500, content={
            "status": "error",
            "message": "Internal server error during enrollment.",
        })

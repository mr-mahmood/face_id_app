import os
from fastapi import APIRouter, Form
from fastapi.responses import JSONResponse
from app.config import CLIENT_FOLDER
from api.models import Enroll
from database.connection import get_pool

router = APIRouter()

@router.post("/enroll_identity", response_model=Enroll)
async def enroll_identity(
    identity_name: str = Form(...),
    organization_name: str = Form(...),
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
                "message": f"organization '{organization_name}' is not enrolled, please enroll organization and then try enroll identities of that organization",
            })
        organization_id = str(row["id"])
        
        async with pool.acquire() as conn:
            row = await conn.fetchrow("""
                SELECT id 
                FROM identities 
                WHERE full_name = $1
            """, identity_name)
        
        if row is not None:
            return JSONResponse(status_code=400, content={
                "status": "error",
                "message": f"Identity '{identity_name}' is already enrolled for organization '{organization_name}'.",
            })

        async with pool.acquire() as conn:
            row = await conn.fetchrow("""
                INSERT INTO identities (client_id, full_name)
                VALUES ($1, $2)
                RETURNING id
            """, int(organization_id), identity_name)

        identity_id = str(row["id"])
        os.makedirs(os.path.join(CLIENT_FOLDER, organization_id, "images", identity_id), exist_ok=True)

        return Enroll(
            status="success",
            message=f"identity '{identity_name}' enrolled for organization '{organization_name}'.",
        )

    except Exception as e:
        print(e)
        return JSONResponse(status_code=500, content={
            "status": "error",
            "message": "Internal server error during enrollment.",
        })

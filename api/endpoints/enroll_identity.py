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
    Enroll a new identity/person in an organization for face recognition.

    This endpoint creates a new identity record in the database for a specific
    organization and sets up the directory structure for storing reference images
    for that identity. The identity can then be used for face recognition.

    Parameters
    ----------
    identity_name : str
        Full name of the person to enroll in the organization.
    
    organization_name : str
        Name of the organization the identity belongs to. Will be converted to lowercase.

    Returns
    -------
    Enroll
        Response containing:
        - status: str - "success" or "error"
        - message: str - Description of enrollment result or error details

    Raises
    ------
    HTTPException
        If organization doesn't exist, identity already exists, or database operation fails.
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
                "message": f"organization '{organization_name}' is not enrolled, please enroll organization and then try enroll identities of that organization",
            })
        organization_id = str(row["id"])
        
        async with pool.acquire() as conn:
            row = await conn.fetchrow("""
                SELECT id 
                FROM identities 
                WHERE full_name = $1 and client_id = $2
            """, identity_name, int(organization_id))
        
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
        if CLIENT_FOLDER is None:
            raise ValueError("CLIENT_FOLDER environment variable is not set")
        
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

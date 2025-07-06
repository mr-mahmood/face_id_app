import os
from fastapi import APIRouter, Form, Header
from fastapi.responses import JSONResponse
from app.config import CLIENT_FOLDER
from api.models import Enroll
from database.connection import get_pool

router = APIRouter()

@router.post("/enroll_identity", response_model=Enroll)
async def enroll_identity(
    x_api_key: str = Header(...),
    organization_id: str = Form(...),
    identity_name: str = Form(...),
):
    """
    Enroll a new identity/person in an organization for face recognition with API key authentication.

    This endpoint creates a new identity record in the database for a specific organization
    and sets up the directory structure for storing reference images for that identity.
    The identity can then be used for face recognition. API key authentication is required
    to ensure only authorized organizations can enroll identities.

    Parameters
    ----------
    x_api_key : str
        API key for authentication. Must match the organization's active API key.
    
    organization_id : str
        UUID of the organization the identity belongs to.
    
    identity_name : str
        Full name of the person to enroll in the organization.

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
        identity already exists, or database operation fails.
    
    Notes
    -----
    - API key must be provided in the X-API-Key header
    - Organization must be active (is_active = True) to enroll identities
    - Identity names are case-sensitive and must be unique per organization
    - Directory structure is created automatically for storing reference images
    - Identity uniqueness is enforced per organization
    """
    try:
        pool = await get_pool()
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
                "message": f"organization '{organization_id}' is not enrolled, please enroll organization and then try enroll identities for that organization",
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
                "message": f"organization '{organization_name}' is not enrolled, please enroll organization and then try enroll identities for that organization",
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
                FROM identities 
                WHERE full_name = $1 and client_id = $2
            """, identity_name, organization_id)
        
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
            """, organization_id, identity_name)

        identity_id = row["id"]
        if CLIENT_FOLDER is None:
            raise ValueError("CLIENT_FOLDER environment variable is not set")
        os.makedirs(os.path.join(CLIENT_FOLDER, str(organization_id), "images", str(identity_id)), exist_ok=True)
        return Enroll(
            status="success",
            message=f"Identity '{identity_name}' enrolled for organization '{organization_name}'.",
        )

    except Exception as e:
        return JSONResponse(status_code=500, content={
            "status": "error",
            "message": f"Internal server error during enrollment: {e}",
        })

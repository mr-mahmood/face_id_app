import os
from fastapi.responses import JSONResponse
from app.config import CLIENT_FOLDER
from api.models import Enroll
from database.connection import get_pool
from fastapi import APIRouter, Form, Request, Depends, Header
from api.utils import get_organization_name_from_request
from api.dependencies import get_api_key

router = APIRouter()

@router.post("/enroll_identity", response_model=Enroll)
async def enroll_identity(
    request: Request,
    x_organization_id: str = Header(...),
    x_api_key: str = Depends(get_api_key),
    identity_name: str = Form(...),
):
    """
    Enroll a new identity/person in an organization for face recognition.

    This endpoint creates a new identity record in the database for a specific organization
    and sets up the directory structure for storing reference images for that identity.
    The identity can then be used for face recognition. API key authentication is handled
    by middleware to ensure only authorized organizations can enroll identities.

    Parameters
    ----------
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
        If organization doesn't exist, identity already exists, or database operation fails.
    
    Notes
    -----
    - API key authentication is handled automatically by middleware
    - API key must be provided in the X-API-Key header
    - Organization must be active (is_active = True) to enroll identities
    - Identity names are case-sensitive and must be unique per organization
    - Directory structure is created automatically for storing reference images
    - Identity uniqueness is enforced per organization
    """
    try:
        pool = await get_pool()
        if pool is None:
            raise ValueError("Database pool is not initialized")
        
        # API key validation is now handled by middleware
        # Get organization name from request state (set by middleware)
        organization_name = get_organization_name_from_request(request)

        async with pool.acquire() as conn:
            row = await conn.fetchrow("""
                SELECT id 
                FROM identities 
                WHERE full_name = $1 and client_id = $2
            """, identity_name, x_organization_id)
        
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
            """, x_organization_id, identity_name)

        identity_id = row["id"]
        if CLIENT_FOLDER is None:
            raise ValueError("CLIENT_FOLDER environment variable is not set")
        os.makedirs(os.path.join(CLIENT_FOLDER, str(x_organization_id), "images", str(identity_id)), exist_ok=True)
        return Enroll(
            status="success",
            message=f"Identity '{identity_name}' enrolled for organization '{organization_name}'.",
        )

    except Exception as e:
        return JSONResponse(status_code=500, content={
            "status": "error",
            "message": f"Internal server error during enrollment: {e}",
        })

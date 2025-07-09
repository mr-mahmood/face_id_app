from fastapi import APIRouter, Header
from fastapi.responses import JSONResponse
from api.models.enroll import OrganizationEnroll
from database.connection import get_pool
from fastapi import APIRouter, UploadFile, Form, Request, Depends, Header
from api.utils import get_organization_name_from_request
from api.dependencies import get_api_key
import secrets
import hashlib
import secrets
import hashlib
from uuid import UUID

def __hash_api_key(api_key):
    return hashlib.sha256(api_key.encode()).hexdigest()

def __generate_api_key():
    api_key = secrets.token_urlsafe(32)
    return api_key, __hash_api_key(api_key)

router = APIRouter()

@router.post("/api_key_rotation", response_model=OrganizationEnroll)
async def identify_image(
    request: Request,
    x_organization_id: str = Header(...),
    x_api_key: str = Depends(get_api_key)
):
    """
    Enroll a new organization/client in the face recognition system with API key generation.

    This endpoint creates a new organization record in the database, generates a secure
    API key for authentication, and sets up the necessary directory structure for storing
    organization-specific data including FAISS indices, reference images, and weights.
    The API key is required for all subsequent API calls to access organization-specific
    functionality.

    Parameters
    ----------
    organization_name : str
        Name of the organization to enroll. Will be converted to lowercase for consistency.

    Returns
    -------
    OrganizationEnroll
        Response containing:
        - status: str - "success" or "error"
        - message: str - Description of enrollment result or error details
        - client_id: str - UUID of the created organization
        - api_key: str - Generated API key for authentication (format: URL-safe base64)

    Raises
    ------
    HTTPException
        If organization already exists, database operation fails, or environment setup fails.
    
    Notes
    -----
    - The API key is generated using secrets.token_urlsafe(32) for security
    - Organization names are stored in lowercase for consistency
    - Directory structure is created automatically for storing face recognition data
    - If organization already exists, returns existing client_id with "unavailable" api_key
    """
    try:
        organization_name = get_organization_name_from_request(request)

        pool = await get_pool()
        if pool is None:
            raise ValueError("Database connection pool is not available")
    
        old_hashed_api_key = __hash_api_key(x_api_key)
        api_key, hashed_api_key = __generate_api_key()
        async with pool.acquire() as conn:
            await conn.execute("""
                UPDATE api_keys
                SET is_active = false, last_used = CURRENT_TIMESTAMP
                WHERE client_id = $1 AND api_key = $2 AND is_active = true
            """, x_organization_id, old_hashed_api_key)

        async with pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO api_keys (client_id, api_key)
                VALUES ($1, $2)
            """, x_organization_id, hashed_api_key)

        return OrganizationEnroll(
            status="success",
            message=f"Client '{organization_name}' get new api key.",
            organization_id=UUID(x_organization_id),
            api_key=api_key,
        )

    except Exception as e:
        print(e)
        return JSONResponse(status_code=500, content={
            "status": "error",
            "message": "Internal server error during enrollment.",
        })
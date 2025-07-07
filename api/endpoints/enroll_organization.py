import os
import hashlib
import secrets
from fastapi import APIRouter, Form
from fastapi.responses import JSONResponse
from api.models import OrganizationEnroll
from database.connection import get_pool
from app.config import CLIENT_FOLDER

def __hash_api_key(api_key):
    return hashlib.sha256(api_key.encode()).hexdigest()

def __generate_api_key():
    api_key = secrets.token_urlsafe(32)
    return api_key, __hash_api_key(api_key)

router = APIRouter()

@router.post("/enroll_organization", response_model=OrganizationEnroll)
async def enroll_client(
    organization_name: str = Form(...),
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
        name = organization_name.lower()
        pool = await get_pool()
        if pool is None:
            raise ValueError("Database connection pool is not available")

        async with pool.acquire() as conn:
            row = await conn.fetchrow("""
                SELECT id 
                FROM clients 
                WHERE organization_name = $1
            """, name)

        if row:
            return OrganizationEnroll(
                status="error",
                message=f"client '{name}' already exist",
                client_id=row["id"],
                api_key="unavailable",
            )
    
        async with pool.acquire() as conn:
            row = await conn.fetchrow("""
                INSERT INTO clients (organization_name) 
                VALUES ($1)
                RETURNING id
            """, name)

        client_id = row["id"]

        api_key, hashed_api_key = __generate_api_key()
        async with pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO api_keys (client_id, api_key)
                VALUES ($1, $2)
            """, client_id, hashed_api_key)

        if CLIENT_FOLDER is None:
            raise ValueError("CLIENT_FOLDER environment variable is not set")
        
        os.makedirs(os.path.join(CLIENT_FOLDER, str(client_id)), exist_ok=True)
        os.makedirs(os.path.join(CLIENT_FOLDER, str(client_id), "weights"), exist_ok=True)
        os.makedirs(os.path.join(CLIENT_FOLDER, str(client_id), "images"), exist_ok=True)

        return OrganizationEnroll(
            status="success",
            message=f"Client '{name}' added.",
            client_id=client_id,
            api_key=api_key,
        )

    except Exception as e:
        print(e)
        return JSONResponse(status_code=500, content={
            "status": "error",
            "message": "Internal server error during enrollment.",
        })
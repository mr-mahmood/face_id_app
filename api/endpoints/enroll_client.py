import os
from fastapi import APIRouter, Form
from fastapi.responses import JSONResponse
from api.models import Enroll
from database.connection import get_pool
from app.config import CLIENT_FOLDER

router = APIRouter()

@router.post("/enroll_client", response_model=Enroll)
async def enroll_client(
    organization_name: str = Form(...),
):
    """
    Enroll a new organization/client in the face recognition system.

    This endpoint creates a new organization record in the database and sets up
    the necessary directory structure for storing organization-specific data
    including FAISS indices, reference images, and weights.

    Parameters
    ----------
    organization_name : str
        Name of the organization to enroll. Will be converted to lowercase.

    Returns
    -------
    Enroll
        Response containing:
        - status: str - "success" or "error"
        - message: str - Description of enrollment result or error details

    Raises
    ------
    HTTPException
        If organization already exists or database operation fails.
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
            return Enroll(
                status="error",
                message=f"client '{name}' already exist",
            )
    
        async with pool.acquire() as conn:
            row = await conn.fetchrow("""
                INSERT INTO clients (organization_name) 
                VALUES ($1)
                RETURNING id
            """, name)

        client_id = str(row["id"])
        if CLIENT_FOLDER is None:
            raise ValueError("CLIENT_FOLDER environment variable is not set")
        
        os.makedirs(os.path.join(CLIENT_FOLDER, client_id), exist_ok=True)
        os.makedirs(os.path.join(CLIENT_FOLDER, client_id, "weights"), exist_ok=True)
        os.makedirs(os.path.join(CLIENT_FOLDER, client_id, "images"), exist_ok=True)

        return Enroll(
            status="success",
            message=f"Client '{name}' added.",
        )

    except Exception as e:
        print(e)
        return JSONResponse(status_code=500, content={
            "status": "error",
            "message": "Internal server error during enrollment.",
        })
  
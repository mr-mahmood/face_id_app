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
    Enroll a client.

    This endpoint receives a client name and stores it as a clients for later identification.

    Parameters
    ----------
    name : str
        The client company name.
        Example: "university of tehran"

    Returns
    -------
    EnrollClientesponse : dict
        A response indicating success or failure:
        - status: "success" or "error"
        - message: Explanation of the result
    """
    try:
        name = organization_name.lower()
        pool = await get_pool()
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
  
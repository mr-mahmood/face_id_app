from fastapi import APIRouter

from api.models import ClientsInfoResponse
from database.connection import get_pool
from fastapi.responses import JSONResponse

router = APIRouter()

@router.get("/admin/clients", response_model=ClientsInfoResponse)
async def get_all_clients():
    """
    Retrieve all enrolled organizations/clients from the database.

    This endpoint fetches all organization records from the database and returns
    them in a standardized format. Used for administrative purposes to view
    all organizations in the system.

    Returns
    -------
    ClientsInfoResponse
        Response containing:
        - status: str - "success"
        - clients: List[dict] - List of all organizations with their details

    Raises
    ------
    HTTPException
        If database connection fails or query execution fails.
    """
    pool = await get_pool()
    if pool is None:
        raise ValueError("Database connection pool is not available")

    async with pool.acquire() as conn:
        row = await conn.fetch("""
            SELECT *
            FROM clients
        """)

    all_clients = []
    for client in row:
        temp = {}
        for i,j in client.items():
            temp[i] = str(j)
        all_clients.append(temp)

    return JSONResponse(status_code=200, content={
        "status": "success",
        "clients": all_clients
    })
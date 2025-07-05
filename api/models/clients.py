from pydantic import BaseModel
from typing import List

class ClientsInfoResponse(BaseModel):
    status: str                    # "success" or "error"
    clients: List[dict]          # List of recognized faces




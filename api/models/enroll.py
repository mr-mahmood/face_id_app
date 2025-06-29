from pydantic import BaseModel

class EnrollResponse(BaseModel):
    status: str                    # "ok" or "error"
    message: str                   # General description or error message


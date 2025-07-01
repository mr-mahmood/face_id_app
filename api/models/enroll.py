from pydantic import BaseModel

class Enroll(BaseModel):
    status: str                    # "success" or "error"
    message: str                   # General description or error message

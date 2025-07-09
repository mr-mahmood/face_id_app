from uuid import UUID
from pydantic import BaseModel

class Enroll(BaseModel):
    status: str                    # "success" or "error"
    message: str                   # General description or error message

class OrganizationEnroll(BaseModel):
    status: str                    # "success" or "error"
    message: str                   # General description or error message
    organization_id: UUID                 # Client ID
    api_key: str                   # API Key
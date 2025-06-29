from pydantic import BaseModel
from typing import List

class FaceInfo(BaseModel):
    status: str
    label: str
    confidence: float
    detection_time: str
    embbeding_time: str
    total_time: str

class IdentifyResponse(BaseModel):
    status: str                    # "ok" or "error"
    message: str                   # General description or error message
    faces: List[FaceInfo]          # List of recognized faces



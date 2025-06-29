# api/endpoints/identify.py

from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import JSONResponse
import numpy as np
import cv2

from app import add_reference_image, read_image
from api.models import EnrollResponse

router = APIRouter()

@router.post("/enroll", response_model=EnrollResponse)
async def enroll_image(
    id: str = Form(...),
    image: UploadFile = File(...)
):
    """
    Enroll a face image for a given identity.

    This endpoint receives a face image and an identity ID, processes the image 
    (detects face, extracts embedding), and stores it as a reference for later 
    identification.

    Parameters
    ----------
    id : str
        The identifier to associate with the uploaded face image.
        Example: "id_mahmood"

    image : UploadFile
        The image file containing a face to enroll.
        Supported formats: JPEG, PNG.

    Returns
    -------
    EnrollResponse : dict
        A response indicating success or failure:
        - status: "success" or "error"
        - message: Explanation of the result
    """


    img = await read_image(image)

    if img is None:
        return JSONResponse(status_code=400, content={
            "status": "error",
            "message": "Failed to decode the image. File may be corrupted or unsupported.",
        })

    try:
        result = add_reference_image(img, id)

        if result["status"] != "success":
            return JSONResponse(status_code=500, content={
                "status": "error",
                "message": result["message"],
            })

        return EnrollResponse(
            status=result["status"],
            message=result["message"],
        )

    except Exception as e:
        print(f"[enroll_image] Internal error: {e}")
        return JSONResponse(status_code=500, content={
            "status": "error",
            "message": "Internal server error during enrollment.",
        })

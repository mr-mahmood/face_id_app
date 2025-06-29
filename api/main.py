import os
import cv2
from fastapi import FastAPI
from api.endpoints.identify import router as identify_router
from api.endpoints.enroll import router as enroll_router

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
from app import get_id

app = FastAPI(title="Face ID API")


@app.on_event("startup")
async def startup_event():
    print("[Startup] Warming up...")
    img = cv2.imread("./tests/enroll_user_test.png")
    output = img.copy()
    results = get_id(img)
    print("[Startup] Done")


app.include_router(identify_router, prefix="/api", tags=["Identify"])
app.include_router(enroll_router, prefix="/api", tags=["Enroll"])

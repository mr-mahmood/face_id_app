import os
import cv2
from fastapi import FastAPI
from api.endpoints.identify import router as identify_router
from api.endpoints.enroll_identity import router as enroll_identities_router
from api.endpoints.enroll_client import router as enroll_client_router
from api.endpoints.enroll_camera import router as enroll_camera_router
from api.endpoints.enroll_refrence_image import router as enroll_identity_router
from api.endpoints.clients import router as client_info_router
from database.connection import get_pool

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
from app import get_id

app = FastAPI(title="Face ID API")
db_pool = None


@app.on_event("startup")
async def startup_event():
    print("[Startup] Warming up...")
    #img = cv2.imread("./tests/enroll_user_test.png")
    #output = img.copy()
    #results = get_id(img)
    global db_pool
    db_pool = await get_pool()
    print("[Startup] Done")

@app.on_event("shutdown")
async def shutdown():
    global db_pool
    if db_pool:
        await db_pool.close()

app.include_router(identify_router, prefix="/api", tags=["Identify"])
app.include_router(enroll_identities_router, prefix="/api", tags=["Enroll"])
app.include_router(enroll_client_router, prefix="/api", tags=["Enroll"])
app.include_router(enroll_camera_router, prefix="/api", tags=["Enroll"])
app.include_router(enroll_identity_router, prefix="/api", tags=["Enroll"])
app.include_router(client_info_router, prefix="/api", tags=["Admin"])


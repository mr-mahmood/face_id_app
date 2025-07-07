import os
import cv2
from fastapi import FastAPI
from api.endpoints.identify import router as identify_router
from api.endpoints.enroll_identity import router as enroll_identities_router
from api.endpoints.enroll_organization import router as enroll_organization_router
from api.endpoints.enroll_camera import router as enroll_camera_router
from api.endpoints.enroll_refrence_image import router as enroll_identity_reference_image_router
from api.endpoints.clients import router as client_info_router
from api.endpoints.model_status import router as model_status_router
from database.connection import get_pool
from api.middleware import api_key_middleware

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
from app import get_id

app = FastAPI(title="Face ID API")
db_pool = None

# Add API key middleware
app.middleware("http")(api_key_middleware)


@app.on_event("startup")
async def startup_event():
    print("[Startup] Warming up...")
    global db_pool
    
    # Initialize database pool
    db_pool = await get_pool()
    
    # Initialize ML models
    from app.model_manager import initialize_models
    await initialize_models()
    
    print("[Startup] Done")

@app.on_event("shutdown")
async def shutdown():
    global db_pool
    
    # Cleanup database pool
    if db_pool:
        await db_pool.close()
    
    # Cleanup ML models
    from app.model_manager import cleanup_models
    await cleanup_models()

app.include_router(identify_router, prefix="/api", tags=["Identify"])

app.include_router(enroll_organization_router, prefix="/api", tags=["Enroll"])
app.include_router(enroll_camera_router, prefix="/api", tags=["Enroll"])
app.include_router(enroll_identities_router, prefix="/api", tags=["Enroll"])
app.include_router(enroll_identity_reference_image_router, prefix="/api", tags=["Enroll"])

app.include_router(client_info_router, prefix="/api", tags=["Admin"])

app.include_router(model_status_router, prefix="/api", tags=["System"])


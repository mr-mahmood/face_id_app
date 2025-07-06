from fastapi import APIRouter, HTTPException
from typing import Dict, Any

from app.model_manager import get_model_manager

router = APIRouter()

@router.get("/model_status")
async def get_model_status() -> Dict[str, Any]:
    """
    Get status information about loaded ML models for system monitoring.

    This endpoint retrieves comprehensive status information about the loaded
    machine learning models used for face detection and recognition. It provides
    details about model paths, device configuration, initialization status,
    and system capabilities for monitoring and debugging purposes.

    Returns
    -------
    Dict[str, Any]
        Model status information containing:
        - status: str - "success" or "error"
        - models: Dict[str, Any] - Model information including:
          - yolo_model_path: str - Path to YOLO face detection model
          - embedding_model: str - Name of face embedding model
          - device: str - Device (CPU/GPU) being used for inference
          - initialized: bool - Whether models are loaded and ready
          - cuda_available: bool - Whether CUDA is available for GPU acceleration
          - embedding_dim: int - Dimension of face embeddings
        - message: str - Description of the operation result

    Raises
    ------
    HTTPException
        If model manager is not available or model status retrieval fails.
    
    Notes
    -----
    - No authentication required (system monitoring endpoint)
    - Provides real-time status of ML model loading and configuration
    - Useful for system health monitoring and debugging
    - Returns detailed information about model paths and device configuration
    - Helps diagnose issues with model loading or GPU availability
    """
    try:
        model_manager = await get_model_manager()
        model_info = model_manager.get_model_info()
        
        return {
            "status": "success",
            "models": model_info,
            "message": "Model status retrieved successfully"
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get model status: {str(e)}"
        ) 
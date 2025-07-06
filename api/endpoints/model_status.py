from fastapi import APIRouter, HTTPException
from typing import Dict, Any

from app.model_manager import get_model_manager

router = APIRouter()

@router.get("/model_status")
async def get_model_status() -> Dict[str, Any]:
    """
    Get status information about loaded ML models.
    
    Returns
    -------
    Dict[str, Any]
        Model status information including:
        - yolo_model_path: str - Path to YOLO model
        - embedding_model: str - Name of embedding model
        - device: str - Device (CPU/GPU) being used
        - initialized: bool - Whether models are loaded
        - cuda_available: bool - Whether CUDA is available
        - embedding_dim: int - Embedding dimension
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
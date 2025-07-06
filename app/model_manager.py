import os
import time
import numpy as np
from typing import Optional, Tuple
import torch
from ultralytics import YOLO
from deepface import DeepFace

from app.config import YOLO_MODEL_PATH, EMBEDDING_MODEL, EMBEDDING_DIM
from app import normalize

class ModelManager:
    """Global model manager for YOLO and SFace models."""
    
    def __init__(self):
        """Initialize the model manager."""
        self.yolo_model: Optional[YOLO] = None
        self.embedding_model_name: Optional[str] = None
        self.device: str = "cuda" if torch.cuda.is_available() else "cpu"
        self._initialized = False
    
    async def initialize(self) -> None:
        """
        Initialize all models asynchronously.
        
        This method loads the YOLO face detection model and prepares
        the SFace embedding model for use.
        """
        if self._initialized:
            return
        
        print("[ModelManager] Initializing models...")
        
        # Load YOLO model
        await self._load_yolo_model()
        
        # Initialize embedding model
        await self._initialize_embedding_model()
        
        self._initialized = True
        print(f"[ModelManager] Models initialized successfully on {self.device}")
    
    async def _load_yolo_model(self) -> None:
        """
        Load the YOLO face detection model.
        
        Raises
        ------
        ValueError
            If YOLO_MODEL_PATH is not set or model file doesn't exist.
        RuntimeError
            If model loading fails.
        """
        if YOLO_MODEL_PATH is None:
            raise ValueError("YOLO_MODEL_PATH is not set or is None")
        
        if not os.path.exists(YOLO_MODEL_PATH):
            raise ValueError(f"YOLO model file not found: {YOLO_MODEL_PATH}")
        
        try:
            print(f"[ModelManager] Loading YOLO model from {YOLO_MODEL_PATH}")
            self.yolo_model = YOLO(YOLO_MODEL_PATH).to(self.device)
            
            # Warm up the model with a dummy inference
            dummy_image = np.random.randint(0, 255, (640, 640, 3), dtype=np.uint8)
            _ = self.yolo_model(dummy_image, verbose=False)
            
            print(f"[ModelManager] YOLO model loaded successfully on {self.device}")
        
        except Exception as e:
            raise RuntimeError(f"Failed to load YOLO model: {e}")
    
    async def _initialize_embedding_model(self) -> None:
        """
        Initialize the SFace embedding model.
        
        Raises
        ------
        ValueError
            If EMBEDDING_MODEL is not set.
        """
        if EMBEDDING_MODEL is None:
            raise ValueError("EMBEDDING_MODEL is not set or is None")
        
        self.embedding_model_name = EMBEDDING_MODEL
        print(f"[ModelManager] Embedding model initialized: {self.embedding_model_name}")
    
    def detect_faces(self, image: np.ndarray, conf_threshold: float = 0.7) -> Tuple[np.ndarray, float]:
        """
        Detect faces in an image using the loaded YOLO model.
        
        Parameters
        ----------
        image : np.ndarray
            Input image in BGR format. Shape: (H, W, 3), dtype: uint8.
        
        conf_threshold : float, optional
            Minimum confidence threshold for face detection. Default: 0.7.
        
        Returns
        -------
        boxes : np.ndarray
            Bounding boxes of detected faces. Shape: (N, 4), format: [x1, y1, x2, y2].
        
        used_time : float
            Average inference time per detected face in milliseconds.
        
        Raises
        ------
        RuntimeError
            If model is not initialized or face detection fails.
        """
        if not self._initialized or self.yolo_model is None:
            raise RuntimeError("YOLO model not initialized. Call initialize() first.")
        
        try:
            results = self.yolo_model(image, verbose=False)[0]
            all_boxes = results.boxes.xyxy.cpu().numpy()
            confidences = results.boxes.conf.cpu().numpy()
            
            # Calculate timing
            total_time = results.speed['preprocess'] + results.speed['inference'] + results.speed['postprocess']
            time_per_face = total_time / max(len(all_boxes), 1)  # Avoid division by zero
            
            # Filter by confidence
            filtered_boxes = all_boxes[confidences >= conf_threshold]
            
            return filtered_boxes, time_per_face
        
        except Exception as e:
            raise RuntimeError(f"Failed to detect faces: {e}")
    
    def generate_embedding(self, face: np.ndarray) -> Tuple[np.ndarray, float]:
        """
        Generate a normalized facial embedding using the SFace model.
        
        Parameters
        ----------
        face : np.ndarray
            A cropped face image as a NumPy array. Shape: (H, W, 3), dtype: uint8.
        
        Returns
        -------
        embedding : np.ndarray
            The L2-normalized facial embedding vector. Shape: (128,), dtype: float32.
        
        embed_time : float
            Time taken to generate the embedding in milliseconds.
        
        Raises
        ------
        RuntimeError
            If model is not initialized or embedding generation fails.
        """
        if not self._initialized or self.embedding_model_name is None:
            raise RuntimeError("Embedding model not initialized. Call initialize() first.")
        
        try:
            start_time = time.time()
            
            result = DeepFace.represent(
                img_path=face, 
                model_name=self.embedding_model_name, 
                enforce_detection=False
            )[0]
            
            embedding = normalize(np.array(result["embedding"]).astype(np.float32))
            embed_time = (time.time() - start_time) * 1000  # Convert to milliseconds
            
            return embedding, embed_time
        
        except Exception as e:
            raise RuntimeError(f"Failed to generate embedding: {e}")
    
    def get_model_info(self) -> dict:
        """
        Get information about loaded models.
        
        Returns
        -------
        dict
            Information about the loaded models including device and model names.
        """
        return {
            "yolo_model_path": YOLO_MODEL_PATH,
            "embedding_model": self.embedding_model_name,
            "device": self.device,
            "initialized": self._initialized,
            "cuda_available": torch.cuda.is_available(),
            "embedding_dim": EMBEDDING_DIM
        }
    
    async def cleanup(self) -> None:
        """Clean up model resources."""
        if self.yolo_model is not None:
            # Clear CUDA cache if using GPU
            if self.device == "cuda":
                torch.cuda.empty_cache()
            
            del self.yolo_model
            self.yolo_model = None
        
        self._initialized = False
        print("[ModelManager] Models cleaned up")

# Global model manager instance
model_manager = ModelManager()

async def initialize_models() -> None:
    """
    Initialize the global model manager.
    
    This function should be called during application startup.
    """
    await model_manager.initialize()

async def get_model_manager() -> ModelManager:
    """
    Get the global model manager instance.
    
    Returns
    -------
    ModelManager
        The global model manager instance.
    """
    if not model_manager._initialized:
        await model_manager.initialize()
    return model_manager

async def cleanup_models() -> None:
    """
    Clean up model resources.
    
    This function should be called during application shutdown.
    """
    await model_manager.cleanup() 
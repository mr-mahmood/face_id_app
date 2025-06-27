from dotenv import load_dotenv
import os

# Load .env variables once
load_dotenv()

# Constants used throughout the app
YOLO_MODEL_PATH = os.getenv("YOLO_MODEL_PATH", "app/yolo/face_detector.pt")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "SFace")
EMBEDDING_DIM = int(os.getenv("EMBEDDING_DIM", 128))
FAISS_INDEX_PATH = os.getenv("FAISS_INDEX_PATH", "embeddings/face_index.faiss")
LABELS_PATH = os.getenv("LABELS_PATH", "embeddings/labels.pkl")
DATASET_DIR = os.getenv("DATASET_DIR", "dataset/")

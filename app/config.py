from dotenv import load_dotenv
import os

# Load .env variables once
load_dotenv()

# Constants used throughout the app
YOLO_MODEL_PATH = os.getenv("YOLO_MODEL_PATH")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL")
EMBEDDING_DIM = int(os.getenv("EMBEDDING_DIM"))
FAISS_INDEX_PATH = os.getenv("FAISS_INDEX_PATH")
LABELS_PATH = os.getenv("LABELS_PATH")
DATASET_DIR = os.getenv("DATASET_DIR")
DB_URL = os.getenv("DB_URL")
CLIENT_FOLDER = os.getenv("CLIENT_FOLDER")

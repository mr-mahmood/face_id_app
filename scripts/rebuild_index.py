import os
import sys
import cv2
import faiss
import pickle
import numpy as np
from tqdm import tqdm

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.config import EMBEDDING_DIM, FAISS_INDEX_PATH, LABELS_PATH, DATASET_DIR
from app import embbeding_face

def rebuild_faiss_index():
    print("🧹 Rebuilding FAISS index from dataset...")
    
    # Initialize FAISS index and label list
    index = faiss.IndexFlatIP(EMBEDDING_DIM)
    labels = []

    # Loop over dataset folders
    identities = [d for d in os.listdir(DATASET_DIR) if os.path.isdir(os.path.join(DATASET_DIR, d))]

    for identity in tqdm(identities, desc="Processing identities"):
        person_folder = os.path.join(DATASET_DIR, identity)
        image_files = [f for f in os.listdir(person_folder) if f.lower().endswith((".jpg", ".png", ".jpeg"))]

        for img_file in image_files:
            img_path = os.path.join(person_folder, img_file)
            image = cv2.imread(img_path)

            if image is None:
                print(f"[WARN] Could not read image: {img_path}")
                continue

            try:
                embedding, _ = embbeding_face(image)
                index.add(np.expand_dims(embedding, axis=0))
                labels.append(identity)
            except Exception as e:
                print(f"[ERROR] Failed to process {img_path}: {e}")

    # Save index and labels
    os.makedirs(os.path.dirname(FAISS_INDEX_PATH), exist_ok=True)
    faiss.write_index(index, FAISS_INDEX_PATH)
    with open(LABELS_PATH, "wb") as f:
        pickle.dump(labels, f)

    print(f"✅ Rebuilt FAISS index with {len(labels)} entries from {len(identities)} identities.")


if __name__ == "__main__":
    rebuild_faiss_index()

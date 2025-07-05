import time
import numpy as np

from app import load_faiss
from database.connection import get_pool

# Define thresholds
VOTE_THRESHOLD = 0.75      # Adjust as needed
DISTANCE_THRESHOLD = 0.7  # Lower means stricter match

async def faiss_search(embedding: np.ndarray, faiss_path, label_path, top_k: int = 10) -> dict:
    """
    Perform face identity recognition using FAISS nearest neighbor search with weighted voting.

    Parameters
    ----------
    embedding : np.ndarray
        1D normalized face embedding vector. Shape: (128,), dtype: float32.
    
    faiss_path : str
        Path to the FAISS index file.
    
    label_path : str
        Path to the labels pickle file.
    
    top_k : int, optional
        Number of nearest neighbors to consider for voting. Default: 10.

    Returns
    -------
    result : dict
        Recognition result containing:
        - status: str - "ok" if confident, "unconfident" if below threshold
        - label: str - predicted identity name or "unknown"
        - confidence: float - weighted voting confidence score (0.0 - 1.0)

    Raises
    ------
    RuntimeError
        If FAISS search or voting process fails.
    """
    try:
        # Load index and labels
        faiss_index, true_labels = load_faiss(faiss_path, label_path)

        if embedding.ndim == 1:
            embedding = np.expand_dims(embedding, axis=0).astype(np.float32)

        # --- FAISS SEARCH ---
        faiss_start = time.time()
        D, I = faiss_index.search(embedding, top_k)
        faiss_time = (time.time() - faiss_start) * 1000  # ms

        top_k_indices = I[0]
        top_k_distances = D[0]

        # Guard: remove invalid indices (-1 or OOB)
        valid_entries = [(idx, dist) for idx, dist in zip(top_k_indices, top_k_distances)
                        if 0 <= idx < len(true_labels)]

        if not valid_entries:
            return {
                "status": "unconfident",
                "label": "unknown",
                "confidence": 0.0
            }

        # --- Weighted Voting ---
        label_scores = {}
        for idx, dist in valid_entries:
            label = true_labels[idx]
            score = 1 / (dist + 1e-8)
            label_scores[label] = label_scores.get(label, 0) + score

        pred_label = max(label_scores, key=label_scores.get)
        total_score = sum(label_scores.values())
        vote_ratio = label_scores[pred_label] / total_score
        mean_distance = np.mean([dist for _, dist in valid_entries])

        # --- Confidence Decision ---
        confidence = vote_ratio
        is_confident = vote_ratio >= VOTE_THRESHOLD
        pool = await get_pool()
        if pool is None:
            raise ValueError("Database connection pool is not available")
        async with pool.acquire() as conn:
            row = await conn.fetchrow("""
                SELECT full_name 
                FROM identities 
                WHERE id = $1
            """, pred_label)
            if row:
                label_text = row["full_name"]
            else:
                label_text = "unknown"

        return {
            "status": "ok" if is_confident else "unconfident",
            "label": label_text,
            "confidence": round(confidence, 3)
        }
    except Exception as e:
        raise RuntimeError(f"Failed on faiss search with error: {e}")
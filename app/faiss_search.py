import time
import numpy as np

from app import load_faiss

# Define thresholds
VOTE_THRESHOLD = 0.75      # Adjust as needed
DISTANCE_THRESHOLD = 0.7  # Lower means stricter match

def faiss_search(embedding: np.ndarray, top_k: int = 10) -> dict:
    """
    Recognize identity based on input embedding using FAISS nearest neighbors.

    Parameters
    ----------
    embedding : np.ndarray
        1D normalized face embedding vector (shape: (128,))
    
    top_k : int
        Number of nearest neighbors to consider for voting.

    Returns
    -------
    result : dict
        {

            "status": str,

            "label": str,

            "confidence": float

        }
    """
    try:
        # Load index and labels
        faiss_index, true_labels = load_faiss()

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
                "status": "no_match",
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
        
        label_text = pred_label.replace("id_", "").replace("_", " ")
        return {
            "status": "ok" if is_confident else "unconfident",
            "label": label_text,
            "confidence": round(confidence, 3)
        }
    except Exception as e:
        raise RuntimeError(f"Failed on faiss search with error: {e}")
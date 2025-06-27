import sys
import os
import time
import cv2

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

from app import detect_faces, resize_face, crop_face, faiss_search, embbeding_face

# --- Load image
img = cv2.imread("./tests/recognizer_test.jpg")
output = img.copy()  # hard copy for drawing

# --- Detect faces
boxes, detect_time = detect_faces(img)
print(f"[Detect] {len(boxes)} face(s) found in {detect_time:.2f} ms")

# --- Timings for stats
total_embedding_time = 0
total_loop_time = 0

# --- Process each face
for i, box in enumerate(boxes):
    x1, y1, x2, y2 = map(int, box)

    loop_start = time.time()

    # Crop and resize
    cropped_face, _ = crop_face(img, box)
    resized_face, _ = resize_face(cropped_face)

    # Embed
    emb, emb_time = embbeding_face(resized_face)
    total_embedding_time += emb_time

    # FAISS search
    result = faiss_search(emb)

    loop_end = (time.time() - loop_start) * 1000
    total_loop_time += loop_end

    # Format label text
    label_text = f"{result['label'].replace('id_', '').replace('_', ' ')}"
    if result.get("status") == "unconfident":
        label_text = "❓ " + label_text

    # Draw results
    cv2.rectangle(output, (x1, y1), (x2, y2), (0, 255, 0), 2)
    cv2.putText(output, label_text, (x1, max(y1 - 10, 10)),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    print(f"[Face {i+1}] Embedding: {emb_time:.2f} ms | Total loop: {loop_end:.2f} ms")

# --- Display final average stats
if len(boxes) > 0:
    print(f"\n--- Summary ---")
    print(f"Avg embedding time: {total_embedding_time / len(boxes):.2f} ms")
    print(f"Avg recognition loop time: {total_loop_time / len(boxes):.2f} ms")

# --- Display result
cv2.imshow("Recognition Result", output)
cv2.imwrite("./tests/recognizer_test_result.jpg", output)
cv2.waitKey(0)
cv2.destroyAllWindows()

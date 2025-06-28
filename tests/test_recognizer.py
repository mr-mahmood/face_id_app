import sys
import os
import time
import cv2

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

from app import get_id  # single entrypoint for recognition

# --- Load image
img = cv2.imread("./tests/recognizer_test.jpg")
output = img.copy()

# --- Call recognition pipeline
results = get_id(img)

# --- Timing summary vars
total_emb_time = 0
total_total_time = 0

for i, res in enumerate(results["faces"]):
    x1, y1, x2, y2 = res["bounding_box"]
    label = res["label"]
    label_text = label.replace("id_", "").replace("_", " ")

    # Draw results
    cv2.rectangle(output, (x1, y1), (x2, y2), (0, 255, 0), 2)
    cv2.putText(output, label_text, (x1, max(y1 - 10, 10)),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    print(f"[Face {i+1}] Label: {label_text} | emb_time: {res['emb_time']:.2f} ms | detect_time: {res['detect_time']:.2f} ms | total: {res['total_time']:.2f} ms")
    
    total_emb_time += res["emb_time"]
    total_total_time += res["total_time"]

# --- Stats summary
if results:
    print(f"\n--- Summary ---")
    print(f"Avg embedding time: {total_emb_time / len(results):.2f} ms")
    print(f"Avg total time: {total_total_time / len(results):.2f} ms")

# --- Display
cv2.imshow("Recognition Result", output)
cv2.imwrite("./tests/recognizer_test_result.jpg", output)
cv2.waitKey(0)
cv2.destroyAllWindows()

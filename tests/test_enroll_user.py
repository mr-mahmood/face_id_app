import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import cv2
import time

from app import add_reference_image

num_trials = 1000
total_latency = 0
total_rec_time = 0
total_emb_time = 0
failures = 0

async def run_tests():
    global total_latency, total_rec_time, total_emb_time, failures
    
    for i in range(num_trials):
        img = cv2.imread("./tests/enroll_user_test.png")
        try:
            start = time.time()
            result = await add_reference_image(img, "mahmood")
            end = (time.time() - start) * 1000  # ms

            if i != 0:
                total_latency += end
                total_rec_time += result["rec_time"]
                total_emb_time += result["emb_time"]
                print(f"[{i+1}] Latency: {end:.2f} ms | rec: {result['rec_time']:.2f} ms | emb: {result['emb_time']:.2f} ms")
                
        except Exception as e:
            failures += 1
            print(f"[{i+1}] ❌ Failed: {e}")

    # Averages
    successful_runs = num_trials - failures

    if successful_runs > 0:
        print("\n✅ Summary:")
        print(f"Successful Runs     : {successful_runs}")
        print(f"Failures            : {failures}")
        print(f"Avg Total Latency   : {total_latency / successful_runs:.2f} ms")
        print(f"Avg Detection Time  : {total_rec_time / successful_runs:.2f} ms")
        print(f"Avg Embedding Time  : {total_emb_time / successful_runs:.2f} ms")
    else:
        print("❌ No successful runs.")

if __name__ == "__main__":
    import asyncio
    asyncio.run(run_tests())

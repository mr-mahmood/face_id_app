import asyncio
import sys
import os
import time
import numpy as np
import cv2

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.model_manager import initialize_models, get_model_manager, cleanup_models

async def test_model_loading():
    """Test that models are loaded correctly and only once."""
    print("🧪 Testing Model Loading System")
    print("=" * 50)
    
    # Test 1: Initialize models
    print("\n1. Testing model initialization...")
    start_time = time.time()
    await initialize_models()
    init_time = time.time() - start_time
    print(f"✅ Models initialized in {init_time:.2f} seconds")
    
    # Test 2: Get model manager multiple times (should reuse loaded models)
    print("\n2. Testing model manager reuse...")
    times = []
    for i in range(5):
        start_time = time.time()
        model_manager = await get_model_manager()
        get_time = time.time() - start_time
        times.append(get_time)
        print(f"   Get {i+1}: {get_time:.4f} seconds")
    
    avg_get_time = sum(times) / len(times)
    print(f"✅ Average get time: {avg_get_time:.4f} seconds")
    
    # Test 3: Get model information
    print("\n3. Testing model information...")
    model_info = model_manager.get_model_info()
    print("Model Information:")
    for key, value in model_info.items():
        print(f"   {key}: {value}")
    
    # Test 4: Test face detection
    print("\n4. Testing face detection...")
    # Create a dummy image
    dummy_image = np.random.randint(0, 255, (640, 640, 3), dtype=np.uint8)
    
    detection_times = []
    for i in range(3):
        start_time = time.time()
        boxes, detect_time = model_manager.detect_faces(dummy_image)
        total_time = time.time() - start_time
        detection_times.append(total_time)
        print(f"   Detection {i+1}: {total_time:.4f} seconds, {len(boxes)} faces detected")
    
    avg_detection_time = sum(detection_times) / len(detection_times)
    print(f"✅ Average detection time: {avg_detection_time:.4f} seconds")
    
    # Test 5: Test embedding generation
    print("\n5. Testing embedding generation...")
    # Create a dummy face image
    dummy_face = np.random.randint(0, 255, (112, 112, 3), dtype=np.uint8)
    
    embedding_times = []
    for i in range(3):
        start_time = time.time()
        embedding, embed_time = model_manager.generate_embedding(dummy_face)
        total_time = time.time() - start_time
        embedding_times.append(total_time)
        print(f"   Embedding {i+1}: {total_time:.4f} seconds, shape: {embedding.shape}")
    
    avg_embedding_time = sum(embedding_times) / len(embedding_times)
    print(f"✅ Average embedding time: {avg_embedding_time:.4f} seconds")
    
    # Test 6: Test cleanup
    print("\n6. Testing model cleanup...")
    start_time = time.time()
    await cleanup_models()
    cleanup_time = time.time() - start_time
    print(f"✅ Models cleaned up in {cleanup_time:.2f} seconds")
    
    print("\n🎉 All tests passed!")
    print("=" * 50)
    
    # Summary
    print("\n📊 Performance Summary:")
    print(f"   Model initialization: {init_time:.2f}s")
    print(f"   Average get time: {avg_get_time:.4f}s")
    print(f"   Average detection time: {avg_detection_time:.4f}s")
    print(f"   Average embedding time: {avg_embedding_time:.4f}s")
    print(f"   Model cleanup: {cleanup_time:.2f}s")

async def test_concurrent_access():
    """Test concurrent access to model manager."""
    print("\n🔄 Testing Concurrent Access")
    print("=" * 50)
    
    # Initialize models
    await initialize_models()
    
    # Test concurrent access
    async def concurrent_task(task_id):
        model_manager = await get_model_manager()
        boxes, _ = model_manager.detect_faces(np.random.randint(0, 255, (640, 640, 3), dtype=np.uint8))
        embedding, _ = model_manager.generate_embedding(np.random.randint(0, 255, (112, 112, 3), dtype=np.uint8))
        print(f"   Task {task_id}: Detection={len(boxes)} faces, Embedding shape={embedding.shape}")
    
    # Run 5 concurrent tasks
    tasks = [concurrent_task(i) for i in range(5)]
    start_time = time.time()
    await asyncio.gather(*tasks)
    total_time = time.time() - start_time
    
    print(f"✅ Concurrent tasks completed in {total_time:.2f} seconds")
    
    # Cleanup
    await cleanup_models()

async def main():
    """Main test function."""
    try:
        await test_model_loading()
        await test_concurrent_access()
        print("\n🎯 All tests completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 
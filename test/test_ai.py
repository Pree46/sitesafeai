import cv2
import numpy as np
from app.services.stream import run_ai_task

def test_inference():
    print("Testing AI Worker Task...")
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    try:
        dets = run_ai_task(frame)
        print(f"SUCCESS! Detections count: {len(dets)}")
    except Exception as e:
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_inference()

import sys
import os
import time
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__))))

from app.geofence.engine import GeofenceEngine

def test_geofencing():
    print("Initializing GeofenceEngine (IoA threshold = 0.3)...")
    engine = GeofenceEngine(ioa_threshold=0.3)
    
    frame_shape = (480, 640, 3) # h, w, c
    
    zones_data = [
        {
            "name": "danger_zone",
            "points": [[100, 100], [300, 100], [300, 300], [100, 300]]
        }
    ]
    
    detections = [
        {"class": "person", "bbox": (150, 150, 200, 200)}, # fully inside (IoA 1.0)
        {"class": "person", "bbox": (50, 50, 150, 150)},   # 1/4 inside (IoA 0.25) -> should NOT trigger
        {"class": "person", "bbox": (80, 80, 280, 280)},   # mostly inside (IoA > 0.3) -> should trigger
        {"class": "person", "bbox": (10, 10, 50, 50)}      # outside (IoA 0.0) -> should NOT trigger
    ]
    
    print("Testing processing...")
    start_t = time.perf_counter()
    violations = engine.process(detections, frame_shape, zones_data)
    dur = (time.perf_counter() - start_t) * 1000
    print(f"Violations: {violations}")
    print(f"Processed in {dur:.2f}ms")
    
    assert "danger_zone" in violations
    assert len(violations["danger_zone"]) == 2, "Should trigger exactly 2 times (fully inside, mostly inside)"
    print("Test passed successfully!")

if __name__ == "__main__":
    test_geofencing()

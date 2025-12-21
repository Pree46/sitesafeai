from datetime import datetime
from ..services.model import CLASS_NAMES

detections_history = []

def extract_violations(results):
    violations = []
    boxes = results[0].boxes
    if boxes is not None:
        for box in boxes:
            label = CLASS_NAMES[int(box.cls)]
            if label.startswith("NO-"):
                violations.append(label)
    return list(set(violations))

def record_detection(message):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    detections_history.append(f"[{ts}] {message}")

from datetime import datetime

# Store detection history (in-memory)
detections_history = []


def extract_violations(detections):
    """
    Extract PPE violations from OpenVINO detections.

    Expected detection format:
    {
        "class": "NO-Hardhat",
        "confidence": 0.82,
        "bbox": (x1, y1, x2, y2)
    }
    """

    violations = set()

    for det in detections:
        label = det.get("class", "")
        if label.startswith("NO-"):
            violations.add(label)

    return list(violations)


def record_detection(message):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    detections_history.append(f"[{ts}] {message}")

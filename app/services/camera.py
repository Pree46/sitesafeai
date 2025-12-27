import cv2
import time

cap = None


def open_camera(src=0):
    """
    Open a fresh camera safely.
    Avoids OpenCV crash on restart (Windows-safe).
    """
    global cap

    # Release old camera if any
    if cap is not None:
        try:
            cap.release()
        except Exception:
            pass
        cap = None

    # Small delay to allow OS to release device
    time.sleep(0.2)

    cap = cv2.VideoCapture(src, cv2.CAP_DSHOW)

    if not cap.isOpened():
        cap = None
        raise RuntimeError("Webcam not accessible")

    return cap


def release_camera():
    global cap
    if cap is not None:
        try:
            cap.release()
        except Exception:
            pass
        cap = None

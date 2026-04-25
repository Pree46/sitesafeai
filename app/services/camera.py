import cv2
import time
import os
import numpy as np
import threading

cap = None
DEMO_MODE = False  # Track if using demo/fallback mode


class ThreadedCamera:
    """
    A threaded camera grabs frames continuously in the background.
    This eliminates OpenCV OS buffering which causes extreme lag
    when the AI inference loop runs slower than the camera's native FPS.
    """
    def __init__(self, src=0, is_demo=False):
        self.is_demo = is_demo
        if not is_demo:
            self.cap = cv2.VideoCapture(src, cv2.CAP_DSHOW)
            # Instruct DSHOW to drop internal buffering if possible
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        else:
            self.cap = cv2.VideoCapture(src, cv2.CAP_FFMPEG)
            
        self.ret = False
        self.frame = None
        self.running = True

        if self.cap.isOpened():
            self.ret, self.frame = self.cap.read()
            # Start daemon thread to keep consuming frames
            self.thread = threading.Thread(target=self.update, args=())
            self.thread.daemon = True
            self.thread.start()

    def update(self):
        while self.running:
            if self.cap.isOpened():
                ret, frame = self.cap.read()
                if ret:
                    self.ret = ret
                    self.frame = frame
                else:
                    # For demo videos, loop back to start if it ends
                    if self.is_demo:
                        self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            else:
                time.sleep(0.01)

    def read(self):
        # We always return the absolute latest frame fetched
        return self.ret, self.frame

    def isOpened(self):
        return self.cap.isOpened()

    def release(self):
        self.running = False
        if hasattr(self, 'thread'):
            self.thread.join(timeout=1.0)
        self.cap.release()


def open_camera(src=0):
    """
    Open a fresh camera safely with threaded optimization.
    Falls back to demo video or test pattern if no camera found.
    """
    global cap, DEMO_MODE

    # Release old camera if any
    if cap is not None:
        try:
            cap.release()
        except Exception:
            pass
        cap = None

    time.sleep(0.2)

    # Try opening native camera first using Threaded implementation directly
    try:
        temp_cap = ThreadedCamera(src, is_demo=False)
        if temp_cap.isOpened():
            DEMO_MODE = False
            print("[CAMERA] ✅ Webcam opened successfully with zero-lag Threading")
            cap = temp_cap
            return cap
        else:
            temp_cap.release()
    except Exception as e:
        print(f"[CAMERA] ⚠️ Camera error: {e}")

    # Fallback: Try demo video if camera fails
    print("[CAMERA] ⚠️ Webcam not found, trying demo video...")
    
    demo_paths = [
        "demo.mp4",
        "test.mp4",
        "sample.mp4",
        "archive/data/sample.mp4",
        "archive/data/demo.mp4",
        "../demo.mp4"
    ]
    
    for path in demo_paths:
        if os.path.exists(path):
            try:
                temp_cap = cv2.VideoCapture(path, cv2.CAP_FFMPEG)
                if temp_cap.isOpened():
                    temp_cap.release()
                    print(f"[CAMERA] 📹 Found demo video: {path}")
                    DEMO_MODE = True
                    cap = ThreadedCamera(path, is_demo=True)
                    print("[CAMERA] ✅ Threaded Demo video loaded")
                    return cap
            except:
                pass

    # Last resort: Return a dummy object that will trigger test pattern mode
    print("[CAMERA] 🎨 Using test pattern mode")
    DEMO_MODE = True
    
    class DummyCapture:
        def isOpened(self):
            return True
        def read(self):
            return False, None
        def release(self):
            pass
    
    cap = DummyCapture()
    return cap


def release_camera():
    global cap
    if cap is not None:
        try:
            cap.release()
        except Exception:
            pass
        cap = None

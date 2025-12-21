import os
import cv2
import time
import traceback
import logging
import smtplib

from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from fastapi import FastAPI, UploadFile, File, WebSocket
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from ultralytics import YOLO

# ================== APP SETUP ==================


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("sitesafeai")

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.mount("/uploads", StaticFiles(directory=UPLOAD_FOLDER), name="uploads")

@app.get("/")
def root():
    return {
        "status": "SiteSafeAI FastAPI backend running",
        "stream": "/api/stream",
        "docs": "/docs"
    }



# ================== GLOBAL STATE ==================
detections_history = []
streaming_active = False
connected_clients = []

ALERT_COOLDOWN_SECONDS = 15
last_alert_time = 0

# ================== MODEL ==================
logger.info("Loading YOLO model...")
model = YOLO("best.pt")
model.conf = 0.25
model.iou = 0.45
logger.info("YOLO model loaded")

CLASS_NAMES = [
    "Hardhat", "Mask", "NO-Hardhat", "NO-Mask",
    "NO-Safety Vest", "Person", "Safety Cone",
    "Safety Vest", "machinery", "vehicle"
]

# ================== CAMERA ==================
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

if not cap.isOpened():
    raise RuntimeError("Webcam not accessible")

# ================== HELPERS ==================
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


async def broadcast_alert(message):
    payload = {
        "message": message,
        "timestamp": datetime.now().strftime("%H:%M:%S")
    }
    for ws in connected_clients:
        await ws.send_json(payload)

# ================== STREAM ==================
def generate_frames():
    global last_alert_time

    while True:
        success, frame = cap.read()
        if not success:
            time.sleep(0.1)
            continue

        try:
            results = model(frame, verbose=False)

            if streaming_active:
                violations = extract_violations(results)
                now = time.time()

                if violations and (now - last_alert_time) > ALERT_COOLDOWN_SECONDS:
                    msg = f"Violation detected: {', '.join(violations)}"
                    record_detection(msg)
                    last_alert_time = now

                    import asyncio
                    asyncio.run(broadcast_alert(msg))

            annotated = results[0].plot()
            _, buffer = cv2.imencode(".jpg", annotated)

            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n" +
                buffer.tobytes() +
                b"\r\n"
            )

        except Exception:
            logger.error(traceback.format_exc())

# ================== ROUTES ==================
@app.get("/api/stream")
def stream():
    return StreamingResponse(
        generate_frames(),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )

@app.post("/api/start")
def start_stream():
    global streaming_active, last_alert_time
    streaming_active = True
    last_alert_time = 0
    logger.info("🚨 STREAMING STARTED")
    return {"status": "streaming started"}

@app.post("/api/stop")
def stop_stream():
    global streaming_active
    streaming_active = False
    return {"status": "streaming stopped"}

# ================== IMAGE UPLOAD ==================
@app.post("/api/upload")
async def upload_image(file: UploadFile = File(...)):
    path = os.path.join(UPLOAD_FOLDER, file.filename)

    with open(path, "wb") as f:
        f.write(await file.read())

    try:
        frame = cv2.imread(path)
        results = model(frame)
        violations = extract_violations(results)

        annotated = results[0].plot()
        out_name = f"annotated_{int(time.time())}_{file.filename}"
        out_path = os.path.join(UPLOAD_FOLDER, out_name)
        cv2.imwrite(out_path, annotated)

        os.remove(path)

        return {
            "violations": violations,
            "annotated_image": f"http://127.0.0.1:8000/uploads/{out_name}"
        }

    except Exception:
        logger.error(traceback.format_exc())
        return JSONResponse({"error": "Processing failed"}, status_code=500)

# ================== VIDEO UPLOAD ==================
@app.post("/api/upload/video")
async def upload_video(file: UploadFile = File(...)):
    input_path = os.path.join(UPLOAD_FOLDER, file.filename)

    with open(input_path, "wb") as f:
        f.write(await file.read())

    cap_vid = cv2.VideoCapture(input_path)
    fps = cap_vid.get(cv2.CAP_PROP_FPS) or 25
    w = int(cap_vid.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap_vid.get(cv2.CAP_PROP_FRAME_HEIGHT))

    fourcc = cv2.VideoWriter_fourcc(*"avc1")
    out_name = f"annotated_{int(time.time())}.mp4"
    out_path = os.path.join(UPLOAD_FOLDER, out_name)

    out = cv2.VideoWriter(out_path, fourcc, fps, (w, h))
    violations = set()

    while cap_vid.isOpened():
        ret, frame = cap_vid.read()
        if not ret:
            break
        results = model(frame)
        violations.update(extract_violations(results))
        out.write(results[0].plot())

    cap_vid.release()
    out.release()
    os.remove(input_path)

    return {
        "violations": list(violations),
        "annotated_video": f"http://127.0.0.1:8000/uploads/{out_name}"
    }

# ================== REPORT ==================
@app.get("/api/report")
def report():
    report = "\n".join(detections_history) or "No alerts yet."
    detections_history.clear()
    return {"message": "Report generated", "count": len(report.splitlines())}

# ================== WEBSOCKET ==================
@app.websocket("/ws/alerts")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    connected_clients.append(ws)
    try:
        while True:
            await ws.receive_text()
    except:
        connected_clients.remove(ws)

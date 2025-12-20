import os
import cv2
import time
import logging
import traceback
import smtplib

from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from flask import Flask, Response, jsonify, request, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO
from werkzeug.utils import secure_filename
from ultralytics import YOLO

# ================== APP SETUP ==================
app = Flask(__name__)
CORS(app, origins=["http://localhost:3000"])
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

detections_history = []
streaming_active = False

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
cap.set(cv2.CAP_PROP_FPS, 30)

if not cap.isOpened():
    raise RuntimeError("❌ Webcam not accessible")

# ================== GLOBAL STATE ==================
detections_history = []

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
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    detections_history.append(f"[{timestamp}] {message}")


# ================== EMAIL ==================
def send_email(report):
    sender = "sitesafety.ai@gmail.com"
    receiver = "xxx@gmail.com"
    password = "xxxxxxxxxx"  # move to env in production

    msg = MIMEMultipart()
    msg["From"] = sender
    msg["To"] = receiver
    msg["Subject"] = "SiteSafeAI – Detection Report"

    msg.attach(MIMEText(report, "plain"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender, password)
            server.send_message(msg)
        logger.info("Email sent")
    except Exception as e:
        logger.error(f"Email error: {e}")


# ================== STREAM ==================
def generate_frames():
    while True:
        success, frame = cap.read()
        if not success:
            time.sleep(0.1)
            continue

        try:
            results = model(frame, verbose=False)
            violations = extract_violations(results)

            if violations:
                message = f"Violation detected: {', '.join(violations)}"
                record_detection(message)

                socketio.emit("status_update", {
                    "message": message,
                    "timestamp": datetime.now().strftime("%H:%M:%S")
                })

            annotated = results[0].plot()
            _, buffer = cv2.imencode(".jpg", annotated)

            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n" +
                buffer.tobytes() +
                b"\r\n"
            )

        except Exception as e:
            logger.error(traceback.format_exc())
            _, buffer = cv2.imencode(".jpg", frame)
            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n" +
                buffer.tobytes() +
                b"\r\n"
            )


@app.route("/api/stream")
def api_stream():
    return Response(
        generate_frames(),
        mimetype="multipart/x-mixed-replace; boundary=frame"
    )


# ================== IMAGE UPLOAD ==================
@app.route("/api/upload", methods=["POST"])
def api_upload():
    if "file" not in request.files:
        return jsonify({"error": "No file"}), 400

    file = request.files["file"]
    filename = secure_filename(file.filename)
    path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(path)

    try:
        frame = cv2.imread(path)
        results = model(frame)
        violations = extract_violations(results)

        annotated = results[0].plot()
        out_name = f"annotated_{int(time.time())}_{filename}"
        out_path = os.path.join(UPLOAD_FOLDER, out_name)
        cv2.imwrite(out_path, annotated)

        os.remove(path)

        return jsonify({
            "violations": violations,
            "annotated_image": f"http://127.0.0.1:5000/uploads/{out_name}"
        })

    except Exception as e:
        logger.error(traceback.format_exc())
        return jsonify({"error": str(e)}), 500


@app.route("/uploads/<filename>")
def serve_upload(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)


# ================== VIDEO UPLOAD ==================
@app.route("/api/upload/video", methods=["POST"])
def upload_video():
    file = request.files["file"]
    filename = secure_filename(file.filename)
    path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(path)

    cap_vid = cv2.VideoCapture(path)
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    fps = int(cap_vid.get(cv2.CAP_PROP_FPS))
    w = int(cap_vid.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap_vid.get(cv2.CAP_PROP_FRAME_HEIGHT))

    out_name = f"annotated_{int(time.time())}_{filename}"
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
    os.remove(path)

    return jsonify({
        "violations": list(violations),
        "annotated_video": f"http://127.0.0.1:5000/uploads/{out_name}"
    })


# ================== REPORT ==================
@app.route("/api/report")
def api_report():
    report = "\n".join(detections_history) or "No alerts yet."
    send_email(report)
    detections_history.clear()

    return jsonify({
        "message": "Report generated and emailed",
        "count": len(report.splitlines())
    })


# ================== SOCKET.IO ==================
@socketio.on("connect")
def on_connect():
    logger.info("Socket connected")


@socketio.on("disconnect")
def on_disconnect():
    logger.info("Socket disconnected")

# ================== MAIN ==================
if __name__ == "__main__":
    print("\n🚀 SiteSafeAI Backend Running")
    print("📍 http://127.0.0.1:5000\n")
    socketio.run(app, debug=True, use_reloader=False)


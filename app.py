import torch
import cv2
import time
import os
from flask import request, jsonify, Flask, render_template, Response, send_from_directory, url_for
from flask_socketio import SocketIO, emit
from datetime import datetime
from threading import Thread
from ultralytics import YOLO
from twilio.rest import Client
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from werkzeug.utils import secure_filename
import traceback
import logging

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load YOLOv8 model with lower confidence threshold
print("Loading YOLO model...")
model = YOLO('best.pt')
model.conf = 0.25  # Lower confidence threshold (default is 0.25, try 0.2 if still no detections)
model.iou = 0.45   # IoU threshold for NMS
print("Model loaded successfully!")

# Open the webcam with explicit settings
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
cap.set(cv2.CAP_PROP_FPS, 30)

# Check if the camera opened successfully
if not cap.isOpened():
    print("Error: Could not open webcam")
    # Try alternative camera indices
    for i in range(1, 5):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            print(f"Webcam opened on index {i}")
            break
    if not cap.isOpened():
        print("Could not open any webcam")
        exit()
else:
    print("Webcam opened successfully!")

# Test read a frame
ret, test_frame = cap.read()
if ret:
    print(f"Test frame captured successfully. Shape: {test_frame.shape}")
else:
    print("Warning: Could not capture test frame")

# Class names as per your model
class_names = ['Hardhat', 'Mask', 'NO-Hardhat', 'NO-Mask', 'NO-Safety Vest', 
               'Person', 'Safety Cone', 'Safety Vest', 'machinery', 'vehicle']

# Global variable to store detections for reporting
detections_history = []

# Define a folder to save uploaded files
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads') 
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Function to generate a report with timestamps
def generate_report():
    if detections_history:
        report = "\n".join(detections_history)
        detections_history.clear()
        return report
    else:
        return "No alerts yet."

# Email sending function
def send_email(report):
    sender_email = "sitesafety.ai@gmail.com"
    receiver_email = "xxx@gmail.com"
    password = "xxxxxxxxxx"

    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = "YOLOv8 Detection Report"

    body = MIMEText(report, "plain")
    message.attach(body)

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message.as_string())
            print("Email sent successfully")
    except Exception as e:
        print(f"Error sending email: {e}")

# Twilio configuration
twilio_sid = ''
twilio_auth_token = ''
twilio_phone_number = ''
recipient_phone_number = ''

# Initialize Twilio client (only if credentials are provided)
if twilio_sid and twilio_auth_token:
    twilio_client = Client(twilio_sid, twilio_auth_token)
else:
    twilio_client = None
    print("Twilio credentials not configured - SMS alerts disabled")

# Function to send SMS alert
def send_sms_alert(message):
    if not twilio_client:
        print("SMS not configured")
        return
    try:
        twilio_client.messages.create(
            body=message,
            from_=twilio_phone_number,
            to=recipient_phone_number
        )
        print(f"SMS alert sent to {recipient_phone_number}.")
    except Exception as e:
        print(f"Failed to send SMS: {e}")

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            logger.error("No file part in request")
            return jsonify({"error": "No file uploaded"}), 400
        
        file = request.files['file']
        if file.filename == '':
            logger.error("No selected file")
            return jsonify({"error": "No file selected"}), 400

        logger.info(f"Received file: {file.filename} of type {file.content_type}")

        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        logger.info(f"Saving file to: {filepath}")
        file.save(filepath)

        if file.content_type.startswith('image'):
            logger.info("Processing image file")
            return process_image(filepath)
        elif file.content_type.startswith('video'):
            logger.info("Processing video file")
            return process_video(filepath)
        else:
            logger.error(f"Unsupported file type: {file.content_type}")
            os.remove(filepath)
            return jsonify({"error": "Unsupported file type"}), 400

    except Exception as e:
        logger.error(f"Error in upload_file: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

def process_image(filepath):
    try:
        logger.info(f"Reading image from {filepath}")
        frame = cv2.imread(filepath)
        if frame is None:
            raise ValueError(f"Could not read image file: {filepath}")

        logger.info("Running YOLOv8 model on image")
        results = model(frame, conf=0.25)  # Explicit confidence threshold
        violations = extract_violations(results)

        logger.info("Creating annotated image")
        annotated_frame = results[0].plot()
        
        timestamp = int(time.time())
        annotated_filename = f"annotated_{timestamp}_{os.path.basename(filepath)}"
        annotated_path = os.path.join(app.config['UPLOAD_FOLDER'], annotated_filename)
        
        logger.info(f"Saving annotated image to {annotated_path}")
        cv2.imwrite(annotated_path, annotated_frame)

        os.remove(filepath)

        return jsonify({
            "violations": violations,
            "annotated_image": url_for('download_file', filename=annotated_filename, _external=True)
        })

    except Exception as e:
        logger.error(f"Error in process_image: {str(e)}")
        logger.error(traceback.format_exc())
        if os.path.exists(filepath):
            os.remove(filepath)
        raise

def process_video(filepath):
    try:
        logger.info(f"Opening video file: {filepath}")
        cap_video = cv2.VideoCapture(filepath)
        if not cap_video.isOpened():
            raise ValueError(f"Could not open video file: {filepath}")

        timestamp = int(time.time())
        annotated_filename = f"annotated_{timestamp}_{os.path.basename(filepath)}"
        annotated_path = os.path.join(app.config['UPLOAD_FOLDER'], annotated_filename)
        
        logger.info("Setting up video writer")
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        fps = int(cap_video.get(cv2.CAP_PROP_FPS))
        width = int(cap_video.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap_video.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        logger.info(f"Video properties: {width}x{height} @ {fps}fps")
        out = cv2.VideoWriter(annotated_path, fourcc, fps, (width, height))

        violations = []
        frames_processed = 0
        max_frames = 300

        logger.info("Processing video frames")
        while cap_video.isOpened() and frames_processed < max_frames:
            ret, frame = cap_video.read()
            if not ret:
                break

            results = model(frame, conf=0.25)
            current_violations = extract_violations(results)
            violations.extend(current_violations)
            
            annotated_frame = results[0].plot()
            out.write(annotated_frame)
            
            frames_processed += 1
            if frames_processed % 10 == 0:
                logger.info(f"Processed {frames_processed} frames")

        cap_video.release()
        out.release()

        os.remove(filepath)

        violations = list(set(violations))

        video_url = url_for('serve_video', filename=annotated_filename, _external=True)
        
        return jsonify({
            "violations": violations,
            "annotated_video": video_url,
            "video_filename": annotated_filename
        })

    except Exception as e:
        logger.error(f"Error in process_video: {str(e)}")
        logger.error(traceback.format_exc())
        if os.path.exists(filepath):
            os.remove(filepath)
        raise

def extract_violations(results):
    violations = []
    detections = results[0].boxes

    if detections is not None and len(detections) > 0:
        for box in detections:
            cls_id = int(box.cls)
            label = class_names[cls_id]
            if label.startswith('NO-'):
                violations.append(label)
    return violations

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video')
def video():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/download/<filename>')
def download_file(filename):
    try:
        logger.info(f"Attempting to serve file: {filename}")
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    except Exception as e:
        logger.error(f"Error serving file {filename}: {str(e)}")
        return jsonify({"error": "File not found"}), 404

@app.route('/video/<filename>')
def serve_video(filename):
    try:
        return send_from_directory(
            app.config['UPLOAD_FOLDER'],
            filename,
            mimetype='video/mp4',
            as_attachment=False
        )
    except Exception as e:
        logger.error(f"Error serving video {filename}: {str(e)}")
        return jsonify({"error": "Video not found"}), 404

@socketio.on('request_report')
def handle_request_report():
    report = generate_report()
    send_email(report)
    print("Report generated and sent to email.")

# Function to generate frames and process detections
def generate_frames():
    frame_count = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            logger.error("Failed to read frame from webcam")
            time.sleep(0.1)
            continue

        frame_count += 1
        
        # Process every frame for better detection
        try:
            # Run inference with explicit confidence
            results = model(frame, conf=0.25, verbose=False)

            # Process detections
            detections = results[0].boxes
            violations = []
            persons = []

            if detections is not None and len(detections) > 0:
                logger.info(f"Frame {frame_count}: Detected {len(detections)} objects")
                
                for box in detections:
                    cls_id = int(box.cls)
                    label = class_names[cls_id]
                    conf = float(box.conf)
                    
                    logger.debug(f"Detected: {label} (confidence: {conf:.2f})")

                    if label == 'Person':
                        persons.append({'id': len(persons) + 1, 'violations': []})
                    elif label.startswith('NO-'):
                        if persons:
                            persons[-1]['violations'].append(label)

            # Format the message for the frontend
            if persons:
                for person in persons:
                    if person['violations']:
                        violations.append(f"Person {person['id']} missing: {', '.join(person['violations'])}")

            if violations:
                message = " | ".join(violations)
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                detections_history.append(f"[{timestamp}] {message}")
            else:
                if detections is not None and len(detections) > 0:
                    message = "All safety equipment present for all detected individuals."
                else:
                    message = "No persons detected in frame."
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                detections_history.append(f"[{timestamp}] {message}")

            # Emit real-time updates via Socket.IO
            socketio.emit('status_update', {'message': message})

            # Render predictions on the frame
            frame_with_preds = results[0].plot()

            # Convert frame with predictions to JPEG
            _, buffer = cv2.imencode('.jpg', frame_with_preds)
            frame_bytes = buffer.tobytes()

            # Yield the frame as JPEG for real-time streaming
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n\r\n')

        except Exception as e:
            logger.error(f"Error processing frame: {str(e)}")
            # Yield the original frame on error
            _, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n\r\n')

if __name__ == "__main__":
    print("\n" + "="*50)
    print("Starting Site Safety AI Detection System")
    print("="*50)
    print(f"Webcam: {'✓ Connected' if cap.isOpened() else '✗ Not Connected'}")
    print(f"Model: {'✓ Loaded' if model else '✗ Not Loaded'}")
    print(f"Server: http://127.0.0.1:5000")
    print("="*50 + "\n")
    
    socketio.run(app, debug=True, use_reloader=False)
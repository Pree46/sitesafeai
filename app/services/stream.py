import time
import cv2
import traceback
import logging
import asyncio
import threading
import numpy as np
import concurrent.futures

from . import camera
from .model import infer_openvino, CLASS_NAMES
from app.services.model import infer_openvino, decode_yolov8_flat
from ..utils.helpers import extract_violations, record_detection
from .alerts import state, alert_manager
from ..core.websocket import broadcast_alert
from ..geofence.engine import GeofenceEngine

from app.services.face_recognition.recognize import recognize_worker

geofence_engine = GeofenceEngine(ioa_threshold=0.3)

logger = logging.getLogger("sitesafeai")

CONF_THRES = 0.25
IOU_THRES = 0.5

# ================= FACE CACHE =================
LAST_WORKER_ID = "UNKNOWN"
LAST_FACE_TS = 0
FACE_INTERVAL = 4.0  # seconds

# ================= YOLO BOX PERSISTENCE =================
BOX_CACHE = []
BOX_CACHE_TS = 0
BOX_TTL = 0.6  # seconds (YOLO-like)

# ================= INFERENCE RATE LIMIT =================
LAST_INFER_TS = 0
INFER_INTERVAL = 0.06  # ~16 FPS (prevents Infer Request busy)

# ================= BACKGROUND EXECUTOR =================
executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
ai_future = None
LATEST_DETECTIONS = []


# ================= ALERT THREAD =================
def alert_in_background(alert_data):
    try:
        asyncio.run(broadcast_alert(alert_data["message"]))
    except Exception as e:
        logger.error(f"Failed to broadcast alert: {e}")


# ================= CLASS-WISE NMS =================
def nms(detections, iou_thresh=0.5):
    if not detections:
        return []

    final = []

    for cls in set(d["class"] for d in detections):
        cls_dets = [d for d in detections if d["class"] == cls]

        boxes = np.array([d["bbox"] for d in cls_dets])
        scores = np.array([d["confidence"] for d in cls_dets])

        x1, y1, x2, y2 = boxes.T
        areas = (x2 - x1) * (y2 - y1)
        order = scores.argsort()[::-1]

        keep = []

        while order.size > 0:
            i = order[0]
            keep.append(i)

            xx1 = np.maximum(x1[i], x1[order[1:]])
            yy1 = np.maximum(y1[i], y1[order[1:]])
            xx2 = np.minimum(x2[i], x2[order[1:]])
            yy2 = np.minimum(y2[i], y2[order[1:]])

            w = np.maximum(0, xx2 - xx1)
            h = np.maximum(0, yy2 - yy1)
            inter = w * h

            iou = inter / (areas[i] + areas[order[1:]] - inter)
            order = order[1:][iou < iou_thresh]

        final.extend([cls_dets[i] for i in keep])

    return final


# ================= YOLO POSTPROCESS =================
def postprocess_yolo_openvino(output, frame_shape):
    h, w, _ = frame_shape
    detections = []

    output = np.squeeze(output)

    # (C, N) → (N, C)
    if output.shape[0] < output.shape[1]:
        output = output.T

    num_classes = len(CLASS_NAMES)

    for row in output:
        cx, cy, bw, bh = row[:4]
        class_scores = row[4:4 + num_classes]

        class_id = int(np.argmax(class_scores))
        score = float(class_scores[class_id])

        if score < CONF_THRES:
            continue

        # scale to pixels
        cx *= w
        cy *= h
        bw *= w
        bh *= h

        x1 = int(cx - bw / 2)
        y1 = int(cy - bh / 2)
        x2 = int(cx + bw / 2)
        y2 = int(cy + bh / 2)

        detections.append({
            "class": CLASS_NAMES[class_id],
            "confidence": score,
            "bbox": (x1, y1, x2, y2)
        })

    return nms(detections, IOU_THRES)


# ================= YOLO BOX STABILIZATION =================
def stabilize_detections(detections):
    global BOX_CACHE, BOX_CACHE_TS
    now = time.time()

    if detections:
        BOX_CACHE = detections
        BOX_CACHE_TS = now
        return detections

    if now - BOX_CACHE_TS < BOX_TTL:
        return BOX_CACHE

    BOX_CACHE = []
    return []


# ================= DRAW BOXES =================
def draw_detections(frame, detections):
    h, w, _ = frame.shape

    # Color codes as per user specification and model.py class names
    color_map = {
        # Safe classes
        "Hardhat": (100, 167, 0),
        "Mask": (100, 167, 0),
        "Safety Vest": (100, 167, 0),
        "Safety Cone": (100, 167, 0),
        "Person": (100, 167, 0),
        # Violation classes
        "NO-Hardhat": (163, 23, 23),
        "NO-Mask": (163, 23, 23),
        "NO-Safety Vest": (163, 23, 23),
        # Machinery/Vehicle
        "machinery": (242, 236, 63),
        "vehicle": (242, 236, 63),
    }

    for d in detections:
        x1, y1, x2, y2 = d["bbox"]

        x1 = max(0, min(w - 1, x1))
        y1 = max(0, min(h - 1, y1))
        x2 = max(0, min(w - 1, x2))
        y2 = max(0, min(h - 1, y2))

        if x2 <= x1 or y2 <= y1:
            continue

        label = d["class"]
        conf = d["confidence"]

        # Use exact match for model output class names, fallback to green
        color = color_map[label] if label in color_map else (0, 255, 0)

        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        cv2.putText(
            frame,
            f"{label} {conf:.2f}",
            (x1, max(y1 - 8, 12)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            color,
            2
        )

    return frame


# ================= FACE RECOGNITION =================
def try_face_recognition(frame):
    global LAST_WORKER_ID, LAST_FACE_TS

    now = time.time()
    if now - LAST_FACE_TS < FACE_INTERVAL:
        return LAST_WORKER_ID

    LAST_FACE_TS = now

    h, w, _ = frame.shape
    crop = frame[int(h * 0.15):int(h * 0.85), int(w * 0.25):int(w * 0.75)]
    if crop.size == 0:
        return LAST_WORKER_ID

    crop = cv2.cvtColor(crop, cv2.COLOR_BGR2RGB)
    worker_id = recognize_worker(crop)
    LAST_WORKER_ID = worker_id
    return worker_id


# ================= TEST PATTERN GENERATOR =================
def generate_test_pattern(width=640, height=480):
    """Generate a simple test pattern frame when no camera is available"""
    frame = np.ones((height, width, 3), dtype=np.uint8) * 30  # Dark gray
    
    # Add grid
    for i in range(0, width, 50):
        cv2.line(frame, (i, 0), (i, height), (100, 100, 100), 1)
    for i in range(0, height, 50):
        cv2.line(frame, (0, i), (width, i), (100, 100, 100), 1)
    
    # Add text
    cv2.putText(frame, "TEST PATTERN MODE", (width//2 - 150, height//2 - 50), 
                cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 255), 2)
    cv2.putText(frame, "No camera connected", (width//2 - 130, height//2 + 20), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (100, 200, 255), 2)
    cv2.putText(frame, "Connect webcam or place demo.mp4 in project root", 
                (width//2 - 250, height//2 + 70), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (150, 150, 255), 1)
    
    return frame


# ================= BACKGROUND AI TASK =================
def run_ai_task(frame):
    worker_id = try_face_recognition(frame)
    output, scale, pad_x, pad_y = infer_openvino(frame)
    
    detections = decode_yolov8_flat(
        output=output,
        frame_shape=frame.shape,
        scale=scale,
        pad_x=pad_x,
        pad_y=pad_y,
        conf_thresh=0.25,
        iou_thresh=0.5,
    )
    
    # ===== PPE VIOLATIONS =====
    violations = extract_violations(detections)
    if violations and alert_manager.can_alert():
        msg = f"PPE violation by {worker_id}: " + ", ".join(violations)
        alert_data = alert_manager.trigger(msg)
        record_detection(msg)
        threading.Thread(target=alert_in_background, args=(alert_data,), daemon=True).start()

    # ===== GEOFENCE =====
    if state.get("geofence_enabled") and state.get("zones"):
        try:
            violations_dict = geofence_engine.process(detections, frame.shape, state["zones"])
            if violations_dict:
                for zone_name, violation_classes in violations_dict.items():
                    if alert_manager.can_alert_geofence(zone_name):
                        violations_str = ", ".join(violation_classes)
                        geofence_msg = f"Zone violation by {worker_id}: {violations_str} in '{zone_name}'"
                        alert_data = alert_manager.trigger_geofence(zone_name, {"violations": violation_classes, "worker_id": worker_id})
                        alert_data["message"] = geofence_msg
                        logger.info(f"[GEOFENCE] Alert: {alert_data['message']}")
                        record_detection(alert_data["message"])
                        threading.Thread(target=alert_in_background, args=(alert_data,), daemon=True).start()
        except Exception as e:
            logger.error(f"[GEOFENCE] Exception in geofence processing: {e}\n{traceback.format_exc()}")
            
    return detections

# ================= MAIN STREAM =================
FPS_LIMIT = 1.0 / 30.0  # 30 FPS Lock

def generate_frames():
    global ai_future, LATEST_DETECTIONS
    last_frame_ts = 0

    logger.info("Stream generator started")

    try:
        test_pattern_counter = 0
        
        while True:
            # 🕰️ STREAM FPS LIMITER to prevent GIL starvation!
            now = time.time()
            if now - last_frame_ts < FPS_LIMIT:
                time.sleep(0.01)
                continue
            last_frame_ts = now

            # 🔴 STOP = CLOSE MJPEG CONNECTION
            if not state.get("streaming_active"):
                logger.info("Streaming stopped, closing MJPEG connection")
                break

            # ⏳ Wait until camera is opened by /api/start
            if camera.cap is None or not camera.cap.isOpened():
                time.sleep(0.05)
                continue

            success, frame = camera.cap.read()
            
            # If frame read failed but we're in demo mode, generate test pattern
            if not success:
                if camera.DEMO_MODE:
                    frame = generate_test_pattern(640, 480)
                    test_pattern_counter += 1
                else:
                    time.sleep(0.03)
                    continue

            try:
                # Dispatch background computation seamlessly
                if ai_future is None or ai_future.done():
                    if ai_future is not None:
                        try:
                            LATEST_DETECTIONS = ai_future.result()
                        except Exception as e:
                            logger.error(f"AI Worker crashed: {e}")
                    
                    # Submit next frame instantly
                    ai_future = executor.submit(run_ai_task, frame.copy())
                
                # Instantly draw and push using independent Latest State
                # NOTE: Zone overlays are rendered by the frontend canvas, not here.
                annotated = draw_detections(frame.copy(), LATEST_DETECTIONS)

                # ===== STREAM FRAME =====
                _, buffer = cv2.imencode(".jpg", annotated)
                yield (
                    b"--frame\r\n"
                    b"Content-Type: image/jpeg\r\n\r\n"
                    + buffer.tobytes()
                    + b"\r\n"
                )

            except Exception as e:
                logger.error(f"Frame processing error: {e}\n{traceback.format_exc()}")
                # Still yield a frame so stream doesn't break
                try:
                    _, buffer = cv2.imencode(".jpg", frame)
                    yield (
                        b"--frame\r\n"
                        b"Content-Type: image/jpeg\r\n\r\n"
                        + buffer.tobytes()
                        + b"\r\n"
                    )
                except:
                    pass

    except GeneratorExit:
        logger.info("Stream closed by client")

    except asyncio.CancelledError:
        logger.info("Streaming cancelled")

    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received")





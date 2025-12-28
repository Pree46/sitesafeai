import time
import cv2
import traceback
import logging
import asyncio
import threading
import numpy as np

from . import camera
from .model import infer_openvino, CLASS_NAMES
from app.services.model import infer_openvino, decode_yolov8_flat
from ..utils.helpers import extract_violations, record_detection
from .alerts import state, alert_manager
from ..core.websocket import broadcast_alert
from ..geofence.engine import GeofenceEngine
from ..geofence.zones import Zone
from shapely.geometry import Polygon

from app.services.face_recognition.recognize import recognize_worker

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


# ================= MAIN STREAM =================
def generate_frames():
    global LAST_INFER_TS

    logger.info("Stream generator started")

    try:
        while True:

            # 🔴 STOP = CLOSE MJPEG CONNECTION
            if not state.get("streaming_active"):
                logger.info("Streaming stopped, closing MJPEG connection")
                break

            # ⏳ Wait until camera is opened by /api/start
            if camera.cap is None or not camera.cap.isOpened():
                time.sleep(0.05)
                continue

            success, frame = camera.cap.read()
            if not success:
                time.sleep(0.03)
                continue

            try:
                # ===== FACE (lightweight) =====
                worker_id = try_face_recognition(frame)

                # ===== INFERENCE RATE LIMIT =====
                now = time.time()
                if now - LAST_INFER_TS < INFER_INTERVAL:
                    time.sleep(0.005)
                    continue

                LAST_INFER_TS = now

                # ===== OPENVINO INFERENCE =====
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

                # ===== DRAW BOXES =====
                annotated = draw_detections(frame.copy(), detections)

                # ===== PPE VIOLATIONS =====
                violations = extract_violations(detections)
                if violations and alert_manager.can_alert():
                    msg = f"PPE violation by {worker_id}: " + ", ".join(violations)
                    alert_data = alert_manager.trigger(msg)
                    record_detection(msg)

                    threading.Thread(
                        target=alert_in_background,
                        args=(alert_data,),
                        daemon=True
                    ).start()

                # ===== GEOFENCE =====
                if state.get("geofence_enabled") and state.get("zones"):
                    logger.info(f"[GEOFENCE] Geofence enabled. Zones count: {len(state['zones'])}")
                    try:
                        zones = []
                        for z in state["zones"]:
                            if not z.get("points") or len(z["points"]) < 3:
                                logger.warning(f"[GEOFENCE] Zone '{z.get('name', 'unnamed')}' has invalid or missing points: {z.get('points')}")
                                continue
                            try:
                                poly = Polygon(z["points"])
                                if not poly.is_valid:
                                    logger.warning(f"[GEOFENCE] Zone '{z.get('name', 'unnamed')}' polygon is invalid: {z['points']}")
                                    continue
                                zones.append(Zone(
                                    name=z["name"],
                                    polygon=poly,
                                    color=tuple(z.get("color", [255, 0, 0])),
                                    alpha=z.get("alpha", 0.3)
                                ))
                            except Exception as e:
                                logger.error(f"[GEOFENCE] Error creating polygon for zone '{z.get('name', 'unnamed')}': {e}")
                        logger.info(f"[GEOFENCE] Valid zones after parsing: {len(zones)}")
                        if not zones:
                            logger.warning("[GEOFENCE] No valid geofence zones available, skipping geofence processing.")
                        else:
                            # Robust: For each zone, check all detections for violations inside that zone
                            worker_id_str = worker_id if 'worker_id' in locals() else 'UNKNOWN'
                            zone_violations = {}
                            for zone in zones:
                                zone_name = zone.name
                                poly = zone.polygon
                                for det in detections:
                                    # Get bbox center
                                    x1, y1, x2, y2 = det["bbox"]
                                    cx = (x1 + x2) / 2
                                    cy = (y1 + y2) / 2
                                    from shapely.geometry import Point
                                    if poly.contains(Polygon([(x1, y1), (x2, y1), (x2, y2), (x1, y2)])) or poly.contains(Point(cx, cy)):
                                        if zone_name not in zone_violations:
                                            zone_violations[zone_name] = []
                                        zone_violations[zone_name].append(det["class"])
                            if not zone_violations:
                                logger.info("[GEOFENCE] No geofence events generated for current detections.")
                            else:
                                for zone_name, violations in zone_violations.items():
                                    if alert_manager.can_alert_geofence(zone_name):
                                        violations_str = ", ".join(violations)
                                        geofence_msg = f"Zone violation by {worker_id_str}: {violations_str} in '{zone_name}'"
                                        alert_data = alert_manager.trigger_geofence(zone_name, {"violations": violations, "worker_id": worker_id_str})
                                        alert_data["message"] = geofence_msg
                                        logger.info(f"[GEOFENCE] Geofence alert triggered: {alert_data['message']}")
                                        record_detection(alert_data["message"])
                                        threading.Thread(
                                            target=alert_in_background,
                                            args=(alert_data,),
                                            daemon=True
                                        ).start()
                                    else:
                                        logger.info(f"[GEOFENCE] Alert for zone '{zone_name}' suppressed by rate limiter or state.")
                    except Exception as e:
                        logger.error(f"[GEOFENCE] Exception in geofence processing: {e}\n{traceback.format_exc()}")

                # ===== STREAM FRAME =====
                _, buffer = cv2.imencode(".jpg", annotated)
                yield (
                    b"--frame\r\n"
                    b"Content-Type: image/jpeg\r\n\r\n"
                    + buffer.tobytes()
                    + b"\r\n"
                )

            except Exception:
                logger.error(traceback.format_exc())

    except GeneratorExit:
        logger.info("Stream closed by client")

    except asyncio.CancelledError:
        logger.info("Streaming cancelled")

    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received")





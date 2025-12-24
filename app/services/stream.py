import time
import cv2
import traceback
import logging
import asyncio
import threading

from .camera import cap
from .model import model
from ..utils.helpers import extract_violations, record_detection
from .alerts import state, alert_manager  # Import alert_manager
from ..core.websocket import broadcast_alert
from ..geofence.engine import GeofenceEngine
from ..geofence.zones import Zone
from shapely.geometry import Polygon

logger = logging.getLogger("sitesafeai")


def alert_in_background(alert_data):
    """
    Send alert via WebSocket in background thread.
    Ensures frontend always receives a STRING message.
    """
    try:
        if isinstance(alert_data, dict):
            msg = alert_data.get("message", "")
        else:
            msg = alert_data

        asyncio.run(broadcast_alert(msg))
    except Exception as e:
        logger.error(f"Failed to broadcast alert: {e}")



def yolo_to_detections(results):
    """Convert YOLO results to detection format"""
    detections = []

    boxes = results[0].boxes
    if boxes is None:
        return detections

    for box in boxes:
        cls_id = int(box.cls)
        label = model.names[cls_id]
        x1, y1, x2, y2 = map(int, box.xyxy[0])

        detections.append({
            "class": label,
            "bbox": (x1, y1, x2, y2)
        })

    return detections


def load_zones_from_state():
    """Convert state zones to Zone objects"""
    zones = []
    
    for z in state.get("zones", []):
        try:
            zones.append(
                Zone(
                    name=z["name"],
                    polygon=Polygon(z["points"]),
                    color=tuple(z.get("color", [255, 0, 0])),
                    alpha=z.get("alpha", 0.3)
                )
            )
        except Exception as e:
            logger.error(f"Failed to load zone {z.get('name')}: {e}")
    
    return zones


def generate_frames():
    """Main streaming loop with PPE and geofence detection"""
    
    while True:
        success, frame = cap.read()
        if not success:
            time.sleep(0.1)
            continue

        try:
            results = model(frame, verbose=False)

            if state["streaming_active"]:
                # ===== PPE VIOLATIONS =====
                violations = extract_violations(results)
                
                if violations and alert_manager.can_alert():
                    msg = "PPE: " + ", ".join(violations)
                    alert_data = alert_manager.trigger(msg)
                    record_detection(msg)
                    
                    # Send to WebSocket
                    threading.Thread(
                        target=alert_in_background,
                        args=(alert_data,),
                        daemon=True
                    ).start()

                # ===== GEOFENCE VIOLATIONS =====
                if state.get("geofence_enabled") and state.get("zones"):
                    zones = load_zones_from_state()
                    
                    if zones:
                        # Create engine with current zones
                        engine = GeofenceEngine(zones, alert_manager)
                        
                        # Get detections
                        detections = yolo_to_detections(results)
                        
                        # Check for violations
                        violations_list = engine.process_detections(detections)
                        
                        # Send alerts for each violation
                        for v in violations_list:
                            zone_name = v["zone"]
                            obj_class = v["object"]
                            
                            # Check cooldown per zone
                            if alert_manager.can_alert_geofence(zone_name):
                                alert_data = alert_manager.trigger_geofence(
                                    zone_name, 
                                    obj_class
                                )
                                
                                msg = alert_data["message"]
                                record_detection(msg)
                                
                                # Send to WebSocket
                                threading.Thread(
                                    target=alert_in_background,
                                    args=(alert_data,),
                                    daemon=True
                                ).start()

            # Annotate frame
            annotated = results[0].plot()
            
            # Draw zones on frame (optional visualization)
            if state.get("geofence_enabled") and state.get("zones"):
                for z in state["zones"]:
                    points = z["points"]
                    if len(points) >= 3:
                        pts = [[int(p[0]), int(p[1])] for p in points]
                        pts_array = [pts]
                        
                        color = tuple(z.get("color", [255, 0, 0]))
                        alpha = z.get("alpha", 0.3)
                        
                        # Create overlay
                        overlay = annotated.copy()
                        cv2.fillPoly(overlay, pts_array, color)
                        cv2.addWeighted(overlay, alpha, annotated, 1 - alpha, 0, annotated)
                        
                        # Draw border
                        cv2.polylines(annotated, pts_array, True, color, 2)
                        
                        # Draw zone name
                        cv2.putText(
                            annotated,
                            z["name"],
                            (pts[0][0], pts[0][1] - 5),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.6,
                            (255, 255, 255),
                            2
                        )

            # Encode frame
            _, buffer = cv2.imencode(".jpg", annotated)

            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n" +
                buffer.tobytes() +
                b"\r\n"
            )

        except Exception:
            logger.error(traceback.format_exc())
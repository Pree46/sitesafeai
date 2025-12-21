import time
import cv2
import traceback
import logging
import asyncio
import threading

from .camera import cap
from .model import model
from ..utils.helpers import extract_violations, record_detection
from .alerts import state, ALERT_COOLDOWN_SECONDS
from ..core.websocket import broadcast_alert

logger = logging.getLogger("sitesafeai")

def alert_in_background(message):
    """Send alert in a background thread to avoid blocking"""
    try:
        asyncio.run(broadcast_alert(message))
    except Exception as e:
        logger.error(f"Failed to broadcast alert: {e}")

def generate_frames():
    while True:
        success, frame = cap.read()
        if not success:
            time.sleep(0.1)
            continue

        try:
            results = model(frame, verbose=False)

            if state["streaming_active"]:
                violations = extract_violations(results)
                now = time.time()
                
                logger.debug(f"Violations detected: {violations}, Streaming active: {state['streaming_active']}")

                if violations and (now - state["last_alert_time"]) > ALERT_COOLDOWN_SECONDS:
                    msg = f"Violation detected: {', '.join(violations)}"
                    record_detection(msg)
                    state["last_alert_time"] = now
                    logger.info(f"Broadcasting alert: {msg}")
                    # Send alert in background thread
                    thread = threading.Thread(target=alert_in_background, args=(msg,))
                    thread.daemon = True
                    thread.start()

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

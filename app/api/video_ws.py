from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import logging
from app.services.stream import generate_frames

logger = logging.getLogger("sitesafeai")

video_ws_router = APIRouter()

@video_ws_router.websocket("/ws/video")
async def video_stream_ws(ws: WebSocket):
    await ws.accept()
    logger.info("Video WebSocket client connected")
    try:
        frame_gen = generate_frames()
        while True:
            frame = next(frame_gen, None)
            if frame is None:
                break
            # Extract JPEG bytes from MJPEG chunk
            # MJPEG: b"--frame\r\nContent-Type: image/jpeg\r\n\r\n...bytes...\r\n"
            # We'll just send the JPEG bytes
            start = frame.find(b'\r\n\r\n') + 4
            end = frame.rfind(b'\r\n')
            jpeg_bytes = frame[start:end]
            await ws.send_bytes(jpeg_bytes)
    except WebSocketDisconnect:
        logger.info("Video WebSocket client disconnected")
    except Exception as e:
        logger.error(f"Video WebSocket error: {e}")
    finally:
        await ws.close()

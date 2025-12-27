from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from ..services.stream import generate_frames
from ..services.alerts import state
from ..services import camera  # IMPORTANT

router = APIRouter()


@router.get("/api/stream")
def stream():
    """
    MJPEG video stream endpoint.
    The generator will exit automatically when streaming_active becomes False.
    """
    return StreamingResponse(
        generate_frames(),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )


@router.post("/api/start")
def start_stream():
    if state.get("streaming_active"):
        return {"status": "already streaming"}

    try:
        camera.open_camera()
    except Exception as e:
        return {"status": "camera_error", "detail": str(e)}

    state["streaming_active"] = True
    return {"status": "streaming started"}



@router.post("/api/stop")
def stop_stream():
    """
    Stop streaming:
    - Just flip the flag
    - Generator will exit and release camera safely
    """
    state["streaming_active"] = False
    camera.release_camera()
    return {"status": "streaming stopped"}

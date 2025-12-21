from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from ..services.stream import generate_frames
from ..services.alerts import state

router = APIRouter()

@router.get("/api/stream")
def stream():
    return StreamingResponse(
        generate_frames(),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )

@router.post("/api/start")
def start_stream():
    state["streaming_active"] = True
    return {"status": "streaming started"}

@router.post("/api/stop")
def stop_stream():
    state["streaming_active"] = False
    return {"status": "streaming stopped"}

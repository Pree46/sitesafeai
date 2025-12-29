# Minimal aiortc WebRTC video streaming endpoint
# Requires: pip install aiortc opencv-python
from fastapi import APIRouter, WebSocket
from aiortc import RTCPeerConnection, RTCSessionDescription, VideoStreamTrack
from aiortc.contrib.media import MediaBlackhole
import cv2
import asyncio
import numpy as np
from app.services.stream import generate_frames
import logging

logger = logging.getLogger("sitesafeai")

video_webrtc_router = APIRouter()

class CameraVideoTrack(VideoStreamTrack):
    def __init__(self):
        super().__init__()
        self.frame_gen = generate_frames()

    async def recv(self):
        from av import VideoFrame
        frame_bytes = next(self.frame_gen, None)
        if frame_bytes is None:
            await asyncio.sleep(0.04)
            return None
        # Extract JPEG bytes
        start = frame_bytes.find(b'\r\n\r\n') + 4
        end = frame_bytes.rfind(b'\r\n')
        jpeg_bytes = frame_bytes[start:end]
        arr = np.frombuffer(jpeg_bytes, dtype=np.uint8)
        img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        if img is None:
            await asyncio.sleep(0.04)
            return None
        frame = VideoFrame.from_ndarray(img, format="bgr24")
        frame.pts, frame.time_base = self.next_timestamp()
        return frame

@video_webrtc_router.post("/ws/webrtc-offer")
async def webrtc_offer(offer: dict):
    pc = RTCPeerConnection()
    pc.addTrack(CameraVideoTrack())
    await pc.setRemoteDescription(RTCSessionDescription(sdp=offer["sdp"], type=offer["type"]))
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)
    return {"sdp": pc.localDescription.sdp, "type": pc.localDescription.type}

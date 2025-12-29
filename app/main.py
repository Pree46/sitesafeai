from fastapi import FastAPI

from .core.settings import setup_app
from .api.stream import router as stream_router
from .api.upload import router as upload_router
from .api.report import router as report_router
from .core.websocket import websocket_router

from .api.video_ws import video_ws_router
from .api.video_webrtc import video_webrtc_router
from .api.geofence import router as geofence_router
app = FastAPI()

setup_app(app)

app.include_router(stream_router)
app.include_router(upload_router)
app.include_router(report_router)
app.include_router(websocket_router)
app.include_router(geofence_router)
app.include_router(video_ws_router)
app.include_router(video_webrtc_router)
app.include_router(video_ws_router)




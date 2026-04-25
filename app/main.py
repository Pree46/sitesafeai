from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware


from .core.settings import setup_app
from .api.stream import router as stream_router
from .api.upload import router as upload_router
from .api.report import router as report_router
from .core.websocket import websocket_router

from .api.video_ws import video_ws_router
from .api.video_webrtc import video_webrtc_router
from .api.geofence import router as geofence_router
from .api.dashboard import router as dashboard_router
app = FastAPI()

setup_app(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(stream_router)
app.include_router(upload_router)
app.include_router(report_router)
app.include_router(websocket_router)
app.include_router(geofence_router)
app.include_router(video_webrtc_router)
app.include_router(video_ws_router)
app.include_router(dashboard_router)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")




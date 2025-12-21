import os
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def setup_app(app):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.mount("/uploads", StaticFiles(directory=UPLOAD_FOLDER), name="uploads")

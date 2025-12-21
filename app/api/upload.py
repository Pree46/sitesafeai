import os
import cv2
import time
import traceback
import logging

from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse

from ..services.model import model
from ..utils.helpers import extract_violations
from ..core.settings import UPLOAD_FOLDER

router = APIRouter()
logger = logging.getLogger("sitesafeai")


# ================== IMAGE UPLOAD ==================
@router.post("/api/upload")
async def upload_image(file: UploadFile = File(...)):
    path = os.path.join(UPLOAD_FOLDER, file.filename)

    with open(path, "wb") as f:
        f.write(await file.read())

    try:
        frame = cv2.imread(path)
        results = model(frame)
        violations = extract_violations(results)

        annotated = results[0].plot()
        out_name = f"annotated_{int(time.time())}_{file.filename}"
        out_path = os.path.join(UPLOAD_FOLDER, out_name)
        cv2.imwrite(out_path, annotated)

        os.remove(path)

        return {
            "violations": violations,
            "annotated_image": f"http://127.0.0.1:8000/uploads/{out_name}"
        }

    except Exception:
        logger.error(traceback.format_exc())
        return JSONResponse({"error": "Processing failed"}, status_code=500)


# ================== VIDEO UPLOAD ==================
@router.post("/api/upload/video")
async def upload_video(file: UploadFile = File(...)):
    input_path = os.path.join(UPLOAD_FOLDER, file.filename)

    with open(input_path, "wb") as f:
        f.write(await file.read())

    cap_vid = cv2.VideoCapture(input_path)
    fps = cap_vid.get(cv2.CAP_PROP_FPS) or 25
    w = int(cap_vid.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap_vid.get(cv2.CAP_PROP_FRAME_HEIGHT))

    fourcc = cv2.VideoWriter_fourcc(*"avc1")
    out_name = f"annotated_{int(time.time())}.mp4"
    out_path = os.path.join(UPLOAD_FOLDER, out_name)

    out = cv2.VideoWriter(out_path, fourcc, fps, (w, h))
    violations = set()

    while cap_vid.isOpened():
        ret, frame = cap_vid.read()
        if not ret:
            break
        results = model(frame)
        violations.update(extract_violations(results))
        out.write(results[0].plot())

    cap_vid.release()
    out.release()
    os.remove(input_path)

    return {
        "violations": list(violations),
        "annotated_video": f"http://127.0.0.1:8000/uploads/{out_name}"
    }

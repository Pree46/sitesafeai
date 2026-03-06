import os
import cv2
import time
import traceback
import logging
import subprocess

from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse

from ..services.model import infer_openvino, decode_yolov8_flat
from ..utils.helpers import extract_violations
from ..core.settings import UPLOAD_FOLDER

router = APIRouter()
logger = logging.getLogger("sitesafeai")


# ================= DRAW BOXES =================
def draw_detections(frame, detections):
    for det in detections:
        x1, y1, x2, y2 = det["bbox"]
        label = f"{det['class']} {det['confidence']:.2f}"

        cv2.rectangle(frame, (x1, y1), (x2, y2), (0,255,0), 2)

        cv2.putText(
            frame,
            label,
            (x1, y1 - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0,255,0),
            2
        )

    return frame


# ================= IMAGE UPLOAD =================
@router.post("/api/upload")
async def upload_image(file: UploadFile = File(...)):
    path = os.path.join(UPLOAD_FOLDER, file.filename)

    with open(path, "wb") as f:
        f.write(await file.read())

    try:
        frame = cv2.imread(path)

        # OPENVINO INFERENCE
        output, scale, pad_x, pad_y = infer_openvino(frame)

        detections = decode_yolov8_flat(
            output,
            frame.shape,
            scale,
            pad_x,
            pad_y
        )

        violations = extract_violations(detections)

        annotated = draw_detections(frame.copy(), detections)

        out_name = f"annotated_{int(time.time())}_{file.filename}"
        out_path = os.path.join(UPLOAD_FOLDER, out_name)

        cv2.imwrite(out_path, annotated)

        os.remove(path)

        return {
            "violations": violations,
            "annotated_image": f"/serve-video/uploads/{out_name}"
        }

    except Exception:
        logger.error(traceback.format_exc())
        return JSONResponse({"error": "Processing failed"}, status_code=500)


# ================= VIDEO UPLOAD =================
@router.post("/api/upload/video")
async def upload_video(file: UploadFile = File(...)):
    import subprocess
    
    input_path = os.path.join(UPLOAD_FOLDER, file.filename)
    
    with open(input_path, "wb") as f:
        f.write(await file.read())

    cap_vid = cv2.VideoCapture(input_path)
    
    fps = int(cap_vid.get(cv2.CAP_PROP_FPS)) or 25
    w = int(cap_vid.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap_vid.get(cv2.CAP_PROP_FRAME_HEIGHT))

    temp_output = os.path.join(UPLOAD_FOLDER, "temp_annotated.mp4")
    
    violations = set()
    frame_count = 0

    try:
        # Write frames to temp file using OpenCV
        fourcc = cv2.VideoWriter_fourcc(*"MJPG")
        out = cv2.VideoWriter(temp_output.replace(".mp4", ".avi"), fourcc, fps, (w, h))

        while True:
            ret, frame = cap_vid.read()
            if not ret:
                break

            frame = cv2.resize(frame, (w, h))
            frame_count += 1

            if frame_count % 3 == 0:
                output, scale, pad_x, pad_y = infer_openvino(frame)
                detections = decode_yolov8_flat(output, frame.shape, scale, pad_x, pad_y)
                violations.update(extract_violations(detections))
                frame = draw_detections(frame, detections)

            out.write(frame)

        cap_vid.release()
        out.release()

        # Convert AVI to MP4 using FFmpeg
        out_name = f"annotated_{int(time.time())}.mp4"
        out_path = os.path.join(UPLOAD_FOLDER, out_name)
        
        subprocess.run([
            r"C:\ffmpeg-n8.0-latest-win64-gpl-8.0\bin\ffmpeg.exe", "-i", temp_output.replace(".mp4", ".avi"), 
            "-c:v", "libx264", "-preset", "fast",
            "-c:a", "aac", out_path, "-y"
        ], check=True)

        # Clean up temp files
        os.remove(input_path)
        os.remove(temp_output.replace(".mp4", ".avi"))

        return {
            "violations": list(violations),
            "annotated_video": f"/serve-video/{out_name}"
        }

    except Exception as e:
        cap_vid.release()
        logger.error(traceback.format_exc())
        return JSONResponse({"error": str(e)}, status_code=500)
    
    
@router.get("/serve-video/{filename}")
async def serve_video(filename: str):
    """Serve video file"""
    from fastapi.responses import FileResponse
    
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    
    logger.info(f"Attempting to serve: {file_path}")
    logger.info(f"File exists: {os.path.exists(file_path)}")
    
    if not os.path.exists(file_path):
        logger.error(f"File NOT found: {file_path}")
        return JSONResponse({"error": "File not found"}, status_code=404)
    
    try:
        return FileResponse(
            file_path, 
            media_type="video/mp4",
            headers={"Content-Disposition": "inline"}
        )
    except Exception as e:
        logger.error(f"Error serving video: {e}")
        return JSONResponse({"error": str(e)}, status_code=500)
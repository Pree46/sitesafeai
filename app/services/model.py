import logging
from ultralytics import YOLO
import cv2
import numpy as np
from openvino import Core



logger = logging.getLogger("sitesafeai")

logger.info("Loading YOLO model...")
model = YOLO("best.pt")
model.conf = 0.25
model.iou = 0.45
logger.info("YOLO model loaded")

CLASS_NAMES = [
    "Hardhat", "Mask", "NO-Hardhat", "NO-Mask",
    "NO-Safety Vest", "Person", "Safety Cone",
    "Safety Vest", "machinery", "vehicle"
]



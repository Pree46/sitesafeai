import cv2
import numpy as np
import logging
from openvino import Core

logger = logging.getLogger("sitesafeai")

# ================= CLASS NAMES =================
CLASS_NAMES = [
    "Hardhat",
    "Mask",
    "NO-Hardhat",
    "NO-Mask",
    "NO-Safety Vest",
    "Person",
    "Safety Cone",
    "Safety Vest",
    "machinery",
    "vehicle"
]

# ================= OPENVINO INIT =================
core = Core()

logger.info("Loading OpenVINO YOLOv8 INT8 model...")

model = core.read_model("best_int8_model/best.xml")
compiled_model = core.compile_model(model, "CPU")

input_layer = compiled_model.input(0)
_, _, INPUT_H, INPUT_W = input_layer.shape

output_layers = compiled_model.outputs  # IMPORTANT: multiple heads

logger.info(f"Model input size: {INPUT_W}x{INPUT_H}")

# ================= UTILS =================
def sigmoid(x):
    return 1 / (1 + np.exp(-x))


def box_iou(a, b):
    x1 = max(a[0], b[0])
    y1 = max(a[1], b[1])
    x2 = min(a[2], b[2])
    y2 = min(a[3], b[3])

    inter = max(0, x2 - x1) * max(0, y2 - y1)
    area1 = (a[2] - a[0]) * (a[3] - a[1])
    area2 = (b[2] - b[0]) * (b[3] - b[1])

    return inter / (area1 + area2 - inter + 1e-6)


def nms(detections, iou_thresh):
    detections = sorted(detections, key=lambda x: x["confidence"], reverse=True)
    final = []

    while detections:
        best = detections.pop(0)
        final.append(best)
        detections = [
            d for d in detections
            if box_iou(best["bbox"], d["bbox"]) < iou_thresh
        ]

    return final


# ================= INFERENCE =================
def infer_openvino(frame):
    img_lb, scale, pad_x, pad_y = letterbox(frame, (INPUT_W, INPUT_H))

    inp = img_lb.transpose(2, 0, 1)
    inp = np.expand_dims(inp, axis=0).astype(np.float32) / 255.0

    result = compiled_model([inp])
    output = result[compiled_model.outputs[0]]
    print("OpenVINO output shape:", output.shape)

    # return all heads
    return output, scale, pad_x, pad_y


# ================= YOLOv8 DFL DECODER =================
def decode_yolov8_flat(
    output,
    frame_shape,
    scale,
    pad_x,
    pad_y,
    conf_thresh=0.25,
    iou_thresh=0.5
):
    """
    output shape: [1, N, 4 + num_classes]
    boxes are xywh (center-based) in letterbox space
    """

    img_h, img_w = frame_shape[:2]
    output = output.squeeze(0).T

    boxes = output[:, :4]
    scores = output[:, 4:]

    class_ids = np.argmax(scores, axis=1)
    confidences = scores[np.arange(len(scores)), class_ids]

    detections = []

    for box, cls_id, conf in zip(boxes, class_ids, confidences):
        if conf < conf_thresh:
            continue

        cx, cy, w, h = box

        # Convert xywh → xyxy (letterbox space)
        x1 = cx - w / 2
        y1 = cy - h / 2
        x2 = cx + w / 2
        y2 = cy + h / 2

        # 🔥 UNLETTERBOX (THIS FIXES YOUR BOXES)
        x1 = (x1 - pad_x) / scale
        y1 = (y1 - pad_y) / scale
        x2 = (x2 - pad_x) / scale
        y2 = (y2 - pad_y) / scale

        # Clamp
        x1 = max(0, min(img_w, x1))
        y1 = max(0, min(img_h, y1))
        x2 = max(0, min(img_w, x2))
        y2 = max(0, min(img_h, y2))

        detections.append({
            "class": CLASS_NAMES[int(cls_id)],
            "confidence": float(conf),
            "bbox": (int(x1), int(y1), int(x2), int(y2))
        })

    return nms(detections, iou_thresh)


def letterbox(img, new_shape=(640, 640), color=(114, 114, 114)):
    h, w = img.shape[:2]
    new_w, new_h = new_shape

    r = min(new_w / w, new_h / h)
    nw, nh = int(w * r), int(h * r)

    img_resized = cv2.resize(img, (nw, nh), interpolation=cv2.INTER_LINEAR)

    pad_w = new_w - nw
    pad_h = new_h - nh

    top = pad_h // 2
    bottom = pad_h - top
    left = pad_w // 2
    right = pad_w - left

    img_padded = cv2.copyMakeBorder(
        img_resized, top, bottom, left, right,
        cv2.BORDER_CONSTANT, value=color
    )

    return img_padded, r, left, top


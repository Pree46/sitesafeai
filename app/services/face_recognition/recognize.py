import os
import pickle
import numpy as np
import cv2
from insightface.app import FaceAnalysis

BASE_DIR = os.path.dirname(__file__)
DB_FILE = os.path.join(BASE_DIR, "embeddings.pkl")

print("📂 Loading Face DB from:", DB_FILE)
with open(DB_FILE, "rb") as f:
    DB = pickle.load(f)

print("👥 Workers in DB:", list(DB.keys()))

app = FaceAnalysis(name="buffalo_l", providers=["CPUExecutionProvider"])
app.prepare(ctx_id=0)

# 🔐 STRICT threshold (very important)
THRESHOLD = 0.55

def l2_normalize(x):
    return x / np.linalg.norm(x)


def recognize_worker(image):
    faces = app.get(image)

    if not faces:
        print("❌ No face detected")
        return "UNKNOWN"

    # ✅ Use the LARGEST face only
    face = max(
        faces,
        key=lambda f: (f.bbox[2] - f.bbox[0]) * (f.bbox[3] - f.bbox[1])
    )

    x1, y1, x2, y2 = map(int, face.bbox)
    face_crop = image[y1:y2, x1:x2]

    if face_crop.size == 0:
        print("❌ Empty face crop")
        return "UNKNOWN"

    # 🔍 DEBUG — overwrite every frame
    cv2.imwrite("debug_face.jpg", face_crop)

    emb = l2_normalize(face.embedding)

    best_id = "UNKNOWN"
    best_score = -1.0

    for worker_id, vectors in DB.items():
        for v in vectors:
            v = l2_normalize(v)
            score = float(np.dot(emb, v))

            print(f"🔍 Comparing with {worker_id}, score={score:.3f}")

            if score > best_score:
                best_score = score
                best_id = worker_id

    print(f"🏆 Best match: {best_id} | Score: {best_score:.3f}")

    # 🚨 HARD REJECTION
    if best_score < THRESHOLD:
        print("🚫 Rejected → UNKNOWN")
        return "UNKNOWN"

    print("✅ Accepted:", best_id)
    return best_id

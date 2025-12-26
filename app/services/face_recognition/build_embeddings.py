import os
import cv2
import pickle
from insightface.app import FaceAnalysis

BASE_DIR = os.path.dirname(__file__)
FACES_DIR = os.path.join(BASE_DIR, "faces")
OUT_FILE = os.path.join(BASE_DIR, "embeddings.pkl")

app = FaceAnalysis(name="buffalo_l", providers=["CPUExecutionProvider"])
app.prepare(ctx_id=0)

db = {}

for worker_id in os.listdir(FACES_DIR):
    person_dir = os.path.join(FACES_DIR, worker_id)
    if not os.path.isdir(person_dir):
        continue

    embeddings = []

    for img_name in os.listdir(person_dir):
        img_path = os.path.join(person_dir, img_name)
        img = cv2.imread(img_path)
        if img is None:
            continue

        faces = app.get(img)
        if faces:
            embeddings.append(faces[0].embedding)

    if embeddings:
        db[worker_id] = embeddings
        print(f"✔ {worker_id}: {len(embeddings)} embeddings")

with open(OUT_FILE, "wb") as f:
    pickle.dump(db, f)

print("\n✅ Embeddings saved")

# InsightFace Setup Guide (Windows – CPU Only)

This project uses **InsightFace (buffalo_l)** for face recognition.

⚠️ InsightFace depends on **Python-version-specific wheels**, so it is **NOT installed via `requirements.txt`**.  
Each collaborator must install it manually using the steps below.

---

## 1. Check Python Version

```bash
python --version
```

Examples:

- Python **3.9.x** → `cp39`
- Python **3.10.x** → `cp310`

You must use the InsightFace wheel that matches your Python version.

---

## 2. Download Face Model (buffalo_l)

Download **buffalo_l.zip** from the official InsightFace releases page:

https://github.com/deepinsight/insightface/releases

### Extract Location (IMPORTANT)

Extract the model files to:

```
C:\Users\<YOUR_USERNAME>\.insightface\models\
```

Final structure must look like:

```
C:\Users\<YOUR_USERNAME>\.insightface\
└── models/
    └── buffalo_l/
        ├── det_10g.onnx
        ├── w600k_r50.onnx
        ├── genderage.onnx
        ├── 2d106det.onnx
        └── 1k3d68.onnx
```

❌ Do NOT commit this directory  
❌ Do NOT move it into the project

InsightFace automatically loads models from this location.

---

## 3. Remove Conflicting Packages

```bash
pip uninstall -y numpy opencv-python-headless albumentations albucore insightface
```

---

## 4. Install Required Dependency Versions

```bash
pip install numpy==1.26.4
pip install opencv-python-headless==4.8.1.78
```

⚠️ NumPy **2.x is incompatible** with InsightFace.

---

## 5. Install Albumentations (Without Dependency Upgrades)

```bash
pip install albucore==0.0.13 --no-deps
pip install albumentations==1.4.14 --no-deps
```

---

## 6. Install InsightFace Wheel (Local)

Each collaborator must download the correct wheel for their Python version.

Notes:

- The `.whl` file is **NOT committed**
- Store it locally (e.g., a `whls/` folder ignored by Git)
- Download the whl compatible to your python version
- example: if Python version: 3.9, Download: insightface-0.7.3-cp39-cp39-win_amd64.whl
- https://github.com/Gourieff/Assets/tree/main/Insightface

Example (Python 3.9):

```bash
pip install path\to\insightface-0.7.3-cp39-cp39-win_amd64.whl --no-deps
```

---

## 7. Install Remaining Dependencies

```bash
pip install onnx==1.19.1 onnxruntime==1.19.2
pip install scipy scikit-image scikit-learn pillow matplotlib tqdm requests prettytable
```

---

## 8. Verify Installation

```bash
python -c "from insightface.app import FaceAnalysis; print('InsightFace import OK')"
```

Expected output:

```
InsightFace import OK
```

---

## 9. Create Embeddings

- Create a folder app/services/face_recognition/faces
- Under this create multiple worker profiles, Example: app/services/face_recognition/faces/wkr001
- under wkr001 You will adding atleast 3-8 pictures of yourself facing the camera.
- You can add multiple worker id's (wkr002,wkr003 etc...) in the same way.
- Once you are done with creating worker id's and storing respective images, you can open a new Terminal.

```bash
cd face_recognition
python build_embeddings.py
```

Now You are ready to run your Back-end

## Required `.gitignore` Entries

```gitignore
# InsightFace models
.insightface/

# Face data (PII)
app/services/face_recognition/faces/
app/services/face_recognition/embeddings.pkl

# Local wheels
whls/
```

---

## Notes

- Face enrollment is **manual by design**
- Automatic learning is intentionally disabled (security reason)
- GPU is NOT required
- CPU execution only

---

End of setup guide.

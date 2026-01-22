# Site Safe AI

<p align="left">
  <img src="frontend/src/assets/logo_without_bg" alt="Site Safe AI Logo" width="48" style="vertical-align:middle; margin-right:8px;" />
  <strong>Site Safe AI</strong> – AI-driven PPE and safety monitoring for construction sites
</p>

Site Safe AI is an AI-driven system designed to enhance safety compliance on construction sites. Using advanced computer vision techniques and deep learning models, the project detects essential safety equipment like helmets and vests, monitors geofencing zones, and supports face recognition for worker identification. The solution provides real-time monitoring to reduce risks, prevent accidents, and improve compliance with safety regulations.

## Problem Statement

Construction sites are high-risk environments where failure to use proper safety equipment, such as helmets and vests, can result in serious injuries or fatalities. Manual safety monitoring is labor-intensive, error-prone, and often inefficient. Site Safe AI addresses these challenges by automating safety equipment detection, ensuring worker compliance in real-time, and promoting a safer work environment.

## Solution

Site Safe AI leverages the YOLOv8 (You Only Look Once) model for object detection, OpenVINO for optimization, and integrates geofencing and face recognition modules. It processes video footage or images to identify safety equipment, monitor worker locations within defined zones, and recognize faces for access control or attendance. The solution integrates:

- **Computer Vision**: To detect and classify workers' safety gear.
- **Geofencing**: To monitor and enforce virtual boundaries for restricted or hazardous areas on-site.
- **Face Recognition**: For worker identification, attendance, and access control.
- **Real-Time Inference**: To monitor compliance and zone breaches on-site without manual intervention.
- **Performance Optimization**: Using Intel Extension for PyTorch (IPEX) and OpenVINO for maximum efficiency.
- **Post-Processing Alerts**: Notifications via email or SMS when safety violations or geofence breaches are detected.

## Features

- Real-time detection of safety equipment (helmets, vests, etc.).
- Geofencing: Define and monitor virtual zones to restrict or track worker movement.
- Face recognition: Identify workers for access control, attendance, or personalized alerts.
- Optimized inference using Intel OpenVINO for faster processing.
- Enhanced PyTorch performance with Intel IPEX optimization.
- Alerts for safety violations, geofence breaches, or unauthorized access via email or SMS.
- Scalable architecture for deployment on edge devices or cloud platforms.

## Geofencing & Face Recognition

Geofencing and face recognition are included for zone monitoring and worker identification. See `app/geofence/` and `app/services/face_recognition/` for details.

## Dataset

The dataset is sourced from Kaggle: [Construction Site Safety Dataset](https://www.kaggle.com/datasets/snehilsanyal/construction-site-safety-image-dataset-roboflow).

## Technologies Used

- **AI Models and Frameworks**:
  - YOLOv8: Deep learning model for object detection.
  - OpenVINO: Model optimization for faster inference.
  - Intel Extension for PyTorch (IPEX): Performance optimization for PyTorch operations.

- **Programming Languages**:
  - Python

- **Tools and Platforms**:
  - Kaggle for model training and experimentation.
  - OpenVINO Toolkit: For optimizing the YOLOv8 model, enhancing inference performance on Intel hardware.
  - Intel IPEX: For accelerating PyTorch workloads on Intel hardware.

- **Frontend**:
  - Next.js (see `frontend/`), with the logo located at `frontend/src/assets/logo.png` and used in the main layout/header.

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/Pree46/sitesafeai.git
cd sitesafeai

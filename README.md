# Smart Trash Bin: Real-Time PET Plastic Bottle Detection & Automated Sorting System

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Ultralytics RT-DETR](https://img.shields.io/badge/Ultralytics-RT--DETR--L-purple.svg?logo=yolo&logoColor=white)](https://docs.ultralytics.com/models/rtdetr/)
[![Intel OpenVINO](https://img.shields.io/badge/Intel-OpenVINO%202024-0071C5.svg?logo=intel&logoColor=white)](https://www.intel.com/content/www/us/en/developer/tools/openvino-toolkit/overview.html)
[![Microcontroller](https://img.shields.io/badge/Hardware-ESP32%20DevKit-red.svg?logo=espressif&logoColor=white)](https://www.espressif.com/en/products/socs/esp32)
[![Accuracy](https://img.shields.io/badge/mAP%400.5-97.4%25-brightgreen.svg)](#evaluation--benchmark-results)
[![Inference Speed](https://img.shields.io/badge/Inference-22.8ms%20%2F%20frame-orange.svg)](#evaluation--benchmark-results)

An end-to-end Cyber-Physical Waste Sorting System integrating **Real-Time Detection Transformer (RT-DETR-L)**, **Intel OpenVINO edge acceleration**, and an **ESP32 microcontroller** to identify PET plastic bottles and trigger mechanical actuation and audio alerts via serial communication.

---

## 📌 Project Overview

Automated waste segregation at disposal points helps reduce cross-contamination in recyclable plastic streams. This repository implements an end-to-end smart trash bin prototype that:
1. Acquires a video stream from a camera.
2. Performs real-time object detection using an **RT-DETR-L** model optimized with **Intel OpenVINO**.
3. Communicates detection decisions to an **ESP32 microcontroller** via UART serial communication (`115200 baud`).
4. Actuates physical sorting hardware: a servo motor for the sorting flap and an active buzzer for non-PET object alerts.

---

## 🏗️ System Pipeline & Architecture

```text
       ┌────────────────────────┐
       │     Digital Camera     │
       │  (1280x720 in GUI App) │
       └───────────┬────────────┘
                   │ Video Frames
                   ▼
       ┌────────────────────────┐
       │   Intel OpenVINO IR    │
       │ (RT-DETR-L 640x640 IR) │
       └───────────┬────────────┘
                   │ Class ID & Confidence
                   ▼
       ┌────────────────────────┐
       │ Python Decision Engine │
       │ (GUI / CLI Controller) │
       └───────────┬────────────┘
                   │ Serial Command (UART @ 115200 baud)
                   ▼
       ┌────────────────────────┐
       │  ESP32 Microcontroller │
       │   (CodeArduinoIDE)     │
       └─────┬────────────┬─────┘
             │            │
             │ Signal '1' │ Signal '2'
             ▼            ▼
   ┌────────────────┐   ┌───────────────────────┐
   │ Servo Motor    │   │ Active Buzzer         │
   │ (GPIO 13)      │   │ (GPIO 19)             │
   │ Rotate 90°     │   │ 3x Alert Beep Pattern │
   └────────────────┘   └───────────────────────┘
```

---

## 📊 Dataset & Model Configuration

* **Dataset Identifier:** `SampahPlastik-2` (Roboflow `data.yaml`)
* **Classes (2 Classes):**
  * `0: Botol Plastik` (Target PET plastic bottles)
  * `1: Random` (Foreign materials / non-PET objects / background items)
* **Training Resolution:** 640 × 640 pixels
* **Validation Split Evaluated in Training:** 33 images (484 total instances: 288 `Botol Plastik`, 196 `Random`)

---

## ⚙️ Model Architecture & Training Parameters

The model was trained in Google Colab as documented in [`notebooks/SkripsiRTDETR1.ipynb`](notebooks/SkripsiRTDETR1.ipynb):

* **Architecture:** Baidu / Ultralytics RT-DETR Large (`rtdetr-l.pt`)
* **Model Summary:** 310 layers, 31,987,850 parameters, 103.4 GFLOPs
* **Hardware Acceleration:** NVIDIA Tesla T4 (14,913 MiB VRAM), CUDA 13.0, PyTorch 2.10.0+cu128
* **Epochs:** 50 completed epochs (0.932 hours)
* **Batch Size:** 16
* **Image Size:** 640 × 640 pixels
* **Optimizer:** AdamW (`lr=0.001667`, `momentum=0.9`)
* **Export Target:** Intel OpenVINO IR (`best.xml`, `best.bin`, `metadata.yaml`)

---

## 📈 Evaluation & Benchmark Results

### 1. Model Performance Metrics (Validated from Training Notebook)
| Metric | Overall (`all`) | Class: `Botol Plastik` | Class: `Random` |
|---|:---:|:---:|:---:|
| **Precision (Box P)** | **94.9%** | 91.5% | 98.4% |
| **Recall (Box R)** | **94.6%** | 95.8% | 93.4% |
| **mAP @ 0.5** | **97.4%** | 96.7% | 98.2% |
| **mAP @ 0.5:0.95** | **81.2%** | 82.1% | 80.3% |

### 2. Inference Speed
* **Preprocessing:** 0.2 ms per image
* **Inference Latency (GPU Tesla T4):** 22.8 ms per image
* **Postprocessing:** 1.7 ms per image

---

## 🔬 Script Configuration & Operational Modes

The project includes different scripts tailored for specific testing and deployment needs. Configurations differ based on the operational target:

| Script File | Execution Mode | Inference Engine | Confidence Threshold | Confirmation Delay / Debounce |
|---|---|---|:---:|:---:|
| [`src/Uji_TerakhirBuzzer.py`](src/Uji_TerakhirBuzzer.py) | Desktop GUI (Tkinter) | OpenVINO (`best_openvino_model`) | `conf = 0.90` | `0 seconds` (Immediate trigger mode) |
| [`src/uji_integrasi_igpu.py`](src/uji_integrasi_igpu.py) | Headless / CLI | OpenVINO (`best_openvino_model`) | `conf = 0.60` | `5 seconds` (Debounce security window) |
| [`experiments/Uji_Terakhir.py`](experiments/Uji_Terakhir.py) | Desktop GUI (Tkinter) | OpenVINO (`best_openvino_model`) | `conf = 0.90` | `5 seconds` (Timed confirmation mode) |
| [`src/uji_kamera.py`](src/uji_kamera.py) | Standalone Video Test | PyTorch (`best.pt`) | `conf = 0.60` | None (Camera test only) |

---

## 🔌 Hardware Control & Pinout

Firmware is implemented in [`firmware/CodeArduinoIDE_ForESP32/CodeArduinoIDE_ForESP32.ino`](firmware/CodeArduinoIDE_ForESP32/CodeArduinoIDE_ForESP32.ino):

* **Microcontroller:** ESP32 Development Board
* **Baud Rate:** `115200 baud` (Serial UART)
* **Servo Actuator:**
  * **Pin:** `GPIO 13` (`pinServo`)
  * **Mode in Code:** `MODE SG90 PRESISI`
  * **Behavior:** Default position at 180°. When command `'1'` is received, moves to 90°, holds for 3000 ms, then returns to 180°.
* **Buzzer Alarm:**
  * **Pin:** `GPIO 19` (`pinBuzzer`)
  * **Type:** Active Buzzer (driven by `digitalWrite` HIGH/LOW)
  * **Behavior:** On startup, beeps for 800 ms. When command `'2'` is received, sounds 3 alert beeps (200 ms ON, 200 ms OFF).

---

## 📁 Repository Structure

```text
smart-trash-bin-rtdetr/
│
├── .gitignore                          # Excludes heavy binaries, caches, and local files (UTF-8)
├── README.md                           # Technical documentation & project portfolio
├── requirements.txt                    # Python runtime and analysis dependencies
│
├── src/                                # Primary application source code
│   ├── Uji_TerakhirBuzzer.py           # Production Desktop Control Panel GUI (Tkinter + OpenVINO)
│   ├── uji_integrasi_igpu.py           # Headless/CLI OpenVINO inference with 5s confirmation
│   └── uji_kamera.py                   # Camera feed diagnostic utility
│
├── firmware/                           # Embedded microcontroller source code
│   └── CodeArduinoIDE_ForESP32/
│       └── CodeArduinoIDE_ForESP32.ino # ESP32 actuator firmware for Servo (Pin 13) & Buzzer (Pin 19)
│
├── notebooks/                          # Training and analysis pipelines
│   └── SkripsiRTDETR1.ipynb            # Colab training notebook with 50-epoch log and loss graphs
│
├── weights/                            # Trained model configuration & download guides
│   ├── metadata.yaml                   # Model specification and class label mappings
│   └── README.md                       # Download instructions for best.pt and best_openvino_model
│
└── experiments/                        # Development and preliminary testing scripts
    ├── Uji_Terakhir.py                 # GUI with 5s confirmation delay
    ├── uji_integrasi_buzzer.py         # PyTorch baseline buzzer test script
    └── uji_integrasi.py                # Serial integration test baseline
```

---

## 🚀 Getting Started

### 1. Clone Repository & Setup Environment
```bash
# Clone the repository
git clone https://github.com/dmascp/smart-trash-bin-based-on-RTDETR-model-for-bottle-plastic.git
cd smart-trash-bin-based-on-RTDETR-model-for-bottle-plastic

# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate      # On Windows
# source venv/bin/activate  # On Linux/macOS

# Install required dependencies
pip install -r requirements.txt
```

### 2. Model Weights
Due to GitHub file size limitations, model binaries (`best.pt` ~66.2 MB and `best_openvino_model/best.bin` ~127.9 MB) are excluded from direct version control:
* Refer to [`weights/README.md`](weights/README.md) for download links and instructions to place model files in the project directory.

### 3. Flash ESP32 Firmware
1. Open [`firmware/CodeArduinoIDE_ForESP32/CodeArduinoIDE_ForESP32.ino`](firmware/CodeArduinoIDE_ForESP32/CodeArduinoIDE_ForESP32.ino) in the Arduino IDE.
2. Install the `ESP32Servo` library via Arduino Library Manager.
3. Select your ESP32 board and COM port, then upload the firmware.

### 4. Run the Application
Launch the Desktop Control Panel GUI:
```bash
python src/Uji_TerakhirBuzzer.py
```
Or run the headless CLI inference engine:
```bash
python src/uji_integrasi_igpu.py
```

---

## 🛠️ Technologies Used

* **Computer Vision & Deep Learning:** Ultralytics RT-DETR-L, PyTorch
* **Inference Optimization:** Intel OpenVINO Toolkit
* **Image Processing & GUI:** OpenCV (cv2), Pillow (PIL), Tkinter
* **Embedded Systems:** ESP32 DevKit, Arduino C++, ESP32Servo
* **Data Handling:** Roboflow, Pandas, Matplotlib, Seaborn

---

## 👨‍💻 Author & Academic Affiliation

* **Author:** Demas Chandra Permana
* **Program:** Pendidikan Teknik Otomasi Industri dan Robotika (PTOIR)
* **Faculty:** Fakultas Pendidikan Teknologi dan Kejuruan (FPTK)
* **Institution:** Universitas Pendidikan Indonesia (UPI), Bandung, Indonesia
* **Advisor:** Dr. Erik Haritman, S.Pd., M.T.
# Model Weights & Deployment Artifacts

Direktori ini berisi konfigurasi model ([`metadata.yaml`](metadata.yaml)) dan panduan penempatan file bobot model untuk repositori [smart-trash-bin-based-on-RTDETR-model-for-bottle-plastic](https://github.com/dmascp/smart-trash-bin-based-on-RTDETR-model-for-bottle-plastic).

> **Catatan:** File bobot biner (`best.pt` ~66.2 MB dan `best_openvino_model/best.bin` ~127.9 MB) tidak disimpan langsung di dalam repositori Git karena batasan ukuran file.

---

## Struktur File Model

```text
# Model OpenVINO IR untuk inferensi real-time:
best_openvino_model/
├── best.xml                      # Deskripsi topologi & arsitektur model OpenVINO
├── best.bin                      # Bobot biner model OpenVINO (~128 MB)
└── metadata.yaml                 # Konfigurasi runtime OpenVINO (resolusi & kelas)

# Checkpoint PyTorch pelatihan:
best.pt                           # Bobot model RT-DETR PyTorch (~66.2 MB)
```

---

## Cara Memperoleh Bobot Model

File bobot model pre-trained dan arsip dataset tersedia melalui folder Google Drive resmi proyek:
🔗 **[Google Drive Model & Dataset Storage](https://drive.google.com/drive/folders/13PXKEgIr3O0g9s6dhWu9olDuxcSmuCL_?usp=sharing)**

File yang tersedia di cloud storage:
* `best_openvino_model/` (folder berisi `best.xml`, `best.bin`, dan `metadata.yaml`)
* `SampahPlastik-2-20260910T102751Z-1-001.zip` (arsip dataset pelatihan)

---

## Penempatan File Model untuk Menjalankan Aplikasi

Aplikasi utama ([`src/Uji_TerakhirBuzzer.py`](../src/Uji_TerakhirBuzzer.py)) dan script CLI ([`src/uji_integrasi_igpu.py`](../src/uji_integrasi_igpu.py)) memuat model menggunakan path relatif:
```python
model = RTDETR('best_openvino_model')
```

Oleh karena itu, folder `best_openvino_model/` **harus ditempatkan langsung pada root project** (Current Working Directory saat menjalankan program):

```text
smart-trash-bin-based-on-RTDETR-model-for-bottle-plastic/
├── best_openvino_model/
│   ├── best.xml
│   ├── best.bin
│   └── metadata.yaml
├── src/
│   ├── Uji_TerakhirBuzzer.py
│   └── uji_integrasi_igpu.py
└── ...
```

Untuk pengujian webcam menggunakan script [`src/uji_kamera.py`](../src/uji_kamera.py) yang memuat model PyTorch (`RTDETR('best.pt')`):
* Tempatkan file `best.pt` langsung pada root project.

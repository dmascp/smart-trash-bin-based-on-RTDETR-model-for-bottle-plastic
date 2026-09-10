# Model Weights Directory

Direktori ini digunakan untuk menyimpan bobot model hasil pelatihan dan model hasil ekspor OpenVINO.

> **Catatan:** File bobot biner (`best.pt` dan `best_openvino_model/best.bin`) tidak disimpan langsung di dalam repositori Git karena ukurannya yang besar (> 50 MB dan > 100 MB).

## Struktur File yang Diharapkan
```text
weights/
├── metadata.yaml                     # Metadata konfigurasi kelas dan resolusi model (sudah tersedia)
├── best.pt                           # Bobot model RT-DETR PyTorch (~66.2 MB)
└── best_openvino_model/              # Direktori model OpenVINO IR (~128 MB)
    ├── best.xml                      # Deskripsi arsitektur model OpenVINO
    ├── best.bin                      # Bobot terkuantisasi/biner OpenVINO
    └── metadata.yaml                 # Konfigurasi runtime OpenVINO
```

## Cara Memperoleh Bobot Model
1. Unduh file bobot model melalui [GitHub Releases](https://github.com/JustTenshi22/smart-trash-bin-based-on-RTDETR-model-for-bottle-plastic/releases) atau tautan cloud storage yang disediakan.
2. Tempatkan `best.pt` langsung di dalam folder root atau folder `weights/`.
3. Ekstrak bundel `best_openvino_model/` ke dalam root project atau folder `weights/`.

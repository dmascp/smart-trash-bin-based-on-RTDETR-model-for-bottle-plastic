import cv2
import serial
import time
from ultralytics import RTDETR

# ==========================================
# 1. INISIALISASI KONEKSI (COM5)
# ==========================================
try:
    print("Mencoba terhubung ke ESP32 di COM5...")
    esp32 = serial.Serial(port='COM5', baudrate=115200, timeout=1)
    time.sleep(2)
    print("SISTEM ONLINE: Terhubung ke Hardware (Servo & Buzzer).")
except Exception as e:
    print("ERROR: Cek kabel USB atau tutup Serial Monitor Arduino!")
    exit()

# ==========================================
# 2. LOAD MODEL AI (AKSELERASI INTEL iGPU)
# ==========================================
print("Memuat Model AI dengan Akselerasi Intel iGPU (OpenVINO)...")
model = RTDETR('best_openvino_model') 
cap = cv2.VideoCapture(0)

# ==========================================
# 3. VARIABEL KONFIRMASI (ANTI-LATAH)
# ==========================================
objek_terakhir = None
waktu_mulai_deteksi = 0
durasi_konfirmasi = 5  # Waktu tunggu 5 detik
sudah_eksekusi = False # Penanda agar ESP32 tidak di-spam sinyal

print("\n==========================================")
print("SISTEM PEMILAH + ALARM + ANTI-LATAH AKTIF")
print("Tekan huruf 'q' pada keyboard untuk keluar.")
print("==========================================\n")

# ==========================================
# 4. LOOP DETEKSI UTAMA
# ==========================================
while True:
    ret, frame = cap.read()
    if not ret: 
        print("Gagal membaca frame kamera.")
        break

    # Jalankan AI (verbose=False agar terminal bersih)
    results = model.predict(source=frame, conf=0.6, show=False, verbose=False)
    
    # Ambil semua label benda yang ada di layar saat ini
    labels_saat_ini = []
    for r in results:
        if len(r.boxes) > 0:
            labels_saat_ini = [r.names[int(box.cls[0])] for box in r.boxes]

    # Tentukan status prioritas utama (Random diutamakan demi keamanan)
    status_sekarang = None
    if "Random" in labels_saat_ini:
        status_sekarang = "Random"
    elif "Botol Plastik" in labels_saat_ini:
        status_sekarang = "Botol Plastik"

    # ==========================================
    # LOGIKA KONFIRMASI 5 DETIK
    # ==========================================
    waktu_sekarang = time.time()

    if status_sekarang is not None: # Jika ada objek di layar
        
        # Jika objeknya MASIH SAMA dengan sebelumnya
        if status_sekarang == objek_terakhir:
            durasi_berjalan = waktu_sekarang - waktu_mulai_deteksi
            
            # Jika sudah mencapai 5 detik dan belum dikirim sinyalnya
            if durasi_berjalan >= durasi_konfirmasi and not sudah_eksekusi:
                if status_sekarang == "Botol Plastik":
                    print(f"\n>>> [TERKONFIRMASI 5 DETIK] Botol Plastik Valid! MEMBUKA PINTU...")
                    esp32.write(b'1')
                else:
                    print(f"\n>>> [TERKONFIRMASI 5 DETIK] Objek Ilegal Valid! MENYALAKAN ALARM...")
                    esp32.write(b'2')
                
                sudah_eksekusi = True # Tandai bahwa aksi sudah dilakukan
            
            # Jika masih di bawah 5 detik, tampilkan proses di terminal (opsional)
            elif not sudah_eksekusi:
                print(f"Mengonfirmasi {status_sekarang}... ({int(durasi_berjalan)} detik)", end='\r')
        
        # Jika objeknya BERUBAH (Misal dari Botol tiba-tiba jadi Random)
        else:
            objek_terakhir = status_sekarang
            waktu_mulai_deteksi = waktu_sekarang
            sudah_eksekusi = False
            print(f"\n[OBJEK BARU] Mendeteksi: {status_sekarang}. Mulai menghitung 5 detik...")
            
    else: 
        # Jika layar KOSONG (tidak ada objek)
        if objek_terakhir is not None:
            print("\n[KOSONG] Objek hilang dari kamera. Timer dibatalkan.")
        objek_terakhir = None
        sudah_eksekusi = False
        waktu_mulai_deteksi = 0

    # Tampilkan kotak deteksi di video
    annotated_frame = results[0].plot()
    cv2.imshow('Smart Trash Bin PTOIR - Confirmation Mode', annotated_frame)
    
    # Tombol darurat keluar
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# ==========================================
# 5. MATIKAN SISTEM DENGAN AMAN
# ==========================================
cap.release()
cv2.destroyAllWindows()
esp32.close()
print("\nProgram selesai dan sistem dimatikan.")
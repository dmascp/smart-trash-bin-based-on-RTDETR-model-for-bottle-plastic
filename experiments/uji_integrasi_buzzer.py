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
# 2. LOAD MODEL RT-DETR
# ==========================================
print("Memuat Model AI...")
model = RTDETR('best.pt')
cap = cv2.VideoCapture(0)

# Variabel pengatur jeda antar deteksi
waktu_terakhir_kirim = 0
jeda_sistem = 5 # Jeda 5 detik

print("\n==========================================")
print("SISTEM PEMILAH + ALARM AKTIF")
print("Tekan huruf 'q' pada keyboard untuk keluar.")
print("==========================================\n")

# ==========================================
# 3. LOOP DETEKSI UTAMA
# ==========================================
while True:
    ret, frame = cap.read()
    if not ret: 
        print("Gagal membaca frame kamera.")
        break

    # Jalankan AI (verbose=False agar terminal bersih)
    results = model.predict(source=frame, conf=0.6, show=False, verbose=False)
    
    waktu_sekarang = time.time()
    
    # Jika sudah lewat jeda 5 detik, sistem boleh merespons lagi
    if (waktu_sekarang - waktu_terakhir_kirim) > jeda_sistem:
        for r in results:
            if len(r.boxes) > 0:
                # Kumpulkan semua nama benda yang terdeteksi di layar
                labels = [r.names[int(box.cls[0])] for box in r.boxes]
                
                print(f"Terdeteksi di layar: {labels}")

                # LOGIKA PEMILAHAN BERLAPIS DENGAN BUZZER:
                if "Random" in labels:
                    # Skenario: Ada sampah Random (sendirian ATAU campur dengan botol)
                    print(">>> AWAS: Objek Ilegal! Pintu Dikunci & Alarm Berbunyi!")
                    esp32.write(b'2') # Kirim sinyal 2 (Diam & Bunyi)
                    waktu_terakhir_kirim = waktu_sekarang
                
                elif "Botol Plastik" in labels:
                    # Skenario: HANYA ada Botol Plastik murni
                    print(">>> AMAN: Botol Plastik Murni. Membuka Pintu.")
                    esp32.write(b'1') # Kirim sinyal 1 (Buka Pintu)
                    waktu_terakhir_kirim = waktu_sekarang

    # Tampilkan kotak deteksi di video
    annotated_frame = results[0].plot()
    cv2.imshow('Sistem Pemilah + Alarm', annotated_frame)
    
    # Tombol darurat keluar
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# ==========================================
# 4. MATIKAN SISTEM DENGAN AMAN
# ==========================================
cap.release()
cv2.destroyAllWindows()
esp32.close()
print("Program selesai dan sistem dimatikan.")
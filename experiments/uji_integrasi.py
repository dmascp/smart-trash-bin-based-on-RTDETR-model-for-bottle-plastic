import cv2
import serial
import time
from ultralytics import RTDETR

# ==========================================
# 1. INISIALISASI KONEKSI (COM5)
# ==========================================
try:
    esp32 = serial.Serial(port='COM5', baudrate=115200, timeout=1)
    time.sleep(2)
    print("SISTEM ONLINE: Terhubung ke Hardware.")
except:
    print("ERROR: Cek kabel USB atau tutup Serial Monitor Arduino!")
    exit()

# ==========================================
# 2. LOAD MODEL RT-DETR
# ==========================================
model = RTDETR('best.pt')
cap = cv2.VideoCapture(0)

waktu_terakhir_kirim = 0
jeda_servo = 5 

print("Mulai Pemindaian... Tekan 'q' untuk berhenti.")

# ==========================================
# 3. LOOP DETEKSI
# ==========================================
while True:
    ret, frame = cap.read()
    if not ret: break

    # Jalankan AI (verbose=False agar terminal bersih)
    results = model.predict(source=frame, conf=0.8, show=False, verbose=False)
    
    waktu_sekarang = time.time()
    
    if (waktu_sekarang - waktu_terakhir_kirim) > jeda_servo:
        for r in results:
            if len(r.boxes) > 0:
                # Ambil semua label yang muncul di frame saat ini
                labels = [r.names[int(box.cls[0])] for box in r.boxes]
                
                print(f"Terdeteksi di layar: {labels}")

                # LOGIKA PEMILAHAN BERLAPIS:
                # Jika ada 'Random' (meskipun ada botol juga), kirim sinyal 2 (Diam)
                if "Random" in labels:
                    print(">>> KONFLIK/RANDOM: Pintu tetap ditutup.")
                    esp32.write(b'2')
                    waktu_terakhir_kirim = waktu_sekarang
                
                # Jika HANYA ada 'Botol Plastik' tanpa ada 'Random'
                elif "Botol Plastik" in labels:
                    print(">>> BOTOL MURNI: Mengirim sinyal BUKA.")
                    esp32.write(b'1')
                    waktu_terakhir_kirim = waktu_sekarang

    # Tampilkan visualisasi
    annotated_frame = results[0].plot()
    cv2.imshow('Sistem Pemilah Otomatis PTOIR', annotated_frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
esp32.close()
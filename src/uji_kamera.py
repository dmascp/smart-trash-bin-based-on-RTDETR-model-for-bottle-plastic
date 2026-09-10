import cv2
from ultralytics import RTDETR

# 1. Memuat model AI yang sudah Anda latih
# Pastikan nama filenya sesuai dengan yang ada di folder Anda
print("Memuat model AI...")
model = RTDETR('best.pt') 

# 2. Membuka koneksi ke Webcam
# Angka 0 biasanya untuk webcam bawaan laptop. 
# Jika Anda pakai webcam eksternal (USB), coba ganti ke 1 atau 2.
print("Membuka kamera...")
cap = cv2.VideoCapture(0)

# Mengecek apakah kamera berhasil dibuka
if not cap.isOpened():
    print("Error: Kamera tidak dapat diakses!")
    exit()

print("Kamera aktif. Tekan 'q' untuk keluar.")

# 3. Looping untuk membaca video secara real-time (Frame by Frame)
while True:
    # Membaca satu frame gambar dari kamera
    ret, frame = cap.read()
    
    if not ret:
        print("Gagal membaca frame dari kamera.")
        break

    # 4. Melakukan deteksi objek pada frame tersebut
    # conf=0.6 artinya hanya tampilkan kotak jika AI yakin > 60%
    results = model.predict(source=frame, conf=0.6, show=False)

    # 5. Menggambar kotak (bounding box) hasil deteksi ke gambar asli
    # results[0].plot() akan otomatis menggambar kotak dan labelnya
    annotated_frame = results[0].plot()

    # 6. Menampilkan gambar hasil deteksi di sebuah jendela pop-up
    cv2.imshow('Uji Coba Deteksi Botol Skripsi', annotated_frame)

    # 7. Tombol Keluar (Tekan huruf 'q' di keyboard untuk menutup jendela)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 8. Membersihkan memori setelah selesai
cap.release()
cv2.destroyAllWindows()
print("Program selesai.")
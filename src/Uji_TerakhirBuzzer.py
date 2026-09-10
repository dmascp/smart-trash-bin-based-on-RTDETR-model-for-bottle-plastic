import cv2
import serial
import time
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
from ultralytics import RTDETR

class SmartTrashBinUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Smart Trash Bin PTOIR - Control Panel")
        # PERBESAR JENDELA UI
        self.root.geometry("1000x800")
        self.root.configure(bg="#f0f0f0")

        # ==========================================
        # VARIABEL STATE & AI
        # ==========================================
        self.is_running = False
        self.cap = None
        self.esp32 = None
        self.model = None

        # Variabel Konfirmasi
        self.objek_terakhir = None
        self.waktu_mulai_deteksi = 0
        self.durasi_konfirmasi = 0
        self.sudah_eksekusi = False

        # ==========================================
        # ELEMEN UI / UX
        # ==========================================
        # Judul Atas
        self.lbl_title = tk.Label(self.root, text="Sistem Pemilah Sampah & Alarm", font=("Arial", 18, "bold"), bg="#f0f0f0")
        self.lbl_title.pack(pady=10)

        # FRAME VIDEO
        self.lbl_video = tk.Label(self.root, bg="black")
        self.lbl_video.pack(pady=10)

        # Label Status Info
        self.lbl_status = tk.Label(self.root, text="Status: OFFLINE", font=("Arial", 14, "bold"), fg="red", bg="#f0f0f0")
        self.lbl_status.pack(pady=10)

        # Frame Tombol
        self.btn_frame = tk.Frame(self.root, bg="#f0f0f0")
        self.btn_frame.pack(pady=10)

        self.btn_start = tk.Button(self.btn_frame, text="▶ Start Camera", command=self.start_system, 
                                   bg="#4CAF50", fg="white", font=("Arial", 12, "bold"), width=15, cursor="hand2")
        self.btn_start.pack(side=tk.LEFT, padx=10)

        self.btn_quit = tk.Button(self.btn_frame, text="✖ Quit", command=self.quit_system, 
                                  bg="#F44336", fg="white", font=("Arial", 12, "bold"), width=15, cursor="hand2")
        self.btn_quit.pack(side=tk.LEFT, padx=10)

    def init_hardware_and_ai(self):
        """Fungsi untuk inisialisasi koneksi COM5 dan Model OpenVINO"""
        # 1. Serial ESP32
        if self.esp32 is None:
            try:
                self.lbl_status.config(text="Status: Mencoba terhubung ke ESP32 di COM5...", fg="orange")
                self.root.update()
                self.esp32 = serial.Serial(port='COM5', baudrate=115200, timeout=1)
                time.sleep(2)
                print("SISTEM ONLINE: Terhubung ke Hardware (Servo & Buzzer).")
            except Exception as e:
                messagebox.showerror("Error Hardware", "Cek kabel USB atau tutup Serial Monitor Arduino!")
                return False

        # 2. Model AI
        if self.model is None:
            try:
                self.lbl_status.config(text="Status: Memuat Model AI...", fg="orange")
                self.root.update()
                self.model = RTDETR('best_openvino_model')
                print("Model AI berhasil dimuat.")
            except Exception as e:
                messagebox.showerror("Error Model", f"Gagal memuat model: {e}")
                return False

        return True

    def start_system(self):
        """Dieksekusi saat tombol Start ditekan"""
        if self.is_running:
            return

        # Setup Hardware & AI
        if not self.init_hardware_and_ai():
            self.lbl_status.config(text="Status: Gagal Inisialisasi Hardware/AI", fg="red")
            return

        # Buka Kamera dan paksa resolusinya ke 1280x720
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        
        if not self.cap.isOpened():
            messagebox.showerror("Error Kamera", "Kamera tidak terdeteksi!")
            return

        self.is_running = True
        self.btn_start.config(state=tk.DISABLED)  # Nonaktifkan tombol start agar tidak di-spam
        self.lbl_status.config(text="Status: SISTEM ONLINE", fg="green")
        
        # Reset Logic
        self.objek_terakhir = None
        self.waktu_mulai_deteksi = 0
        self.sudah_eksekusi = False

        # Mulai loop frame
        self.update_frame()

    def update_frame(self):
        """Looping utama pengganti while True agar UI tidak freeze"""
        if not self.is_running:
            return

        ret, frame = self.cap.read()
        if not ret:
            self.lbl_status.config(text="Status: Gagal membaca frame kamera.", fg="red")
            self.quit_system()
            return

        # ==========================================
        # LOGIKA AI DAN KONFIRMASI 
        # ==========================================
        results = self.model.predict(source=frame, conf=0.9, show=False, verbose=False)
        
        labels_saat_ini = []
        for r in results:
            if len(r.boxes) > 0:
                labels_saat_ini = [r.names[int(box.cls[0])] for box in r.boxes]

        status_sekarang = None
        if "Random" in labels_saat_ini:
            status_sekarang = "Random"
        elif "Botol Plastik" in labels_saat_ini:
            status_sekarang = "Botol Plastik"

        waktu_sekarang = time.time()

        if status_sekarang is not None:
            if status_sekarang == self.objek_terakhir:
                durasi_berjalan = waktu_sekarang - self.waktu_mulai_deteksi
                
                # JIKA SUDAH 5 DETIK
                if durasi_berjalan >= self.durasi_konfirmasi and not self.sudah_eksekusi:
                    if status_sekarang == "Botol Plastik":
                        print("\n>>> [TERKONFIRMASI] Botol Plastik Valid! MEMBUKA PINTU...")
                        if self.esp32: self.esp32.write(b'1')
                    else:
                        print("\n>>> [TERKONFIRMASI] Objek Ilegal Valid! MENYALAKAN ALARM...")
                        if self.esp32: self.esp32.write(b'2')
                        
                    self.sudah_eksekusi = True
                    self.lbl_status.config(text=f"Status: EKSEKUSI -> {status_sekarang}", fg="blue")
                    
                # JIKA BELUM 5 DETIK
                elif not self.sudah_eksekusi:
                    self.lbl_status.config(text=f"Status: Mengonfirmasi {status_sekarang}... ({int(durasi_berjalan)} detik)", fg="#b8860b")
            else:
                self.objek_terakhir = status_sekarang
                self.waktu_mulai_deteksi = waktu_sekarang
                self.sudah_eksekusi = False
                print(f"\n[OBJEK BARU] Mendeteksi: {status_sekarang}. Mulai timer...")
                self.lbl_status.config(text=f"Status: [OBJEK BARU] Mendeteksi {status_sekarang}", fg="#b8860b")
        else:
            if self.objek_terakhir is not None:
                print("\n[KOSONG] Objek hilang dari kamera. Timer dibatalkan.")
                self.lbl_status.config(text="Status: SISTEM ONLINE", fg="green")
            self.objek_terakhir = None
            self.sudah_eksekusi = False
            self.waktu_mulai_deteksi = 0

        # ==========================================
        # RESIZE & CONVERT FRAME OPENCV KE TKINTER
        # ==========================================
        annotated_frame = results[0].plot()
        
        # Resize frame agar pas di UI (800x450 adalah rasio 16:9 dari 1280x720)
        frame_resized = cv2.resize(annotated_frame, (800, 450))
        
        # Convert BGR (OpenCV) ke RGB (Tkinter/Pillow)
        cv2image = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(cv2image)
        imgtk = ImageTk.PhotoImage(image=img)

        # Update label gambar di UI
        self.lbl_video.imgtk = imgtk
        self.lbl_video.configure(image=imgtk)

        # Panggil kembali fungsi ini setelah 15 ms untuk loop video
        self.root.after(15, self.update_frame)

    def quit_system(self):
        """Dieksekusi saat tombol Quit ditekan atau Jendela ditutup"""
        print("\nMematikan sistem dengan aman...")
        self.is_running = False
        if self.cap:
            self.cap.release()
        if self.esp32:
            self.esp32.close()
        self.root.quit()
        self.root.destroy()
        print("Program selesai dan sistem dimatikan.")

# ==========================================
# MENJALANKAN APLIKASI
# ==========================================
if __name__ == "__main__":
    root = tk.Tk()
    app = SmartTrashBinUI(root)
    
    # Menangani kejadian saat tombol 'X' di pojok kanan atas ditekan
    root.protocol("WM_DELETE_WINDOW", app.quit_system)
    
    root.mainloop()
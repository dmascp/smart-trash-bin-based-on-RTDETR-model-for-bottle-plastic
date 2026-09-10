#include <ESP32Servo.h>

Servo pintuServo;

// ==========================================
// DEKLARASI PIN
// ==========================================
const int pinServo = 13;   
const int pinBuzzer = 19;  

void setup() {
  Serial.begin(115200);

  // 1. KUNCI SERVO DI POSISI AWAL (180 Derajat)
  // Ini ekuivalen dengan titik awal yang Anda bayangkan sebagai -180
  pintuServo.attach(pinServo);
  pintuServo.write(180); 

  // 2. INISIALISASI BUZZER
  pinMode(pinBuzzer, OUTPUT);
  digitalWrite(pinBuzzer, LOW);

  // 3. BUNYI BEEP STARTUP
  delay(1000); 
  digitalWrite(pinBuzzer, HIGH);
  delay(800);  
  digitalWrite(pinBuzzer, LOW);
  
  Serial.println("==================================================");
  Serial.println("SISTEM READY (MODE SG90 PRESISI)");
  Serial.println("Menunggu sinyal deteksi dari VSCode...");
  Serial.println("==================================================");
}

void loop() {
  if (Serial.available() > 0) {
    char perintah = Serial.read(); 

    // ==========================================
    // LOGIKA 1: BOTOL PLASTIK -> TURUN KE BAWAH
    // ==========================================
    if (perintah == '1') {
      Serial.println(">> Botol Terdeteksi! Lengan turun ke bawah...");
      
      // Mundur 90 derajat (Ekuivalen dengan bergerak ke -90)
      pintuServo.write(90);      
      delay(3000);                
      
      Serial.println(">> Lengan kembali naik (Tiduran)...");
      
      // Kembali ke titik awal (Ekuivalen dengan kembali ke -180)
      pintuServo.write(180);        
    }
    
    // ==========================================
    // LOGIKA 2: OBJEK ILEGAL -> ALARM
    // ==========================================
    else if (perintah == '2') {
      Serial.println(">> Objek Asing! ALARM MENYALA...");
      
      for(int i = 0; i < 3; i++) {
        digitalWrite(pinBuzzer, HIGH); 
        delay(200);                    
        digitalWrite(pinBuzzer, LOW);  
        delay(200);                    
      }
    }
  }
}
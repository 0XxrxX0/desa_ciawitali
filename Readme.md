# 📊 Dashboard Survey Kepuasan Masyarakat (SKM)

![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white)

Dashboard interaktif untuk memvisualisasikan data **Survey Kepuasan Masyarakat** secara *real-time*. Aplikasi ini dirancang untuk membantu perangkat desa/instansi dalam memonitor kualitas pelayanan publik berdasarkan umpan balik masyarakat.

## 🌟 Fitur Utama

* **🟢 Live Data Integration:** Terhubung langsung dengan Google Sheets. Data akan terupdate otomatis setiap 60 detik begitu ada responden baru yang mengisi kuesioner.
* **🧹 Smart Data Cleaning:**
    * Membersihkan penulisan pekerjaan yang tidak standar (misal: "petani", "Petani ", "PETANI").
    * Mengelompokkan pekerjaan minoritas menjadi kategori "Lainnya" agar grafik tetap rapi.
* **📈 Analisis Skala Likert (1-5):** Visualisasi skor rata-rata per unsur pelayanan dengan indikator warna (Merah ke Hijau).
* **🎛️ Filter Interaktif:** Saring data berdasarkan Jenis Kelamin, Pendidikan, dan Pekerjaan.
* **💬 Portal Feedback:** Membaca keluhan dan saran masyarakat dalam format yang mudah dibaca.

## 📂 Struktur Data

Aplikasi ini mengharapkan data kuesioner dengan struktur kolom sebagai berikut (biasanya hasil ekspor Google Forms):
* **Demografi:** Nama, Umur, Jenis Kelamin, Pendidikan, Pekerjaan.
* **Unsur Pelayanan (Q1-Q9):** Skor 1-5 tentang Perilaku, Biaya, Waktu, Prosedur, dll.
* **Kualitatif:** Keluhan/Saran (Feedback) dan Link Bukti Foto.

## 🚀 Cara Menjalankan (Instalasi)

Pastikan kamu sudah menginstal Python di komputermu.

1.  **Clone atau Download repository ini.**
2.  **Install library yang dibutuhkan:**
    Buka terminal/CMD di folder proyek, lalu ketik:
    ```bash
    pip install streamlit pandas plotly
    ```
3.  **Jalankan Aplikasi:**
    ```bash
    streamlit run app.py
    ```
4.  Aplikasi akan terbuka otomatis di browser (biasanya di `http://localhost:8501`).

## ⚙️ Konfigurasi Data

### Menggunakan Google Sheets (Live)
1.  Buka Google Sheets hasil respon kuesioner.
2.  Klik **File** > **Share** > **Publish to web**.
3.  Pilih Sheet yang sesuai, dan ganti format ke **Comma-separated values (.csv)**.
4.  Copy link yang muncul.
5.  Buka `app.py`, lalu tempel link tersebut pada variabel:
    ```python
    GOOGLE_SHEET_URL = "paste_link_disini"
    ```

### Menggunakan File Lokal (Offline)
1.  Simpan file CSV di folder yang sama dengan `app.py`.
2.  Beri nama file: `Survey Kepuasan Masyarakat.csv`.
3.  Aplikasi akan otomatis menggunakannya jika internet mati.

## 📸 Preview

Dashboard mencakup metrik utama seperti:
* Total Responden
* Indeks Kepuasan Masyarakat (IKM)
* Rating Rata-rata (Skala 5)

---
*Dibuat dengan ❤️ menggunakan Streamlit.*

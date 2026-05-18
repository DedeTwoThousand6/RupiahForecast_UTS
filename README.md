# RupiahForecast - Enterprise AI Dashboard

RupiahForecast adalah dasbor intelijen finansial berbasis Machine Learning untuk melakukan prediksi dan segmentasi nilai tukar (kurs) USD ke IDR. Platform ini mengimplementasikan pemrosesan paralel (Multithreading) untuk menjalankan inferensi pada 5 model Machine Learning secara serempak.

## Fitur Utama

- **Inference Mode Paralel**: Menjalankan prediksi dari 5 model ML berbeda di waktu yang bersamaan.
- **Auto Sync (Yahoo Finance)**: Otomatis menarik riwayat data kurs USD/IDR 30 hari terakhir langsung dari bursa menggunakan `yfinance`.
- **Manual Input Mode**: Mendukung pengujian menggunakan data historis yang diisi manual oleh analis.
- **Export CSV**: Simpan hasil komparasi prediksi ke dalam file CSV untuk pelaporan (reporting).
- **Interactive Data Visualization**: Grafik visual komparatif (ApexCharts) dan akses lengkap galeri gambar *output* yang dihasilkan dari pelatihan di Jupyter Notebook.

## Model Algoritma yang Digunakan

Aplikasi ini menggunakan berbagai arsitektur AI yang terintegrasi:

1. **Linear Regression** (Scikit-Learn) - Regresi linear klasik untuk menemukan tren linear.
2. **K-Means Clustering** (Scikit-Learn) - Algoritma Unsupervised untuk membagi volatilitas pasar ke dalam beberapa klaster (Market Insight).
3. **Artificial Neural Network / ANN** (TensorFlow/Keras) - Model deep learning feed-forward.
4. **Custom Backpropagation** (TensorFlow/Keras) - Jaringan saraf yang dilatih menggunakan optimasi backpropagation tingkat lanjut.
5. **LSTM / RNN** (TensorFlow/Keras) - Recurrent Neural Network dengan arsitektur memori (Long Short-Term Memory) untuk data time-series.

## Prasyarat (Requirements)

Pastikan Python versi 3.9 hingga 3.11 sudah terinstal. Instal semua pustaka yang dibutuhkan menggunakan perintah:

```bash
pip install -r requirements.txt
```

Pustaka utama yang digunakan:
- `Flask` (Backend web)
- `TensorFlow` (Deep Learning models)
- `Scikit-Learn` (Machine Learning models)
- `yfinance` (Data bursa)
- `numpy` & `pandas` (Pemrosesan data)

## Cara Menjalankan Aplikasi

1. **Aktifkan Virtual Environment** (Jika ada):
   - Windows: `venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`

2. **Jalankan Aplikasi Flask**:
   Dari direktori proyek utama (folder yang berisi `app/` dan file ini), jalankan:
   ```bash
   python app/app.py
   ```

3. **Buka di Browser**:
   Buka peramban (browser) web Anda dan akses:
   👉 `http://127.0.0.1:5000`

## Struktur Direktori

```text
/
├── app/
│   ├── static/          # CSS, JavaScript, dan Gambar Grafik (dari notebook)
│   ├── templates/       # File HTML (layout.html, index.html, compare.html)
│   └── app.py           # Backend Flask & API
├── data/                # Dataset CSV awal (saat proses pelatihan)
├── model/               # Model Machine Learning & Scaler (.h5, .pkl, .joblib) tersimpan
├── notebook/            # Source code riset eksperimen (Jupyter Notebook)
├── extract_charts.py    # Script otomatis mengambil grafik hasil eksperimen dari .ipynb
├── requirements.txt     # Daftar dependencies / pustaka Python
└── README.md            # Dokumentasi ini
```

---
*Dikembangkan untuk eksperimen AI dan Prediksi Deret Waktu Finansial.*

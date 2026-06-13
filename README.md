# Jakarta Air QUality Command Center

**Dashboard BI ISPU DKI Jakarta** adalah aplikasi Streamlit untuk membaca kondisi kualitas udara DKI Jakarta berdasarkan data historis ISPU pada unit observasi **tanggal-stasiun**. Dashboard ini dirancang sebagai alat bantu pengambilan keputusan bagi pimpinan dan tim teknis, dengan fokus pada kondisi risiko, lokasi prioritas, pencemar kritis, pola temporal, pola musiman, serta kepercayaan data.

Dashboard ini menggunakan pendekatan **decision dashboard**, sehingga tidak hanya menampilkan grafik, tetapi juga menyajikan insight dan arahan tindakan berbasis data.

---

## 1. Tujuan Aplikasi

Aplikasi ini dibuat untuk membantu Dinas Lingkungan Hidup membaca pertanyaan utama berikut:

1. Bagaimana kondisi umum kualitas udara Jakarta pada periode aktif?
2. Apakah kualitas udara membaik, memburuk, atau relatif stabil dari waktu ke waktu?
3. Stasiun pemantau mana yang perlu menjadi prioritas pengendalian?
4. Pencemar kritis apa yang paling dominan dan perlu menjadi fokus kebijakan?
5. Bulan atau periode apa yang paling rawan terhadap kondisi Tidak Sehat+?
6. Seberapa layak data digunakan sebagai dasar keputusan historis dan evaluatif?

---

## 2. Fitur Utama

### A. Overview Kualitas Udara
Menampilkan ringkasan eksekutif kondisi kualitas udara pada filter aktif, meliputi:

- rata-rata ISPU;
- median ISPU;
- persentase observasi Tidak Sehat+;
- kategori ISPU dominan;
- stasiun prioritas;
- pencemar dominan;
- distribusi kategori ISPU;
- distribusi pencemar kritis;
- tabel prioritas per stasiun.

### B. Tren Temporal
Menampilkan perubahan kualitas udara dari waktu ke waktu dengan pilihan granularitas:

- harian;
- bulanan;
- tahunan.

Fitur tambahan pada tren:

- garis ambang Tidak Sehat pada ISPU 101;
- opsi menampilkan seluruh threshold ISPU;
- anotasi periode khusus seperti COVID-19 sebagai konteks aktivitas;
- anotasi ketersediaan PM2.5;
- perbandingan tahun terakhir terhadap tahun sebelumnya dan rata-rata historis.

### C. Perbandingan Stasiun
Menampilkan prioritas lokasi berdasarkan stasiun pemantau, meliputi:

- peta interaktif titik SPKU Jakarta;
- ranking risiko Tidak Sehat+ per stasiun;
- bubble chart prioritas stasiun;
- stacked bar komposisi kategori ISPU per stasiun;
- tabel ringkas keputusan lokasi.

Catatan penting: peta menampilkan **titik stasiun pemantau**, bukan pewarnaan seluruh wilayah Jakarta dan bukan interpolasi sebaran polusi.

### D. Pencemar Kritis
Menampilkan parameter pencemar yang paling sering menjadi pembentuk indeks tertinggi, meliputi:

- pencemar kritis dominan;
- pencemar dominan saat kondisi Tidak Sehat+;
- heatmap frekuensi pencemar kritis per stasiun;
- stacked bar komposisi pencemar kritis per stasiun;
- stacked bar perubahan pencemar kritis per tahun;
- mode pembacaan adil untuk memperhitungkan ketersediaan PM2.5.

Mode pembacaan pencemar kritis:

1. Semua data aktif;
2. Sejak PM2.5 tersedia;
3. Observasi dengan semua parameter tersedia.

### E. Pola Musiman
Menampilkan pola kualitas udara berdasarkan bulan, meliputi:

- bulan dengan rata-rata ISPU tertinggi;
- bulan dengan persentase Tidak Sehat+ tertinggi;
- bulan relatif terbaik;
- pencemar dominan pada bulan rawan;
- heatmap pola musiman;
- grafik bulanan per stasiun;
- kalender antisipasi operasional.

### F. Data Quality / Audit Trail
Menampilkan kepercayaan data dan batasan interpretasi, meliputi:

- status kelayakan data;
- periode data;
- jumlah observasi final;
- jumlah stasiun;
- duplikasi final;
- Decision Confidence;
- coverage data per tahun;
- coverage parameter pencemar;
- timeline ketersediaan parameter;
- heatmap ketersediaan parameter per tahun;
- hasil validasi akhir;
- cleaning log;
- audit duplikasi;
- guardrail kapan angka tidak boleh dibandingkan langsung.

---

## 3. Konsep Desain UI/UX

Dashboard menggunakan konsep **Jakarta Air Quality Decision Observatory**, dengan karakter visual:

- tema terang agar nyaman dibaca oleh pimpinan dan stakeholder non-teknis;
- warna kategori ISPU yang konsisten;
- kartu KPI eksekutif;
- chart interaktif berbasis Plotly;
- insight berbasis format Temuan → Makna → Arahan tindakan → Batasan;
- watermark halus skyline Jakarta dan Monas sebagai identitas visual kota;
- legenda, annotation, dan label chart dibuat kontras agar mudah dibaca pada tampilan Streamlit Cloud.

Identitas “Ini Jakarta” ditampilkan melalui siluet SVG Jakarta secara halus dan transparan, tanpa mengganggu keterbacaan grafik, tabel, maupun teks.

---

## 4. Struktur File yang Disarankan

Gunakan struktur folder berikut saat menjalankan aplikasi:

```text
project-dashboard-ispu-jakarta/
├── app.py
├── requirements.txt
├── README_Dashboard_BI_ISPU_DKI_Jakarta.md
├── data/
│   ├── Clean_Dataset_ISPU_Jakarta_Tugas_3_4_5_FINAL.csv
│   ├── Data_Cleaning_Log_ISPU_Jakarta_Tugas_3_4_5_FINAL.csv
│   ├── Audit_Duplikasi_Tanggal_Stasiun_ISPU_Jakarta_FINAL.csv
│   └── Validasi_Final_Clean_Dataset_ISPU_Jakarta_FINAL.csv
└── assets/
    └── jakarta_skyline_watermark.svg  # opsional bila memakai aset eksternal
```

Pada versi saat ini, watermark Jakarta sudah dimasukkan langsung ke dalam CSS aplikasi sebagai data URI, sehingga file SVG eksternal bersifat opsional.

---

## 5. Kebutuhan Sistem

Aplikasi membutuhkan Python dan beberapa pustaka utama:

```text
streamlit
pandas
numpy
plotly
```

Rekomendasi versi:

```text
Python >= 3.10
streamlit >= 1.30
pandas >= 2.0
numpy >= 1.24
plotly >= 5.18
```

Contoh isi `requirements.txt`:

```text
streamlit>=1.30
pandas>=2.0
numpy>=1.24
plotly>=5.18
```

---

## 6. Cara Menjalankan di Lokal

### 1. Buat virtual environment

```bash
python -m venv .venv
```

### 2. Aktifkan virtual environment

Windows:

```bash
.venv\Scripts\activate
```

macOS/Linux:

```bash
source .venv/bin/activate
```

### 3. Install dependency

```bash
pip install -r requirements.txt
```

### 4. Jalankan aplikasi

```bash
streamlit run app.py
```

Setelah berjalan, buka URL lokal yang muncul di terminal, biasanya:

```text
http://localhost:8501
```

---

## 7. Cara Deploy ke Streamlit Cloud

1. Upload seluruh folder project ke GitHub.
2. Pastikan file utama bernama `app.py`.
3. Pastikan `requirements.txt` tersedia di root repository.
4. Pastikan folder `data/` berisi seluruh file CSV yang dibutuhkan.
5. Buka Streamlit Cloud.
6. Pilih repository GitHub.
7. Set main file path:

```text
app.py
```

8. Klik Deploy.

Jika ada perubahan kode, lakukan:

```bash
git add .
git commit -m "Update dashboard ISPU Jakarta"
git push
```

Streamlit Cloud akan melakukan redeploy otomatis.

---

## 8. Kontrak Data

Dataset utama harus memiliki minimal kolom berikut:

| Kolom | Keterangan |
|---|---|
| `tanggal_clean` atau `tanggal` | tanggal observasi |
| `stasiun` | nama/kode stasiun pemantau |
| `max` | nilai indeks ISPU maksimum pada observasi |
| `categori` | kategori ISPU |
| `critical` | parameter pencemar pembentuk indeks tertinggi |

Kolom pendukung yang direkomendasikan:

| Kolom | Keterangan |
|---|---|
| `pm10` | nilai indeks PM10 |
| `pm25` | nilai indeks PM2.5 |
| `so2` | nilai indeks SO2 |
| `co` | nilai indeks CO |
| `o3` | nilai indeks O3 |
| `no2` | nilai indeks NO2 |
| `flag_tidak_sehat_plus` | penanda kategori Tidak Sehat, Sangat Tidak Sehat, atau Berbahaya |
| `flag_multi_critical` | penanda jika ada lebih dari satu parameter critical |
| `used_for_main_dashboard_kpi` | penanda data yang digunakan untuk KPI utama |

Jika kolom rekomendasi tidak tersedia, beberapa panel diagnostik tetap berjalan tetapi informasi yang ditampilkan menjadi lebih terbatas.

---

## 9. Definisi Metrik Utama

### Unit Observasi
Unit utama dashboard adalah:

```text
tanggal-stasiun
```

Artinya, satu baris data merepresentasikan kondisi pada satu tanggal dan satu stasiun pemantau.

### Tidak Sehat+
Tidak Sehat+ mencakup kategori:

- Tidak Sehat;
- Sangat Tidak Sehat;
- Berbahaya.

### Persentase Tidak Sehat+
Dihitung sebagai:

```text
jumlah observasi Tidak Sehat+ / seluruh observasi pada filter aktif × 100%
```

### Pencemar Kritis
`critical` menunjukkan parameter pembentuk nilai indeks tertinggi pada observasi tersebut. Nilai ini tidak boleh dibaca sebagai konsentrasi fisik terbesar atau penyebab tunggal pencemaran.

### Status Risiko Stasiun
Dashboard menggunakan segmentasi praktis:

| Status | Kriteria |
|---|---:|
| Prioritas Tinggi | Tidak Sehat+ ≥ 30% |
| Prioritas Menengah | Tidak Sehat+ 15%–29% |
| Prioritas Pemantauan | Tidak Sehat+ < 15% |

Segmentasi ini digunakan untuk membantu prioritas pemantauan dan bukan pengganti ketentuan resmi kebijakan.

---

## 10. Catatan Kontekstual Penting

### A. PM2.5 Tidak Selalu Tersedia di Seluruh Periode
Dashboard menampilkan timeline ketersediaan parameter karena PM2.5 dan parameter lain bisa memiliki cakupan historis yang berbeda. Jika PM2.5 baru tersedia mulai periode tertentu, maka ketiadaan PM2.5 pada tahun awal tidak boleh dibaca sebagai PM2.5 rendah.

Cara baca yang benar:

- gunakan mode “Sejak PM2.5 tersedia” saat membandingkan pencemar kritis;
- gunakan persentase, bukan jumlah mentah;
- baca hasil bersama coverage data.

### B. Periode COVID-19 Ditandai sebagai Konteks
Grafik tren menandai periode COVID-19 / pembatasan aktivitas sebagai konteks interpretasi.

Catatan penting:

- annotation COVID-19 bukan klaim sebab-akibat;
- untuk menyimpulkan dampak COVID-19 terhadap kualitas udara, diperlukan analisis kausal dan data aktivitas pendukung.

### C. Dashboard Bukan Real-Time
Dashboard ini menggunakan data historis. Karena itu, hasilnya aman untuk:

- evaluasi historis;
- prioritas lokasi;
- identifikasi pencemar dominan;
- kalender periode rawan;
- bahan diskusi kebijakan berbasis data.

Dashboard ini tidak boleh digunakan sebagai satu-satunya dasar untuk menyatakan status udara hari ini tanpa data pemantauan terbaru.

---

## 11. Cara Membaca Peta Interaktif

Peta pada menu **Perbandingan Stasiun** menampilkan titik SPKU Jakarta.

| Elemen Peta | Makna |
|---|---|
| Titik/marker | lokasi stasiun pemantau |
| Warna marker | status risiko berdasarkan % Tidak Sehat+ |
| Ukuran marker | intensitas risiko Tidak Sehat+ |
| Tooltip | ringkasan stasiun, wilayah, rata-rata ISPU, % Tidak Sehat+, pencemar dominan, dan jumlah observasi |

Catatan metodologis:

- peta bukan interpolasi sebaran polusi;
- peta tidak mewarnai seluruh wilayah administratif Jakarta;
- titik SPKU tidak otomatis mewakili seluruh kecamatan/kota administratif.

---

## 12. Guardrail Interpretasi

Gunakan batasan berikut saat membaca dashboard:

| Kondisi | Risiko Salah Tafsir | Cara Baca yang Benar |
|---|---|---|
| PM2.5 tersedia mulai periode tertentu | PM2.5 tampak tidak dominan pada tahun awal | Bandingkan PM2.5 hanya pada periode ketika datanya tersedia |
| Periode COVID-19 | Perubahan tren dianggap pasti akibat COVID-19 | Baca sebagai konteks, bukan bukti sebab-akibat |
| Jumlah observasi antar stasiun berbeda | Ranking berbasis jumlah mentah menjadi bias | Gunakan persentase dan coverage |
| Critical menunjukkan indeks tertinggi | Dianggap sebagai penyebab tunggal | Validasi dengan sumber emisi, meteorologi, dan data lapangan |
| Data historis | Dianggap sebagai kondisi udara saat ini | Gunakan data real-time untuk keputusan harian |

---

## 13. Troubleshooting

### A. Error: clean dataset tidak ditemukan
Pastikan file berikut tersedia di folder `data/`:

```text
Clean_Dataset_ISPU_Jakarta_Tugas_3_4_5_FINAL.csv
```

### B. Error: kolom wajib hilang
Pastikan dataset memiliki kolom wajib:

```text
tanggal_clean/tanggal, stasiun, max, categori, critical
```

### C. Grafik kosong
Kemungkinan filter terlalu sempit. Longgarkan filter tanggal, stasiun, kategori, atau pencemar kritis.

### D. Peta tidak muncul
Pastikan koneksi internet tersedia karena basemap menggunakan tile map online dari Plotly/Carto.

### E. Tampilan berbeda di Streamlit Cloud
Pastikan file `app.py` terbaru sudah di-push ke GitHub dan Streamlit Cloud sudah melakukan redeploy.

---

## 14. Rekomendasi Pengembangan Lanjutan

Dashboard dapat diperkuat dengan integrasi data tambahan:

| Data Tambahan | Manfaat |
|---|---|
| Curah hujan | membaca pengaruh musim hujan/kemarau terhadap partikulat |
| Arah dan kecepatan angin | memahami potensi pergerakan polutan |
| Suhu dan kelembapan | membantu interpretasi O3 dan partikulat |
| Volume lalu lintas | mendukung analisis sumber emisi transportasi |
| Hotspot/kebakaran | membaca episode partikulat tertentu |
| Data industri/konstruksi | membantu validasi sumber emisi lokal |
| Data real-time SPKU | mendukung keputusan operasional harian |

Untuk tahap lanjutan, dashboard juga dapat dikembangkan menjadi model prediktif kualitas udara, tetapi perlu data meteorologi, aktivitas emisi, dan validasi model yang memadai.

---

## 15. Ringkasan untuk Stakeholder

Dashboard ini membantu pimpinan membaca kualitas udara Jakarta secara lebih terarah:

```text
Apa kondisinya?
Di mana lokasi prioritasnya?
Pencemar apa yang dominan?
Kapan periode rawannya?
Seberapa kuat data untuk mendukung keputusan?
Apa batasan interpretasinya?
```

Dengan struktur tersebut, dashboard tidak hanya menjadi alat visualisasi, tetapi juga alat bantu keputusan berbasis data untuk pengendalian kualitas udara DKI Jakarta.

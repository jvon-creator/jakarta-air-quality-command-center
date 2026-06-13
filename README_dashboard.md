# Dashboard BI ISPU DKI Jakarta — Light Tables Revisi

Dashboard Streamlit untuk Tugas 6 Business Intelligence Analisis ISPU DKI Jakarta.

## Fokus revisi ini

Versi ini memperbaiki tampilan tabel agar konsisten dengan **light theme** dashboard:

- tabel Ringkasan Prioritas per Stasiun;
- tabel Tabel Ringkas Keputusan Lokasi;
- tabel Kalender Antisipasi Operasional;
- tabel Hasil Validasi Akhir;
- tabel Jejak Pembersihan Data;
- tabel Audit Duplikasi Tanggal-Stasiun.

Tabel tidak lagi memakai renderer `st.dataframe` bawaan yang dapat mengikuti dark theme browser/Streamlit. Semua tabel penting dirender sebagai **custom light executive table** dengan:

- background putih/soft blue;
- teks utama navy gelap;
- header terang dengan kontras tinggi;
- progress bar merah-oranye-hijau untuk % Tidak Sehat+;
- chip warna untuk kategori, pencemar, dan status;
- scroll horizontal/vertikal untuk tabel panjang;
- teks panjang tetap dapat dibaca tanpa merusak layout.

## Cara menjalankan

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Struktur file deployment

Pastikan file berikut ada di root repository Streamlit Cloud:

```text
app.py
requirements.txt
README_dashboard.md
.streamlit/config.toml
data/
```

Folder `data/` harus berisi:

```text
Clean_Dataset_ISPU_Jakarta_Tugas_3_4_5_FINAL.csv
Data_Cleaning_Log_ISPU_Jakarta_Tugas_3_4_5_FINAL.csv
Audit_Duplikasi_Tanggal_Stasiun_ISPU_Jakarta_FINAL.csv
Validasi_Final_Clean_Dataset_ISPU_Jakarta_FINAL.csv
```

## Catatan interpretasi

Dashboard ini menggunakan unit observasi **tanggal-stasiun**. Persentase Tidak Sehat+ berarti persentase observasi tanggal-stasiun yang masuk kategori Tidak Sehat, Sangat Tidak Sehat, atau Berbahaya pada filter aktif.

Dashboard bersifat **deskriptif-diagnostik** dan menggunakan data historis, bukan status udara real-time.

## Revisi Light Table

Versi ini mengganti tabel penting dari `st.dataframe` menjadi tabel HTML light theme berkontras tinggi. Tujuannya agar tabel ringkasan prioritas per stasiun, tabel keputusan lokasi, kalender antisipasi operasional, hasil validasi akhir, jejak pembersihan data, dan audit duplikasi tetap mudah dibaca meskipun browser atau Streamlit mewarisi preferensi dark mode.

Prinsip desain tabel:
- latar tabel putih dan header biru muda;
- teks utama navy gelap untuk kontras tinggi;
- bar persentase tetap berwarna tetapi label angka tetap gelap;
- badge status risiko menggunakan warna lembut dengan teks gelap;
- kolom panjang seperti arahan operasional dan justifikasi dapat membungkus teks.

## Revisi UI terbaru

Bagian chip/pill pada hero yang berisi `Ambang keputusan`, `Metrik utama`, `Unit`, dan `Data historis` telah dihapus agar header lebih bersih dan KPI utama lebih cepat terlihat.


## Revisi Active Observations

- Kartu periode data pada header sekarang mengikuti periode data yang aktif setelah filter sidebar diterapkan.
- Ditambahkan indikator jumlah observasi aktif pada kartu periode agar denominator KPI langsung terlihat.

## Revisi No Redundant KPI

Versi ini menghapus decision cards kecil di bawah hero agar tidak mengulang informasi yang sudah muncul pada KPI utama. Header hanya menampilkan konteks data aktif: periode data aktif, jumlah observasi aktif, status clean dataset, dan catatan bahwa data bersifat historis. Satu-satunya pusat KPI eksekutif berada pada bagian **Napas Kota Terkini**, yang kini memuat rata-rata ISPU, median ISPU, % Tidak Sehat+, kategori dominan, stasiun prioritas, dan pencemar dominan.


## Revisi visual heatmap

Versi ini memperbaiki keterbacaan legenda/colorbar heatmap dan menambahkan angka jumlah observasi pada setiap petak heatmap pencemar kritis per stasiun, sehingga stakeholder dapat membaca intensitas warna sekaligus nilai absolutnya.


## Revisi Peta Interaktif SPKU

Dashboard menambahkan peta interaktif pada menu **Perbandingan Stasiun** dengan pendekatan metodologis yang aman:

- Peta menampilkan **titik lokasi SPKU**, bukan pewarnaan seluruh wilayah Jakarta.
- Warna marker menunjukkan **status risiko** berdasarkan persentase observasi Tidak Sehat+ pada filter aktif.
- Ukuran marker menunjukkan intensitas frekuensi Tidak Sehat+.
- Tooltip menampilkan stasiun, wilayah, rata-rata ISPU, % Tidak Sehat+, kategori dominan, pencemar dominan, dan jumlah observasi aktif.
- Koordinat stasiun digunakan sebagai titik aproksimasi untuk konteks visual, sehingga interpretasi kebijakan tetap perlu dilengkapi validasi lapangan dan data sumber emisi.

Catatan penting: peta ini tidak melakukan interpolasi kualitas udara dan tidak menyimpulkan kondisi seluruh kecamatan/kota administratif dari satu titik stasiun.

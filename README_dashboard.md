# Dashboard BI ISPU DKI Jakarta

Dashboard Streamlit ini disusun untuk Tugas 6 Business Intelligence Dashboard berdasarkan clean dataset final Tugas 3–5.

## Filosofi visual

Desain revisi menggunakan konsep **Jakarta Air Quality Observatory**: dashboard dibaca seperti ruang observasi kualitas udara yang menampilkan lapisan atmosfer, jejak partikel, ambang risiko, dan sinyal kesehatan kota. Tampilan tidak memakai gaya dashboard generik, tetapi membangun identitas visual dari tema kualitas udara: latar atmospheric, glass sensor panel, spektrum kategori ISPU, KPI cards seperti panel pemantau, dan garis threshold ISPU 101 sebagai batas awal kondisi Tidak Sehat.

## Isi dashboard

- Overview Kualitas Udara
- Tren Temporal
- Perbandingan Stasiun
- Pencemar Kritis
- Pola Musiman
- Data Quality / Audit Trail

## Cara menjalankan

```bash
pip install -r requirements.txt
streamlit run app.py
```

## File data yang digunakan

File CSV diletakkan pada folder `data/`:

- `Clean_Dataset_ISPU_Jakarta_Tugas_3_4_5_FINAL.csv`
- `Data_Cleaning_Log_ISPU_Jakarta_Tugas_3_4_5_FINAL.csv`
- `Audit_Duplikasi_Tanggal_Stasiun_ISPU_Jakarta_FINAL.csv`
- `Validasi_Final_Clean_Dataset_ISPU_Jakarta_FINAL.csv`

## Catatan interpretasi

Dashboard ini menggunakan clean dataset final yang telah divalidasi dan dibuat unik pada level tanggal-stasiun. Tampilan default menggunakan tahun terakhir tersedia karena keputusan pimpinan membutuhkan konteks terkini. Data historis tetap tersedia melalui filter sebagai pembanding tren, lokasi, pencemar dominan, dan pola musiman.

Data dashboard bukan data real-time, sehingga keputusan operasional harian tetap membutuhkan data terbaru dari sistem pemantauan berjalan.

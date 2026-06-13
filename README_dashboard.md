# Dashboard BI ISPU DKI Jakarta — Colorful High-Contrast Edition

Dashboard Streamlit ini dirancang sebagai **Air Quality Decision Dashboard** untuk membantu Kepala Dinas Lingkungan Hidup membaca kondisi kualitas udara, lokasi prioritas, pencemar dominan, periode rawan, dan tingkat kepercayaan data.

## Prinsip revisi terbaru

Versi ini memperbaiki desain agar lebih berwarna tetapi tetap mudah dibaca:

- Mengganti palet muted yang terlalu lembut menjadi **Air Quality Spectrum Palette** yang lebih hidup.
- Memastikan semua teks utama menggunakan warna gelap berkontras tinggi (`#102033`) di atas panel putih.
- Mengurangi risiko teks cerah di atas latar cerah dengan panel chart, KPI, hero, insight, dan sidebar berbasis permukaan putih.
- Menjaga warna kategori ISPU tetap intuitif: hijau, kuning, oranye, merah, dan ungu.
- Mempertahankan signature visual **Air Quality Ribbon** sebagai legenda spektrum risiko yang aktif mengikuti filter.
- Menjaga dashboard tetap light theme agar nyaman untuk presentasi dan penggunaan lama.

## Palet visual utama

| Peran | Hex | Keterangan |
|---|---:|---|
| Background | `#F7FBFF` | Langit terang bersih |
| Panel/card | `#FFFFFF` | Permukaan baca berkontras tinggi |
| Teks utama | `#102033` | Navy gelap agar terbaca jelas |
| Teks sekunder | `#334155` | Slate gelap untuk deskripsi |
| BAIK | `#00A676` | Hijau udara baik |
| SEDANG | `#F4B400` | Kuning pemantauan |
| TIDAK SEHAT | `#F97316` | Oranye risiko meningkat |
| SANGAT TIDAK SEHAT | `#E11D48` | Merah risiko tinggi |
| BERBAHAYA | `#7C3AED` | Ungu kondisi ekstrem |
| PM10 | `#0284C7` | Biru sensor partikulat |
| PM2.5 | `#16A34A` | Hijau partikulat halus |

## Isi dashboard

1. **Overview Kualitas Udara** — kondisi terkini dan prioritas cepat.
2. **Tren Temporal** — arah perubahan dan periode melewati ambang risiko.
3. **Perbandingan Stasiun** — lokasi prioritas pengendalian.
4. **Pencemar Kritis** — parameter pencemar yang perlu dikendalikan.
5. **Pola Musiman** — kalender antisipasi periode rawan.
6. **Data Quality / Audit Trail** — kelayakan data untuk keputusan.

Default analisis menggunakan **tahun terakhir tersedia** karena keputusan pimpinan membutuhkan kondisi yang paling relevan saat ini.

## File yang dibutuhkan

Pastikan folder `data/` berisi:

- `Clean_Dataset_ISPU_Jakarta_Tugas_3_4_5_FINAL.csv`
- `Data_Cleaning_Log_ISPU_Jakarta_Tugas_3_4_5_FINAL.csv`
- `Audit_Duplikasi_Tanggal_Stasiun_ISPU_Jakarta_FINAL.csv`
- `Validasi_Final_Clean_Dataset_ISPU_Jakarta_FINAL.csv`

## Cara menjalankan lokal

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Catatan deployment Streamlit Cloud

Jika dashboard terlihat kosong atau hanya menampilkan background, cek hal berikut:

1. Pastikan seluruh file CSV di folder `data/` ikut terunggah ke repository.
2. Pastikan nama file sama persis dengan daftar file di atas.
3. Pastikan `requirements.txt` terbaca oleh Streamlit Cloud.
4. Pastikan folder `.streamlit/` dan `config.toml` ikut terunggah agar light theme aktif.
5. Jika filter menghasilkan nol data, dashboard akan menampilkan empty state, bukan grafik kosong.

## Cara membaca dashboard

Ukuran utama yang dipakai adalah **% Tidak Sehat+**, karena lebih mudah diterjemahkan sebagai frekuensi risiko dibanding rata-rata ISPU saja. Rata-rata ISPU tetap ditampilkan sebagai indikator tekanan pencemaran, sedangkan `critical` dipakai untuk melihat pencemar yang paling sering membentuk nilai indeks tertinggi.

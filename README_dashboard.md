# Dashboard BI ISPU DKI Jakarta — Muted Anime Sky Decision Dashboard

Dashboard Streamlit ini dirancang sebagai **Observatorium Langit Udara Jakarta**: dashboard Business Intelligence untuk membantu Kepala Dinas Lingkungan Hidup membaca kondisi kualitas udara, lokasi prioritas, pencemar dominan, periode rawan, dan tingkat kepercayaan data.

## Improvement versi ini

Versi ini memperbaiki dashboard dari sekadar visualisasi menjadi **decision dashboard**:

- Hero dibuat lebih ringkas agar layar pertama langsung menampilkan sinyal keputusan.
- Ditambahkan **decision tiles**: status rata-rata ISPU, % Tidak Sehat+, prioritas lokasi, dan pencemar dominan.
- Ditambahkan **Air Quality Ribbon** sebagai signature visual yang memperlihatkan spektrum kategori ISPU pada filter aktif.
- Setiap menu memiliki **pertanyaan keputusan** agar grafik dibaca sebagai dasar tindakan, bukan sekadar gambar.
- Sidebar diberi keterangan fungsi halaman agar navigasi lebih jelas untuk stakeholder.
- Empty state diperbaiki agar dashboard tidak tampak kosong ketika filter menghasilkan nol data.
- Plotly chart diberi panel visual agar tampil seperti dashboard BI profesional.

## Filosofi desain

Tema visual menggunakan inspirasi **muted anime sky**: langit senja, awan biru pastel, dedaunan hijau, kabut amber, dan warna risiko ISPU yang diredam agar nyaman untuk antarmuka data. Estetika ini dipilih karena kualitas udara secara visual sangat dekat dengan langit, lapisan atmosfer, kabut, dan partikel halus.

Palet warna utama:

| Peran visual | Warna | Hex |
|---|---|---:|
| Paper sky | Putih krem langit | `#FFF9EF` |
| Pastel cloud blue | Awan biru lembut | `#C5DEE4` |
| Leaf oxygen | Hijau dedaunan | `#6D9F75` |
| Haze amber | Kuning kabut | `#D5B76A` |
| Sunset dust | Oranye senja/polusi | `#C8845E` |
| Muted alert red | Merah risiko | `#B95F5C` |
| Twilight violet | Ungu ekstrem | `#7E668C` |
| Ink slate | Teks utama | `#2E4251` |

## Sistem warna kategori ISPU

| Kategori | Makna visual |
|---|---|
| BAIK | Udara relatif aman |
| SEDANG | Perlu dipantau |
| TIDAK SEHAT | Risiko mulai meningkat |
| SANGAT TIDAK SEHAT | Risiko tinggi |
| BERBAHAYA | Kondisi ekstrem |

## Isi dashboard

Dashboard terdiri atas menu:

1. **Overview Kualitas Udara** — kondisi terkini dan prioritas cepat.
2. **Tren Temporal** — arah perubahan dan periode melewati ambang risiko.
3. **Perbandingan Stasiun** — lokasi prioritas pengendalian.
4. **Pencemar Kritis** — parameter pencemar yang perlu dikendalikan.
5. **Pola Musiman** — kalender antisipasi periode rawan.
6. **Data Quality / Audit Trail** — kelayakan data untuk keputusan.

Default analisis menggunakan **tahun terakhir tersedia** karena keputusan pimpinan membutuhkan kondisi yang paling relevan saat ini. Data historis tetap tersedia melalui filter.

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

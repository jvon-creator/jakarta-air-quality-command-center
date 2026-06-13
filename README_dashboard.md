# Dashboard BI ISPU DKI Jakarta — Decision-Safe Color Contrast Edition

Dashboard Streamlit ini dirancang sebagai **Observatorium Langit Udara Jakarta**: dashboard Business Intelligence untuk membantu Kepala Dinas Lingkungan Hidup membaca kondisi kualitas udara, lokasi prioritas, pencemar dominan, periode rawan, dan tingkat kepercayaan data.

Versi ini memperkuat dashboard agar lebih aman untuk pengambilan keputusan, lebih jelas secara metodologi, dan lebih mudah dibaca dari sisi UI/UX.

## Revisi utama versi ini

- Hero dibuat lebih compact agar KPI utama lebih cepat terlihat di layar pertama.
- Ditambahkan badge permanen **Data historis · bukan status udara real-time**.
- Semua persentase risiko diperjelas sebagai **% observasi tanggal-stasiun**, bukan otomatis dibaca sebagai % hari Jakarta.
- KPI dan insight otomatis kini menyertakan denominator, misalnya jumlah observasi tanggal-stasiun pada filter aktif.
- Ditambahkan **schema validation** untuk memeriksa kolom wajib sebelum dashboard berjalan.
- Ditambahkan catatan bahwa dashboard bersifat **deskriptif-diagnostik**, bukan prediktif.
- Import yang tidak digunakan dibersihkan agar kode lebih rapi.
- Empty state dan error state tetap dipertahankan agar dashboard tidak tampak kosong saat data/filter bermasalah.

## Filosofi desain

Tema visual menggunakan konsep **Air Quality Spectrum**: dashboard light theme yang berwarna, tetapi tetap menjaga kontras tinggi. Warna utama mengambil inspirasi dari udara, langit, vegetasi, kabut, dan spektrum risiko ISPU.

Prinsip visual:

- Background boleh berwarna, tetapi konten utama berada di panel putih.
- Teks utama memakai navy gelap agar terbaca di semua panel.
- Warna kategori ISPU tetap tegas dan konsisten.
- Panel insight menggunakan warna lembut, tetapi teks tetap gelap.
- Elemen dekoratif tidak boleh mengalahkan keterbacaan data.

## Sistem warna kategori ISPU

| Kategori | Warna | Fungsi |
|---|---:|---|
| BAIK | Hijau | Udara relatif aman |
| SEDANG | Kuning | Perlu dipantau |
| TIDAK SEHAT | Oranye | Risiko mulai meningkat |
| SANGAT TIDAK SEHAT | Merah | Risiko tinggi |
| BERBAHAYA | Ungu | Kondisi ekstrem |

## Isi dashboard

Dashboard terdiri atas menu:

1. **Overview Kualitas Udara** — kondisi terkini dan prioritas cepat.
2. **Tren Temporal** — arah perubahan dan periode melewati ambang risiko.
3. **Perbandingan Stasiun** — lokasi prioritas pengendalian.
4. **Pencemar Kritis** — parameter pencemar yang perlu dikendalikan.
5. **Pola Musiman** — kalender antisipasi periode rawan.
6. **Data Quality / Audit Trail** — kelayakan data untuk keputusan.

Default analisis menggunakan **tahun terakhir tersedia** karena keputusan pimpinan membutuhkan kondisi yang paling relevan saat ini. Data historis tetap tersedia melalui filter.

## Data contract

Clean dataset minimal harus memiliki salah satu kolom tanggal:

- `tanggal_clean`; atau
- `tanggal`.

Kolom wajib:

- `stasiun`
- `max`
- `categori`
- `critical`

Kolom rekomendasi:

- `pm10`
- `pm25`
- `so2`
- `co`
- `o3`
- `no2`
- `flag_tidak_sehat_plus`

Jika kolom wajib hilang, dashboard akan menampilkan error yang menjelaskan kolom mana yang belum sesuai kontrak data.

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

Ukuran utama yang dipakai adalah **% observasi Tidak Sehat+** pada unit **tanggal-stasiun**. Artinya, denominator adalah jumlah observasi pada filter aktif, bukan otomatis jumlah hari kalender Jakarta.

Untuk membaca “hari Jakarta Tidak Sehat+”, diperlukan agregasi khusus per tanggal, misalnya satu hari dianggap Tidak Sehat+ jika minimal satu stasiun masuk kategori Tidak Sehat+. Dashboard ini tetap memakai unit tanggal-stasiun agar perbandingan antar stasiun dan periode konsisten.

Nilai `max` adalah indeks ISPU, bukan konsentrasi polutan mentah. Kolom `critical` menunjukkan parameter pembentuk indeks tertinggi pada observasi tersebut. Pada kasus multi-critical, interpretasi pencemar dominan perlu hati-hati.

Dashboard ini bersifat **deskriptif-diagnostik**, bukan prediktif. Untuk prediksi kualitas udara diperlukan model tambahan dengan variabel meteorologi, emisi, lalu lintas, aktivitas industri, dan validasi lapangan.

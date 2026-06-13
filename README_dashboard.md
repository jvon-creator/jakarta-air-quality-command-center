# Dashboard BI ISPU DKI Jakarta — Light Air Quality Theme

Dashboard Streamlit ini dirancang sebagai **Jakarta Air Quality Observatory**: tampilan Business Intelligence yang ringan, terang, dan mencerminkan tema kualitas udara melalui lapisan atmosfer, partikel halus, panel sensor, dan warna kategori ISPU.

## Filosofi desain

Desain menggunakan **light theme** agar dashboard lebih mudah dibaca saat dipresentasikan kepada stakeholder pemerintah. Identitas visual mengikuti konsep kualitas udara:

- **Sky blue** untuk atmosfer dan pemantauan udara.
- **Oxygen green** untuk kondisi baik dan aman.
- **Haze yellow** untuk kondisi sedang/perlu dipantau.
- **Particulate orange** untuk risiko tidak sehat.
- **Alert red** untuk risiko tinggi.
- **Ozone violet** untuk kondisi ekstrem/berbahaya.

Signature visual dashboard adalah **lapisan udara tipis dan partikel halus** pada background, tetapi dibuat rendah kontras agar tidak menutupi konten.

## Isi dashboard

Dashboard terdiri atas menu berikut:

1. Overview Kualitas Udara
2. Tren Temporal
3. Perbandingan Stasiun
4. Pencemar Kritis
5. Pola Musiman
6. Data Quality / Audit Trail

Default analisis menggunakan **tahun terakhir tersedia**, karena pengambilan keputusan pimpinan membutuhkan konteks terkini. Data historis tetap dapat dipilih melalui filter.

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
4. Pastikan file `.streamlit/config.toml` ikut terunggah agar tema light aktif.

Dashboard sudah dilengkapi pesan error yang lebih terlihat apabila data tidak berhasil dimuat.

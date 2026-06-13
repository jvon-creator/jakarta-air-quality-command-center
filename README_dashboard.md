# Dashboard BI ISPU DKI Jakarta — Muted Anime Sky Theme

Dashboard Streamlit ini dirancang sebagai **Jakarta Air Quality Sky Observatory**: dashboard Business Intelligence yang membaca kualitas udara seperti lanskap langit Jakarta — langit senja dramatis, awan biru pastel, dedaunan hijau, kabut tipis, dan sinyal risiko ISPU yang tetap mudah dibaca.

## Filosofi desain

Tema visual dibuat untuk tidak terasa seperti dashboard template umum. Identitasnya diambil dari dunia kualitas udara: langit, lapisan atmosfer, partikel halus, kabut, horizon kota, dan perubahan warna saat udara berubah dari aman ke berisiko.

Palet warna dibuat **muted** agar nyaman digunakan pada antarmuka data:

| Peran visual | Warna | Hex |
|---|---|---:|
| Paper sky | Putih krem langit | `#FFF9EF` |
| Pastel cloud blue | Awan biru lembut | `#C5DEE4` |
| Leaf oxygen | Hijau dedaunan | `#6FAE82` |
| Haze amber | Kuning kabut | `#D9B45F` |
| Sunset clay | Oranye senja | `#D1845A` |
| Muted alert red | Merah risiko | `#C95F5F` |
| Twilight violet | Ungu malam | `#8D6E9F` |
| Ink slate | Teks utama | `#2E4251` |

## Sistem warna kategori ISPU

| Kategori | Warna | Makna visual |
|---|---|---|
| BAIK | Leaf oxygen | Udara relatif aman |
| SEDANG | Haze amber | Perlu dipantau |
| TIDAK SEHAT | Sunset clay | Risiko mulai meningkat |
| SANGAT TIDAK SEHAT | Muted alert red | Risiko tinggi |
| BERBAHAYA | Twilight violet | Kondisi ekstrem |

## Signature UI

Signature visual dashboard adalah **sky-layer background**: lapisan senja, awan pastel, dan partikel halus rendah kontras. Elemen ini dipakai untuk menguatkan tema kualitas udara tanpa mengganggu keterbacaan angka, chart, dan insight.

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

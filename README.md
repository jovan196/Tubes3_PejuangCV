# PejuangCV ATS

## 1. Deskripsi Singkat

PejuangCV ATS adalah aplikasi desktop berbasis Python dan Flet yang mengekstraksi teks dari file CV (PDF) dan melakukan pencarian kata kunci menggunakan tiga algoritma string matching:

- **Knuth-Morris-Pratt (KMP)**: menjelajah teks dari kiri ke kanan, memanfaatkan tabel prefix-suffix untuk menghindari pemeriksaan ulang karakter yang sudah dicocokkan, sehingga efisien untuk pencarian pola tunggal.
- **Boyer-Moore (BM)**: mulai mencocokkan dari akhir pola ke depan, menggunakan heuristik bad character dan good suffix, sering memindahkan jendela perbandingan lebih jauh untuk mempercepat proses pada teks panjang.
- **Aho-Corasick**: membangun automaton dari kumpulan pola sekaligus, mampu menemukan banyak pola dalam satu kali pemindaian teks, ideal untuk pencarian multi-pola dan volume data besar.

Pengguna dapat memilih algoritma yang diinginkan untuk mencari pola kata dalam kumpulan CV yang telah diekstraksi.

## 2. Requirement & Instalasi

- Python 3.11 atau lebih baru
- Semua _dependencies_ Python yang terdapat pada Requirements.txt
- MySQL (rekomendasi MariaDB 11.7 ke atas) 

Pastikan `python` dan `pip` tersedia di PATH (bisa diakses oleh terminal).

1. Clone repository:
   ```bash
   git clone https://github.com/jovan196/Tubes3_PejuangCV
   cd Tubes3_PejuangCV
   ```
2. Install dependensi Python:
   ```bash
   pip install -r Requirements.txt
   ```

## 3. Cara Menjalankan Aplikasi

1. Jalankan perintah berikut di direktori utama proyek:
   ```bash
   python main.py
   ```
2. Aplikasi akan mengekstraksi teks dari PDF ke CSV, memasukkan database SQL dari data/tubes3_seeding.sql ke _host_ database melalui MySQL, kemudian membuka antarmuka Flet.
3. Di UI, masukkan kata kunci, pilih algoritma (KMP, BM, Aho-Corasick), dan pilih maks hasil.
4. Klik **Cari** untuk mencari profil pelamar beserta CV yang mengandung kata kunci tersebut.
5. Hasil pencarian akan ditampilkan dalam tabel beserta waktu eksekusi dan jumlah kemunculan kata kunci pada setiap profil tersebut.

## 4. Contoh Pencarian

- Input kata: `Python`
- Algoritma: `Aho-Corasick`

> Output: 23 hasil ditemukan dalam 14.3200 detik

## 5. Troubleshooting

- Jika muncul error koneksi MySQL (e.g., "Can't connect to MySQL server"), pastikan MySQL Server aktif dan host/port di `src/database/db_manager.py` sesuai.
- Jika mendapat "Access denied", periksa kembali username, password, dan hak akses user di database. Kemudian, pada line 13 dan 14 `src/database/db_manager.py`, ganti nilai `user` dan `password` sesuai dengan kredensial MySQL di komputer user (jika menggunakan `localhost` sebagai server (`host`) MySQL).
- Periksa instalasi package `mysql-connector-python` atau driver yang digunakan di `Requirements.txt`.
- Untuk masalah timeout atau jaringan, pastikan port MySQL (default 3306) terbuka dan dapat diakses dari aplikasi.

## 6. Author

Jovandra Otniel P. S. (13523141) <br />
Natalia Desiany Nursimin (13523157) <br />
Anas Ghazi Al Gifari (13523159) <br />
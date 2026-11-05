# Laporan Akhir

## 1. Hasil evaluasi

PS C:\Users\ASUS\Documents\Semester 3\PLP\crud-extractor\crud-extractor> python evaluate.py

Dievaluasi: audit.sql, campuran_error.sql, laporan_penjualan.sql, pemeliharaan.sql (27 triple)

Metode   Precision  Recall     F1
parser        1.00    1.00   1.00
regex         0.65    0.81   0.72

[regex]
  salah ditemukan (FP): ('audit.sql', 16, 'sesi', 'R')
  salah ditemukan (FP): ('campuran_error.sql', 4, 'pesanan', 'R')
  salah ditemukan (FP): ('campuran_error.sql', 8, 'keranjang', 'R')
  salah ditemukan (FP): ('laporan_penjualan.sql', 2, 'pelanggan', 'D')
  salah ditemukan (FP): ('laporan_penjualan.sql', 2, 'pelanggan', 'R')
  salah ditemukan (FP): ('laporan_penjualan.sql', 2, 'pesanan', 'R')
  salah ditemukan (FP): ('laporan_penjualan.sql', 2, 'rahasia', 'R')
  salah ditemukan (FP): ('laporan_penjualan.sql', 15, 'pesanan', 'R')
  salah ditemukan (FP): ('pemeliharaan.sql',2, 'crm.alamat', 'R')
  salah ditemukan (FP): ('pemeliharaan.sql',2, 'crm.pelanggan', 'R')
  salah ditemukan (FP): ('pemeliharaan.sql',2, 'pelanggan_lama', 'U')
  salah ditemukan (FP): ('pemeliharaan.sql',15, 'crm.alamat', 'R')
  terlewat (FN):       ('audit.sql', 2, 'pesanan', 'R')
  terlewat (FN):       ('laporan_penjualan.sql', 3, 'pelanggan', 'R')
  terlewat (FN):       ('laporan_penjualan.sql', 3, 'pesanan', 'R')
  terlewat (FN):       ('pemeliharaan.sql', 3, 'crm.alamat', 'R')
  terlewat (FN):       ('pemeliharaan.sql', 3, 'crm.pelanggan', 'R')
PS C:\Users\ASUS\Documents\Semester 3\PLP\crud-extractor\crud-extractor> 

## 2. Tiga kasus di mana regex salah

Kasus 1: Komentar dan string (laporan_penjualan.sql baris 2–6, pemeliharaan.sql baris 1–2)

    -- DELETE FROM pelanggan   (baris ini komentar, bukan perintah)
    SELECT p.nama ... WHERE o.catatan <> 'FROM rahasia';

    - Kesalahan regex: pola dijalankan pada teks mentah, jadi regex menemukan pelanggan D dari komentar dan rahasia R dari isi string. Baris statement diambil dari kata kunci pertama di potongan teks (termasuk di komentar), sehingga seluruh hasil SELECT dilaporkan di baris 2, bukan baris 3 (itu sebabnya ada FN di baris 3). Di pemeliharaan.sql, regex menemukan pelanggan_lama U dari komentar blok.
    - Kenapa parser benar: lexer membuang komentar dan membaca string sebagai satu token STRING, jadi isinya tidak pernah sampai ke parser.

Kasus 2: DELETE FROM ikut dihitung sebagai pembacaan (laporan_penjualan.sql baris 15, campuran_error.sql baris 8, audit.sql baris 16, pemeliharaan.sql baris 15)

    DELETE FROM pesanan WHERE tanggal < :batas;

    - Kesalahan regex: ada dua pola yang cocok pada teks yang sama: DELETE FROM nama (D) dan FROM nama (R). Hasilnya pesanan D (benar) dan pesanan R (salah).
    - Kenapa parser benar: grammar delete_stmt = "DELETE" "FROM" table_name ... menjadikan FROM bagian dari DELETE, bukan klausa pembacaan. Parser memahami kata dari posisinya dalam grammar, bukan sekadar mencocokkan kata.
3.

## 3. Batas pendekatan kami

Minimal tiga hal yang **tidak bisa** ditangani dengan benar oleh tool ini meskipun semua bug
sudah diperbaiki. Untuk tiap batas: contoh SQL atau situasinya, akibatnya pada CRUD matrix,
dan informasi apa yang dibutuhkan untuk mengatasinya.

1.
2.
3.

## 4. Pembagian kerja

Siapa mengerjakan apa, dan bagaimana kalian memastikan keduanya memahami seluruh kode.

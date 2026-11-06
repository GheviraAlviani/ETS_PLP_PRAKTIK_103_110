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
    
Kasus 3: Tabel kedua pada FROM a, b hilang (audit.sql baris 2)

    FROM pelanggan p, pesanan o

    - kesalahan regex: pola FROM\s+nama hanya menangkap satu nama setelah FROM. pesanan yang ada setelah koma lolos (FN)
    - kenapa parser benar: karena grammar table_ref { "," table_ref } mengenali pengulangan dengan koma, jadi semua tabel di FROM terbaca

## 3. Batas pendekatan kami

Minimal tiga hal yang **tidak bisa** ditangani dengan benar oleh tool ini meskipun semua bug
sudah diperbaiki. Untuk tiap batas: contoh SQL atau situasinya, akibatnya pada CRUD matrix,
dan informasi apa yang dibutuhkan untuk mengatasinya.

1. Kolom tanpa qualifier pada query dengan dua tabel atau lebih
    SELECT nama FROM pelanggan p JOIN pesanan o ON o.pelanggan_id = p.id

    - akibatnya resolver hanya bisa mengeluarkan warning kolom 'nama' ambigu tanpa skema, dan resolved tetap None. Matriks tabel tetap benar (pelanggan R, pesanan R), tapi kolom.csv kehilangan atribusi tabel untuk kolom itu.
    - informasi yang dibutuhkan adalah skema database (kolom milik tabel mana). Tool ini sengaja tidak memilikinya. 

2. Sintaks di luar lingkup (CTE, UNION, MERGE, DDL, t.*)
    WITH x AS (SELECT a FROM t) SELECT a FROM x

    - akibatnya statement ditolak parser (diharapkan awal statement ... ditemukan 'WITH') dan tidak dihitung, jadi matriks untuk statement itu kosong (false negative). Hal serupa terjadi pada UNION, CREATE TABLE, dan SELECT t.*.
    - informasi yang dibutuhkan adalah grammar yang diperluas dan aturan scope untuk CTE.

3. View, trigger, stored procedure, dan SQL dinamis
    SELECT * FROM v_laporan

    - akibatnya v_laporan dihitung sebagai tabel (R), padahal sebenarnya view yang membaca tabel dasar lain. Trigger yang menjalankan DML tersembunyi tidak terlihat. SQL yang dirakit sebagai string lalu dieksekusi aplikasi tidak dianalisis sama sekali.
    - Informasi yang dibutuhkan yaitu definisi view dan trigger dari katalog database, serta analisis kode aplikasi.

## 4. Pembagian kerja

**Cara kerja.** Kami memakai pair programming dengan peran driver dan navigator yang
bergantian. Setiap anggota bekerja di branch sendiri
(`103_Ghevira` dan `110_LuthfianaAriba`), lalu digabung ke `main` lewat Pull Request.
Satu bug atau satu TODO dikerjakan dalam satu commit.

**Siapa mengerjakan apa.**

| Pekerjaan | Dikerjakan oleh | Diperiksa oleh |
| --- | --- | --- |
| Bug 1: keyword huruf kecil | Luthfiana | Ghevira |
| Bug 2: operator `<>` | Ghevira | Luthfiana |
| Bug 3: `''` di dalam string | Luthfiana | Ghevira |
| Bug 4: presedensi `OR` dan `AND` | Ghevira | Luthfiana |
| Bug 5: error recovery | Luthfiana | Ghevira |
| Bug 6: `LEFT OUTER JOIN` | Ghevira | Luthfiana |
| Bug 7: arah pencarian scope | Luthfiana | Ghevira |
| Bug 8: scope `DELETE` bocor | Ghevira | Luthfiana |
| Bug 9: subquery `UPDATE` jadi R | Luthfiana | Ghevira |
| T1: `INSERT ... SELECT` | Luthfiana | Ghevira |
| T2: kolom tanpa qualifier | Ghevira | Luthfiana |
| T3: komentar blok `/* */` | Ghevira | Luthfiana |
| Ground truth `audit.sql` | Luthfiana (baris 2, 8, dan `pelanggan` di baris 12) dan Ghevira (baris 12 `pesanan`, 16, 18, 20) | saling memeriksa |
| Ground truth `pemeliharaan.sql` | Luthfiana (baris 3, 8, dan `crm.log_perubahan` di baris 12) dan Ghevira (baris 12 `crm.pelanggan`, 15) | saling memeriksa |
| Lima test kasus tepi | Ghevira (LexError menghentikan file, BETWEEN dan AND logika); Luthfiana (...) | saling memeriksa |

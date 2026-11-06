# Laporan Bug

Salin blok di bawah untuk setiap bug. Bagian **Akar masalah** wajib ditulis dengan kata-kata
sendiri dan memakai konsep dari *Crafting Interpreters* (sebutkan bab). Bagian ini diuji lisan.

---

## Bug 1: Keyword huruf kecil dikenali sebagai IDENT

**Ditemukan oleh:** Luthfiana dan Ghevira
**Diperbaiki oleh:** Luthfiana

**Gejala.** 
tokenize("select") menghasilkan IDENT 'select'. SPESIFIKASI bagian 2.2 mewajibkan keyword tidak peka huruf besar/kecil dan nilai tokennya dinormalisasi ke huruf besar (KEYWORD 'SELECT'). Test test_keyword_huruf_kecil gagal. Akibat lanjutannya, pemeliharaan.sql (yang memakai select, from, where huruf kecil) tidak bisa diproses dengan benar; baru terlihat setelah komentar blok (T3) didukung, karena file itu berhenti lebih dulu di komentar di baris 1.

**Reproduksi minimal.** SQL terpendek yang memicu bug:

```sql
    select a from t;
```

**Akar masalah.** Mengapa kode lama salah? Konsep apa yang dilanggar? 
Lexer membaca satu kata utuh lalu memutuskan apakah itu keyword dengan mengecek text in KEYWORDS. Isi KEYWORDS semuanya huruf besar, sedangkan text adalah teks persis seperti diketik. Jadi select atau Select tidak pernah cocok dan jatuh ke cabang IDENT. Ini soal tahap scanning: pengenalan reserved word harus membandingkan bentuk yang sudah dinormalisasi.

**Perbaikan.** File dan fungsi yang diubah, serta alasannya. Sebutkan juga perbaikan
alternatif yang kalian pertimbangkan dan alasan tidak memilihnya.
crud/lexer.py, fungsi _word. Teks dibandingkan dalam bentuk huruf besar (upper = text.upper()), dan kalau cocok yang disimpan sebagai nilai token KEYWORD adalah upper. Untuk IDENT, teks asli tetap dipakai karena penormalan ke huruf kecil menjadi urusan parser (spek 2.2), sehingga selection dan fromage tetap IDENT. Alternatif yang ditolak: mengisi KEYWORDS dengan semua kombinasi huruf (tidak mungkin untuk campuran seperti SeLeCt).

**Test regresi.** Nama test di `tests/test_tambahan.py` yang gagal sebelum perbaikan dan lulus
sesudahnya.
test_regresi_keyword_campuran_huruf_dan_identifier_berawalan_keyword (ditambah test bawaan test_keyword_huruf_kecil)

**Peran AI.** Apakah AI membantu menemukan atau memperbaiki bug ini? Bagaimana kalian
memverifikasinya?
menunjukkan lokasi bug (_word), memberi kode perbaikan dan kode test. Kami menerapkannya, memeriksa diff, dan memverifikasi dengan menjalankan test baru (gagal sebelum, lulus sesudah) serta python -m pytest.
---
## Bug 2: (judul singkat)

**Ditemukan oleh:** Ghevira dan Luthfiana
**Diperbaiki oleh:** Luthfiana

**Gejala.** 

**Reproduksi minimal.** SQL terpendek yang memicu bug:

```sql
    
```

**Akar masalah.** Mengapa kode lama salah? Konsep apa yang dilanggar? 


**Perbaikan.** File dan fungsi yang diubah, serta alasannya. Sebutkan juga perbaikan
alternatif yang kalian pertimbangkan dan alasan tidak memilihnya.


**Test regresi.** Nama test di `tests/test_tambahan.py` yang gagal sebelum perbaikan dan lulus
sesudahnya.


**Peran AI.** Apakah AI membantu menemukan atau memperbaiki bug ini? Bagaimana kalian
memverifikasinya?


## Bug 3: '' di dalam string memutus string menjadi dua token

**Ditemukan oleh:** Luthfiana dan Ghevira
**Diperbaiki oleh:** Luthfiana

**Gejala.** 
tokenize("'O''Brien'") menghasilkan dua token STRING (O dan Brien). SPESIFIKASI bagian 2.4 menyatakan '' mewakili satu kutip, sehingga hasil yang benar adalah satu token STRING bernilai O'Brien. File pemeliharaan.sql memuatnya ('O''Brien' dan 'O''Neil').

**Reproduksi minimal.** SQL terpendek yang memicu bug:

```sql
    SELECT a FROM t WHERE nama = 'O''Brien';
```

**Akar masalah.** Mengapa kode lama salah? Konsep apa yang dilanggar? 
Fungsi _string berhenti pada kutip penutup pertama yang ditemukan, tanpa melihat karakter sesudahnya. Padahal dua kutip berturut-turut adalah escape untuk satu kutip. Untuk membedakannya dibutuhkan lookahead satu karakter: begitu menemukan ', intip karakter berikutnya sebelum memutuskan string selesai (Crafting Interpreters Bab 4, string literal).

**Perbaikan.** File dan fungsi yang diubah, serta alasannya. Sebutkan juga perbaikan
alternatif yang kalian pertimbangkan dan alasan tidak memilihnya.
crud/lexer.py, fungsi _string. Ketika ' ditemukan dan _peek() juga ', kutip kedua dikonsumsi dan satu karakter ' ditambahkan ke isi string, lalu loop lanjut. Kalau tidak, kutip itu adalah penutup. String yang tidak ditutup tetap LexError. Alternatif yang ditolak: memotong string di kutip pertama lalu mengganti '' menjadi ' sesudahnya, karena posisi akhir string dan nomor kolom token berikutnya jadi sulit dijaga.

**Test regresi.** Nama test di `tests/test_tambahan.py` yang gagal sebelum perbaikan dan lulus
sesudahnya.
test_regresi_kutip_ganda_dalam_string_jadi_satu_token.

**Peran AI.** Apakah AI membantu menemukan atau memperbaiki bug ini? Bagaimana kalian
memverifikasinya?
AI memberi pertanyaan pemandu soal lookahead dan kode test; bug ini ditemukan lewat pemeriksaan kode dengan bantuan AI. Perbaikan kodenya kami tulis sendiri dan diverifikasi dengan test baru serta python -m pytest.

## Bug 4: (judul singkat)

**Ditemukan oleh:** Ghevira dan Luthfiana
**Diperbaiki oleh:** Luthfiana

**Gejala.** 

**Reproduksi minimal.** SQL terpendek yang memicu bug:

```sql
    
```

**Akar masalah.** Mengapa kode lama salah? Konsep apa yang dilanggar? 


**Perbaikan.** File dan fungsi yang diubah, serta alasannya. Sebutkan juga perbaikan
alternatif yang kalian pertimbangkan dan alasan tidak memilihnya.


**Test regresi.** Nama test di `tests/test_tambahan.py` yang gagal sebelum perbaikan dan lulus
sesudahnya.


**Peran AI.** Apakah AI membantu menemukan atau memperbaiki bug ini? Bagaimana kalian
memverifikasinya?


## Bug 5: Error recovery membuang seluruh sisa file

**Ditemukan oleh:** Luthfiana dan Ghevira
**Diperbaiki oleh:** Luthfiana

**Gejala.** 
Setelah satu statement rusak, semua statement sesudahnya hilang. SELECT FROM a; SELECT x FROM; SELECT y FROM z; menghasilkan 1 error dan 0 statement, padahal SPESIFIKASI bagian 6 meminta 2 error dan 1 statement. Di campuran_error.sql, UPDATE baris 6 dan DELETE baris 8 hilang, dan evaluate.py mencatatnya sebagai FN.

**Reproduksi minimal.** SQL terpendek yang memicu bug:

```sql
   SELECT FROM a;
   SELECT x FROM t; 
```

**Akar masalah.** Mengapa kode lama salah? Konsep apa yang dilanggar? 
Fungsi _synchronize terus memanggil _advance() sampai akhir token dan tidak pernah berhenti di ;. Setelah error, parser seharusnya mencari titik aman (synchronization point) untuk melanjutkan, yaitu batas statement berikutnya. Tanpa itu, panic mode membuang semua token yang tersisa (Crafting Interpreters Bab 6, panic mode error recovery).

**Perbaikan.** File dan fungsi yang diubah, serta alasannya. Sebutkan juga perbaikan
alternatif yang kalian pertimbangkan dan alasan tidak memilihnya.
crud/parser.py, fungsi _synchronize. Setiap token yang dibuang diperiksa, dan begitu token ; terbuang, fungsi berhenti sehingga parse_script melanjutkan ke statement berikutnya (sesuai spek 6: buang sampai dan termasuk ;). Alternatif yang ditolak: berhenti di keyword awal statement berikutnya (SELECT, INSERT, ...), karena SELECT juga muncul di dalam subquery dan INSERT ... SELECT, sehingga parser bisa berhenti di tengah statement yang masih rusak dan menghasilkan error ganda.

**Test regresi.** Nama test di `tests/test_tambahan.py` yang gagal sebelum perbaikan dan lulus
sesudahnya.
test_regresi_recovery_berhenti_di_titik_koma dan test_regresi_recovery_statement_valid_setelah_error.

**Peran AI.** Apakah AI membantu menemukan atau memperbaiki bug ini? Bagaimana kalian
memverifikasinya?
AI menunjukkan lokasi bug dan memberi kode perbaikan serta kode test. Kami menerapkannya dan memverifikasi dengan test baru, python -m pytest, dan evaluate.py

## Bug 6: (judul singkat)

**Ditemukan oleh:** Ghevira dan Luthfiana
**Diperbaiki oleh:** Luthfiana

**Gejala.** 

**Reproduksi minimal.** SQL terpendek yang memicu bug:

```sql
    
```

**Akar masalah.** Mengapa kode lama salah? Konsep apa yang dilanggar? 


**Perbaikan.** File dan fungsi yang diubah, serta alasannya. Sebutkan juga perbaikan
alternatif yang kalian pertimbangkan dan alasan tidak memilihnya.


**Test regresi.** Nama test di `tests/test_tambahan.py` yang gagal sebelum perbaikan dan lulus
sesudahnya.


**Peran AI.** Apakah AI membantu menemukan atau memperbaiki bug ini? Bagaimana kalian
memverifikasinya?

## Bug 7: Alias di subquery menunjuk tabel luar (arah pencarian scope terbalik)

**Ditemukan oleh:** Luthfiana dan Ghevira
**Diperbaiki oleh:** Luthfiana

**Gejala.** 
Pada audit.sql baris 12, x.pelanggan_id dan x.total di dalam subquery di-resolve ke pelanggan, padahal x di subquery adalah alias pesanan. SPESIFIKASI bagian 4.3 menyatakan qualifier dicari dari scope terdalam ke luar (shadowing).

**Reproduksi minimal.** SQL terpendek yang memicu bug:

```sql
    SELECT x.id FROM pelanggan x
    WHERE x.id IN (SELECT x.pelanggan_id FROM pesanan x WHERE x.total > 5);
```

**Akar masalah.** Mengapa kode lama salah? Konsep apa yang dilanggar? 
Fungsi _lookup mengumpulkan rantai scope (dari terdalam ke terluar) lalu menelusurinya dengan reversed(chain), sehingga yang dicek pertama adalah scope terluar. Akibatnya alias luar menang atas alias dalam, padahal resolusi lexical harus mulai dari scope paling dalam dan naik ke luar sehingga alias dalam menutupi alias luar (shadowing), sementara alias yang hanya ada di luar tetap bisa ditemukan.

**Perbaikan.** File dan fungsi yang diubah, serta alasannya. Sebutkan juga perbaikan
alternatif yang kalian pertimbangkan dan alasan tidak memilihnya.
crud/resolver.py, fungsi _lookup. Rantai dan reversed dihapus. Pencarian dimulai dari self.scope (terdalam) lalu naik lewat parent, dan mengembalikan entri pertama yang ditemukan. Alternatif yang ditolak: tetap membuat daftar lalu menelusurinya tanpa reversed; hasilnya sama tetapi memboroskan langkah yang tidak perlu.

**Test regresi.** Nama test di `tests/test_tambahan.py` yang gagal sebelum perbaikan dan lulus
sesudahnya.
test_regresi_alias_dalam_menutupi_alias_luar dan test_regresi_correlated_subquery_tetap_melihat_alias_luar
(penjaga agar correlated subquerry tidak rusak)

**Peran AI.** Apakah AI membantu menemukan atau memperbaiki bug ini? Bagaimana kalian
memverifikasinya?
AI menunjukkan lokasi bug dan memberi kode perbaikan serta kode test. Kami menerapkannya dan memverifikasi dengan test baru, --ast audit.sql, kolom.csv (kolom baris 12 sekarang menunjuk pesanan), dan python -m pytest

## Bug 8: (judul singkat)

**Ditemukan oleh:** Ghevira dan Luthfiana
**Diperbaiki oleh:** Luthfiana

**Gejala.** 

**Reproduksi minimal.** SQL terpendek yang memicu bug:

```sql
    
```

**Akar masalah.** Mengapa kode lama salah? Konsep apa yang dilanggar? 


**Perbaikan.** File dan fungsi yang diubah, serta alasannya. Sebutkan juga perbaikan
alternatif yang kalian pertimbangkan dan alasan tidak memilihnya.


**Test regresi.** Nama test di `tests/test_tambahan.py` yang gagal sebelum perbaikan dan lulus
sesudahnya.


**Peran AI.** Apakah AI membantu menemukan atau memperbaiki bug ini? Bagaimana kalian
memverifikasinya?

## Bug 9: Tabel di subquery pada UPDATE ditandai U, bukan R

**Ditemukan oleh:** Luthfiana dan Ghevira
**Diperbaiki oleh:** Luthfiana

**Gejala.** 
UPDATE pesanan ... WHERE pelanggan_id IN (SELECT id FROM pelanggan ...) menghasilkan pelanggan: U. SPESIFIKASI bagian 5: membaca tabel lewat subquery selalu R apa pun jenis statement luarnya. Di audit.sql, matriks pelanggan jadi RU padahal seharusnya R. ground_truth.csv pun sudah memuat laporan_penjualan.sql,12,pesanan,R

**Reproduksi minimal.** SQL terpendek yang memicu bug:

```sql
    UPDATE pesanan SET status = 'X' WHERE pelanggan_id IN (SELECT id FROM pelanggan);
```

**Akar masalah.** Mengapa kode lama salah? Konsep apa yang dilanggar? 
Di cabang ast.Update, analyzer memanggil _collect(..., "U") untuk bagian SET dan WHERE. _collect memberi operasi yang diterimanya ke semua tabel di dalam subquery, sehingga tabel yang hanya dibaca ikut ditandai U. Operasi seharusnya diturunkan dari peran tabel di AST (target atau sumber baca), bukan diwariskan dari jenis statement luar. Ini analisis atas AST yang sudah di-resolve, bukan atas teks.

**Perbaikan.** File dan fungsi yang diubah, serta alasannya. Sebutkan juga perbaikan
alternatif yang kalian pertimbangkan dan alasan tidak memilihnya.
crud/analyzer.py, cabang ast.Update. Tabel target tetap ditandai U secara terpisah, sedangkan argumen operasi untuk _collect pada SET dan WHERE diganti menjadi "R". Alternatif yang ditolak: menghapus U dari hasil setelah dikumpulkan (untuk kasus tabel yang dibaca sekaligus diubah, UPDATE t SET a = (SELECT MAX(a) FROM t), yang harus menghasilkan R dan U sekaligus).

**Test regresi.** Nama test di `tests/test_tambahan.py` yang gagal sebelum perbaikan dan lulus
sesudahnya.
test_regresi_subquery_di_update_hanya_dibaca dan test_regresi_update_membaca_tabelnya_sendiri_lewat_subquery.

**Peran AI.** Apakah AI membantu menemukan atau memperbaiki bug ini? Bagaimana kalian
memverifikasinya?
AI menunjukkan lokasi bug dan memberi kode perbaikan serta kode test. Kami menerapkannya dan memverifikasi dengan test baru, detail.csv dan crud_matrix.csv (pelanggan di audit.sql sekarang R), serta python -m pytest.
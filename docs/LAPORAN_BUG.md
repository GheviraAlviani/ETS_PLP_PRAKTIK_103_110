`# Laporan Bug

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
Lexer membaca satu kata full, lalu mengecek apakah kata itu ada di daftar KEYWORDS. Namun, isi daftar itu huruf besar semua, sedangkan kata yang dicek dibiarkan sama seperti yang diketik. Jadi select tidak pernah cocok dengan SELECT dan menjadi identifier. Hal Ini ada di tahap scanning (Crafting Interpreters Bab 4): sebelum memutuskan sebuah kata itu reserved word atau bukan, bentuknya harus disamakan dulu.

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
## Bug 2: Operator <> terpecah menjadi dua token

**Ditemukan oleh:** Ghevira dan Luthfiana
**Diperbaiki oleh:** Ghevira

**Gejala.** tokenize("a <> b") menghasilkan token < lalu >. SPESIFIKASI bagian 2.5 mewajibkan <> menjadi satu token OP (maximal munch). Akibatnya laporan_penjualan.sql gagal di-parse: Baris 6, kolom 41: diharapkan ekspresi, ditemukan '>', dan seluruh file tidak menghasilkan satu pun statement (recall parser di evaluate.py awalnya hanya 0.10).

**Reproduksi minimal.** SQL terpendek yang memicu bug:
```sql
SELECT a FROM t WHERE a <> 1;
```

**Akar masalah.** Mengapa kode lama salah? Konsep apa yang dilanggar? 
Pada cabang ch == "<", lexer hanya memeriksa apakah karakter berikutnya = (untuk <=). Karakter > tidak diperiksa, sehingga < langsung diterima sebagai operator pendek dan > dibaca terpisah. Scanner seharusnya memakai maximal munch: mencoba lexeme terpanjang yang cocok sebelum menyerah ke yang lebih pendek.


**Perbaikan.** crud/lexer.py, cabang < di _scan_token. Setelah membaca <, dicoba = (menjadi <=), kalau tidak dicoba > (menjadi <>), baru terakhir < saja. Alternatif yang ditolak: menggabungkan < dan > di parser. Itu menaruh perbaikan di tahap yang salah dan membuat < > (dengan spasi) ikut diterima sebagai satu operator.


**Test regresi.** test_regresi_operator_tidak_sama_dengan_satu_token.


**Peran AI.** Apakah AI membantu menemukan atau memperbaiki bug ini? Bagaimana kalian
memverifikasinya?
AI menunjukkan lokasi bug, menjelaskan konsep *maximal munch*, dan memberi
bentuk kode perbaikan serta kode test. Kami menerapkannya, memeriksa diff, lalu memverifikasi
dengan test baru dan `python -m pytest` (pesan error `laporan_penjualan.sql` berubah, tidak
lagi `ditemukan '>'`).


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
Fungsi _string berhenti ketika ketemu kutip penutup pertama, tanpa melihat karakter setelahnya. Padahal dua kutip berturut-turut adalah cara menulis satu kutip di dalam isi string. Untuk membedakannya, lexer perlu lookahead satu karakter: begitu ketemu ', intip dulu karakter berikutnya sebelum memutuskan string sudah selesai (Crafting Interpreters Bab 4, string literal).

**Perbaikan.** File dan fungsi yang diubah, serta alasannya. Sebutkan juga perbaikan
alternatif yang kalian pertimbangkan dan alasan tidak memilihnya.
crud/lexer.py, fungsi _string. Ketika ' ditemukan dan _peek() juga ', kutip kedua dikonsumsi dan satu karakter ' ditambahkan ke isi string, lalu loop lanjut. Kalau tidak, kutip itu adalah penutup. String yang tidak ditutup tetap LexError. Alternatif yang ditolak: memotong string di kutip pertama lalu mengganti '' menjadi ' sesudahnya, karena posisi akhir string dan nomor kolom token berikutnya jadi sulit dijaga.

**Test regresi.** Nama test di `tests/test_tambahan.py` yang gagal sebelum perbaikan dan lulus
sesudahnya.
test_regresi_kutip_ganda_dalam_string_jadi_satu_token.

**Peran AI.** Apakah AI membantu menemukan atau memperbaiki bug ini? Bagaimana kalian
memverifikasinya?
AI memberi pertanyaan pemandu soal lookahead dan kode test; bug ini ditemukan lewat pemeriksaan kode dengan bantuan AI. Perbaikan kodenya kami tulis sendiri dan diverifikasi dengan test baru serta python -m pytest.


## Bug 4: Presedensi AND dan OR salah

**Ditemukan oleh:** Ghevira dan Luthfiana
**Diperbaiki oleh:** Ghevira

**Gejala.** Untuk a = 1 OR b = 2 AND c = 3, AST menaruh AND di puncak dengan OR di dalamnya, padahal SPESIFIKASI bagian 3.1 menyatakan OR berpresedensi lebih rendah dari AND, jadi harusnya a = 1 OR (b = 2 AND c = 3). Terlihat di --ast audit.sql baris 2.

**Reproduksi minimal.** SQL terpendek yang memicu bug:

```sql
    SELECT a FROM t WHERE a = 1 OR b = 2 AND c = 3;
```

**Akar masalah.** Mengapa kode lama salah? Konsep apa yang dilanggar? 
 Fungsi _logical memproses AND dan OR dalam satu loop, sehingga keduanya diperlakukan sebagai operator di tingkat yang sama dan dibaca dari kiri ke kanan. Grammar spek punya dua tingkat terpisah (or_expr dan and_expr). Di recursive descent, presedensi dicapai lewat urutan pemanggilan fungsi: operator berpresedensi lebih rendah memanggil yang lebih tinggi untuk operan-operannya.


**Perbaikan.** File dan fungsi yang diubah, serta alasannya. Sebutkan juga perbaikan
alternatif yang kalian pertimbangkan dan alasan tidak memilihnya.
crud/parser.py. _logical dipecah menjadi _or (loop untuk OR, operannya dari _and) dan _and (loop untuk AND, operannya dari _not); _expr sekarang memanggil _or. Alternatif yang ditolak: tabel prioritas operator atau precedence climbing. Keduanya lebih ringkas tetapi menyembunyikan struktur grammar, sedangkan dua fungsi mencerminkan spek satu-satu dan sejalan dengan gaya fungsi lain di parser (additive, multiplicative).


**Test regresi.** Nama test di `tests/test_tambahan.py` yang gagal sebelum perbaikan dan lulus
sesudahnya.
test_regresi_and_lebih_kuat_dari_or dan test_regresi_dua_cabang_and_digabung_or.


**Peran AI.** Apakah AI membantu menemukan atau memperbaiki bug ini? Bagaimana kalian
memverifikasinya?
AI menunjukkan lokasi bug, memberi pertanyaan pemandu, bentuk kode perbaikan
(`_or` dan `_and`), dan kode test. Kami menerapkannya, lalu memverifikasi dengan
`--ast audit.sql` (OR di puncak), test baru, dan `python -m pytest`.

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
_synchronize terus memanggil _advance() hingga token habis dan tidak pernah berhenti di ;. Setelah error, parser seharusnya mencari titik aman untuk melanjutkan. Pada SQL, batas statement ditandai dengan tanda titik koma (;). Jika batas tersebut tidak ditemukan, mekanisme panic mode dapat membuang token atau statement valid berikutnya saat proses pemulihan error. (Bab 6, panic mode error recovery).

**Perbaikan.** File dan fungsi yang diubah, serta alasannya. Sebutkan juga perbaikan
alternatif yang kalian pertimbangkan dan alasan tidak memilihnya.
crud/parser.py, fungsi _synchronize. Setiap token yang dibuang diperiksa, dan begitu token ; terbuang, fungsi berhenti sehingga parse_script melanjutkan ke statement berikutnya (sesuai spek 6: buang sampai dan termasuk ;). Alternatif yang ditolak: berhenti di keyword awal statement berikutnya (SELECT, INSERT, ...), karena SELECT juga muncul di dalam subquery dan INSERT ... SELECT, sehingga parser bisa berhenti di tengah statement yang masih rusak dan menghasilkan error ganda.

**Test regresi.** Nama test di `tests/test_tambahan.py` yang gagal sebelum perbaikan dan lulus
sesudahnya.
test_regresi_recovery_berhenti_di_titik_koma dan test_regresi_recovery_statement_valid_setelah_error.

**Peran AI.** Apakah AI membantu menemukan atau memperbaiki bug ini? Bagaimana kalian
memverifikasinya?
AI menunjukkan lokasi bug dan memberi kode perbaikan serta kode test. Kami menerapkannya dan memverifikasi dengan test baru, python -m pytest, dan evaluate.py

## Bug 6: LEFT OUTER JOIN ditolak

**Ditemukan oleh:** Ghevira dan Luthfiana
**Diperbaiki oleh:** Ghevira

**Gejala.** LEFT OUTER JOIN menghasilkan parse error karena parser mengharapkan JOIN tetapi menemukan OUTER. SPESIFIKASI bagian 3 mengizinkan "LEFT" [ "OUTER" ] "JOIN". pemeliharaan.sql baris 5 memakainya. Tidak tertangkap test bawaan.

**Reproduksi minimal.** SQL terpendek yang memicu bug:

```sql
   SELECT a FROM t LEFT OUTER JOIN u ON t.id = u.id; 
```

**Akar masalah.** Mengapa kode lama salah? Konsep apa yang dilanggar? 
Setelah mengenali LEFT, fungsi _join langsung menuntut JOIN lewat _expect_kw("JOIN") tanpa menangani OUTER yang bersifat opsional. Bagian opsional di grammar ([ ... ]) harus dicerminkan di parser dengan pengecekan yang tidak menimbulkan error kalau bagian itu tidak ada.


**Perbaikan.** File dan fungsi yang diubah, serta alasannya. Sebutkan juga perbaikan
alternatif yang kalian pertimbangkan dan alasan tidak memilihnya.
crud/parser.py, fungsi _join. Setelah LEFT, dipanggil _match_kw("OUTER") yang mengonsumsi OUTER kalau ada dan tidak berbuat apa-apa kalau tidak ada, baru kemudian JOIN dituntut. Alternatif yang ditolak: menjadikan LEFT OUTER satu token di lexer, karena itu menyimpang dari spek (keyword diperlakukan satu per satu) dan merusak LEFT JOIN biasa.

**Test regresi.** 
test_regresi_left_outer_join.


**Peran AI.** Apakah AI membantu menemukan atau memperbaiki bug ini? Bagaimana kalian
memverifikasinya?
AI menemukan bug ini lewat pemeriksaan kode terhadap grammar, lalu memberi kode perbaikan dan kode test. Kami menerapkannya dan memverifikasi dengan test baru serta python -m pytest (pemeliharaan.sql bisa diurai seluruhnya setelah T3 selesai).

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
_lookup mengumpulkan rantai scope dari terdalam hingga terluar, lalu menelusurinya dengan reversed, jadi yang dicek pertama justru scope terluar. Akibatnya alias luar menang daripada alias dalam. Resolusi nama (Crafting Interpreters Bab 11) seharusnya mulai dari scope paling dalam lalu naik keluar. Dengan begitu alias dalam menutupi alias luar (shadowing), sementara alias yang hanya ada di luar tetap bisa ditemukan oleh correlated subquery.

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

## Bug 8: Alias DELETE bocor ke statement berikutnya

**Ditemukan oleh:** Ghevira dan Luthfiana
**Diperbaiki oleh:** Ghevira

**Gejala.** Di audit.sql, alias s dari DELETE FROM sesi s (baris 16) masih terlihat di SELECT s.id FROM pengguna u (baris 18) dan di-resolve ke sesi, tanpa diagnostik. SPESIFIKASI bagian 4.5: setelah satu statement selesai tidak boleh ada scope tersisa, dan harusnya muncul error alias 's' tidak terdefinisi.

**Reproduksi minimal.** SQL terpendek yang memicu bug:

```sql
    DELETE FROM sesi s WHERE s.a = 1;
    SELECT s.id FROM u;
```

**Akar masalah.** Mengapa kode lama salah? Konsep apa yang dilanggar? 
Fungsi _delete memanggil _push() untuk membuat scope baru tetapi tidak pernah _pop(), sehingga scope DELETE tetap menempel di tumpukan dan terlihat oleh statement berikutnya. _select dan _update sudah memasangkan _push dengan _pop. Scope diperlakukan sebagai tumpukan: setiap yang dibuka harus ditutup.

**Perbaikan.** File dan fungsi yang diubah, serta alasannya. Sebutkan juga perbaikan
alternatif yang kalian pertimbangkan dan alasan tidak memilihnya.
crud/resolver.py, fungsi _delete. Ditambahkan self._pop() di akhir fungsi, berpasangan dengan _push(). Alternatif yang ditolak: mereset self.scope = None di loop resolve_script setiap statement. Itu menutupi gejalanya, tetapi tidak memperbaiki ketidakpasangan push dan pop, dan bug serupa di fungsi lain tidak akan ketahuan.

**Test regresi.** 
test_regresi_alias_delete_tidak_bocor_ke_statement_berikutnya.

**Peran AI.** Apakah AI membantu menemukan atau memperbaiki bug ini? Bagaimana kalian
memverifikasinya?
AI menunjukkan lokasi bug dan memberi kode perbaikan serta kode test. Kami menerapkannya dan memverifikasi dengan test baru dan python -m pytest. Setelah perbaikan, CLI menampilkan audit.sql: baris 18: error: alias 's' tidak terdefinisi.

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
Di cabang ast.Update, analyzer memanggil _collect(..., "U"), lalu _collect memberi operasi itu ke semua tabel di dalam subquery. Jadi tabel yang hanya dibaca ikut ditandai U. Operasi seharusnya ditentukan dari peran tabel di AST (tabel target diubah, tabel sumber dibaca), bukan diwariskan dari jenis statement luarnya. Analyzer bekerja di atas AST yang sudah di-resolve (Crafting Interpreters Bab 5 untuk representasi AST dan Bab 11 untuk pemrosesan sesudah parsing), bukan di atas teks.

**Perbaikan.** File dan fungsi yang diubah, serta alasannya. Sebutkan juga perbaikan
alternatif yang kalian pertimbangkan dan alasan tidak memilihnya.
crud/analyzer.py, cabang ast.Update. Tabel target tetap ditandai U secara terpisah, sedangkan argumen operasi untuk _collect pada SET dan WHERE diganti menjadi "R". Alternatif yang ditolak: menghapus U dari hasil setelah dikumpulkan (untuk kasus tabel yang dibaca sekaligus diubah, UPDATE t SET a = (SELECT MAX(a) FROM t), yang harus menghasilkan R dan U sekaligus).

**Test regresi.** Nama test di `tests/test_tambahan.py` yang gagal sebelum perbaikan dan lulus
sesudahnya.
test_regresi_subquery_di_update_hanya_dibaca dan test_regresi_update_membaca_tabelnya_sendiri_lewat_subquery.

**Peran AI.** Apakah AI membantu menemukan atau memperbaiki bug ini? Bagaimana kalian
memverifikasinya?
AI menunjukkan lokasi bug dan memberi kode perbaikan serta kode test. Kami menerapkannya dan memverifikasi dengan test baru, detail.csv dan crud_matrix.csv (pelanggan di audit.sql sekarang R), serta python -m pytest.`
# Kartu Desain

Tuliskan lima keputusan desain penting dalam pekerjaan kalian. Untuk tiap keputusan, sebutkan
alternatif yang ditolak dan alasannya. Contoh topik (boleh memilih yang lain):

- bagaimana parser membedakan `*` sebagai "semua kolom" dan sebagai perkalian;
- di mana dan bagaimana presedensi `AND`/`OR` dinyatakan;
- mengapa error recovery berhenti di `;`, bukan di keyword `SELECT` berikutnya;
- urutan pencarian scope dan akibatnya pada shadowing serta correlated subquery;
- mengapa kolom tanpa qualifier hanya dilihat di scope terdalam, dan apa kelemahannya;
- bagaimana implementasi `INSERT ... SELECT` atau komentar blok kalian.

| No | Keputusan | Alternatif yang ditolak | Alasan |
| --- | --- | --- | --- |
| 1 |Presedensi AND/OR dinyatakan lewat dua fungsi terpisah (_or memanggil _and, _and memanggil _not)|(a) Satu loop dengan tabel prioritas operator, (b) precedence climbing|Dua fungsi mencerminkan grammar spek satu-satu (or_expr, and_expr, not_expr), jadi mudah diperiksa terhadap spek. Gayanya juga sama dengan fungsi lain yang ada di parser (additive, multiplicative). Alternatif (a) dan (b) lebih ringkas tetapi menyembunyikan struktur grammar, dan satu loop itu persis sumber Bug 4.|
| 2 |Error recovery berhenti di ; (buang token sampai dan termasuk ;, lalu lanjut)|(a) Berhenti di keyword awal statement berikutnya (SELECT, INSERT, ...), (b) berhenti di akhir file|Keyword SELECT juga muncul di dalam statement (subquery dan INSERT ... SELECT), jadi parser bisa berhenti di tengah statement yang masih rusak dan menghasilkan error ganda. ; adalah batas statement yang pasti. Spek 6 juga menetapkannya. Alternatif (b) adalah perilaku lama yang membuang semua statement valid sesudahnya (Bug 5)|
| 3 |Alias berkualifier dicari dari scope terdalam ke luar lewat rantai parent, kolom tanpa qualifier hanya melihat scope terdalam |(a) Satu tabel nama global untuk semua alias, (b) kolom tanpa qualifier ikut mencari ke scope luar |Rantai scope memberi shadowing (alias dalam menutupi alias luar) dan correlated subquery sekaligus. Alternatif (a) tidak bisa membedakan alias yang sama di dua level. Alternatif (b) berarti menebak tabel tanpa skema. Kelemahan: kolom tanpa qualifier pada dua tabel atau lebih jadi ambigu dan hanya mendapat warning. |
| 4 |Operasi tabel di subquery selalu R, diturunkan dari peran tabel di AST (parameter operasi hanya untuk tabel target)|Mewariskan operasi statement luar (U/D) ke seluruh pohon di bawahnya |Subquery cuma membaca data, apa pun statement luarnya. Mewariskan operasi luar menyebabkan Bug 9 (pelanggan di subquery UPDATE jadi U). Pendekatan ini juga membuat kasus tabel yang dibaca sekaligus diubah (UPDATE t SET a=(SELECT MAX(a) FROM t)) menghasilkan RU, bukan salah satunya. |
| 5 |Komentar blok dibuang di lexer dengan lookahead dua karakter (* lalu /); komentar yang tidak ditutup menjadi LexError di posisi awal komentar |(a) Memakai regex untuk komentar, (b) membuat token COMMENT lalu menyaringnya di parser, (c) mendukung komentar bersarang|komentar tidak menghasilkan token dan tidak bersarang, jadi lexer tidak perlu meneruskannya ke parser (alternatif b). Scanner tangan menjaga nomor baris dan kolom tetap benar tanpa kode tambahan (_advance yang menghitung). Melaporkan posisi awal membantu menemukan komentar yang lupa ditutup. Alternatif (a) memakai regex, padahal batasan arsitektur melarang regex di analyzer dan pendekatan yang konsisten lebih mudah dijelaskan.|

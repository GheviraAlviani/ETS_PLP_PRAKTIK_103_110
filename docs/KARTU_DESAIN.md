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
| 3 | | | |
| 4 | | | |
| 5 | | | |

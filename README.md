# ETS_PLP_PRAKTIK_103_110

# CRUD Matrix Extractor

Tool Python yang membaca file SQL dan menghasilkan **CRUD matrix**: tabel mana yang dibuat (C),
dibaca (R), diubah (U), atau dihapus (D) oleh tiap statement dan tiap file. Tool dibangun sebagai
pipeline kompilator kecil (lexer, parser, resolver, analyzer), mengikuti pendekatan buku
*Crafting Interpreters*. Proyek ini adalah tugas ETS PLP (praktik) yang dikerjakan berdua.

Acuan kebenaran perilaku tool ada di [`SPESIFIKASI.md`](SPESIFIKASI.md).

## Anggota

| Nama | Branch |
| --- | --- |
| Ghevira Alviani Kamila | `103_Ghevira` |
| Luthfiana Ariba | `110_LuthfianaAriba` |

Pengerjaan memakai pair programming (driver dan navigator bergantian). Perubahan digabung ke
`main` lewat Pull Request. Pembagian kerja dan pemakaian AI dijelaskan di
[`docs/LAPORAN_AKHIR.md`](docs/LAPORAN_AKHIR.md) dan [`docs/LOG_AI.md`](docs/LOG_AI.md).
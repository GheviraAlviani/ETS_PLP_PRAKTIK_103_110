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
| Luthfiana Ariba Kusna | `110_LuthfianaAriba` |

Pengerjaan memakai pair programming (driver dan navigator bergantian). Perubahan digabung ke
`main` lewat Pull Request. Pembagian kerja dan pemakaian AI dijelaskan di
[`docs/LAPORAN_AKHIR.md`](docs/LAPORAN_AKHIR.md) dan [`docs/LOG_AI.md`](docs/LOG_AI.md).

## Cara Kerja
```text
teks SQL -> lexer -> parser -> resolver -> analyzer -> CRUD matrix
            token     AST      kolom ke    C/R/U/D
                               tabel       per tabel
```
| Tahap | File | Tugas |
| Lexer | crud/lexer.py | Memecah teks menjadi token, membuang komentar, mengenali string, operator, dan parameter |
| Parser | crud/parser.py | Recursive descent menjadi AST, dengan error recovery (panic mode) di ; |
| Resolver | crud/resolver.py | Menentukan kolom milik tabel mana lewat scope bersarang, melaporkan diagnostik |
| Analyzer | crud/analyzer.py | Menurunkan operasi C/R/U/D per tabel dari AST |
| Pipeline | crud/pipeline.py | Menyambungkan keempat tahap, analyze_source(text) |
| CLI |crud/cli.py | Antarmuka baris perintah |

Batasan arsitektur: tidak ada skema database, analyzer bekerja di atas AST (bukan teks mentah dan tanpa regex), dan baseline/regex_extractor.py sengaja dibiarkan naif sebagai pembanding.
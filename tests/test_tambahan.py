"""Test tambahan buatan kelompok.

Isi dengan:
1. Satu test regresi untuk setiap bug yang kalian perbaiki (gagal sebelum perbaikan,
   lulus sesudahnya). Beri nama yang menjelaskan bug-nya.
2. Lima test kasus tepi, masing-masing dengan komentar singkat mengapa kasus itu berisiko.
"""

from crud.lexer import TokenType as T, tokenize


def test_regresi_keyword_campuran_huruf_dan_identifier_berawalan_keyword():
    # Keyword tidak peka huruf besar/kecil (spek 2.2), dan nilainya jadi huruf besar.
    toks = tokenize("Select selection")
    assert toks[0].type == T.KEYWORD and toks[0].value == "SELECT"
    # "selection" hanya DIAWALI keyword, jadi tetap IDENT dan teksnya tidak diubah.
    assert toks[1].type == T.IDENT and toks[1].value == "selection"
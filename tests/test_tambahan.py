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

def test_regresi_operator_tidak_sama_dengan_satu_token():
    # <> harus satu token OP (spek 2.5, maximal munch), bukan '<' lalu '>'.
    toks = [t for t in tokenize("a <> b") if t.type != T.EOF]
    assert [t.value for t in toks] == ["a", "<>", "b"]
    assert toks[1].type == T.OP
    # tanpa spasi pun harus tetap satu token
    assert [t.value for t in tokenize("a<>b") if t.type != T.EOF] == ["a", "<>", "b"]

def test_regresi_kutip_ganda_dalam_string_jadi_satu_token():
    # '' di dalam string berarti SATU kutip (spek 2.4), bukan akhir string.
    toks = [t for t in tokenize("'O''Brien'") if t.type != T.EOF]
    assert len(toks) == 1
    assert toks[0].type == T.STRING and toks[0].value == "O'Brien"
    
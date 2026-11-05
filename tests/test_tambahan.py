"""Test tambahan buatan kelompok.

Isi dengan:
1. Satu test regresi untuk setiap bug yang kalian perbaiki (gagal sebelum perbaikan,
   lulus sesudahnya). Beri nama yang menjelaskan bug-nya.
2. Lima test kasus tepi, masing-masing dengan komentar singkat mengapa kasus itu berisiko.
"""

from crud.lexer import TokenType as T, tokenize
from crud.parser import parse_sql


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

def test_regresi_and_lebih_kuat_dari_or():
    # a OR (b AND c), bukan (a OR b) AND c  (spek 3.1)
    script = parse_sql("SELECT a FROM t WHERE a = 1 OR b = 2 AND c = 3")
    assert script.errors == []
    where = script.statements[0].where
    assert where.op == "OR"
    assert where.left.op == "="
    assert where.right.op == "AND"


def test_regresi_dua_cabang_and_digabung_or():
    # (a AND b) OR (c AND d)
    script = parse_sql("SELECT a FROM t WHERE a = 1 AND b = 2 OR c = 3 AND d = 4")
    where = script.statements[0].where
    assert where.op == "OR"
    assert where.left.op == "AND"
    assert where.right.op == "AND"

def test_regresi_and_lebih_kuat_dari_or():
    # a OR (b AND c), bukan (a OR b) AND c  (spek 3.1)
    script = parse_sql("SELECT a FROM t WHERE a = 1 OR b = 2 AND c = 3")
    assert script.errors == []
    where = script.statements[0].where
    assert where.op == "OR"
    assert where.left.op == "="
    assert where.right.op == "AND"


def test_regresi_dua_cabang_and_digabung_or():
    # (a AND b) OR (c AND d)
    script = parse_sql("SELECT a FROM t WHERE a = 1 AND b = 2 OR c = 3 AND d = 4")
    where = script.statements[0].where
    assert where.op == "OR"
    assert where.left.op == "AND"
    assert where.right.op == "AND"

def test_regresi_recovery_berhenti_di_titik_koma():
    # Setiap statement rusak = satu error; statement valid sesudahnya tetap diproses (spek 6).
    script = parse_sql("SELECT FROM a; SELECT x FROM; SELECT y FROM z;")
    assert len(script.errors) == 2
    assert len(script.statements) == 1

def test_regresi_recovery_statement_valid_setelah_error():
    script = parse_sql("SELECT FROM a;\nSELECT x FROM t;")
    assert len(script.errors) == 1
    assert len(script.statements) == 1
    assert script.statements[0].line == 2

def test_regresi_left_outer_join():
    script = parse_sql("SELECT a FROM t LEFT OUTER JOIN u ON t.id = u.id")
    assert script.errors == []
    assert script.statements[0].joins[0].kind == "LEFT"
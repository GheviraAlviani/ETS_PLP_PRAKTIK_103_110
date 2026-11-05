"""Test tambahan buatan kelompok.

Isi dengan:
1. Satu test regresi untuk setiap bug yang kalian perbaiki (gagal sebelum perbaikan,
   lulus sesudahnya). Beri nama yang menjelaskan bug-nya.
2. Lima test kasus tepi, masing-masing dengan komentar singkat mengapa kasus itu berisiko.
"""

from crud.lexer import TokenType as T, tokenize
from crud.parser import parse_sql
from crud.resolver import Resolver
from crud.ast_nodes import ColumnRef, iter_nodes
from crud.analyzer import analyze_statement
import pytest
from crud.lexer import LexError

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

def _kolom(sql):
    script = parse_sql(sql)
    diags = Resolver().resolve_script(script)
    cols = [(c.qualifier, c.name, c.resolved)
            for c in iter_nodes(script.statements) if isinstance(c, ColumnRef)]
    return cols, diags

def test_regresi_alias_dalam_menutupi_alias_luar():
    # Alias x di subquery milik pesanan, menutupi alias x di luar (spek 4.3).
    cols, _ = _kolom("SELECT x.id FROM pelanggan x WHERE x.id IN "
                     "(SELECT x.pelanggan_id FROM pesanan x WHERE x.total > 5)")
    dalam = [c for c in cols if c[1] in ("pelanggan_id", "total")]
    luar = [c for c in cols if c[1] == "id"]
    assert dalam and all(c[2] == "pesanan" for c in dalam)
    assert luar and all(c[2] == "pelanggan" for c in luar)

def test_regresi_correlated_subquery_tetap_melihat_alias_luar():
    # Penjaga: setelah perbaikan, subquery tetap bisa merujuk alias luar.
    cols, diags = _kolom("SELECT p.a FROM t p WHERE EXISTS "
                         "(SELECT 1 FROM u q WHERE q.id = p.id)")
    assert diags == []
    assert ("p", "id", "t") in cols and ("q", "id", "u") in cols

def test_regresi_alias_delete_tidak_bocor_ke_statement_berikutnya():
    script = parse_sql("DELETE FROM sesi s WHERE s.a = 1; SELECT s.id FROM u")
    resolver = Resolver()
    diags = resolver.resolve_script(script)
    assert resolver.scope is None  # tidak ada scope tersisa (spek 4.5)
    kolom_s = [c for c in iter_nodes(script.statements[1]) if isinstance(c, ColumnRef)]
    assert kolom_s[0].resolved is None
    assert any(d.level == "error" and "'s'" in d.message for d in diags)

def test_regresi_subquery_di_update_hanya_dibaca():
    # Tabel di subquery selalu R, apa pun jenis statement luarnya (spek 5).
    where = parse_sql("UPDATE pesanan SET status = 'X' "
                      "WHERE pelanggan_id IN (SELECT id FROM pelanggan)")
    assert analyze_statement(where.statements[0]) == {"pesanan": {"U"}, "pelanggan": {"R"}}
    setclause = parse_sql("UPDATE t SET a = (SELECT b FROM u)")
    assert analyze_statement(setclause.statements[0]) == {"t": {"U"}, "u": {"R"}}

def test_regresi_update_membaca_tabelnya_sendiri_lewat_subquery():
    # Tabel yang sama dibaca dan diubah: harus R dan U sekaligus.
    script = parse_sql("UPDATE t SET a = (SELECT MAX(a) FROM t)")
    assert analyze_statement(script.statements[0]) == {"t": {"R", "U"}}

def test_komentar_blok_tidak_menghasilkan_token():
    # Komentar blok dibuang lexer, tidak sampai ke parser (spek 2.3).
    toks = tokenize("SELECT /* abc */ a")
    assert [t.value for t in toks if t.type != T.EOF] == ["SELECT", "a"]


def test_komentar_blok_lintas_baris_menjaga_nomor_baris():
    toks = tokenize("/* a\n b\n c */ SELECT")
    assert toks[0].value == "SELECT" and toks[0].line == 3


def test_komentar_blok_tidak_ditutup_adalah_lexerror():
    with pytest.raises(LexError) as info:
        tokenize("SELECT /* abc")
    assert info.value.line == 1 and info.value.col == 8


def test_komentar_blok_boleh_berisi_bintang():
    assert [t.value for t in tokenize("SELECT /* a * b ** c */ x") if t.type != T.EOF] == ["SELECT", "x"]
    assert [t.value for t in tokenize("/**/ SELECT") if t.type != T.EOF] == ["SELECT"]


def test_komentar_blok_tidak_bersarang():
    # Komentar berakhir di */ pertama (spek 2.3: tidak bersarang).
    toks = tokenize("/* a /* b */ SELECT")
    assert [t.value for t in toks if t.type != T.EOF] == ["SELECT"]
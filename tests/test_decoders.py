"""Unit tests for the DBC decoders — run without needing a real MPQ.

    python -m pytest tests/           (or: python tests/test_decoders.py)
"""
import os
import struct
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from decoders.charbaseinfo import CharBaseInfoDecoder  # noqa: E402
from decoders.dbc import GenericDbcDecoder             # noqa: E402


def _make_charbaseinfo(combos):
    """Build a minimal CharBaseInfo.dbc blob (2 bytes/record)."""
    rec_size = 2
    body = b"".join(bytes([r, c]) for r, c in combos)
    header = b"WDBC" + struct.pack("<4I", len(combos), 2, rec_size, 0)
    return header + body


def test_charbaseinfo_flags_new_combos():
    combos = [
        (1, 1),   # Human Warrior  -> standard
        (1, 3),   # Human Hunter   -> NEW
        (7, 5),   # Gnome Priest   -> NEW
        (5, 2),   # Undead Paladin -> NEW
        (2, 3),   # Orc Hunter     -> standard
    ]
    blob = _make_charbaseinfo(combos)
    out = CharBaseInfoDecoder().render("CharBaseInfo.dbc", blob)
    assert "Human Hunter" in out
    assert "Gnome Priest" in out
    assert "Undead Paladin" in out
    assert "Human Warrior" not in out      # standard -> not listed as new
    assert "3 non-standard" in out


def test_charbaseinfo_all_standard():
    blob = _make_charbaseinfo([(1, 1), (2, 3)])
    out = CharBaseInfoDecoder().render("CharBaseInfo.dbc", blob)
    assert "nothing added" in out


def test_generic_dbc_header():
    blob = b"WDBC" + struct.pack("<4I", 10, 4, 16, 32) + b"\x00" * (10 * 16 + 32)
    out = GenericDbcDecoder().render("SomeOther.dbc", blob)
    assert "10" in out and "WDBC" in out


if __name__ == "__main__":
    test_charbaseinfo_flags_new_combos()
    test_charbaseinfo_all_standard()
    test_generic_dbc_header()
    print("all tests passed")

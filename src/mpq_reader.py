"""MPQ loader abstraction.

Currently backed by mpyq (MIT, pure-Python). If a patch ever uses a compression
mpyq can't handle, swap the body of `open_archive` for a StormLib-backed reader
(`apt install smpq`) — the rest of the tool only depends on the small interface
below, so nothing else changes.
"""
from __future__ import annotations

from typing import List


class Archive:
    """Minimal read interface over an MPQ file."""

    def __init__(self, path: str):
        from mpyq import MPQArchive  # imported lazily so tests don't need it
        self._path = path
        self._mpq = MPQArchive(path)

    def files(self) -> List[str]:
        names = []
        for f in (self._mpq.files or []):
            name = f.decode("utf-8", "replace") if isinstance(f, bytes) else f
            if name and not name.startswith("("):  # skip (listfile), (attributes)
                names.append(name)
        return sorted(names)

    def read(self, name: str) -> bytes:
        return self._mpq.read_file(name)


def open_archive(path: str) -> Archive:
    return Archive(path)

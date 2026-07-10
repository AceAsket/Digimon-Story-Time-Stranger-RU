#!/usr/bin/env python3
"""Use one Russian spelling for Mechanorimon in names and prose."""

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CANONICAL = "Механоримон"
OLD = "Меканоримон"
TARGETS = {
    ROOT / "csv/patch_text01/text/digimon_profile.mbe/000_Sheet1.csv": {
        "digimon_0463_profile": 1,
        "digimon_0615_profile": 2,
    },
    ROOT / "csv/patch_text01/text/jogress_skill_name.mbe/000_Sheet1.csv": {
        "40003": 1,
    },
}


def read_rows(path: Path) -> list[list[str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.reader(handle))


def write_rows(path: Path, rows: list[list[str]]) -> None:
    raw = path.read_bytes()
    encoding = "utf-8-sig" if raw.startswith(b"\xef\xbb\xbf") else "utf-8"
    newline = "\r\n" if b"\r\n" in raw else "\n"
    with path.open("w", encoding=encoding, newline="") as handle:
        csv.writer(handle, lineterminator=newline).writerows(rows)


def main() -> None:
    changed = current = 0
    for path, targets in TARGETS.items():
        rows = read_rows(path)
        by_id = {row[0]: row for row in rows[1:] if len(row) >= 2}
        file_changed = False
        for row_id, expected_count in targets.items():
            row = by_id.get(row_id)
            if row is None:
                raise ValueError(f"missing row {path}:{row_id}")
            old_count = row[1].count(OLD)
            canonical_count = row[1].count(CANONICAL)
            if old_count == expected_count:
                row[1] = row[1].replace(OLD, CANONICAL)
                changed += expected_count
                file_changed = True
            elif old_count == 0 and canonical_count >= expected_count:
                current += expected_count
            else:
                raise ValueError(
                    f"unexpected spelling count {path}:{row_id}: "
                    f"old={old_count}, canonical={canonical_count}"
                )
        if file_changed:
            write_rows(path, rows)
    print(f"Mechanorimon spellings changed: {changed}")
    print(f"Mechanorimon spellings already current: {current}")


if __name__ == "__main__":
    main()

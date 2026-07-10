#!/usr/bin/env python3
"""Balance the reported early-game Digitter log lines."""

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "csv/patch_text01/text/digitter_message.mbe/000_Sheet1.csv"

UPDATES = {
    "main_010_120_010": (
        "Та девушка сказала, что что-то должно произойти на крыше.",
        "Та девушка сказала, что на крыше\nдолжно что-то произойти.",
    ),
    "main_010_120_011": (
        "Кажется, у неё больше информации, чем у нас. Возможно, стоит\nостаться с ней.",
        "Похоже, она знает больше нас.\nВозможно, пока лучше не отходить от неё.",
    ),
}


def main() -> None:
    with PATH.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.reader(handle))
    by_id = {row[0]: row for row in rows if len(row) >= 2}
    changed = 0
    current = 0
    for row_id, (old, new) in UPDATES.items():
        row = by_id.get(row_id)
        if row is None:
            raise SystemExit(f"Missing Digitter row: {row_id}")
        if row[1] == new:
            current += 1
        elif row[1] == old:
            row[1] = new
            changed += 1
        else:
            raise SystemExit(f"Unexpected Digitter text: {row_id}: {row[1]!r}")
    if changed:
        with PATH.open("w", encoding="utf-8", newline="") as handle:
            csv.writer(handle, lineterminator="\n").writerows(rows)
    longest = max(len(line) for _, new in UPDATES.values() for line in new.splitlines())
    print(f"Targets: {len(UPDATES)}")
    print(f"Changed: {changed}")
    print(f"Already current: {current}")
    print(f"Longest line: {longest}")


if __name__ == "__main__":
    main()

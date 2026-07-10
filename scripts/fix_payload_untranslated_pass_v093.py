#!/usr/bin/env python3
"""Fix source-checked visible English remnants found in the current payload."""

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "csv/addcont_02_text01/message/d220.mbe/000_Sheet1.csv"
KEY = "d220_040_020"
OLD = "...Hm?"
NEW = "...Хм?"


def main() -> None:
    with TARGET.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.reader(handle))

    row = next((candidate for candidate in rows if candidate and candidate[0] == KEY), None)
    if row is None or len(row) < 3:
        raise SystemExit(f"Missing or malformed row {KEY!r} in {TARGET}")
    if row[2] == NEW:
        changed = 0
    elif row[2] == OLD:
        row[2] = NEW
        changed = 1
    else:
        raise SystemExit(f"Unexpected text for {KEY!r}: {row[2]!r}")

    if changed:
        with TARGET.open("w", encoding="utf-8-sig", newline="") as handle:
            csv.writer(handle, lineterminator="\n").writerows(rows)

    print("Targets: 1")
    print(f"Changed: {changed}")
    print(f"Already current: {1 - changed}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Restore the final source idiom with a deliberate literal bite image."""

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "csv/patch_text01/message/d09.mbe/000_Sheet1.csv"
KEY = "f_d0905_0010_0190"
OLD = (
    "Мы не хотели, чтобы какие-нибудь убийцы последовали за нами по\n"
    "мосту, но, похоже, наш план сработал!"
)
NEW = (
    "Мы не хотели, чтобы убийцы перешли мост вслед за нами,\n"
    "но наш план обернулся против нас — и больно укусил!"
)


def main() -> None:
    with PATH.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.reader(handle))
    row = next((item for item in rows if item and item[0] == KEY), None)
    if row is None:
        raise SystemExit(f"Missing key {KEY!r} in {PATH}")
    if row[2] == NEW:
        print("Changed: 0\nAlready current: 1")
        return
    if row[2] != OLD:
        raise SystemExit(f"Unexpected text for {KEY}: {row[2]!r}")
    row[2] = NEW
    with PATH.open("w", encoding="utf-8-sig", newline="") as handle:
        csv.writer(handle, lineterminator="\n").writerows(rows)
    print("Changed: 1\nAlready current: 0")


if __name__ == "__main__":
    main()

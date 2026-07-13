#!/usr/bin/env python3
"""Fix player-visible broken placeholder punctuation found by v088."""

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "csv/patch_text01/message/m250.mbe/000_Sheet1.csv"
ROW_ID = "m250_035_110"
OLD = (
    "Если бы мне пришлось??... Я бы сказала, что такого целителя вы,\n"
    "возможно, сможете найти в деревне у моря."
)
NEW = (
    "Если предположить... Думаю, такого целителя можно найти\n"
    "в деревне у моря."
)


def main() -> None:
    raw = PATH.read_bytes()
    encoding = "utf-8-sig" if raw.startswith(b"\xef\xbb\xbf") else "utf-8"
    newline = "\r\n" if b"\r\n" in raw else "\n"
    with PATH.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.reader(handle))
    row = next((item for item in rows if item and item[0] == ROW_ID), None)
    if row is None or len(row) < 3:
        raise ValueError(f"missing row {ROW_ID}")
    changed = row[2] != NEW
    if row[2] == OLD:
        row[2] = NEW
    elif row[2] != NEW:
        raise ValueError(f"unexpected text for {ROW_ID}: {row[2]!r}")
    with PATH.open("w", encoding=encoding, newline="") as handle:
        csv.writer(handle, lineterminator=newline).writerow(rows[0])
        csv.writer(handle, lineterminator=newline, quoting=csv.QUOTE_ALL).writerows(rows[1:])
    print(f"Broken marker fixed: {int(changed)}")
    print(f"Broken marker already current: {int(not changed)}")


if __name__ == "__main__":
    main()

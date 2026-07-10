#!/usr/bin/env python3
"""Fix source-order move names missed by global profile-name matching."""

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "csv/patch_text01/text/digimon_profile.mbe/000_Sheet1.csv"


def replace_once(text: str, old: str, new: str, identity: str) -> tuple[str, bool]:
    count = text.count(old)
    if count == 1:
        return text.replace(old, new, 1), True
    if count == 0 and new in text:
        return text, False
    raise SystemExit(f"Ambiguous fragment for {identity}: {old!r} count={count}")


def main() -> None:
    with PATH.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.reader(handle))
    row_by_id = {row[0]: row for row in rows if row}
    changed = 0

    slayer = row_by_id["digimon_0213_profile"]
    text = slayer[1]
    replacements = [
        ("Вторая форма — «Разрез Тэнрю»", "Вторая форма — «Разрез Сёрю»"),
        ("«Тэнрю\nСлэш»", "«Разрез Тэнрю»"),
        ("«Корю Слэш»", "«Разрез Корю»"),
    ]
    for old, new in replacements:
        text, did_change = replace_once(text, old, new, "digimon_0213_profile")
        changed += int(did_change)
    slayer[1] = text

    justimon = row_by_id["digimon_0737_profile"]
    old = (
        "позволяет ему чередовать силовой\n"
        "тип Ускоряющая рука, электрический тип Блиц-рука и\n"
        "режущий тип Critical Arm."
    )
    new = (
        "позволяет выбирать одну из трёх конфигураций:\n"
        "«Ускоряющая рука» силового типа, «Блиц-рука»\n"
        "электрического типа или «Критическая рука» режущего типа."
    )
    justimon[1], did_change = replace_once(justimon[1], old, new, "digimon_0737_profile")
    changed += int(did_change)

    if changed:
        with PATH.open("w", encoding="utf-8-sig", newline="") as handle:
            csv.writer(handle, lineterminator="\n").writerows(rows)

    print("Target move references: 4")
    print(f"Changed: {changed}")
    print(f"Already current: {4 - changed}")


if __name__ == "__main__":
    main()

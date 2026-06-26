from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CHAR_NAMES = ROOT / "csv" / "patch_text01" / "text" / "char_name.mbe" / "000_Sheet1.csv"
OUT = ROOT / "exports" / "digimon_mode_abbreviation_fixes.csv"


FIXES = {
    "char_BELPHEMON_RM": ("Бельфемон: Режим ярости", "RM = Rage Mode"),
    "char_BELPHEMON_RM_BIG": ("Бельфемон: Режим ярости", "RM = Rage Mode"),
    "char_CHRONOMON_DESTROY": ("Хрономон: Режим разрушения", "DM = Destroy Mode"),
    "char_DUKEMON_CM": ("Дюкмон: Багровый режим", "CM = Crimson Mode"),
    "char_JUNOMON_HYSTERICMODE": ("Юномон: Истерический режим", "HM = Hysteric Mode"),
    "char_JUNOMON_HYSTERICMODE_ADD": ("Юномон: Истерический режим (копья)", "HM = Hysteric Mode; local suffix preserved"),
    "char_BELPHEMON_SM": ("Бельфемон: Режим сна", "SM = Sleep Mode"),
    "char_BELPHEMON_SM_BIG": ("Бельфемон: Режим сна", "SM = Sleep Mode"),
    "char_BACCHUSMON_DRUNK": ("Вакхмон: Режим опьянения", "DM = Deisui Mode"),
    "char_BEELZEMON_BM": ("Вельзевумон: Бласт-режим", "BM = Blast Mode for Beelzemon/Beelzebumon"),
    "char_BEELZEMON_BM_BIG": ("Вельзевумон: Бласт-режим", "BM = Blast Mode for Beelzemon/Beelzebumon"),
    "char_SHINEGREYMON_BM": ("Шайн Греймон: Взрывной режим", "BM = Burst Mode"),
    "char_RAVEMON_BM": ("Равемон: Взрывной режим", "BM = Burst Mode"),
    "char_ROSEMON_BM": ("Роузмон: Взрывной режим", "BM = Burst Mode"),
}


def main() -> None:
    with CHAR_NAMES.open("r", encoding="utf-8-sig", newline="") as f:
        rows = list(csv.reader(f))

    applied: list[dict[str, str]] = []
    for row in rows[1:]:
        if len(row) < 2 or row[0] not in FIXES:
            continue
        after, meaning = FIXES[row[0]]
        before = row[1]
        if before == after:
            continue
        row[1] = after
        applied.append({"id": row[0], "before": before, "after": after, "meaning": meaning})

    with CHAR_NAMES.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f, lineterminator="\n")
        writer.writerows(rows)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8-sig", newline="") as f:
        fieldnames = ["id", "before", "after", "meaning"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(applied)

    print("applied", len(applied))
    print(OUT)


if __name__ == "__main__":
    main()

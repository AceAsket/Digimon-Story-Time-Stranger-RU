#!/usr/bin/env python3
"""Fix the remaining source-checked story/DLC lines at overflow risk.

Only exact, manually reviewed rows are touched.  The replacements preserve the
English meaning, repair several inherited machine-translation errors, and keep
every visible line at 65 characters or fewer.
"""

from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CSV_ROOT = ROOT / "csv"


UPDATES: dict[tuple[str, str, str], tuple[str, str]] = {
    (
        "addcont_02_text01",
        "message/d220.mbe/000_Sheet1.csv",
        "d220_030_110",
    ): (
        "Это привело к многочисленным пространственно-временным возмущениям, которые Параллельмон\n"
        "использовать в своих интересах, чтобы стать сильнее.",
        "Возникло множество пространственно-временных возмущений.\n"
        "Параллельмон воспользовался ими, чтобы стать сильнее.",
    ),
    (
        "addcont_03_text01",
        "message/d310.mbe/000_Sheet1.csv",
        "d310_040_140",
    ): (
        "Это означает, что фундаментальные законы реальности, которые мы когда-то принимали за\n"
        "предоставленные ломаются из-за Параллельмон. Не хорошо.",
        "Выходит, из-за Параллельмона рушатся даже законы реальности,\n"
        "которые мы считали незыблемыми. Дело плохо.",
    ),
    (
        "addcont_03_text01",
        "message/d320.mbe/000_Sheet1.csv",
        "d320_010_160",
    ): (
        "Что ты такое говоришь?\n"
        "Параллельмон в любом случае будет нелёгким противником. Если мы не объединимся...",
        "Как бы то ни было, Параллельмон — грозный противник.\n"
        "Если мы не объединимся...",
    ),
    (
        "addcont_03_text01",
        "message/d320.mbe/000_Sheet1.csv",
        "d320_040_210",
    ): (
        "Справедливость должна восторжествовать, поэтому то, что мы делаем, не изменится.\n"
        "Если вы попытаетесь остановить нас, мы можем оказаться в серьезном соперничестве.\u200b\u200b",
        "Мы по-прежнему будем вершить правосудие.\n"
        "Попытаетесь нас остановить — станете нашими соперниками.\u200b\u200b",
    ),
    (
        "addcont_03_text01",
        "message/d350.mbe/000_Sheet1.csv",
        "d350_020_150",
    ): (
        "Очевидно, они заставляли себя деволюционировать,\n"
        "чтобы оставаться достаточно малыми и выдерживать путешествия сквозь пространство-время.",
        "Очевидно, они принудительно деволюционировали,\n"
        "чтобы уменьшиться и выдержать пространственно-временной переход.",
    ),
    (
        "patch_text01",
        "message/m390.mbe/000_Sheet1.csv",
        "m390_040_050",
    ): (
        "С искренней надеждой улучшить мир Вулканусмон добросовестно предложил свои знания\n"
        "человечеству. Но, по жестокой иронии судьбы, он сам стал угрозой для мира.",
        "В надежде улучшить мир Вулканусмон искренне поделился\n"
        "знаниями с людьми. Но по жестокой иронии сам стал угрозой миру.",
    ),
}


def main() -> None:
    by_file: dict[tuple[str, str], list[tuple[str, str, str]]] = defaultdict(list)
    for (package, relative, key), (old, new) in UPDATES.items():
        by_file[(package, relative)].append((key, old, new))

    changed = 0
    already_current = 0
    for (package, relative), updates in sorted(by_file.items()):
        path = CSV_ROOT / package / relative
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.reader(handle))

        row_by_key = {row[0]: row for row in rows if row}
        file_changed = False
        for key, old, new in updates:
            row = row_by_key.get(key)
            if row is None:
                raise SystemExit(f"Missing key {key!r} in {path}")
            if len(row) < 3:
                raise SystemExit(f"Malformed row {key!r} in {path}")
            if row[2] == new:
                already_current += 1
                continue
            if row[2] != old:
                raise SystemExit(
                    f"Unexpected text for {key!r} in {path}:\n"
                    f"expected: {old!r}\nactual:   {row[2]!r}"
                )
            row[2] = new
            changed += 1
            file_changed = True

        if file_changed:
            with path.open("w", encoding="utf-8-sig", newline="") as handle:
                csv.writer(handle, lineterminator="\n").writerows(rows)

    longest = max(len(line) for _, new in UPDATES.values() for line in new.splitlines())
    print(f"Targets: {len(UPDATES)}")
    print(f"Changed: {changed}")
    print(f"Already current: {already_current}")
    print(f"Longest replacement line: {longest}")


if __name__ == "__main__":
    main()

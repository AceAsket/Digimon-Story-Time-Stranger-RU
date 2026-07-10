#!/usr/bin/env python3
"""Restore six player-visible rows damaged by literal ``??`` markers."""

from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
UPDATES = {
    (
        "csv/patch_text01/message/t01.mbe/000_Sheet1.csv",
        "f_t0105_0040_0020",
    ): (
        "Привет там! Это???!",
        "Привет! Это же 〇〇〇!",
    ),
    (
        "csv/patch_text01/message/t02.mbe/000_Sheet1.csv",
        "f_t0203_0030_0030",
    ): (
        "Но правительственное здание сейчас на??ом. Как они собираются\n"
        "туда попасть?",
        "Но здание правительства сейчас оцеплено. Как они собираются\n"
        "туда попасть?",
    ),
    (
        "csv/patch_text01/text/digimon_profile.mbe/000_Sheet1.csv",
        "digimon_0369_profile",
    ): (
        "Хотя он травоядный и\n"
        "сравнительно послушный,?? он разозлен, он\n"
        "обрушивает грозные контратаки своим\n"
        "танкоподобным телом.",
        "Хотя он травояден и сравнительно покладист,\n"
        "в гневе он обрушивает грозные контратаки\n"
        "своим танкоподобным телом.",
    ),
    (
        "csv/patch_text01/text/digimon_profile.mbe/000_Sheet1.csv",
        "digimon_0548_profile",
    ): (
        '"Дикий"\n'
        "Унимон такой же горячий, как любая\n"
        "необъезженная лошадь, но?? приручен,\n"
        "Укротитель может обращаться с ним с легкостью.",
        "«Дикий» Унимон горяч, как необъезженная\n"
        "лошадь, но после приручения укротитель легко\n"
        "может с ним управиться.",
    ),
    (
        "csv/patch_text01/text/digimon_profile.mbe/000_Sheet1.csv",
        "digimon_0584_profile",
    ): (
        "Дигимон-Жнец, владеющий гигантской косой и\n"
        "цепью. Дигимон-Призрак более продвинутый, чем\n"
        "Бакемон,?? Фантомон овладевает индивидуумом,\n"
        "его судьба почти предрешена.",
        "Дигимон-жнец, владеющий гигантской косой и\n"
        "цепью. Этот более развитый, чем Бакемон,\n"
        "дигимон-призрак почти наверняка обрекает на\n"
        "гибель любого, кем завладеет.",
    ),
    (
        "csv/patch_text01/text/digimon_profile.mbe/000_Sheet1.csv",
        "digimon_0594_profile",
    ): (
        "Гидзамон ведет себя трусливо на суше, но\n"
        "проявляет свирепый нрав,?? возвращается в\n"
        "воду.",
        "На суше Гидзамон ведёт себя трусливо, но,\n"
        "вернувшись в воду, становится свирепым.",
    ),
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
    grouped: dict[str, list[tuple[str, str, str]]] = defaultdict(list)
    for (relative, row_id), (old, new) in UPDATES.items():
        grouped[relative].append((row_id, old, new))
    changed = current = 0
    for relative, updates in grouped.items():
        path = ROOT / relative
        rows = read_rows(path)
        by_id = {row[0]: row for row in rows[1:] if row}
        file_changed = False
        for row_id, old, new in updates:
            row = by_id.get(row_id)
            if row is None or len(row) < 2:
                raise ValueError(f"missing row {relative}:{row_id}")
            field = 2 if "/message/" in relative else 1
            if row[field] == new or new in row[field]:
                current += 1
            elif row[field] == old:
                row[field] = new
                changed += 1
                file_changed = True
            elif old in row[field]:
                row[field] = row[field].replace(old, new)
                changed += 1
                file_changed = True
            else:
                raise ValueError(f"unexpected text {relative}:{row_id}")
        if file_changed:
            write_rows(path, rows)
    print(f"Broken question-marker rows changed: {changed}")
    print(f"Broken question-marker rows already current: {current}")


if __name__ == "__main__":
    main()

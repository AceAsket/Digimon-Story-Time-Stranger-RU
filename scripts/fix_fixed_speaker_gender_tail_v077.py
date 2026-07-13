#!/usr/bin/env python3
"""Fix source-checked first-person gender errors for fixed speakers."""

from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CSV_ROOT = ROOT / "csv"


UPDATES: dict[tuple[str, str, str], str] = {
    ("addcont_02_text01", "message/d220.mbe/000_Sheet1.csv", "d220_050_160"): (
        "Я-я не уверена, что понимаю вашу логику!"
    ),
    ("addcont_02_text01", "message/d220.mbe/000_Sheet1.csv", "d220_070_020"): (
        "После исчезновения Инори я стала\n"
        "одержима созданием видео."
    ),
    ("addcont_02_text01", "message/d250.mbe/000_Sheet1.csv", "d250_040_090"): (
        "Уверена, с Инори было так же.\n"
        "В конце концов, она тоже обожала это шоу!"
    ),
    ("addcont_03_text01", "message/d320.mbe/000_Sheet1.csv", "d320_020_150"): (
        "По-моему, их разговор был даже слишком логичным.\n"
        "В нём совсем не было радости."
    ),
    ("addcont_03_text01", "message/d320.mbe/000_Sheet1.csv", "d320_050_190"): (
        "«Для чего нужна наука, если не для воплощения надежд\n"
        "и мечтаний? Уверена, доктор Юки сказал бы именно так»."
    ),
    ("addcont_03_text01", "message/d320.mbe/000_Sheet1.csv", "d320_060_130"): (
        "Я... не стану отрицать того, что сделала."
    ),
    ("addcont_03_text01", "message/d320.mbe/000_Sheet1.csv", "d320_070_090"): (
        "«Я уже не была уверена, что мы по-прежнему\n"
        "должны защищать именно человечество...»"
    ),
    ("addcont_03_text01", "message/d330.mbe/000_Sheet1.csv", "d330_030_020"): (
        "«Уверена, даже ты уже пожалел об этом.\n"
        "Ведь разрушения снаружи невозможно не замечать»."
    ),
    ("addcont_03_text01", "message/d330.mbe/000_Sheet1.csv", "d330_030_120"): (
        "«Но сейчас мне нужны все свободные руки.\n"
        "У тебя ведь есть две? Уверена, ты сможешь помочь»."
    ),
    ("addcont_03_text01", "message/d340.mbe/000_Sheet1.csv", "d340_022_200"): (
        "Я просто хотела... поступить правильно..."
    ),
    ("addcont_03_text01", "message/d350.mbe/000_Sheet1.csv", "d350_020_400"): (
        "Я уверена, что агент Альфа…"
    ),
    ("patch_text01", "message/d02.mbe/000_Sheet1.csv", "f_d0207_0060_0015"): (
        "Такое насилие... Я знала, что от Титанов добра не жди!"
    ),
    ("patch_text01", "message/d06.mbe/000_Sheet1.csv", "f_d0604_0410_0020"): (
        "Я не могу допустить, чтобы с Минни что-нибудь случилось.\n"
        "Я должна остаться здесь и охранять её."
    ),
    ("patch_text01", "message/d09.mbe/000_Sheet1.csv", "f_d0905_0110_0010"): (
        "Видишь вон те ворота? Это я их создала."
    ),
    ("patch_text01", "message/d09.mbe/000_Sheet1.csv", "f_d0907_0040_0030"): (
        "Не хочу верить, что даже это чувство было ошибкой. Поэтому\n"
        "я должна остановить план Хрономона, пусть даже ценой жизни!"
    ),
    (
        "patch_text01",
        "message/digimon_chat.mbe/000_Sheet1.csv",
        "tail_001_3_reaction_char_TAILMON",
    ): "Я рада! Важно прикрывать друг друга.",
    ("patch_text01", "message/field_text.mbe/000_Sheet1.csv", "dummy_dlc010_0500"): (
        "Меня заставили сражаться лишь потому, что я родилась Титаном,\n"
        "хотя я совсем этого не хотела."
    ),
    ("patch_text01", "message/s010_003.mbe/000_Sheet1.csv", "s010_003_050"): (
        "Я знала, что на тебя можно положиться!\n"
        "Приятно видеть такой энтузиазм!"
    ),
    ("patch_text01", "message/s010_003.mbe/000_Sheet1.csv", "s010_003_250"): (
        "Я конфискую её, если понадобится. А теперь отведу вас туда,\n"
        "где услышала этот крик."
    ),
    ("patch_text01", "message/s070_057.mbe/000_Sheet1.csv", "s070_057_060"): (
        "С тех пор как я увидела Вельземона, меня не покидает\n"
        "странное чувство, которое трудно выразить словами."
    ),
    ("patch_text01", "message/s070_167.mbe/000_Sheet1.csv", "s070_167_610"): (
        "Да. Увидев, как мои братья и сёстры стали сильнее,\n"
        "я рада, что и во мне ещё осталась такая сила."
    ),
    ("patch_text01", "message/s200_148.mbe/000_Sheet1.csv", "s200_148_470"): (
        "Да, уверена, они помогли, но дело было не только в этом."
    ),
    ("patch_text01", "message/s910_170.mbe/000_Sheet1.csv", "s910_170_1030"): (
        "Меня беспокоит возможный временной парадокс,\n"
        "но должна признать: я согласна с Ханае."
    ),
}


if len(UPDATES) != 23:
    raise ValueError(f"expected 23 fixed-speaker targets, got {len(UPDATES)}")


def serialization(path: Path) -> tuple[str, str, bool]:
    raw = path.read_bytes()
    bom = raw.startswith(b"\xef\xbb\xbf")
    body = raw.removeprefix(b"\xef\xbb\xbf")
    newline = "\r\n" if b"\r\n" in body else "\n"
    lines = body.splitlines()
    quote_all = len(lines) > 1 and lines[1].lstrip().startswith(b'"')
    return ("utf-8-sig" if bom else "utf-8"), newline, quote_all


def write_rows(path: Path, rows: list[list[str]]) -> None:
    encoding, newline, quote_all = serialization(path)
    with path.open("w", encoding=encoding, newline="") as handle:
        writer = csv.writer(
            handle,
            lineterminator=newline,
            quoting=csv.QUOTE_ALL if quote_all else csv.QUOTE_MINIMAL,
        )
        if quote_all:
            csv.writer(handle, lineterminator=newline).writerow(rows[0])
            writer.writerows(rows[1:])
        else:
            writer.writerows(rows)


def apply_updates() -> tuple[int, int]:
    grouped: dict[tuple[str, str], dict[str, str]] = defaultdict(dict)
    for (package, relative_path, row_id), replacement in UPDATES.items():
        grouped[(package, relative_path)][row_id] = replacement

    loaded: dict[tuple[str, str], tuple[Path, list[list[str]]]] = {}
    changed = current = 0
    for key, wanted in grouped.items():
        package, relative_path = key
        path = CSV_ROOT / package / relative_path
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.reader(handle))
        counts: defaultdict[str, int] = defaultdict(int)
        for row in rows[1:]:
            if not row or row[0] not in wanted:
                continue
            counts[row[0]] += 1
            if len(row) <= 2:
                raise RuntimeError(f"Missing text column: {path}:{row[0]}")
            if row[2] == wanted[row[0]]:
                current += 1
            else:
                changed += 1
        missing = set(wanted) - set(counts)
        duplicates = {row_id: count for row_id, count in counts.items() if count != 1}
        if missing or duplicates:
            raise RuntimeError(
                f"Target cardinality failure in {path}: "
                f"missing={sorted(missing)}, counts={duplicates}"
            )
        loaded[key] = (path, rows)

    for key, (path, rows) in loaded.items():
        wanted = grouped[key]
        dirty = False
        for row in rows[1:]:
            if row and row[0] in wanted and row[2] != wanted[row[0]]:
                row[2] = wanted[row[0]]
                dirty = True
        if dirty:
            write_rows(path, rows)
    return changed, current


def main() -> None:
    changed, current = apply_updates()
    print(f"Targets: {len(UPDATES)}")
    print(f"Changed: {changed}")
    print(f"Already current: {current}")


if __name__ == "__main__":
    main()

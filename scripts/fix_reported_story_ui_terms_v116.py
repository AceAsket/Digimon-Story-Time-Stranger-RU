#!/usr/bin/env python3
"""Fix the reported story lines, Digitter wrapping, names, and HP/SP terms."""

from __future__ import annotations

import csv
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CSV_ROOT = ROOT / "csv/patch_text01"
TERM_RE = re.compile(r"\b(?:HP|SP)\b")

# Counts before this pass. A zero count is also accepted for idempotent reruns.
TERM_FILES = {
    "message/d02.mbe/000_Sheet1.csv": (1, 1),
    "text/buff_message.mbe/000_Sheet1.csv": (11, 10),
    "text/buff_name.mbe/000_Sheet1.csv": (5, 5),
    "text/info_message.mbe/000_Sheet1.csv": (1, 0),
    "text/jogress_skill_name.mbe/000_Sheet1.csv": (2, 2),
    "text/personality_skill_explanation.mbe/000_Sheet1.csv": (18, 7),
    "text/skill_auto_explanation.mbe/000_Sheet1.csv": (12, 9),
    "text/skill_explanation.mbe/000_Sheet1.csv": (18, 7),
    "text/skill_name.mbe/000_Sheet1.csv": (2, 2),
}

# Preserve the encoding convention already used by each source table.
BOMLESS_FILES = {
    "message/m020.mbe/000_Sheet1.csv",
    "message/rumor_npc.mbe/000_Sheet1.csv",
    "text/buff_message.mbe/000_Sheet1.csv",
    "text/buff_name.mbe/000_Sheet1.csv",
    "text/char_name.mbe/000_Sheet1.csv",
    "text/digitter_message.mbe/000_Sheet1.csv",
    "text/info_message.mbe/000_Sheet1.csv",
    "text/personality_skill_explanation.mbe/000_Sheet1.csv",
}

# The terminology normalization runs first, so HP/SP in guarded old strings below
# are already represented as ОЗ/ОС.
UPDATES = [
    (
        "message/d10.mbe/000_Sheet1.csv",
        "f_d1001_0030_0020",
        2,
        "Но если мы не пробьёмся через него, начнётся серьёзный\n"
        "конфликт. Неужели его никак нельзя открыть?",
        "Но если мы не пройдём через эту дверь, начнётся\n"
        "серьёзный конфликт. Неужели её никак не открыть?",
    ),
    (
        "message/d10.mbe/000_Sheet1.csv",
        "f_d1001_0030_0050",
        2,
        "Мы должны приблизиться к зданию правительства. Мы должны\n"
        "остановить битву, которая вот-вот начнется на его крыше!",
        "Мы уже близко к правительственному зданию. Нужно\n"
        "остановить битву, которая вот-вот начнётся на крыше!",
    ),
    (
        "message/d14.mbe/000_Sheet1.csv",
        "f_d1401_0050_0020",
        2,
        "Я не хочу быть свидетелем всей этой драки. Давайте посмотрим,\n"
        "как высоко нас сможет поднять лифт.",
        "Не хочу смотреть на всю эту драку. Посмотрим,\n"
        "как высоко нас поднимет лифт.",
    ),
    (
        "message/d14.mbe/000_Sheet1.csv",
        "f_d1405_0050_0010",
        2,
        "Ответа нет... Пиёмон говорил что-то о войне между\nДигимонами...",
        "Пиёмон без сознания... Перед этим он что-то говорил\n"
        "о войне между дигимонами...",
    ),
    (
        "message/d14.mbe/000_Sheet1.csv",
        "f_d1405_0060_0010",
        2,
        "Ответа нет... Между Дигимонами правда идёт война?",
        "Пиёмон без сознания... Неужели между дигимонами\n"
        "действительно идёт война?",
    ),
    (
        "message/digimon_chat.mbe/000_Sheet1.csv",
        "pata_001_1_replay",
        2,
        "Это верно.",
        "Да, всё верно.",
    ),
    (
        "message/digimon_chat.mbe/000_Sheet1.csv",
        "pata_001_2_replay",
        2,
        "Что-то пошло не так?",
        "Ты что-то натворил?",
    ),
    (
        "message/digimon_chat.mbe/000_Sheet1.csv",
        "pata_001_3_replay",
        2,
        "Кто-то что-то с тобой сделал?",
        "Тебя кто-то обидел?",
    ),
    (
        "message/digimon_chat.mbe/000_Sheet1.csv",
        "pata_001_4_replay",
        2,
        "Я принесу извинения от их имени.",
        "Давай я извинюсь за того, кто виноват.",
    ),
    (
        "message/rumor_npc.mbe/000_Sheet1.csv",
        "r_d1403_0010_0010",
        2,
        "Что вообще происходит прямо сейчас?!",
        "Что здесь вообще происходит?!",
    ),
    (
        "message/m020.mbe/000_Sheet1.csv",
        "m020_130_022",
        2,
        "Здесь произошло странное нападение.",
        "Нападение произошло при странных обстоятельствах.",
    ),
    (
        "text/digitter_message.mbe/000_Sheet1.csv",
        "field_14_020_1",
        1,
        "Обнаружена неизвестная фазово-электронная форма жизни. Возможно,\n"
        "она что-то знает. Попробуйте установить контакт.",
        "Обнаружена неизвестная фазово-электронная форма жизни.\n"
        "Возможно, она что-то знает. Попробуй установить контакт.",
    ),
    (
        "text/digitter_message.mbe/000_Sheet1.csv",
        "main_020_160_010",
        1,
        "Взаимодействия с неизвестной фазово-электронной формой жизни...\n"
        "Должен быть ценным образцом.",
        "Контакт с неизвестной фазово-электронной формой\n"
        "жизни даст ценный материал для анализа.",
    ),
    (
        "text/digitter_message.mbe/000_Sheet1.csv",
        "main_020_160_011",
        1,
        "Мы передадим данные в аналитический отдел. Продолжай\n"
        "расследование.",
        "Данные изучит аналитический отдел.\nПродолжай расследование.",
    ),
    (
        "text/char_name.mbe/000_Sheet1.csv",
        "char_WANYAMON",
        1,
        "  Ванямон",
        "Ванямон",
    ),
    (
        "text/personality_skill_explanation.mbe/000_Sheet1.csv",
        "1",
        1,
        "Снижает стоимость ОС навыков физической атаки на 10%.",
        "Снижает расход ОС на навыки физических атак на 10%.",
    ),
    (
        "text/personality_skill_explanation.mbe/000_Sheet1.csv",
        "21",
        1,
        "Снижает стоимость ОС навыков восстановления на 10%.",
        "Снижает расход ОС на восстанавливающие навыки на 10%.",
    ),
    (
        "text/personality_skill_explanation.mbe/000_Sheet1.csv",
        "61",
        1,
        "Снижает стоимость ОС навыков магической атаки на 10%.",
        "Снижает расход ОС на навыки магических атак на 10%.",
    ),
]


def read_rows(path: Path) -> list[list[str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.reader(handle))


def main() -> None:
    documents: dict[str, list[list[str]]] = {}
    dirty: set[str] = set()
    term_changes = {"HP": 0, "SP": 0}

    for relative, expected in TERM_FILES.items():
        rows = documents.setdefault(relative, read_rows(CSV_ROOT / relative))
        actual = tuple(
            sum(len(re.findall(rf"\b{term}\b", cell)) for row in rows for cell in row[1:])
            for term in ("HP", "SP")
        )
        if actual == (0, 0):
            continue
        if actual != expected:
            raise SystemExit(
                f"Unexpected HP/SP counts in {relative}: {actual}, expected {expected}"
            )
        for row in rows:
            for index in range(1, len(row)):
                old = row[index]
                term_changes["HP"] += len(re.findall(r"\bHP\b", old))
                term_changes["SP"] += len(re.findall(r"\bSP\b", old))
                row[index] = re.sub(r"\bHP\b", "ОЗ", old)
                row[index] = re.sub(r"\bSP\b", "ОС", row[index])
        dirty.add(relative)

    exact_changed = 0
    exact_current = 0
    for relative, row_id, column, old, new in UPDATES:
        rows = documents.setdefault(relative, read_rows(CSV_ROOT / relative))
        matches = [row for row in rows if row and row[0] == row_id]
        if len(matches) != 1:
            raise SystemExit(f"Expected one row {row_id} in {relative}, found {len(matches)}")
        row = matches[0]
        if len(row) <= column:
            raise SystemExit(f"Missing column {column} for {row_id} in {relative}")
        if row[column] == new:
            exact_current += 1
        elif row[column] == old:
            row[column] = new
            exact_changed += 1
            dirty.add(relative)
        else:
            raise SystemExit(
                f"Unexpected text for {row_id} in {relative}: {row[column]!r}"
            )

    # Also repair a BOM introduced by an interrupted/older run of this pass.
    for relative in documents:
        has_bom = (CSV_ROOT / relative).read_bytes().startswith(b"\xef\xbb\xbf")
        if (relative in BOMLESS_FILES) == has_bom:
            dirty.add(relative)

    for relative in sorted(dirty):
        path = CSV_ROOT / relative
        encoding = "utf-8" if relative in BOMLESS_FILES else "utf-8-sig"
        with path.open("w", encoding=encoding, newline="") as handle:
            csv.writer(handle, lineterminator="\n").writerows(documents[relative])

    print(f"Files written: {len(dirty)}")
    print(f"HP -> ОЗ: {term_changes['HP']}")
    print(f"SP -> ОС: {term_changes['SP']}")
    print(f"Exact changes: {exact_changed}")
    print(f"Already current: {exact_current}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Propagate the localized Twentiest wordplay outside s010_159."""

from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CSV_ROOT = ROOT / "csv"


UPDATES: dict[tuple[str, str, str], str] = {
    # First ZubaEagermon encounter.  s010_001_430 is the male fallback;
    # its H/F runtime rows are regenerated from the reviewed dataset.
    ("patch_text01", "message/s010_001.mbe/000_Sheet1.csv", "s010_001_390"): (
        "Хе-хе-хе... Как сделать эту футболку\n"
        "по-настоящему двадцатейшей?"
    ),
    ("patch_text01", "message/s010_001.mbe/000_Sheet1.csv", "s010_001_410"): (
        "А?! Вы двое тоже двадцатейшие?!"
    ),
    ("patch_text01", "message/s010_001.mbe/000_Sheet1.csv", "s010_001_420"): (
        "Двадцатейшие? Это ещё что значит?"
    ),
    ("patch_text01", "message/s010_001.mbe/000_Sheet1.csv", "s010_001_430"): (
        "Это скорее ощущение, так что объяснить трудно.\n"
        "Как бы ты сделал эту футболку по-двадцатейшему?"
    ),
    ("patch_text01", "message/s010_001.mbe/000_Sheet1.csv", "s010_001_442"): (
        "{next}Одвадцатейшить её."
    ),
    ("patch_text01", "message/s010_001.mbe/000_Sheet1.csv", "s010_001_450"): (
        "Вот что для тебя значит Двадцатейшесть? Тогда я\n"
        "порву ТЕБЯ!"
    ),
    ("patch_text01", "message/s010_001.mbe/000_Sheet1.csv", "s010_001_460"): (
        "Вот что для тебя значит Двадцатейшесть? Тогда я ТЕБЯ\n"
        "в канализации замочу!"
    ),
    ("patch_text01", "message/s010_001.mbe/000_Sheet1.csv", "s010_001_470"): (
        "Ах ты... Думаешь, это смешно? К Двадцатейшести\n"
        "нельзя относиться так легкомысленно!"
    ),
    ("patch_text01", "message/s010_001.mbe/000_Sheet1.csv", "s010_001_480"): (
        "Моя Двадцатейшесть..."
    ),
    ("patch_text01", "message/s010_001.mbe/000_Sheet1.csv", "s010_001_490"): (
        "С кражами футболок разобрались, но появилась новая загадка:\n"
        "что такое Двадцатейшесть?"
    ),
    ("patch_text01", "message/s010_001.mbe/000_Sheet1.csv", "s010_001_540"): (
        "Двадцатейшесть всё ещё загадка для меня,\n"
        "зато я увидела кое-что крутое!"
    ),

    # Arena and repeat-battle dialogue.
    ("patch_text01", "message/arena01.mbe/000_Sheet1.csv", "arena01_f001_022_020"): (
        "Сумеет ли чемпион завоевать титул «Двадцатейшего»?!"
    ),
    ("patch_text01", "message/arena01.mbe/000_Sheet1.csv", "arena01_f001_022_030"): (
        "Он прошёл путь двадцати — Истинный Двадцатейший!\n"
        "Двадцатейший из всех двадцатейших!"
    ),
    ("patch_text01", "message/arena01.mbe/000_Sheet1.csv", "arena01_f001_022_040"): (
        "А, вижу, ты тоже желаешь вступить\n"
        "на путь Двадцатейшести!"
    ),
    ("patch_text01", "message/arena01.mbe/000_Sheet1.csv", "arena01_f001_022_041"): (
        "Хорошо. Уважаю твоё решение."
    ),
    ("patch_text01", "message/arena01.mbe/000_Sheet1.csv", "arena01_f001_022_042"): (
        "Позволь показать, чего я достиг\n"
        "на самой вершине Двадцатейшести!"
    ),
    ("patch_text01", "message/d05.mbe/000_Sheet1.csv", "f_d0506_0240_0010"): (
        "Благодаря тебе я всё ближе к истинной Двадцатейшести.\n"
        "Буду рад сразиться снова в любое время!"
    ),

    # Quest, arena label, and notification copy.
    ("patch_text01", "text/char_name.mbe/000_Sheet1.csv", "char_ARENA_022"): (
        "Истинный Двадцатейший"
    ),
    ("patch_text01", "text/quest_outline.mbe/000_Sheet1.csv", "159"): (
        "Что вообще значит быть «двадцатейшим»?.. Я совсем потерялся\n"
        "и теперь торчу в тупике одного из переулков Синдзюку..."
    ),
    ("patch_text01", "text/digitter_message.mbe/000_Sheet1.csv", "sub_010_159_1"): (
        "Что вообще значит быть «двадцатейшим»?.. Я совсем потерялся\n"
        "и теперь торчу в тупике одного из переулков Синдзюку...\n"
        "Просмотреть детали миссии {decision}"
    ),
    ("patch_text01", "text/digitter_message.mbe/000_Sheet1.csv", "arena_010_220"): (
        "Великий Двадцатейший согласился сразиться с тобой!\n"
        "Но у меня один вопрос: кто или что такое «Двадцатейший»?"
    ),

    # Profiles preserve both the Twentiest gag and the sharp/sharp-looking
    # double meaning; the old versions were otherwise heavily mechanical.
    ("patch_text01", "text/digimon_profile.mbe/000_Sheet1.csv", "digimon_0697_profile"): (
        "Зубамон — одно из Легендарных Орудий,\n"
        "дигимонов, способных превращать свои тела\n"
        "в оружие. Говорят, в руках ангела они могут\n"
        "спасти мир, а в руках дьявола — уничтожить.\n"
        "Зубамон несёт в себе данные Двадцатейшести\n"
        "и часто кричит: «Я Двадцатейший!», хотя сам\n"
        "не знает, что это значит. Он терпеть не может\n"
        "кривизну и стремится к идеальной остроте.\n"
        "И в бою, и в шутках он старается быть острым;\n"
        "удачный день сразу поднимает ему настроение.\n"
        "Его приём «Двадцатейший рывок» — стремительная\n"
        "атака в лоб, но истинная сила Зубамона\n"
        "раскрывается в форме оружия."
    ),
    ("patch_text01", "text/digimon_profile.mbe/000_Sheet1.csv", "digimon_0698_profile"): (
        "«Я Двадцатейший! Я не остановлюсь! Буду\n"
        "мчаться вперёд!» С этими словами в душе\n"
        "Зубамон эволюционировал в ЗубаИгермона.\n"
        "Новая форма идеально воплощает этот дух:\n"
        "ЗубаИгермон неустанно движется вперёд\n"
        "по любой местности, даже если приходится\n"
        "ползти. Особый приём «Вантеон» сворачивает\n"
        "его в шар; вращаясь, он рассекает врагов\n"
        "клинком на хвосте. В форме меча, которой\n"
        "он очень гордится, ЗубаИгермон вкладывает\n"
        "всю силу в удар по любому противнику."
    ),
    ("patch_text01", "text/skill_name.mbe/000_Sheet1.csv", "26971"): (
        "Двадцатейший рывок"
    ),
    ("patch_text01", "text/jogress_skill_name.mbe/000_Sheet1.csv", "26971"): (
        "Двадцатейший рывок"
    ),
}


if len(UPDATES) != 25:
    raise ValueError(f"expected 25 consistency targets, got {len(UPDATES)}")


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


def text_column(relative_path: str) -> int:
    return 2 if relative_path.startswith("message/") else 1


def apply_updates() -> tuple[int, int]:
    grouped: dict[str, dict[str, str]] = defaultdict(dict)
    for (package, relative_path, row_id), replacement in UPDATES.items():
        if package != "patch_text01":
            raise ValueError(f"unexpected package: {package}")
        grouped[relative_path][row_id] = replacement

    loaded: dict[str, tuple[Path, list[list[str]], int]] = {}
    changed = current = 0
    for relative_path, wanted in grouped.items():
        path = CSV_ROOT / "patch_text01" / relative_path
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.reader(handle))
        column = text_column(relative_path)
        counts: defaultdict[str, int] = defaultdict(int)
        for row in rows[1:]:
            if not row or row[0] not in wanted:
                continue
            counts[row[0]] += 1
            if len(row) <= column:
                raise RuntimeError(f"Missing text column: {path}:{row[0]}")
            if row[column] == wanted[row[0]]:
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
        loaded[relative_path] = (path, rows, column)

    for relative_path, (path, rows, column) in loaded.items():
        wanted = grouped[relative_path]
        dirty = False
        for row in rows[1:]:
            if row and row[0] in wanted and row[column] != wanted[row[0]]:
                row[column] = wanted[row[0]]
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

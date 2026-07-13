#!/usr/bin/env python3
"""Apply source-checked wordplay, fixed-gender, and speaker-label fixes.

The English localization contains several deliberate puns and speech quirks
that a literal pass turned into opaque Russian fragments.  Every target below
was reviewed in its surrounding scene.  The updater changes exact IDs only,
preserves the original CSV serialization, and fails when a target is absent.
"""

from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CSV_ROOT = ROOT / "csv"


UPDATES: dict[tuple[str, str, str], str] = {
    # Whamon consistently replaces English "well/anyway" with
    # "whale/any-whale".  The old Russian alternated between literal Кит,
    # transliterated Уэйл/Вэйл and the meaningless Ани-кит.  The recurring
    # Russian forms below recreate the same species-based verbal tic.
    ("patch_text01", "message/arena01.mbe/000_Sheet1.csv", "arena01_f001_005_040"): (
        "Вот так кит! Я точно знаю: Пиноккимон говорит правду!"
    ),
    ("patch_text01", "message/d03.mbe/000_Sheet1.csv", "f_d0301_0080_0030"): (
        "Китово! Запрыгивай!"
    ),
    ("patch_text01", "message/d03.mbe/000_Sheet1.csv", "f_d0301_0080_0040"): (
        "Ну что, китуем или как?"
    ),
    ("patch_text01", "message/d03.mbe/000_Sheet1.csv", "f_d0301_0080_0060"): (
        "Китово, отправляемся!"
    ),
    ("patch_text01", "message/d03.mbe/000_Sheet1.csv", "f_d0301_0160_0010"): (
        "Вот так кит... А вы кто? Кажется,\n"
        "мы уже встречались..."
    ),
    ("patch_text01", "message/d03.mbe/000_Sheet1.csv", "f_d0301_0160_0030"): (
        "Кит с ним! Чем могу помочь?"
    ),
    ("patch_text01", "message/d03.mbe/000_Sheet1.csv", "f_d0301_0160_0040"): (
        "Китово! Хочешь туда? Я не против."
    ),
    ("patch_text01", "message/d03.mbe/000_Sheet1.csv", "f_d0302_0350_0010"): (
        "Вот так кит! Я же только что тебя подвозил!"
    ),
    ("patch_text01", "message/d03.mbe/000_Sheet1.csv", "f_d0302_0350_0020"): (
        "Хм... Память что-то подводит. Ну и кит с ним —\n"
        "подвезу тебя ещё раз!"
    ),
    ("patch_text01", "message/d03.mbe/000_Sheet1.csv", "f_d0302_0350_0030"): (
        "Куда китуем?"
    ),
    ("patch_text01", "message/d03.mbe/000_Sheet1.csv", "f_d0302_0350_0045"): (
        "Вот так кит... Значит, у леди Венусмон есть план!"
    ),
    ("patch_text01", "message/d03.mbe/000_Sheet1.csv", "f_d0302_0350_0050"): (
        "Ну что, китуем? Запрыгиваешь?"
    ),
    ("patch_text01", "message/d03.mbe/000_Sheet1.csv", "f_d0302_0360_0010"): (
        "Срочные дела? Ну и кит с ним — обо мне не волнуйся.\n"
        "Иди уже!"
    ),
    ("patch_text01", "message/d03.mbe/000_Sheet1.csv", "f_d0305_0090_0010"): (
        "Срочные дела? Ну и кит с ним — обо мне не волнуйся.\n"
        "Иди уже!"
    ),
    ("patch_text01", "message/d03.mbe/000_Sheet1.csv", "f_d0305_0090_0020"): (
        "Вот так кит. Что случилось? Хочешь вернуться?"
    ),
    ("patch_text01", "message/d09.mbe/000_Sheet1.csv", "f_d0903_0100_0030"): (
        "Китово! Тогда в путь!"
    ),
    ("patch_text01", "message/d09.mbe/000_Sheet1.csv", "f_d0903_0390_0010"): (
        "Вот так кит — а вот и ты! Я тебя ждал!"
    ),
    ("patch_text01", "message/d09.mbe/000_Sheet1.csv", "f_d0903_0390_0050"): (
        "Ну что, китуем?"
    ),
    ("patch_text01", "message/d09.mbe/000_Sheet1.csv", "f_d0903_0390_0080"): (
        "Китово! Сразу полегчало! Ладно,\n"
        "тогда вперё-о-о-од!"
    ),
    ("patch_text01", "message/d09.mbe/000_Sheet1.csv", "f_d0903_0390_0100"): (
        "Китово, запрыгивай!"
    ),
    ("patch_text01", "message/d09.mbe/000_Sheet1.csv", "f_d0904_0420_0020"): (
        "Рад, что память вернулась и я смог доставить тебя на место.\n"
        "Вот так кит! Удачи!"
    ),
    ("patch_text01", "message/field_text.mbe/000_Sheet1.csv", "g_degi_h0212_0010"): (
        "*принюхивается* Пахнет морским бризом! Инстинкты\n"
        "разыгрались! Поможешь киту добраться до моря?"
    ),
    ("patch_text01", "message/field_text.mbe/000_Sheet1.csv", "g_degi_h0212_0020"): (
        "Места не хватает?\n"
        "Вот так кит... Прости, я слишком большой."
    ),
    ("patch_text01", "message/m170.mbe/000_Sheet1.csv", "m170_100_040"): (
        "Вот так кит... Кто вы? Раз у вас раковина,\n"
        "можно считать, что вы друзья Шеллмона?"
    ),
    ("patch_text01", "message/m170.mbe/000_Sheet1.csv", "m170_100_060"): (
        "Вот так кит! Я так и знал!"
    ),
    ("patch_text01", "message/m170.mbe/000_Sheet1.csv", "m170_100_070"): (
        "Вот так кит... Но раковина-то у тебя..."
    ),
    ("patch_text01", "message/m170.mbe/000_Sheet1.csv", "m170_100_080"): (
        "Хороший довод. Вижу раковину —\n"
        "кит с ним, поверю!"
    ),
    ("patch_text01", "message/m170.mbe/000_Sheet1.csv", "m170_100_090"): (
        "Китово, запрыгивай! Тебе в океан, да?\n"
        "Я отвезу!"
    ),
    ("patch_text01", "message/m170.mbe/000_Sheet1.csv", "m170_110_010"): (
        "Китово! Особая тонкая плёнка удержит воздух.\n"
        "Скажи, когда захочешь вернуться."
    ),

    # Explicit English puns and corrections.
    ("patch_text01", "message/s110_093.mbe/000_Sheet1.csv", "s110_093_372"): (
        "{next}Надеюсь, ты больше не будешь валять коня."
    ),
    ("patch_text01", "message/s110_093.mbe/000_Sheet1.csv", "s110_093_400"): (
        "Это сейчас был каламбур про «валять коня»?\n"
        "Надеюсь, это не твой уровень..."
    ),
    ("patch_text01", "message/s200_149.mbe/000_Sheet1.csv", "s200_149_770"): (
        "Проект «ЭДЕМ»?.. Что такое «Эдем»?"
    ),
    ("patch_text01", "message/s200_149.mbe/000_Sheet1.csv", "s200_149_780"): "{next}Рай.",
    ("patch_text01", "message/s200_149.mbe/000_Sheet1.csv", "s200_149_781"): (
        "{next}Сеть магазинов «Эдион»."
    ),
    ("patch_text01", "message/s200_149.mbe/000_Sheet1.csv", "s200_149_782"): (
        "{next}То, что мы едим."
    ),
    ("patch_text01", "message/s200_149.mbe/000_Sheet1.csv", "s200_149_790"): (
        "Точно, Эдемский сад! Интересно, что за проект\n"
        "позаимствовал это название."
    ),
    ("patch_text01", "message/s200_149.mbe/000_Sheet1.csv", "s200_149_800"): (
        "Точно, там продают еду и канцтовары. Но мы сейчас\n"
        "не про «Эдион»!"
    ),
    ("patch_text01", "message/s200_149.mbe/000_Sheet1.csv", "s200_149_810"): (
        "Надеюсь, мне послышалось. Неужели всё это было\n"
        "ради ужасного каламбура «Эдем — едим»?"
    ),
    ("patch_text01", "message/d05.mbe/000_Sheet1.csv", "f_d0502_0150_0110"): (
        "Кто я? Я Нанимон!"
    ),
    ("patch_text01", "message/d05.mbe/000_Sheet1.csv", "f_d0502_0150_0120"): (
        "«Нянимон»? Ты нянчишь маленьких дигимонов?.."
    ),
    ("patch_text01", "message/d05.mbe/000_Sheet1.csv", "f_d0502_0150_0130"): (
        "Нет! Я Нанимон! Уши прочисти!"
    ),
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "lyla_001_0_char_LILAMON"): (
        "У каждого прекрасного цветка есть свой яд."
    ),
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "lyla_001_2_replay"): (
        "Разве не говорят: «У каждой розы есть шипы»?"
    ),
    (
        "patch_text01",
        "message/digimon_chat.mbe/000_Sheet1.csv",
        "lyla_001_2_reaction_char_LILAMON",
    ): (
        "И это тоже верно. Раз ты так вдумчиво к этому относишься,\n"
        "думаю, всё будет хорошо."
    ),

    # Fixed-character gender and the one remaining player-address form.
    ("patch_text01", "message/s010_156.mbe/000_Sheet1.csv", "s010_156_302"): (
        "{next}Ты уверена, что это был не сон?"
    ),
    ("patch_text01", "message/s010_156.mbe/000_Sheet1.csv", "s010_156_320"): (
        "Дай подумать... Кажется, это было задолго\n"
        "до того, как я встретила тебя..."
    ),
    ("patch_text01", "message/m410.mbe/000_Sheet1.csv", "m410_110_060"): (
        "Вот почему Хрономон оставил яйцо — чтобы его преемник\n"
        "появился на свет. И тогда... наступил день твоего рождения."
    ),
    ("patch_text01", "message/arena01.mbe/000_Sheet1.csv", "arena01_f001_005_042"): (
        "Я никогда не видела, чтобы Уэмон или Пиноккимон лгали."
    ),

    # Descriptive names and nicknames whose grammar identifies a woman or
    # accidentally addresses only the male protagonist.
    ("patch_text01", "text/char_name.mbe/000_Sheet1.csv", "char_HIROKO_nickname"): (
        "Начинающая стримерша"
    ),
    ("patch_text01", "text/char_name.mbe/000_Sheet1.csv", "char_COSPLAYER_TOMOYO"): (
        "Косплеерша Томойо"
    ),
    ("patch_text01", "text/char_name.mbe/000_Sheet1.csv", "char_BEGINNER_COSPLAYER"): (
        "Начинающая косплеерша"
    ),
    ("patch_text01", "text/char_name.mbe/000_Sheet1.csv", "char_ARENA_011"): (
        "Эй, боец! Хочешь сразиться?!"
    ),
    ("patch_text01", "text/digitter_message.mbe/000_Sheet1.csv", "hazama_02_212_10"): (
        "Китово! Запрыгивай ко мне на спину — и в открытое море!\n"
        "Йо-хо-хо! Нас ждут приключения!"
    ),
}


if len(UPDATES) != 53:
    raise ValueError(f"expected 53 reviewed targets, got {len(UPDATES)}")


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
    grouped: dict[tuple[str, str], dict[str, str]] = defaultdict(dict)
    for (package, relative_path, row_id), text in UPDATES.items():
        grouped[(package, relative_path)][row_id] = text

    loaded: dict[tuple[str, str], tuple[Path, list[list[str]], int]] = {}
    changed = current = 0
    for (package, relative_path), wanted in grouped.items():
        path = CSV_ROOT / package / relative_path
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
        loaded[(package, relative_path)] = (path, rows, column)

    # No file is written until all targets have passed the cardinality check.
    for key, (path, rows, column) in loaded.items():
        package, relative_path = key
        wanted = grouped[(package, relative_path)]
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

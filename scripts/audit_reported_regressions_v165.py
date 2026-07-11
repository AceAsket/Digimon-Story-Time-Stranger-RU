#!/usr/bin/env python3
"""Fail-closed audit for localization regressions reported by players.

This check is intentionally strict: the fixtures below are confirmed edits, not
heuristic candidates.  A release must stop if a row disappears, becomes
ambiguous, changes unexpectedly, or one of the known broken forms returns.
"""

from __future__ import annotations

import csv
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


ROOT = Path(__file__).resolve().parents[1]
CSV_ROOT = ROOT / "csv"


@dataclass(frozen=True)
class Fixture:
    package: str
    relative: str
    row_id: str
    column: int
    expected: str


def fixture(
    relative: str,
    row_id: str,
    expected: str,
    *,
    package: str = "patch_text01",
    column: Optional[int] = None,
) -> Fixture:
    if column is None:
        column = 2 if relative.startswith("message/") else 1
    return Fixture(package, relative, row_id, column, expected)


FIXTURES: list[Fixture] = [
    fixture("text/char_name.mbe/000_Sheet1.csv", "char_WANYAMON", "Ванямон"),
    fixture("text/char_name.mbe/000_Sheet1.csv", "char_MECHANORIMON", "Механоримон"),
    fixture("text/char_name.mbe/000_Sheet1.csv", "char_VAMDEMON", "Вамдемон"),
    fixture("text/char_name.mbe/000_Sheet1.csv", "char_CENTRAL_TOWN", "Центральный город"),
    fixture("text/item_name.mbe/000_Sheet1.csv", "1142", "Известный баг"),
    fixture("text/item_ruby.mbe/000_Sheet1.csv", "1142", "Известный баг"),
    fixture(
        "text/skill_name_dlc03.mbe/000_Sheet1.csv",
        "24497",
        "Известный баг",
        package="addcont_03_text01",
    ),
    fixture(
        "text/jogress_skill_name_dlc03.mbe/000_Sheet1.csv",
        "24497",
        "Известный баг",
        package="addcont_03_text01",
    ),
    fixture("text/skill_name.mbe/000_Sheet1.csv", "31011", "Исцеление"),
    fixture("text/skill_ruby.mbe/000_Sheet1.csv", "31011", "Исцеление"),
    fixture("text/jogress_skill_name.mbe/000_Sheet1.csv", "31011", "Исцеление"),
    fixture("text/info_message.mbe/000_Sheet1.csv", "10110100", "Получено: {fc9Капсула ОЗ I x5}."),
    fixture(
        "text/personality_skill_explanation.mbe/000_Sheet1.csv",
        "21",
        "Снижает расход ОС на восстанавливающие навыки на 10%.",
    ),
    fixture(
        "text/item_explanation.mbe/000_Sheet1.csv",
        "83",
        "Драгоценный камень, добываемый из моллюсков.\n"
        "Не путать с чёрным жемчугом, который создаёт Сякомон.\n"
        "Можно продать по высокой цене.",
    ),
    fixture(
        "text/item_explanation.mbe/000_Sheet1.csv",
        "20001",
        "Предмет для Дигифермы.\n"
        "Используйте его, чтобы оформить Дигиферму по своему вкусу.",
    ),
    fixture(
        "message/d10.mbe/000_Sheet1.csv",
        "f_d1001_0030_0010",
        "*вздох* Бесполезно... Эту дверь заклинило.",
    ),
    fixture(
        "message/d10.mbe/000_Sheet1.csv",
        "f_d1001_0030_0020",
        "Но если мы не пройдём через эту дверь, начнётся\n"
        "серьёзный конфликт. Неужели её никак не открыть?",
    ),
    fixture(
        "message/d14.mbe/000_Sheet1.csv",
        "f_d1405_0050_0010",
        "Пиёмон без сознания... Перед этим он что-то говорил\n"
        "о войне между дигимонами...",
    ),
    fixture(
        "message/d14.mbe/000_Sheet1.csv",
        "f_d1405_0060_0010",
        "Пиёмон без сознания... Неужели между дигимонами\n"
        "действительно идёт война?",
    ),
    fixture(
        "message/m030.mbe/000_Sheet1.csv",
        "m030_010_090",
        "Какое-то «правитмственное здание»... взорвалось?\nТы вообще о чём?",
    ),
    fixture(
        "message/rumor_npc.mbe/000_Sheet1.csv",
        "r_d1403_0010_0010",
        "Что здесь вообще происходит?!",
    ),
    fixture(
        "message/m020.mbe/000_Sheet1.csv",
        "m020_130_022",
        "Нападение произошло при странных обстоятельствах.",
    ),
    fixture(
        "text/digitter_message.mbe/000_Sheet1.csv",
        "field_14_020_1",
        "Обнаружена неизвестная фазово-электронная форма жизни.\n"
        "Возможно, она что-то знает. Попробуй установить контакт.",
    ),
    fixture(
        "text/digitter_message.mbe/000_Sheet1.csv",
        "main_020_160_010",
        "Контакт с неизвестной фазово-электронной формой\n"
        "жизни даст ценный материал для анализа.",
    ),
    fixture(
        "text/digitter_message.mbe/000_Sheet1.csv",
        "main_020_160_011",
        "Данные изучит аналитический отдел.\nПродолжай расследование.",
    ),
    fixture("message/digimon_chat.mbe/000_Sheet1.csv", "pata_001_1_replay", "Да, всё верно."),
    fixture("message/digimon_chat.mbe/000_Sheet1.csv", "pata_001_2_replay", "Ты что-то натворил?"),
    fixture("message/digimon_chat.mbe/000_Sheet1.csv", "pata_001_3_replay", "Тебя кто-то обидел?"),
    fixture(
        "message/digimon_chat.mbe/000_Sheet1.csv",
        "pata_001_4_replay",
        "Давай я извинюсь за того, кто виноват.",
    ),
    fixture(
        "message/s050_038.mbe/000_Sheet1.csv",
        "s050_038_0030",
        "Да ладно! О тебе говорит весь город — тебя тут знает каждый!",
    ),
    fixture(
        "message/s050_038.mbe/000_Sheet1.csv",
        "s050_038_0150",
        "Материалы лежат прямо у входа в Центральную башню.\n"
        "Я на тебя рассчитываю!",
    ),
    fixture(
        "message/s050_038.mbe/000_Sheet1.csv",
        "s050_038_0210",
        "Скорее, давай их сюда! ...Идеально. Спасибо.",
    ),
    fixture(
        "message/s050_041.mbe/000_Sheet1.csv",
        "s050_041_0060",
        "Вдруг с ним что-то случилось... Хотя он тот ещё лентяй\n"
        "и часто спит на посту.",
    ),
    fixture(
        "message/s050_041.mbe/000_Sheet1.csv",
        "s050_041_0070",
        "Но если с ним и правда что-то случилось, это уже серьёзно...\n"
        "Лучше всё-таки проверить.",
    ),
    fixture(
        "message/s050_041.mbe/000_Sheet1.csv",
        "s050_041_0180",
        "Как это вышло?.. Ах да. Я смотрел под ноги, пока убирал\n"
        "мусор, и в кого-то врезался...",
    ),
    fixture(
        "message/rumor_npc.mbe/000_Sheet1.csv",
        "r_d0501_0010_0050",
        "Нашу артиллерийскую батарею захватили...",
    ),
    fixture(
        "message/d05.mbe/000_Sheet1.csv",
        "f_d0501_0080_0010",
        "Так это вы прибыли на Блимпмоне?\nКуда ни глянь — всюду вы!",
    ),
    fixture(
        "message/d05.mbe/000_Sheet1.csv",
        "f_d0501_0080_0030",
        "На нас напали Титаны. Тут теперь не до сна.\nБерегите себя!",
    ),
    fixture(
        "message/s200_148.mbe/000_Sheet1.csv",
        "s200_148_140",
        "Хм... Точно! Можешь раздобыть одежду в стиле дигимонов\n"
        "и примерить её?",
    ),
    fixture(
        "message/s200_148.mbe/000_Sheet1.csv",
        "s200_148_200",
        "Теперь ты выглядишь как дигимон — это должно\n"
        "их немного успокоить!",
    ),
    fixture(
        "message/s200_148.mbe/000_Sheet1.csv",
        "s200_148_431",
        "{next}Всё благодаря костюмам.",
    ),
    fixture(
        "message/d05.mbe/000_Sheet1.csv",
        "f_d0502_0140_0020",
        "Отлично, спасибо! Теперь мы сможем выбраться.",
    ),
    fixture(
        "message/d05.mbe/000_Sheet1.csv",
        "f_d0502_0140_0030",
        "Это немного, но держи. Надеюсь, пригодится!",
    ),
    fixture(
        "message/d05.mbe/000_Sheet1.csv",
        "f_d0551_0010_0080",
        "Потрясающе, Наномон! Ещё одна первоклассная идея!\n"
        "Прими моё уважение!",
    ),
]


for relative in (
    "text/skill_name.mbe/000_Sheet1.csv",
    "text/skill_ruby.mbe/000_Sheet1.csv",
    "text/jogress_skill_name.mbe/000_Sheet1.csv",
):
    FIXTURES.extend(
        [
            fixture(relative, "30151", "Громопад I"),
            fixture(relative, "30152", "Громопад II"),
            fixture(relative, "30153", "Громопад III"),
            fixture(relative, "30301", "Адский сокрушитель I"),
            fixture(relative, "30302", "Адский сокрушитель II"),
            fixture(relative, "30303", "Адский сокрушитель III"),
        ]
    )


DISPLAY_FORBIDDEN: list[tuple[str, re.Pattern[str]]] = [
    (
        "latin_HP_SP",
        re.compile(r"(?<![A-Za-zА-Яа-яЁё])(?:HP|SP)(?![A-Za-zА-Яа-яЁё])"),
    ),
    ("old_mechanorimon", re.compile(r"Меканоримон")),
    ("old_datamon", re.compile(r"Дейтамон")),
    ("broken_vamdemon_case", re.compile(r"ВаМдемон")),
    ("old_central_town", re.compile(r"(?:Сентрал|Централ)[- ]Таун")),
    ("old_central_tower", re.compile(r"(?:Сентрал|Централ)[- ]Тауэр")),
    ("old_unconscious_line", re.compile(r"Ответа нет\.\.\.\s*Пиёмон")),
    ("old_door_pronoun", re.compile(r"пробь[её]мся через него|Неужели его никак нельзя открыть", re.I)),
    ("old_now_calque", re.compile(r"Что вообще происходит прямо сейчас", re.I)),
    ("old_attack_calque", re.compile(r"Здесь произошло странное нападение", re.I)),
    ("old_sample_calque", re.compile(r"Должен быть ценным образцом", re.I)),
    (
        "old_zudomon_site_calque",
        re.compile(r"Я отправлю информацию о необходимых мне материалах на ваш сайт", re.I),
    ),
    ("old_zudomon_fame_gender", re.compile(r"насколько ты знаменит", re.I)),
    ("old_zudomon_handover", re.compile(r"Быстро, отдавай их!\.\.\.\s*Идеальный", re.I)),
    ("broken_skill_numeral", re.compile(r"(?:Гремит Гром|Сокрушитель Ада)\s*,?\s*Я")),
]


DIALOGUE_FORBIDDEN: list[tuple[str, re.Pattern[str]]] = [
    ("clarify_calque", re.compile(r"\bвнес(?:и|ите) ясность\b", re.I)),
    ("nap_on_clock_calque", re.compile(r"\bдремать по часам\b", re.I)),
    ("whole_situation_calque", re.compile(r"\bцелая ситуация\b", re.I)),
    ("extremely_cruel_calque", re.compile(r"\bкак чрезвычайно жесток\w*\b", re.I)),
    ("heartless_calque", re.compile(r"\bпросто бессердечн\w*\b", re.I)),
    ("be_able_calque", re.compile(r"\bдолжн\w* быть в состоянии\b", re.I)),
    ("little_but_here_calque", re.compile(r"\bэто немного,? но здесь\b", re.I)),
    ("leave_rest_to_me_calque", re.compile(r"\bдальше я сам\b", re.I)),
    ("everywhere_calque", re.compile(r"\bвы повсюду\b", re.I)),
    ("get_help_calque", re.compile(r"\bполучить помощь\b", re.I)),
    ("fellow_digimon_calque", re.compile(r"\bпарень\s*-?\s*дигимон\b", re.I)),
    ("costumes_calque", re.compile(r"\bвс[её] сделали костюмы\b", re.I)),
    ("lowered_eyes_calque", re.compile(r"\bопустил[аи]? глаза\b", re.I)),
]


def normalized(value: str) -> str:
    return value.replace("\r\n", "\n").replace("\r", "\n")


def looks_like_mojibake(value: str) -> bool:
    """Detect a UTF-8 string that becomes better Cyrillic after reverse decoding."""

    original_cyrillic = sum("\u0400" <= char <= "\u04ff" for char in value)
    for encoding in ("cp1251", "latin-1"):
        try:
            repaired = value.encode(encoding).decode("utf-8")
        except (UnicodeEncodeError, UnicodeDecodeError):
            continue
        repaired_cyrillic = sum("\u0400" <= char <= "\u04ff" for char in repaired)
        if repaired != value and repaired_cyrillic > original_cyrillic:
            return True
    return False


def read_rows(path: Path) -> list[list[str]]:
    try:
        raw = path.read_bytes()
    except OSError as error:
        raise RuntimeError(f"cannot read {path}: {error}") from error
    try:
        raw.decode("utf-8-sig", errors="strict")
    except UnicodeDecodeError as error:
        raise RuntimeError(f"invalid UTF-8 in {path}: {error}") from error
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.reader(handle, strict=True))
    except (OSError, csv.Error) as error:
        raise RuntimeError(f"invalid CSV {path}: {error}") from error
    if not rows:
        raise RuntimeError(f"empty CSV: {path}")
    return rows


def display_value(relative: str, row: list[str]) -> Optional[tuple[int, str]]:
    if relative.startswith("message/") and len(row) > 2:
        return 2, row[2]
    if relative.startswith("text/") and len(row) > 1:
        return 1, row[1]
    return None


def context(value: str) -> str:
    return normalized(value).replace("\n", " / ")[:220]


def main() -> int:
    if not CSV_ROOT.is_dir():
        print(f"Regression audit infrastructure error: CSV root not found: {CSV_ROOT}", file=sys.stderr)
        return 2

    documents: dict[tuple[str, str], list[list[str]]] = {}
    issues: list[str] = []

    try:
        for item in FIXTURES:
            marker = (item.package, item.relative)
            if marker not in documents:
                path = CSV_ROOT / item.package / item.relative
                if not path.is_file():
                    raise RuntimeError(f"fixture file not found: {path}")
                documents[marker] = read_rows(path)
            matches = [row for row in documents[marker] if row and row[0] == item.row_id]
            label = f"{item.package}/{item.relative}:{item.row_id}"
            if len(matches) != 1:
                issues.append(f"fixture_row_count {label}: expected 1, found {len(matches)}")
                continue
            row = matches[0]
            if len(row) <= item.column:
                issues.append(f"fixture_missing_column {label}: column {item.column}")
                continue
            actual = normalized(row[item.column])
            expected = normalized(item.expected)
            if actual != expected:
                issues.append(
                    f"fixture_text_mismatch {label}: actual={context(actual)!r}; "
                    f"expected={context(expected)!r}"
                )

        wanyamon = next(
            item for item in FIXTURES if item.row_id == "char_WANYAMON"
        )
        rows = documents[(wanyamon.package, wanyamon.relative)]
        value = next(row[wanyamon.column] for row in rows if row and row[0] == wanyamon.row_id)
        if value != value.strip():
            issues.append(f"wanyamon_whitespace: {value!r}")

        files = sorted(CSV_ROOT.glob("*_text01/**/*.csv"))
        if not files:
            raise RuntimeError("no *_text01 CSV files found")

        rows_scanned = 0
        display_cells_scanned = 0
        for path in files:
            package = path.relative_to(CSV_ROOT).parts[0]
            relative = path.relative_to(CSV_ROOT / package).as_posix()
            marker = (package, relative)
            rows = documents.get(marker)
            if rows is None:
                rows = read_rows(path)
                documents[marker] = rows
            for row_number, row in enumerate(rows[1:], 2):
                rows_scanned += 1
                display = display_value(relative, row)
                if display is None:
                    continue
                column, value = display
                display_cells_scanned += 1
                label = f"{package}/{relative}:{row_number}:{column + 1}"
                common_checks = (
                    ("replacement_character", "\ufffd" in value),
                    ("embedded_bom", "\ufeff" in value),
                    (
                        "control_character",
                        any(ord(char) < 32 and char not in "\t\r\n" for char in value),
                    ),
                    ("mojibake", looks_like_mojibake(value)),
                )
                for issue_name, found in common_checks:
                    if found:
                        issues.append(f"{issue_name} {label}: {context(value)!r}")
                for issue_name, pattern in DISPLAY_FORBIDDEN:
                    if pattern.search(value):
                        issues.append(f"{issue_name} {label}: {context(value)!r}")

                is_dialogue = relative.startswith("message/") or relative == (
                    "text/digitter_message.mbe/000_Sheet1.csv"
                )
                if is_dialogue:
                    for issue_name, pattern in DIALOGUE_FORBIDDEN:
                        if pattern.search(value):
                            issues.append(f"{issue_name} {label}: {context(value)!r}")

                is_skill_name = relative.startswith("text/") and "skill_name" in relative
                if is_skill_name and value.strip() == "Исцелять":
                    issues.append(f"verb_as_skill_name {label}: {context(value)!r}")

        if rows_scanned == 0 or display_cells_scanned == 0 or not FIXTURES:
            raise RuntimeError(
                "audit scanned an empty dataset "
                f"(rows={rows_scanned}, display={display_cells_scanned}, fixtures={len(FIXTURES)})"
            )
    except RuntimeError as error:
        print(f"Regression audit infrastructure error: {error}", file=sys.stderr)
        return 2

    print("Reported localization regression audit v165")
    print(f"fixture_assertions={len(FIXTURES)}")
    print(f"csv_files_scanned={len(documents)}")
    print(f"csv_rows_scanned={rows_scanned}")
    print(f"display_cells_scanned={display_cells_scanned}")
    print(f"issues={len(issues)}")
    if issues:
        for issue in issues[:100]:
            print(f"ERROR: {issue}", file=sys.stderr)
        if len(issues) > 100:
            print(f"ERROR: ... and {len(issues) - 100} more issue(s)", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

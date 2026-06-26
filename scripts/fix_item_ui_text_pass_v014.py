from __future__ import annotations

import csv
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
APP_ROOT = ROOT / "csv" / "app_text01"
PATCH_ROOT = ROOT / "csv" / "patch_text01"
LOG_PATH = ROOT / "logs" / "fix_item_ui_text_pass_v014.log"
BLANK_TEXT = "\u00a0"

STAT_TOKEN_MAP = {
    "ATK": "АТК",
    "DEF": "ЗАЩ",
    "INT": "ИНТ",
    "SPI": "ДУХ",
    "SPD": "СКР",
    "ACU": "МЕТ",
    "EVA": "УКЛ",
    "CRT": "КРТ",
    "CRI": "КРТ",
}

STAT_TOKEN_RE = re.compile(
    r"(?<![A-Za-zА-Яа-я])("
    + "|".join(sorted(STAT_TOKEN_MAP, key=len, reverse=True))
    + r")(?![A-Za-zА-Яа-я])"
)

PHRASE_REPLACEMENTS = {
    "CRT Rate": "КРТ",
    "CRT damage": "критический урон",
    "CRI boost": "бонус КРТ",
    "ACU boost": "бонус МЕТ",
    "EVA boost": "бонус УКЛ",
}

changes: list[str] = []


def set_csv_values(root: Path, rel_path: str, values: dict[str, str], column: int = 1) -> None:
    path = root / rel_path
    if not path.exists():
        changes.append(f"missing {path.relative_to(ROOT).as_posix()}")
        return

    with path.open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.reader(f))

    found: set[str] = set()
    updated = 0
    for row in rows:
        if len(row) <= column:
            continue
        key = row[0]
        if key not in values:
            continue
        found.add(key)
        new_value = values[key]
        if row[column] != new_value:
            old = row[column]
            row[column] = new_value
            updated += 1
            changes.append(
                f"{path.relative_to(ROOT).as_posix()}: {key}: {old!r} -> {new_value!r}"
            )

    missing = sorted(set(values) - found)
    if missing:
        changes.append(f"{path.relative_to(ROOT).as_posix()}: missing keys {missing}")

    if updated:
        with path.open("w", encoding="utf-8", newline="") as f:
            csv.writer(f, lineterminator="\r\n").writerows(rows)


def normalize_stat_tokens(text: str) -> str:
    for old, new in PHRASE_REPLACEMENTS.items():
        text = text.replace(old, new)
    return STAT_TOKEN_RE.sub(lambda match: STAT_TOKEN_MAP[match.group(1)], text)


def normalize_stat_tokens_in_csv(root: Path) -> None:
    for path in sorted(root.rglob("*.csv")):
        with path.open("r", encoding="utf-8", newline="") as f:
            rows = list(csv.reader(f))

        updated = 0
        for row in rows:
            for column in range(1, len(row)):
                old = row[column]
                new = normalize_stat_tokens(old)
                if old != new:
                    row[column] = new
                    updated += 1
                    if updated <= 20:
                        changes.append(
                            f"{path.relative_to(ROOT).as_posix()}: {row[0]}: {old!r} -> {new!r}"
                        )

        if updated:
            if updated > 20:
                changes.append(f"{path.relative_to(ROOT).as_posix()}: {updated} stat-token edits")
            with path.open("w", encoding="utf-8", newline="") as f:
                csv.writer(f, lineterminator="\r\n").writerows(rows)


def main() -> None:
    blank_item_auto_keys = [
        "22",
        "23",
        "24",
        "25",
        "28",
        "29",
        "30",
        "31",
        "32",
        "33",
        "34",
        "35",
        "36",
        "37",
        "45",
        "46",
    ]

    for root in (APP_ROOT, PATCH_ROOT):
        set_csv_values(
            root,
            "text/common_message.mbe/000_Sheet1.csv",
            {
                "117": "Деньги",
                "11304": "Очки аномалии",
                "150112": "Кол-во",
                "icon_info_description_04_01": "АТК ↑/↓",
                "icon_info_description_04_02": "ЗАЩ ↑/↓",
                "icon_info_description_04_03": "ИНТ ↑/↓",
                "icon_info_description_04_04": "ДУХ ↑/↓",
                "icon_info_description_04_05": "СКР ↑/↓",
                "icon_info_description_04_06": "МЕТ ↑/↓",
                "icon_info_description_04_07": "УКЛ ↑/↓",
                "icon_info_description_04_08": "КРТ ↑/↓",
                "icon_info_description_04_09": "Макс ОЗ ↑/↓",
                "icon_info_description_04_10": "Макс ОС ↑/↓",
                "icon_info_description_05_07": "Повышение ОЗ",
                "icon_info_description_05_08": "Повышение ОС",
                "icon_info_description_05_09": "Повышение АТК",
                "icon_info_description_05_10": "Повышение ЗАЩ",
                "icon_info_description_05_11": "Повышение ИНТ",
                "icon_info_description_05_12": "Повышение ДУХ",
                "icon_info_description_05_13": "Повышение СКР",
            },
        )
        status_name_rel = "text/status_name.mbe/000_Sheet1.csv"
        if (root / status_name_rel).exists():
            set_csv_values(
                root,
                status_name_rel,
                {
                    "0": "Макс. ОЗ",
                    "1": "Макс. ОС",
                    "2": "АТК",
                    "3": "ЗАЩ",
                    "4": "ИНТ",
                    "5": "ДУХ",
                    "6": "СКР",
                    "7": "МЕТ",
                    "8": "УКЛ",
                    "9": "КРТ",
                },
            )
        set_csv_values(
            root,
            "text/personality_effect.mbe/000_Sheet1.csv",
            {
                "0": "–",
                "1": "Увеличивает прирост {fc7АТК} и {fc7ОС}.",
                "2": "Увеличивает прирост {fc7АТК} и {fc7СКР}.",
                "3": "Увеличивает прирост {fc7АТК} и {fc7ЗАЩ}.",
                "4": "Увеличивает прирост {fc7АТК} и {fc7ОЗ}.",
                "5": "Увеличивает прирост {fc7ДУХ} и {fc7ЗАЩ}.",
                "6": "Увеличивает прирост {fc7ДУХ} и {fc7ИНТ}.",
                "7": "Увеличивает прирост {fc7ДУХ} и {fc7ОС}.",
                "8": "Увеличивает прирост {fc7ДУХ} и {fc7ОЗ}.",
                "9": "Увеличивает прирост {fc7ЗАЩ} и {fc7ОЗ}.",
                "10": "Увеличивает прирост {fc7ЗАЩ} и {fc7ОС}.",
                "11": "Увеличивает прирост {fc7ЗАЩ} и {fc7АТК}.",
                "12": "Увеличивает прирост {fc7ЗАЩ} и {fc7ДУХ}.",
                "13": "Увеличивает прирост {fc7ИНТ} и {fc7СКР}.",
                "14": "Увеличивает прирост {fc7ИНТ} и {fc7ДУХ}.",
                "15": "Увеличивает прирост {fc7ИНТ} и {fc7ОС}.",
                "16": "Увеличивает прирост {fc7ИНТ} и {fc7ОЗ}.",
            },
        )
        set_csv_values(
            root,
            "text/key_help_text.mbe/000_Sheet1.csv",
            {
                "key_help_0033": " Журнал диалогов",
                "key_help_0104": " Быстрый доступ",
            },
        )
        set_csv_values(
            root,
            "text/item_auto_explanation.mbe/000_Sheet1.csv",
            {key: BLANK_TEXT for key in blank_item_auto_keys},
        )
        set_csv_values(
            root,
            "text/item_name.mbe/000_Sheet1.csv",
            {
                "37": "Усиление КРТ",
                "1026": "Модуль КРТ I",
                "1027": "Модуль КРТ II",
            },
        )
        set_csv_values(
            root,
            "text/item_ruby.mbe/000_Sheet1.csv",
            {
                "37": "Усиление КРТ",
                "1026": "Модуль КРТ I",
                "1027": "Модуль КРТ II",
            },
        )
        set_csv_values(
            root,
            "text/item_explanation.mbe/000_Sheet1.csv",
            {
                "723": (
                    "Экипируйте на Эгиомона, чтобы начинать бой как Эгиохусмон.\r\n"
                    "Увеличивает критический урон на 20%."
                ),
                "1026": "Усиление КРТ 1\r\n/Экипировка",
                "1027": "Усиление КРТ 2\r\n/Экипировка",
                "1040": "Усиление АТК и КРТ 1\r\n/Экипировка",
                "1041": "Усиление АТК и КРТ 2\r\n/Экипировка",
                "1042": "Усиление ИНТ и КРТ 1\r\n/Экипировка",
                "1043": "Усиление ИНТ и КРТ 2\r\n/Экипировка",
            },
        )
        set_csv_values(
            root,
            "text/skill_explanation.mbe/000_Sheet1.csv",
            {
                "80032": "[Цель: 1 союзник] Увеличивает ЗАЩ на 20% на 3 хода.",
                "80038": "[Цель: 1 союзник] Увеличивает КРТ на 20% на 3 хода.",
                "80040": "[Цель: 1 союзник] Увеличивает МЕТ / УКЛ / КРТ на 20% на 3 хода.",
            },
        )
        normalize_stat_tokens_in_csv(root)

    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    LOG_PATH.write_text("\n".join(changes) + "\n", encoding="utf-8")
    print(f"changes={len(changes)}")
    print(f"log={LOG_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()

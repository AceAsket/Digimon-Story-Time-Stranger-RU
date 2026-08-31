#!/usr/bin/env python3
"""Apply guarded proofreading fixes to skill names and descriptions."""

from __future__ import annotations

import csv
import io
import re
import subprocess
from pathlib import Path

from fix_t01_npc_context_v169 import read_document, unique_row, write_document


ROOT = Path(__file__).resolve().parents[1]
CSV_ROOT = ROOT / "csv"
BASELINE_REF = "v0.1.51"
UPDATES: list[tuple[str, str, str, int, str]] = []
_BASELINE_CACHE: dict[str, list[list[str]]] = {}


def read_baseline(relative: str) -> list[list[str]]:
    if relative in _BASELINE_CACHE:
        return _BASELINE_CACHE[relative]
    object_name = f"{BASELINE_REF}:csv/patch_text01/{relative}"
    result = subprocess.run(
        ["git", "show", object_name],
        cwd=ROOT,
        capture_output=True,
        check=False,
    )
    if result.returncode:
        detail = result.stderr.decode("utf-8", errors="replace").strip()
        raise RuntimeError(f"Cannot read baseline {object_name}: {detail}")
    rows = list(csv.reader(io.StringIO(result.stdout.decode("utf-8-sig"), newline="")))
    _BASELINE_CACHE[relative] = rows
    return rows


def baseline_values(relative: str) -> dict[str, str]:
    return {row[0]: row[1] for row in read_baseline(relative)[1:] if len(row) > 1}


def add(relative: str, row_id: str, replacement: str) -> None:
    UPDATES.append(("patch_text01", relative, row_id, 1, replacement))


def normalized(value: str) -> str:
    return value.replace("\r\n", "\n").replace("\r", "\n")


SKILL_NAME = "text/skill_name.mbe/000_Sheet1.csv"
JOGRESS_NAME = "text/jogress_skill_name.mbe/000_Sheet1.csv"
SKILL_RUBY = "text/skill_ruby.mbe/000_Sheet1.csv"
SKILL_DESCRIPTION = "text/skill_explanation.mbe/000_Sheet1.csv"
AUTO_DESCRIPTION = "text/skill_auto_explanation.mbe/000_Sheet1.csv"


# Keep every runtime copy of a skill name identical.
CANONICAL_NAMES = {
    "10012": "Защита",
    "20443": "Магическая рука",
    "23701": "Ледяной удар абсолютного нуля",
    "32101": "Ментальное поле",
    "70001": "Его сила резко возрастает!",
    "70004": "Его сила продолжает расти…",
}
for relative in (SKILL_NAME, JOGRESS_NAME):
    values = baseline_values(relative)
    for row_id, replacement in CANONICAL_NAMES.items():
        if row_id in values:
            add(relative, row_id, replacement)
add(SKILL_RUBY, "32101", CANONICAL_NAMES["32101"])


ELEMENT_PATTERN = re.compile(
    r"(физическую|магическую|скоростную) атаку "
    r"(\{is\d+\}\{image\(ui_icon_skill_\d+\)\}) "
    r"(Нейтральный|Огонь|Лёд|Растения|Растение|Вода|Электричество|Сталь|Ветер|Земля|Свет|Тьма)"
)


def normalize_skill_description(value: str) -> str:
    value = normalized(value)
    for old, new in (
        ("тяжелый", "тяжёлый"),
        ("серьезный", "серьёзный"),
        ("Крадет", "Крадёт"),
        ("[Цель: Все", "[Цель: все"),
        ("[Цель: Пользователь]", "[Цель: пользователь]"),
        ("физический/магический", "физический и магический"),
        ("с особенностью", "с чертой"),
        (" x ", " × "),
    ):
        value = value.replace(old, new)

    def add_element_label(match: re.Match[str]) -> str:
        attack, icon, label = match.groups()
        if label == "Растения":
            label = "Растение"
        return f"{attack} атаку стихии {icon} {label}"

    return ELEMENT_PATTERN.sub(add_element_label, value)


SPECIAL_SKILL_DESCRIPTIONS = {
    "11018": "[Цель: все враги]\nНаносит умеренный урон и всегда попадает.\nНакладывает {is28}{image(ui_icon_btlStatus_011)} инверсию.",
    "11020": "[Цель: все союзники]\nУмеренно восстанавливает ОЗ.\nНакладывает {is28}{image(ui_icon_btlStatus_040)} иммунитет к аномалиям состояния и\n{is28}{image(ui_icon_btlStatus_041)} иммунитет к ослаблению характеристик.",
    "11021": "[Цель: 1 союзник]\nВосстанавливает ОЗ и ОС до 200% от их максимального значения.",
    "11022": "[Цель: все союзники]\nВыводит союзников из нокаута и немного восстанавливает ОЗ.\nНакладывает {is28}{image(ui_icon_btlStatus_042)} Стойкость: смертельный урон оставляет 1 ОЗ.",
    "20441": "[Цель: 1 враг]\nЛибо наносит физическую атаку стихии {is28}{image(ui_icon_skill_001)} Огонь силой 110,\nлибо со 100%-й вероятностью снижает СКР на 10% на 3 хода.",
    "21782": "[Цель: 1 враг]\nНаносит физическую атаку стихии {is28}{image(ui_icon_skill_000)} Нейтральный силой 80.\nЕсли у цели есть атрибут, наносит повышенный урон.\nПовышенный урон по целям с чертой «Минеральный».",
    "24511": "[Цель: 1 враг] Крадёт все изменения характеристик цели.",
    "27375": "[Цель: 1 враг] Наносит одну из случайных физических атак:\n"
        "- силой 110, стихии {is28}{image(ui_icon_skill_006)} Сталь; повышенный урон по целям с чертой «Минеральный»; игнорирует невыгодную совместимость;\n"
        "- силой 100, стихии {is28}{image(ui_icon_skill_000)} Нейтральный; повышенный урон по целям с чертой «Оружие»; шанс крита 20%;\n"
        "- силой 105, стихии {is28}{image(ui_icon_skill_005)} Электричество; повышенный урон по целям с чертой «Амфибия».",
    "31011": "[Цель: 1 союзник] Умеренно восстанавливает ОЗ.",
    "31012": "[Цель: 1 союзник] Значительно восстанавливает ОЗ.",
    "31021": "[Цель: все союзники] Немного восстанавливает ОЗ.",
    "31022": "[Цель: все союзники] Умеренно восстанавливает ОЗ.",
    "31031": "[Цель: 1 союзник] Выводит цель из нокаута и умеренно восстанавливает ОЗ.",
    "31032": "[Цель: 1 союзник] Выводит цель из нокаута и значительно восстанавливает ОЗ.",
    "31041": "[Цель: 1 союзник] Снимает аномалии состояния.",
    "31051": "[Цель: 1 союзник] Снимает ослабления характеристик.",
    "31061": "[Цель: 1 союзник]\nСнимает аномалии состояния, {is28}{image(ui_icon_btlStatus_012)} травму и\n{is28}{image(ui_icon_btlStatus_013)} болезнь.",
    "80027": "[Цель: 1 союзник] Выводит цель из нокаута и умеренно восстанавливает ОЗ.",
    "80028": "[Цель: 1 союзник] Выводит цель из нокаута и значительно восстанавливает ОЗ.",
    "80029": "[Цель: все союзники] Выводит союзников из нокаута и немного восстанавливает ОЗ.",
    "80030": "[Цель: все союзники] Выводит союзников из нокаута и умеренно восстанавливает ОЗ.",
    "21282": "[Цель: все союзники]\nНа 2 хода со 100%-й вероятностью снижает получаемый физический и\nмагический урон на 20% и повышает сопротивление\n{is28}{image(ui_icon_skill_006)} стали.",
    "27342": "[Цель: пользователь] Со 100%-й вероятностью нейтрализует физический и магический урон.",
    "26991": "[Цель: 1 враг]\nНаносит 20% урона ОЗ.\nПовышает АТК пользователя на 20% на 3 хода.",
    "23121": "[Цель: 1 враг]\nСо 100%-й вероятностью снижает СКР на 30% на 3 хода.\nС вероятностью 60% обездвиживает цель на следующий ход.",
    "21941": "[Цель: все враги]\nНаносит 4 физических атаки стихии {is28}{image(ui_icon_skill_006)} Сталь силой 35.\nЧем ниже ОС пользователя, тем меньше урон. Расходует все ОС.\nПользователь не может действовать в следующий ход.\nПовышенный урон по целям с чертой «Машина».",
    "21832": "[Цель: пользователь]\nНакладывает {is28}{image(ui_icon_btlStatus_048)} провокацию.\nСо 100%-й вероятностью повышает УКЛ на 30% на 1 ход.",
    "21271": "[Цель: все враги]\nСо 100%-й вероятностью снижает АТК и ИНТ на 50% на 1 ход.\nНакладывает на пользователя {is28}{image(ui_icon_btlStatus_048)} провокацию.",
    "80031": "[Цель: 1 союзник] Повышает АТК на 20% на 3 хода.",
    "80032": "[Цель: 1 союзник] Повышает ЗАЩ на 20% на 3 хода.",
    "80033": "[Цель: 1 союзник] Повышает ИНТ на 20% на 3 хода.",
    "80034": "[Цель: 1 союзник] Повышает ДУХ на 20% на 3 хода.",
    "80035": "[Цель: 1 союзник] Повышает СКР на 20% на 3 хода.",
    "80036": "[Цель: 1 союзник] Повышает МЕТ на 20% на 3 хода.",
    "80037": "[Цель: 1 союзник] Повышает УКЛ на 20% на 3 хода.",
    "80038": "[Цель: 1 союзник] Повышает КРТ на 20% на 3 хода.",
    "80039": "[Цель: 1 союзник] Повышает все характеристики на 20% на 3 хода.",
    "27521": "[Цель: 1 враг]\nНаносит 5 ударов, каждый из которых отнимает 1% ОЗ.\nСо 100%-й вероятностью снижает ДУХ на 20% на 3 хода.\nС вероятностью 30% накладывает {is28}{image(ui_icon_btlStatus_002)} смятение.",
    "23131": "[Цель: 1 враг]\nНаносит 5 ударов, каждый из которых отнимает 1% ОЗ.\nСо 100%-й вероятностью снижает ДУХ на 10% на 3 хода.\nС вероятностью 60% накладывает {is28}{image(ui_icon_btlStatus_000)} отравление.",
    "27901": "[Цель: 1 враг]\nНаносит физическую атаку стихии {is28}{image(ui_icon_skill_000)} Нейтральный силой 30.\nСо 100%-й вероятностью снижает случайную характеристику на 60% на 1 ход.",
}


for row_id, baseline in baseline_values(SKILL_DESCRIPTION).items():
    replacement = SPECIAL_SKILL_DESCRIPTIONS.get(row_id, normalize_skill_description(baseline))
    if replacement != normalized(baseline):
        add(SKILL_DESCRIPTION, row_id, replacement)


for row_id, replacement in {
    "13": "[Цель: случайная цель]",
    "25": "× {d0} уд.",
    "26": "× {d0}–{d1} уд.",
    "44": "Выводит из нокаута и восстанавливает {d0}% ОЗ.",
    "48": "Восстанавливает ОЗ сверх максимального значения цели.",
    "56": "Если стихия цели — {d0}:",
    "73": "Шанс наложить {d1}: {d2}.",
    "74": "Шанс срабатывания {d1}: {d2}.",
    "102": "Повышенный урон по целям с чертой {d0}.",
}.items():
    add(AUTO_DESCRIPTION, row_id, replacement)


def main() -> None:
    markers = [(package, relative, row_id, column) for package, relative, row_id, column, _ in UPDATES]
    if len(markers) != len(set(markers)):
        raise SystemExit("Duplicate guarded target in UPDATES")

    documents: dict[str, list[list[str]]] = {}
    baselines: dict[str, list[list[str]]] = {}
    formats: dict[str, tuple[str, str]] = {}
    dirty: set[str] = set()
    changed = current = 0

    for package, relative, row_id, column, replacement in UPDATES:
        if relative not in documents:
            path = CSV_ROOT / package / relative
            rows, encoding, mode = read_document(path)
            documents[relative] = rows
            baselines[relative] = read_baseline(relative)
            formats[relative] = (encoding, mode)

        label = f"{package}:{relative}"
        row = unique_row(documents[relative], row_id, column, label)
        baseline_row = unique_row(baselines[relative], row_id, column, f"{BASELINE_REF}:{label}")
        if normalized(row[column]) == normalized(replacement):
            current += 1
        elif normalized(row[column]) == normalized(baseline_row[column]):
            row[column] = replacement
            changed += 1
            dirty.add(relative)
        else:
            raise SystemExit(
                f"Unexpected text {label}:{row_id}:\n"
                f"baseline={baseline_row[column]!r}\n"
                f"current={row[column]!r}\n"
                f"replacement={replacement!r}"
            )

    for relative in sorted(dirty):
        encoding, mode = formats[relative]
        write_document(CSV_ROOT / "patch_text01" / relative, documents[relative], encoding, mode)

    print(f"Baseline: {BASELINE_REF}")
    print(f"Guarded targets: {len(UPDATES)}")
    print(f"Changed: {changed}")
    print(f"Already current: {current}")
    print(f"Files written: {len(dirty)}")


if __name__ == "__main__":
    main()

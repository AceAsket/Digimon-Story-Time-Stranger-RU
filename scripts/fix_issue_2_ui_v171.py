#!/usr/bin/env python3
"""Apply source-checked UI and terminology fixes reported in issue #2."""

from __future__ import annotations

import csv
import io
import subprocess
from pathlib import Path

from fix_t01_npc_context_v169 import (
    csv_format,
    read_document,
    unique_row,
    write_document,
)


ROOT = Path(__file__).resolve().parents[1]
CSV_ROOT = ROOT / "csv"
BASELINE_REF = "v0.1.50"

# package, relative CSV, row id, text column, replacement
UPDATES: list[tuple[str, str, str, int, str]] = []


def add(
    relative: str,
    row_id: str,
    replacement: str,
    *,
    package: str = "patch_text01",
    column: int | None = None,
) -> None:
    if column is None:
        column = 2 if relative.startswith("message/") else 1
    UPDATES.append((package, relative, row_id, column, replacement))


# Confirmed labels and typos.  The compact wording is intentional for UI cells.
add("text/common_message_dx11.mbe/000_Sheet1.csv", "1901007", "Глубина резкости")
add("text/common_message.mbe/000_Sheet1.csv", "10048", "Ур. изучения")
add("text/common_message.mbe/000_Sheet1.csv", "10028", "Получить навык")
add("text/common_message.mbe/000_Sheet1.csv", "10040", "Исходный дигимон    ур. {n0}")
add("text/common_message.mbe/000_Sheet1.csv", "10041", "Результат эволюции    ур. {n0}")
add("text/common_message.mbe/000_Sheet1.csv", "10400", "Результат деволюции    ур. {n0}")
add("text/common_message.mbe/000_Sheet1.csv", "10068", "Выбранный дигимон")
add("text/common_message.mbe/000_Sheet1.csv", "205", "Костюмы/Аксессуары")
add("text/common_message.mbe/000_Sheet1.csv", "11304", "Запас очков аномалий")
add("text/tutorial_title.mbe/000_Sheet1.csv", "tutorial_title_BondsPoint_01", "Очки аномалий")
add("text/common_message.mbe/000_Sheet1.csv", "120303", "Покупки")
add("text/common_message.mbe/000_Sheet1.csv", "190008", "Личные навыки")
add("text/common_message.mbe/000_Sheet1.csv", "ui_battle_0080", "Точка пробития")

add(
    "text/common_message_dx11.mbe/000_Sheet1.csv",
    "1019011",
    "Меню паузы/Сменить сортировку",
)
add(
    "text/common_message_dx11.mbe/000_Sheet1.csv",
    "1019012",
    "Анализ/Сменить вкладку",
)
add(
    "text/common_message_dx11.mbe/000_Sheet1.csv",
    "1019013",
    "Дигиатака/Кросс-арт/Сменить вкладку",
)
add("text/common_message_dx11.mbe/000_Sheet1.csv", "1019014", "Открыть настройки")
add("text/common_message_dx11.mbe/000_Sheet1.csv", "1019030", "Фоторежим")
add("text/common_message_dx11.mbe/000_Sheet1.csv", "1901201", "Без рамки")


# The three remaining HP/SP labels in patch_text01.  The other two hits found by
# the audit are actually mistranslated CP labels and are handled in the CP block.
add(
    "message/field_text.mbe/000_Sheet1.csv",
    "g_hazama_0010_0030",
    "Выполнение протокола восстановления...\nОЗ/ОС дигимона восстановлены.",
)
add("text/common_message.mbe/000_Sheet1.csv", "11508", "Стоимость ОС")
add("text/skill_auto_explanation.mbe/000_Sheet1.csv", "97", "ОС")


# The English source has exactly 20 CP-related rows.  Seven already use the
# canonical Russian abbreviation "КО"; the 13 inconsistent rows are normalized
# here.  Do not conflate Critical Points with SP (skill points).
add("text/buff_message.mbe/000_Sheet1.csv", "133", "КО больше не накапливаются!")
add("text/buff_message.mbe/000_Sheet1.csv", "100133", "КО больше не накапливаются!")
add("text/common_message.mbe/000_Sheet1.csv", "ui_battle_0060", "КО")
add("text/common_message.mbe/000_Sheet1.csv", "ui_battle_evolution_0060", "КО")
add(
    "text/common_message.mbe/000_Sheet1.csv",
    "icon_info_description_05_15",
    "Ускорение заполнения шкалы КО",
)
add(
    "text/personality_skill_explanation.mbe/000_Sheet1.csv",
    "2",
    "Немного увеличивает количество получаемых КО.",
)
add(
    "text/tamer_skill_explanation.mbe/000_Sheet1.csv",
    "201",
    "Открывает кросс-арт «Поле».\n"
    "Эффект: значительно повышает все характеристики союзников на 2 хода.\n"
    "Активировать кросс-арт можно при полностью заполненной шкале КО.",
)
for row_id in ("203", "209", "219"):
    add(
        "text/tamer_skill_explanation.mbe/000_Sheet1.csv",
        row_id,
        "В начале боя шкала КО заполняется на {d0} за каждый ранг агента.",
    )
add(
    "text/tutorial_explanation.mbe/000_Sheet1.csv",
    "tutorial_exp_BattleCrossarts_01_002",
    "{fc9Когда шкала КО полностью заполнится во время боя,\n"
    "вы перейдёте в режим готовности кросс-арта.\n"
    "Нажмите {r2}, чтобы активировать кросс-арт.}",
)
add(
    "text/tutorial_title.mbe/000_Sheet1.csv",
    "tutorial_title_CpAdd_01",
    "Критические очки (КО)",
)
add(
    "text/tutorial_title.mbe/000_Sheet1.csv",
    "tutorial_title_CpFluctuation_01",
    "Получение и потеря КО",
)


# High-confidence grammar failures adjacent to the terminology audit.
add(
    "text/tutorial_explanation.mbe/000_Sheet1.csv",
    "tutorial_exp_Attribute_01_001",
    "Каждый дигимон имеет сродство со стихиями:\n\n"
    "{is28}{image(ui_icon_skill_001)} Огонь, {is28}{image(ui_icon_skill_002)} Лёд, "
    "{is28}{image(ui_icon_skill_003)} Растение, {is28}{image(ui_icon_skill_004)} Вода, "
    "{is28}{image(ui_icon_skill_005)} Электричество,\n"
    "{is28}{image(ui_icon_skill_006)} Сталь, {is28}{image(ui_icon_skill_007)} Ветер, "
    "{Is28}{image(ui_icon_skill_008)} Земля, {is28}{image(ui_icon_skill_009)} Свет, "
    "{is28}{image(ui_icon_skill_010)} Тьма и\n"
    "{is28}{image(ui_icon_skill_000)} Нейтральный.\n\n"
    "Сродство определяет сопротивление стихии:\n"
    "{fc11◎}:{fc9 урон ×2}\n"
    "{fc11○}:{fc9 урон ×1,5}\n"
    "－: без изменений\n"
    "{fc2△}:{fc9 урон ×0,5}\n"
    "{fc2×}:{fc9 урона нет}",
)
add(
    "text/tutorial_explanation.mbe/000_Sheet1.csv",
    "tutorial_exp_RushOut_01_001",
    "Кажется, вы только что пережили «неожиданную встречу». Ходят\n"
    "слухи, что при такой встрече неожиданно появляется определённый\n"
    "дигимон и вступает в битву.\n\n"
    "{fc9Победите этого дигимона — и получите редкие предметы.\n"
    "Но учтите: он быстро отступает.} Уверен, это лишь вопрос времени,\n"
    "когда какой-нибудь агент раскроет правду.",
)


def read_baseline(package: str, relative: str) -> tuple[list[list[str]], str]:
    object_name = f"{BASELINE_REF}:csv/{package}/{relative}"
    result = subprocess.run(
        ["git", "show", object_name],
        cwd=ROOT,
        capture_output=True,
        check=False,
    )
    if result.returncode:
        detail = result.stderr.decode("utf-8", errors="replace").strip()
        raise SystemExit(f"Cannot read baseline {object_name}: {detail}")
    rows = list(csv.reader(io.StringIO(result.stdout.decode("utf-8-sig"), newline="")))
    return rows, csv_format(result.stdout)


def main() -> None:
    markers = [(p, r, k, c) for p, r, k, c, _ in UPDATES]
    if len(markers) != len(set(markers)):
        raise SystemExit("Duplicate guarded target in UPDATES")

    documents: dict[tuple[str, str], list[list[str]]] = {}
    baselines: dict[tuple[str, str], list[list[str]]] = {}
    formats: dict[tuple[str, str], tuple[str, str]] = {}
    dirty: set[tuple[str, str]] = set()
    changed = current = 0

    for package, relative, row_id, column, replacement in UPDATES:
        marker = (package, relative)
        if marker not in documents:
            path = CSV_ROOT / package / relative
            documents[marker], encoding, _ = read_document(path)
            baselines[marker], mode = read_baseline(package, relative)
            formats[marker] = (encoding, mode)

        label = f"{package}:{relative}"
        row = unique_row(documents[marker], row_id, column, label)
        baseline_row = unique_row(
            baselines[marker], row_id, column, f"{BASELINE_REF}:{label}"
        )
        if row[column] == replacement:
            current += 1
        elif row[column] == baseline_row[column]:
            row[column] = replacement
            changed += 1
            dirty.add(marker)
        else:
            raise SystemExit(
                f"Unexpected text {label}:{row_id}:\n"
                f"baseline={baseline_row[column]!r}\n"
                f"current={row[column]!r}\n"
                f"replacement={replacement!r}"
            )

    for marker in sorted(dirty):
        package, relative = marker
        encoding, mode = formats[marker]
        write_document(CSV_ROOT / package / relative, documents[marker], encoding, mode)

    print(f"Baseline: {BASELINE_REF}")
    print(f"Guarded targets: {len(UPDATES)}")
    print(f"Changed: {changed}")
    print(f"Already current: {current}")
    print(f"Files written: {len(dirty)}")


if __name__ == "__main__":
    main()

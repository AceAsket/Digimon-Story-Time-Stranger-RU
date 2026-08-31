#!/usr/bin/env python3
"""Apply a guarded proofreading pass to controller and keyboard help labels."""

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
BASELINE_REF = "v0.1.51"
RELATIVE = "text/key_help_text.mbe/000_Sheet1.csv"
UPDATES: list[tuple[str, str, str, int, str]] = []


def add(row_id: str, replacement: str) -> None:
    UPDATES.append(("patch_text01", RELATIVE, row_id, 1, replacement))


add("key_help_0004", " Сменить сортировку")
add("key_help_0007", "Переключить информацию")
add("key_help_0013", " Авто")
add("key_help_0017", " Защитить")
add("key_help_0018", " Характеристики")
add("key_help_0022", " (Удерж.) настройки автовыбора")
add("key_help_0024", " Просмотреть навыки")
add("key_help_0028", " Просмотреть модель")
add("key_help_0033", " История диалогов")
add("key_help_0034", " Показать/скрыть")
add("key_help_0036", " Дигиатака")
add("key_help_0037", " Дигирайд")
add("key_help_0039", " Спешиться")
add("key_help_0050", " Переключить навыки")
add("key_help_0054", " Конвертировать")
add("key_help_0055", " Анализировать")
add("key_help_0065", " Перейти к текущей миссии")
add("key_help_0066", " Вернуться в реальный мир")
add("key_help_0071", " Разместить остров")
add("key_help_0072", " Изменить размер")
add("key_help_0074", " Покинуть ферму")
add("key_help_0075", " Изменить радиус")
add("key_help_0076", " Изменить направление")
add("key_help_0079", " Выбрать категорию")
add("key_help_0085", " Выйти")
add("key_help_0088", " Призвать")
add("key_help_0092", " Обучить")
add("key_help_0095", " Подробности миссии")
add("key_help_0099", " Оседлать")
add("key_help_0101", " Выключить авто")
add("key_help_0107", " Согласиться")
add("key_help_0111", " Просмотреть")
add("key_help_0112", " Приостановить")
add("key_help_0115", " Осмотреть/поговорить")
add("key_help_0117", " Обычная модель")
add("key_help_0119", " Снаряжение/навыки")
add("key_help_0121", " Перенести")
add("key_help_0123", " Вернуться в главное меню")
add("key_help_0124", " Купить товар")
add("key_help_0127", " Выбрать ячейку")
add("key_help_0129", " Выбрать остров")
add("key_help_0131", " Сведения о дигимоне")
add("key_help_0132", " Настройки дигимона")
add("key_help_0133", " Просмотреть правила")


def read_baseline() -> tuple[list[list[str]], str]:
    object_name = f"{BASELINE_REF}:csv/patch_text01/{RELATIVE}"
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
    markers = [(package, relative, row_id, column) for package, relative, row_id, column, _ in UPDATES]
    if len(markers) != len(set(markers)):
        raise SystemExit("Duplicate guarded target in UPDATES")

    path = CSV_ROOT / "patch_text01" / RELATIVE
    rows, encoding, _ = read_document(path)
    baseline_rows, mode = read_baseline()
    changed = current = 0

    for package, relative, row_id, column, replacement in UPDATES:
        label = f"{package}:{relative}"
        row = unique_row(rows, row_id, column, label)
        baseline_row = unique_row(
            baseline_rows,
            row_id,
            column,
            f"{BASELINE_REF}:{label}",
        )
        if row[column] == replacement:
            current += 1
        elif row[column] == baseline_row[column]:
            row[column] = replacement
            changed += 1
        else:
            raise SystemExit(
                f"Unexpected text {label}:{row_id}:\n"
                f"baseline={baseline_row[column]!r}\n"
                f"current={row[column]!r}\n"
                f"replacement={replacement!r}"
            )

    if changed:
        write_document(path, rows, encoding, mode)

    print(f"Baseline: {BASELINE_REF}")
    print(f"Guarded targets: {len(UPDATES)}")
    print(f"Changed: {changed}")
    print(f"Already current: {current}")


if __name__ == "__main__":
    main()

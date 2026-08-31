#!/usr/bin/env python3
"""Apply a guarded proofreading pass to Windows and keyboard UI labels."""

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
RELATIVE = "text/common_message_dx11.mbe/000_Sheet1.csv"
UPDATES: list[tuple[str, str, str, int, str]] = []


def add(row_id: str, replacement: str) -> None:
    UPDATES.append(("patch_text01", RELATIVE, row_id, 1, replacement))


# Keyboard and mouse actions.
add("1019007", "Двигаться вперёд/Клавиша ↑")
add("1019008", "Двигаться назад/Клавиша ↓")
add("1019009", "Двигаться влево/Клавиша ←")
add("1019010", "Двигаться вправо/Клавиша →")
add("1019015", "Открыть предметы")
add("1019016", "Открыть Дигилайн")
add("1019017", "Открыть конвертацию")
add("1019018", "Дигирайд/Побег/Сменить вкладку (доп.)")
add("1019021", "Открыть Дигивайс/Переключить информацию/Пропустить ролик")
add("1019022", "Повернуть камеру вверх/Увеличить скорость боя")
add("1019023", "Повернуть камеру вниз/Уменьшить скорость боя")
add("1019024", "Повернуть камеру влево")
add("1019025", "Повернуть камеру вправо")
add("1019026", "Сбросить камеру/Сохранить/Авто")
add("1019027", "Переключить карту/Закрыть Дигивайс")
add("1019028", "Сменить вкладку (доп.)")


# Graphics settings.
add("1901000", "Режим отображения")
add("1901002", "Частота кадров")
add("1901003", "Вертикальная синхронизация")
add("1901009", "Качество текстур")
add("1901010", "Объёмный туман")
add("1901012", "Окклюзия окружения")
add("1901013", "Фильтрация текстур")
add("1901015", "Предустановка качества")
add("1901100", "Вкл.")
add("1901101", "Выкл.")
add("1901102", "Пользовательское")
add("1901103", "Очень высокое")
add("1901104", "Высокое")
add("1901105", "Среднее")
add("1901106", "Низкое")
add("1901107", "Очень низкое")
for row_id, value in {
    "1901108": "Анизотропная (16×)",
    "1901109": "Анизотропная (8×)",
    "1901110": "Анизотропная (4×)",
    "1901111": "Анизотропная (2×)",
    "1901113": "8×",
    "1901114": "4×",
    "1901115": "2×",
    "1901116": "0×",
}.items():
    add(row_id, value)
add("1901200", "Оконный режим")
add("1901202", "Полноэкранный режим")

for row_id, value in {
    "1901300": "1280 × 720 (16:9)",
    "1901301": "1280 × 800 (16:10)",
    "1901302": "1366 × 768 (16:9)",
    "1901303": "1440 × 900 (16:10)",
    "1901304": "1600 × 900 (16:9)",
    "1901305": "1600 × 1000 (16:10)",
    "1901306": "1680 × 1050 (16:10)",
    "1901307": "(Debug) 1720 × 720 (21:9)",
    "1901308": "1920 × 1080 (16:9)",
    "1901309": "1920 × 1200 (16:10)",
    "1901310": "2048 × 1152 (16:9)",
    "1901311": "2560 × 1080 (21:9)",
    "1901312": "2560 × 1440 (16:9)",
    "1901313": "2560 × 1600 (16:10)",
    "1901314": "2880 × 1800 (16:10)",
    "1901315": "3200 × 1800 (16:9)",
    "1901316": "3440 × 1440 (21:9)",
    "1901317": "3840 × 2160 (16:9)",
    "1901318": "3840 × 2400 (16:10)",
    "1901319": "(Отладка) Симуляция Steam Deck",
}.items():
    add(row_id, value)

add("1901400", "Без ограничений")
add("1901501", "Введите имя")


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

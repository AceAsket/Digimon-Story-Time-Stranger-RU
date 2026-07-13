#!/usr/bin/env python3
"""Apply source-checked NPC and tremor terminology fixes in the Shinjuku prologue."""

from __future__ import annotations

import csv
import io
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CSV_ROOT = ROOT / "csv"
BASELINE_REF = "v0.1.48"

# package, relative CSV, row id, text column, replacement
UPDATES: list[tuple[str, str, str, int, str]] = []


def add(row_id: str, replacement: str) -> None:
    UPDATES.append(
        (
            "patch_text01",
            "message/t01.mbe/000_Sheet1.csv",
            row_id,
            2,
            replacement,
        )
    )


# Transport shutdown and the operation around the government building.
add(
    "f_t0101_0030_0010",
    "Похоже, у Стены Надежды идёт протест.\n"
    "И весь транспорт тоже встал... Что происходит?",
)
add(
    "f_t0101_0110_0010",
    "Станция сейчас закрыта. Все линии токийского метро остановлены\n"
    "из-за ожидаемого сильного подземного толчка.",
)
add(
    "f_t0101_0120_0010",
    "Дальше нельзя... Эх! И почему мы должны участвовать\n"
    "в этой так называемой «операции» чужого ведомства?",
)
add(
    "f_t0101_0140_0010",
    "Сейчас главное — добраться до правительственного здания.\n"
    "Именно на него упал тот свет.",
)
add(
    "f_t0101_0160_0010",
    "Вот чёрт! У меня срочное дело! Поезда до сих пор не ходят?!",
)


# Evacuation NPCs: replace literal syntax and disambiguate seismic tremors.
add(
    "f_t0102_0010_0010",
    "Подземные толчки в отдельных районах, резкие перемены погоды,\n"
    "а теперь ещё и странные существа... Что творится в Синдзюку?",
)
add(
    "f_t0102_0060_0010",
    "Да, станция сейчас закрыта. Скоро ожидается\n"
    "сильный подземный толчок. Пожалуйста, будьте осторожны.",
)
add(
    "f_t0102_0090_0010",
    "Дорогу перекрыли из-за недавнего происшествия...\n"
    "Приносим извинения за неудобства.",
)
add(
    "f_t0102_0100_0010",
    "Синдзюку временно изолируют электромагнитной сетью.\n"
    "Всем немедленно эвакуироваться!",
)
add(
    "f_t0102_0130_0010",
    "При такой обстановке работу наверняка отменили.\n"
    "Выходному я, конечно, рад, но...",
)
add(
    "f_t0102_0130_0020",
    "...похоже, мне теперь никак не добраться домой.\n"
    "И что мне делать?",
)
add(
    "f_t0102_0220_0010",
    "Дальше проход закрыт. Пожалуйста, поверните назад.\n"
    "Ожидается сильный подземный толчок. Будьте осторожны.",
)
add("f_t0102_0230_0010", "Сюда нельзя. Поверните назад.")
add(
    "f_t0102_0240_0010",
    "Сюда нельзя... Эта штука вот-вот начнёт двигаться...",
)


# Public reaction and reports around the incident.
add(
    "f_t0103_0050_0060",
    "Подписчики теперь повалят на мой канал! Я обгоню ОккультТокио ТВ\n"
    "с его двумя миллионами подписчиков!",
)
add(
    "f_t0103_0080_0040",
    "И ВСЁ ЖЕ ЭТО СТАЛО ОДНОЙ ИЗ СТУПЕНЕЙ НА ПУТИ\n"
    "К СОСУЩЕСТВОВАНИЮ.",
)
add(
    "f_t0103_0140_0020",
    "Должно быть, всё из-за роликов с дигимонами в сети.\n"
    "Таких роликов полно — видимо, их снимают ради просмотров.",
)
add(
    "f_t0103_0140_0030",
    "Люди привыкли видеть дигимонов и не понимают: им просто повезло,\n"
    "что те пока не нападают.",
)
add(
    "f_t0105_0030_0010",
    "По словам очевидцев, его видели в конце платформы!",
)
add(
    "f_t0105_0060_0040",
    "Только и делают, что проводят совещания,\n"
    "а решить ничего не могут.",
)
add(
    "f_t0105_0060_0050",
    "До дальнейших распоряжений мы патрулируем район.",
)
add(
    "f_t0106_0010_0010",
    "Сегодня мы закрыты: нам не привезли продукты.\n"
    "Похоже, что-то случилось...",
)


# Protest crowd and nearby passers-by.
add(
    "f_t0107_0030_0010",
    "Мы знаем, что это место — источник всех паранормальных явлений!\n"
    "Признайте это наконец и примите меры!",
)
add(
    "f_t0107_0040_0010",
    "Успокойтесь! Это тоже из-за того, что скрывается за Стеной!\n"
    "Нужно действовать, пока всё не стало ещё хуже!",
)
add(
    "f_t0107_0050_0010",
    "Ч-что это сейчас так тряхнуло?! Здесь что-то есть?!\n"
    "Что происходит?!",
)
add(
    "f_t0107_0080_0010",
    "Ты тоже участвуешь в протесте? Тогда не стой в стороне!\n"
    "Иди туда и заставь их тебя услышать!",
)
add(
    "f_t0108_0040_0010",
    "Я хочу сесть на поезд, но всё закрыто. Что полиция имела в виду,\n"
    "когда велела готовиться к сильному подземному толчку?",
)
add(
    "f_t0108_0050_0010",
    "Тот кран время от времени раскачивается сам по себе.\n"
    "Наверняка там что-то происходит, да?",
)
add(
    "f_t0108_0060_0010",
    "Я хочу присоединиться к протесту, но одному идти неловко...\n"
    "Вот бы найти компанию...",
)
add(
    "f_t0108_0110_0010",
    "Это устройство создаёт мощные электромагнитные волны.\n"
    "Они воздействуют на фазовые электроны и обездвиживают дигимонов.",
)
add(
    "f_t0108_0160_0010",
    "Митинг проходит прямо впереди!\n"
    "Пора разоблачить этих мошенников!",
)
add(
    "f_t0108_0170_0020",
    "Почему полиция и служба общественной безопасности всё скрывают?!\n"
    "Люди потому и вышли на протест!",
)
add(
    "f_t0108_0170_0030",
    "Нервничать бесполезно. Охранник предупредил\n"
    "о сильном подземном толчке. Что это вообще значит?",
)
add(
    "f_t0108_0170_0040",
    "Хотя я и сам не знаю, что делать...\n"
    "Как нам теперь добраться домой?",
)
add(
    "f_t0108_0180_0020",
    "Но что толку от отменённых занятий,\n"
    "если всё равно никуда не выбраться?",
)


def csv_format(raw: bytes) -> str:
    physical = raw.removeprefix(b"\xef\xbb\xbf").splitlines()
    if len(physical) > 1 and physical[1].startswith(b'"'):
        return "all"
    return "minimal"


def read_document(path: Path) -> tuple[list[list[str]], str, str]:
    raw = path.read_bytes()
    encoding = "utf-8-sig" if raw.startswith(b"\xef\xbb\xbf") else "utf-8"
    with path.open("r", encoding=encoding, newline="") as handle:
        return list(csv.reader(handle)), encoding, csv_format(raw)


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


def write_document(path: Path, rows: list[list[str]], encoding: str, mode: str) -> None:
    with path.open("w", encoding=encoding, newline="") as handle:
        writer = csv.writer(
            handle,
            lineterminator="\n",
            quoting=csv.QUOTE_ALL if mode == "all" else csv.QUOTE_MINIMAL,
        )
        writer.writerows(rows)


def unique_row(rows: list[list[str]], row_id: str, column: int, label: str) -> list[str]:
    matches = [row for row in rows if row and row[0] == row_id]
    if len(matches) != 1 or len(matches[0]) <= column:
        raise SystemExit(f"Missing or ambiguous target {label}:{row_id}")
    return matches[0]


def main() -> None:
    markers = [(p, r, k, c) for p, r, k, c, _ in UPDATES]
    if len(markers) != len(set(markers)):
        raise SystemExit("Duplicate guarded target in UPDATES")

    documents: dict[tuple[str, str], list[list[str]]] = {}
    formats: dict[tuple[str, str], tuple[str, str]] = {}
    baselines: dict[tuple[str, str], list[list[str]]] = {}
    dirty: set[tuple[str, str]] = set()
    changed = current = 0

    for package, relative, row_id, column, replacement in UPDATES:
        marker = (package, relative)
        if marker not in documents:
            path = CSV_ROOT / package / relative
            documents[marker], encoding, _ = read_document(path)
            baselines[marker], baseline_mode = read_baseline(package, relative)
            formats[marker] = (encoding, baseline_mode)

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

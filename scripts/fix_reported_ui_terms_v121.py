#!/usr/bin/env python3
"""Apply reported UI, terminology, and compact-layout corrections."""

from __future__ import annotations

import csv
import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CSV_ROOT = ROOT / "csv"

# package, relative CSV, row id, text column, expected SHA-256, replacement
UPDATES: list[tuple[str, str, str, int, str, str]] = [
    ("patch_text01", "text/digitter_message.mbe/000_Sheet1.csv", "main_150_010_010", 1,
     "72db13c23eec4ea0e8f36c9c19b02965146eef0f2122535cb513a489952df0a7",
     "Факториальная область... Что-то вроде промышленного\nрайона Цифрового мира?"),
    ("patch_text01", "text/digitter_message.mbe/000_Sheet1.csv", "main_150_010_011", 1,
     "7408db58a7d46e0b28a7ea25c7b5eddf7f72768a888eb138e330b0b434908976",
     "Конфликт местных дигимонов серьёзно обострился.\nНеужели здесь повторяется то, что случится\nвосемь лет спустя?"),
    ("patch_text01", "text/digitter_message.mbe/000_Sheet1.csv", "evolution_possible", 1,
     "41083b86f529706f2d95ec90a88d7859b329df84fa59bf45e94e11c7672807eb",
     "Дигимон {fc9готов к эволюции}. Подробнее:\n{fc15Дигивайс > Дигимон > Эволюция}."),
    ("patch_text01", "text/digitter_message.mbe/000_Sheet1.csv", "kizuna_possible", 1,
     "c15cd1993441a8f3cac4b3c98da47b1ea71b6ecb3052edc31c8fdcf4754bcae2",
     "Открылись новые {fc9Навыки Агента}. Подробнее:\n{fc15Дигивайс > Агент > Навыки Агента}."),
    ("patch_text01", "message/m150.mbe/000_Sheet1.csv", "m150_070_392", 2,
     "cf250ce3708cf644ff955772ca6ef58b5aba147f8be27c398d8cde389c4b93d5",
     "Чтобы попасть на нижний уровень, сначала попроси\nКокувамона в деревне открыть путь."),
    ("patch_text01", "message/m150.mbe/000_Sheet1.csv", "m150_070_393", 2,
     "4ecb6ea86387f826a16ce709d63fc4bd420e393fce221412fd15e75da08e7643",
     "Кокувамон управляет переборками, но перестарался\nи пострадал во время эвакуации."),
    ("patch_text01", "text/item_name.mbe/000_Sheet1.csv", "765", 1,
     "15cac808d2eb1d7b43dc4595e85e3da0f8e4f131d72a6bfc571a6d12ccc08822",
     "Перо Пэрротмона"),
    ("patch_text01", "text/item_ruby.mbe/000_Sheet1.csv", "765", 1,
     "15cac808d2eb1d7b43dc4595e85e3da0f8e4f131d72a6bfc571a6d12ccc08822",
     "Перо Пэрротмона"),
    ("patch_text01", "text/item_name.mbe/000_Sheet1.csv", "1142", 1,
     "1ae163521414af02fca62bad08cc72784f06ac51352e055ffd462f240a54595e",
     "Известный баг"),
    ("patch_text01", "text/item_ruby.mbe/000_Sheet1.csv", "1142", 1,
     "1ae163521414af02fca62bad08cc72784f06ac51352e055ffd462f240a54595e",
     "Известный баг"),
    ("patch_text01", "text/char_name.mbe/000_Sheet1.csv", "char_SELF_PROCLAIMED_STUFFED_TOY", 1,
     "8f32dc06a177f1e4839c8f86788b5bfac4fdf5b982d1fa0c80f415cfc6ace87a",
     "Самозваная плюшевая игрушка"),
    ("patch_text01", "text/item_explanation.mbe/000_Sheet1.csv", "83", 1,
     "0ea5fc4ad6a2efdcf4c20c0470ca5812d55f920a823d7d915c6c13904b1d02d6",
     "Драгоценный камень, добываемый из моллюсков.\nНе путать с чёрным жемчугом, который создаёт Сякомон.\nМожно продать по высокой цене."),
    ("patch_text01", "message/d02.mbe/000_Sheet1.csv", "f_d0201_0230_0010", 2,
     "70c73c58c9e061d5149436732c33438444d6f4dc7ab74b593ae11e2091c4c7d8",
     "Помимо Центральной башни, вы помогли восстановить\nжелезную дорогу Локомона. Вы оказали нам огромную услугу."),
]

# These source terms are uninflected English transliterations.  Counts are
# fixed so a partial prior edit cannot silently produce mixed terminology.
GLOBAL_REPLACEMENTS: list[tuple[str, str, int]] = [
    ("Сентрал-Тауне", "Центральном городе", 6),
    ("Сентрал-Тауна", "Центрального города", 3),
    ("Сентрал-Таун", "Центральный город", 16),
    ("в Сентрал Тауэр", "в Центральной башне", 2),
]


def digest(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def read_document(path: Path) -> tuple[list[list[str]], str, bool]:
    raw = path.read_bytes()
    encoding = "utf-8-sig" if raw.startswith(b"\xef\xbb\xbf") else "utf-8"
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.reader(handle))
    physical = raw.removeprefix(b"\xef\xbb\xbf").splitlines()
    quote_all_after_header = len(physical) > 1 and physical[1].startswith(b'"')
    return rows, encoding, quote_all_after_header


def write_document(
    path: Path,
    rows: list[list[str]],
    encoding: str,
    quote_all_after_header: bool,
) -> None:
    with path.open("w", encoding=encoding, newline="") as handle:
        if quote_all_after_header:
            csv.writer(handle, lineterminator="\n").writerow(rows[0])
            csv.writer(handle, lineterminator="\n", quoting=csv.QUOTE_ALL).writerows(rows[1:])
        else:
            csv.writer(handle, lineterminator="\n").writerows(rows)


def main() -> None:
    documents: dict[tuple[str, str], list[list[str]]] = {}
    formats: dict[tuple[str, str], tuple[str, bool]] = {}
    dirty: set[tuple[str, str]] = set()
    changed = current = 0

    for package, relative, row_id, column, expected_hash, replacement in UPDATES:
        marker = (package, relative)
        path = CSV_ROOT / package / relative
        if marker not in documents:
            rows, encoding, quote_all = read_document(path)
            documents[marker] = rows
            formats[marker] = (encoding, quote_all)
        matches = [row for row in documents[marker] if row and row[0] == row_id]
        if len(matches) != 1 or len(matches[0]) <= column:
            raise SystemExit(f"Missing or ambiguous row {package}:{relative}:{row_id}")
        row = matches[0]
        if row[column] == replacement:
            current += 1
        elif digest(row[column]) == expected_hash:
            row[column] = replacement
            changed += 1
            dirty.add(marker)
        else:
            raise SystemExit(f"Unexpected text {package}:{relative}:{row_id}: {row[column]!r}")

    # Load the remaining documents only after every guarded row target passes.
    for path in sorted(CSV_ROOT.glob("*_text01/**/*.csv")):
        package = path.relative_to(CSV_ROOT).parts[0]
        relative = path.relative_to(CSV_ROOT / package).as_posix()
        marker = (package, relative)
        if marker not in documents:
            rows, encoding, quote_all = read_document(path)
            documents[marker] = rows
            formats[marker] = (encoding, quote_all)

    replacement_counts: dict[str, int] = {}
    for old, new, expected_count in GLOBAL_REPLACEMENTS:
        count = sum(cell.count(old) for rows in documents.values() for row in rows for cell in row)
        replacement_counts[old] = count
        if count == 0:
            continue
        if count != expected_count:
            raise SystemExit(f"Unexpected count for {old!r}: {count}, expected {expected_count}")
        for marker, rows in documents.items():
            touched = False
            for row in rows:
                for index, cell in enumerate(row):
                    if old not in cell:
                        continue
                    row[index] = cell.replace(old, new)
                    touched = True
            if touched:
                dirty.add(marker)

    for marker in sorted(dirty):
        package, relative = marker
        encoding, quote_all = formats[marker]
        write_document(CSV_ROOT / package / relative, documents[marker], encoding, quote_all)

    print(f"Guarded targets: {len(UPDATES)}")
    print(f"Guarded changed: {changed}")
    print(f"Guarded already current: {current}")
    print(f"Global old-term counts: {replacement_counts}")
    print(f"Files written: {len(dirty)}")


if __name__ == "__main__":
    main()

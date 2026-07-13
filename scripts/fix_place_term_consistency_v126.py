#!/usr/bin/env python3
"""Unify source-equivalent place names and their Russian inflections."""

from __future__ import annotations

from pathlib import Path

from fix_reported_sidequests_v120 import read_document, write_document


ROOT = Path(__file__).resolve().parents[1]
CSV_ROOT = ROOT / "csv"

# Ordered longest/specific first.  The count is evaluated after all preceding
# replacements, making overlaps deterministic and the migration fail-closed.
REPLACEMENTS: list[tuple[str, str, int]] = [
    ("на Фабричном Контуре", "в Факториальной области", 4),
    ("до Фабричного Контура", "до Факториальной области", 1),
    ("отправиться на Фабричный Контур", "отправиться в Факториальную область", 1),
    ("захватить Фабричный Контур", "захватить Факториальную область", 1),
    ("к Фабричному\nКонтуру", "в Факториальную\nобласть", 1),
    ("Фабричный Контур", "Факториальная область", 6),
    ("Фабричной зоне", "Факториальной области", 1),
    ("Фабричной Территорией", "Факториальной областью", 1),
    ("Заводской зоны", "Факториальной области", 1),
    ("Заводской район", "Факториальная область", 1),
    ("Фабричного района", "Факториальной области", 1),
    ("Факториальная Зона", "Факториальная область", 1),
    ("Факториальную Зону", "Факториальную область", 1),
    ("Факториальной Зоны", "Факториальной области", 1),
    ("Факториальная зона", "Факториальная область", 1),
    ("Факторная область", "Факториальная область", 1),
    ("Фабричном городке", "Факториальном городе", 2),
    ("Фабричном городе", "Факториальном городе", 1),
    ("Фабричного города", "Факториального города", 1),
    ("Заводской городок", "Факториальный город", 5),
    ("Фабричный городок", "Факториальный город", 2),
    ("Факториальный Город", "Факториальный город", 2),
    ("Фабричный город", "Факториальный город", 4),
    ("Фабричный туннель", "Факториальный туннель", 1),
    ("Факторный туннель", "Факториальный туннель", 1),
    ("Фабричное ядро", "Факториальное ядро", 2),
    ("Факторное Ядро", "Факториальное ядро", 1),
    ("Промежуточного кинотеатра", "Промежуточного театра", 2),
    ("Промежуточном Кинотеатре", "Промежуточном театре", 1),
    ("промежуточном кинотеатре", "промежуточном театре", 1),
    ("Промежуточный кинотеатр", "Промежуточный театр", 1),
    ("промежуточный кинотеатр", "Промежуточный театр", 2),
]


def main() -> None:
    documents: dict[tuple[str, str], list[list[str]]] = {}
    formats: dict[tuple[str, str], tuple[str, bool]] = {}
    for path in sorted(CSV_ROOT.glob("*_text01/**/*.csv")):
        package = path.relative_to(CSV_ROOT).parts[0]
        relative = path.relative_to(CSV_ROOT / package).as_posix()
        documents[(package, relative)], encoding, quote_all = read_document(path)
        formats[(package, relative)] = (encoding, quote_all)

    dirty: set[tuple[str, str]] = set()
    counts: dict[str, int] = {}
    for old, new, expected in REPLACEMENTS:
        count = sum(cell.count(old) for rows in documents.values() for row in rows for cell in row)
        counts[old] = count
        if count == 0:
            continue
        if count != expected:
            raise SystemExit(f"Unexpected count for {old!r}: {count}, expected {expected}")
        for marker, rows in documents.items():
            touched = False
            for row in rows:
                for index, cell in enumerate(row):
                    if old in cell:
                        row[index] = cell.replace(old, new)
                        touched = True
            if touched:
                dirty.add(marker)

    for marker in sorted(dirty):
        package, relative = marker
        encoding, quote_all = formats[marker]
        write_document(CSV_ROOT / package / relative, documents[marker], encoding, quote_all)

    print(f"Replacement rules: {len(REPLACEMENTS)}")
    print(f"Old-term counts: {counts}")
    print(f"Files written: {len(dirty)}")


if __name__ == "__main__":
    main()

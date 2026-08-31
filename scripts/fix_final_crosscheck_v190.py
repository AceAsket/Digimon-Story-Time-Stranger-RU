#!/usr/bin/env python3
"""Apply guarded residual fixes found by the final cross-check."""

from __future__ import annotations

from pathlib import Path

from fix_t01_npc_context_v169 import read_document, unique_row, write_document


ROOT = Path(__file__).resolve().parents[1]
CSV_ROOT = ROOT / "csv" / "patch_text01"
UPDATES: list[tuple[str, str, str, str]] = [
    (
        "message/m050.mbe/000_Sheet1.csv",
        "m050_010_150",
        "фрагменты аудиозаписи с твоей стороны",
        "фрагменты твоей аудиозаписи",
    ),
    (
        "message/m285.mbe/000_Sheet1.csv",
        "m285_030_130",
        "тогда он мог бы осуществить почти всё,\nчто пожелает",
        "тогда ему было бы по силам почти всё,\nчего он пожелает",
    ),
    (
        "message/m410.mbe/000_Sheet1.csv",
        "m410_070_030",
        "Чтобы осуществить это желание",
        "Чтобы исполнить это желание",
    ),
    (
        "message/m090.mbe/000_Sheet1.csv",
        "m090_010_060",
        "и Эгиомон сами являются аномалиями",
        "и Эгиомон сами по себе — аномалии",
    ),
    (
        "message/m310.mbe/000_Sheet1.csv",
        "m310_070_010",
        "Робкий младший брат остался верен данному старшему\nобещанию и превратился в доблестного воина",
        "Робкий младший брат сдержал обещание,\nданное старшему, и стал доблестным воином",
    ),
    (
        "message/d13.mbe/000_Sheet1.csv",
        "f_d1301_0280_0010",
        "Здесь был оставлен документ: \"Данные о Вулканусмоне\".",
        "Здесь лежит документ: «Данные о Вулканусмоне».",
    ),
    (
        "message/d13.mbe/000_Sheet1.csv",
        "f_d1301_0430_0010",
        "На экране появляется документ: \"Исследование моего\nпредшественника о социальных волнениях и аномальных явлениях\".",
        "На экране открыт документ: «Исследование моего\nпредшественника о социальных волнениях и аномальных явлениях».",
    ),
]


def main() -> None:
    documents: dict[str, list[list[str]]] = {}
    formats: dict[str, tuple[str, str]] = {}
    dirty: set[str] = set()
    changed = current = 0

    for relative, row_id, old, new in UPDATES:
        if relative not in documents:
            rows, encoding, mode = read_document(CSV_ROOT / relative)
            documents[relative] = rows
            formats[relative] = (encoding, mode)
        row = unique_row(documents[relative], row_id, 2, relative)
        if new in row[2]:
            current += 1
        elif row[2].count(old) == 1:
            row[2] = row[2].replace(old, new, 1)
            changed += 1
            dirty.add(relative)
        else:
            raise SystemExit(
                f"Unexpected guarded fragment {relative}:{row_id}: "
                f"old_count={row[2].count(old)}, new_count={row[2].count(new)}, "
                f"text={row[2]!r}"
            )

    for relative in sorted(dirty):
        encoding, mode = formats[relative]
        write_document(CSV_ROOT / relative, documents[relative], encoding, mode)

    print(f"Final guarded transforms: {len(UPDATES)}")
    print(f"Changed: {changed}")
    print(f"Already current: {current}")
    print(f"Files written: {len(dirty)}")


if __name__ == "__main__":
    main()

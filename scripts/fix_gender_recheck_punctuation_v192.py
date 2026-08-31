from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

REPLACEMENTS = {
    "message/m180.mbe/000_Sheet1.csv": {
        "m180_050_030": (
            "Хи-хи! Я рада, что тебе нравится!.. О, нужно рассказать\n"
            "всем о Титанах!"
        ),
        "m180_050_060": "Староста деревни!.. В некотором смысле.",
    },
    "message/m190.mbe/000_Sheet1.csv": {
        "m190_060_110": (
            "А теперь отдайте сокровище... Или намерены и дальше\n"
            "сопротивляться?"
        ),
    },
    "message/m280.mbe/000_Sheet1.csv": {
        "m280_030_010": (
            "Будто плывём по воде, словно в лодке. Кто запустил\n"
            "МастерБлимпмона?.. Ранамон?"
        ),
    },
    "message/s050_038.mbe/000_Sheet1.csv": {
        "s050_038_0210": "Скорее, давай их сюда!.. Идеально. Спасибо.",
    },
}


def read_rows(path: Path) -> list[list[str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.reader(handle))
    bad = [(line, len(row)) for line, row in enumerate(rows, 1) if len(row) != 4]
    if bad:
        raise ValueError(f"{path}: expected four columns; bad rows: {bad[:10]}")
    return rows


def write_rows(path: Path, rows: list[list[str]]) -> None:
    raw = path.read_bytes()
    has_bom = raw.startswith(b"\xef\xbb\xbf")
    newline = "\r\n" if b"\r\n" in raw else "\n"
    physical_lines = raw.removeprefix(b"\xef\xbb\xbf").splitlines()
    quote_all = len(physical_lines) > 1 and physical_lines[1].lstrip().startswith(b'"')
    with path.open("w", encoding="utf-8-sig" if has_bom else "utf-8", newline="") as handle:
        writer = csv.writer(
            handle,
            lineterminator=newline,
            quoting=csv.QUOTE_ALL if quote_all else csv.QUOTE_MINIMAL,
        )
        writer.writerows(rows)


def main() -> None:
    changed = 0
    for relative, replacements in REPLACEMENTS.items():
        path = ROOT / "csv" / "patch_text01" / relative
        rows = read_rows(path)
        positions = {row[0]: index for index, row in enumerate(rows[1:], 1)}
        missing = sorted(set(replacements) - positions.keys())
        if missing:
            raise ValueError(f"{path}: missing IDs {missing}")
        for row_id, wanted in replacements.items():
            index = positions[row_id]
            if rows[index][2] != wanted:
                rows[index][2] = wanted
                changed += 1
        write_rows(path, rows)
    print(f"punctuation rows updated: {changed}")


if __name__ == "__main__":
    main()

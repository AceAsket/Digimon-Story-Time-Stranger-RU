#!/usr/bin/env python3
"""Reflow the remaining overlong Digimon Chat rows to two lines."""

from __future__ import annotations

import csv
import textwrap
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CSV_ROOT = ROOT / "csv"
WRAP_WIDTH = 61
OVERFLOW_THRESHOLD = 65


# These three source-checked rows cannot fit in two safe-width lines without
# editing.  Everything else is reflowed without changing a word.
MANUAL: dict[tuple[str, str, str], str] = {
    (
        "patch_text01",
        "message/digimon_chat.mbe/000_Sheet1.csv",
        "hyoga_001_4_reaction_char_HYOUGAMON",
    ): (
        "Вот лентяй! Пробегись немного, разогрейся.\n"
        "Я даже составлю тебе компанию на пару кругов!"
    ),
    (
        "patch_text01",
        "message/digimon_chat.mbe/000_Sheet1.csv",
        "pyoko_001_4_reaction_char_PYOCOMON",
    ): (
        "Как хочешь! Мне не терпится услышать,\n"
        "какое чудесное имя ты придумаешь!"
    ),
    (
        "patch_text01",
        "message/digimon_chat.mbe/000_Sheet1.csv",
        "aonb_001_1_reaction_char_ENBARRMON",
    ): (
        "Любопытно, но страшновато? Решать сейчас не обязательно.\n"
        "Просто приготовься к долгому путешествию!"
    ),
}


def serialization(path: Path) -> tuple[str, str, bool]:
    raw = path.read_bytes()
    bom = raw.startswith(b"\xef\xbb\xbf")
    body = raw.removeprefix(b"\xef\xbb\xbf")
    newline = "\r\n" if b"\r\n" in body else "\n"
    lines = body.splitlines()
    quote_all = len(lines) > 1 and lines[1].lstrip().startswith(b'"')
    return ("utf-8-sig" if bom else "utf-8"), newline, quote_all


def write_rows(path: Path, rows: list[list[str]]) -> None:
    encoding, newline, quote_all = serialization(path)
    with path.open("w", encoding=encoding, newline="") as handle:
        writer = csv.writer(
            handle,
            lineterminator=newline,
            quoting=csv.QUOTE_ALL if quote_all else csv.QUOTE_MINIMAL,
        )
        if quote_all:
            csv.writer(handle, lineterminator=newline).writerow(rows[0])
            writer.writerows(rows[1:])
        else:
            writer.writerows(rows)


def wrapped(text: str) -> str:
    logical = " ".join(text.splitlines())
    lines = textwrap.wrap(
        logical,
        width=WRAP_WIDTH,
        break_long_words=False,
        break_on_hyphens=False,
    )
    if len(lines) > 2 or any(len(line) > WRAP_WIDTH for line in lines):
        raise RuntimeError(f"Cannot fit chat text in two lines: {text!r} -> {lines!r}")
    return "\n".join(lines)


def main() -> None:
    changed = current_manual = reflowed = 0
    found_manual: set[tuple[str, str, str]] = set()
    loaded: list[tuple[Path, list[list[str]], dict[int, str]]] = []

    for path in sorted(CSV_ROOT.glob("*_text01/message/digimon_chat*.mbe/000_Sheet1.csv")):
        package = path.relative_to(CSV_ROOT).parts[0]
        relative = path.relative_to(CSV_ROOT / package).as_posix()
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.reader(handle))
        replacements: dict[int, str] = {}
        for index, row in enumerate(rows[1:], start=1):
            if len(row) <= 2:
                continue
            key = (package, relative, row[0])
            if key in MANUAL:
                found_manual.add(key)
                desired = MANUAL[key]
                if row[2] == desired:
                    current_manual += 1
                    continue
                replacements[index] = desired
                continue
            lines = row[2].splitlines() or [""]
            if max(len(line) for line in lines) <= OVERFLOW_THRESHOLD:
                continue
            desired = wrapped(row[2])
            if desired != row[2]:
                replacements[index] = desired
                reflowed += 1
        loaded.append((path, rows, replacements))

    missing_manual = set(MANUAL) - found_manual
    if missing_manual:
        raise RuntimeError(f"Missing manual chat targets: {sorted(missing_manual)}")

    # Preflight every new value before writing any file.
    for _, _, replacements in loaded:
        for desired in replacements.values():
            lines = desired.splitlines()
            if len(lines) > 2 or any(len(line) > WRAP_WIDTH for line in lines):
                raise RuntimeError(f"Unsafe chat layout: {desired!r}")

    for path, rows, replacements in loaded:
        if not replacements:
            continue
        for index, desired in replacements.items():
            rows[index][2] = desired
            changed += 1
        write_rows(path, rows)

    print(f"Changed rows: {changed}")
    print(f"Automatically reflowed rows: {reflowed}")
    print(f"Manual rows already current: {current_manual}")


if __name__ == "__main__":
    main()

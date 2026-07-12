#!/usr/bin/env python3
"""Apply source-checked wording fixes to the character-creation scene."""

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
BASELINE_REF = "v0.1.49"

# package, relative CSV, row id, text column, replacement
UPDATES: list[tuple[str, str, str, int, str]] = [
    (
        "patch_text01",
        "message/m010.mbe/000_Sheet1.csv",
        "m010_001_011",
        2,
        "Выбери облик, в котором тебе предстоит выполнить свою миссию.",
    )
]


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

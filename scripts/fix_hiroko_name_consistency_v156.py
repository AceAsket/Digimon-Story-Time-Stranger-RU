#!/usr/bin/env python3
"""Keep the indeclinable Japanese given name Hiroko consistent everywhere."""

from __future__ import annotations

import re
from pathlib import Path

from fix_reported_sidequests_v120 import read_document, write_document


ROOT = Path(__file__).resolve().parents[1]
CSV_ROOT = ROOT / "csv"
PATTERN = re.compile(r"\bХирок(?:а|е|ой|у)\b")
EXPECTED_REPLACEMENTS = 29


def main() -> None:
    changed = 0
    dirty_files = 0
    for path in sorted(CSV_ROOT.rglob("*.csv")):
        rows, encoding, quote_all = read_document(path)
        dirty = False
        for row in rows:
            for index, value in enumerate(row):
                replacement, count = PATTERN.subn("Хироко", value)
                if count:
                    row[index] = replacement
                    changed += count
                    dirty = True
        if dirty:
            write_document(path, rows, encoding, quote_all)
            dirty_files += 1

    if changed not in {0, EXPECTED_REPLACEMENTS}:
        raise SystemExit(
            f"Unexpected Hiroko replacement count: {changed}; "
            f"expected 0 or {EXPECTED_REPLACEMENTS}"
        )
    print(f"Replacements: {changed}")
    print(f"Files written: {dirty_files}")


if __name__ == "__main__":
    main()

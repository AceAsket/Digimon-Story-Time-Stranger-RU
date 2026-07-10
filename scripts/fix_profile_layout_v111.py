#!/usr/bin/env python3
"""Reflow only Digimon profiles that contain unsafe physical line lengths."""

from __future__ import annotations

import csv
import re
import textwrap
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CSV_ROOT = ROOT / "csv"
MANIFEST = ROOT / "exports/profile_layout_reflow_v111.csv"
OVERFLOW_THRESHOLD = 65
WRAP_WIDTH = 55
PROFILE_GLOB = "*_text01/text/digimon_profile*.mbe/000_Sheet1.csv"
FIELDS = [
    "package", "file", "row_id", "max_before", "max_after",
    "lines_before", "lines_after",
]


def reflow(text: str) -> str:
    paragraphs = re.split(r"\n\s*\n", text.strip())
    wrapped = []
    for paragraph in paragraphs:
        logical = " ".join(paragraph.split())
        wrapped.append(
            textwrap.fill(
                logical,
                width=WRAP_WIDTH,
                break_long_words=False,
                break_on_hyphens=False,
            )
        )
    return "\n\n".join(wrapped)


def max_line(text: str) -> int:
    return max((len(line) for line in text.splitlines()), default=0)


def main() -> None:
    pending: list[tuple[Path, list[list[str]], list[dict[str, str]]]] = []
    manifest: list[dict[str, str]] = []
    for path in sorted(CSV_ROOT.glob(PROFILE_GLOB)):
        package = path.relative_to(CSV_ROOT).parts[0]
        relative = path.relative_to(CSV_ROOT / package).as_posix()
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.reader(handle))
        changes: list[dict[str, str]] = []
        for row in rows[1:]:
            if len(row) < 2 or max_line(row[1]) <= OVERFLOW_THRESHOLD:
                continue
            before = row[1]
            after = reflow(before)
            if max_line(after) > WRAP_WIDTH:
                raise SystemExit(f"Unsafe profile reflow: {package}:{relative}:{row[0]}")
            row[1] = after
            change = {
                "package": package,
                "file": relative,
                "row_id": row[0],
                "max_before": str(max_line(before)),
                "max_after": str(max_line(after)),
                "lines_before": str(len(before.splitlines())),
                "lines_after": str(len(after.splitlines())),
            }
            changes.append(change)
            manifest.append(change)
        pending.append((path, rows, changes))

    if not MANIFEST.exists() and len(manifest) != 157:
        raise SystemExit(f"Profile layout baseline changed: expected 157 rows, got {len(manifest)}")

    for path, rows, changes in pending:
        if not changes:
            continue
        with path.open("w", encoding="utf-8-sig", newline="") as handle:
            csv.writer(handle, lineterminator="\n").writerows(rows)

    if manifest:
        with MANIFEST.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=FIELDS, lineterminator="\n")
            writer.writeheader()
            writer.writerows(manifest)

    print(f"Reflowed profiles: {len(manifest)}")
    print(f"Overflow threshold: {OVERFLOW_THRESHOLD}")
    print(f"Wrap width: {WRAP_WIDTH}")
    print(f"Manifest: {MANIFEST.relative_to(ROOT)}")


if __name__ == "__main__":
    main()

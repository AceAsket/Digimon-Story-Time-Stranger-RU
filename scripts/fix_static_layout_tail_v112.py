#!/usr/bin/env python3
"""Insert safe manual line breaks in the reviewed static-layout tail."""

from __future__ import annotations

import csv
import textwrap
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CSV_ROOT = ROOT / "csv"
AUDIT = ROOT / "exports/static_layout_audit_v110.csv"
MANIFEST = ROOT / "exports/static_layout_reflow_v112.csv"
WIDTHS = {"explanation": 100, "system_text": 85}
FIELDS = [
    "category", "package", "file", "row_id", "column",
    "max_before", "max_after", "lines_before", "lines_after",
]


def reflow(text: str, width: int) -> str:
    output = []
    for line in text.splitlines() or [""]:
        output.extend(
            textwrap.wrap(
                line,
                width=width,
                break_long_words=False,
                break_on_hyphens=False,
            ) or [""]
        )
    return "\n".join(output)


def max_line(text: str) -> int:
    return max((len(line) for line in text.splitlines()), default=0)


def main() -> None:
    with AUDIT.open("r", encoding="utf-8-sig", newline="") as handle:
        candidates = list(csv.DictReader(handle))
    if set(row["category"] for row in candidates) - set(WIDTHS):
        raise SystemExit("Static layout audit contains an unreviewed UI category.")
    if not MANIFEST.exists() and len(candidates) != 20:
        raise SystemExit(f"Static layout baseline changed: expected 20 rows, got {len(candidates)}")

    grouped: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in candidates:
        grouped[(row["package"], row["file"])].append(row)

    manifest: list[dict[str, str]] = []
    changed = 0
    already_current = 0
    for (package, relative), updates in sorted(grouped.items()):
        path = CSV_ROOT / package / relative
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.reader(handle))
        by_id = {row[0]: row for row in rows if row}
        file_changed = False
        for update in updates:
            row = by_id.get(update["row_id"])
            if row is None:
                raise SystemExit(f"Missing layout row: {package}:{relative}:{update['row_id']}")
            column = 2 if "message" in path.parts else 1
            if len(row) <= column:
                raise SystemExit(f"Malformed layout row: {package}:{relative}:{update['row_id']}")
            before = row[column]
            after = reflow(before, WIDTHS[update["category"]])
            if max_line(after) > WIDTHS[update["category"]]:
                raise SystemExit(f"Unsafe reflow: {package}:{relative}:{update['row_id']}")
            if before == after:
                already_current += 1
                continue
            row[column] = after
            changed += 1
            file_changed = True
            manifest.append(
                {
                    "category": update["category"],
                    "package": package,
                    "file": relative,
                    "row_id": update["row_id"],
                    "column": str(column),
                    "max_before": str(max_line(before)),
                    "max_after": str(max_line(after)),
                    "lines_before": str(len(before.splitlines())),
                    "lines_after": str(len(after.splitlines())),
                }
            )
        if file_changed:
            with path.open("w", encoding="utf-8-sig", newline="") as handle:
                csv.writer(handle, lineterminator="\n").writerows(rows)

    if manifest:
        with MANIFEST.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=FIELDS, lineterminator="\n")
            writer.writeheader()
            writer.writerows(manifest)

    print(f"Static layout rows changed: {changed}")
    print(f"Already current: {already_current}")
    print(f"Manifest: {MANIFEST.relative_to(ROOT)}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Apply the second reviewed high/medium profile move-name batch."""

from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CSV_ROOT = ROOT / "csv"
SUGGESTIONS = ROOT / "exports/profile_move_replacement_suggestions_v097.csv"
MANIFEST = ROOT / "exports/profile_move_replacements_tail_v101.csv"
FIELDS = [
    "package", "file", "row_id", "source_move", "approved_ru",
    "current_fragment", "replacement", "basis", "score", "margin",
]


def build_manifest() -> list[dict[str, str]]:
    with SUGGESTIONS.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = [row for row in csv.DictReader(handle) if row["confidence"] in {"high", "medium"}]
    manifest = [{field: row[field] for field in FIELDS} for row in rows]
    with MANIFEST.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(manifest)
    return manifest


def read_manifest() -> list[dict[str, str]]:
    if not MANIFEST.exists():
        return build_manifest()
    with MANIFEST.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def main() -> None:
    manifest = read_manifest()
    if not manifest:
        raise SystemExit("Reviewed profile move-name tail manifest is empty.")

    grouped: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in manifest:
        grouped[(row["package"], row["file"])].append(row)

    changed = 0
    current = 0
    for (package, relative), updates in sorted(grouped.items()):
        path = CSV_ROOT / package / relative
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.reader(handle))
        row_by_id = {row[0]: row for row in rows if row}
        file_changed = False
        by_row: dict[str, list[dict[str, str]]] = defaultdict(list)
        for update in updates:
            by_row[update["row_id"]].append(update)

        for row_id, row_updates in by_row.items():
            row = row_by_id.get(row_id)
            if row is None or len(row) < 2:
                raise SystemExit(f"Missing or malformed row {package}:{relative}:{row_id}")
            text = row[1]
            for update in sorted(row_updates, key=lambda item: len(item["current_fragment"]), reverse=True):
                if update["basis"] != "quoted_name_similarity":
                    raise SystemExit(f"Unexpected replacement basis: {update['basis']}")
                old = "«" + update["current_fragment"] + "»"
                new = "«" + update["replacement"] + "»"
                count = text.count(old)
                if count == 1:
                    text = text.replace(old, new, 1)
                    changed += 1
                    file_changed = True
                elif count == 0 and new in text:
                    current += 1
                else:
                    raise SystemExit(
                        f"Ambiguous replacement {package}:{relative}:{row_id}: {old!r} count={count}"
                    )
            row[1] = text

        if file_changed:
            with path.open("w", encoding="utf-8-sig", newline="") as handle:
                csv.writer(handle, lineterminator="\n").writerows(rows)

    print(f"Manifest replacements: {len(manifest)}")
    print(f"Changed: {changed}")
    print(f"Already current: {current}")


if __name__ == "__main__":
    main()

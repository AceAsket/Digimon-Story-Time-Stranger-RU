#!/usr/bin/env python3
"""Audit all editable game CSVs for damaged Unicode and mojibake."""

from __future__ import annotations

import csv
import re
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CSV_ROOT = ROOT / "csv"
OUT_CSV = ROOT / "exports/text_encoding_audit_v088.csv"
OUT_SUMMARY = ROOT / "exports/text_encoding_audit_v088_summary.txt"

QUESTION_RUN_RE = re.compile(r"\?{2,}")


def ignored_placeholder(row: list[str]) -> bool:
    row_id = row[0] if row else ""
    joined = "\n".join(row)
    return (
        row_id.startswith("dummy_")
        or "char_???" in joined
        or any(value == "???" for value in row)
        or "Идентификатор события" in joined
        or "Идентификатор мероприятия" in joined
    )


def looks_like_mojibake(value: str) -> bool:
    """Return true only when a reverse mis-decoding produces better Unicode."""

    original_cyrillic = sum("\u0400" <= char <= "\u04ff" for char in value)
    for encoding in ("cp1251", "latin-1"):
        try:
            repaired = value.encode(encoding).decode("utf-8")
        except (UnicodeEncodeError, UnicodeDecodeError):
            continue
        repaired_cyrillic = sum("\u0400" <= char <= "\u04ff" for char in repaired)
        if repaired != value and repaired_cyrillic > original_cyrillic:
            return True
    return False


def main() -> None:
    issues: list[dict[str, str]] = []
    files = sorted(CSV_ROOT.rglob("*.csv"))
    rows_scanned = 0
    ignored_question_placeholders = 0
    canonical_mechanorimon = 0
    old_mechanorimon = 0

    for path in files:
        relative = path.relative_to(ROOT).as_posix()
        try:
            raw = path.read_bytes()
            text = raw.decode("utf-8-sig", errors="strict")
        except UnicodeDecodeError as error:
            issues.append(
                {
                    "issue": "invalid_utf8",
                    "file": relative,
                    "row": "",
                    "field": "",
                    "context": str(error),
                }
            )
            continue

        try:
            rows = list(csv.reader(text.splitlines(keepends=True)))
        except csv.Error as error:
            issues.append(
                {
                    "issue": "invalid_csv",
                    "file": relative,
                    "row": "",
                    "field": "",
                    "context": str(error),
                }
            )
            continue

        for row_number, row in enumerate(rows, 1):
            rows_scanned += 1
            for field_number, value in enumerate(row, 1):
                canonical_mechanorimon += value.count("Механоримон")
                old_mechanorimon += value.count("Меканоримон")
                checks = (
                    ("replacement_character", "�" in value),
                    ("embedded_bom", "\ufeff" in value),
                    (
                        "control_character",
                        any(ord(char) < 32 and char not in "\t\r\n" for char in value),
                    ),
                    (
                        "mojibake",
                        looks_like_mojibake(value),
                    ),
                    ("mechanorimon_name_variant", "Меканоримон" in value),
                )
                for issue, found in checks:
                    if found:
                        issues.append(
                            {
                                "issue": issue,
                                "file": relative,
                                "row": str(row_number),
                                "field": str(field_number),
                                "context": value.replace("\n", " / ")[:240],
                            }
                        )
                if QUESTION_RUN_RE.search(value):
                    if ignored_placeholder(row):
                        ignored_question_placeholders += 1
                    else:
                        issues.append(
                            {
                                "issue": "question_mark_run_review",
                                "file": relative,
                                "row": str(row_number),
                                "field": str(field_number),
                                "context": value.replace("\n", " / ")[:240],
                            }
                        )

    fieldnames = ["issue", "file", "row", "field", "context"]
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(issues)

    counts = Counter(row["issue"] for row in issues)
    summary = [
        f"CSV files scanned: {len(files)}",
        f"CSV rows scanned: {rows_scanned}",
        f"Encoding/name issues: {len(issues)}",
        f"Known non-display question placeholders ignored: {ignored_question_placeholders}",
        f"Canonical Механоримон occurrences: {canonical_mechanorimon}",
        f"Old Меканоримон occurrences: {old_mechanorimon}",
    ]
    for issue, count in sorted(counts.items()):
        summary.append(f"{issue}: {count}")
    summary.append(f"Report: {OUT_CSV.relative_to(ROOT)}")
    OUT_SUMMARY.write_text("\n".join(summary) + "\n", encoding="utf-8-sig")
    print("\n".join(summary))


if __name__ == "__main__":
    main()

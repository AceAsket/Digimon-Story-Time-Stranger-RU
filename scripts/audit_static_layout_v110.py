#!/usr/bin/env python3
"""Audit physical line lengths using UI-specific thresholds."""

from __future__ import annotations

import csv
import re
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CSV_ROOT = ROOT / "csv"
OUT = ROOT / "exports/static_layout_audit_v110.csv"
SUMMARY = ROOT / "exports/static_layout_audit_v110_summary.txt"

RULES = {
    "digimon_chat": (65, 2),
    "digitter": (65, None),
    "profile": (65, None),
    "dialogue": (75, None),
    "tutorial": (75, None),
    "explanation": (120, None),
    "system_text": (95, None),
}

TAG_PATTERNS = [
    re.compile(r"\{image\([^)]*\)\}"),
    re.compile(r"\{[^{}]*\}"),
    re.compile(r"\{[A-Za-z]+\d*"),
]


def category(path: Path) -> str | None:
    value = path.as_posix().lower()
    if "/message/digimon_chat" in value:
        return "digimon_chat"
    if "/text/digitter_message" in value:
        return "digitter"
    if "/message/" in value:
        return "dialogue"
    if "digimon_profile" in value:
        return "profile"
    if "tutorial" in value:
        return "tutorial"
    if any(
        name in value
        for name in (
            "skill_explanation", "item_explanation", "buff_explanation",
            "tamer_skill_explanation", "personality_explanation",
        )
    ):
        return "explanation"
    if "/text/" in value:
        return "system_text"
    return None


def visible_text(text: str) -> str:
    result = text
    for pattern in TAG_PATTERNS:
        result = pattern.sub("", result)
    return result.replace("}", "")


def main() -> None:
    findings: list[dict[str, str]] = []
    scanned_rows = Counter()
    technical_dummy = 0
    for path in sorted(CSV_ROOT.glob("*_text01/**/*.csv")):
        group = category(path)
        if group is None:
            continue
        package = path.relative_to(CSV_ROOT).parts[0]
        relative = path.relative_to(CSV_ROOT / package).as_posix()
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.reader(handle))
        column = 2 if "message" in path.parts else 1
        max_width, max_lines = RULES[group]
        for row in rows[1:]:
            if len(row) <= column:
                continue
            scanned_rows[group] += 1
            if group == "dialogue" and row[0].startswith("dummy_"):
                technical_dummy += 1
                continue
            lines = row[column].splitlines() or [""]
            visible_lengths = [len(visible_text(line)) for line in lines]
            overlong = max(visible_lengths, default=0) > max_width
            too_many = max_lines is not None and len(lines) > max_lines
            if not overlong and not too_many:
                continue
            findings.append(
                {
                    "priority": "P2" if max(visible_lengths, default=0) > max_width + 10 else "P3",
                    "category": group,
                    "package": package,
                    "file": relative,
                    "row_id": row[0],
                    "max_visible_line": str(max(visible_lengths, default=0)),
                    "line_limit": str(max_width),
                    "line_count": str(len(lines)),
                    "max_lines": "" if max_lines is None else str(max_lines),
                    "text": row[column],
                }
            )

    findings.sort(
        key=lambda row: (
            row["priority"], row["category"], -int(row["max_visible_line"]),
            row["package"], row["file"], row["row_id"],
        )
    )
    fields = [
        "priority", "category", "package", "file", "row_id",
        "max_visible_line", "line_limit", "line_count", "max_lines", "text",
    ]
    with OUT.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(findings)

    counts = Counter(row["category"] for row in findings)
    summary = ["Static layout audit v110"]
    summary.extend(f"scanned_{name}={scanned_rows[name]}" for name in RULES)
    summary.append(f"technical_dummy_rows_excluded={technical_dummy}")
    summary.append(f"candidates={len(findings)}")
    summary.extend(f"{name}_candidates={counts[name]}" for name in RULES)
    summary.append(f"report={OUT.relative_to(ROOT)}")
    SUMMARY.write_text("\n".join(summary) + "\n", encoding="utf-8")
    print("\n".join(summary))


if __name__ == "__main__":
    main()

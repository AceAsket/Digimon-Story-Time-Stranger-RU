#!/usr/bin/env python3
"""Find Russian dialogue lines at risk in the narrow portrait/log layout."""

from __future__ import annotations

import csv
import re
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CSV_ROOT = ROOT / "csv"
SOURCE_ROOT = ROOT / "verify" / "game_build_23514637" / "text_original"
OUT = ROOT / "exports" / "compact_dialogue_layout_audit_v125.csv"
SUMMARY = ROOT / "exports" / "compact_dialogue_layout_audit_v125_summary.txt"
LIMIT = 65
TAG_RE = re.compile(r"\{[^}]*\}|\[[^]]*\]")


def read_rows(path: Path) -> dict[str, list[str]]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return {row[0]: row for row in csv.reader(handle) if row}


def visible_length(line: str) -> int:
    return len(TAG_RE.sub("", line))


def source_text(package: str, relative: Path, key: str) -> str:
    candidates = []
    if package == "patch_text01":
        candidates.append(SOURCE_ROOT / "patch_text01" / "csv" / relative)
        candidates.append(SOURCE_ROOT / "app_text01" / "csv" / relative)
    else:
        candidates.append(SOURCE_ROOT / package / "csv" / relative)
    for path in candidates:
        row = read_rows(path).get(key)
        if row and len(row) > 2 and row[2].strip():
            return row[2]
    return ""


def main() -> None:
    findings: list[dict[str, str | int]] = []
    cache: dict[Path, dict[str, list[str]]] = {}
    scanned = 0
    for path in sorted(CSV_ROOT.glob("*_text01/message/**/*.csv")):
        package = path.relative_to(CSV_ROOT).parts[0]
        relative = path.relative_to(CSV_ROOT / package)
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.reader(handle))
        useful = [row for row in rows[1:] if len(row) > 2 and not row[0].startswith("dummy_")]
        for index, row in enumerate(useful):
            scanned += 1
            current_lines = row[2].splitlines() or [""]
            current_max = max(visible_length(line) for line in current_lines)
            if current_max <= LIMIT:
                continue
            source = ""
            source_candidates = []
            if package == "patch_text01":
                source_candidates.extend(
                    [
                        SOURCE_ROOT / "patch_text01" / "csv" / relative,
                        SOURCE_ROOT / "app_text01" / "csv" / relative,
                    ]
                )
            else:
                source_candidates.append(SOURCE_ROOT / package / "csv" / relative)
            for source_path in source_candidates:
                if source_path not in cache:
                    cache[source_path] = read_rows(source_path)
                source_row = cache[source_path].get(row[0])
                if source_row and len(source_row) > 2 and source_row[2].strip():
                    source = source_row[2]
                    break
            if not source:
                continue
            source_lines = source.splitlines() or [""]
            source_max = max(visible_length(line) for line in source_lines)
            divergence = current_max - source_max
            if divergence < 8:
                continue
            visible_total = sum(visible_length(line) for line in current_lines) + max(0, len(current_lines) - 1)
            if current_max >= 72 or divergence >= 20:
                priority = "P1"
            elif current_max >= 68 or divergence >= 14:
                priority = "P2"
            else:
                priority = "P3"
            findings.append(
                {
                    "priority": priority,
                    "max_ru_line": current_max,
                    "max_en_line": source_max,
                    "divergence": divergence,
                    "ru_lines": len(current_lines),
                    "en_lines": len(source_lines),
                    "fits_two_65": "yes" if visible_total <= LIMIT * 2 else "no",
                    "package": package,
                    "file": relative.as_posix(),
                    "key": row[0],
                    "speaker": row[1],
                    "source_en": source,
                    "current_ru": row[2],
                    "previous_ru": useful[index - 1][2] if index else "",
                    "next_ru": useful[index + 1][2] if index + 1 < len(useful) else "",
                }
            )
    findings.sort(
        key=lambda row: (
            {"P1": 0, "P2": 1, "P3": 2}[str(row["priority"])],
            -int(row["max_ru_line"]),
            -int(row["divergence"]),
            str(row["package"]),
            str(row["file"]),
            str(row["key"]),
        )
    )
    fields = [
        "priority", "max_ru_line", "max_en_line", "divergence", "ru_lines", "en_lines",
        "fits_two_65", "package", "file", "key", "speaker", "source_en", "current_ru",
        "previous_ru", "next_ru",
    ]
    with OUT.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(findings)
    counts = Counter(str(row["priority"]) for row in findings)
    summary = [
        "Compact dialogue layout audit v125",
        f"rows_scanned={scanned}",
        f"line_limit={LIMIT}",
        f"source_divergence_min=8",
        f"candidates={len(findings)}",
        f"P1={counts['P1']}",
        f"P2={counts['P2']}",
        f"P3={counts['P3']}",
        f"report={OUT.relative_to(ROOT)}",
    ]
    SUMMARY.write_text("\n".join(summary) + "\n", encoding="utf-8")
    print("\n".join(summary))


if __name__ == "__main__":
    main()

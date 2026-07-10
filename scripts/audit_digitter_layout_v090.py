#!/usr/bin/env python3
"""Find overlong Digitter log lines and attach their English source text."""

from __future__ import annotations

import csv
import re
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CSV_ROOT = ROOT / "csv"
ORIGINAL_ROOT = ROOT / "verify/game_build_23514637/text_original"
OUT = ROOT / "exports/digitter_layout_audit_v090.csv"
SUMMARY = ROOT / "exports/digitter_layout_audit_v090_summary.txt"
RELATIVE = Path("text/digitter_message.mbe/000_Sheet1.csv")
MAX_VISIBLE_LINE = 65
TAG_RE = re.compile(r"\{[^}]+\}")


def read_rows(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return {row[0]: row[1] for row in csv.reader(handle) if len(row) >= 2}


def visible_length(line: str) -> int:
    return len(TAG_RE.sub("", line))


def main() -> None:
    findings: list[dict[str, str | int]] = []
    scanned = 0
    packages = 0

    for package_root in sorted(path for path in CSV_ROOT.iterdir() if path.is_dir()):
        current_path = package_root / RELATIVE
        if not current_path.exists():
            continue
        packages += 1
        current = read_rows(current_path)
        source = read_rows(ORIGINAL_ROOT / package_root.name / "csv" / RELATIVE)
        for key, text in current.items():
            if key.startswith("string"):
                continue
            scanned += 1
            lengths = [visible_length(line) for line in text.splitlines()] or [0]
            longest = max(lengths)
            if longest <= MAX_VISIBLE_LINE:
                continue
            source_text = source.get(key, "")
            source_lengths = [visible_length(line) for line in source_text.splitlines()] or [0]
            findings.append(
                {
                    "priority": "P4" if longest >= 75 else "P3",
                    "package": package_root.name,
                    "file": RELATIVE.as_posix(),
                    "key": key,
                    "max_visible_line": longest,
                    "line_count": len(text.splitlines()) or 1,
                    "source_max_line": max(source_lengths),
                    "source_line_count": len(source_text.splitlines()) or 1,
                    "source_en": source_text,
                    "current_ru": text,
                }
            )

    findings.sort(key=lambda row: (-int(row["max_visible_line"]), str(row["package"]), str(row["key"])))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "priority",
        "package",
        "file",
        "key",
        "max_visible_line",
        "line_count",
        "source_max_line",
        "source_line_count",
        "source_en",
        "current_ru",
    ]
    with OUT.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(findings)

    priorities = Counter(str(row["priority"]) for row in findings)
    summary = [
        "Digitter layout audit v090",
        f"packages_scanned={packages}",
        f"rows_scanned={scanned}",
        f"max_visible_line={MAX_VISIBLE_LINE}",
        f"candidates={len(findings)}",
        f"P4={priorities['P4']}",
        f"P3={priorities['P3']}",
        f"report={OUT.relative_to(ROOT)}",
    ]
    SUMMARY.write_text("\n".join(summary) + "\n", encoding="utf-8")
    print("\n".join(summary))


if __name__ == "__main__":
    main()

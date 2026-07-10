#!/usr/bin/env python3
"""Find high-confidence corruption and broken Russian prose in Digimon profiles."""

from __future__ import annotations

import csv
import re
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CSV_ROOT = ROOT / "csv"
SOURCE_ROOT = ROOT / "verify/game_build_23514637/text_original"
OUT = ROOT / "exports/profile_prose_audit_v104.csv"
SUMMARY = ROOT / "exports/profile_prose_audit_v104_summary.txt"
PROFILE_FILE_RE = re.compile(
    r"(?:^|/)digimon_profile(?:_dlc\d+)?\.mbe/000_Sheet1\.csv$", re.I
)
SPACE_RE = re.compile(r"\s+")

ISSUE_PATTERNS = [
    ("broken_question_inside_word", re.compile(r"[А-Яа-яЁё]\?[А-Яа-яЁё]")),
    ("agreement_own_special_move", re.compile(r"\bсво(?:е|ё)\s+особый\s+приём\b", re.I)),
    ("agreement_primitive", re.compile(r"\bсамым\s+примитивный\b", re.I)),
    ("broken_best_known_weapons", re.compile(r"\bбольшинства\s+известнейшего\s+оружия\b", re.I)),
    ("broken_whenever_possible", re.compile(r"\bкогда\s+бы\s+ни\s+возможно\b", re.I)),
    ("literal_at_which_point", re.compile(r"\bв\s+какой\s+момент\b", re.I)),
    ("broken_fans_alike", re.compile(r"\bфанатиков\s+дигимонов\s+одинаково\b", re.I)),
    ("broken_excels_boasts", re.compile(r"\bпреуспевает\s+в\s+может\s+похвастаться\b", re.I)),
]


def read_rows(path: Path) -> dict[str, str]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return {row[0]: row[1] for row in csv.reader(handle) if len(row) >= 2}


def flatten(text: str) -> str:
    return SPACE_RE.sub(" ", text).strip()


def snippet(text: str, start: int, end: int, radius: int = 100) -> str:
    left = max(0, start - radius)
    right = min(len(text), end + radius)
    return ("…" if left else "") + text[left:right] + ("…" if right < len(text) else "")


def main() -> None:
    findings: list[dict[str, str]] = []
    profile_rows = 0
    profile_files = 0

    for package_root in sorted(path for path in CSV_ROOT.iterdir() if path.is_dir()):
        text_root = package_root / "text"
        if not text_root.exists():
            continue
        for path in sorted(text_root.rglob("000_Sheet1.csv")):
            relative = path.relative_to(package_root).as_posix()
            if not PROFILE_FILE_RE.search(relative):
                continue
            source_path = SOURCE_ROOT / package_root.name / "csv" / relative
            if not source_path.exists():
                continue
            profile_files += 1
            current_rows = read_rows(path)
            source_rows = read_rows(source_path)
            for row_id, current_text in current_rows.items():
                profile_rows += 1
                current_flat = flatten(current_text)
                source_flat = flatten(source_rows.get(row_id, ""))
                for issue, pattern in ISSUE_PATTERNS:
                    for match in pattern.finditer(current_flat):
                        findings.append(
                            {
                                "priority": "P1" if issue == "broken_question_inside_word" else "P2",
                                "issue": issue,
                                "package": package_root.name,
                                "file": relative,
                                "row_id": row_id,
                                "matched_text": match.group(0),
                                "current_snippet": snippet(current_flat, match.start(), match.end()),
                                "source_en": source_flat,
                            }
                        )

    findings.sort(key=lambda row: (row["priority"], row["issue"], row["package"], row["row_id"]))
    fields = [
        "priority", "issue", "package", "file", "row_id",
        "matched_text", "current_snippet", "source_en",
    ]
    with OUT.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(findings)

    counts = Counter(row["issue"] for row in findings)
    summary = [
        "Profile prose audit v104",
        f"profile_files={profile_files}",
        f"profile_rows={profile_rows}",
        f"candidates={len(findings)}",
    ]
    summary.extend(f"{issue}={counts[issue]}" for issue, _ in ISSUE_PATTERNS)
    summary.append(f"report={OUT.relative_to(ROOT)}")
    SUMMARY.write_text("\n".join(summary) + "\n", encoding="utf-8")
    print("\n".join(summary))


if __name__ == "__main__":
    main()

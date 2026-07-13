#!/usr/bin/env python3
"""Audit Digimon skill/attack names against the English game tables."""

from __future__ import annotations

import csv
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path

from fix_skill_attack_names_pass_v087 import (
    SOURCELESS_ID_NAMES,
    TABLES,
    desired_name,
    source_map,
)


ROOT = Path(__file__).resolve().parents[1]
OUT_CSV = ROOT / "exports/skill_attack_name_audit_v086.csv"
OUT_SUMMARY = ROOT / "exports/skill_attack_name_audit_v086_summary.txt"
TIER_RE = re.compile(r"^(.*) (I|II|III)$")
LATIN_RE = re.compile(r"[A-Za-z]{2,}")
TAG_RE = re.compile(r"\{[^}]*\}")
ALLOWED_LATIN = {"HP", "SP", "DX", "I", "II", "III", "IV", "V", "X"}


@dataclass(frozen=True)
class Entry:
    table: str
    row_id: str
    english: str
    russian: str


def read_map(path: Path) -> dict[str, str]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return {row[0]: row[1] for row in list(csv.reader(handle))[1:] if len(row) >= 2}


def add_issue(
    output: list[dict[str, str]],
    issue: str,
    severity: str,
    english: str,
    russian: str,
    locations: str,
    details: str,
) -> None:
    output.append(
        {
            "issue": issue,
            "severity": severity,
            "english": english,
            "russian": russian,
            "locations": locations,
            "details": details,
        }
    )


def main() -> None:
    entries: list[Entry] = []
    unlinked: list[tuple[str, str, str]] = []
    tables: dict[str, list[Entry]] = {}
    sourceless_mismatches: list[tuple[str, str, str, str]] = []
    for spec in TABLES:
        source = source_map(spec)
        target = read_map(spec.target)
        current: list[Entry] = []
        for row_id, russian in target.items():
            english = source.get(row_id)
            if english is None:
                wanted = SOURCELESS_ID_NAMES.get((spec.label, row_id))
                if wanted is None:
                    unlinked.append((spec.label, row_id, russian))
                elif russian != wanted:
                    sourceless_mismatches.append((spec.label, row_id, russian, wanted))
                continue
            entry = Entry(spec.label, row_id, english, russian)
            entries.append(entry)
            current.append(entry)
        tables[spec.label] = current

    output: list[dict[str, str]] = []

    for table, row_id, russian, wanted in sourceless_mismatches:
        add_issue(
            output,
            "reviewed_sourceless_mismatch",
            "confirmed",
            "",
            russian,
            f"{table}:{row_id}",
            f"expected: {wanted}",
        )

    # Regression check for every reviewed canonical rule.
    for entry in entries:
        wanted = desired_name(entry.english)
        if wanted is not None and entry.russian != wanted:
            add_issue(
                output,
                "canonical_mismatch",
                "confirmed",
                entry.english,
                entry.russian,
                f"{entry.table}:{entry.row_id}",
                f"expected: {wanted}",
            )

    # The same exact English attack should not acquire different Russian names
    # merely because it appears in another package or table.
    by_english: dict[str, list[Entry]] = defaultdict(list)
    for entry in entries:
        by_english[entry.english].append(entry)
    for english, group in sorted(by_english.items()):
        translations = sorted({entry.russian for entry in group})
        if len(translations) <= 1:
            continue
        add_issue(
            output,
            "same_english_multiple_russian",
            "confirmed",
            english,
            " | ".join(translations),
            " | ".join(f"{e.table}:{e.row_id}" for e in group),
            "Exact English name has inconsistent Russian equivalents.",
        )

    # Each I/II/III family must retain one Russian base name and one matching
    # numeral.  This catches mistranslations such as «Сокрушитель Ада Я».
    for label, group in sorted(tables.items()):
        families: dict[str, list[tuple[Entry, str]]] = defaultdict(list)
        for entry in group:
            match = TIER_RE.match(entry.english)
            if match:
                families[match.group(1)].append((entry, match.group(2)))
        for english_base, family in sorted(families.items()):
            if {numeral for _, numeral in family} != {"I", "II", "III"}:
                continue
            roots: set[str] = set()
            bad_suffix = False
            for entry, numeral in family:
                suffix = f" {numeral}"
                if not entry.russian.endswith(suffix):
                    bad_suffix = True
                    roots.add(entry.russian)
                else:
                    roots.add(entry.russian[: -len(suffix)])
            if len(roots) > 1 or bad_suffix:
                add_issue(
                    output,
                    "tier_family_inconsistent",
                    "confirmed",
                    english_base,
                    " | ".join(e.russian for e, _ in family),
                    " | ".join(f"{e.table}:{e.row_id}" for e, _ in family),
                    "I/II/III tiers do not share one Russian base name.",
                )

    # Preserve Latin-script names for review: many are intentional trademarks,
    # abbreviations or Japanese romanizations, so these are not auto-fixed.
    seen_latin: set[tuple[str, str]] = set()
    for entry in entries:
        words = LATIN_RE.findall(TAG_RE.sub("", entry.russian))
        if not words or all(word.upper() in ALLOWED_LATIN for word in words):
            continue
        key = (entry.english, entry.russian)
        if key in seen_latin:
            continue
        seen_latin.add(key)
        add_issue(
            output,
            "latin_script_review",
            "review",
            entry.english,
            entry.russian,
            " | ".join(
                f"{e.table}:{e.row_id}"
                for e in by_english[entry.english]
                if e.russian == entry.russian
            ),
            "May be a canon name or abbreviation; requires manual review.",
        )

    fieldnames = ["issue", "severity", "english", "russian", "locations", "details"]
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(output)

    counts = Counter((row["severity"], row["issue"]) for row in output)
    confirmed = sum(count for (severity, _), count in counts.items() if severity == "confirmed")
    review = sum(count for (severity, _), count in counts.items() if severity == "review")
    summary = [
        f"Source-linked rows: {len(entries)}",
        f"Rows without matching extracted English source: {len(unlinked)}",
        f"Confirmed anomalies: {confirmed}",
        f"Manual-review markers: {review}",
    ]
    for (severity, issue), count in sorted(counts.items()):
        summary.append(f"{severity}.{issue}: {count}")
    summary.append(f"Report: {OUT_CSV.relative_to(ROOT)}")
    OUT_SUMMARY.write_text("\n".join(summary) + "\n", encoding="utf-8-sig")
    print("\n".join(summary))


if __name__ == "__main__":
    main()

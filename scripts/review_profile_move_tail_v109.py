#!/usr/bin/env python3
"""Record the reviewed contextual false positives left by profile move audit v096."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "exports/profile_move_name_audit_v096.csv"
OUT = ROOT / "exports/profile_move_context_exclusions_v109.csv"
SUMMARY = ROOT / "exports/profile_move_context_exclusions_v109_summary.txt"

EXPECTED = {
    ("patch_text01", "digimon_0034_profile", "Dark Breath"): "generic_description",
    ("patch_text01", "digimon_0379_profile", "Deep Forest"): "title_phrase",
    ("patch_text01", "digimon_0423_profile", "Deep Forest"): "title_phrase",
    ("patch_text01", "digimon_0359_profile", "Energy Bomb"): "generic_description",
    ("patch_text01", "digimon_0489_profile", "Energy Bomb"): "generic_description",
    ("patch_text01", "digimon_0548_profile", "Energy Bomb"): "generic_description",
    ("patch_text01", "digimon_0627_profile", "Energy Bomb"): "generic_description",
    ("patch_text01", "digimon_0632_profile", "Energy Bomb"): "generic_description",
    ("patch_text01", "digimon_0720_profile", "Energy Bomb"): "generic_description",
    ("patch_text01", "digimon_0771_profile", "Energy Bomb"): "generic_description",
    ("patch_text01", "digimon_0395_profile", "Fox Tail"): "longer_move_substring",
    ("patch_text01", "digimon_0422_profile", "Infinity Cannon"): "longer_move_substring",
    ("patch_text01", "digimon_0740_profile", "Lightning Blade"): "generic_description",
    ("patch_text01", "digimon_0609_profile", "Scissor Claw"): "longer_move_substring",
    ("patch_text01", "digimon_0027_profile", "Speed Charge"): "generic_description",
    ("patch_text01", "digimon_0135_profile", "Wolf Claw"): "longer_move_substring",
}


def main() -> None:
    with AUDIT.open("r", encoding="utf-8-sig", newline="") as handle:
        candidates = list(csv.DictReader(handle))
    actual = {(row["package"], row["row_id"], row["source_move"]): row for row in candidates}
    if set(actual) != set(EXPECTED):
        missing = sorted(set(EXPECTED) - set(actual))
        unexpected = sorted(set(actual) - set(EXPECTED))
        raise SystemExit(f"Profile tail changed: missing={missing}, unexpected={unexpected}")

    output = []
    for key, reason in sorted(EXPECTED.items()):
        row = actual[key]
        output.append(
            {
                "package": row["package"],
                "file": row["file"],
                "row_id": row["row_id"],
                "source_move": row["source_move"],
                "classification": reason,
                "review_status": "accepted_contextual_collision",
                "source_en": row["source_en"],
                "current_ru": row["current_ru"],
            }
        )

    fields = [
        "package", "file", "row_id", "source_move", "classification",
        "review_status", "source_en", "current_ru",
    ]
    with OUT.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(output)

    counts = Counter(row["classification"] for row in output)
    summary = [
        "Profile move contextual exclusions v109",
        f"reviewed={len(output)}",
        f"generic_description={counts['generic_description']}",
        f"title_phrase={counts['title_phrase']}",
        f"longer_move_substring={counts['longer_move_substring']}",
        "actionable=0",
        f"report={OUT.relative_to(ROOT)}",
    ]
    SUMMARY.write_text("\n".join(summary) + "\n", encoding="utf-8")
    print("\n".join(summary))


if __name__ == "__main__":
    main()

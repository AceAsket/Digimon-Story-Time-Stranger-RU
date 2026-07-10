#!/usr/bin/env python3
"""Reconcile the current dialogue audit with completed manual review decisions."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "exports/dialogue_gender_style_audit_v071.csv"
HISTORICAL_REVIEW = ROOT / "exports/dialogue_gender_style_review_v068.csv"
OUT = ROOT / "exports/dialogue_candidate_review_v091.csv"
SUMMARY = ROOT / "exports/dialogue_candidate_review_v091_summary.txt"


SOURCE_CONFIRMED_KEEP = {
    ("machine_phrase", "patch_text01", "message/field_text.mbe/000_Sheet1.csv", "g_shop096_0030_0010"),
    ("machine_phrase", "patch_text01", "message/field_text.mbe/000_Sheet1.csv", "g_shop099_0030_0010"),
}

DEFERRED_UNHOOKED_CHAT = {
    (
        "possible_player_address_gender",
        "patch_text01",
        "message/digimon_chat.mbe/000_Sheet1.csv",
        "rapi_001_3_replay",
    ),
}


def key(row: dict[str, str]) -> tuple[str, str, str, str]:
    return row["category"], row["package"], row["file"], row["row_id"]


def read_dicts(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def main() -> None:
    audit = read_dicts(AUDIT)
    historical = {key(row): row for row in read_dicts(HISTORICAL_REVIEW)}
    output: list[dict[str, str]] = []

    for row in audit:
        identity = key(row)
        old = historical.get(identity)
        if old is not None:
            disposition = "reviewed_" + old["disposition"]
            note = old["review_note"]
            review_source = "manual_review_v068"
        elif identity in SOURCE_CONFIRMED_KEEP:
            disposition = "source_confirmed_keep"
            note = "Natural Russian equivalent of the English source; pattern match is a false positive."
            review_source = "source_context_v091"
        elif identity in DEFERRED_UNHOOKED_CHAT:
            disposition = "deferred_unhooked_player_chat"
            note = "Player-gender chat variant deliberately deferred with the runtime-hook task."
            review_source = "scope_deferred_v091"
        else:
            disposition = "actionable_manual_review"
            note = "No prior decision or explicit source-checked exception."
            review_source = "unreviewed_v091"

        output.append(
            {
                **row,
                "disposition": disposition,
                "review_note": note,
                "review_source": review_source,
            }
        )

    fields = list(audit[0]) + ["disposition", "review_note", "review_source"] if audit else []
    with OUT.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(output)

    dispositions = Counter(row["disposition"] for row in output)
    actionable = dispositions["actionable_manual_review"]
    deferred = dispositions["deferred_unhooked_player_chat"]
    reviewed = len(output) - actionable - deferred
    summary = [
        "Dialogue candidate review v091",
        f"current_candidates={len(output)}",
        f"reviewed_or_source_confirmed={reviewed}",
        f"deferred_unhooked_player_chat={deferred}",
        f"actionable_manual_review={actionable}",
        "",
        "By disposition:",
    ]
    summary.extend(f"- {name}: {count}" for name, count in sorted(dispositions.items()))
    SUMMARY.write_text("\n".join(summary) + "\n", encoding="utf-8")
    print("\n".join(summary))
    if actionable:
        raise SystemExit(f"Unreviewed dialogue candidates remain: {actionable}")


if __name__ == "__main__":
    main()

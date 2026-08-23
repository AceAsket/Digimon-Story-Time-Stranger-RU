#!/usr/bin/env python3
"""Fail on regressions in the reviewed Issue #2 Digimon profile pass."""

from __future__ import annotations

import csv
from pathlib import Path

import fix_issue_2_profiles_v172 as fixes


ROOT = Path(__file__).resolve().parents[1]
PROFILE = ROOT / "csv/patch_text01/text/digimon_profile.mbe/000_Sheet1.csv"
SOURCE_PROFILE = (
    ROOT
    / "verify/game_build_23514637/text_original/patch_text01/csv/text"
    / "digimon_profile.mbe/000_Sheet1.csv"
)

# English source move, canonical Russian skill name.  These were previously
# invisible to the move-name audit because every English name is one word.
REVIEWED_ONE_WORD_MOVES = {
    "digimon_0322_profile": [("Bubbles", "Пузыри")],
    "digimon_0086_profile": [("Bifrost", "Биврёст")],
    "digimon_0185_profile": [
        ("Triangler", "Трианглер"),
        ("Plasmadness", "Плазмобезумие"),
    ],
    "digimon_0193_profile": [("Eiseiryuojin", "Эйсейрюоджин")],
    "digimon_0219_profile": [("Hothead", "Горячая Голова")],
    "digimon_0227_profile": [("Necromist", "Некротуман")],
    "digimon_0749_profile": [("Weltgeist", "Вельтгайст")],
}


def read_rows(path: Path) -> dict[str, str]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return {row[0]: row[1] for row in csv.reader(handle) if len(row) >= 2}


def main() -> None:
    current = read_rows(PROFILE)
    source = read_rows(SOURCE_PROFILE)
    failures: list[str] = []

    for row_id, prose in fixes.NEW_PROSE.items():
        expected = fixes.wrap_profile(prose)
        actual = current.get(row_id)
        if actual != expected:
            failures.append(f"reviewed full row changed: {row_id}")
            continue
        longest = max(map(len, actual.splitlines()))
        if longest > fixes.WRAP_WIDTH:
            failures.append(
                f"reviewed row exceeds {fixes.WRAP_WIDTH} columns: "
                f"{row_id} ({longest})"
            )

    for row_id, old, new, expected_count in fixes.TERM_FIXES:
        actual = current.get(row_id, "")
        if old in actual:
            failures.append(f"old reviewed term remains: {row_id}: {old}")
        if row_id in fixes.NEW_PROSE:
            # The exact full-row guard above is authoritative; a human rewrite
            # may legitimately mention the canonical name fewer times.
            continue
        if actual.count(new) < expected_count:
            failures.append(
                f"approved term missing: {row_id}: {new} "
                f"({actual.count(new)} < {expected_count})"
            )

    for row_id, moves in REVIEWED_ONE_WORD_MOVES.items():
        source_text = source.get(row_id, "")
        current_text = current.get(row_id, "")
        current_compact = " ".join(current_text.split())
        for english, russian in moves:
            if english not in source_text:
                failures.append(f"English move guard changed: {row_id}: {english}")
            if russian not in current_compact:
                failures.append(f"canonical move missing: {row_id}: {russian}")

    # Direct Issue #2 regressions that are more specific than the general
    # terminology table above.
    issue_guards = {
        "digimon_0322_profile": ["Коромон", "Пузыри"],
        "digimon_0097_profile": [
            "Пико Девимон",
            "Девимон",
            "Вамдемон",
            "Малые дротики",
        ],
    }
    for row_id, required in issue_guards.items():
        actual = " ".join(current.get(row_id, "").split())
        for value in required:
            if value not in actual:
                failures.append(f"Issue #2 value missing: {row_id}: {value}")

    print(f"Reviewed full rows: {len(fixes.NEW_PROSE)}")
    print(f"Reviewed terminology guards: {len(fixes.TERM_FIXES)}")
    print(
        "Reviewed one-word moves: "
        + str(sum(len(moves) for moves in REVIEWED_ONE_WORD_MOVES.values()))
    )
    print(f"Failures: {len(failures)}")
    for failure in failures:
        print(f"FAIL: {failure}")
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

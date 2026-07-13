#!/usr/bin/env python3
"""Classify current payload English-text findings after source review."""

from __future__ import annotations

import csv
import re
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "exports/payload_text_audit_v092.csv"
PATCH_ROOT = ROOT / "csv/patch_text01"
OUT = ROOT / "exports/payload_text_review_v093.csv"
SUMMARY = ROOT / "exports/payload_text_review_v093_summary.txt"

SEMANTIC_NEXT_PASS = re.compile(
    r"(?:skill_name|skill_ruby|item_name|item_ruby|item_explanation|"
    r"personality_skill_explanation|digimon_profile|buff_message)\.mbe/",
    re.IGNORECASE,
)

# Every remaining mixed-script token was reviewed in context.  New tokens are
# deliberately not accepted automatically and will become actionable findings.
ALLOWED_MIXED_TOKENS = {
    "A.D.V", "Accel", "Access", "Adventure", "AltaVision", "Alter-B", "Alter-S",
    "amp", "Anti-ParadoX", "ARE", "Arise", "Arm", "Assemble", "BAN-TYO", "Bats",
    "Battles", "Bearmon", "BEATBREAK", "Believer", "Black", "Blitz", "BM", "CP",
    "Critical", "Cyber", "D-", "Data", "Debug", "Deck", "Defeat", "DIGIFARM",
    "Digimon", "dl", "DM", "DORU-Din", "D-VI'S", "DX", "Edion", "EP", "Esc",
    "eShop", "EX", "Expo", "Frontier", "Fusion", "GAKU-RAN", "Ghost", "Going",
    "Golden", "Gouing", "HDR", "Heart", "Hickeys", "Home", "Hootle", "HRCGT",
    "HUD", "ID", "Idolmaster", "II", "III", "inForce", "IQ", "IT-", "IV",
    "JUCG", "Kamedical", "LB", "Little", "LT", "Makino", "Marsmon's", "Microsoft",
    "MM", "My", "Nebagiba", "Nightmare", "Nintendo", "no", "NPC", "of", "Olympus",
    "Omega", "OMNI-", "PAC-MAN", "Photon", "PlayStation", "Ramen", "RB", "REM-",
    "RT", "Savers", "SDGP", "Select", "Shield", "Sleuth", "soul", "Spreads",
    "Squad", "Start", "Store", "Story", "Stranger", "Taiko", "Tales", "Tamers",
    "Tatsujin", "TBD", "TEKKEN", "Tense-Great", "The", "Time", "TP", "Ulforce",
    "USB-", "V-", "VIP-", "VS", "Wars", "WE", "X-", "XD", "XII", "Xros", "xx",
    "ZERO-ARMS", "Zwart",
}

ALLOWED_SAME_AS_SOURCE = {
    ("addcont_03_text01", "text/quest_title_dlc03.mbe/000_Sheet1.csv", "530"),
    ("app_text01", "text/common_message_dx11.mbe/000_Sheet1.csv", "1901307"),
    ("patch_text01", "text/common_message_dx11.mbe/000_Sheet1.csv", "1901307"),
}


def patch_keys() -> set[tuple[str, str]]:
    result: set[tuple[str, str]] = set()
    for path in sorted(PATCH_ROOT.rglob("*.csv")):
        relative = path.relative_to(PATCH_ROOT).as_posix()
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            for row in csv.reader(handle):
                if row:
                    result.add((relative, row[0]))
    return result


def main() -> None:
    with AUDIT.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))

    patch = patch_keys()
    output: list[dict[str, str]] = []
    for row in rows:
        identity = (row["package"], row["file"], row["row_id"])
        if row["package"] == "app_text01" and (row["file"], row["row_id"]) in patch:
            disposition = "shadowed_by_patch"
            note = "The effective value is supplied by patch_text01."
        elif row["category"] == "extra_payload_package" and row["package"] == "addcont_17_text01":
            disposition = "optional_dlc_not_installed"
            note = "Optional DLC payload is valid but absent from this game installation."
        elif row["category"] == "same_as_original" and identity in ALLOWED_SAME_AS_SOURCE:
            disposition = "reviewed_proper_or_debug_label"
            note = "Source-identical proper title or internal debug resolution label."
        elif row["category"] == "latin_no_cyrillic" and "common_message_dx11.mbe/" in row["file"]:
            disposition = "reviewed_input_or_graphics_label"
            note = "Keyboard key, rendering mode, or graphics abbreviation."
        elif row["category"] == "latin_mixed" and SEMANTIC_NEXT_PASS.search(row["file"]):
            disposition = "deferred_semantic_items_skills_profiles"
            note = "Review together with item, skill, effect, and profile terminology."
        elif row["category"] == "latin_mixed":
            tokens = {token.strip() for token in row["detail"].split(",") if token.strip()}
            unknown = sorted(tokens - ALLOWED_MIXED_TOKENS)
            if unknown:
                disposition = "actionable_manual_review"
                note = "Unreviewed mixed-script token(s): " + ", ".join(unknown)
            else:
                disposition = "reviewed_proper_or_technical_token"
                note = "Source-checked name, acronym, brand, control label, or retained title."
        else:
            disposition = "actionable_manual_review"
            note = "Visible English finding has no reviewed exception."

        output.append({**row, "disposition": disposition, "review_note": note})

    fields = list(rows[0]) + ["disposition", "review_note"] if rows else []
    with OUT.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(output)

    counts = Counter(row["disposition"] for row in output)
    actionable = counts["actionable_manual_review"]
    summary = [
        "Current payload text review v093",
        f"audit_rows={len(output)}",
        f"actionable_manual_review={actionable}",
        "",
        "By disposition:",
    ]
    summary.extend(f"- {name}: {count}" for name, count in sorted(counts.items()))
    SUMMARY.write_text("\n".join(summary) + "\n", encoding="utf-8")
    print("\n".join(summary))
    if actionable:
        raise SystemExit(f"Unreviewed payload text findings remain: {actionable}")


if __name__ == "__main__":
    main()

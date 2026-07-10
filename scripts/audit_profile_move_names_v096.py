#!/usr/bin/env python3
"""Compare move names mentioned in Digimon profiles with approved skill names."""

from __future__ import annotations

import csv
import re
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CSV_ROOT = ROOT / "csv"
SOURCE_ROOT = ROOT / "verify/game_build_23514637/text_original"
OUT = ROOT / "exports/profile_move_name_audit_v096.csv"
SUMMARY = ROOT / "exports/profile_move_name_audit_v096_summary.txt"

SKILL_FILE_RE = re.compile(r"(?:^|/)(?:skill_name|jogress_skill_name)(?:_dlc\d+)?\.mbe/000_Sheet1\.csv$", re.I)
PROFILE_FILE_RE = re.compile(r"(?:^|/)digimon_profile(?:_dlc\d+)?\.mbe/000_Sheet1\.csv$", re.I)
SPACE_RE = re.compile(r"\s+")

ACCEPTED_INFLECTED_PROFILE_NAMES = {
    ("addcont_02_text01", "digimon_0448_profile", "Graceful Cannon"),
    ("addcont_03_text01", "digimon_0432_profile", "Shining Gold Solar Storm"),
    ("patch_text01", "digimon_0744_profile", "Phosphorus Fire Attack"),
    ("patch_text01", "digimon_0232_profile", "Symphony No. 1"),
    ("patch_text01", "digimon_0232_profile", "Symphony No. 2"),
}

ACCEPTED_CONTEXTUAL_COLLISIONS = {
    ("patch_text01", "digimon_0034_profile", "Dark Breath"),
    ("patch_text01", "digimon_0379_profile", "Deep Forest"),
    ("patch_text01", "digimon_0423_profile", "Deep Forest"),
    ("patch_text01", "digimon_0359_profile", "Energy Bomb"),
    ("patch_text01", "digimon_0489_profile", "Energy Bomb"),
    ("patch_text01", "digimon_0548_profile", "Energy Bomb"),
    ("patch_text01", "digimon_0627_profile", "Energy Bomb"),
    ("patch_text01", "digimon_0632_profile", "Energy Bomb"),
    ("patch_text01", "digimon_0720_profile", "Energy Bomb"),
    ("patch_text01", "digimon_0771_profile", "Energy Bomb"),
    ("patch_text01", "digimon_0395_profile", "Fox Tail"),
    ("patch_text01", "digimon_0422_profile", "Infinity Cannon"),
    ("patch_text01", "digimon_0740_profile", "Lightning Blade"),
    ("patch_text01", "digimon_0609_profile", "Scissor Claw"),
    ("patch_text01", "digimon_0027_profile", "Speed Charge"),
    ("patch_text01", "digimon_0135_profile", "Wolf Claw"),
}


def read_rows(path: Path) -> dict[str, str]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return {row[0]: row[1] for row in csv.reader(handle) if len(row) >= 2}


def normalize(text: str) -> str:
    text = text.replace("ё", "е").replace("Ё", "Е")
    text = text.replace("«", '"').replace("»", '"').replace("“", '"').replace("”", '"')
    return SPACE_RE.sub(" ", text).strip().casefold()


def useful_move_name(name: str) -> bool:
    words = re.findall(r"[A-Za-z][A-Za-z'-]+", name)
    if len(name.strip()) < 7:
        return False
    if len(words) >= 2:
        return True
    return any(char in name for char in "-:/") and bool(words)


def contains_name(text: str, name: str) -> bool:
    pieces = [re.escape(piece) for piece in name.split()]
    pattern = r"(?<![A-Za-z])" + r"\s+".join(pieces) + r"(?![A-Za-z])"
    return bool(re.search(pattern, text, re.I))


def main() -> None:
    approved: dict[str, set[str]] = defaultdict(set)
    display_name: dict[str, str] = {}
    linked_skill_rows = 0

    for package_root in sorted(path for path in CSV_ROOT.iterdir() if path.is_dir()):
        for path in sorted((package_root / "text").rglob("000_Sheet1.csv")):
            relative = path.relative_to(package_root).as_posix()
            if not SKILL_FILE_RE.search(relative):
                continue
            source_path = SOURCE_ROOT / package_root.name / "csv" / relative
            if not source_path.exists():
                continue
            current = read_rows(path)
            source = read_rows(source_path)
            for row_id, english in source.items():
                russian = current.get(row_id, "").strip()
                english = english.strip()
                if not russian or not useful_move_name(english):
                    continue
                linked_skill_rows += 1
                key = normalize(english)
                display_name.setdefault(key, english)
                approved[key].add(russian)

    findings: list[dict[str, str]] = []
    profile_rows = 0
    source_mentions = 0
    ordered_names = sorted(display_name, key=len, reverse=True)
    for package_root in sorted(path for path in CSV_ROOT.iterdir() if path.is_dir()):
        for path in sorted((package_root / "text").rglob("000_Sheet1.csv")):
            relative = path.relative_to(package_root).as_posix()
            if not PROFILE_FILE_RE.search(relative):
                continue
            source_path = SOURCE_ROOT / package_root.name / "csv" / relative
            if not source_path.exists():
                continue
            current_rows = read_rows(path)
            source_rows = read_rows(source_path)
            for row_id, source_text in source_rows.items():
                current_text = current_rows.get(row_id, "")
                if not current_text:
                    continue
                profile_rows += 1
                normalized_current = normalize(current_text)
                seen: set[str] = set()
                for name_key in ordered_names:
                    english = display_name[name_key]
                    if name_key in seen or not contains_name(source_text, english):
                        continue
                    seen.add(name_key)
                    source_mentions += 1
                    if (package_root.name, row_id, english) in ACCEPTED_INFLECTED_PROFILE_NAMES:
                        continue
                    if (package_root.name, row_id, english) in ACCEPTED_CONTEXTUAL_COLLISIONS:
                        continue
                    translations = sorted(approved[name_key])
                    if any(normalize(value) in normalized_current for value in translations):
                        continue
                    retained = contains_name(current_text, english)
                    findings.append(
                        {
                            "priority": "P4" if retained else "P3",
                            "issue": "english_move_name_retained" if retained else "profile_move_translation_mismatch",
                            "package": package_root.name,
                            "file": relative,
                            "row_id": row_id,
                            "source_move": english,
                            "approved_ru": " | ".join(translations),
                            "source_en": source_text,
                            "current_ru": current_text,
                        }
                    )

    findings.sort(key=lambda row: (-int(row["priority"][1:]), row["source_move"], row["package"], row["row_id"]))
    fields = ["priority", "issue", "package", "file", "row_id", "source_move", "approved_ru", "source_en", "current_ru"]
    with OUT.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(findings)

    retained_count = sum(row["issue"] == "english_move_name_retained" for row in findings)
    summary = [
        "Profile move-name audit v096",
        f"linked_skill_rows={linked_skill_rows}",
        f"profile_rows={profile_rows}",
        f"source_move_mentions={source_mentions}",
        f"candidates={len(findings)}",
        f"english_move_name_retained={retained_count}",
        f"translation_mismatch={len(findings) - retained_count}",
        f"report={OUT.relative_to(ROOT)}",
    ]
    SUMMARY.write_text("\n".join(summary) + "\n", encoding="utf-8")
    print("\n".join(summary))


if __name__ == "__main__":
    main()

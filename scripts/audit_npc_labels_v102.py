#!/usr/bin/env python3
"""Audit generic NPC labels against displayed English names and usage counts."""

from __future__ import annotations

import csv
import re
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CSV_ROOT = ROOT / "csv"
CURRENT = CSV_ROOT / "patch_text01/text/char_name.mbe/000_Sheet1.csv"
SOURCE = ROOT / "verify/game_build_23514637/text_original/patch_text01/csv/text/char_name.mbe/000_Sheet1.csv"
REGISTRY = ROOT / "exports/npc_label_registry_v102.csv"
ISSUES = ROOT / "exports/npc_label_audit_v102.csv"
SUMMARY = ROOT / "exports/npc_label_audit_v102_summary.txt"

GENERIC_EN = re.compile(
    r"\b(?:man|woman|boy|girl|male|female|mother|maiden|student|clerk|employee|"
    r"passerby|voice|guest|worker|manager|agent|otaku|geek|customer|client|staff|"
    r"public security|shopkeeper|bartender)\b",
    re.I,
)
FEMALE_EN = re.compile(r"\b(?:woman|girl|female|mother|maiden|schoolgirl|waitress|lady)\b", re.I)
MALE_EN = re.compile(r"\b(?:man|boy|male|schoolboy|oldman)\b", re.I)

FEMALE_RU = re.compile(r"девуш|девоч|женщ|студентк|сотрудниц|заказчиц|прохожая|сплетниц|жриц|мать|она\b", re.I)
MALE_RU = re.compile(r"мужчин|мальчик|парень|старик|студент\b|сотрудник\b|прохожий|сплетник\b|рабочий\b", re.I)

DESCRIPTORS = [
    (re.compile(r"\bglasses\b", re.I), re.compile(r"очк", re.I), "glasses"),
    (re.compile(r"\bsuit\b", re.I), re.compile(r"костюм", re.I), "suit"),
    (re.compile(r"\bphone\b", re.I), re.compile(r"телефон", re.I), "phone"),
    (re.compile(r"\bpasserby\b", re.I), re.compile(r"прохож", re.I), "passerby"),
    (re.compile(r"\b(?:tired|exhausted)\b", re.I), re.compile(r"устал|уставш|измуч", re.I), "tired"),
    (re.compile(r"\bpale\b", re.I), re.compile(r"блед", re.I), "pale"),
    (re.compile(r"\bmysterious\b", re.I), re.compile(r"таинствен|загадоч", re.I), "mysterious"),
    (re.compile(r"\bstudent\b", re.I), re.compile(r"студент|школьник|школьниц|старшекласс", re.I), "student"),
    (re.compile(r"\bvoice\b", re.I), re.compile(r"голос", re.I), "voice"),
    (re.compile(r"public security", re.I), re.compile(r"общественн.{0,20}безопас", re.I), "public_security"),
    (re.compile(r"\b(?:standing around|idling around)\b", re.I), re.compile(r"без дела|скуча|стоящ", re.I), "idling"),
    (re.compile(r"faking interest", re.I), re.compile(r"изобража|притвор", re.I), "faking_interest"),
    (re.compile(r"\buninterested\b", re.I), re.compile(r"равнодуш|безразлич|неинтерес", re.I), "uninterested"),
    (re.compile(r"\bcreative\b", re.I), re.compile(r"творч", re.I), "creative"),
]


def read_rows(path: Path) -> dict[str, str]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return {row[0]: row[1] for row in csv.reader(handle) if len(row) >= 2}


def speaker_usage() -> Counter[str]:
    counts: Counter[str] = Counter()
    for package_root in sorted(path for path in CSV_ROOT.iterdir() if path.is_dir()):
        message_root = package_root / "message"
        if not message_root.exists():
            continue
        for path in message_root.rglob("000_Sheet1.csv"):
            with path.open("r", encoding="utf-8-sig", newline="") as handle:
                for row in csv.reader(handle):
                    if len(row) >= 3 and row[1]:
                        counts[row[1]] += 1
    return counts


def main() -> None:
    current = read_rows(CURRENT)
    source = read_rows(SOURCE)
    usage = speaker_usage()
    registry: list[dict[str, str | int]] = []
    issues: list[dict[str, str | int]] = []

    for speaker, english in source.items():
        russian = current.get(speaker, "")
        if not russian or not GENERIC_EN.search(english):
            continue
        source_gender = "female" if FEMALE_EN.search(english) else "male" if MALE_EN.search(english) else "neutral"
        registry.append(
            {
                "speaker": speaker,
                "source_en": english,
                "current_ru": russian,
                "source_gender": source_gender,
                "dialogue_rows": usage[speaker],
            }
        )

        if source_gender == "female" and MALE_RU.search(russian) and not FEMALE_RU.search(russian):
            issues.append(
                {
                    "priority": "P5",
                    "issue": "female_label_rendered_male",
                    "speaker": speaker,
                    "source_en": english,
                    "current_ru": russian,
                    "dialogue_rows": usage[speaker],
                    "detail": "English label is explicitly female.",
                }
            )
        if source_gender == "male" and FEMALE_RU.search(russian) and not MALE_RU.search(russian):
            issues.append(
                {
                    "priority": "P5",
                    "issue": "male_label_rendered_female",
                    "speaker": speaker,
                    "source_en": english,
                    "current_ru": russian,
                    "dialogue_rows": usage[speaker],
                    "detail": "English label is explicitly male.",
                }
            )

        for en_pattern, ru_pattern, descriptor in DESCRIPTORS:
            if en_pattern.search(english) and not ru_pattern.search(russian):
                issues.append(
                    {
                        "priority": "P2",
                        "issue": "descriptor_missing",
                        "speaker": speaker,
                        "source_en": english,
                        "current_ru": russian,
                        "dialogue_rows": usage[speaker],
                        "detail": descriptor,
                    }
                )

    registry.sort(key=lambda row: (-int(row["dialogue_rows"]), str(row["speaker"])))
    issues.sort(key=lambda row: (-int(str(row["priority"])[1:]), -int(row["dialogue_rows"]), str(row["speaker"])))

    registry_fields = ["speaker", "source_en", "current_ru", "source_gender", "dialogue_rows"]
    with REGISTRY.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=registry_fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(registry)
    issue_fields = ["priority", "issue", "speaker", "source_en", "current_ru", "dialogue_rows", "detail"]
    with ISSUES.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=issue_fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(issues)

    gender_errors = sum(row["priority"] == "P5" for row in issues)
    summary = [
        "NPC label audit v102",
        f"generic_labels={len(registry)}",
        f"dialogue_rows={sum(int(row['dialogue_rows']) for row in registry)}",
        f"gender_errors={gender_errors}",
        f"descriptor_review={len(issues) - gender_errors}",
        f"registry={REGISTRY.relative_to(ROOT)}",
        f"issues={ISSUES.relative_to(ROOT)}",
    ]
    SUMMARY.write_text("\n".join(summary) + "\n", encoding="utf-8")
    print("\n".join(summary))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Audit Digimon gender per dialogue context using explicit English pronouns."""

from __future__ import annotations

import csv
import re
from collections import Counter, defaultdict
from pathlib import Path

from audit_fixed_speaker_gender_v076 import FEMALE_FORMS, MALE_FORMS, self_forms


ROOT = Path(__file__).resolve().parents[1]
CSV_ROOT = ROOT / "csv"
SOURCE_ROOT = ROOT / "verify/game_build_23514637/text_original"
CURRENT_NAMES = CSV_ROOT / "patch_text01/text/char_name.mbe/000_Sheet1.csv"
SOURCE_NAMES = SOURCE_ROOT / "patch_text01/csv/text/char_name.mbe/000_Sheet1.csv"
OUT = ROOT / "exports/digimon_gender_context_registry_v103.csv"
ISSUES = ROOT / "exports/digimon_gender_context_conflicts_v103.csv"
SUMMARY = ROOT / "exports/digimon_gender_context_v103_summary.txt"

SPACE_RE = re.compile(r"\s+")


def read_rows(path: Path) -> list[list[str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.reader(handle))


def digimon_ids() -> set[str]:
    result: set[str] = set()
    for row in read_rows(CURRENT_NAMES)[1:]:
        if not row:
            continue
        if row[0] == "char_PLAYER_M":
            break
        result.add(row[0])
    return result


def names(path: Path) -> dict[str, str]:
    return {row[0]: row[1] for row in read_rows(path) if len(row) >= 2}


def source_gender_evidence(name: str, texts: list[str]) -> tuple[Counter[str], list[str]]:
    counts: Counter[str] = Counter()
    samples: list[str] = []
    if not name or len(name) < 4:
        return counts, samples
    escaped = re.escape(name)
    pronouns = r"(?:he|him|his|she|her|hers)"
    # A pronoun before a name often refers to the preceding character (for
    # example, "put him to sleep! Witchmon, ..."), so only accept the safer
    # name-then-pronoun direction.
    patterns = [re.compile(r"\b" + escaped + r"\b.{0,160}\b(" + pronouns + r")\b", re.I)]
    for text in texts:
        compact = SPACE_RE.sub(" ", text)
        for pattern in patterns:
            match = pattern.search(compact)
            if not match:
                continue
            pronoun = match.group(1).lower()
            gender = "female" if pronoun in {"she", "her", "hers"} else "male"
            counts[gender] += 1
            if len(samples) < 3:
                samples.append(compact)
            break
    return counts, samples


def main() -> None:
    ids = digimon_ids()
    current_names = names(CURRENT_NAMES)
    source_names = names(SOURCE_NAMES)
    registry: list[dict[str, str | int]] = []
    conflicts: list[dict[str, str | int]] = []

    for package_root in sorted(path for path in CSV_ROOT.iterdir() if path.is_dir()):
        message_root = package_root / "message"
        if not message_root.exists():
            continue
        for path in sorted(message_root.rglob("000_Sheet1.csv")):
            relative = path.relative_to(package_root).as_posix()
            source_path = SOURCE_ROOT / package_root.name / "csv" / relative
            if not source_path.exists():
                continue
            current_rows = read_rows(path)
            source_rows = read_rows(source_path)
            source_texts = [row[2] for row in source_rows if len(row) >= 3]
            grouped: dict[str, list[str]] = defaultdict(list)
            for row in current_rows[1:]:
                if len(row) >= 3 and row[1] in ids and not row[0].endswith(("__H", "__F")):
                    grouped[row[1]].append(row[2])

            for speaker, texts in grouped.items():
                male_forms = sum(len(self_forms(text, MALE_FORMS)) for text in texts)
                female_forms = sum(len(self_forms(text, FEMALE_FORMS)) for text in texts)
                if male_forms and female_forms:
                    observed = "mixed"
                elif male_forms:
                    observed = "male"
                elif female_forms:
                    observed = "female"
                else:
                    observed = "unknown"

                evidence, samples = source_gender_evidence(source_names.get(speaker, ""), source_texts)
                if evidence["male"] and evidence["female"]:
                    source_gender = "mixed"
                elif evidence["male"]:
                    source_gender = "male"
                elif evidence["female"]:
                    source_gender = "female"
                else:
                    source_gender = "unknown"

                registry.append(
                    {
                        "package": package_root.name,
                        "file": relative,
                        "speaker": speaker,
                        "speaker_name": current_names.get(speaker, ""),
                        "dialogue_rows": len(texts),
                        "observed_ru_gender": observed,
                        "male_first_person_forms": male_forms,
                        "female_first_person_forms": female_forms,
                        "source_pronoun_gender": source_gender,
                        "source_male_evidence": evidence["male"],
                        "source_female_evidence": evidence["female"],
                        "source_samples": " || ".join(samples),
                    }
                )

                if source_gender in {"male", "female"} and observed in {"male", "female"} and source_gender != observed:
                    conflicts.append(
                        {
                            "priority": "P5",
                            "package": package_root.name,
                            "file": relative,
                            "speaker": speaker,
                            "speaker_name": current_names.get(speaker, ""),
                            "dialogue_rows": len(texts),
                            "source_gender": source_gender,
                            "observed_ru_gender": observed,
                            "source_samples": " || ".join(samples),
                        }
                    )

    registry.sort(key=lambda row: (-int(row["dialogue_rows"]), str(row["speaker"]), str(row["file"])))
    conflicts.sort(key=lambda row: (-int(row["dialogue_rows"]), str(row["speaker"])))
    fields = [
        "package", "file", "speaker", "speaker_name", "dialogue_rows", "observed_ru_gender",
        "male_first_person_forms", "female_first_person_forms", "source_pronoun_gender",
        "source_male_evidence", "source_female_evidence", "source_samples",
    ]
    with OUT.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(registry)
    conflict_fields = [
        "priority", "package", "file", "speaker", "speaker_name", "dialogue_rows",
        "source_gender", "observed_ru_gender", "source_samples",
    ]
    with ISSUES.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=conflict_fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(conflicts)

    explicit = sum(row["source_pronoun_gender"] in {"male", "female"} for row in registry)
    mixed_source = sum(row["source_pronoun_gender"] == "mixed" for row in registry)
    summary = [
        "Digimon gender context audit v103",
        f"contexts={len(registry)}",
        f"dialogue_rows={sum(int(row['dialogue_rows']) for row in registry)}",
        f"explicit_source_pronoun_contexts={explicit}",
        f"mixed_source_pronoun_contexts={mixed_source}",
        f"confirmed_conflicts={len(conflicts)}",
        f"registry={OUT.relative_to(ROOT)}",
        f"conflicts={ISSUES.relative_to(ROOT)}",
    ]
    SUMMARY.write_text("\n".join(summary) + "\n", encoding="utf-8")
    print("\n".join(summary))


if __name__ == "__main__":
    main()

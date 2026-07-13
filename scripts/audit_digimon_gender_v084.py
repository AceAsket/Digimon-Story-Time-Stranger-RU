#!/usr/bin/env python3
"""Build a dialogue-gender registry for Digimon speaker IDs.

Species reused for unrelated NPCs are deliberately not assigned one global
sex.  Fixed recurring story characters use the curated source-confirmed sets;
other speakers receive only contextual evidence from their own Russian lines.
"""

from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path

from audit_fixed_speaker_gender_v076 import (
    FEMALE_FORMS,
    FEMALE_SPEAKERS,
    INTENTIONAL_MALE_QUOTES,
    MALE_FORMS,
    MALE_SPEAKERS,
    self_forms,
)


ROOT = Path(__file__).resolve().parents[1]
CSV_ROOT = ROOT / "csv"
CHAR_NAMES = ROOT / "csv/patch_text01/text/char_name.mbe/000_Sheet1.csv"
OUT_REGISTRY = ROOT / "exports/digimon_dialogue_gender_registry_v084.csv"
OUT_CONFLICTS = ROOT / "exports/digimon_dialogue_gender_conflicts_v084.csv"
OUT_SUMMARY = ROOT / "exports/digimon_dialogue_gender_v084_summary.txt"


def digimon_speaker_ids() -> set[str]:
    with CHAR_NAMES.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.reader(handle))
    result: set[str] = set()
    for row in rows[1:]:
        if not row:
            continue
        if row[0] == "char_PLAYER_M":
            break
        result.add(row[0])
    return result


def main() -> None:
    digimon_ids = digimon_speaker_ids()
    stats: dict[str, Counter[str]] = defaultdict(Counter)
    names: dict[str, str] = {}
    with CHAR_NAMES.open("r", encoding="utf-8-sig", newline="") as handle:
        for row in csv.reader(handle):
            if len(row) >= 2:
                names[row[0]] = row[1]

    conflicts: list[dict[str, str]] = []
    for package_root in sorted(path for path in CSV_ROOT.iterdir() if path.is_dir()):
        message_root = package_root / "message"
        if not message_root.exists():
            continue
        for path in sorted(message_root.rglob("000_Sheet1.csv")):
            relative = path.relative_to(package_root).as_posix()
            with path.open("r", encoding="utf-8-sig", newline="") as handle:
                rows = list(csv.reader(handle))
            for row in rows[1:]:
                if len(row) < 3 or row[0].endswith(("__H", "__F")):
                    continue
                row_id, speaker, text = row[0], row[1], row[2]
                if speaker not in digimon_ids:
                    continue
                identity = (package_root.name, relative, row_id)
                stats[speaker]["rows"] += 1
                male = self_forms(text, MALE_FORMS)
                female = self_forms(text, FEMALE_FORMS)
                stats[speaker]["male_forms"] += len(male)
                stats[speaker]["female_forms"] += len(female)
                if identity in INTENTIONAL_MALE_QUOTES:
                    continue
                if speaker in FEMALE_SPEAKERS:
                    wrong = male
                    expected = "female"
                elif speaker in MALE_SPEAKERS:
                    wrong = female
                    expected = "male"
                else:
                    wrong = []
                    expected = ""
                for form, context in wrong:
                    conflicts.append(
                        {
                            "expected_gender": expected,
                            "package": package_root.name,
                            "file": relative,
                            "row_id": row_id,
                            "speaker": speaker,
                            "speaker_name": names.get(speaker, ""),
                            "found": form,
                            "context": context,
                            "text": text,
                        }
                    )

    registry: list[dict[str, str]] = []
    for speaker, count in sorted(stats.items()):
        male = count["male_forms"]
        female = count["female_forms"]
        if speaker in FEMALE_SPEAKERS:
            expected = "female"
            status = "curated_source_confirmed"
        elif speaker in MALE_SPEAKERS:
            expected = "male"
            status = "curated_source_confirmed"
        elif male and female:
            expected = "context-dependent"
            status = "mixed_context_review"
        elif male:
            expected = "contextual male"
            status = "first_person_evidence_only"
        elif female:
            expected = "contextual female"
            status = "first_person_evidence_only"
        else:
            expected = "unknown"
            status = "no_explicit_first_person_form"
        registry.append(
            {
                "speaker": speaker,
                "speaker_name": names.get(speaker, ""),
                "dialogue_rows": str(count["rows"]),
                "expected_or_observed_gender": expected,
                "male_first_person_forms": str(male),
                "female_first_person_forms": str(female),
                "status": status,
            }
        )

    OUT_REGISTRY.parent.mkdir(parents=True, exist_ok=True)
    registry_fields = [
        "speaker",
        "speaker_name",
        "dialogue_rows",
        "expected_or_observed_gender",
        "male_first_person_forms",
        "female_first_person_forms",
        "status",
    ]
    with OUT_REGISTRY.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=registry_fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(registry)

    conflict_fields = [
        "expected_gender",
        "package",
        "file",
        "row_id",
        "speaker",
        "speaker_name",
        "found",
        "context",
        "text",
    ]
    with OUT_CONFLICTS.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=conflict_fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(conflicts)

    status_counts = Counter(row["status"] for row in registry)
    summary = [
        f"Digimon speaker IDs with dialogue: {len(registry)}",
        f"Digimon dialogue rows: {sum(int(row['dialogue_rows']) for row in registry)}",
        f"Curated source-confirmed speakers: {status_counts['curated_source_confirmed']}",
        f"Curated first-person gender conflicts: {len(conflicts)}",
        f"Mixed context-dependent speaker IDs: {status_counts['mixed_context_review']}",
        f"Context-only single-gender evidence: {status_counts['first_person_evidence_only']}",
        f"No explicit first-person form: {status_counts['no_explicit_first_person_form']}",
        f"Registry: {OUT_REGISTRY.relative_to(ROOT)}",
        f"Conflicts: {OUT_CONFLICTS.relative_to(ROOT)}",
    ]
    OUT_SUMMARY.write_text("\n".join(summary) + "\n", encoding="utf-8-sig")
    print("\n".join(summary))


if __name__ == "__main__":
    main()

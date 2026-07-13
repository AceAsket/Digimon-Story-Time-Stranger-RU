#!/usr/bin/env python3
"""Audit item, skill, buff, and effect text against the clean English source."""

from __future__ import annotations

import csv
import re
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CSV_ROOT = ROOT / "csv"
SOURCE_ROOT = ROOT / "verify/game_build_23514637/text_original"
OUT = ROOT / "exports/item_skill_semantic_audit_v094.csv"
SUMMARY = ROOT / "exports/item_skill_semantic_audit_v094_summary.txt"

FILE_RE = re.compile(
    r"(?:item_(?:name|ruby|explanation|auto_explanation|pack_name|pack_explanation)|"
    r"skill_(?:name|ruby|explanation|auto_explanation)|jogress_skill_name|"
    r"personality_(?:effect|skill_explanation)|tamer_skill_explanation|"
    r"buff_(?:name|message))"
    r"(?:_dlc\d+)?\.mbe/000_Sheet1\.csv$",
    re.IGNORECASE,
)

TAG_RE = re.compile(r"\{([A-Za-z_]+\d*)")
NUMBER_RE = re.compile(r"(?<![A-Za-zА-Яа-яЁё])\d+(?:[.,]\d+)?%?")
ROMAN_RE = re.compile(r"(?<![A-Za-zА-Яа-яЁё&])(VIII|VII|VI|IV|V|III|II|I)\s*$")
ROMAN_VALUES = {"I": "1", "II": "2", "III": "3", "IV": "4", "V": "5", "VI": "6", "VII": "7", "VIII": "8"}
SPACE_RE = re.compile(r"\s+")

DUPLICATE_EXCEPTIONS = {
    ("text/item_explanation.mbe/000_Sheet1.csv", "835"),
}


def normalize(text: str) -> str:
    return SPACE_RE.sub(" ", text).strip()


def numbers(text: str, include_roman: bool = False) -> tuple[str, ...]:
    text = re.sub(r"\{[^}]*\}", " ", text)
    values = [value.replace(",", ".") for value in NUMBER_RE.findall(text)]
    if include_roman:
        values.extend(ROMAN_VALUES[value] for value in ROMAN_RE.findall(text))
    return tuple(sorted(values))


def controls(text: str) -> tuple[str, ...]:
    return tuple(sorted(TAG_RE.findall(text)))


def family(relative: str) -> str:
    return re.sub(r"_dlc\d+(?=\.mbe/)", "", relative, flags=re.IGNORECASE)


def add(
    findings: list[dict[str, str]],
    priority: str,
    issue: str,
    package: str,
    relative: str,
    row_id: str,
    source: str,
    current: str,
    detail: str,
) -> None:
    findings.append(
        {
            "priority": priority,
            "issue": issue,
            "package": package,
            "file": relative,
            "row_id": row_id,
            "detail": detail,
            "source_en": source,
            "current_ru": current,
        }
    )


def semantic_checks(source: str, current: str) -> list[tuple[str, str, str]]:
    en = normalize(source).lower()
    ru = normalize(current).lower()
    result: list[tuple[str, str, str]] = []

    increase_en = bool(re.search(r"\b(?:increase|increases|boost|boosts|raise|raises)\b", en))
    decrease_en = bool(re.search(r"\b(?:decrease|decreases|reduce|reduces|lowers|lowered|lowering)\b", en))
    increase_ru = bool(re.search(r"повыш|повыс|увелич|усил|укреп|\+\s*\{", ru))
    decrease_ru = bool(re.search(r"сниж|уменьш|ослаб|сокращ|-\s*\{", ru))
    if increase_en and decrease_ru and not increase_ru:
        result.append(("P5", "polarity_inversion", "English increases/boosts, Russian decreases/weakens"))
    elif increase_en and not increase_ru:
        result.append(("P3", "increase_term_missing", "No Russian increase/boost marker"))
    if decrease_en and increase_ru and not decrease_ru:
        result.append(("P5", "polarity_inversion", "English decreases/reduces, Russian increases/boosts"))
    elif decrease_en and not decrease_ru:
        result.append(("P3", "decrease_term_missing", "No Russian decrease/reduce marker"))

    concepts = [
        (r"\b(?:restore|restores|recover|recovers)\b", r"восстан|пополн|возвращ", "restore_term_missing"),
        (r"\b(?:heal|heals)\b", r"исцел|леч|восстан", "heal_term_missing"),
        (r"\b(?:remove|removes|dispel|dispels|cure|cures)\b", r"снима|устран|избав|леч|удал|лекар|исцел|рассе", "remove_term_missing"),
        (r"\b(?:chance|probability)\b", r"шанс|вероятн", "chance_term_missing"),
        (r"\b(?:for (?:\d+|\{[^}]+\}) turns?|next turn)\b", r"ход", "turn_term_missing"),
        (r"\b(?:physical|phys\.)\b", r"физичес|физ\.", "physical_term_missing"),
        (r"\b(?:magic|magical|mag\.)\b", r"маг", "magic_term_missing"),
        (r"\bignore(?:s)? (?:the )?(?:target's )?(?:defense|def)\b", r"игнор.*защит", "ignore_defense_missing"),
        (r"\b(?:always hits|cannot miss|never misses)\b", r"всегда попада|не промах|без промаха", "accuracy_guarantee_missing"),
    ]
    for en_pattern, ru_pattern, issue in concepts:
        if re.search(en_pattern, en) and not re.search(ru_pattern, ru):
            result.append(("P3", issue, f"Missing Russian semantic marker for {en_pattern}"))

    all_allies_en = bool(re.search(r"\b(?:all allies|all party members|entire party)\b", en))
    all_enemies_en = bool(re.search(r"\b(?:all enemies|all foes)\b", en))
    allies_ru = bool(re.search(r"вс(?:е|ех|ем|ей) союз|всей групп|всей команд", ru))
    enemies_ru = bool(re.search(r"вс(?:е|ех|ем) враг|всех противник", ru))
    if all_allies_en and enemies_ru and not allies_ru:
        result.append(("P5", "target_inversion", "English targets all allies, Russian targets enemies"))
    elif all_allies_en and not allies_ru:
        result.append(("P3", "all_allies_marker_missing", "No Russian all-allies marker"))
    if all_enemies_en and allies_ru and not enemies_ru:
        result.append(("P5", "target_inversion", "English targets all enemies, Russian targets allies"))
    elif all_enemies_en and not enemies_ru:
        result.append(("P3", "all_enemies_marker_missing", "No Russian all-enemies marker"))

    return result


def main() -> None:
    findings: list[dict[str, str]] = []
    linked: list[tuple[str, str, str, str, str, str]] = []
    rows_scanned = 0
    rows_linked = 0

    for package_root in sorted(path for path in CSV_ROOT.iterdir() if path.is_dir()):
        for path in sorted((package_root / "text").rglob("000_Sheet1.csv")):
            relative = path.relative_to(package_root).as_posix()
            if not FILE_RE.search(relative):
                continue
            source_path = SOURCE_ROOT / package_root.name / "csv" / relative
            if not source_path.exists():
                continue
            with path.open("r", encoding="utf-8-sig", newline="") as handle:
                current_rows = {row[0]: row[1] for row in csv.reader(handle) if len(row) >= 2}
            with source_path.open("r", encoding="utf-8-sig", newline="") as handle:
                source_rows = {row[0]: row[1] for row in csv.reader(handle) if len(row) >= 2}

            for row_id, current in current_rows.items():
                if row_id.startswith("string") or not current.strip():
                    continue
                rows_scanned += 1
                source = source_rows.get(row_id)
                if source is None or not source.strip():
                    continue
                rows_linked += 1
                linked.append((family(relative), normalize(source), package_root.name, relative, row_id, normalize(current)))

                include_roman = bool(re.search(r"(?:name|ruby).*\.mbe/", relative, re.IGNORECASE))
                source_numbers = numbers(source, include_roman)
                current_numbers = numbers(current, include_roman)
                if source_numbers != current_numbers:
                    add(
                        findings,
                        "P5",
                        "number_mismatch",
                        package_root.name,
                        relative,
                        row_id,
                        source,
                        current,
                        f"source={source_numbers}; current={current_numbers}",
                    )

                source_controls = controls(source)
                current_controls = controls(current)
                if source_controls != current_controls:
                    add(
                        findings,
                        "P4",
                        "control_tag_mismatch",
                        package_root.name,
                        relative,
                        row_id,
                        source,
                        current,
                        f"source={source_controls}; current={current_controls}",
                    )

                for priority, issue, detail in semantic_checks(source, current):
                    add(findings, priority, issue, package_root.name, relative, row_id, source, current, detail)

    duplicate_groups: dict[tuple[str, str], list[tuple[str, str, str, str]]] = defaultdict(list)
    for file_family, source, package, relative, row_id, current in linked:
        if source:
            duplicate_groups[(file_family, source)].append((package, relative, row_id, current))
    for (_, source), values in duplicate_groups.items():
        checked_values = [value for value in values if (value[1], value[2]) not in DUPLICATE_EXCEPTIONS]
        translations = {value[3] for value in checked_values}
        if len(checked_values) < 2 or len(translations) < 2:
            continue
        sample = checked_values[0]
        detail = " | ".join(f"{package}:{row_id}={current}" for package, _, row_id, current in checked_values)
        add(findings, "P2", "duplicate_translation_mismatch", sample[0], sample[1], sample[2], source, sample[3], detail)

    findings.sort(key=lambda row: (-int(row["priority"][1:]), row["issue"], row["package"], row["file"], row["row_id"]))
    fields = ["priority", "issue", "package", "file", "row_id", "detail", "source_en", "current_ru"]
    with OUT.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(findings)

    counts = Counter(row["issue"] for row in findings)
    priorities = Counter(row["priority"] for row in findings)
    summary = [
        "Item and skill semantic audit v094",
        f"rows_scanned={rows_scanned}",
        f"rows_linked={rows_linked}",
        f"candidates={len(findings)}",
        "",
        "By priority:",
    ]
    summary.extend(f"- {name}: {count}" for name, count in sorted(priorities.items(), reverse=True))
    summary.extend(["", "By issue:"])
    summary.extend(f"- {name}: {count}" for name, count in counts.most_common())
    SUMMARY.write_text("\n".join(summary) + "\n", encoding="utf-8")
    print("\n".join(summary))


if __name__ == "__main__":
    main()

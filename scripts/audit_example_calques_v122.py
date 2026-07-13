#!/usr/bin/env python3
"""Audit all text for the literal patterns found in player screenshots."""

from __future__ import annotations

import csv
import re
from collections import Counter
from pathlib import Path

import audit_machine_translation_tail_v117 as base


ROOT = Path(__file__).resolve().parents[1]
OUT_CSV = ROOT / "exports" / "example_calque_audit_v122.csv"
OUT_SUMMARY = ROOT / "exports" / "example_calque_audit_v122_summary.txt"


def rx(pattern: str) -> re.Pattern[str]:
    return re.compile(pattern, re.I | re.S)


base.TARGET_RULES.extend(
    [
        base.PatternRule(92, "example_calque", "буквальное get this straight", rx(r"\bвнес(?:и|ите) ясность\b")),
        base.PatternRule(92, "example_calque", "буквальное nap on the clock", rx(r"\bдремать по часам\b")),
        base.PatternRule(90, "example_calque", "буквальное a whole situation", rx(r"\bцелая ситуация\b")),
        base.PatternRule(90, "example_calque", "калька how extremely cruel", rx(r"\bкак чрезвычайно жесток\w*\b")),
        base.PatternRule(90, "example_calque", "калька simply heartless", rx(r"\bпросто бессердечн(?:ый|ая|ое|ые)\b")),
        base.PatternRule(90, "example_calque", "буквальное should be able to", rx(r"\bдолжн\w+ быть в состоянии\b")),
        base.PatternRule(90, "example_calque", "буквальное it's not much, but here", rx(r"\bэто немного,? но здесь\b")),
        base.PatternRule(86, "example_calque", "буквальное I've got it from here", rx(r"\bдальше я сам\b")),
        base.PatternRule(84, "example_calque", "буквальное you're everywhere", rx(r"\bвы повсюду\b")),
        base.PatternRule(80, "example_calque", "буквальное get the help of", rx(r"\bполучить помощь\b"), frozenset({"dialogue", "digitter"})),
        base.PatternRule(90, "example_calque", "fellow ошибочно понят как парень", rx(r"\bпарень\s*-?\s*дигимон\b")),
        base.PatternRule(88, "example_calque", "буквальное costumes did all the work", rx(r"\bвс[её] сделали костюмы\b")),
        base.PatternRule(86, "example_calque", "had my eyes down переведено как опустил глаза", rx(r"\bопустил[аи]? глаза\b"), frozenset({"dialogue"})),
        base.PatternRule(88, "example_calque", "английское here переведено как здесь", rx(r"^\s*это немного,? но здесь[.!?…]*")),
    ]
)

base.SOURCE_RULES.extend(
    [
        base.SourceRule(96, "example_source_calque", "get this straight → внести ясность", rx(r"\bget this straight\b"), rx(r"\bвнес(?:и|ите) ясность\b")),
        base.SourceRule(96, "example_source_calque", "nap on the clock → дремать по часам", rx(r"\bnap on the clock\b"), rx(r"\bдремать по часам\b")),
        base.SourceRule(94, "example_source_calque", "a whole situation → целая ситуация", rx(r"\ba whole situation\b"), rx(r"\bцелая ситуация\b")),
        base.SourceRule(94, "example_source_calque", "extremely cruel переведено пословно", rx(r"\bextremely cruel\b"), rx(r"\bкак чрезвычайно жесток\w*\b")),
        base.SourceRule(94, "example_source_calque", "simply heartless переведено пословно", rx(r"\bsimply heartless\b"), rx(r"\bпросто бессердечн\w*\b")),
        base.SourceRule(94, "example_source_calque", "should be able to → быть в состоянии", rx(r"\bshould be able to\b"), rx(r"\bдолжн\w+ быть в состоянии\b")),
        base.SourceRule(94, "example_source_calque", "not much, but here переведено пословно", rx(r"\bnot much,? but here\b"), rx(r"\bэто немного,? но здесь\b")),
        base.SourceRule(92, "example_source_calque", "I've got it from here → дальше я сам", rx(r"\bi(?:'ve| have) got it from here\b"), rx(r"\bдальше я сам\b")),
        base.SourceRule(90, "example_source_calque", "you're everywhere → вы повсюду", rx(r"\byou(?:'re| are) everywhere\b"), rx(r"\bвы повсюду\b")),
        base.SourceRule(88, "example_source_calque", "get the help of → получить помощь", rx(r"\bget the help of\b"), rx(r"\bполучить помощь\b")),
        base.SourceRule(96, "example_source_calque", "fellow Digimon ошибочно понят как парень", rx(r"\bfellow digimon\b"), rx(r"\bпарень\s*-?\s*дигимон\b")),
        base.SourceRule(94, "example_source_calque", "costumes did all the work переведено пословно", rx(r"\bcostumes did all the work\b"), rx(r"\bвс[её] сделали костюмы\b")),
        base.SourceRule(92, "example_source_calque", "had my eyes down → опустил глаза", rx(r"\bhad my eyes down\b"), rx(r"\bопустил[аи]? глаза\b")),
        base.SourceRule(92, "example_source_calque", "Our gun battery оставлено обрывком", rx(r"^\s*our gun battery\.{3}\s*$"), rx(r"^\s*наш\w* (?:орудийн\w*|артиллерийск\w*) батаре\w*\.{3}\s*$")),
    ]
)


original_apply_target_rules = base.apply_target_rules


def apply_target_rules(entry: base.Entry) -> None:
    original_apply_target_rules(entry)
    skill_table = entry.relative.endswith(
        (
            "skill_name.mbe/000_Sheet1.csv",
            "skill_ruby.mbe/000_Sheet1.csv",
            "jogress_skill_name.mbe/000_Sheet1.csv",
        )
    )
    source_tier = re.search(r" (I|II|III)$", entry.en)
    if skill_table and source_tier and not entry.ru.endswith(f" {source_tier.group(1)}"):
        base.add_issue(
            entry,
            98,
            "tier_numeral",
            "римская ступень навыка переведена или потеряна",
            f"EN={entry.en} | RU={entry.ru}",
        )


base.apply_target_rules = apply_target_rules


def main() -> None:
    entries, coverage = base.load_entries()
    rows = base.audit_entries(entries)
    base.write_csv(
        OUT_CSV,
        rows,
        [
            "priority", "score", "confidence", "categories", "reasons", "evidence",
            "scope", "package", "file", "line", "key", "speaker", "source_en",
            "current_ru", "previous_ru", "next_ru",
        ],
    )
    priorities = Counter(str(row["priority"]) for row in rows)
    examples = [
        row
        for row in rows
        if "example_calque" in str(row["categories"])
        or "example_source_calque" in str(row["categories"])
        or "tier_numeral" in str(row["categories"])
    ]
    with OUT_SUMMARY.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write("Example-driven machine-translation audit v122\n")
        handle.write(f"rows_checked={coverage['rows']}\n")
        handle.write(f"source_aligned={coverage['rows_with_source']}\n")
        handle.write(f"all_candidates={len(rows)}\n")
        handle.write(f"example_pattern_candidates={len(examples)}\n")
        for priority in ("P1", "P2", "P3", "P4"):
            handle.write(f"{priority}={priorities[priority]}\n")
        handle.write(f"report={OUT_CSV.relative_to(ROOT)}\n")
    print(OUT_SUMMARY.read_text(encoding="utf-8"), end="")


if __name__ == "__main__":
    main()

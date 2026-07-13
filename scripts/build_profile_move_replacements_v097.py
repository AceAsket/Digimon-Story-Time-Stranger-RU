#!/usr/bin/env python3
"""Suggest exact profile move-name replacements with confidence scores."""

from __future__ import annotations

import csv
import re
from collections import defaultdict
from difflib import SequenceMatcher
from functools import lru_cache
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "exports/profile_move_name_audit_v096.csv"
OUT = ROOT / "exports/profile_move_replacement_suggestions_v097.csv"
SUMMARY = ROOT / "exports/profile_move_replacement_suggestions_v097_summary.txt"
CSV_ROOT = ROOT / "csv"

QUOTE_RE = re.compile(r"«([^»\n]{2,100})»")
NON_LETTER_RE = re.compile(r"[^a-zа-яё0-9]+", re.I)

CYR_TO_LAT = str.maketrans(
    {
        "а": "a", "б": "b", "в": "v", "г": "g", "д": "d", "е": "e", "ё": "e",
        "ж": "zh", "з": "z", "и": "i", "й": "y", "к": "k", "л": "l", "м": "m",
        "н": "n", "о": "o", "п": "p", "р": "r", "с": "s", "т": "t", "у": "u",
        "ф": "f", "х": "h", "ц": "ts", "ч": "ch", "ш": "sh", "щ": "shch",
        "ъ": "", "ы": "y", "ь": "", "э": "e", "ю": "yu", "я": "ya",
    }
)


def normalize(value: str) -> str:
    return NON_LETTER_RE.sub(" ", value.casefold()).strip()


def latinize(value: str) -> str:
    return normalize(value).translate(CYR_TO_LAT)


def score_pair(source_move: str, approved: str, quote: str) -> float:
    source_score = SequenceMatcher(None, normalize(source_move), latinize(quote)).ratio()
    approved_score = SequenceMatcher(None, normalize(approved), normalize(quote)).ratio()
    return max(source_score, approved_score)


def confidence(score: float, margin: float) -> str:
    if score >= 0.78 and margin >= 0.08:
        return "high"
    if score >= 0.62 and margin >= 0.04:
        return "medium"
    return "low"


def approved_quote_names() -> set[str]:
    result: set[str] = set()
    for package_root in sorted(path for path in CSV_ROOT.iterdir() if path.is_dir()):
        for pattern in ("skill_name*.mbe/000_Sheet1.csv", "jogress_skill_name*.mbe/000_Sheet1.csv"):
            for path in (package_root / "text").glob(pattern):
                with path.open("r", encoding="utf-8-sig", newline="") as handle:
                    for row in csv.reader(handle):
                        if len(row) >= 2 and row[1].strip():
                            result.add(normalize(row[1]))
    return result


def ordered_alignment(rows: list[dict[str, str]], quotes: list[str]) -> list[tuple[int, int, float, float]]:
    scores: list[list[float]] = []
    margins: list[float] = []
    for row in rows:
        approved = row["approved_ru"].split(" | ")[0]
        row_scores = [score_pair(row["source_move"], approved, quote) for quote in quotes]
        ranked = sorted(row_scores, reverse=True)
        margins.append((ranked[0] - ranked[1]) if len(ranked) > 1 else (ranked[0] if ranked else 0.0))
        scores.append(row_scores)

    @lru_cache(maxsize=None)
    def solve(row_index: int, quote_index: int) -> tuple[float, tuple[tuple[int, int], ...]]:
        if row_index >= len(rows) or quote_index >= len(quotes):
            return 0.0, ()
        options = [solve(row_index + 1, quote_index), solve(row_index, quote_index + 1)]
        pair_score = scores[row_index][quote_index]
        if pair_score >= 0.25:
            tail_score, tail_pairs = solve(row_index + 1, quote_index + 1)
            options.append((tail_score + pair_score + 0.10, ((row_index, quote_index),) + tail_pairs))
        return max(options, key=lambda item: (item[0], len(item[1])))

    _, pairs = solve(0, 0)
    return [(row_index, quote_index, scores[row_index][quote_index], margins[row_index]) for row_index, quote_index in pairs]


def main() -> None:
    with AUDIT.open("r", encoding="utf-8-sig", newline="") as handle:
        candidates = list(csv.DictReader(handle))
    approved_names = approved_quote_names()

    groups: dict[tuple[str, str, str], list[dict[str, str]]] = defaultdict(list)
    for row in candidates:
        groups[(row["package"], row["file"], row["row_id"])].append(row)

    output: list[dict[str, str]] = []
    for (package, relative, row_id), rows in sorted(groups.items()):
        rows.sort(key=lambda row: row["source_en"].casefold().find(row["source_move"].casefold()))
        current = rows[0]["current_ru"]
        quotes = [
            match.group(1)
            for match in QUOTE_RE.finditer(current)
            if normalize(match.group(1)) not in approved_names
        ]
        exact_rows: set[int] = set()

        for index, row in enumerate(rows):
            source_move = row["source_move"]
            approved = row["approved_ru"].split(" | ")[0]
            if re.search(r"(?<![A-Za-z])" + re.escape(source_move) + r"(?![A-Za-z])", current, re.I):
                output.append(
                    {
                        "confidence": "high",
                        "score": "1.000",
                        "margin": "1.000",
                        "package": package,
                        "file": relative,
                        "row_id": row_id,
                        "source_move": source_move,
                        "approved_ru": approved,
                        "current_fragment": source_move,
                        "replacement": approved,
                        "basis": "exact_english_retained",
                        "current_ru": current,
                    }
                )
                exact_rows.add(index)

        remaining = [row for index, row in enumerate(rows) if index not in exact_rows]
        assigned_rows: set[int] = set()
        for row_index, quote_index, score, margin in ordered_alignment(remaining, quotes):
            row = remaining[row_index]
            approved = row["approved_ru"].split(" | ")[0]
            quote = quotes[quote_index]
            output.append(
                {
                    "confidence": confidence(score, margin),
                    "score": f"{score:.3f}",
                    "margin": f"{margin:.3f}",
                    "package": package,
                    "file": relative,
                    "row_id": row_id,
                    "source_move": row["source_move"],
                    "approved_ru": approved,
                    "current_fragment": quote,
                    "replacement": approved,
                    "basis": "quoted_name_similarity",
                    "current_ru": current,
                }
            )
            assigned_rows.add(row_index)

        for row_index, row in enumerate(remaining):
            if row_index in assigned_rows:
                continue
            output.append(
                {
                    "confidence": "low",
                    "score": "0.000",
                    "margin": "0.000",
                    "package": package,
                    "file": relative,
                    "row_id": row_id,
                    "source_move": row["source_move"],
                    "approved_ru": row["approved_ru"].split(" | ")[0],
                    "current_fragment": "",
                    "replacement": row["approved_ru"].split(" | ")[0],
                    "basis": "no_unambiguous_fragment",
                    "current_ru": current,
                }
            )

    order = {"high": 0, "medium": 1, "low": 2}
    output.sort(key=lambda row: (order[row["confidence"]], -float(row["score"]), row["package"], row["row_id"], row["source_move"]))
    fields = [
        "confidence", "score", "margin", "package", "file", "row_id", "source_move",
        "approved_ru", "current_fragment", "replacement", "basis", "current_ru",
    ]
    with OUT.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(output)

    counts = {name: sum(row["confidence"] == name for row in output) for name in ("high", "medium", "low")}
    summary = [
        "Profile move replacement suggestions v097",
        f"candidates={len(output)}",
        f"high={counts['high']}",
        f"medium={counts['medium']}",
        f"low={counts['low']}",
        f"report={OUT.relative_to(ROOT)}",
    ]
    SUMMARY.write_text("\n".join(summary) + "\n", encoding="utf-8")
    print("\n".join(summary))


if __name__ == "__main__":
    main()

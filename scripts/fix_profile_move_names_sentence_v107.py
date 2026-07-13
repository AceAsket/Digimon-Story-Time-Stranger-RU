#!/usr/bin/env python3
"""Align remaining profile move names by source/translation sentence order."""

from __future__ import annotations

import csv
import re
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CSV_ROOT = ROOT / "csv"
AUDIT = ROOT / "exports/profile_move_name_audit_v096.csv"
MANIFEST = ROOT / "exports/profile_move_replacements_sentence_v107.csv"
QUOTE_RE = re.compile(r"«([^»\n]{2,100})»")
EN_QUOTE_RE = re.compile(r'"([^"\n]{2,100})"')
SENTENCE_RE = re.compile(r"(?<=[.!?])\s+")
FIELDS = [
    "package", "file", "row_id", "source_move", "approved_ru",
    "old", "expected_count", "source_sentence", "current_sentence",
]


def flatten(text: str) -> str:
    return " ".join(text.split())


def split_sentences(text: str) -> list[str]:
    return [part.strip() for part in SENTENCE_RE.split(flatten(text)) if part.strip()]


def flexible_quote_pattern(value: str) -> re.Pattern[str]:
    pieces = [re.escape(piece) for piece in value.split()]
    return re.compile(r"«" + r"\s+".join(pieces) + r"»")


def current_rows(package: str, relative: str) -> dict[str, str]:
    path = CSV_ROOT / package / relative
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return {row[0]: row[1] for row in csv.reader(handle) if len(row) >= 2}


def build_manifest() -> list[dict[str, str]]:
    with AUDIT.open("r", encoding="utf-8-sig", newline="") as handle:
        candidates = list(csv.DictReader(handle))
    groups: dict[tuple[str, str, str], list[dict[str, str]]] = defaultdict(list)
    for row in candidates:
        groups[(row["package"], row["file"], row["row_id"])].append(row)

    cache: dict[tuple[str, str], dict[str, str]] = {}
    manifest: list[dict[str, str]] = []
    for (package, relative, row_id), rows in sorted(groups.items()):
        source_sentences = split_sentences(rows[0]["source_en"])
        current_sentences = split_sentences(rows[0]["current_ru"])
        if len(source_sentences) != len(current_sentences):
            continue

        candidates_by_sentence: dict[int, list[dict[str, str]]] = defaultdict(list)
        for row in rows:
            # Exact case is intentional: it rejects generic lowercase phrases such as
            # "energy bomb" that only happen to equal a title-cased skill-table name.
            sentence_index = next(
                (index for index, sentence in enumerate(source_sentences) if row["source_move"] in sentence),
                None,
            )
            if sentence_index is not None:
                candidates_by_sentence[sentence_index].append(row)

        for sentence_index, sentence_rows in sorted(candidates_by_sentence.items()):
            source_sentence = source_sentences[sentence_index]
            current_sentence = current_sentences[sentence_index]
            events: list[tuple[int, str, object]] = []
            for row in sentence_rows:
                events.append((source_sentence.index(row["source_move"]), "move", row))
            for match in EN_QUOTE_RE.finditer(source_sentence):
                events.append((match.start(), "literal_quote", match.group(1)))
            events.sort(key=lambda event: event[0])
            current_quotes = [match.group(1) for match in QUOTE_RE.finditer(current_sentence)]
            if len(events) != len(current_quotes):
                continue

            key = (package, relative)
            if key not in cache:
                cache[key] = current_rows(package, relative)
            full_current = cache[key].get(row_id)
            if full_current is None:
                raise SystemExit(f"Missing profile row: {package}:{relative}:{row_id}")

            for event_index, (_, kind, payload) in enumerate(events):
                if kind != "move":
                    continue
                row = payload
                assert isinstance(row, dict)
                old = current_quotes[event_index]
                approved = row["approved_ru"].split(" | ")[0]
                if old == approved:
                    continue
                pattern = flexible_quote_pattern(old)
                count = len(pattern.findall(full_current))
                if count < 1:
                    raise SystemExit(
                        f"Aligned quote missing from row: {package}:{relative}:{row_id}:{old!r}"
                    )
                manifest.append(
                    {
                        "package": package,
                        "file": relative,
                        "row_id": row_id,
                        "source_move": row["source_move"],
                        "approved_ru": approved,
                        "old": old,
                        "expected_count": str(count),
                        "source_sentence": source_sentence,
                        "current_sentence": current_sentence,
                    }
                )

    identities = [(row["package"], row["row_id"], row["source_move"]) for row in manifest]
    if len(identities) != len(set(identities)):
        raise SystemExit("Duplicate sentence-aligned move identity in manifest.")
    if len(manifest) != 73:
        raise SystemExit(f"Reviewed sentence-alignment baseline changed: expected 73, got {len(manifest)}")

    with MANIFEST.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(manifest)
    return manifest


def read_manifest() -> list[dict[str, str]]:
    if not MANIFEST.exists():
        return build_manifest()
    with MANIFEST.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def main() -> None:
    manifest = read_manifest()
    grouped: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in manifest:
        grouped[(row["package"], row["file"])].append(row)

    changed = 0
    already_current = 0
    for (package, relative), updates in sorted(grouped.items()):
        path = CSV_ROOT / package / relative
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.reader(handle))
        by_id = {row[0]: row for row in rows if len(row) >= 2}
        file_changed = False
        for update in updates:
            row = by_id.get(update["row_id"])
            if row is None:
                raise SystemExit(f"Missing profile row: {package}:{relative}:{update['row_id']}")
            old_pattern = flexible_quote_pattern(update["old"])
            new_pattern = flexible_quote_pattern(update["approved_ru"])
            expected = int(update["expected_count"])
            old_count = len(old_pattern.findall(row[1]))
            if old_count == expected:
                row[1] = old_pattern.sub(f"«{update['approved_ru']}»", row[1])
                changed += expected
                file_changed = True
            elif old_count == 0 and len(new_pattern.findall(row[1])) >= expected:
                already_current += expected
            else:
                raise SystemExit(
                    f"Ambiguous sentence replacement {package}:{relative}:{update['row_id']}: "
                    f"{update['old']!r} count={old_count}, expected={expected}"
                )
        if file_changed:
            with path.open("w", encoding="utf-8-sig", newline="") as handle:
                csv.writer(handle, lineterminator="\n").writerows(rows)

    print(f"Sentence-aligned replacements: {len(manifest)}")
    print(f"Changed occurrences: {changed}")
    print(f"Already current occurrences: {already_current}")
    print(f"Manifest: {MANIFEST.relative_to(ROOT)}")


if __name__ == "__main__":
    main()

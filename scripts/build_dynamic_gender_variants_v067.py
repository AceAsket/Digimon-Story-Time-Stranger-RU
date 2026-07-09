#!/usr/bin/env python3
"""Create the minimal runtime M/F rows and the Lua resolver map.

The reviewed source list uses protagonist-oriented columns.  Runtime row
suffixes, however, describe the gender of the speaking role: ``__H`` for a
male speaker and ``__F`` for a female speaker.  The Operator is the opposite
gender to the protagonist, so its texts and Lua mapping are intentionally
inverted.

Player answers shown by MessageTalkSel are stored as a contiguous run of rows.
The game receives only the first ID of that run.  For those answers this script
duplicates the complete run for each gender, changes only the reviewed row,
and maps the selection's first ID.  Direct messages receive two ordinary rows.
"""

from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATASET = ROOT / "exports" / "dynamic_gender_confirmed_variants_v066.csv"
DEFAULT_MAP = ROOT / "verify" / "lua_gender_hook" / "patched_source" / "gender_message_map.lua"
DEFAULT_MANIFEST = ROOT / "exports" / "dynamic_gender_runtime_manifest_v067.csv"

DATASET_FIELDS = (
    "package",
    "file",
    "base_id",
    "role",
    "male_protagonist_text",
    "female_protagonist_text",
    "confidence",
    "basis",
)


@dataclass(frozen=True)
class ReviewedVariant:
    package: str
    file: str
    base_id: str
    role: str
    male_protagonist_text: str
    female_protagonist_text: str
    confidence: str
    basis: str


@dataclass(frozen=True)
class RuntimeEntry:
    package: str
    file: str
    reviewed_id: str
    runtime_key: str
    role: str
    mode: str
    group_ids: tuple[str, ...]
    hero_id: str
    heroine_id: str


def read_csv_rows(path: Path) -> list[list[str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.reader(handle))
    bad = [(index + 1, len(row)) for index, row in enumerate(rows) if len(row) != 4]
    if bad:
        raise ValueError(f"{path}: expected four MBE columns; bad rows: {bad[:10]}")
    return rows


def write_csv_rows(path: Path, rows: list[list[str]]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        csv.writer(handle, lineterminator="\n").writerows(rows)


def read_dataset(path: Path) -> list[ReviewedVariant]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != DATASET_FIELDS:
            raise ValueError(
                f"{path}: unexpected columns {reader.fieldnames}; expected {DATASET_FIELDS}"
            )
        rows = [ReviewedVariant(**row) for row in reader]

    if not rows:
        raise ValueError(f"{path}: dataset is empty")
    seen: set[tuple[str, str, str]] = set()
    for row in rows:
        key = (row.package, row.file, row.base_id)
        if key in seen:
            raise ValueError(f"{path}: duplicate reviewed ID: {key}")
        seen.add(key)
        if row.role not in {"player", "operator"}:
            raise ValueError(f"{path}: unsupported role {row.role!r} for {row.base_id}")
        if not row.male_protagonist_text or not row.female_protagonist_text:
            raise ValueError(f"{path}: empty gender text for {row.base_id}")
        if row.male_protagonist_text == row.female_protagonist_text:
            raise ValueError(f"{path}: identical gender texts for {row.base_id}")
        if "digimon_chat" in row.file.lower():
            raise ValueError(f"{path}: unhooked Digimon Chat row leaked into production: {row.base_id}")
    return rows


def is_generated_id(message_id: str) -> bool:
    return message_id.endswith("__H") or message_id.endswith("__F")


def contiguous_same_speaker_group(rows: list[list[str]], target_index: int) -> tuple[int, int]:
    """Return the contiguous source block sharing the target's speaker.

    Only player rows can become selection groups.  Reviewed player choices in
    this build form three-row contiguous blocks; a one-row block is a direct
    message.  Generated rows are ignored because they are always appended.
    """

    speaker = rows[target_index][1]
    start = target_index
    while start > 0:
        candidate = rows[start - 1]
        if candidate[1] != speaker or is_generated_id(candidate[0]):
            break
        start -= 1
    end = target_index + 1
    while end < len(rows):
        candidate = rows[end]
        if candidate[1] != speaker or is_generated_id(candidate[0]):
            break
        end += 1
    return start, end


def variant_texts(reviewed: ReviewedVariant) -> tuple[str, str]:
    if reviewed.role == "player":
        return reviewed.male_protagonist_text, reviewed.female_protagonist_text
    # __H/__F describe the Operator's gender.  The Operator is opposite to the
    # selected protagonist, including lines whose grammar addresses the player.
    return reviewed.female_protagonist_text, reviewed.male_protagonist_text


def upsert_direct_rows(
    rows: list[list[str]],
    base_row: list[str],
    reviewed: ReviewedVariant,
) -> tuple[int, int]:
    text_h, text_f = variant_texts(reviewed)
    desired = {
        f"{reviewed.base_id}__H": [f"{reviewed.base_id}__H", base_row[1], text_h, base_row[3]],
        f"{reviewed.base_id}__F": [f"{reviewed.base_id}__F", base_row[1], text_f, base_row[3]],
    }
    created = updated = 0
    by_id = {row[0]: index for index, row in enumerate(rows)}
    for message_id, wanted in desired.items():
        index = by_id.get(message_id)
        if index is None:
            rows.append(wanted)
            created += 1
        elif rows[index] != wanted:
            rows[index] = wanted
            updated += 1
    return created, updated


def upsert_selection_rows(
    rows: list[list[str]],
    source_group: list[list[str]],
    reviewed: ReviewedVariant,
) -> tuple[int, int]:
    text_h, text_f = variant_texts(reviewed)
    created = updated = 0
    by_id = {row[0]: index for index, row in enumerate(rows)}
    for suffix, target_text in (("__H", text_h), ("__F", text_f)):
        for source in source_group:
            wanted = source.copy()
            wanted[0] = f"{source[0]}{suffix}"
            if source[0] == reviewed.base_id:
                wanted[2] = target_text
            index = by_id.get(wanted[0])
            if index is None:
                rows.append(wanted)
                by_id[wanted[0]] = len(rows) - 1
                created += 1
            elif rows[index] != wanted:
                rows[index] = wanted
                updated += 1
    return created, updated


def lua_quote(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def write_lua_map(path: Path, entries: list[RuntimeEntry]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "-- Generated by scripts/build_dynamic_gender_variants_v067.py.",
        "-- Do not edit by hand; edit the reviewed CSV and rebuild instead.",
        "return {",
    ]
    for entry in sorted(entries, key=lambda item: item.runtime_key):
        lines.append(
            f"  [{lua_quote(entry.runtime_key)}] = "
            f"{{ hero = {lua_quote(entry.hero_id)}, heroine = {lua_quote(entry.heroine_id)} }},"
        )
    lines.extend(("}", ""))
    path.write_text("\n".join(lines), encoding="utf-8", newline="\n")


def write_manifest(path: Path, entries: list[RuntimeEntry]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = (
        "package",
        "file",
        "reviewed_id",
        "runtime_key",
        "role",
        "mode",
        "group_ids",
        "hero_id",
        "heroine_id",
    )
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for entry in entries:
            writer.writerow(
                {
                    "package": entry.package,
                    "file": entry.file,
                    "reviewed_id": entry.reviewed_id,
                    "runtime_key": entry.runtime_key,
                    "role": entry.role,
                    "mode": entry.mode,
                    "group_ids": " ".join(entry.group_ids),
                    "hero_id": entry.hero_id,
                    "heroine_id": entry.heroine_id,
                }
            )


def validate_generated_rows(csv_path: Path, rows: list[list[str]], entries: list[RuntimeEntry]) -> None:
    positions: dict[str, list[int]] = defaultdict(list)
    for index, row in enumerate(rows):
        positions[row[0]].append(index)

    for entry in entries:
        suffixes = ("__H", "__F")
        for suffix in suffixes:
            expected = [f"{message_id}{suffix}" for message_id in entry.group_ids]
            for message_id in expected:
                found = positions.get(message_id, [])
                if len(found) != 1:
                    raise ValueError(
                        f"{csv_path}: expected one generated row {message_id}, found {len(found)}"
                    )
            if entry.mode == "selection_group":
                start = positions[expected[0]][0]
                actual = [row[0] for row in rows[start : start + len(expected)]]
                if actual != expected:
                    raise ValueError(
                        f"{csv_path}: selection rows are not contiguous/in order: "
                        f"expected {expected}, got {actual}"
                    )


def build(dataset_path: Path, map_path: Path, manifest_path: Path, check_only: bool) -> int:
    reviewed_rows = read_dataset(dataset_path)
    grouped: dict[Path, list[ReviewedVariant]] = defaultdict(list)
    for reviewed in reviewed_rows:
        grouped[ROOT / "csv" / reviewed.package / reviewed.file].append(reviewed)

    entries: list[RuntimeEntry] = []
    created_total = updated_total = 0
    runtime_keys: set[str] = set()

    for csv_path, variants in grouped.items():
        if not csv_path.is_file():
            raise FileNotFoundError(csv_path)
        rows = read_csv_rows(csv_path)
        source_rows = [row for row in rows if not is_generated_id(row[0])]
        source_index: dict[str, list[int]] = defaultdict(list)
        for index, row in enumerate(source_rows):
            source_index[row[0]].append(index)

        file_entries: list[RuntimeEntry] = []

        for reviewed in variants:
            indices = source_index.get(reviewed.base_id, [])
            if len(indices) != 1:
                raise ValueError(
                    f"{csv_path}: expected one source row for {reviewed.base_id}, found {len(indices)}"
                )
            target_index = indices[0]
            base_row = source_rows[target_index]
            if reviewed.role == "player" and base_row[1] != "char_PLAYER_M":
                raise ValueError(f"{csv_path}: unexpected player speaker for {reviewed.base_id}: {base_row[1]}")
            if reviewed.role == "operator" and base_row[1] != "char_OPERATOR_M":
                raise ValueError(f"{csv_path}: unexpected Operator speaker for {reviewed.base_id}: {base_row[1]}")

            start, end = contiguous_same_speaker_group(source_rows, target_index)
            group = source_rows[start:end]
            is_selection = reviewed.role == "player" and len(group) > 1
            if is_selection:
                if len(group) != 3 or not all("{next}" in row[2] for row in group):
                    # A handful of original selection rows omit {next}; the
                    # stable three-row structure is the authoritative check.
                    if len(group) != 3:
                        raise ValueError(
                            f"{csv_path}: ambiguous player group for {reviewed.base_id}: "
                            f"{[row[0] for row in group]}"
                        )
                runtime_key = group[0][0]
                group_ids = tuple(row[0] for row in group)
                created, updated = upsert_selection_rows(rows, group, reviewed)
                mode = "selection_group"
            else:
                runtime_key = reviewed.base_id
                group_ids = (reviewed.base_id,)
                created, updated = upsert_direct_rows(rows, base_row, reviewed)
                mode = "direct"

            if runtime_key in runtime_keys:
                raise ValueError(f"global Lua map collision for runtime key {runtime_key}")
            runtime_keys.add(runtime_key)

            if reviewed.role == "player":
                hero_id = f"{runtime_key}__H"
                heroine_id = f"{runtime_key}__F"
            else:
                hero_id = f"{runtime_key}__F"
                heroine_id = f"{runtime_key}__H"
            entry = RuntimeEntry(
                package=reviewed.package,
                file=reviewed.file,
                reviewed_id=reviewed.base_id,
                runtime_key=runtime_key,
                role=reviewed.role,
                mode=mode,
                group_ids=group_ids,
                hero_id=hero_id,
                heroine_id=heroine_id,
            )
            entries.append(entry)
            file_entries.append(entry)
            created_total += created
            updated_total += updated

        validate_generated_rows(csv_path, rows, file_entries)
        if not check_only:
            write_csv_rows(csv_path, rows)

    # A global resolver cannot safely distinguish duplicate IDs loaded from
    # different MBE files.  Check the complete production package, excluding
    # generated variants, before emitting the map.
    all_base_occurrences: dict[str, list[str]] = defaultdict(list)
    for csv_path in (ROOT / "csv" / "patch_text01" / "message").rglob("000_Sheet1.csv"):
        for row in read_csv_rows(csv_path):
            if not is_generated_id(row[0]):
                all_base_occurrences[row[0]].append(str(csv_path.relative_to(ROOT)))
    for key in runtime_keys:
        places = all_base_occurrences.get(key, [])
        if len(places) != 1:
            raise ValueError(f"global runtime key {key!r} occurs {len(places)} times: {places}")

    if not check_only:
        write_lua_map(map_path, entries)
        write_manifest(manifest_path, entries)

    selection_count = sum(entry.mode == "selection_group" for entry in entries)
    direct_count = len(entries) - selection_count
    print(f"Reviewed IDs: {len(entries)}")
    print(f"Runtime keys: {len(runtime_keys)} ({selection_count} selection groups, {direct_count} direct)")
    print(f"Variant rows created: {created_total}")
    print(f"Variant rows updated: {updated_total}")
    print(f"Mode: {'check' if check_only else 'apply'}")
    if not check_only:
        print(f"Lua map: {map_path}")
        print(f"Manifest: {manifest_path}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    parser.add_argument("--lua-map", type=Path, default=DEFAULT_MAP)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--check", action="store_true", help="validate without writing files")
    args = parser.parse_args(argv)
    try:
        return build(
            args.dataset.resolve(),
            args.lua_map.resolve(),
            args.manifest.resolve(),
            args.check,
        )
    except Exception as exc:  # fail closed in release scripts
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

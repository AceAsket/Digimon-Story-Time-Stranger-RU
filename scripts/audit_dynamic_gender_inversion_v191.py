from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path

from audit_operator_lines_v055 import (
    FEMALE_SELF_WORDS,
    MALE_SELF_WORDS,
    OPERATOR_IDS,
    WORD_RE,
    has_self_context,
    sentence_for_word,
    unpack_text,
)


ROOT = Path(__file__).resolve().parents[1]
CSV_ROOT = ROOT / "csv"
DATASET = ROOT / "exports" / "dynamic_gender_confirmed_variants_v066.csv"
MANIFEST = ROOT / "exports" / "dynamic_gender_runtime_manifest_v067.csv"
SUMMARY = ROOT / "exports" / "dynamic_gender_inversion_audit_v191_summary.txt"

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
MANIFEST_FIELDS = (
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
REQUIRED_RECHECK_IDS = {
    "m140_100_060",
    "m390_010_010",
    "m390_060_030",
}


def read_dicts(path: Path, fields: tuple[str, ...]) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != fields:
            raise ValueError(f"{path}: unexpected columns {reader.fieldnames}")
        return list(reader)


def read_mbe(path: Path) -> list[list[str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.reader(handle))
    bad = [(line, len(row)) for line, row in enumerate(rows, 1) if len(row) != 4]
    if bad:
        raise ValueError(f"{path}: expected four columns; bad rows: {bad[:10]}")
    return rows


def is_generated(message_id: str) -> bool:
    return message_id.endswith(("__H", "__F"))


def main() -> int:
    dataset = read_dicts(DATASET, DATASET_FIELDS)
    manifest = read_dicts(MANIFEST, MANIFEST_FIELDS)
    issues: list[str] = []

    dataset_keys = [(row["package"], row["file"], row["base_id"]) for row in dataset]
    manifest_keys = [
        (row["package"], row["file"], row["reviewed_id"]) for row in manifest
    ]
    if len(set(dataset_keys)) != len(dataset_keys):
        issues.append("duplicate key in reviewed dataset")
    if len(set(manifest_keys)) != len(manifest_keys):
        issues.append("duplicate key in runtime manifest")
    if set(dataset_keys) != set(manifest_keys):
        issues.append("reviewed dataset and runtime manifest contain different keys")

    present_ids = {row["base_id"] for row in dataset}
    missing_rechecks = sorted(REQUIRED_RECHECK_IDS - present_ids)
    if missing_rechecks:
        issues.append(f"required v191 recheck IDs missing: {missing_rechecks}")

    manifest_by_key = {
        (row["package"], row["file"], row["reviewed_id"]): row for row in manifest
    }
    mbe_cache: dict[Path, list[list[str]]] = {}
    desired_generated: dict[Path, set[str]] = defaultdict(set)

    for reviewed in dataset:
        key = (reviewed["package"], reviewed["file"], reviewed["base_id"])
        entry = manifest_by_key.get(key)
        if entry is None:
            continue
        if entry["role"] != reviewed["role"]:
            issues.append(f"{key}: role differs between dataset and manifest")

        runtime_key = entry["runtime_key"]
        if reviewed["role"] == "operator":
            expected_hero = f"{runtime_key}__F"
            expected_heroine = f"{runtime_key}__H"
            text_h = reviewed["female_protagonist_text"]
            text_f = reviewed["male_protagonist_text"]
        else:
            expected_hero = f"{runtime_key}__H"
            expected_heroine = f"{runtime_key}__F"
            text_h = reviewed["male_protagonist_text"]
            text_f = reviewed["female_protagonist_text"]
        if entry["hero_id"] != expected_hero or entry["heroine_id"] != expected_heroine:
            issues.append(
                f"{key}: wrong runtime mapping; got hero={entry['hero_id']} "
                f"heroine={entry['heroine_id']}"
            )

        csv_path = CSV_ROOT / reviewed["package"] / reviewed["file"]
        rows = mbe_cache.setdefault(csv_path, read_mbe(csv_path))
        positions: dict[str, list[list[str]]] = defaultdict(list)
        for row in rows[1:]:
            positions[row[0]].append(row)
        base_rows = positions.get(reviewed["base_id"], [])
        if len(base_rows) != 1:
            issues.append(f"{key}: expected one base row, found {len(base_rows)}")
            continue
        source_by_id = {
            row[0]: row for row in rows[1:] if not is_generated(row[0])
        }
        group_ids = tuple(filter(None, entry["group_ids"].split()))
        if not group_ids:
            issues.append(f"{key}: empty runtime group")
            continue

        for suffix, reviewed_text in (("__H", text_h), ("__F", text_f)):
            expected_ids = [f"{message_id}{suffix}" for message_id in group_ids]
            desired_generated[csv_path].update(expected_ids)
            actual_positions: list[int] = []
            for group_id, generated_id in zip(group_ids, expected_ids):
                source = source_by_id.get(group_id)
                generated_rows = positions.get(generated_id, [])
                if source is None or len(generated_rows) != 1:
                    issues.append(
                        f"{key}: source/generated row count failure for {generated_id}"
                    )
                    continue
                wanted = source.copy()
                wanted[0] = generated_id
                if group_id == reviewed["base_id"]:
                    wanted[2] = reviewed_text
                if generated_rows[0] != wanted:
                    issues.append(f"{key}: generated row is stale: {generated_id}")
                actual_positions.append(rows.index(generated_rows[0]))
            if entry["mode"] == "selection_group" and actual_positions:
                start = actual_positions[0]
                if actual_positions != list(range(start, start + len(actual_positions))):
                    issues.append(f"{key}: selection variants are not contiguous: {suffix}")

    production_packages = [
        path
        for path in CSV_ROOT.iterdir()
        if path.is_dir() and (path.name == "patch_text01" or path.name.startswith("addcont_"))
    ]
    actual_generated_count = 0
    for package_root in sorted(production_packages):
        message_root = package_root / "message"
        if not message_root.exists():
            continue
        for csv_path in sorted(message_root.rglob("000_Sheet1.csv")):
            rows = mbe_cache.setdefault(csv_path, read_mbe(csv_path))
            actual_ids = {row[0] for row in rows[1:] if is_generated(row[0])}
            actual_generated_count += len(actual_ids)
            stale = sorted(actual_ids - desired_generated.get(csv_path, set()))
            if stale:
                issues.append(f"{csv_path.relative_to(ROOT)}: stale generated IDs: {stale}")

    reviewed_operator_keys = {
        (row["package"], row["file"], row["base_id"])
        for row in dataset
        if row["role"] == "operator"
    }
    uncovered_operator_self: set[tuple[str, str, str]] = set()
    for package_root in sorted(production_packages):
        message_root = package_root / "message"
        if not message_root.exists():
            continue
        for csv_path in sorted(message_root.rglob("000_Sheet1.csv")):
            relative = csv_path.relative_to(package_root).as_posix()
            for row in read_mbe(csv_path)[1:]:
                if row[1] not in OPERATOR_IDS or is_generated(row[0]):
                    continue
                text = unpack_text(row[2])
                words = {word.lower() for word in WORD_RE.findall(text)}
                for marker in words & (MALE_SELF_WORDS | FEMALE_SELF_WORDS):
                    if has_self_context(sentence_for_word(text, marker)):
                        key = (package_root.name, relative, row[0])
                        if key not in reviewed_operator_keys:
                            uncovered_operator_self.add(key)
    for key in sorted(uncovered_operator_self):
        issues.append(f"uncovered gendered Operator self-form: {key}")

    role_counts: dict[str, int] = defaultdict(int)
    for row in dataset:
        role_counts[row["role"]] += 1
    selection_count = sum(row["mode"] == "selection_group" for row in manifest)
    direct_count = len(manifest) - selection_count
    summary = [
        "Dynamic gender inversion audit v191",
        f"reviewed_ids={len(dataset)}",
        f"manifest_ids={len(manifest)}",
        f"player={role_counts['player']}",
        f"operator={role_counts['operator']}",
        f"player_address={role_counts['player_address']}",
        f"selection_groups={selection_count}",
        f"direct_messages={direct_count}",
        f"generated_rows={actual_generated_count}",
        f"issues={len(issues)}",
    ]
    if issues:
        summary.extend(("", "Issues:", *(f"- {issue}" for issue in issues)))
    SUMMARY.write_text("\n".join(summary) + "\n", encoding="utf-8")
    print("\n".join(summary))
    if issues:
        for issue in issues:
            print(f"ERROR: {issue}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

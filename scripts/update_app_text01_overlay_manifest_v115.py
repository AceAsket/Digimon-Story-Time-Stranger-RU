#!/usr/bin/env python3
"""Add/check app_text01 overlay entries for patch rows changed since a release.

This is an explicit maintenance tool, not an automatic broad copy operation.
It compares row values in the current ``csv/patch_text01`` with a Git release,
then considers only those changed addresses which also exist in an unpacked
``app_text01``.  ``--update`` adds the missing addresses with the exact hash of
their current app value.  Without ``--update`` it is a fail-closed coverage
check suitable for review before a release.
"""

from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
from pathlib import Path

from apply_app_text01_overlay_v115 import (
    Address,
    canonical_value,
    compute_table_guard,
    value_sha256,
)


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PATCH_ROOT = ROOT / "csv/patch_text01"
DEFAULT_MANIFEST = ROOT / "assets/app_text01_overlay/manifest_v115.json"


def read_rows(path: Path) -> list[list[str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.reader(handle))


def parse_rows(data: bytes) -> list[list[str]]:
    text = data.decode("utf-8-sig")
    return list(csv.reader(text.splitlines(keepends=True)))


def index_rows(rows: list[list[str]], label: str) -> dict[str, list[str]]:
    result: dict[str, list[str]] = {}
    for row in rows:
        if not row:
            continue
        if row[0] in result:
            raise RuntimeError(f"{label}: duplicate row ID {row[0]!r}")
        result[row[0]] = row
    return result


def git_blob(ref: str, repo_relative: str) -> bytes | None:
    result = subprocess.run(
        ["git", "show", f"{ref}:{repo_relative}"],
        cwd=ROOT,
        capture_output=True,
    )
    if result.returncode == 0:
        return result.stdout
    missing_markers = (b"does not exist", b"exists on disk, but not in", b"Path '")
    if any(marker in result.stderr for marker in missing_markers):
        return None
    raise RuntimeError(
        f"git show failed for {ref}:{repo_relative}: "
        + result.stderr.decode("utf-8", errors="replace")[-1000:]
    )


def address_key(entry: dict[str, object]) -> tuple[str, str, str, int]:
    return (
        str(entry["section"]),
        str(entry["table"]),
        str(entry["row_id"]),
        int(entry["column"]),
    )


def changed_app_addresses(
    app_root: Path,
    patch_root: Path,
    baseline_ref: str,
) -> list[tuple[tuple[str, str, str, int], str, str]]:
    result: list[tuple[tuple[str, str, str, int], str, str]] = []
    for current_path in sorted(patch_root.rglob("*.csv")):
        relative = current_path.relative_to(patch_root)
        if relative.parts[0] not in {"message", "text"}:
            continue
        app_path = app_root / relative
        if not app_path.is_file():
            continue
        repo_relative = current_path.relative_to(ROOT).as_posix()
        baseline_data = git_blob(baseline_ref, repo_relative)

        # Row zero is the MBE schema header, not a localizable address.  A
        # table or row added after the baseline is still a changed overlap and
        # must not escape coverage merely because it has no baseline row.
        current = index_rows(read_rows(current_path)[1:], str(current_path))
        baseline = (
            index_rows(
                parse_rows(baseline_data)[1:],
                f"{baseline_ref}:{repo_relative}",
            )
            if baseline_data is not None
            else {}
        )
        app = index_rows(read_rows(app_path)[1:], str(app_path))
        column = 2 if relative.parts[0] == "message" else 1
        table = Path(*relative.parts[1:]).as_posix()

        for row_id in sorted(current.keys() & app.keys()):
            current_row = current[row_id]
            app_row = app[row_id]
            if min(len(current_row), len(app_row)) <= column:
                continue
            target = canonical_value(current_row[column])
            baseline_row = baseline.get(row_id)
            if (
                baseline_row is not None
                and len(baseline_row) > column
                and target == canonical_value(baseline_row[column])
            ):
                continue
            app_value = canonical_value(app_row[column])
            key = (relative.parts[0], table, row_id, column)
            result.append((key, app_value, target))
    return result


def all_app_tables(app_root: Path) -> list[tuple[str, str, Path]]:
    result: list[tuple[str, str, Path]] = []
    for path in sorted(app_root.rglob("*.csv")):
        relative = path.relative_to(app_root)
        if not relative.parts or relative.parts[0] not in {"message", "text"}:
            continue
        table = Path(*relative.parts[1:]).as_posix()
        result.append((relative.parts[0], table, path))
    return result


def expected_table_guards(
    app_root: Path,
    manifest: dict[str, object],
) -> list[dict[str, object]]:
    targeted_by_table: dict[tuple[str, str], set[tuple[str, int]]] = {}
    for kind in ("shared", "app_only"):
        entries = manifest.get(kind)
        if not isinstance(entries, list):
            raise RuntimeError(f"Manifest {kind} field must be an array")
        for raw in entries:
            if not isinstance(raw, dict):
                raise RuntimeError(f"Manifest {kind} entry must be an object")
            address = Address(
                str(raw["section"]),
                str(raw["table"]),
                str(raw["row_id"]),
                int(raw["column"]),
            )
            targeted_by_table.setdefault(
                (address.section, address.table), set()
            ).add((address.row_id, address.column))

    result: list[dict[str, object]] = []
    for section, table, path in all_app_tables(app_root):
        guard = compute_table_guard(
            read_rows(path),
            section,
            table,
            targeted_by_table.get((section, table), set()),
        )
        result.append(
            {
                "section": guard.section,
                "table": guard.table,
                "row_count": guard.row_count,
                "structure_sha256": guard.structure_sha256,
                "untargeted_sha256": guard.untargeted_sha256,
            }
        )
    return result


def guard_key(entry: dict[str, object]) -> tuple[str, str]:
    return str(entry["section"]), str(entry["table"])


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--app-csv-root", type=Path, required=True)
    parser.add_argument("--patch-root", type=Path, default=DEFAULT_PATCH_ROOT)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--baseline-ref", default="v0.1.50")
    parser.add_argument("--update", action="store_true")
    args = parser.parse_args(sys.argv[1:] if argv is None else argv)

    manifest = json.loads(args.manifest.read_text(encoding="utf-8-sig"))
    shared = manifest.get("shared")
    if not isinstance(shared, list):
        raise RuntimeError("Manifest shared field must be an array")
    existing = {address_key(entry): entry for entry in shared}
    changed = changed_app_addresses(
        args.app_csv_root.resolve(),
        args.patch_root.resolve(),
        args.baseline_ref,
    )

    missing: list[tuple[tuple[str, str, str, int], str, str]] = []
    invalid: list[str] = []
    refreshed = 0
    for key, app_value, target in changed:
        entry = existing.get(key)
        if entry is None:
            missing.append((key, app_value, target))
            continue
        old_hash = str(entry.get("old_sha256", "")).lower()
        if canonical_value(app_value) == canonical_value(target):
            continue
        if value_sha256(app_value) != old_hash:
            if args.update:
                entry["old_sha256"] = value_sha256(app_value)
                refreshed += 1
                continue
            invalid.append(
                f"{'/'.join(key[:2])}:{key[2]}[{key[3]}]: "
                f"app_sha256={value_sha256(app_value)} manifest_old={old_hash}"
            )

    if invalid:
        raise SystemExit("Existing manifest entries reject current app values:\n" + "\n".join(invalid))

    if args.update and missing:
        for key, app_value, _target in missing:
            section, table, row_id, column = key
            shared.append(
                {
                    "section": section,
                    "table": table,
                    "row_id": row_id,
                    "column": column,
                    "old_sha256": value_sha256(app_value),
                }
            )
        shared.sort(key=address_key)
        print(f"Added {len(missing)} shared app_text01 overlay address(es).")
        missing = []

    expected_guards = expected_table_guards(args.app_csv_root.resolve(), manifest)
    raw_guards = manifest.get("table_guards")
    if not isinstance(raw_guards, list):
        raw_guards = []
    expected_guard_map = {guard_key(entry): entry for entry in expected_guards}
    actual_guard_map = {
        guard_key(entry): entry
        for entry in raw_guards
        if isinstance(entry, dict) and "section" in entry and "table" in entry
    }
    guard_missing = sorted(set(expected_guard_map) - set(actual_guard_map))
    guard_extra = sorted(set(actual_guard_map) - set(expected_guard_map))
    guard_changed = sorted(
        key
        for key in set(expected_guard_map) & set(actual_guard_map)
        if expected_guard_map[key] != actual_guard_map[key]
    )

    if args.update:
        manifest["table_guards"] = expected_guards
        args.manifest.write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        if refreshed:
            print(f"Refreshed {refreshed} accepted old app value hash(es).")
        print(f"Refreshed {len(expected_guards)} complete app table guard(s).")
        guard_missing = []
        guard_extra = []
        guard_changed = []

    print(f"changed_app_overlap={len(changed)}")
    print(f"manifest_shared={len(shared)}")
    print(f"missing={len(missing)}")
    print(f"table_guards={len(expected_guards)}")
    print(
        "table_guard_issues="
        f"{len(guard_missing) + len(guard_extra) + len(guard_changed)}"
    )
    if missing:
        for key, _app_value, _target in missing:
            print(f"missing: {'/'.join(key[:2])}:{key[2]}[{key[3]}]")
        raise SystemExit("Manifest does not cover every changed patch row present in app_text01.")
    if guard_missing or guard_extra or guard_changed:
        for section, table in guard_missing[:20]:
            print(f"missing table guard: {section}/{table}")
        for section, table in guard_extra[:20]:
            print(f"obsolete table guard: {section}/{table}")
        for section, table in guard_changed[:20]:
            print(f"changed table guard: {section}/{table}")
        raise SystemExit(
            "Manifest table guards do not match unpacked app_text01; "
            "review the source and run again with --update."
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

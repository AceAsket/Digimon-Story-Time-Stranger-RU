#!/usr/bin/env python3
"""Apply the small, guarded Russian overlay to an unpacked ``app_text01``.

The main translation lives in ``patch_text01``.  ``app_text01`` nevertheless
contains a few UI rows which the game can read directly, plus a small number of
rows which do not exist in the patch package.  Copying an entire patch table
over an app table is unsafe because it drops app-only rows and can change the
table topology.  This tool therefore changes only addresses explicitly listed
in ``assets/app_text01_overlay/manifest_v115.json``.

For a shared row, the target value is read from the current patch CSV.  The
manifest stores the hash of the one accepted old app value.  For an app-only
row, both the accepted old hash and the target value are explicit.  Re-running
the tool is safe: either the accepted old value or the already-applied target
is allowed; every third value fails closed.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / "assets/app_text01_overlay/manifest_v115.json"
DEFAULT_PATCH_ROOT = ROOT / "csv/patch_text01"
ALLOWED_SECTIONS = frozenset({"message", "text"})


def canonical_value(value: str) -> str:
    """Use semantic line endings for hashes and equality checks."""

    return value.replace("\r\n", "\n").replace("\r", "\n")


def value_sha256(value: str) -> str:
    return hashlib.sha256(canonical_value(value).encode("utf-8")).hexdigest()


@dataclass(frozen=True, order=True)
class Address:
    section: str
    table: str
    row_id: str
    column: int

    @property
    def relative_path(self) -> Path:
        return Path(self.section) / Path(*PurePosixPath(self.table).parts)

    @property
    def label(self) -> str:
        return f"{self.section}/{self.table}:{self.row_id}[{self.column}]"


@dataclass(frozen=True)
class Entry:
    address: Address
    old_sha256: str
    target: str | None
    kind: str


@dataclass(frozen=True, order=True)
class TableGuard:
    section: str
    table: str
    row_count: int
    structure_sha256: str
    untargeted_sha256: str

    @property
    def relative_path(self) -> Path:
        return Path(self.section) / Path(*PurePosixPath(self.table).parts)

    @property
    def label(self) -> str:
        return f"{self.section}/{self.table}"


def _require_string(raw: dict[str, Any], name: str, context: str) -> str:
    value = raw.get(name)
    if not isinstance(value, str) or not value:
        raise ValueError(f"{context}: {name} must be a non-empty string")
    return value


def _parse_entry(raw: Any, kind: str, index: int) -> Entry:
    context = f"{kind}[{index}]"
    if not isinstance(raw, dict):
        raise ValueError(f"{context}: entry must be an object")
    section = _require_string(raw, "section", context)
    if section not in ALLOWED_SECTIONS:
        raise ValueError(f"{context}: unsupported section {section!r}")
    table = _require_string(raw, "table", context)
    table_path = PurePosixPath(table)
    if table_path.is_absolute() or ".." in table_path.parts:
        raise ValueError(f"{context}: unsafe table path {table!r}")
    if table_path.name != "000_Sheet1.csv":
        raise ValueError(f"{context}: table must end in 000_Sheet1.csv")
    row_id = _require_string(raw, "row_id", context)
    column = raw.get("column")
    if not isinstance(column, int) or isinstance(column, bool) or column < 1:
        raise ValueError(f"{context}: column must be an integer >= 1")
    old_sha256 = _require_string(raw, "old_sha256", context).lower()
    if len(old_sha256) != 64 or any(ch not in "0123456789abcdef" for ch in old_sha256):
        raise ValueError(f"{context}: old_sha256 is not a SHA-256 digest")
    target = raw.get("target")
    if kind == "app_only":
        if not isinstance(target, str):
            raise ValueError(f"{context}: app-only target must be a string")
    elif target is not None:
        raise ValueError(f"{context}: shared target must come from patch CSV")
    return Entry(Address(section, table, row_id, column), old_sha256, target, kind)


def _parse_digest(value: Any, name: str, context: str) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{context}: {name} must be a SHA-256 digest")
    digest = value.lower()
    if len(digest) != 64 or any(ch not in "0123456789abcdef" for ch in digest):
        raise ValueError(f"{context}: {name} is not a SHA-256 digest")
    return digest


def _parse_table_guard(raw: Any, index: int) -> TableGuard:
    context = f"table_guards[{index}]"
    if not isinstance(raw, dict):
        raise ValueError(f"{context}: entry must be an object")
    section = _require_string(raw, "section", context)
    if section not in ALLOWED_SECTIONS:
        raise ValueError(f"{context}: unsupported section {section!r}")
    table = _require_string(raw, "table", context)
    table_path = PurePosixPath(table)
    if table_path.is_absolute() or ".." in table_path.parts:
        raise ValueError(f"{context}: unsafe table path {table!r}")
    if table_path.name != "000_Sheet1.csv":
        raise ValueError(f"{context}: table must end in 000_Sheet1.csv")
    row_count = raw.get("row_count")
    if not isinstance(row_count, int) or isinstance(row_count, bool) or row_count < 0:
        raise ValueError(f"{context}: row_count must be an integer >= 0")
    return TableGuard(
        section=section,
        table=table,
        row_count=row_count,
        structure_sha256=_parse_digest(raw.get("structure_sha256"), "structure_sha256", context),
        untargeted_sha256=_parse_digest(raw.get("untargeted_sha256"), "untargeted_sha256", context),
    )


def load_manifest(path: Path) -> tuple[list[Entry], list[str], list[TableGuard]]:
    with path.open("r", encoding="utf-8-sig") as handle:
        raw = json.load(handle)
    if not isinstance(raw, dict) or raw.get("schema") != 1:
        raise ValueError(f"{path}: expected manifest schema 1")

    entries: list[Entry] = []
    for kind in ("shared", "app_only"):
        values = raw.get(kind)
        if not isinstance(values, list):
            raise ValueError(f"{path}: {kind} must be an array")
        entries.extend(_parse_entry(value, kind, index) for index, value in enumerate(values))

    addresses: set[Address] = set()
    for entry in entries:
        if entry.address in addresses:
            raise ValueError(f"{path}: duplicate address {entry.address.label}")
        addresses.add(entry.address)

    forbidden = raw.get("forbidden_terms", [])
    if not isinstance(forbidden, list) or any(not isinstance(value, str) or not value for value in forbidden):
        raise ValueError(f"{path}: forbidden_terms must be an array of non-empty strings")

    raw_guards = raw.get("table_guards")
    if not isinstance(raw_guards, list) or not raw_guards:
        raise ValueError(f"{path}: table_guards must be a non-empty array")
    guards = [_parse_table_guard(raw, index) for index, raw in enumerate(raw_guards)]
    guard_paths: set[Path] = set()
    for guard in guards:
        if guard.relative_path in guard_paths:
            raise ValueError(f"{path}: duplicate table guard {guard.label}")
        guard_paths.add(guard.relative_path)
    return (
        sorted(entries, key=lambda entry: entry.address),
        forbidden,
        sorted(guards, key=lambda guard: guard.relative_path.as_posix()),
    )


def read_rows(path: Path) -> list[list[str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.reader(handle))


def write_rows(path: Path, rows: list[list[str]]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerows(rows)


def build_index(rows: list[list[str]], path: Path) -> dict[str, int]:
    result: dict[str, int] = {}
    for index, row in enumerate(rows):
        if not row:
            continue
        row_id = row[0]
        if row_id in result:
            raise ValueError(f"{path}: duplicate row ID {row_id!r}")
        result[row_id] = index
    return result


def _json_sha256(value: Any) -> str:
    payload = json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def compute_table_guard(
    rows: list[list[str]],
    section: str,
    table: str,
    targeted: set[tuple[str, int]],
) -> TableGuard:
    """Fingerprint topology and every cell outside the explicit overlay."""

    structure: list[list[Any]] = []
    untargeted: list[list[Any]] = []
    for row_index, row in enumerate(rows):
        row_id = row[0] if row else ""
        structure.append([row_id, len(row)])
        cells: list[list[Any]] = []
        for column, value in enumerate(row):
            if (row_id, column) in targeted:
                continue
            cells.append([column, canonical_value(value)])
        untargeted.append([row_index, cells])
    return TableGuard(
        section=section,
        table=table,
        row_count=len(rows),
        structure_sha256=_json_sha256(structure),
        untargeted_sha256=_json_sha256(untargeted),
    )


def verify_table_guard(
    path: Path,
    rows: list[list[str]],
    guard: TableGuard,
    targeted: set[tuple[str, int]],
) -> None:
    actual = compute_table_guard(rows, guard.section, guard.table, targeted)
    mismatches: list[str] = []
    for name in ("row_count", "structure_sha256", "untargeted_sha256"):
        expected_value = getattr(guard, name)
        actual_value = getattr(actual, name)
        if expected_value != actual_value:
            mismatches.append(f"{name}={actual_value} expected={expected_value}")
    if mismatches:
        raise RuntimeError(f"{path}: app table guard mismatch: " + "; ".join(mismatches))


def resolved_under(root: Path, relative: Path) -> Path:
    root = root.resolve()
    result = (root / relative).resolve()
    if result != root and root not in result.parents:
        raise ValueError(f"Unsafe path outside {root}: {result}")
    return result


def target_from_patch(entry: Entry, patch_root: Path) -> str:
    path = resolved_under(patch_root, entry.address.relative_path)
    if not path.is_file():
        raise FileNotFoundError(f"{entry.address.label}: patch table not found: {path}")
    rows = read_rows(path)
    index = build_index(rows, path)
    if entry.address.row_id not in index:
        raise KeyError(f"{entry.address.label}: row is absent from patch table")
    row = rows[index[entry.address.row_id]]
    if entry.address.column >= len(row):
        raise ValueError(
            f"{entry.address.label}: patch row has {len(row)} column(s), "
            f"requested {entry.address.column}"
        )
    return canonical_value(row[entry.address.column])


def verify_untargeted_cells(
    path: Path,
    before: list[list[str]],
    after: list[list[str]],
    changed_cells: set[tuple[int, int]],
) -> None:
    if len(before) != len(after):
        raise RuntimeError(f"{path}: overlay changed row count {len(before)} -> {len(after)}")
    for row_index, (old_row, new_row) in enumerate(zip(before, after)):
        if len(old_row) != len(new_row):
            raise RuntimeError(
                f"{path}: overlay changed column count in row {row_index}: "
                f"{len(old_row)} -> {len(new_row)}"
            )
        for column, (old, new) in enumerate(zip(old_row, new_row)):
            if (row_index, column) not in changed_cells and old != new:
                raise RuntimeError(f"{path}: untargeted cell changed at row {row_index}, column {column}")
        if old_row and new_row and old_row[0] != new_row[0]:
            raise RuntimeError(f"{path}: row ID changed at row {row_index}")


def apply_overlay(csv_root: Path, patch_root: Path, manifest: Path, dry_run: bool) -> dict[str, int]:
    entries, _, guards = load_manifest(manifest)
    by_path: dict[Path, list[Entry]] = {}
    for entry in entries:
        by_path.setdefault(entry.address.relative_path, []).append(entry)
    guard_by_path = {guard.relative_path: guard for guard in guards}

    unguarded_entries = sorted(
        (path.as_posix() for path in set(by_path) - set(guard_by_path))
    )
    if unguarded_entries:
        raise RuntimeError(
            "app_text01 overlay entries lack table guards: "
            f"{unguarded_entries[:20]}"
        )

    actual_tables = {
        path.relative_to(csv_root)
        for path in csv_root.rglob("*.csv")
        if path.is_file()
    }
    if actual_tables != set(guard_by_path):
        missing = sorted(path.as_posix() for path in actual_tables - set(guard_by_path))
        extra = sorted(path.as_posix() for path in set(guard_by_path) - actual_tables)
        raise RuntimeError(
            "app_text01 table guard coverage mismatch: "
            f"unguarded={missing[:20]}; absent={extra[:20]}"
        )

    changed = 0
    already_target = 0
    shared = 0
    app_only = 0
    files_changed = 0
    pending_writes: list[tuple[Path, list[list[str]]]] = []

    # Validate every guarded app table before writing any of them.  Most app
    # tables have no overlay entries, but their reviewed topology and contents
    # are still part of the source contract.
    for relative, guard in sorted(
        guard_by_path.items(), key=lambda pair: pair[0].as_posix()
    ):
        file_entries = by_path.get(relative, [])
        path = resolved_under(csv_root, relative)
        if not path.is_file():
            raise FileNotFoundError(f"Overlay table not found: {path}")
        rows = read_rows(path)
        before = deepcopy(rows)
        index = build_index(rows, path)
        changed_cells: set[tuple[int, int]] = set()
        targeted = {(entry.address.row_id, entry.address.column) for entry in file_entries}
        verify_table_guard(path, rows, guard, targeted)

        for entry in file_entries:
            address = entry.address
            if address.row_id not in index:
                raise KeyError(f"{address.label}: row is absent from unpacked app table")
            row_index = index[address.row_id]
            row = rows[row_index]
            if address.column >= len(row):
                raise ValueError(
                    f"{address.label}: app row has {len(row)} column(s), requested {address.column}"
                )

            target = (
                target_from_patch(entry, patch_root)
                if entry.kind == "shared"
                else canonical_value(entry.target or "")
            )
            current = canonical_value(row[address.column])
            if entry.kind == "shared":
                shared += 1
            else:
                app_only += 1

            if current == target:
                already_target += 1
                continue
            actual_hash = value_sha256(current)
            if actual_hash != entry.old_sha256:
                raise RuntimeError(
                    f"{address.label}: unexpected third value; "
                    f"actual_sha256={actual_hash}, expected_old={entry.old_sha256}, "
                    f"target_sha256={value_sha256(target)}"
                )
            row[address.column] = target
            changed_cells.add((row_index, address.column))
            changed += 1

        verify_untargeted_cells(path, before, rows, changed_cells)
        verify_table_guard(path, rows, guard, targeted)
        if changed_cells:
            files_changed += 1
            if not dry_run:
                pending_writes.append((path, rows))

    for path, rows in pending_writes:
        write_rows(path, rows)
        persisted = read_rows(path)
        expected = [
            [canonical_value(value) for value in row]
            for row in rows
        ]
        actual = [
            [canonical_value(value) for value in row]
            for row in persisted
        ]
        if actual != expected:
            raise RuntimeError(f"{path}: semantic mismatch after writing overlay CSV")

    return {
        "entries": len(entries),
        "shared": shared,
        "app_only": app_only,
        "changed": changed,
        "already_target": already_target,
        "files_changed": files_changed,
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv-root", type=Path, required=True, help="unpacked app_text01 CSV root")
    parser.add_argument("--patch-root", type=Path, default=DEFAULT_PATCH_ROOT)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--dry-run", action="store_true", help="validate and report without writing")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    result = apply_overlay(
        args.csv_root.resolve(),
        args.patch_root.resolve(),
        args.manifest.resolve(),
        args.dry_run,
    )
    mode = "dry-run" if args.dry_run else "apply"
    print(f"app_text01 overlay v115 ({mode})")
    for name in ("entries", "shared", "app_only", "changed", "already_target", "files_changed"):
        print(f"{name}={result[name]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Round-trip verify release MVGL payloads against source CSV and Lua chunks."""

from __future__ import annotations

import argparse
import csv
import hashlib
import re
import shutil
import struct
import subprocess
from pathlib import Path

from apply_app_text01_overlay_v115 import (
    Address,
    build_index,
    canonical_value,
    compute_table_guard,
    load_manifest,
    target_from_patch,
)
from update_app_text01_overlay_manifest_v115 import changed_app_addresses


ROOT = Path(__file__).resolve().parents[1]
CSV_ROOT = ROOT / "csv"
PAYLOAD_ROOT = ROOT / "installer/payload"
WORK_ROOT = ROOT / "analysis/release_payload_verify_v114"
MVGL_TOOL = ROOT / ".tools/MVGLTools-v2.2.0-fixed/MVGLToolsCLI.exe"
LLVM_READOBJ = ROOT / ".tools/llvm-mingw-20260616-ucrt-x86_64/bin/llvm-readobj.exe"
NATIVE_INPUT_PAYLOAD = PAYLOAD_ROOT / "dinput8.dll"
LUA_ROOT = ROOT / "verify/lua_gender_hook/compiled"
TITLE_VERSION_ROOT = ROOT / "assets/title_version"
TITLE_VERSION_ASSET = TITLE_VERSION_ROOT / "ui_title_copyright_01.img"
TITLE_VERSION_MARKER = TITLE_VERSION_ROOT / "VERSION"
RELEASE_VERSION_FILE = ROOT / "VERSION"
OUT = ROOT / "exports/release_payload_verify_v114.csv"
SUMMARY = ROOT / "exports/release_payload_verify_v114_summary.txt"
APP_OVERLAY_MANIFEST = ROOT / "assets/app_text01_overlay/manifest_v115.json"
PATCH_TEXT_ROOT = CSV_ROOT / "patch_text01"
APP_OVERLAY_BASELINE_REF = "v0.1.50"
APP_VALUE_COLUMNS = {"message": 2, "text": 1}
EXPECTED_PAYLOAD_NAMES = {
    "addcont_01_text01.dx11.mvgl",
    "addcont_02_text01.dx11.mvgl",
    "addcont_03_text01.dx11.mvgl",
    "addcont_05_text01.dx11.mvgl",
    "addcont_07_text01.dx11.mvgl",
    "addcont_12_text01.dx11.mvgl",
    "addcont_17_text01.dx11.mvgl",
    "app_text01.dx11.mvgl",
    "patch_text01.dx11.mvgl",
}
APP_FORBIDDEN_TOKEN = re.compile(
    r"(?<![A-Za-zА-Яа-яЁё])(HP|SP|СП|ХП)(?![A-Za-zА-Яа-яЁё])",
    re.IGNORECASE,
)
CRITICAL_APP_ADDRESSES = (
    Address("text", "common_message.mbe/000_Sheet1.csv", "10048", 1),
    Address("text", "common_message_dx11.mbe/000_Sheet1.csv", "1901007", 1),
    Address("text", "digimon_profile.mbe/000_Sheet1.csv", "digimon_0097_profile", 1),
    Address("text", "digimon_profile.mbe/000_Sheet1.csv", "digimon_0322_profile", 1),
    Address("text", "char_name.mbe/000_Sheet1.csv", "char_PICODEVIMON", 1),
    Address("text", "char_name.mbe/000_Sheet1.csv", "char_KOROMON", 1),
)
CRITICAL_APP_ONLY_VALUES = {
    Address("text", "personality_skill_auto_explanation.mbe/000_Sheet1.csv", "14", 1): "ОЗ",
    Address("text", "personality_skill_auto_explanation.mbe/000_Sheet1.csv", "15", 1): "ОС",
    Address("text", "personality_skill_name.mbe/000_Sheet1.csv", "22", 1): "Подпитка ОС",
}
LUA_NAMES = [
    "function_common.lua",
    "function_field.lua",
    "battle_10810200.lua",
    "battle_11200010.lua",
    "m360.lua",
    "m440.lua",
    "t04prcs.lua",
    "gender_message_map.lua",
]


def safe_rmtree(path: Path) -> None:
    if not path.exists():
        return
    resolved = path.resolve()
    allowed = WORK_ROOT.resolve()
    if resolved != allowed and allowed not in resolved.parents:
        raise RuntimeError(f"Refusing to delete outside {allowed}: {resolved}")
    shutil.rmtree(resolved)


def run_tool(args: list[str]) -> None:
    result = subprocess.run(
        [str(MVGL_TOOL), *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if result.returncode:
        raise RuntimeError(
            "MVGLToolsCLI failed: " + " ".join(args)
            + "\n" + result.stdout[-2000:] + "\n" + result.stderr[-2000:]
        )


def read_rows(path: Path) -> list[list[str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.reader(handle))


def normalize_rows(rows: list[list[str]]) -> list[list[str]]:
    return [
        [value.replace("\r\n", "\n").replace("\r", "\n") for value in row]
        for row in rows
    ]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def dds_title_metadata(path: Path) -> tuple[bytes, int, int, int, int, int, int]:
    data = path.read_bytes()
    if len(data) < 148:
        raise ValueError(f"DDS is too short: {len(data)} bytes")
    return (
        data[:4],
        struct.unpack_from("<I", data, 12)[0],  # height
        struct.unpack_from("<I", data, 16)[0],  # width
        struct.unpack_from("<I", data, 28)[0],  # mip count
        struct.unpack_from("<I", data, 128)[0],  # DXGI format
        struct.unpack_from("<I", data, 132)[0],  # resource dimension
        struct.unpack_from("<I", data, 140)[0],  # array size
    )


def add_issue(
    issues: list[dict[str, str]],
    issue: str,
    package: str,
    file: str,
    detail: str = "",
) -> None:
    issues.append(
        {
            "issue": issue,
            "package": package,
            "file": file,
            "detail": detail,
        }
    )


def verify_app_text01_overlay(
    actual_csv: Path,
    issues: list[dict[str, str]],
) -> dict[str, int]:
    """Verify the complete guarded app overlay after MVGL round-trip."""

    counters = {
        "app_overlay_entries": 0,
        "app_overlap_rows": 0,
        "app_table_guards": 0,
        "app_forbidden_hits": 0,
        "app_critical_ids": 0,
    }
    try:
        entries, forbidden_terms, guards = load_manifest(APP_OVERLAY_MANIFEST)
    except Exception as error:  # report a durable release failure instead of a traceback
        add_issue(
            issues,
            "invalid_app_overlay_manifest",
            "app_text01",
            APP_OVERLAY_MANIFEST.relative_to(ROOT).as_posix(),
            str(error),
        )
        return counters

    counters["app_overlay_entries"] = len(entries)
    rows_cache: dict[Path, list[list[str]]] = {}
    index_cache: dict[Path, dict[str, int]] = {}

    def rows_and_index(relative: Path) -> tuple[list[list[str]], dict[str, int]] | None:
        path = actual_csv / relative
        if not path.is_file():
            add_issue(
                issues,
                "missing_app_overlay_table",
                "app_text01",
                relative.as_posix(),
            )
            return None
        if relative not in rows_cache:
            rows_cache[relative] = read_rows(path)
            try:
                index_cache[relative] = build_index(rows_cache[relative], path)
            except Exception as error:
                add_issue(
                    issues,
                    "invalid_app_overlay_table",
                    "app_text01",
                    relative.as_posix(),
                    str(error),
                )
                return None
        return rows_cache[relative], index_cache[relative]

    def actual_at(address: Address) -> str | None:
        data = rows_and_index(address.relative_path)
        if data is None:
            return None
        rows, index = data
        row_index = index.get(address.row_id)
        if row_index is None:
            add_issue(
                issues,
                "missing_app_overlay_row",
                "app_text01",
                address.relative_path.as_posix(),
                address.label,
            )
            return None
        row = rows[row_index]
        if address.column >= len(row):
            add_issue(
                issues,
                "missing_app_overlay_column",
                "app_text01",
                address.relative_path.as_posix(),
                f"{address.label}; columns={len(row)}",
            )
            return None
        return canonical_value(row[address.column])

    # Every explicit overlay entry must resolve to its final intended value.
    for entry in entries:
        actual = actual_at(entry.address)
        if actual is None:
            continue
        try:
            expected = (
                target_from_patch(entry, PATCH_TEXT_ROOT)
                if entry.kind == "shared"
                else canonical_value(entry.target or "")
            )
        except Exception as error:
            add_issue(
                issues,
                "invalid_app_overlay_target",
                "app_text01",
                entry.address.relative_path.as_posix(),
                f"{entry.address.label}; {error}",
            )
            continue
        if actual != expected:
            add_issue(
                issues,
                "app_overlay_target_mismatch",
                "app_text01",
                entry.address.relative_path.as_posix(),
                (
                    f"{entry.address.label}; actual_sha256="
                    f"{hashlib.sha256(actual.encode('utf-8')).hexdigest()}; "
                    f"expected_sha256={hashlib.sha256(expected.encode('utf-8')).hexdigest()}"
                ),
            )

    # Explicitly pin the user-visible issue #2/profile and old-label rows even
    # when a row already matched the patch before v0.1.50 and needs no overlay.
    for address in CRITICAL_APP_ADDRESSES:
        counters["app_critical_ids"] += 1
        actual = actual_at(address)
        if actual is None:
            continue
        patch_path = PATCH_TEXT_ROOT / address.relative_path
        try:
            patch_rows = read_rows(patch_path)
            patch_index = build_index(patch_rows, patch_path)
            patch_row = patch_rows[patch_index[address.row_id]]
            expected = canonical_value(patch_row[address.column])
        except Exception as error:
            add_issue(
                issues,
                "invalid_critical_app_patch_target",
                "app_text01",
                address.relative_path.as_posix(),
                f"{address.label}; {error}",
            )
            continue
        if actual != expected:
            add_issue(
                issues,
                "critical_app_id_mismatch",
                "app_text01",
                address.relative_path.as_posix(),
                address.label,
            )

    for address, expected in CRITICAL_APP_ONLY_VALUES.items():
        counters["app_critical_ids"] += 1
        actual = actual_at(address)
        if actual is not None and actual != expected:
            add_issue(
                issues,
                "critical_app_only_id_mismatch",
                "app_text01",
                address.relative_path.as_posix(),
                address.label,
            )

    # Compare every post-pack table's topology and every non-overlay cell with
    # the reviewed baseline manifest.  This proves that app-only rows survive.
    targeted_by_path: dict[Path, set[tuple[str, int]]] = {}
    for entry in entries:
        targeted_by_path.setdefault(entry.address.relative_path, set()).add(
            (entry.address.row_id, entry.address.column)
        )
    guard_by_path = {guard.relative_path: guard for guard in guards}
    actual_paths = {
        path.relative_to(actual_csv)
        for path in actual_csv.rglob("*.csv")
        if path.is_file()
    }
    expected_paths = set(guard_by_path)
    for relative in sorted(actual_paths - expected_paths, key=lambda path: path.as_posix()):
        add_issue(
            issues,
            "unguarded_app_table",
            "app_text01",
            relative.as_posix(),
        )
    for relative in sorted(expected_paths - actual_paths, key=lambda path: path.as_posix()):
        add_issue(
            issues,
            "missing_guarded_app_table",
            "app_text01",
            relative.as_posix(),
        )
    for relative in sorted(actual_paths & expected_paths, key=lambda path: path.as_posix()):
        guard = guard_by_path[relative]
        rows = read_rows(actual_csv / relative)
        actual_guard = compute_table_guard(
            rows,
            guard.section,
            guard.table,
            targeted_by_path.get(relative, set()),
        )
        counters["app_table_guards"] += 1
        mismatch = [
            name
            for name in ("row_count", "structure_sha256", "untargeted_sha256")
            if getattr(actual_guard, name) != getattr(guard, name)
        ]
        if mismatch:
            add_issue(
                issues,
                "app_table_guard_mismatch",
                "app_text01",
                relative.as_posix(),
                ",".join(mismatch),
            )

    # No standalone old HP/SP vocabulary or reviewed legacy forms may remain
    # in user-visible app values (including rows which exist only in app).
    for relative in sorted(actual_paths, key=lambda path: path.as_posix()):
        section = relative.parts[0] if relative.parts else ""
        column = APP_VALUE_COLUMNS.get(section)
        if column is None:
            continue
        for row in read_rows(actual_csv / relative):
            if not row or len(row) <= column:
                continue
            row_id = row[0]
            value = canonical_value(row[column])
            for match in APP_FORBIDDEN_TOKEN.finditer(value):
                counters["app_forbidden_hits"] += 1
                add_issue(
                    issues,
                    "forbidden_app_vocabulary",
                    "app_text01",
                    relative.as_posix(),
                    f"row_id={row_id}; token={match.group(0)}",
                )
            for term in forbidden_terms:
                if term in value:
                    counters["app_forbidden_hits"] += 1
                    add_issue(
                        issues,
                        "forbidden_app_legacy_form",
                        "app_text01",
                        relative.as_posix(),
                        f"row_id={row_id}; term={term}",
                    )

    # Release changes that overlap app must stay on the explicit shared
    # allowlist, even when the current app payload already equals the target.
    overlap = changed_app_addresses(
        actual_csv,
        PATCH_TEXT_ROOT,
        APP_OVERLAY_BASELINE_REF,
    )
    counters["app_overlap_rows"] = len(overlap)
    shared_keys = {
        (
            entry.address.section,
            entry.address.table,
            entry.address.row_id,
            entry.address.column,
        )
        for entry in entries
        if entry.kind == "shared"
    }
    for key, _app_value, _target in overlap:
        if key not in shared_keys:
            add_issue(
                issues,
                "uncovered_changed_app_row",
                "app_text01",
                f"{key[0]}/{key[1]}",
                f"row_id={key[2]}; column={key[3]}",
            )

    return counters


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--app-csv-root",
        type=Path,
        help="verify one unpacked post-pack app_text01 CSV tree and exit",
    )
    args = parser.parse_args(argv)

    if args.app_csv_root is not None:
        app_csv_root = args.app_csv_root.resolve()
        if not app_csv_root.is_dir():
            raise SystemExit(f"app_text01 CSV root not found: {app_csv_root}")
        issues: list[dict[str, str]] = []
        stats = verify_app_text01_overlay(app_csv_root, issues)
        print("app_text01 post-pack overlay verification")
        for name, value in stats.items():
            print(f"{name}={value}")
        print(f"issues={len(issues)}")
        if issues:
            for issue in issues[:50]:
                print(
                    f"{issue['issue']}: {issue['file']}: "
                    f"{issue['detail']}"
                )
            raise SystemExit("app_text01 post-pack overlay verification failed.")
        return

    if not MVGL_TOOL.exists():
        raise SystemExit(f"Fixed MVGL tool not found: {MVGL_TOOL}")
    payloads = sorted(PAYLOAD_ROOT.glob("*.dx11.mvgl"))
    actual_payload_names = {path.name for path in payloads}
    if actual_payload_names != EXPECTED_PAYLOAD_NAMES:
        missing = sorted(EXPECTED_PAYLOAD_NAMES - actual_payload_names)
        extra = sorted(actual_payload_names - EXPECTED_PAYLOAD_NAMES)
        raise SystemExit(
            "Release payload package set mismatch: "
            f"missing={missing}; extra={extra}"
        )

    safe_rmtree(WORK_ROOT)
    WORK_ROOT.mkdir(parents=True, exist_ok=True)
    issues: list[dict[str, str]] = []
    files_compared = 0
    rows_compared = 0
    csv_packages = 0
    lua_compared = 0
    title_assets_compared = 0
    app_overlay_stats = {
        "app_overlay_entries": 0,
        "app_overlap_rows": 0,
        "app_table_guards": 0,
        "app_forbidden_hits": 0,
        "app_critical_ids": 0,
    }

    native_payloads = 0
    if not NATIVE_INPUT_PAYLOAD.exists():
        issues.append(
            {
                "issue": "missing_native_input_payload",
                "package": "installer",
                "file": "payload/dinput8.dll",
                "detail": "",
            }
        )
    elif not LLVM_READOBJ.exists():
        issues.append(
            {
                "issue": "missing_pe_verifier",
                "package": "installer",
                "file": "payload/dinput8.dll",
                "detail": str(LLVM_READOBJ),
            }
        )
    else:
        native_payloads = 1
        result = subprocess.run(
            [
                str(LLVM_READOBJ),
                "--file-headers",
                "--coff-exports",
                str(NATIVE_INPUT_PAYLOAD),
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        required = {
            "Machine: IMAGE_FILE_MACHINE_AMD64",
            "DirectInput8Create",
            "DstsRuInstallInputHook",
            "DstsRuInputFixVersion",
        }
        missing = sorted(value for value in required if value not in result.stdout)
        if result.returncode or missing:
            issues.append(
                {
                    "issue": "invalid_native_input_payload",
                    "package": "installer",
                    "file": "payload/dinput8.dll",
                    "detail": f"exit={result.returncode}; missing={missing}",
                }
            )

    for payload in payloads:
        package = payload.name.removesuffix(".dx11.mvgl")
        package_root = WORK_ROOT / package
        base_root = package_root / "base"
        run_tool(["--game=dsts", "--mode=unpack-mvgl", "--input", str(payload), "--output", str(base_root)])

        expected_package = CSV_ROOT / package
        # app_text01 is intentionally verified against the guarded cell
        # overlay below.  Ignore any local csv/app_text01 tree left by an
        # unpack operation; whole-table equality is both wrong and unsafe for
        # this package's app-only rows.
        if package != "app_text01" and expected_package.exists():
            csv_packages += 1
            actual_csv = package_root / "csv"
            for section in ("message", "text"):
                expected_section = expected_package / section
                if not expected_section.exists():
                    continue
                packed_section = base_root / section
                if not packed_section.exists():
                    issues.append(
                        {
                            "issue": "missing_packed_section",
                            "package": package,
                            "file": section,
                            "detail": str(packed_section),
                        }
                    )
                    continue
                output_section = actual_csv / section
                run_tool(
                    [
                        "--game=dsts", "--mode=unpack-mbe-dir",
                        "--input", str(packed_section), "--output", str(output_section),
                    ]
                )
                for expected_file in sorted(expected_section.rglob("*.csv")):
                    relative = expected_file.relative_to(expected_package)
                    actual_file = actual_csv / relative
                    if not actual_file.exists():
                        issues.append(
                            {
                                "issue": "missing_csv_after_unpack",
                                "package": package,
                                "file": relative.as_posix(),
                                "detail": "",
                            }
                        )
                        continue
                    expected_rows = normalize_rows(read_rows(expected_file))
                    actual_rows = normalize_rows(read_rows(actual_file))
                    files_compared += 1
                    rows_compared += max(0, len(expected_rows) - 1)
                    if expected_rows != actual_rows:
                        mismatch = next(
                            (
                                index
                                for index, pair in enumerate(zip(expected_rows, actual_rows), start=1)
                                if pair[0] != pair[1]
                            ),
                            min(len(expected_rows), len(actual_rows)) + 1,
                        )
                        issues.append(
                            {
                                "issue": "csv_semantic_mismatch",
                                "package": package,
                                "file": relative.as_posix(),
                                "detail": (
                                    f"first_row={mismatch}; expected_rows={len(expected_rows)}; "
                                    f"actual_rows={len(actual_rows)}"
                                ),
                            }
                        )

        if package == "patch_text01":
            for name in LUA_NAMES:
                expected_lua = LUA_ROOT / name
                actual_lua = base_root / "lua" / name
                if not expected_lua.exists() or not actual_lua.exists():
                    issues.append(
                        {
                            "issue": "missing_lua_chunk",
                            "package": package,
                            "file": f"lua/{name}",
                            "detail": "",
                        }
                    )
                    continue
                lua_compared += 1
                if sha256(expected_lua) != sha256(actual_lua):
                    issues.append(
                        {
                            "issue": "lua_sha256_mismatch",
                            "package": package,
                            "file": f"lua/{name}",
                            "detail": "",
                        }
                    )

        if package == "app_text01":
            actual_csv = package_root / "csv"
            app_sections_ok = True
            for section in ("message", "text"):
                packed_section = base_root / section
                if not packed_section.exists():
                    app_sections_ok = False
                    add_issue(
                        issues,
                        "missing_app_packed_section",
                        package,
                        section,
                        str(packed_section),
                    )
                    continue
                run_tool(
                    [
                        "--game=dsts", "--mode=unpack-mbe-dir",
                        "--input", str(packed_section),
                        "--output", str(actual_csv / section),
                    ]
                )
            if app_sections_ok:
                app_overlay_stats = verify_app_text01_overlay(actual_csv, issues)

            actual_title = base_root / "images/ui_title_copyright_01.img"
            expected_metadata = (b"DDS ", 32, 2048, 1, 98, 3, 1)
            release_version = RELEASE_VERSION_FILE.read_text(encoding="utf-8-sig").strip()
            asset_version = (
                TITLE_VERSION_MARKER.read_text(encoding="utf-8-sig").strip()
                if TITLE_VERSION_MARKER.exists()
                else ""
            )
            if asset_version != release_version:
                issues.append(
                    {
                        "issue": "title_version_marker_mismatch",
                        "package": package,
                        "file": "images/ui_title_copyright_01.img",
                        "detail": f"asset={asset_version!r}; release={release_version!r}",
                    }
                )
            if not TITLE_VERSION_ASSET.exists() or not actual_title.exists():
                issues.append(
                    {
                        "issue": "missing_title_version_asset",
                        "package": package,
                        "file": "images/ui_title_copyright_01.img",
                        "detail": "",
                    }
                )
            else:
                title_assets_compared += 1
                if sha256(TITLE_VERSION_ASSET) != sha256(actual_title):
                    issues.append(
                        {
                            "issue": "title_version_asset_sha256_mismatch",
                            "package": package,
                            "file": "images/ui_title_copyright_01.img",
                            "detail": "",
                        }
                    )
                try:
                    actual_metadata = dds_title_metadata(actual_title)
                except ValueError as error:
                    actual_metadata = None
                    issues.append(
                        {
                            "issue": "invalid_title_version_dds",
                            "package": package,
                            "file": "images/ui_title_copyright_01.img",
                            "detail": str(error),
                        }
                    )
                if actual_metadata is not None and actual_metadata != expected_metadata:
                    issues.append(
                        {
                            "issue": "invalid_title_version_dds_metadata",
                            "package": package,
                            "file": "images/ui_title_copyright_01.img",
                            "detail": f"actual={actual_metadata!r}; expected={expected_metadata!r}",
                        }
                    )
            data_file_count = sum(1 for path in base_root.rglob("*") if path.is_file())
            if data_file_count != 254:
                issues.append(
                    {
                        "issue": "app_text01_file_count_mismatch",
                        "package": package,
                        "file": ".",
                        "detail": f"actual={data_file_count}; expected=254",
                    }
                )

    fields = ["issue", "package", "file", "detail"]
    with OUT.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(issues)

    summary = [
        "Release payload verification v114",
        f"payload_packages={len(payloads)}",
        f"csv_packages={csv_packages}",
        f"csv_files_compared={files_compared}",
        f"csv_rows_compared={rows_compared}",
        f"lua_chunks_compared={lua_compared}",
        f"native_payloads={native_payloads}",
        f"title_assets_compared={title_assets_compared}",
        f"app_overlay_entries={app_overlay_stats['app_overlay_entries']}",
        f"app_overlap_rows={app_overlay_stats['app_overlap_rows']}",
        f"app_table_guards={app_overlay_stats['app_table_guards']}",
        f"app_forbidden_hits={app_overlay_stats['app_forbidden_hits']}",
        f"app_critical_ids={app_overlay_stats['app_critical_ids']}",
        f"issues={len(issues)}",
        f"report={OUT.relative_to(ROOT)}",
    ]
    SUMMARY.write_text("\n".join(summary) + "\n", encoding="utf-8")
    print("\n".join(summary))
    if issues:
        raise SystemExit("Release payload verification failed; see report.")


if __name__ == "__main__":
    main()

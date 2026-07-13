#!/usr/bin/env python3
"""Round-trip verify release MVGL payloads against source CSV and Lua chunks."""

from __future__ import annotations

import csv
import hashlib
import shutil
import struct
import subprocess
from pathlib import Path


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


def main() -> None:
    if not MVGL_TOOL.exists():
        raise SystemExit(f"Fixed MVGL tool not found: {MVGL_TOOL}")
    payloads = sorted(PAYLOAD_ROOT.glob("*.dx11.mvgl"))
    if len(payloads) != 9:
        raise SystemExit(f"Expected 9 payload packages, found {len(payloads)}")

    safe_rmtree(WORK_ROOT)
    WORK_ROOT.mkdir(parents=True, exist_ok=True)
    issues: list[dict[str, str]] = []
    files_compared = 0
    rows_compared = 0
    csv_packages = 0
    lua_compared = 0
    title_assets_compared = 0

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
        if expected_package.exists():
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
        f"issues={len(issues)}",
        f"report={OUT.relative_to(ROOT)}",
    ]
    SUMMARY.write_text("\n".join(summary) + "\n", encoding="utf-8")
    print("\n".join(summary))
    if issues:
        raise SystemExit("Release payload verification failed; see report.")


if __name__ == "__main__":
    main()

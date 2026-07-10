from __future__ import annotations

import csv
import json
import re
import shutil
import subprocess
from collections import Counter
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GAME_DATA = Path(r"D:\SteamLibrary\steamapps\common\Digimon Story Time Stranger\gamedata")
CSV_ROOT = ROOT / "csv"
PAYLOAD_ROOT = ROOT / "installer" / "payload"
WORK_ROOT = ROOT / "analysis" / "game_text01_compare_v030"
ORIGINAL_CSV_ROOT = WORK_ROOT / "original_csv"
PAYLOAD_CSV_ROOT = WORK_ROOT / "payload_csv"
OUT_CSV = ROOT / "exports" / "game_text01_compare_v030.csv"
OUT_SUMMARY = ROOT / "exports" / "game_text01_compare_summary_v030.txt"
REPORT_LABEL = "Game text01 vs RU payload audit v0.1.30"
PREEXTRACTED_ORIGINAL_ROOT: Path | None = None

MVGL_TOOL = ROOT / ".tools" / "MVGLTools-v2.2.0" / "MVGLTools-v2.2.0-win64" / "MVGLToolsCLI.exe"

CYRILLIC_RE = re.compile(r"[\u0400-\u04FF]")
LATIN_RE = re.compile(r"[A-Za-z][A-Za-z'&.-]{1,}")
TAG_RE = re.compile(r"\{[^}]*\}|image\([^)]*\)|ui_[A-Za-z0-9_]+|[a-z]\d{2,4}_[A-Za-z0-9_]+")

ALLOWED_WORDS = {
    "ADAMAS",
    "ATK",
    "BGM",
    "CRT",
    "DATS",
    "DEF",
    "DLC",
    "DMW",
    "DNA",
    "D-SAT",
    "EXP",
    "HP",
    "INT",
    "JPN",
    "LV",
    "Lv",
    "OK",
    "ON",
    "OFF",
    "SP",
    "SPD",
    "Steam",
    "USB",
}


@dataclass(frozen=True)
class TextRow:
    package: str
    relative_file: str
    row_id: str
    line_no: int
    speaker: str
    text: str


def safe_rmtree(path: Path, allowed_parent: Path) -> None:
    if not path.exists():
        return
    resolved = path.resolve()
    allowed = allowed_parent.resolve()
    if allowed not in resolved.parents and resolved != allowed:
        raise RuntimeError(f"Refusing to delete outside {allowed}: {resolved}")
    shutil.rmtree(resolved)


def run_tool(args: list[str]) -> None:
    completed = subprocess.run(
        [str(MVGL_TOOL), *args],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
    )
    if completed.returncode != 0:
        raise RuntimeError(
            "MVGLToolsCLI failed\n"
            + " ".join(args)
            + "\nSTDOUT:\n"
            + completed.stdout[-4000:]
            + "\nSTDERR:\n"
            + completed.stderr[-4000:]
        )


def package_name(path: Path) -> str:
    return path.name.replace(".dx11.mvgl", "")


def game_text01_packages() -> dict[str, Path]:
    return {package_name(p): p for p in sorted(GAME_DATA.glob("*_text01.dx11.mvgl"))}


def payload_packages() -> dict[str, Path]:
    return {package_name(p): p for p in sorted(PAYLOAD_ROOT.glob("*.dx11.mvgl"))}


def extract_original_package(name: str, mvgl_path: Path) -> Path:
    csv_package = ORIGINAL_CSV_ROOT / name
    marker = csv_package / ".source.json"
    source_meta = {
        "path": str(mvgl_path),
        "size": mvgl_path.stat().st_size,
        "mtime_ns": mvgl_path.stat().st_mtime_ns,
    }
    if marker.exists():
        try:
            if json.loads(marker.read_text(encoding="utf-8")) == source_meta:
                return csv_package
        except json.JSONDecodeError:
            pass

    package_work = WORK_ROOT / "unpacked" / name
    safe_rmtree(package_work, WORK_ROOT)
    safe_rmtree(csv_package, ORIGINAL_CSV_ROOT)
    package_work.mkdir(parents=True, exist_ok=True)
    csv_package.mkdir(parents=True, exist_ok=True)

    base_dir = package_work / "base"
    run_tool(["--game=dsts", "--mode=unpack-mvgl", "--input", str(mvgl_path), "--output", str(base_dir)])
    for section in ("message", "text"):
        base_section = base_dir / section
        if not base_section.exists():
            continue
        out_section = csv_package / section
        run_tool(["--game=dsts", "--mode=unpack-mbe-dir", "--input", str(base_section), "--output", str(out_section)])

    marker.write_text(json.dumps(source_meta, ensure_ascii=False, indent=2), encoding="utf-8")
    safe_rmtree(package_work, WORK_ROOT)
    return csv_package


def extract_payload_package(name: str, mvgl_path: Path) -> Path:
    csv_package = PAYLOAD_CSV_ROOT / name
    marker = csv_package / ".source.json"
    source_meta = {
        "path": str(mvgl_path),
        "size": mvgl_path.stat().st_size,
        "mtime_ns": mvgl_path.stat().st_mtime_ns,
    }
    if marker.exists():
        try:
            if json.loads(marker.read_text(encoding="utf-8")) == source_meta:
                return csv_package
        except json.JSONDecodeError:
            pass

    package_work = WORK_ROOT / "unpacked_payload" / name
    safe_rmtree(package_work, WORK_ROOT)
    safe_rmtree(csv_package, PAYLOAD_CSV_ROOT)
    package_work.mkdir(parents=True, exist_ok=True)
    csv_package.mkdir(parents=True, exist_ok=True)

    base_dir = package_work / "base"
    run_tool(["--game=dsts", "--mode=unpack-mvgl", "--input", str(mvgl_path), "--output", str(base_dir)])
    for section in ("message", "text"):
        base_section = base_dir / section
        if not base_section.exists():
            continue
        out_section = csv_package / section
        run_tool(["--game=dsts", "--mode=unpack-mbe-dir", "--input", str(base_section), "--output", str(out_section)])

    marker.write_text(json.dumps(source_meta, ensure_ascii=False, indent=2), encoding="utf-8")
    safe_rmtree(package_work, WORK_ROOT)
    return csv_package


def read_rows(path: Path) -> list[list[str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.reader(f))


def text_column(relative_file: str, row: list[str]) -> int | None:
    if relative_file.startswith("message/"):
        return 2 if len(row) > 2 else None
    if relative_file.startswith("text/"):
        return 1 if len(row) > 1 else None
    return None


def collect_rows(package: str, csv_package: Path) -> dict[tuple[str, str], TextRow]:
    rows_by_key: dict[tuple[str, str], TextRow] = {}
    if not csv_package.exists():
        return rows_by_key
    for path in sorted(csv_package.rglob("*.csv")):
        relative_file = path.relative_to(csv_package).as_posix()
        for line_no, row in enumerate(read_rows(path), start=1):
            if line_no == 1 or not row:
                continue
            col = text_column(relative_file, row)
            if col is None:
                continue
            row_id = row[0].strip() if row else ""
            speaker = row[1].strip() if relative_file.startswith("message/") and len(row) > 1 else ""
            rows_by_key[(relative_file, row_id)] = TextRow(
                package=package,
                relative_file=relative_file,
                row_id=row_id,
                line_no=line_no,
                speaker=speaker,
                text=row[col],
            )
    return rows_by_key


def normalize_text(value: str) -> str:
    return "\n".join(line.rstrip() for line in value.replace("\r\n", "\n").replace("\r", "\n").strip().split("\n"))


def strip_technical(value: str) -> str:
    value = TAG_RE.sub(" ", value)
    value = re.sub(r"\b[A-Za-z0-9_]+_[A-Za-z0-9_]+\b", " ", value)
    value = re.sub(r"\b\d+(?:\.\d+)?\b", " ", value)
    return value


def latin_words(value: str) -> list[str]:
    clean = strip_technical(value)
    found: list[str] = []
    for word in LATIN_RE.findall(clean):
        stripped = word.strip(".,:;!?()[]\"'")
        if len(stripped) < 2:
            continue
        if stripped in ALLOWED_WORDS or stripped.upper() in ALLOWED_WORDS:
            continue
        if stripped.startswith("fc") or stripped.startswith("is"):
            continue
        found.append(stripped)
    return found


def english_like(value: str) -> bool:
    words = latin_words(value)
    if not words:
        return False
    clean = strip_technical(value)
    if CYRILLIC_RE.search(clean):
        return False
    return len(words) >= 2 or len(clean.strip()) >= 8


def add_audit_row(
    audit_rows: list[list[str]],
    severity: int,
    category: str,
    source: TextRow | None,
    translated: TextRow | None,
    detail: str,
) -> None:
    row = translated or source
    current_text = translated.text if translated else ""
    source_text = source.text if source else ""
    current_text = re.sub(r"[ \t]+(?=\r?\n)", "", current_text)
    source_text = re.sub(r"[ \t]+(?=\r?\n)", "", source_text)
    if row and "ed_lyrics" in row.relative_file:
        current_text = "[lyrics redacted in audit report]"
        source_text = "[lyrics redacted in audit report]"
    audit_rows.append(
        [
            str(severity),
            category,
            row.package if row else "",
            row.relative_file if row else "",
            row.row_id if row else "",
            str(row.line_no) if row else "",
            row.speaker if row else "",
            detail,
            current_text,
            source_text,
        ]
    )


def main() -> None:
    if not GAME_DATA.exists():
        raise SystemExit(f"Game data folder not found: {GAME_DATA}")
    if not MVGL_TOOL.exists():
        raise SystemExit(f"MVGLToolsCLI not found: {MVGL_TOOL}")

    ORIGINAL_CSV_ROOT.mkdir(parents=True, exist_ok=True)
    PAYLOAD_CSV_ROOT.mkdir(parents=True, exist_ok=True)
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)

    game_packages = game_text01_packages()
    translated_packages = payload_packages()
    csv_packages = {p.name: p for p in CSV_ROOT.iterdir() if p.is_dir()}

    headers = [
        "severity",
        "category",
        "package",
        "file",
        "row_id",
        "line",
        "speaker",
        "detail",
        "current_translation",
        "source_game_text01",
    ]
    audit_rows: list[list[str]] = [headers]
    counts: Counter[str] = Counter()

    for name, game_path in game_packages.items():
        if name not in translated_packages:
            counts["missing_package"] += 1
            audit_rows.append([
                "3",
                "missing_package",
                name,
                "",
                "",
                "",
                "",
                "Game text01 package is not included in installer payload",
                "",
                str(game_path),
            ])
            continue
        original_csv = None
        if PREEXTRACTED_ORIGINAL_ROOT is not None:
            cached_original = PREEXTRACTED_ORIGINAL_ROOT / name / "csv"
            if cached_original.is_dir():
                original_csv = cached_original
        if original_csv is None:
            original_csv = extract_original_package(name, game_path)
        translated_csv = csv_packages.get(name)
        if translated_csv is None:
            translated_csv = extract_payload_package(name, translated_packages[name])
        original_rows = collect_rows(name, original_csv)
        translated_rows = collect_rows(name, translated_csv)

        source_files = {key[0] for key in original_rows}
        translated_files = {key[0] for key in translated_rows}
        for missing_file in sorted(source_files - translated_files):
            counts["missing_file"] += 1
            sample = next(row for key, row in original_rows.items() if key[0] == missing_file)
            add_audit_row(audit_rows, 3, "missing_file", sample, None, "Source file is absent from translated CSV")

        for key, source in sorted(original_rows.items()):
            translated = translated_rows.get(key)
            if translated is None:
                counts["missing_row"] += 1
                add_audit_row(audit_rows, 3, "missing_row", source, None, "Source row is absent from translated CSV")
                continue

            source_norm = normalize_text(source.text)
            translated_norm = normalize_text(translated.text)
            if not translated_norm:
                continue

            if source_norm == translated_norm and english_like(source_norm):
                counts["same_as_original"] += 1
                sev = 3 if len(latin_words(source_norm)) >= 4 or len(source_norm) >= 32 else 2
                add_audit_row(audit_rows, sev, "same_as_original", source, translated, "Translation is identical to game text01 source")
                continue

            words = latin_words(translated_norm)
            if not words:
                continue
            if CYRILLIC_RE.search(strip_technical(translated_norm)):
                counts["latin_mixed"] += 1
                add_audit_row(
                    audit_rows,
                    2,
                    "latin_mixed",
                    source,
                    translated,
                    ", ".join(sorted(set(words))[:16]),
                )
            else:
                counts["latin_no_cyrillic"] += 1
                sev = 3 if len(words) >= 3 or len(translated_norm) >= 24 else 2
                add_audit_row(
                    audit_rows,
                    sev,
                    "latin_no_cyrillic",
                    source,
                    translated,
                    ", ".join(sorted(set(words))[:16]),
                )

    for name in sorted(translated_packages.keys() - game_packages.keys()):
        counts["extra_payload_package"] += 1
        audit_rows.append([
            "1",
            "extra_payload_package",
            name,
            "",
            "",
            "",
            "",
            "Installer payload has no matching game text01 package in this install",
            str(translated_packages[name]),
            "",
        ])

    with OUT_CSV.open("w", encoding="utf-8-sig", newline="") as f:
        csv.writer(f, lineterminator="\n").writerows(audit_rows)

    summary_lines = [
        REPORT_LABEL,
        f"game_data={GAME_DATA}",
        f"source_root={PREEXTRACTED_ORIGINAL_ROOT or ORIGINAL_CSV_ROOT}",
        f"payload_root={PAYLOAD_ROOT}",
        f"rows={len(audit_rows) - 1}",
        "",
        "Counts:",
    ]
    for category, count in counts.most_common():
        summary_lines.append(f"- {category}: {count}")
    summary_lines.extend(["", "Top packages:"])
    package_counts = Counter(row[2] for row in audit_rows[1:])
    for package, count in package_counts.most_common(20):
        summary_lines.append(f"- {package}: {count}")
    OUT_SUMMARY.write_text("\n".join(summary_lines) + "\n", encoding="utf-8")

    print(f"Wrote {len(audit_rows) - 1} candidates to {OUT_CSV.relative_to(ROOT)}")
    for category, count in counts.most_common():
        print(f"{category}: {count}")
    print(f"Summary: {OUT_SUMMARY.relative_to(ROOT)}")


if __name__ == "__main__":
    main()

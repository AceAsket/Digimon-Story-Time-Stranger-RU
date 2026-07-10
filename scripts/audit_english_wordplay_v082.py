#!/usr/bin/env python3
"""Build a source-linked registry of localized English wordplay.

The registry combines explicit source markers (``pun``), deliberate English
misspellings, name confusions, recurring character tics, rhymes, and idioms
whose literal image matters in context.  It joins every reviewed source row to
the current Russian row so future releases can audit these fragile places.
"""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

import fix_long_dialogue_quality_tail_v080 as v080
import fix_twentiest_consistency_tail_v075 as v075
import fix_twentiest_wordplay_scene_v074 as v074
import fix_wordplay_gender_npc_tail_v073 as v073


ROOT = Path(__file__).resolve().parents[1]
CURRENT_ROOT = ROOT / "csv"
SOURCE_ROOT = ROOT / "verify/game_build_23514637/text_original"
REPORT = ROOT / "exports/english_wordplay_audit_v082.csv"
SUMMARY = ROOT / "exports/english_wordplay_audit_v082_summary.md"


def v073_family(package: str, relative: str, row_id: str) -> str | None:
    if row_id == "hazama_02_212_10":
        return "Whamon: whale/well"
    if row_id in {"s110_093_372", "s110_093_400"}:
        return "Horse idiom/pun"
    if row_id in {
        "s200_149_770", "s200_149_780", "s200_149_781",
        "s200_149_782", "s200_149_790", "s200_149_800",
        "s200_149_810",
    }:
        return "EDEN/Edion/oden"
    if row_id in {
        "f_d0502_0150_0110", "f_d0502_0150_0120",
        "f_d0502_0150_0130",
    }:
        return "Nanimon/Nannymon"
    if row_id.startswith("lyla_001_"):
        return "Lilamon proverb contrast"
    if (
        row_id == "arena01_f001_005_040"
        or row_id.startswith("f_d0301_")
        or row_id.startswith("f_d0302_0350_")
        or row_id.startswith("f_d0302_0360_")
        or row_id.startswith("f_d0305_0090_")
        or row_id.startswith("f_d0903_")
        or row_id == "f_d0904_0420_0020"
        or row_id.startswith("g_degi_h0212_")
        or row_id.startswith("m170_100_")
        or row_id == "m170_110_010"
    ):
        return "Whamon: whale/well"
    return None


def registry() -> dict[tuple[str, str, str], str]:
    result: dict[tuple[str, str, str], str] = {}
    for key in v073.UPDATES:
        family = v073_family(*key)
        if family:
            result[key] = family
    for row_id in v074.UPDATES:
        result[(
            "patch_text01",
            "message/s010_159.mbe/000_Sheet1.csv",
            row_id,
        )] = "Twentiest/Dвадцатейшесть"
    for key in v075.UPDATES:
        result[key] = "Twentiest/Dвадцатейшесть"
    for key in v080.UPDATES:
        if key[2] == "f_d0202_0780_0020":
            result[key] = "Rhyming shop jingle"
        elif key[2] == "sow_202_040":
            result[key] = "Bite idiom/literal bite"
    result[("patch_text01", "message/d09.mbe/000_Sheet1.csv", "f_d0905_0010_0190")] = (
        "Bite idiom/literal bite"
    )
    result[("patch_text01", "message/m030.mbe/000_Sheet1.csv", "m030_010_090")] = (
        "Minervamon: gubmint"
    )
    return result


def load_rows(path: Path) -> dict[str, list[str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return {row[0]: row for row in csv.reader(handle) if row}


def text_column(relative: str) -> int:
    return 2 if relative.startswith("message/") else 1


def clean_report_text(value: str) -> str:
    return "\n".join(line.rstrip() for line in value.splitlines())


def main() -> None:
    rows: list[list[str]] = []
    missing: list[str] = []
    for (package, relative, row_id), family in sorted(
        registry().items(), key=lambda item: (item[1], item[0])
    ):
        source_path = SOURCE_ROOT / package / "csv" / relative
        if not source_path.exists() and package == "patch_text01":
            source_path = SOURCE_ROOT / "app_text01" / "csv" / relative
        current_path = CURRENT_ROOT / package / relative
        if not source_path.exists() or not current_path.exists():
            missing.append(f"{package}/{relative}:{row_id} (file)")
            continue
        source = load_rows(source_path).get(row_id)
        current = load_rows(current_path).get(row_id)
        if source is None or current is None:
            missing.append(f"{package}/{relative}:{row_id} (row)")
            continue
        column = text_column(relative)
        speaker = source[1] if relative.startswith("message/") and len(source) > 1 else ""
        rows.append([
            family,
            package,
            relative,
            row_id,
            speaker,
            clean_report_text(source[column]),
            clean_report_text(current[column]),
            "localized" if current[column].strip() else "empty",
        ])

    if missing:
        raise SystemExit("Missing wordplay rows:\n" + "\n".join(missing))

    with REPORT.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow([
            "family", "package", "relative_path", "row_id", "speaker",
            "english_source", "current_russian", "status",
        ])
        writer.writerows(rows)

    counts = Counter(row[0] for row in rows)
    lines = [
        "# Аудит английской игры слов v082",
        "",
        f"Проверено строк с привязкой к английскому оригиналу: **{len(rows)}**. Пропущено: **0**.",
        "",
        "Проверка охватывает явные каламбуры, намеренные искажения слов, видовую",
        "манеру речи, путаницу имён, рифмованные реплики и образные идиомы.",
        "",
        "| Семейство | Строк | Русская локализация |",
        "|---|---:|---|",
    ]
    descriptions = {
        "Bite idiom/literal bite": "«аукнется — укусит» / «обернулся — и укусил»",
        "EDEN/Edion/oden": "«ЭДЕМ / Эдион / Эдем — едим»",
        "Horse idiom/pun": "«валять коня»",
        "Lilamon proverb contrast": "«цветок и яд» против «розы и шипов»",
        "Minervamon: gubmint": "намеренное «правитмственное здание»",
        "Nanimon/Nannymon": "«Нанимон / Нянимон / нянчить»",
        "Rhyming shop jingle": "новая русская рифмованная реклама",
        "Twentiest/Dвадцатейшесть": "«двадцатейший / Двадцатейшесть» и острота",
        "Whamon: whale/well": "«вот так кит / китово / китуем / кит с ним»",
    }
    for family in sorted(counts):
        lines.append(f"| {family} | {counts[family]} | {descriptions[family]} |")
    lines += [
        "",
        "Две английские строки, где прямо написано `pun`, входят в семейства про коня",
        "и ЭДЕМ. Менее явные случаи найдены по искажениям (`gubmint`, `any-whale`),",
        "выдуманному термину (`Twentiest`), рифме и контексту сцен.",
        "",
    ]
    SUMMARY.write_text("\n".join(lines), encoding="utf-8")

    print(f"Wordplay rows: {len(rows)}")
    for family in sorted(counts):
        print(f"  {family}: {counts[family]}")
    print(f"Missing rows: {len(missing)}")
    print(f"Wrote: {REPORT.relative_to(ROOT)}")
    print(f"Wrote: {SUMMARY.relative_to(ROOT)}")


if __name__ == "__main__":
    main()

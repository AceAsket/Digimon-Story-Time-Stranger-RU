from __future__ import annotations

import csv
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CHAR_NAMES = ROOT / "csv" / "patch_text01" / "text" / "char_name.mbe" / "000_Sheet1.csv"
COMPARE = ROOT / "exports" / "digimon_name_wiki_compare.csv"
RECOMMENDATIONS = ROOT / "exports" / "digimon_name_recommendations.csv"
OUT = ROOT / "exports" / "digimon_name_changes_applied.csv"


def read_csv_text(text: str) -> list[list[str]]:
    return list(csv.reader(text.splitlines()))


def read_file_rows(path: Path) -> list[list[str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.reader(f))


def main() -> None:
    previous_text = subprocess.check_output(
        ["git", "show", f"HEAD:{CHAR_NAMES.relative_to(ROOT).as_posix()}"],
        cwd=ROOT,
        text=True,
        encoding="utf-8-sig",
    )
    previous = {row[0]: row[1] for row in read_csv_text(previous_text)[1:] if len(row) >= 2}
    current = {row[0]: row[1] for row in read_file_rows(CHAR_NAMES)[1:] if len(row) >= 2}

    compare_by_id: dict[str, dict[str, str]] = {}
    if COMPARE.exists():
        with COMPARE.open("r", encoding="utf-8-sig", newline="") as f:
            compare_by_id = {row["id"]: row for row in csv.DictReader(f)}

    recommendations_by_id: dict[str, dict[str, str]] = {}
    if RECOMMENDATIONS.exists():
        with RECOMMENDATIONS.open("r", encoding="utf-8-sig", newline="") as f:
            recommendations_by_id = {row["id"]: row for row in csv.DictReader(f)}

    applied: list[dict[str, str]] = []
    for row_id, before in previous.items():
        after = current.get(row_id, "")
        if not after or before == after:
            continue
        compare = compare_by_id.get(row_id, {})
        recommendation = recommendations_by_id.get(row_id, {})
        source_url = compare.get("wiki_url") or recommendation.get("source_url", "")
        source_type = "ru_digimon_fandom" if source_url else recommendation.get("source_type", "manual")
        confidence = "medium" if source_url else recommendation.get("confidence", "low")
        if source_url:
            note = "Changed to the selected Russian Digimon Wiki/Fandom form during the name localization pass."
        else:
            note = recommendation.get("note") or "Changed during Digimon name localization pass."
        applied.append(
            {
                "id": row_id,
                "english_name": compare.get("english_name") or recommendation.get("english_name", ""),
                "before": before,
                "after": after,
                "source_type": source_type,
                "source_url": source_url,
                "confidence": confidence,
                "note": note,
            }
        )

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8-sig", newline="") as f:
        fieldnames = ["id", "english_name", "before", "after", "source_type", "source_url", "confidence", "note"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(applied)

    print("changes", len(applied))
    print(OUT)


if __name__ == "__main__":
    main()

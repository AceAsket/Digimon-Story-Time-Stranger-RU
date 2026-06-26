from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RECOMMENDATIONS = ROOT / "exports" / "digimon_name_recommendations.csv"
CHAR_NAMES = ROOT / "csv" / "patch_text01" / "text" / "char_name.mbe" / "000_Sheet1.csv"
LOG = ROOT / "exports" / "digimon_name_changes_applied.csv"


def main() -> None:
    with RECOMMENDATIONS.open("r", encoding="utf-8-sig", newline="") as f:
        recommendations = {
            row["id"]: row
            for row in csv.DictReader(f)
            if row["action"] == "apply" and row["recommended_ru"]
        }

    with CHAR_NAMES.open("r", encoding="utf-8-sig", newline="") as f:
        rows = list(csv.reader(f))

    applied: list[dict[str, str]] = []
    for row in rows[1:]:
        if len(row) < 2:
            continue
        row_id = row[0]
        recommendation = recommendations.get(row_id)
        if not recommendation:
            continue
        before = row[1]
        after = recommendation["recommended_ru"]
        if before == after:
            continue
        row[1] = after
        applied.append(
            {
                "id": row_id,
                "english_name": recommendation["english_name"],
                "before": before,
                "after": after,
                "source_type": recommendation["source_type"],
                "source_url": recommendation["source_url"],
                "confidence": recommendation["confidence"],
                "note": recommendation["note"],
            }
        )

    with CHAR_NAMES.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f, lineterminator="\n")
        writer.writerows(rows)

    LOG.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["id", "english_name", "before", "after", "source_type", "source_url", "confidence", "note"]
    existing: dict[str, dict[str, str]] = {}
    if LOG.exists():
        with LOG.open("r", encoding="utf-8-sig", newline="") as f:
            existing = {row["id"]: row for row in csv.DictReader(f)}
    for row in applied:
        existing[row["id"]] = row

    with LOG.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(existing.values())

    print("applied", len(applied))
    print(LOG)


if __name__ == "__main__":
    main()

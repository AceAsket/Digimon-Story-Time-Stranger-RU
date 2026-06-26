from __future__ import annotations

import csv
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPORTS = ROOT / "exports"
COMPARE = EXPORTS / "digimon_name_wiki_compare.csv"
OUT = EXPORTS / "digimon_name_recommendations.csv"


RU_FANDOM_NOTE = (
    "Russian Digimon Wiki/Fandom is used as a broad community localization fallback; "
    "no complete official Russian glossary was found."
)

NON_DIGIMON_HINTS = {
    "Right Arm",
    "Left Arm",
    "Giant Slayer",
    "Dark Shadow",
}


def normalize_suffix(value: str) -> str:
    value = re.sub(r"\s+", " ", value.strip())
    value = re.sub(r"^П\.\s*", "правая ", value)
    value = re.sub(r"^Л\.\s*", "левая ", value)

    words: list[str] = []
    for word in value.split(" "):
        if re.fullmatch(r"[A-ZА-ЯЁ0-9]{1,3}", word):
            words.append(word)
        else:
            words.append(word[:1].lower() + word[1:])
    return " ".join(words)


def parenthetical_suffix(value: str) -> str:
    match = re.search(r"\(([^()]*)\)\s*$", value)
    return match.group(1) if match else ""


def recommendation_for(row: dict[str, str]) -> dict[str, str]:
    current = row["local_russian_name"]
    wiki = row["wiki_russian_name"].strip()
    status = row["status"]
    note = ""

    recommended = current
    action = "keep"
    source_type = "local_current"
    source_url = ""
    confidence = "low"

    if status == "ok":
        confidence = "high"
        note = "Already matches the selected Russian reference."
    elif wiki:
        recommended = wiki
        suffix = parenthetical_suffix(current)
        if suffix and "(" not in wiki:
            recommended = f"{wiki} ({normalize_suffix(suffix)})"
            note = f"{RU_FANDOM_NOTE} Base name from source; local form suffix preserved."
            confidence = "medium"
        else:
            note = RU_FANDOM_NOTE
            confidence = "medium"

        source_type = "ru_digimon_fandom"
        source_url = row["wiki_url"]
        if recommended != current and row["english_name"] not in NON_DIGIMON_HINTS:
            action = "apply"
    elif status == "no_wiki_match":
        note = "No matching Russian Digimon Wiki/Fandom page found; kept current translation for manual review."
    elif status == "no_wiki_ru_name":
        note = "Matching page found, but no Russian name could be extracted; kept current translation."

    return {
        "#": row["#"],
        "id": row["id"],
        "english_name": row["english_name"],
        "current_ru": current,
        "recommended_ru": recommended,
        "action": action,
        "compare_status": status,
        "wiki_page": row["wiki_page"],
        "source_type": source_type,
        "source_url": source_url,
        "confidence": confidence,
        "note": note,
    }


def main() -> None:
    with COMPARE.open("r", encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))

    recommendations = [recommendation_for(row) for row in rows]

    fieldnames = [
        "#",
        "id",
        "english_name",
        "current_ru",
        "recommended_ru",
        "action",
        "compare_status",
        "wiki_page",
        "source_type",
        "source_url",
        "confidence",
        "note",
    ]
    with OUT.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(recommendations)

    counts: dict[str, int] = {}
    for row in recommendations:
        key = f"{row['action']}:{row['confidence']}"
        counts[key] = counts.get(key, 0) + 1

    print("rows", len(recommendations))
    print("counts", counts)
    print(OUT)


if __name__ == "__main__":
    main()

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

MODE_RECOMMENDATIONS = {
    "char_BELPHEMON_RM": (
        "Бельфемон: Режим ярости",
        "RM = Rage Mode. Mode abbreviation expanded from official English naming.",
        "https://digimon.net/reference_en/detail.php?directory_name=belphemonragemode",
    ),
    "char_BELPHEMON_RM_BIG": (
        "Бельфемон: Режим ярости",
        "RM = Rage Mode. Mode abbreviation expanded from official English naming.",
        "https://digimon.net/reference_en/detail.php?directory_name=belphemonragemode",
    ),
    "char_CHRONOMON_DESTROY": (
        "Хрономон: Режим разрушения",
        "DM = Destroy Mode. Mode abbreviation expanded from official English naming.",
        "https://digimon.net/reference_en/",
    ),
    "char_DUKEMON_CM": (
        "Дюкмон: Багровый режим",
        "CM = Crimson Mode. Mode abbreviation expanded from official English naming.",
        "https://digimon.net/reference_en/detail.php?directory_name=dukemoncrimsonmode",
    ),
    "char_JUNOMON_HYSTERICMODE": (
        "Юномон: Истерический режим",
        "HM = Hysteric Mode. Mode abbreviation expanded from official English naming.",
        "https://digimon.net/reference_en/",
    ),
    "char_JUNOMON_HYSTERICMODE_ADD": (
        "Юномон: Истерический режим (копья)",
        "HM = Hysteric Mode. Mode abbreviation expanded; local form suffix preserved.",
        "https://digimon.net/reference_en/",
    ),
    "char_BELPHEMON_SM": (
        "Бельфемон: Режим сна",
        "SM = Sleep Mode. Mode abbreviation expanded from official English naming.",
        "https://digimon.net/reference_en/detail.php?directory_name=belphemonsleepmode",
    ),
    "char_BELPHEMON_SM_BIG": (
        "Бельфемон: Режим сна",
        "SM = Sleep Mode. Mode abbreviation expanded from official English naming.",
        "https://digimon.net/reference_en/detail.php?directory_name=belphemonsleepmode",
    ),
    "char_BACCHUSMON_DRUNK": (
        "Вакхмон: Режим опьянения",
        "DM = Deisui Mode. Mode abbreviation expanded from Digimon Wiki naming.",
        "https://digimon.fandom.com/wiki/Bacchusmon_%28Deisui_Mode%29",
    ),
    "char_BEELZEMON_BM": (
        "Вельзевумон: Бласт-режим",
        "BM = Blast Mode for Beelzemon/Beelzebumon. Not Burst Mode.",
        "https://digimon.net/reference_en/detail.php?directory_name=beelzebumonblastmode",
    ),
    "char_BEELZEMON_BM_BIG": (
        "Вельзевумон: Бласт-режим",
        "BM = Blast Mode for Beelzemon/Beelzebumon. Not Burst Mode.",
        "https://digimon.net/reference_en/detail.php?directory_name=beelzebumonblastmode",
    ),
    "char_SHINEGREYMON_BM": (
        "Шайн Греймон: Взрывной режим",
        "BM = Burst Mode. Mode abbreviation expanded from official English naming.",
        "https://digimon.net/reference_en/detail.php?directory_name=shinegreymonburstmode",
    ),
    "char_RAVEMON_BM": (
        "Равемон: Взрывной режим",
        "BM = Burst Mode. Mode abbreviation expanded from official English naming.",
        "https://digimon.net/reference_en/detail.php?directory_name=ravmonburstmode",
    ),
    "char_ROSEMON_BM": (
        "Роузмон: Взрывной режим",
        "BM = Burst Mode. Mode abbreviation expanded from official English naming.",
        "https://digimon.net/reference_en/detail.php?directory_name=rosemonburstmode",
    ),
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

    if row["id"] in MODE_RECOMMENDATIONS:
        recommended, note, source_url = MODE_RECOMMENDATIONS[row["id"]]
        source_type = "mode_abbreviation_policy"
        confidence = "medium"
        action = "apply" if recommended != current else "keep"
    elif status == "ok":
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

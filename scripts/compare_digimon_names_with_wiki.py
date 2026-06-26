from __future__ import annotations

import csv
import json
import re
import urllib.parse
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPORTS = ROOT / "exports"
LOCAL_NAMES = EXPORTS / "digimon_names.csv"
OUT_ALL = EXPORTS / "digimon_name_wiki_compare.csv"
OUT_MISMATCHES = EXPORTS / "digimon_name_wiki_mismatches.csv"
OUT_UNMATCHED = EXPORTS / "digimon_name_wiki_unmatched.csv"
CACHE = EXPORTS / ".digimon_wiki_name_cache.json"

API = "https://digimon.fandom.com/ru/api.php"
LIST_URL = (
    "https://digimon.fandom.com/ru/api.php?action=parse&"
    "page=%D0%A1%D0%BF%D0%B8%D1%81%D0%BE%D0%BA_%D0%B4%D0%B8%D0%B3%D0%B8%D0%BC%D0%BE%D0%BD%D0%BE%D0%B2&"
    "prop=links&format=json"
)
USER_AGENT = "Codex local translation comparison for Digimon Story Time Stranger"


SUFFIXES_TO_TRY = [
    "_BIG",
    "_BOSS",
    "_EVENT",
    "_RAMP",
    "_ADD",
    "_ADD1",
    "_ADD2",
    "_ADD3",
    "_ADD4",
    "_A",
    "_B",
    "_C",
    "_E",
    "_BL",
]

MODE_ALIASES = {
    "FM": "Falldown Mode",
    "CM": "Crimson Mode",
    "RM": "Rage Mode",
    "HM": "Hysteric Mode",
    "WM": "Wrath Mode",
    "DM": "Destroy Mode",
}

SPECIAL_ID_ALIASES = {
    "BLACKTAILMON": ["Tailmon (Black)", "Black Tailmon", "BlackGatomon"],
    "V-MON": ["V-mon", "Veemon"],
    "DEMON": ["Demon", "Creepymon"],
    "DEMON_BIG": ["Demon", "Creepymon"],
    "DUKEMON": ["Dukemon", "Gallantmon"],
    "DUKEMON_BIG": ["Dukemon", "Gallantmon"],
    "DUKEMON_CM": ["Dukemon Crimson Mode", "Gallantmon Crimson Mode"],
    "HOLYANGEMON": ["Holy Angemon", "MagnaAngemon"],
    "PICODEVIMON": ["Pico Devimon", "DemiDevimon"],
    "TAILMON": ["Tailmon", "Gatomon"],
    "VAMDEMON": ["Vamdemon", "Myotismon"],
    "BELPHEMON_RM": ["Belphemon Rage Mode"],
    "LUCEMON_FM": ["Lucemon Falldown Mode"],
    "CHRONOMON_DESTROY": ["Chronomon Destroy Mode"],
    "JUPITERMON_WRATHMODE": ["Jupitermon Wrath Mode"],
    "JUPITERMON_WRATHMODE_BIG": ["Jupitermon Wrath Mode"],
    "CHAOSMONVALDURARM": ["Chaosmon Valdur Arm", "Chaosmon: Valdur Arm"],
    "CHAOSMONVALDURARM_BIG": ["Chaosmon Valdur Arm", "Chaosmon: Valdur Arm"],
    "CERESMON_MEDIUM": ["Ceresmon Medium"],
    "CERBERUSMON_WM": ["Cerberumon Werewolf Mode", "Cerberusmon Werewolf Mode"],
    "METALGREYMON_BIG_BL": ["Metal Greymon (Blue)", "MetalGreymon (Blue)"],
}


def get_json(url: str) -> dict:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=45) as response:
        return json.loads(response.read().decode("utf-8"))


def normalize_en(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", value.lower())


def normalize_ru(value: str) -> str:
    value = value.casefold().replace("ё", "е")
    return re.sub(r"[^0-9a-zа-я]+", "", value)


def clean_wikitext_value(value: str) -> str:
    value = re.sub(r"<!--.*?-->", "", value, flags=re.DOTALL)
    value = re.sub(r"<br\s*/?>", " / ", value, flags=re.IGNORECASE)
    value = re.sub(r"\[\[(?:[^|\]]*\|)?([^\]]+)\]\]", r"\1", value)
    value = re.sub(r"''+", "", value)
    value = re.sub(r"<[^>]+>", "", value)
    return value.strip()


def title_case_id(token: str) -> str:
    parts = re.split(r"([_\-\s]+)", token)
    converted: list[str] = []
    for part in parts:
        if not part or re.fullmatch(r"[_\-\s]+", part):
            converted.append(part.replace("_", " "))
        elif part in MODE_ALIASES:
            converted.append(MODE_ALIASES[part])
        elif part.isupper() or part.isdigit():
            converted.append(part[:1].upper() + part[1:].lower())
        else:
            converted.append(part)
    return "".join(converted).strip()


def id_core(row_id: str) -> str:
    return row_id.removeprefix("char_").strip()


def without_known_suffixes(core: str) -> list[str]:
    variants = [core]
    changed = True
    while changed:
        changed = False
        current = variants[-1]
        for suffix in SUFFIXES_TO_TRY:
            if current.endswith(suffix):
                variants.append(current[: -len(suffix)])
                changed = True
                break
    return variants


def candidate_titles(row_id: str, english_name: str) -> list[str]:
    candidates: list[str] = []
    core = id_core(row_id)

    candidates.append(english_name)
    candidates.extend(SPECIAL_ID_ALIASES.get(core, []))

    for variant in without_known_suffixes(core):
        candidates.append(title_case_id(variant))
        candidates.append(title_case_id(variant.replace("_", "")))

        pieces = variant.split("_")
        if pieces and pieces[-1] in MODE_ALIASES:
            candidates.append(f"{title_case_id('_'.join(pieces[:-1]))} {MODE_ALIASES[pieces[-1]]}")

    # Also try removing parenthesized suffixes from the game name.
    candidates.append(re.sub(r"\s*\([^)]*\)", "", english_name).strip())

    result: list[str] = []
    seen: set[str] = set()
    for candidate in candidates:
        candidate = re.sub(r"\s+", " ", candidate).strip()
        if candidate and candidate not in seen:
            seen.add(candidate)
            result.append(candidate)
    return result


def load_local_rows() -> list[dict[str, str]]:
    with LOCAL_NAMES.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def load_wiki_titles() -> dict[str, str]:
    data = get_json(LIST_URL)
    titles = [
        link["*"]
        for link in data["parse"]["links"]
        if link.get("ns") == 0 and "exists" in link
    ]

    mapping: dict[str, str] = {}
    for title in titles:
        mapping.setdefault(normalize_en(title), title)
    return mapping


def extract_ru_name_from_wikitext(content: str) -> str:
    match = re.search(r"(?im)^\s*\|\s*Название\s*=\s*(.*?)\s*$", content)
    if match:
        return clean_wikitext_value(match.group(1))

    match = re.search(r"'''([^']+)'''", content)
    if match:
        return clean_wikitext_value(match.group(1))

    return ""


def fetch_ru_names_for_titles(titles: list[str], cache: dict[str, str]) -> None:
    missing = [title for title in titles if title not in cache]
    for start in range(0, len(missing), 45):
        chunk = missing[start : start + 45]
        url = API + "?" + urllib.parse.urlencode(
            {
                "action": "query",
                "titles": "|".join(chunk),
                "prop": "revisions",
                "rvprop": "content",
                "rvslots": "main",
                "format": "json",
                "formatversion": "2",
                "redirects": "1",
            }
        )
        data = get_json(url)
        redirect_from_to = {
            item.get("from", ""): item.get("to", "")
            for item in data.get("query", {}).get("redirects", [])
        }
        by_title: dict[str, str] = {}
        for page in data.get("query", {}).get("pages", []):
            title = page.get("title", "")
            revisions = page.get("revisions") or []
            content = ""
            if revisions:
                content = revisions[0].get("slots", {}).get("main", {}).get("content", "")
            by_title[title] = extract_ru_name_from_wikitext(content)

        for original in chunk:
            resolved = redirect_from_to.get(original, original)
            cache[original] = by_title.get(resolved, by_title.get(original, ""))


def get_ru_name_for_title_slow_parse(title: str, cache: dict[str, str]) -> str:
    """Fallback retained for odd pages without revision content."""
    if title in cache:
        return cache[title]
    url = API + "?" + urllib.parse.urlencode(
        {
            "action": "parse",
            "page": title,
            "prop": "text",
            "format": "json",
            "redirects": "1",
        }
    )
    data = get_json(url)
    page_html = data.get("parse", {}).get("text", {}).get("*", "")

    match = re.search(
        r'<h2[^>]*data-source="Название"[^>]*>(.*?)</h2>',
        page_html,
        flags=re.IGNORECASE | re.DOTALL,
    )
    if not match:
        match = re.search(
            r'<h2[^>]*class="[^"]*\bpi-title\b[^"]*"[^>]*>(.*?)</h2>',
            page_html,
            flags=re.IGNORECASE | re.DOTALL,
        )

    if match:
        ru_name = clean_wikitext_value(match.group(1))
    else:
        ru_name = ""

    cache[title] = ru_name
    return ru_name


def classify(local_ru: str, wiki_ru: str, wiki_title: str) -> str:
    if not wiki_title:
        return "no_wiki_match"
    if not wiki_ru:
        return "no_wiki_ru_name"
    if local_ru == wiki_ru:
        return "ok"
    if normalize_ru(local_ru) == normalize_ru(wiki_ru):
        return "punct_case_or_yo"
    return "different"


def main() -> None:
    EXPORTS.mkdir(parents=True, exist_ok=True)
    local_rows = load_local_rows()
    title_map = load_wiki_titles()
    cache = json.loads(CACHE.read_text(encoding="utf-8")) if CACHE.exists() else {}

    output_rows: list[dict[str, str]] = []
    titles_needed: set[str] = set()

    for row in local_rows:
        row_id = row["id"]
        english_name = row["english_name"]
        wiki_title = ""
        matched_by = ""
        matched_candidate = ""

        for candidate in candidate_titles(row_id, english_name):
            key = normalize_en(candidate)
            if key in title_map:
                wiki_title = title_map[key]
                matched_by = "candidate"
                matched_candidate = candidate
                break

        if wiki_title:
            titles_needed.add(wiki_title)

        output_rows.append(
            {
                "#": row["#"],
                "id": row_id,
                "english_name": english_name,
                "local_russian_name": row["russian_name"],
                "wiki_page": wiki_title,
                "wiki_russian_name": "",
                "status": "",
                "matched_by": matched_by,
                "matched_candidate": matched_candidate,
                "wiki_url": f"https://digimon.fandom.com/ru/wiki/{urllib.parse.quote(wiki_title.replace(' ', '_'))}"
                if wiki_title
                else "",
            }
        )

    fetch_ru_names_for_titles(sorted(titles_needed), cache)
    CACHE.write_text(json.dumps(cache, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")

    for row in output_rows:
        wiki_title = row["wiki_page"]
        wiki_ru = cache.get(wiki_title, "") if wiki_title else ""
        row["wiki_russian_name"] = wiki_ru
        row["status"] = classify(row["local_russian_name"], wiki_ru, wiki_title)

    fieldnames = [
        "#",
        "id",
        "english_name",
        "local_russian_name",
        "wiki_page",
        "wiki_russian_name",
        "status",
        "matched_by",
        "matched_candidate",
        "wiki_url",
    ]

    with OUT_ALL.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(output_rows)

    mismatches = [row for row in output_rows if row["status"] not in {"ok"}]
    with OUT_MISMATCHES.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(mismatches)

    unmatched = [row for row in output_rows if row["status"] == "no_wiki_match"]
    with OUT_UNMATCHED.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(unmatched)

    counts: dict[str, int] = {}
    for row in output_rows:
        counts[row["status"]] = counts.get(row["status"], 0) + 1

    print("total", len(output_rows))
    print("counts", counts)
    print(OUT_ALL)
    print(OUT_MISMATCHES)
    print(OUT_UNMATCHED)


if __name__ == "__main__":
    main()

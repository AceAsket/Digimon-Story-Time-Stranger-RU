from __future__ import annotations

import csv
import re
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CSV_ROOT = ROOT / "csv"
OUT_PATH = ROOT / "exports" / "translation_quality_audit_v025.csv"

SCAN_ROOTS = [
    CSV_ROOT / "patch_text01",
    CSV_ROOT / "addcont_01_text01",
    CSV_ROOT / "addcont_02_text01",
    CSV_ROOT / "app_text01",
]

LATIN_RE = re.compile(r"[A-Za-z]{3,}")
CYRILLIC_RE = re.compile(r"[А-Яа-яЁё]")
TAG_RE = re.compile(r"\{[^}]*\}|image\([^)]*\)|ui_[A-Za-z0-9_]+|[A-Za-z0-9_]+_[A-Za-z0-9_]+")

ALLOWED_TOKENS = {
    "ADAMAS",
    "ATK",
    "BGM",
    "CRT",
    "DLC",
    "DNA",
    "D-SAT",
    "DATS",
    "DEF",
    "DMW",
    "ENG",
    "EXP",
    "HP",
    "INT",
    "JPN",
    "LV",
    "OK",
    "SP",
    "SPD",
    "USB",
}

ALLOWED_WORDS = {
    "Cyber",
    "Digimon",
    "PlayStation",
    "Store",
    "Steam",
    "Time",
    "Stranger",
    "Alter",
    "Defeat",
}

MACHINE_PATTERNS = [
    ("machine:calque", re.compile(pattern, re.IGNORECASE))
    for pattern in [
        r"на руках несколько хлопотн",
        r"несколько хлопотное дело",
        r"нижнем мире",
        r"Дигиволв",
        r"\bНовичок\b",
        r"\bБийомон\b",
        r"\bзасню\b",
        r"переключить информацию",
        r"журнал регистрации",
        r"Оборудовать все",
        r"В коробке",
        r"Автонайти",
        r"De-эвол",
        r"No Text",
        r"Changed to",
        r"удовлетвор[её]н[аоы]?\b",
        r"явля(?:ет|ются|юсь|лся|лась)",
        r"осуществ",
        r"касательно|относительно",
        r"на данный момент",
        r"позволили цели",
        r"с вашей стороны|с твоей стороны",
    ]
]


def read_rows(path: Path) -> list[list[str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.reader(f))


def text_column(path: Path, row: list[str]) -> int | None:
    if "message" in path.parts:
        return 2 if len(row) > 2 else None
    return 1 if len(row) > 1 else None


def strip_technical(text: str) -> str:
    text = TAG_RE.sub(" ", text)
    text = re.sub(r"\b[a-z]\d{2,4}_[A-Za-z0-9_]+\b", " ", text)
    text = re.sub(r"\b\d{6,}(?:_[MF])?\b", " ", text)
    return text


def suspicious_latin_words(text: str) -> list[str]:
    clean = strip_technical(text)
    words: list[str] = []
    for word in LATIN_RE.findall(clean):
        if word.upper() in ALLOWED_TOKENS or word in ALLOWED_WORDS:
            continue
        if word.startswith("fc") or word.startswith("is") or (word.startswith("d") and word[1:].isdigit()):
            continue
        words.append(word)
    return words


def category_for(text: str) -> tuple[str | None, str]:
    words = suspicious_latin_words(text)
    has_cyrillic = bool(CYRILLIC_RE.search(text))
    if words and not has_cyrillic:
        return "english:full", ", ".join(sorted(set(words))[:12])
    if words and has_cyrillic:
        return "english:mixed", ", ".join(sorted(set(words))[:12])
    for category, pattern in MACHINE_PATTERNS:
        match = pattern.search(text)
        if match:
            return category, match.group(0)
    if any(len(line) > 115 for line in text.splitlines()) and ("message" in text or len(text) > 115):
        return "layout:long_line", f"{max(len(line) for line in text.splitlines())} chars"
    return None, ""


def main() -> None:
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    audit_rows: list[list[str]] = [
        ["category", "root", "relative_path", "row_id", "line", "detail", "text"]
    ]
    counts: Counter[str] = Counter()

    for root in SCAN_ROOTS:
        if not root.exists():
            continue
        for path in sorted(root.rglob("*.csv")):
            relative = path.relative_to(root).as_posix()
            for line_no, row in enumerate(read_rows(path), start=1):
                if line_no == 1 or not row:
                    continue
                column = text_column(path, row)
                if column is None:
                    continue
                text = row[column]
                category, detail = category_for(text)
                if not category:
                    continue
                counts[category] += 1
                audit_rows.append([category, root.name, relative, row[0], str(line_no), detail, text])

    with OUT_PATH.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f, lineterminator="\n")
        writer.writerows(audit_rows)

    print(f"Wrote {len(audit_rows) - 1} audit rows to {OUT_PATH.relative_to(ROOT)}")
    for category, count in counts.most_common():
        print(f"{category}: {count}")


if __name__ == "__main__":
    main()

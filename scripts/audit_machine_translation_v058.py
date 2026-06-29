from __future__ import annotations

import csv
import re
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CSV_ROOT = ROOT / "csv"
ORIG_ROOT = ROOT / "analysis" / "game_text01_compare_v030" / "original_csv"
OUT_CSV = ROOT / "exports" / "translation_machine_audit_v058.csv"
OUT_SUMMARY = ROOT / "exports" / "translation_machine_audit_v058_summary.txt"

TAG_RE = re.compile(r"\{[^}]*\}|\[[^\]]*\]|image\([^)]*\)")
LATIN_RE = re.compile(r"[A-Za-z]{3,}")
CYRILLIC_RE = re.compile(r"[А-Яа-яЁё]")

ALLOW_LATIN_PHRASES = {
    "Accel Arm",
    "Alter-B",
    "Alter-S",
    "BAN-TYO",
    "Believer",
    "Black Hickeys",
    "Blitz Arm",
    "Critical Arm",
    "Cyber Sleuth",
    "DIGIFARM",
    "DIGIMON BEATBREAK",
    "Digimon Data Squad",
    "Digimon Fusion Battles",
    "Digimon Savers",
    "Digimon Story: Cyber Sleuth",
    "Digimon Xros Wars",
    "Freeze Bomber",
    "GAKU-RAN",
    "Garuru Hou",
    "Golden Bats",
    "Gouing! Going! My soul!!",
    "Grey Tou",
    "Hootle",
    "Kanshaku Dust",
    "Little Bearmon",
    "Marsmon's Makino",
    "Nebagiba",
    "Nightmare Assemble",
    "Omega inForce",
    "Olympus XII",
    "Photon Spreads",
    "Taiko no Tatsujin",
    "Tales of Arise",
    "Tense-Great Shield",
    "The Idolmaster",
    "THE IDOLM@STER",
    "Ulforce",
    "WE ARE Xros Heart",
    "ZERO-ARMS",
    "Zwart Defeat",
}

ALLOW_LATIN = {
    "ADAMAS",
    "AIDA",
    "Anti",
    "Arts",
    "BGM",
    "CP",
    "CRT",
    "Cyber",
    "D-SAT",
    "DATS",
    "DLC",
    "DMW",
    "DNA",
    "DigiLine",
    "Digimon",
    "ENG",
    "EXP",
    "HP",
    "INT",
    "JPN",
    "LV",
    "Microsoft",
    "Nintendo",
    "OK",
    "ParadoX",
    "PlayStation",
    "SDGP",
    "SP",
    "SPD",
    "Steam",
    "Store",
    "Stranger",
    "Time",
    "USB",
    "Xros",
    "eShop",
}

TEXTUAL_DIRS = {"message", "text"}

# priority: 5 = urgent visible/likely wrong, 1 = low-confidence style smell
PATTERNS: list[tuple[int, str, str, re.Pattern[str], str]] = [
    (
        5,
        "encoding",
        "mojibake/битая кодировка",
        re.compile(r"вЂ|Р|Рџ|РЎ|Рќ|Р“|Р”|Рљ|Рњ|Рћ|Р§|Рђ|Р‘|Р’|Р—|Р™"),
        "битая кодировка",
    ),
    (
        5,
        "machine_exact",
        "старый машинный хвост",
        re.compile(r"обожал в прошлом|не то чтобы я мог|Прийти в переулки|прийти в переулки|No Text|Changed to", re.I),
        "точная машинная калька",
    ),
    (
        5,
        "punctuation",
        "пробел перед знаком препинания",
        re.compile(r"\s+[?!]|\s+\.\.\."),
        "видимый машинный пробел перед пунктуацией",
    ),
    (
        5,
        "style",
        "смешение ты/вы в одной реплике",
        re.compile(r"\bты\b.*\bвы\b|\bвы\b.*\bты\b", re.I | re.S),
        "возможное смешение обращения",
    ),
    (4, "machine_phrase", "в настоящее время", re.compile(r"\bв настоящее время\b", re.I), "канцелярит/currently"),
    (4, "machine_phrase", "на данный момент", re.compile(r"\bна данный момент\b", re.I), "канцелярит/at the moment"),
    (4, "machine_phrase", "тот факт/факт, что", re.compile(r"\bтот факт\b|\bфакт, что\b", re.I), "английский каркас the fact that"),
    (
        4,
        "machine_phrase",
        "с вашей/твоей стороны",
        re.compile(r"\bс вашей стороны\b|\bс твоей стороны\b", re.I),
        "английский каркас on your side/part",
    ),
    (
        4,
        "machine_phrase",
        "сделал(а) меня/делает меня",
        re.compile(r"\b(сделал[аи]?|дела(?:ет|ют))\s+меня\b", re.I),
        "английский make me",
    ),
    (
        4,
        "machine_phrase",
        "как реагирует/показывает",
        re.compile(r"\bкак реагирует\b|\bплохо это показывает\b", re.I),
        "буквальная калька",
    ),
    (4, "machine_phrase", "осуществил/осуществить", re.compile(r"\bосуществ\w*\b", re.I), "часто машинный выбор слова"),
    (4, "machine_phrase", "удовлетворение/удовлетворён", re.compile(r"\bудовлетвор\w*\b", re.I), "часто literal satisfied"),
    (
        4,
        "machine_phrase",
        "кажется, что является",
        re.compile(r"кажется,\s*что[^\n]{0,80}\bявля\w*", re.I),
        "двойная калька seems/is",
    ),
    (
        4,
        "machine_phrase",
        "который/что является",
        re.compile(r"\b(котор(?:ый|ая|ое|ые)|что)\s+явля\w*\b", re.I),
        "буквальное which is/that is",
    ),
    (
        3,
        "machine_phrase",
        "является/являются",
        re.compile(r"\bявля(?:ет|ются|юсь|лся|лась|лось|лись)\w*\b", re.I),
        "возможный канцелярит is/are",
    ),
    (3, "machine_phrase", "данный/данные", re.compile(r"\bданн(?:ый|ая|ое|ые|ого|ому|ыми|ых)\b", re.I), "канцелярит this/given"),
    (3, "machine_phrase", "относительно/касательно", re.compile(r"\bотносительно\b|\bкасательно\b", re.I), "часто буквальное regarding"),
    (
        3,
        "machine_phrase",
        "присутствие/наличие",
        re.compile(r"\bприсутстви[еяию]\b|\bналичи[еяию]\b", re.I),
        "часто тяжеловесная калька",
    ),
    (3, "machine_phrase", "в полевых условиях", re.compile(r"\bв полевых условиях\b", re.I), "буквальная калька field"),
    (3, "machine_phrase", "в процессе", re.compile(r"\bв процессе\b", re.I), "часто канцелярит"),
    (3, "machine_phrase", "позволяет/позволят цели", re.compile(r"\bпозвол\w+\s+цел[иь]\b", re.I), "неестественное allows target"),
    (3, "machine_phrase", "по мере их/его/её", re.compile(r"\bпо мере (?:их|его|е[ёе])\b", re.I), "часто буквальное as they/it"),
    (3, "machine_phrase", "не могу сказать много", re.compile(r"\bне могу сказать много\b", re.I), "буквальное I cannot say much"),
    (
        3,
        "machine_phrase",
        "довольно/действительно/различные перегруз",
        re.compile(r"\bдовольно\b|\bдействительно\b|\bразличн(?:ые|ых|ым|ыми)\b", re.I),
        "проверить на машинную избыточность",
    ),
    (2, "layout", "очень длинная строка", re.compile(r".{125,}"), "риск влезания/читабельности"),
]


def text_column(path: Path, row: list[str]) -> int | None:
    parts = set(path.parts)
    if "message" in parts:
        return 2 if len(row) > 2 else None
    if "text" in parts:
        return 1 if len(row) > 1 else None
    return None


def speaker_column(path: Path, row: list[str]) -> str:
    return row[1] if "message" in path.parts and len(row) > 1 else ""


def clean_for_latin(text: str) -> str:
    text = TAG_RE.sub(" ", text)
    for phrase in sorted(ALLOW_LATIN_PHRASES, key=len, reverse=True):
        text = re.sub(re.escape(phrase), " ", text, flags=re.I)
    return re.sub(
        r"\b(?:ui|vo|char|icon|tutorial|quest|field|main|sub|dlc|s|m|d|f|g|r|t)_?[A-Za-z0-9_]+\b",
        " ",
        text,
    )


def latin_issue(text: str) -> tuple[int, str, str] | None:
    cleaned = clean_for_latin(text)
    words = [
        word
        for word in LATIN_RE.findall(cleaned)
        if word not in ALLOW_LATIN and word.upper() not in ALLOW_LATIN
    ]
    if not words:
        return None
    unique = sorted(set(words))[:12]
    has_cyrillic = bool(CYRILLIC_RE.search(cleaned))
    latin_len = sum(len(word) for word in words)
    if not has_cyrillic and latin_len >= 12:
        return 5, "english_full", "полностью/почти полностью английская строка: " + ", ".join(unique)
    if has_cyrillic and latin_len >= 10:
        return 4, "english_mixed", "английский хвост в русской строке: " + ", ".join(unique)
    return None


def scope_for(rel: Path) -> str:
    rel_posix = rel.as_posix()
    if rel_posix.startswith("message/"):
        return "dialogue"
    if "digimon_profile" in rel_posix:
        return "profile"
    if "tutorial" in rel_posix or "help" in rel_posix:
        return "tutorial/help"
    if "digitter" in rel_posix:
        return "digitter"
    if "common_message" in rel_posix or "yes_no" in rel_posix or "info_message" in rel_posix:
        return "ui/system"
    return "text"


def source_text(package: str, rel: Path, key: str, column: int) -> str:
    path = ORIG_ROOT / package / rel
    if not path.exists():
        return ""
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as f:
            for row in csv.reader(f):
                if row and row[0] == key and len(row) > column:
                    return row[column]
    except OSError:
        return ""
    return ""


def clean_output_text(text: str) -> str:
    return "\n".join(line.rstrip() for line in text.replace("\r\n", "\n").replace("\r", "\n").split("\n"))


def adjusted_priority(priority: int, category: str, reason: str, scope: str) -> int:
    if scope == "profile" and category == "machine_phrase" and "является" in reason:
        return min(priority, 2)
    if scope in {"tutorial/help", "ui/system"} and reason in {
        "данный/данные",
        "присутствие/наличие",
        "довольно/действительно/различные перегруз",
    }:
        return min(priority, 2)
    return priority


def audit() -> list[dict[str, str | int]]:
    rows: list[dict[str, str | int]] = []
    seen: set[tuple[str, str, str, str]] = set()

    for package_root in sorted(path for path in CSV_ROOT.iterdir() if path.is_dir()):
        package = package_root.name
        for path in sorted(package_root.rglob("*.csv")):
            rel = path.relative_to(package_root)
            if not (set(rel.parts) & TEXTUAL_DIRS):
                continue
            with path.open("r", encoding="utf-8-sig", newline="") as f:
                data = list(csv.reader(f))
            for line_no, row in enumerate(data, 1):
                if not row or (line_no == 1 and row[0].startswith("string")):
                    continue
                column = text_column(rel, row)
                if column is None or len(row) <= column:
                    continue
                text = row[column].strip()
                if not text:
                    continue
                key = row[0]
                speaker = speaker_column(rel, row)
                scope = scope_for(rel)
                issues: list[tuple[int, str, str, str]] = []

                latin = latin_issue(text)
                if latin:
                    priority, category, reason = latin
                    issues.append((priority, category, reason, ""))

                for priority, category, reason, pattern, _detail in PATTERNS:
                    match = pattern.search(text)
                    if not match:
                        continue
                    issues.append(
                        (
                            adjusted_priority(priority, category, reason, scope),
                            category,
                            reason,
                            match.group(0),
                        )
                    )

                for priority, category, reason, match in issues:
                    marker = (package, rel.as_posix(), key, reason)
                    if marker in seen:
                        continue
                    seen.add(marker)
                    rows.append(
                        {
                            "priority": priority,
                            "category": category,
                            "reason": reason,
                            "match": match,
                            "scope": scope,
                            "package": package,
                            "file": rel.as_posix(),
                            "line": line_no,
                            "key": key,
                            "speaker": speaker,
                            "source_en": clean_output_text(source_text(package, rel, key, column)),
                            "current_ru": clean_output_text(text),
                        }
                    )

    rows.sort(
        key=lambda row: (
            -int(row["priority"]),
            str(row["category"]),
            str(row["scope"]),
            str(row["package"]),
            str(row["file"]),
            str(row["key"]),
        )
    )
    return rows


def write_outputs(rows: list[dict[str, str | int]]) -> None:
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "priority",
        "category",
        "reason",
        "match",
        "scope",
        "package",
        "file",
        "line",
        "key",
        "speaker",
        "source_en",
        "current_ru",
    ]
    with OUT_CSV.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    by_priority = Counter(int(row["priority"]) for row in rows)
    by_category = Counter(str(row["category"]) for row in rows)
    by_scope = Counter(str(row["scope"]) for row in rows)
    by_reason = Counter(str(row["reason"]) for row in rows)
    with OUT_SUMMARY.open("w", encoding="utf-8") as f:
        f.write("Translation machine audit v058\n")
        f.write(f"rows={len(rows)}\n")
        f.write("\nBy priority:\n")
        for priority in sorted(by_priority, reverse=True):
            f.write(f"- P{priority}: {by_priority[priority]}\n")
        f.write("\nBy category:\n")
        for category, count in by_category.most_common():
            f.write(f"- {category}: {count}\n")
        f.write("\nBy scope:\n")
        for scope, count in by_scope.most_common():
            f.write(f"- {scope}: {count}\n")
        f.write("\nTop reasons:\n")
        for reason, count in by_reason.most_common(30):
            f.write(f"- {reason}: {count}\n")


def main() -> None:
    rows = audit()
    write_outputs(rows)
    print(f"Wrote {len(rows)} rows to {OUT_CSV.relative_to(ROOT)}")
    counts = Counter(int(row["priority"]) for row in rows)
    print("Priorities:", dict(sorted(counts.items(), reverse=True)))
    categories = Counter(str(row["category"]) for row in rows)
    print("Categories:", dict(categories.most_common(12)))


if __name__ == "__main__":
    main()

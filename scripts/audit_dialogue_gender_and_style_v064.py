from __future__ import annotations

import argparse
import csv
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CSV_ROOT = ROOT / "csv"
DEFAULT_ORIGINAL_ROOT = ROOT / "verify" / "game_build_23514637" / "text_original"
DEFAULT_OUT = ROOT / "exports" / "dialogue_gender_style_audit_v065.csv"
DEFAULT_SUMMARY = ROOT / "exports" / "dialogue_gender_style_audit_v065_summary.txt"

CYRILLIC_RE = re.compile(r"[А-Яа-яЁё]")
LATIN_RE = re.compile(r"[A-Za-z][A-Za-z'&.-]{2,}")
WORD_RE = re.compile(r"[А-Яа-яЁё]+")
TAG_RE = re.compile(r"\{[^}]*\}|\[[^]]*]|image\([^)]*\)")
MOJIBAKE_RE = re.compile(r"вЂ|Р|Рџ|РЎ|Рќ|Р“|Р”|Рљ|Рњ|Рћ|Р§|Рђ|Р‘|Р’|Р—|Р™")

PLAYER_IDS = {"char_PLAYER", "char_PLAYER_M", "char_PLAYER_F"}
OPERATOR_IDS = {"char_OPERATOR", "char_OPERATOR_M", "char_OPERATOR_F"}
FIRST_PERSON = {"я", "мне", "меня", "мной", "мой", "моя", "моё", "мое", "мою", "мои"}
SECOND_PERSON = {
    "ты",
    "тебя",
    "тебе",
    "тобой",
    "твой",
    "твоя",
    "твоё",
    "твое",
    "твою",
    "твои",
}

# Curated forms are intentionally conservative. The audit should find visible
# player/operator mistakes without treating every past-tense verb in the game
# as a gender issue.
MALE_FORMS = {
    "был",
    "готов",
    "рад",
    "прав",
    "уверен",
    "должен",
    "сам",
    "один",
    "жив",
    "ранен",
    "потрясён",
    "потрясен",
    "виноват",
    "согласен",
    "сделал",
    "решил",
    "пришёл",
    "пришел",
    "ушёл",
    "ушел",
    "вернулся",
    "родился",
    "испугался",
    "смог",
    "хотел",
    "думал",
    "знал",
    "видел",
    "сказал",
    "нашёл",
    "нашел",
    "получил",
    "попал",
    "устал",
    "спасён",
    "спасен",
    "назначен",
    "выбран",
    "отправлен",
}

FEMALE_FORMS = {
    "была",
    "готова",
    "рада",
    "права",
    "уверена",
    "должна",
    "сама",
    "одна",
    "жива",
    "ранена",
    "потрясена",
    "виновата",
    "согласна",
    "сделала",
    "решила",
    "пришла",
    "ушла",
    "вернулась",
    "родилась",
    "испугалась",
    "смогла",
    "хотела",
    "думала",
    "знала",
    "видела",
    "сказала",
    "нашла",
    "получила",
    "попала",
    "устала",
    "спасена",
    "назначена",
    "выбрана",
    "отправлена",
}

GENDER_FORMS = MALE_FORMS | FEMALE_FORMS

ALLOWED_LATIN = {
    "ADAMAS",
    "AIDA",
    "ATK",
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

ALLOWED_PHRASES = {
    "Accel Arm",
    "Alter-B",
    "Alter-S",
    "BAN-TYO",
    "Black Hickeys",
    "Blitz Arm",
    "Critical Arm",
    "Cyber Sleuth",
    "DIGIMON BEATBREAK",
    "Digimon Data Squad",
    "Digimon Story: Cyber Sleuth",
    "Freeze Bomber",
    "GAKU-RAN",
    "Golden Bats",
    "Grey Tou",
    "Little Bearmon",
    "Marsmon's Makino",
    "Omega inForce",
    "AltaVision",
    "Olympus XII",
    "Taiko no Tatsujin",
    "Tales of Arise",
    "THE IDOLM@STER",
    "ZERO-ARMS",
}

MACHINE_PATTERNS: list[tuple[int, str, re.Pattern[str], str]] = [
    (5, "machine_exact", re.compile(r"обожал в прошлом|не то чтобы я мог|приударили|No Text|Changed to", re.I), "явный машинный хвост"),
    (5, "literal_idiom", re.compile(r"сделк[аи]\s+\d+\s+в\s+\d+|выброс\w*\s+полотенц|если бы это зависело от меня", re.I), "буквально переведённая английская идиома"),
    (5, "machine_exact", re.compile(r"преобразоват\w*\s+эволюционировать|режим\w*\s+серийн\w*\s+съ[её]м", re.I), "ошибочный машинный термин или дубль"),
    (5, "broken_repeat", re.compile(r"ловлю себя на том, что ловлю себя", re.I), "ошибочный повтор фразы"),
    (5, "punctuation", re.compile(r"[ \t]+[?!]|[ \t]+\.\.\."), "пробел перед знаком препинания"),
    (5, "address_mix", re.compile(r"\bты\b.*\bвы\b|\bвы\b.*\bты\b", re.I | re.S), "возможное смешение ты/вы"),
    (4, "machine_phrase", re.compile(r"\bв настоящее время\b|\bна данный момент\b", re.I), "канцелярская калька времени"),
    (4, "machine_phrase", re.compile(r"\bтот факт\b|\bфакт, что\b", re.I), "калька the fact that"),
    (4, "machine_phrase", re.compile(r"\bс вашей стороны\b|\bс твоей стороны\b", re.I), "калька on your side/part"),
    (4, "machine_phrase", re.compile(r"\bне могу сказать много\b", re.I), "буквальное I cannot say much"),
    (4, "machine_phrase", re.compile(r"\bкак насч[её]т того, чтобы\b|\b(?:если\s+)?это то, что\b", re.I), "буквальный английский каркас фразы"),
    (4, "machine_phrase", re.compile(r"\bбольшой помощью\b|\bтепл\w* и пушист\w* внутри\b|\bпора набухаться\b", re.I), "явная лексическая калька"),
    (4, "machine_phrase", re.compile(r"кажется,\s*что[^\n]{0,80}\bявля\w*", re.I), "двойная калька seems/is"),
    (3, "machine_phrase", re.compile(r"\b(?:котор(?:ый|ая|ое|ые)|что)\s+явля\w*", re.I), "буквальное which/that is"),
    (3, "machine_phrase", re.compile(r"\bосуществ\w*\b|\bкасательно\b", re.I), "тяжеловесный машинный выбор слова"),
    (3, "machine_phrase", re.compile(r"\bв полевых условиях\b|\bне могу сказать много\b", re.I), "буквальная калька"),
    (2, "style_review", re.compile(r"\bявля(?:ет|ются|юсь|лся|лась|лось|лись)\w*\b", re.I), "проверить канцелярское является"),
    (2, "style_review", re.compile(r"\bдовольно\b|\bдействительно\b", re.I), "проверить машинный усилитель"),
]


@dataclass(frozen=True)
class DialogueRow:
    package: str
    relative_file: str
    line: int
    row_id: str
    speaker: str
    text: str
    tags: str


def read_rows(path: Path) -> list[list[str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.reader(handle))


def collect_dialogue(package: str, package_root: Path) -> list[DialogueRow]:
    result: list[DialogueRow] = []
    message_root = package_root / "message"
    if not message_root.exists():
        return result
    for path in sorted(message_root.rglob("000_Sheet1.csv")):
        relative = path.relative_to(package_root).as_posix()
        for line, row in enumerate(read_rows(path), start=1):
            if line == 1 or len(row) < 3:
                continue
            # Runtime M/F variants are intentionally gendered and mirror a
            # reviewed base row.  Auditing them as ordinary dialogue would
            # re-introduce expected masculine/feminine forms as false hits.
            if row[0].endswith(("__H", "__F")):
                continue
            result.append(
                DialogueRow(
                    package=package,
                    relative_file=relative,
                    line=line,
                    row_id=row[0],
                    speaker=row[1],
                    text=row[2],
                    tags=row[3] if len(row) > 3 else "",
                )
            )
    return result


def original_package_root(original_root: Path, package: str) -> Path:
    direct = original_root / package / "csv"
    if direct.exists():
        return direct
    return original_root / package


def collect_originals(original_root: Path) -> dict[tuple[str, str, str], str]:
    result: dict[tuple[str, str, str], str] = {}
    for package_dir in sorted(path for path in original_root.iterdir() if path.is_dir()):
        package = package_dir.name
        for row in collect_dialogue(package, original_package_root(original_root, package)):
            result[(package, row.relative_file, row.row_id)] = row.text
    return result


def source_text(originals: dict[tuple[str, str, str], str], row: DialogueRow) -> str:
    direct = originals.get((row.package, row.relative_file, row.row_id))
    if direct is not None:
        return direct
    if row.package == "patch_text01":
        return originals.get(("app_text01", row.relative_file, row.row_id), "")
    return ""


def clean_text(value: str) -> str:
    return "\n".join(line.rstrip() for line in value.replace("\r\n", "\n").replace("\r", "\n").split("\n"))


def sentences(value: str) -> list[str]:
    return [part.strip() for part in re.split(r"(?<=[.!?…])\s+|\n+", value) if part.strip()]


def words(value: str) -> set[str]:
    return {word.lower() for word in WORD_RE.findall(value)}


def alias_pair(tags: str) -> bool:
    tokens = tags.split()
    return any(token.endswith("_M") for token in tokens) and any(token.endswith("_F") for token in tokens)


GENDER_FORM_PATTERN = "|".join(sorted(map(re.escape, GENDER_FORMS), key=len, reverse=True))
DIRECT_FIRST_RE = re.compile(
    rf"\bя\s+(?:(?:бы|не|ничего|полностью|это)\s+){{0,3}}(?P<form>{GENDER_FORM_PATTERN})\b"
    rf"|\b(?P<form_before>{GENDER_FORM_PATTERN})\s+бы\s+я\b",
    re.I,
)
DIRECT_SECOND_RE = re.compile(
    rf"\bты\s+(?:(?:бы|не|ведь|же|это)\s+){{0,2}}(?P<form>{GENDER_FORM_PATTERN})\b",
    re.I,
)
DIRECT_FIRST_SPECIAL_RE = re.compile(r"\b(?:я\s+сам(?:а)?|остаюсь\s+один|останусь\s+один)\b", re.I)


def direct_gender_forms(pattern: re.Pattern[str], value: str) -> set[str]:
    result: set[str] = set()
    for match in pattern.finditer(value):
        for group in match.groups():
            if group and group.lower() in GENDER_FORMS:
                result.add(group.lower())
    return result


def gender_issues(row: DialogueRow) -> list[tuple[int, str, str, str]]:
    issues: list[tuple[int, str, str, str]] = []
    shared = alias_pair(row.tags)
    for sentence in sentences(row.text):
        token_words = words(sentence)
        forms = sorted(token_words & GENDER_FORMS)
        if not forms:
            continue
        first_forms = direct_gender_forms(DIRECT_FIRST_RE, sentence)
        if DIRECT_FIRST_SPECIAL_RE.search(sentence):
            first_forms.update(set(forms) & {"сам", "сама", "один", "одна"})
        second_forms = direct_gender_forms(DIRECT_SECOND_RE, sentence)
        form_text = " ".join(sorted(first_forms or second_forms or set(forms)))

        if row.speaker in PLAYER_IDS and first_forms:
            issues.append((5, "player_self_gender", form_text, "нужны мужской и женский варианты либо нейтральная реплика"))
        elif row.speaker in OPERATOR_IDS and first_forms:
            issues.append((5, "operator_self_gender", form_text, "род Оператора противоположен роду выбранного героя"))
        elif second_forms and (shared or row.speaker in OPERATOR_IDS):
            issues.append((5, "player_address_gender", form_text, "общая M/F-строка обращается к игроку в одном роде"))
        elif second_forms:
            issues.append((4, "possible_player_address_gender", form_text, "проверить, относится ли форма к игроку"))
    return issues


def latin_issue(text: str) -> tuple[int, str, str, str] | None:
    cleaned = TAG_RE.sub(" ", text)
    for phrase in sorted(ALLOWED_PHRASES, key=len, reverse=True):
        cleaned = re.sub(re.escape(phrase), " ", cleaned, flags=re.I)
    cleaned = re.sub(r"\b(?:ui|vo|char|icon|tutorial|quest|field|main|sub|dlc)_[A-Za-z0-9_]+\b", " ", cleaned)
    hits = [word for word in LATIN_RE.findall(cleaned) if word not in ALLOWED_LATIN and word.upper() not in ALLOWED_LATIN]
    if not hits:
        return None
    unique = ", ".join(sorted(set(hits))[:12])
    if not CYRILLIC_RE.search(cleaned):
        return 5, "english_full", unique, "непереведённая английская строка"
    if sum(map(len, hits)) >= 10:
        return 4, "english_mixed", unique, "проверить английский хвост или добавить термин в allowlist"
    return None


def structural_issues(text: str) -> list[tuple[int, str, str, str]]:
    issues: list[tuple[int, str, str, str]] = []
    if MOJIBAKE_RE.search(text):
        issues.append((5, "mojibake", "битая кодировка", "исправить до сборки"))
    if "\ufffd" in text:
        issues.append((5, "replacement_character", "U+FFFD", "восстановить повреждённый символ"))
    for previous, following in zip(text.splitlines(), text.splitlines()[1:]):
        previous = previous.strip()
        if previous.endswith(("...", "…", "...\"", "...»", "…\"", "…»")):
            continue
        if re.match(r"^(?:и|но|а)\s+[«\"]", following.strip(), re.I):
            continue
        if re.search(r"[.!?][\"»']?$", previous) and re.match(r"^[а-яё]", following.strip()):
            issues.append((4, "lowercase_after_sentence", following.strip()[:40], "проверить сломанную границу предложения"))
            break
    return issues


def machine_issues(text: str) -> list[tuple[int, str, str, str]]:
    issues: list[tuple[int, str, str, str]] = []
    for priority, category, pattern, reason in MACHINE_PATTERNS:
        match = pattern.search(text)
        if match:
            issues.append((priority, category, match.group(0), reason))
    return issues


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit all translated dialogue for gender and machine-translation risks.")
    parser.add_argument("--csv-root", type=Path, default=DEFAULT_CSV_ROOT)
    parser.add_argument("--original-root", type=Path, default=DEFAULT_ORIGINAL_ROOT)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--summary", type=Path, default=DEFAULT_SUMMARY)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if not args.csv_root.exists():
        raise SystemExit(f"CSV root not found: {args.csv_root}")
    if not args.original_root.exists():
        raise SystemExit(f"Original CSV root not found: {args.original_root}")

    originals = collect_originals(args.original_root)
    translated: list[DialogueRow] = []
    for package_root in sorted(path for path in args.csv_root.iterdir() if path.is_dir()):
        translated.extend(collect_dialogue(package_root.name, package_root))

    fieldnames = [
        "priority",
        "category",
        "package",
        "file",
        "line",
        "row_id",
        "speaker",
        "shared_mf_alias",
        "marker",
        "recommended_action",
        "source_en",
        "current_ru",
        "tags",
    ]
    output: list[dict[str, str | int]] = []
    seen: set[tuple[str, str, str, str]] = set()
    missing_source = 0

    for row in translated:
        source = source_text(originals, row)
        missing_source += not bool(source)
        issues = structural_issues(row.text) + gender_issues(row) + machine_issues(row.text)
        latin = latin_issue(row.text)
        if latin:
            issues.append(latin)
        if source and clean_text(source).strip() == clean_text(row.text).strip() and latin_issue(source):
            issues.append((5, "same_as_english_source", "без изменений", "перевести строку"))

        for priority, category, marker, action in issues:
            identity = (row.package, row.relative_file, row.row_id, category)
            if identity in seen:
                continue
            seen.add(identity)
            output.append(
                {
                    "priority": priority,
                    "category": category,
                    "package": row.package,
                    "file": row.relative_file,
                    "line": row.line,
                    "row_id": row.row_id,
                    "speaker": row.speaker,
                    "shared_mf_alias": "yes" if alias_pair(row.tags) else "",
                    "marker": marker,
                    "recommended_action": action,
                    "source_en": clean_text(source),
                    "current_ru": clean_text(row.text),
                    "tags": row.tags,
                }
            )

    output.sort(
        key=lambda item: (
            -int(item["priority"]),
            str(item["category"]),
            str(item["package"]),
            str(item["file"]),
            str(item["row_id"]),
        )
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(output)

    by_priority = Counter(int(item["priority"]) for item in output)
    by_category = Counter(str(item["category"]) for item in output)
    summary = [
        "Dialogue gender and style audit v065",
        f"csv_root={args.csv_root}",
        f"original_root={args.original_root}",
        f"dialogue_rows_scanned={len(translated)}",
        f"source_rows_loaded={len(originals)}",
        f"translated_rows_without_source={missing_source}",
        f"audit_candidates={len(output)}",
        "",
        "By priority:",
    ]
    summary.extend(f"- P{priority}: {count}" for priority, count in sorted(by_priority.items(), reverse=True))
    summary.append("")
    summary.append("By category:")
    summary.extend(f"- {category}: {count}" for category, count in by_category.most_common())
    args.summary.write_text("\n".join(summary) + "\n", encoding="utf-8")

    print(f"Scanned dialogue rows: {len(translated)}")
    print(f"Audit candidates: {len(output)}")
    print("Priorities:", dict(sorted(by_priority.items(), reverse=True)))
    print("Top categories:", by_category.most_common(12))
    print(f"Wrote: {args.out.resolve().relative_to(ROOT)}")
    print(f"Summary: {args.summary.resolve().relative_to(ROOT)}")


if __name__ == "__main__":
    main()

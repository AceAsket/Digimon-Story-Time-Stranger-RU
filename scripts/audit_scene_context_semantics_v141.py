#!/usr/bin/env python3
"""Audit EN->RU message semantics with two-line scene context.

The report is intentionally read-only and conservative.  It combines several
source-aligned signals into one candidate per dialogue row, keeps candidates in
package/file/row order, and records two useful neighbouring rows on each side.
"""

from __future__ import annotations

import csv
import re
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CSV_ROOT = ROOT / "csv"
SOURCE_ROOT = ROOT / "verify" / "game_build_23514637" / "text_original"
OUT = ROOT / "exports" / "scene_context_semantics_v141.csv"
SUMMARY = ROOT / "exports" / "scene_context_semantics_v141_summary.txt"

BRACE_RE = re.compile(r"\{[^{}]*\}")
PLAIN_WORD_RE = re.compile(r"[A-Za-zА-Яа-яЁё0-9]+")
EN_NEG_RE = re.compile(
    r"\b(?:nah|neither|never|no|nobody|none|nope|not|nothing|cannot|without)\b|"
    r"\bcan\s+not\b|\b[A-Za-z]+n['’]t\b",
    re.I,
)
EN_NEG_IDIOM_RE = re.compile(
    r"\b(?:never\s+mind|no\s+(?:doubt|longer|need|problem|use|way|wonder)|"
    r"not\s+(?:again|bad|exactly|just|long|much|necessarily|only|quite|really|yet)|"
    r"why\s+not|whether\s+or\s+not|can['’]t\s+(?:help|wait))\b",
    re.I,
)
EN_NEG_PARAPHRASE_RE = re.compile(
    r"\b(?:can['’]t\s+(?:bear|be\s+bothered|catch\s+a\s+break|help|say|wait)|"
    r"(?:are|is)n['’]t\s+completely|didn['’]t\s+(?:know|realize)|"
    r"doesn['’]t\s+(?:begin|disappoint)|don['’]t\s+(?:like\s+your\s+chances|say|tell\s+me)|"
    r"[A-Za-z]+n['’]t\s+exactly\s+un\w+|"
    r"in\s+no\s+time|I\s+wish\s+you\s+didn['’]t\s+have\s+to|"
    r"never[- ]ending|never\s+(?:expected|fear|gets?\s+old|know)|"
    r"no\s+(?:avail|cheating|choice|end|fair|fun|matter|minor|more|problems?|"
    r"reason|response|time)|not\s+(?:far|good|guilty|happy|healthy|same|well)|"
    r"not\s+treat\b.{0,30}\bnice|without\s+(?:fail|flaw|question|saying|a\s+trace)|"
    r"won['’]t\s+beat)\b",
    re.I,
)
EN_TAG_QUESTION_RE = re.compile(
    r"(?:,|\.{2,})?\s*(?:(?:are|can|could|did|do|does|had|has|have|is|must|"
    r"should|was|were|will|would)n['’]t|(?:are|can|could|did|do|does|had|has|"
    r"have|is|must|should|was|were|will|would)\s+not)\s+"
    r"(?:he|her|him|it|she|they|we|you)\s*[?!…\.]*$",
    re.I,
)
EN_IMPLICIT_NEG_RE = re.compile(
    r"\b(?:against|avoid|barely|deny|empty|except|fail|few|forget|free|hardly|"
    r"impossible|lack|lose|lost|miss|only|prevent|rarely|refuse|remove|scarcely|"
    r"stop|unless|unable|useless|wrong)\w*\b",
    re.I,
)
RU_NEG_RE = re.compile(
    r"\b(?:без|не|ни|нельзя|нет|никогда|никто|ничто|ничего|нигде|никуда|"
    r"ниоткуда|никак|нисколько)\b",
    re.I,
)
RU_LEXICAL_NEG_RE = re.compile(
    r"\b(?:без\w+|бес\w+|вряд\s+ли|держ\w*|едва\b|избеж\w*|измен\w*|"
    r"лиш[её]н\w*|лень\w*|мертв\w*|молч\w*|напрас\w*|"
    r"не(?!бо\b|бес\w*|вест\w*|дра\b|ктар\w*|навист\w*|птун\w*|рв\w*)\w+|"
    r"ни(?:г|к|от|ск|ч)\w+|далек\w*|ерунд\w*|обиж\w*|отказ\w*|отсутств\w*|"
    r"плох\w*|поздн\w*|пустяк\w*|редко\w*|трудн\w*|вред\w*)\b",
    re.I,
)
RU_NEG_EXCLUSION_RE = re.compile(
    r"\b(?:не\s+правда\s+ли|не\s+так\s+ли|не\s+то\s+чтобы|чуть\s+не|едва\s+не)\b",
    re.I,
)
EN_HE_RE = re.compile(r"\bhe\b", re.I)
EN_SHE_RE = re.compile(r"\bshe\b", re.I)
EN_FIRST_PERSON_RE = re.compile(r"\b(?:I|I['’](?:d|ll|m|ve)|me|my|mine|myself)\b")
EN_YOU_RE = re.compile(r"\b(?:you|your|yours|yourself|yourselves)\b", re.I)
EN_PLURAL_YOU_RE = re.compile(
    r"\byourselves\b|\b(?:all|both|two)\s+of\s+you\b|\byou\s+(?:both|guys|people|two)\b|\by['’]all\b",
    re.I,
)
EN_GROUP_ADDRESS_RE = re.compile(
    r"\b(?:everyone|folks|guys|which\s+one\s+of\s+you|you\s+all\s+(?!right\b|set\b|the\s+way\b)|"
    r"you\s+lot|you\s+ones|you\s+people|you\s+folks|\bselves\b|"
    r"you(?:['’]re|\s+are|\s+were)?(?:\W+\w+){0,4}\W+(?:cowards|humans|lot|ones|people))\b",
    re.I,
)
RU_TY = {
    "ты", "тебя", "тебе", "тобой", "тобою", "твой", "твоя", "твоё",
    "твое", "твоего", "твоей", "твоему", "твою", "твои", "твоих",
}
RU_VY = {
    "вы", "вас", "вам", "вами", "ваш", "ваша", "ваше", "вашего",
    "вашей", "вашему", "вашу", "ваши", "ваших",
}
RU_MALE_FORMS = {
    "был", "готов", "должен", "думал", "знал", "нашёл", "нашел", "понял",
    "пришёл", "пришел", "рад", "решил", "родился", "сделал", "сказал",
    "смог", "стал", "уверен", "увидел", "ушёл", "ушел", "хотел",
}
RU_FEMALE_FORMS = {
    "была", "готова", "должна", "думала", "знала", "нашла", "поняла",
    "пришла", "рада", "решила", "родилась", "сделала", "сказала", "смогла",
    "стала", "уверена", "увидела", "ушла", "хотела",
}
NUMBER_RE = re.compile(
    r"(?<![A-Za-zА-Яа-яЁё0-9])"
    r"(?:\d{1,3}(?:(?:,|[ \u00a0\u202f])\d{3})+|\d+(?:[.,]\d+)?)%?"
    r"(?![A-Za-zА-Яа-яЁё0-9])"
)
TIME_RE = re.compile(r"(?<!\d)(\d{1,2}):(\d{2})(?:\s*([AP])\.?M\.?)?", re.I)
ROMAN_RE = re.compile(r"(?<![A-Za-zА-Яа-яЁё])(VIII|VII|VI|IV|III|II|IX|XI|XII|V|X|I)(?![A-Za-zА-Яа-яЁё])")
ROMAN_ALWAYS = {"II", "III", "IV", "VI", "VII", "VIII", "IX", "XI", "XII"}
PERCENT_PLACEHOLDER_RE = re.compile(r"%(?:\d+\$)?[a-zA-Z]")
ANGLE_PLACEHOLDER_RE = re.compile(r"<\s*[A-Za-z_][A-Za-z0-9_]*\s*>")
SERVICE_KEY_RE = re.compile(r"^(?:dummy|debug|test|g_sel_|sel_|choice_)", re.I)
SERVICE_TEXT_RE = re.compile(r"^\s*\((?:preliminary|temporary|предварительно|временно)\)", re.I)
FULL_CHOICE_RE = re.compile(r"^\s*\[[^\]]+\](?:\{[^{}]*\})*\s*$", re.S)
ENTITY_TABLES = (
    Path("text/char_name.mbe/000_Sheet1.csv"),
    Path("text/field_name.mbe/000_Sheet1.csv"),
    Path("text/worldmap_place_name.mbe/000_Sheet1.csv"),
    Path("text/worldmap_group_name.mbe/000_Sheet1.csv"),
    Path("text/quest_client.mbe/000_Sheet1.csv"),
)
GENERIC_ENTITY_NAMES = {
    "all", "assistant", "bed", "both", "boy", "captain", "child", "citizen",
    "customer", "device", "digimon", "doctor", "door", "entrance", "everyone",
    "everything", "father", "friend", "girl", "guard", "man", "merchant",
    "mister", "mother", "narration", "operator", "partner", "passerby", "player",
    "researcher", "security", "shelves", "sound", "student", "titan", "tv",
    "unknown", "voice", "woman", "young man", "young woman",
}
GENERIC_CHAR_KEY_PARTS = {
    "ANNOUNCER", "ASSISTANT", "BED", "BOOKSHELF", "BOY", "BROADCAST", "BUTLER",
    "CAPTAIN", "CHARACTER", "CHILD", "CHILDREN", "CITIZEN", "CROWD", "CUSTOMER",
    "DAD", "DEMON", "DEVICE", "DOCTOR", "DOOR", "DOUBLE", "ENTRANCE", "EVERYONE",
    "FATHER", "GIRL", "GROUP", "GUARD", "MAN", "MERCHANT", "MISTER", "MOM",
    "MOTHER", "MULTIPLE", "NARRATION", "OLD", "OPERATOR", "PASSERBY", "PERSONNEL",
    "PLAYER", "PROTAGONIST", "RESEARCHER", "SECURITY", "SEVERAL", "SHELVES", "SOUND",
    "STAFF", "STUDENT", "TELEVISION", "TERMINAL", "TITAN", "TV", "UNKNOWN", "VOICE",
    "WOMAN", "YOUNG",
}
GENERIC_SPEAKER_RE = re.compile(
    r"(?:UNKNOWN|PLAYER|NARRATION|OPERATOR|VOICE|EVERYONE|DOUBLE|MULTIPLE|GROUP|CROWD)",
    re.I,
)
GENDER_REGISTRY = ROOT / "exports" / "digimon_dialogue_gender_registry_v084.csv"

# Manually reviewed A-B-A cases where the apparent register shift is caused by
# a real addressee change (group -> individual, individual -> group, or player
# -> named Digimon), not by an inconsistent translation.
REGISTER_CONTEXT_EXCLUSIONS = {
    "m260_110_170",
    "m300_050_040",
    "m310_032_030",
    "s030_183_170",
}


@dataclass(frozen=True)
class Signal:
    name: str
    severity: str
    score: int
    evidence: str


@dataclass
class DialogueRow:
    package: str
    file: str
    scene: str
    line: int
    key: str
    speaker: str
    en: str
    ru: str
    source_origin: str
    signals: list[Signal] = field(default_factory=list)
    diagnostics: dict[str, str] = field(default_factory=dict)


@dataclass
class EntityLexicon:
    en_to_ru: dict[tuple[str, ...], set[tuple[str, ...]]]
    ru_to_en: dict[tuple[str, ...], set[tuple[str, ...]]]
    en_labels: dict[tuple[str, ...], str]
    ru_labels: dict[tuple[str, ...], str]
    en_ids: dict[tuple[str, ...], set[str]]
    ru_ids: dict[tuple[str, ...], set[str]]
    en_index: dict[str, list[tuple[str, ...]]]
    ru_index: dict[str, list[tuple[str, ...]]]


_SOURCE_CACHE: dict[Path, dict[str, list[str]]] = {}


def clean_text(value: str) -> str:
    return "\n".join(
        line.rstrip()
        for line in value.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    )


def visible_text(value: str) -> str:
    return re.sub(r"\s+", " ", BRACE_RE.sub(" ", clean_text(value))).strip()


def word_tokens(value: str) -> list[str]:
    return [token.lower().replace("ё", "е") for token in PLAIN_WORD_RE.findall(visible_text(value))]


def entity_tokens(value: str) -> tuple[str, ...]:
    return tuple(word_tokens(value))


def read_rows(path: Path) -> dict[str, list[str]]:
    if path not in _SOURCE_CACHE:
        if not path.exists():
            _SOURCE_CACHE[path] = {}
        else:
            with path.open("r", encoding="utf-8-sig", newline="") as handle:
                _SOURCE_CACHE[path] = {row[0]: row for row in csv.reader(handle) if row}
    return _SOURCE_CACHE[path]


def source_maps_for(package: str, relative: Path) -> list[tuple[str, dict[str, list[str]]]]:
    packages = [package]
    if package == "patch_text01":
        packages.append("app_text01")
    return [
        (source_package, read_rows(SOURCE_ROOT / source_package / "csv" / relative))
        for source_package in packages
    ]


def source_value(
    maps: list[tuple[str, dict[str, list[str]]]], key: str, column: int
) -> tuple[str, str]:
    for origin, rows in maps:
        row = rows.get(key)
        if row and len(row) > column and row[column].strip():
            return clean_text(row[column]), origin
    return "", ""


def scene_for(relative: Path) -> str:
    if len(relative.parts) > 1:
        name = relative.parts[1]
        return name[:-4] if name.lower().endswith(".mbe") else name
    return relative.stem


def service_reason(key: str, en: str, ru: str) -> str:
    if SERVICE_KEY_RE.search(key):
        return "dummy_or_service_key"
    for text in (en, ru):
        if SERVICE_TEXT_RE.search(text):
            return "temporary_text"
        if FULL_CHOICE_RE.fullmatch(text):
            return "selection_text"
    if not word_tokens(en) and not word_tokens(ru):
        return "tag_only"
    return ""


def normalize_brace_placeholder(raw: str) -> str:
    value = re.sub(r"\s+", "", raw.strip())
    lower = value.lower()
    color = re.match(r"fc\d+", lower)
    if color:
        return "{" + color.group(0) + "}"
    call = re.match(r"([a-z_][a-z0-9_]*)\(([^()]*)\)$", lower)
    if call:
        # Function arguments can be localized text (notably pf plural forms).
        # The callable name and argument arity are the structural placeholder.
        argument_count = call.group(2).count("/") + 1 if call.group(2) else 0
        return "{" + call.group(1) + f"/{argument_count}" + "}"
    command = re.match(r"[a-z_]+\d*", lower)
    if command:
        return "{" + command.group(0) + "}"
    if lower.isdigit():
        return "{" + lower + "}"
    return "{" + lower[:40] + "}"


def placeholders(value: str) -> Counter[str]:
    result: Counter[str] = Counter()
    for match in BRACE_RE.finditer(value):
        result[normalize_brace_placeholder(match.group(0)[1:-1])] += 1
    for match in PERCENT_PLACEHOLDER_RE.finditer(value):
        result[match.group(0).lower()] += 1
    for match in ANGLE_PLACEHOLDER_RE.finditer(value):
        result[re.sub(r"\s+", "", match.group(0)).lower()] += 1
    return result


def counter_text(values: Counter[str]) -> str:
    parts = []
    for value in sorted(values):
        count = values[value]
        parts.append(value if count == 1 else f"{value}x{count}")
    return ", ".join(parts)


def normalize_number(raw: str) -> str:
    percent = raw.endswith("%")
    body = raw[:-1] if percent else raw
    body = body.replace("\u00a0", " ").replace("\u202f", " ")
    if " " in body or re.fullmatch(r"\d{1,3}(?:,\d{3})+", body):
        body = body.replace(" ", "").replace(",", "")
    elif "," in body:
        body = body.replace(",", ".")
    return body + ("%" if percent else "")


def spelled_numbers(value: str, language: str) -> Counter[str]:
    tokens = word_tokens(value)
    if language == "ru":
        small = {
            "ноль": 0, "один": 1, "одна": 1, "одно": 1, "одном": 1,
            "два": 2, "две": 2, "трех": 3, "три": 3, "четыре": 4,
            "пять": 5, "шесть": 6, "семь": 7, "восемь": 8, "девять": 9,
            "десять": 10, "одиннадцать": 11, "двенадцать": 12,
            "сорок": 40, "сто": 100, "шестьсот": 600,
        }
        scales = {
            "тысяч": 1000, "тысяча": 1000, "тысячи": 1000,
            "миллион": 1000000, "миллиона": 1000000, "миллионов": 1000000,
        }
    else:
        small = {
            "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4,
            "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9,
            "ten": 10, "eleven": 11, "twelve": 12, "forty": 40,
            "hundred": 100, "six hundred": 600,
        }
        scales = {"thousand": 1000, "million": 1000000, "millions": 1000000}
    result: Counter[str] = Counter()
    index = 0
    while index < len(tokens):
        token = tokens[index]
        if token in small and index + 1 < len(tokens) and tokens[index + 1] in scales:
            result["num:" + str(small[token] * scales[tokens[index + 1]])] += 1
            index += 2
            continue
        if token in small:
            result["num:" + str(small[token])] += 1
        index += 1
    return result


def cancel_spelled_equivalents(
    source_only: Counter[str], target_text: str, target_language: str
) -> Counter[str]:
    remaining = source_only.copy()
    spelled = spelled_numbers(target_text, target_language)
    for token in list(remaining):
        if not token.startswith("num:"):
            continue
        cancel = min(remaining[token], spelled[token])
        if cancel:
            remaining[token] -= cancel
            if not remaining[token]:
                del remaining[token]
    return remaining


def number_tokens(value: str) -> Counter[str]:
    visible = visible_text(value)
    found: Counter[str] = Counter()
    time_spans: list[tuple[int, int]] = []
    for match in TIME_RE.finditer(visible):
        hour = int(match.group(1))
        minute = int(match.group(2))
        meridiem = (match.group(3) or "").upper()
        if meridiem == "P" and hour < 12:
            hour += 12
        elif meridiem == "A" and hour == 12:
            hour = 0
        found[f"time:{hour:02d}:{minute:02d}"] += 1
        time_spans.append(match.span())
    for match in NUMBER_RE.finditer(visible):
        if any(start <= match.start() < end for start, end in time_spans):
            continue
        normalized = normalize_number(match.group(0))
        scale_match = re.match(
            r"\s*(million|миллион(?:а|ов)?|тысяч(?:а|и)?)\b",
            visible[match.end():],
            re.I,
        )
        if scale_match and normalized.isdigit():
            scale = 1000000 if scale_match.group(1).lower().startswith(("m", "мил")) else 1000
            normalized = str(int(normalized) * scale)
        found["num:" + normalized] += 1
    for match in ROMAN_RE.finditer(visible):
        roman = match.group(1).upper()
        if roman in ROMAN_ALWAYS:
            found["roman:" + roman] += 1
    return found


def counter_difference_text(source: Counter[str], target: Counter[str]) -> str:
    return f"EN=[{counter_text(source)}] RU=[{counter_text(target)}]"


def known_number_localization(en: str, ru: str) -> bool:
    return bool(
        re.search(r"\bCard\s+Battle\s+101\b", visible_text(en), re.I)
        and re.search(r"\bоснов\w*\s+карточн\w*\s+бо", visible_text(ru), re.I)
    )


def russian_negations(value: str) -> Counter[str]:
    visible = visible_text(value).lower().replace("ё", "е")
    visible = RU_NEG_EXCLUSION_RE.sub(" ", visible)
    result: Counter[str] = Counter()
    for match in RU_NEG_RE.finditer(visible):
        token = match.group(0)
        if token in {"никогда", "никто", "ничто", "ничего", "нигде", "никуда", "ниоткуда", "никак", "нисколько"}:
            token = "ни"
        result[token] += 1
    if not result and RU_LEXICAL_NEG_RE.search(visible):
        result["лексическое_отрицание"] += 1
    return result


def english_negations(value: str) -> Counter[str]:
    visible = visible_text(value).replace("’", "'")
    visible = EN_TAG_QUESTION_RE.sub(" ", visible)
    visible = EN_NEG_IDIOM_RE.sub(" ", visible)
    result: Counter[str] = Counter()
    for match in EN_NEG_RE.finditer(visible):
        token = match.group(0).lower().replace(" ", "")
        if token in {"nah", "neither", "nobody", "none", "nope", "nothing"}:
            token = "no"
        elif token in {"cannot", "can't"}:
            token = "cannot"
        elif token.endswith("n't"):
            token = "not"
        result[token] += 1
    return result


def confident_lost_negation(
    en: str, ru: str, en_markers: Counter[str], ru_markers: Counter[str]
) -> bool:
    if not en_markers or ru_markers or sum(en_markers.values()) != 1:
        return False
    en_visible = visible_text(en)
    # Negative questions, tag questions, and longer clauses are routinely and
    # correctly recast with affirmative Russian wording. They are unsuitable
    # surface evidence for a polarity error.
    if "?" in en_visible or len(word_tokens(en_visible)) > 14:
        return False
    if re.search(r"\bNo\.\s*\d", en_visible):
        return False
    if EN_NEG_PARAPHRASE_RE.search(en_visible):
        return False
    return True


def confident_added_negation(en: str, ru: str, ru_markers: Counter[str]) -> bool:
    if EN_IMPLICIT_NEG_RE.search(en) or EN_NEG_RE.search(en):
        return False
    normalized = visible_text(ru).lower().replace("ё", "е")
    normalized = normalized.lstrip(" \t\n\r\"'«([—–-")
    if not re.match(r"^(?:нет\b|нельзя\b)", normalized):
        return False
    return bool(re.match(r"^(?:yes|certainly|definitely|sure)\b", visible_text(en), re.I))


def register(value: str) -> str:
    tokens = set(word_tokens(value))
    informal = bool(tokens & RU_TY)
    formal = bool(tokens & RU_VY)
    if informal and formal:
        return "mixed"
    if informal:
        return "ty"
    if formal:
        return "vy"
    return "none"


def add_signal(row: DialogueRow, name: str, severity: str, score: int, evidence: str) -> None:
    if any(signal.name == name for signal in row.signals):
        return
    row.signals.append(Signal(name, severity, score, clean_text(evidence)[:400]))


def entity_allowed(table: str, key: str, en: str, ru: str) -> bool:
    en_words = entity_tokens(en)
    ru_words = entity_tokens(ru)
    if not en_words or not ru_words or len(en_words) > 7 or len(ru_words) > 7:
        return False
    if len(en) > 80 or len(ru) > 80:
        return False
    normalized_en = " ".join(en_words)
    normalized_ru = " ".join(ru_words)
    if normalized_en in GENERIC_ENTITY_NAMES or normalized_ru in GENERIC_ENTITY_NAMES:
        return False
    if table == "char_name.mbe":
        if not key.startswith("char_"):
            return False
        key_parts = set(re.split(r"[_\-\s]+", key.removeprefix("char_").upper()))
        if key_parts & GENERIC_CHAR_KEY_PARTS:
            return False
    elif not key.isdigit():
        return False
    # Inclusion is based solely on the same table/key having a non-empty source
    # and target value. Capitalization is deliberately not used as evidence.
    return True


def ru_stem(value: str) -> str:
    value = value.lower().replace("ё", "е")
    if not re.search(r"[а-я]", value):
        return value
    if value.endswith("мон"):
        return value
    for ending in ("ский", "цкий", "ый", "ий", "ой", "ая", "яя", "ое", "ее", "ые", "ие"):
        if value.endswith(ending) and len(value) - len(ending) >= 4:
            return value[:-len(ending)]
    if value.endswith(("а", "я", "ь", "й")) and len(value) >= 5:
        return value[:-1]
    return value


def ru_word_matches(base: str, actual: str) -> bool:
    if base == actual:
        return True
    if (base, actual) in {("доктор", "др"), ("доктор", "док") }:
        return True
    if not re.search(r"[а-я]", base) or not re.search(r"[а-я]", actual):
        return False
    if len(base) >= 4 and actual.startswith(base) and len(actual) - len(base) <= 4:
        return True
    stem = ru_stem(base)
    return len(stem) >= 4 and actual.startswith(stem) and abs(len(actual) - len(base)) <= 4


def build_entity_lexicon() -> EntityLexicon:
    en_to_ru: dict[tuple[str, ...], set[tuple[str, ...]]] = defaultdict(set)
    ru_to_en: dict[tuple[str, ...], set[tuple[str, ...]]] = defaultdict(set)
    en_labels: dict[tuple[str, ...], str] = {}
    ru_labels: dict[tuple[str, ...], str] = {}
    en_ids: dict[tuple[str, ...], set[str]] = defaultdict(set)
    ru_ids: dict[tuple[str, ...], set[str]] = defaultdict(set)
    for package_root in sorted(path for path in CSV_ROOT.iterdir() if path.is_dir()):
        package = package_root.name
        for relative in ENTITY_TABLES:
            path = package_root / relative
            if not path.exists():
                continue
            source_maps = source_maps_for(package, relative)
            with path.open("r", encoding="utf-8-sig", newline="") as handle:
                rows = list(csv.reader(handle))
            table = relative.parts[1]
            for row in rows[1:]:
                if len(row) <= 1 or not row[1].strip():
                    continue
                en, _origin = source_value(source_maps, row[0], 1)
                ru = clean_text(row[1])
                if not en or not entity_allowed(table, row[0], en, ru):
                    continue
                en_key = entity_tokens(en)
                ru_key = entity_tokens(ru)
                en_to_ru[en_key].add(ru_key)
                ru_to_en[ru_key].add(en_key)
                en_labels.setdefault(en_key, visible_text(en))
                ru_labels.setdefault(ru_key, visible_text(ru))
                entity_id = f"{table}:{row[0]}"
                en_ids[en_key].add(entity_id)
                ru_ids[ru_key].add(entity_id)
    en_index: dict[str, list[tuple[str, ...]]] = defaultdict(list)
    ru_index: dict[str, list[tuple[str, ...]]] = defaultdict(list)
    for key in en_to_ru:
        en_index[key[0]].append(key)
    for key in ru_to_en:
        first = ru_stem(key[0])
        ru_index[first[:4] if len(first) >= 4 else first].append(key)
    for values in en_index.values():
        values.sort(key=len, reverse=True)
    for values in ru_index.values():
        values.sort(key=len, reverse=True)
    return EntityLexicon(
        en_to_ru, ru_to_en, en_labels, ru_labels, en_ids, ru_ids, en_index, ru_index
    )


def maximal_entities(values: set[tuple[str, ...]]) -> set[tuple[str, ...]]:
    result = set(values)
    for shorter in values:
        for longer in values:
            if shorter == longer or len(shorter) >= len(longer):
                continue
            if any(
                longer[index:index + len(shorter)] == shorter
                for index in range(len(longer) - len(shorter) + 1)
            ):
                result.discard(shorter)
                break
    return result


def find_en_entities(value: str, lexicon: EntityLexicon) -> set[tuple[str, ...]]:
    tokens = entity_tokens(value)
    found: set[tuple[str, ...]] = set()
    for index, token in enumerate(tokens):
        for candidate in lexicon.en_index.get(token, []):
            if tokens[index:index + len(candidate)] == candidate:
                found.add(candidate)
    return maximal_entities(found)


def find_ru_entities(value: str, lexicon: EntityLexicon) -> set[tuple[str, ...]]:
    tokens = entity_tokens(value)
    found: set[tuple[str, ...]] = set()
    for index, token in enumerate(tokens):
        lookup = token[:4] if len(token) >= 4 else token
        lookups = [lookup]
        if token in {"др", "док"}:
            lookups.append("докт")
        candidates = {
            candidate
            for candidate_lookup in lookups
            for candidate in lexicon.ru_index.get(candidate_lookup, [])
        }
        for candidate in candidates:
            if index + len(candidate) > len(tokens):
                continue
            if all(ru_word_matches(base, actual) for base, actual in zip(candidate, tokens[index:index + len(candidate)])):
                found.add(candidate)
    # Keep both a compound glossary label and its aligned component names.
    # Dropping the shorter matches makes "Аполломон и Дианамон" look like a
    # substitution merely because a combined speaker-label ID also exists.
    return found


def labels(keys: set[tuple[str, ...]], mapping: dict[tuple[str, ...], str]) -> str:
    return " | ".join(sorted(mapping[key] for key in keys if key in mapping))


def entity_ids(keys: set[tuple[str, ...]], mapping: dict[tuple[str, ...], set[str]]) -> str:
    return " | ".join(sorted({item for key in keys for item in mapping.get(key, set())}))


def load_speaker_genders() -> dict[str, str]:
    genders: dict[str, str] = {}
    if not GENDER_REGISTRY.exists():
        return genders
    with GENDER_REGISTRY.open("r", encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            if row.get("status") != "curated_source_confirmed":
                continue
            gender = row.get("expected_or_observed_gender", "")
            if gender in {"male", "female"} and row.get("speaker"):
                genders[row["speaker"]] = gender
    return genders


SELF_FORM_FILLERS = {
    "бы", "ведь", "всегда", "давно", "едва", "еще", "ещё", "же", "не", "никогда",
    "просто", "снова", "совсем", "так", "также", "только", "тоже", "уже",
}


def first_person_forms(value: str, forms: set[str]) -> set[str]:
    tokens = word_tokens(value)
    found: set[str] = set()
    for index, token in enumerate(tokens):
        if token != "я":
            continue
        for following in tokens[index + 1:index + 6]:
            if following in forms:
                found.add(following)
                break
            if following not in SELF_FORM_FILLERS:
                break
    return found


def apply_content_signals(
    row: DialogueRow, lexicon: EntityLexicon, speaker_genders: dict[str, str]
) -> None:
    en_visible = visible_text(row.en)
    ru_visible = visible_text(row.ru)
    en_words = word_tokens(row.en)
    ru_words = word_tokens(row.ru)
    en_chars = len(en_visible)
    ru_chars = len(ru_visible)
    word_ratio = len(ru_words) / max(1, len(en_words))
    char_ratio = ru_chars / max(1, en_chars)
    row.diagnostics.update(
        {
            "en_words": str(len(en_words)),
            "ru_words": str(len(ru_words)),
            "word_ratio": f"{word_ratio:.2f}",
            "char_ratio": f"{char_ratio:.2f}",
        }
    )

    en_placeholders = placeholders(row.en)
    ru_placeholders = placeholders(row.ru)
    row.diagnostics["source_placeholders"] = counter_text(en_placeholders)
    row.diagnostics["current_placeholders"] = counter_text(ru_placeholders)
    if en_placeholders != ru_placeholders:
        add_signal(
            row, "placeholder_mismatch", "high", 100,
            f"EN=[{counter_text(en_placeholders)}] RU=[{counter_text(ru_placeholders)}]",
        )

    en_numbers = number_tokens(row.en)
    ru_numbers = number_tokens(row.ru)
    row.diagnostics["source_numbers"] = counter_text(en_numbers)
    row.diagnostics["current_numbers"] = counter_text(ru_numbers)
    en_number_only = cancel_spelled_equivalents(en_numbers - ru_numbers, row.ru, "ru")
    ru_number_only = cancel_spelled_equivalents(ru_numbers - en_numbers, row.en, "en")
    if (en_number_only or ru_number_only) and not known_number_localization(row.en, row.ru):
        add_signal(
            row, "number_or_roman_mismatch", "high", 98,
            counter_difference_text(en_number_only, ru_number_only),
        )

    en_negations = english_negations(row.en)
    ru_negations = russian_negations(row.ru)
    row.diagnostics["source_negated"] = counter_text(en_negations) or "no"
    row.diagnostics["current_negated"] = counter_text(ru_negations) or "no"
    if confident_lost_negation(row.en, row.ru, en_negations, ru_negations):
        add_signal(
            row, "negation_lost", "high", 92,
            f"explicit EN markers=[{counter_text(en_negations)}]; RU has none after idiom/lexical normalization",
        )
    elif ru_negations and not en_negations and confident_added_negation(en_visible, ru_visible, ru_negations):
        add_signal(
            row, "negation_added", "high", 90,
            f"sentence-initial RU markers=[{counter_text(ru_negations)}]; EN has no explicit/implicit negative cue",
        )

    en_question = "?" in en_visible
    ru_question = "?" in ru_visible
    row.diagnostics["source_question"] = "yes" if en_question else "no"
    row.diagnostics["current_question"] = "yes" if ru_question else "no"

    word_gap = len(en_words) - len(ru_words)
    char_gap = en_chars - ru_chars
    if len(en_words) >= 5 and not ru_words:
        add_signal(row, "meaning_drop_empty", "high", 100, f"words RU/EN = 0/{len(en_words)}")
    elif (
        len(en_words) >= 20
        and 1 <= len(ru_words) <= 5
        and word_gap >= 15
        and char_gap >= 70
        and word_ratio <= 0.30
        and char_ratio <= 0.42
    ):
        add_signal(
            row, "length_ratio_short", "high", 84,
            f"words RU/EN={len(ru_words)}/{len(en_words)} ({word_ratio:.2f}, gap={word_gap}); chars={ru_chars}/{en_chars} ({char_ratio:.2f}, gap={char_gap})",
        )
    elif (
        len(en_words) >= 8
        and len(ru_words) - len(en_words) >= 11
        and ru_chars - en_chars >= 55
        and word_ratio >= 1.90
        and char_ratio >= 1.65
    ):
        add_signal(
            row, "length_ratio_long", "high", 76,
            f"words RU/EN={len(ru_words)}/{len(en_words)} ({word_ratio:.2f}, gap={-word_gap}); chars={ru_chars}/{en_chars} ({char_ratio:.2f}, gap={-char_gap})",
        )

    ru_token_set = set(ru_words)
    en_entities = find_en_entities(row.en, lexicon)
    ru_entities = find_ru_entities(row.ru, lexicon)
    row.diagnostics["source_entities"] = labels(en_entities, lexicon.en_labels)
    row.diagnostics["current_entities"] = labels(ru_entities, lexicon.ru_labels)
    row.diagnostics["source_entity_ids"] = entity_ids(en_entities, lexicon.en_ids)
    row.diagnostics["current_entity_ids"] = entity_ids(ru_entities, lexicon.ru_ids)
    missing_entities = {
        en_key for en_key in en_entities
        if not (lexicon.en_to_ru.get(en_key, set()) & ru_entities)
    }
    added_entities = {
        ru_key for ru_key in ru_entities
        if not (lexicon.ru_to_en.get(ru_key, set()) & en_entities)
    }
    row.diagnostics["mismatched_source_entity_ids"] = entity_ids(missing_entities, lexicon.en_ids)
    # A missing glossary form is only reviewable when the source line is
    # essentially a direct name/title utterance. In longer prose, pronouns,
    # descriptions and deliberate term adaptation make this surface test noisy.
    entity_reviewable = bool(missing_entities) and len(en_words) <= 4
    if entity_reviewable and added_entities:
        add_signal(
            row, "named_entity_substitution", "high", 96,
            "EN=" + labels(missing_entities, lexicon.en_labels)
            + " [" + entity_ids(missing_entities, lexicon.en_ids) + "]"
            + "; RU=" + labels(added_entities, lexicon.ru_labels)
            + " [" + entity_ids(added_entities, lexicon.ru_ids) + "]",
        )
    elif entity_reviewable:
        add_signal(
            row, "named_entity_missing", "high", 88,
            labels(missing_entities, lexicon.en_labels)
            + " [" + entity_ids(missing_entities, lexicon.en_ids) + "]",
        )

    # Gender is only considered when the source contains an explicit pronoun.
    # Third-person checks also require one aligned glossary referent and explicit
    # opposite target pronouns; unrelated gendered verbs are never evidence.
    aligned_entities = {
        en_key for en_key in en_entities
        if lexicon.en_to_ru.get(en_key, set()) & ru_entities
    }
    if len(en_entities) == 1 and aligned_entities:
        if EN_HE_RE.search(en_visible) and not EN_SHE_RE.search(en_visible) and "она" in ru_token_set and "он" not in ru_token_set:
            add_signal(row, "gender_named_he_to_she", "high", 91, "named glossary referent + EN he vs RU она")
        elif EN_SHE_RE.search(en_visible) and not EN_HE_RE.search(en_visible) and "он" in ru_token_set and "она" not in ru_token_set:
            add_signal(row, "gender_named_she_to_he", "high", 91, "named glossary referent + EN she vs RU он")

    expected_gender = speaker_genders.get(row.speaker, "")
    if expected_gender and EN_FIRST_PERSON_RE.search(en_visible) and not row.key.endswith(("__H", "__F")):
        wrong_forms = RU_FEMALE_FORMS if expected_gender == "male" else RU_MALE_FORMS
        found_wrong = first_person_forms(row.ru, wrong_forms)
        if found_wrong:
            add_signal(
                row, "gender_first_person_mismatch", "high", 93,
                f"speaker={row.speaker} registry={expected_gender}; RU я-form={','.join(sorted(found_wrong))}",
            )

    current_register = register(row.ru)
    row.diagnostics["source_you"] = "yes" if EN_YOU_RE.search(en_visible) else "no"
    row.diagnostics["current_register"] = current_register
    if EN_PLURAL_YOU_RE.search(en_visible) and current_register == "ty":
        add_signal(row, "you_plural_vs_ty", "medium", 60, "EN explicitly addresses multiple people; RU has only ты-register")


def apply_context_register_signals(rows: list[DialogueRow]) -> None:
    # A-B-A is the narrow conversational case in which the same named speaker
    # is very likely addressing the same respondent on both sides of a reply.
    for index in range(2, len(rows)):
        previous = rows[index - 2]
        respondent = rows[index - 1]
        row = rows[index]
        if (
            not row.en
            or row.speaker != previous.speaker
            or not row.speaker
            or respondent.speaker in {"", row.speaker}
            or GENERIC_SPEAKER_RE.search(row.speaker)
            or GENERIC_SPEAKER_RE.search(respondent.speaker)
            or "{player}" in row.en.lower()
            or "{player}" in previous.en.lower()
            or not EN_YOU_RE.search(visible_text(row.en))
            or not EN_YOU_RE.search(visible_text(previous.en))
            or EN_PLURAL_YOU_RE.search(visible_text(row.en))
            or EN_PLURAL_YOU_RE.search(visible_text(previous.en))
            or EN_GROUP_ADDRESS_RE.search(visible_text(row.en))
            or EN_GROUP_ADDRESS_RE.search(visible_text(previous.en))
        ):
            continue
        current = register(row.ru)
        previous_register = register(previous.ru)
        if current not in {"ty", "vy"} or previous_register not in {"ty", "vy"}:
            continue
        if row.key in REGISTER_CONTEXT_EXCLUSIONS:
            continue
        if previous_register != current:
            add_signal(
                row, "register_shift_context", "medium", 62,
                f"A-B-A exchange via {respondent.speaker}: {previous.key}={previous_register}; current={current}",
            )


def load_dialogue() -> tuple[list[tuple[str, str, list[DialogueRow]]], Counter[str]]:
    files: list[tuple[str, str, list[DialogueRow]]] = []
    coverage: Counter[str] = Counter()
    for path in sorted(CSV_ROOT.glob("*_text01/message/**/*.csv")):
        package = path.relative_to(CSV_ROOT).parts[0]
        relative = path.relative_to(CSV_ROOT / package)
        source_maps = source_maps_for(package, relative)
        coverage["message_files"] += 1
        if any(rows for _origin, rows in source_maps):
            coverage["files_with_source"] += 1
        else:
            coverage["files_without_source"] += 1
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            current_rows = list(csv.reader(handle))
        dialogue_rows: list[DialogueRow] = []
        for line_no, current in enumerate(current_rows, 1):
            if not current or (line_no == 1 and current[0].startswith("string")):
                continue
            coverage["rows_seen"] += 1
            if len(current) <= 2:
                coverage["excluded_missing_column"] += 1
                continue
            key = current[0]
            speaker = current[1] if len(current) > 1 else ""
            ru = clean_text(current[2])
            en, origin = source_value(source_maps, key, 2)
            reason = service_reason(key, en, ru)
            if reason:
                coverage["excluded_" + reason] += 1
                continue
            if not en:
                coverage["rows_without_source"] += 1
            else:
                coverage["rows_with_source"] += 1
                coverage["source_" + origin] += 1
            dialogue_rows.append(
                DialogueRow(
                    package=package,
                    file=relative.as_posix(),
                    scene=scene_for(relative),
                    line=line_no,
                    key=key,
                    speaker=speaker,
                    en=en,
                    ru=ru,
                    source_origin=origin,
                )
            )
        files.append((package, relative.as_posix(), dialogue_rows))
    return files, coverage


def context_values(rows: list[DialogueRow], index: int, offset: int) -> dict[str, str]:
    prefix = "previous_" + str(abs(offset)) if offset < 0 else "next_" + str(offset)
    target_index = index + offset
    if not (0 <= target_index < len(rows)):
        return {
            prefix + "_key": "",
            prefix + "_speaker": "",
            prefix + "_en": "",
            prefix + "_ru": "",
        }
    target = rows[target_index]
    return {
        prefix + "_key": target.key,
        prefix + "_speaker": target.speaker,
        prefix + "_en": target.en,
        prefix + "_ru": target.ru,
    }


def build_report(
    files: list[tuple[str, str, list[DialogueRow]]], lexicon: EntityLexicon
) -> tuple[list[dict[str, str | int]], Counter[str], int]:
    report: list[dict[str, str | int]] = []
    speaker_genders = load_speaker_genders()
    for _package, _file, rows in files:
        for row in rows:
            if row.en:
                apply_content_signals(row, lexicon, speaker_genders)
        apply_context_register_signals(rows)
        for index, row in enumerate(rows):
            if not row.en or not row.signals:
                continue
            row.signals.sort(key=lambda signal: (-signal.score, signal.name))
            severity = "high" if any(signal.severity == "high" for signal in row.signals) else "medium"
            record: dict[str, str | int] = {
                "severity": severity,
                "score": max(signal.score for signal in row.signals),
                "signals": "; ".join(signal.name for signal in row.signals),
                "evidence": " | ".join(f"{signal.name}: {signal.evidence}" for signal in row.signals),
                "package": row.package,
                "scene": row.scene,
                "file": row.file,
                "line": row.line,
                "key": row.key,
                "speaker": row.speaker,
                "source_origin": row.source_origin,
                "source_en": row.en,
                "current_ru": row.ru,
            }
            for name in (
                "en_words", "ru_words", "word_ratio", "char_ratio", "source_negated",
                "current_negated", "source_question", "current_question", "source_numbers",
                "current_numbers", "source_placeholders", "current_placeholders",
                "source_entities", "current_entities", "source_entity_ids", "current_entity_ids",
                "mismatched_source_entity_ids", "source_you", "current_register",
            ):
                record[name] = row.diagnostics.get(name, "")
            for offset in (-2, -1, 1, 2):
                record.update(context_values(rows, index, offset))
            report.append(record)
    report.sort(key=lambda item: (str(item["package"]), str(item["file"]), int(item["line"])))
    raw_count = len(report)
    report = prune_repeated_entity_rows(report)
    signal_counts: Counter[str] = Counter()
    for record in report:
        signal_counts.update(str(record["signals"]).split("; "))
    return report, signal_counts, raw_count - len(report)


def prune_repeated_entity_rows(
    rows: list[dict[str, str | int]],
) -> list[dict[str, str | int]]:
    """Keep one contextual example per repeated glossary mismatch.

    A systematic spelling/term mismatch can occur dozens of times. Repeating it
    does not improve review quality; rows carrying any independent signal are
    retained, while entity-only duplicates are represented once per source ID
    and target-ID combination.
    """
    entity_signals = {"named_entity_missing", "named_entity_substitution"}
    seen: set[tuple[str, str, str]] = set()
    kept: list[dict[str, str | int]] = []
    for row in rows:
        names = set(str(row["signals"]).split("; "))
        if names and names <= entity_signals:
            signature = (
                ";".join(sorted(names)),
                str(row.get("mismatched_source_entity_ids", "")),
                str(row.get("current_entity_ids", "")),
            )
            if signature in seen:
                continue
            seen.add(signature)
        kept.append(row)
    return kept


def write_report(rows: list[dict[str, str | int]]) -> None:
    fields = [
        "severity", "score", "signals", "evidence", "package", "scene", "file",
        "line", "key", "speaker", "source_origin", "source_en", "current_ru",
        "en_words", "ru_words", "word_ratio", "char_ratio", "source_negated",
        "current_negated", "source_question", "current_question", "source_numbers",
        "current_numbers", "source_placeholders", "current_placeholders",
        "source_entities", "current_entities", "source_entity_ids", "current_entity_ids",
        "mismatched_source_entity_ids", "source_you", "current_register",
        "previous_2_key", "previous_2_speaker", "previous_2_en", "previous_2_ru",
        "previous_1_key", "previous_1_speaker", "previous_1_en", "previous_1_ru",
        "next_1_key", "next_1_speaker", "next_1_en", "next_1_ru",
        "next_2_key", "next_2_speaker", "next_2_en", "next_2_ru",
    ]
    with OUT.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    lexicon = build_entity_lexicon()
    files, coverage = load_dialogue()
    report, signal_counts, suppressed_repeated_entities = build_report(files, lexicon)
    write_report(report)
    severity_counts = Counter(str(row["severity"]) for row in report)
    lines = [
        "Scene context semantics audit v141",
        f"message_files={coverage['message_files']}",
        f"files_with_source={coverage['files_with_source']}",
        f"files_without_source={coverage['files_without_source']}",
        f"rows_seen={coverage['rows_seen']}",
        f"rows_with_source={coverage['rows_with_source']}",
        f"rows_without_source={coverage['rows_without_source']}",
        f"excluded_dummy_or_service_key={coverage['excluded_dummy_or_service_key']}",
        f"excluded_temporary_text={coverage['excluded_temporary_text']}",
        f"excluded_selection_text={coverage['excluded_selection_text']}",
        f"excluded_tag_only={coverage['excluded_tag_only']}",
        f"source_patch_text01={coverage['source_patch_text01']}",
        f"source_app_text01_fallback={coverage['source_app_text01']}",
        f"entity_source_names={len(lexicon.en_to_ru)}",
        f"entity_target_names={len(lexicon.ru_to_en)}",
        f"speaker_gender_ids={len(load_speaker_genders())}",
        f"raw_candidates={len(report) + suppressed_repeated_entities}",
        f"suppressed_repeated_entity_rows={suppressed_repeated_entities}",
        f"candidates={len(report)}",
        f"high={severity_counts['high']}",
        f"medium={severity_counts['medium']}",
    ]
    lines.extend(f"signal_{name}={signal_counts[name]}" for name in sorted(signal_counts))
    lines.append(f"report={OUT.relative_to(ROOT)}")
    SUMMARY.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()

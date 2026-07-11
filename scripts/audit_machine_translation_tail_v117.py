from __future__ import annotations

import csv
import re
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CSV_ROOT = ROOT / "csv"
ORIGINAL_ROOT = ROOT / "verify" / "game_build_23514637" / "text_original"
OUT_CSV = ROOT / "exports" / "machine_translation_tail_v117.csv"
OUT_SUMMARY = ROOT / "exports" / "machine_translation_tail_v117_summary.md"
OUT_TEMPLATES = ROOT / "exports" / "machine_translation_templates_v117.csv"

TAG_RE = re.compile(r"\{[^}]*\}|\[[^]]*]|image\([^)]*\)")
WORD_RE = re.compile(r"[A-Za-zА-Яа-яЁё]+(?:[-'][A-Za-zА-Яа-яЁё]+)*")
CYRILLIC_RE = re.compile(r"[А-Яа-яЁё]")
LATIN_WORD_RE = re.compile(r"\b[A-Za-z][A-Za-z'-]{2,}\b")

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
    "Debug",
    "ENG",
    "EXP",
    "HDR",
    "INT",
    "JPN",
    "LV",
    "Microsoft",
    "Nintendo",
    "OK",
    "ParadoX",
    "PlayStation",
    "SDGP",
    "SPD",
    "Steam",
    "Store",
    "Stranger",
    "Time",
    "USB",
    "Xros",
    "eShop",
}

ALLOW_LATIN_PHRASES = {
    "Accel Arm",
    "Alter-B",
    "Alter-S",
    "BAN-TYO",
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
    "Home Expo",
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
    "THE IDOL@STER",
    "Steam Deck",
    "Ulforce",
    "WE ARE Xros Heart",
    "ZERO-ARMS",
    "Zwart Defeat",
}

COMMON_ENGLISH_WORDS = {
    "about",
    "after",
    "again",
    "also",
    "and",
    "are",
    "because",
    "before",
    "but",
    "can",
    "come",
    "could",
    "does",
    "doing",
    "even",
    "for",
    "from",
    "going",
    "have",
    "here",
    "just",
    "know",
    "like",
    "make",
    "now",
    "really",
    "right",
    "should",
    "some",
    "that",
    "the",
    "then",
    "there",
    "they",
    "this",
    "what",
    "when",
    "where",
    "which",
    "with",
    "would",
    "you",
    "your",
}

TEMPLATE_STOPWORDS = {
    "а",
    "без",
    "бы",
    "в",
    "вам",
    "вас",
    "вот",
    "все",
    "вы",
    "где",
    "да",
    "для",
    "до",
    "его",
    "ее",
    "её",
    "же",
    "за",
    "и",
    "из",
    "или",
    "их",
    "к",
    "как",
    "когда",
    "ли",
    "мне",
    "мы",
    "на",
    "не",
    "но",
    "о",
    "он",
    "она",
    "они",
    "от",
    "по",
    "при",
    "с",
    "со",
    "так",
    "то",
    "ты",
    "у",
    "уже",
    "что",
    "это",
    "я",
}

# Manually reviewed contextual false positives.  Only the listed heuristic
# category is suppressed; any different issue found in the same row remains a
# candidate on later runs.
REVIEWED_FALSE_POSITIVE_CATEGORIES = {
    ("patch_text01", "message/d04.mbe/000_Sheet1.csv", "f_d0407_0020_0030"): {"address"},
    ("patch_text01", "message/d06.mbe/000_Sheet1.csv", "f_d0608_0010_0030"): {"address"},
    ("patch_text01", "message/d09.mbe/000_Sheet1.csv", "f_d0902_0030_0240"): {"address"},
    ("patch_text01", "message/m160.mbe/000_Sheet1.csv", "m160_060_240"): {"address"},
    ("patch_text01", "text/digitter_message.mbe/000_Sheet1.csv", "hazama_00_130_1"): {"address"},
    ("addcont_01_text01", "message/dlcep001_field.mbe/000_Sheet1.csv", "dlcep001_0030_0010"): {"translationese"},
    ("addcont_02_text01", "message/d230.mbe/000_Sheet1.csv", "d230_020_140"): {"translationese"},
    ("addcont_03_text01", "message/d320.mbe/000_Sheet1.csv", "d320_040_070"): {"translationese"},
    ("addcont_03_text01", "message/d320.mbe/000_Sheet1.csv", "d320_040_200"): {"translationese"},
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "migao_001_4_reaction_char_MIRAGEGAOGAMON"): {"translationese"},
    ("patch_text01", "message/field_text.mbe/000_Sheet1.csv", "dummy_dlc010_0315"): {"translationese"},
    ("patch_text01", "message/s030_183.mbe/000_Sheet1.csv", "s030_183_250"): {"translationese"},
    ("patch_text01", "message/s110_101.mbe/000_Sheet1.csv", "s110_101_660"): {"translationese"},
    ("patch_text01", "text/digitter_message.mbe/000_Sheet1.csv", "main_290_060_010"): {"translationese"},
    ("patch_text01", "message/s910_169.mbe/000_Sheet1.csv", "s910_169_560"): {"repetition"},
}


@dataclass
class Entry:
    package: str
    relative: str
    line: int
    key: str
    speaker: str
    ru: str
    en: str
    scope: str
    prev_ru: str = ""
    next_ru: str = ""
    issues: list["Issue"] = field(default_factory=list)


@dataclass(frozen=True)
class Issue:
    score: int
    category: str
    reason: str
    evidence: str


@dataclass(frozen=True)
class PatternRule:
    score: int
    category: str
    reason: str
    ru_pattern: re.Pattern[str]
    scopes: frozenset[str] = frozenset()


@dataclass(frozen=True)
class SourceRule:
    score: int
    category: str
    reason: str
    en_pattern: re.Pattern[str]
    ru_pattern: re.Pattern[str]


def rx(pattern: str) -> re.Pattern[str]:
    return re.compile(pattern, re.I | re.S)


TARGET_RULES = [
    PatternRule(
        96,
        "encoding",
        "битая кодировка",
        re.compile(r"(?:вЂ|�|[\x80-\x9f]|[\u0400\u0402-\u040f\u0450\u0452-\u045f])"),
    ),
    PatternRule(94, "terminology", "непереведённые HP/SP", rx(r"(?<![A-Za-z])(?:HP|SP)(?![A-Za-z])")),
    PatternRule(92, "machine_exact", "точная старая машинная калька", rx(r"обожал в прошлом|не то чтобы я мог|прийти в переулки|No Text|Changed to")),
    PatternRule(90, "machine_exact", "буквальное apologize on their behalf", rx(r"принес(?:у|ём|ем) извинения от (?:их|его|её) имени")),
    PatternRule(88, "machine_exact", "буквальное someone did something to you", rx(r"кто-то что-то с тобой сделал")),
    PatternRule(88, "machine_exact", "буквальное take your time", rx(r"возьми(?:те)? сво[её] время")),
    PatternRule(88, "machine_exact", "буквальное feel free", rx(r"чувствуй(?:те)? себя свободн")),
    PatternRule(88, "machine_exact", "буквальное you got this / I got it", rx(r"^\s*(?:ты|я) получил[аи]? это[.!?…]*\s*$")),
    PatternRule(86, "machine_exact", "буквальное way to go", rx(r"\b(?:путь|способ) (?:идти|пойти)\b")),
    PatternRule(86, "machine_exact", "буквальное never mind", rx(r"\bникогда не думай(?:те)?\b")),
    PatternRule(86, "machine_exact", "буквальное by all means", rx(r"\bвсеми средствами\b")),
    PatternRule(84, "machine_exact", "перегруженное what is going on right now", rx(r"что вообще происходит прямо сейчас")),
    PatternRule(82, "machine_exact", "буквальное how high", rx(r"как высоко[^.!?]{0,50}(?:поднять|поднимет|подняться)")),
    PatternRule(80, "machine_exact", "неестественная формула подтверждения", rx(r"^\s*это верно[.!?…]*\s*$"), frozenset({"dialogue", "digitter"})),
    PatternRule(78, "machine_exact", "подозрительное strange attack", rx(r"\bстранн(?:ое|ого|ому) нападени"), frozenset({"dialogue", "digitter"})),
    PatternRule(77, "agreement", "форма жизни согласована как мужской род", rx(r"форма жизни[^.!?]{0,120}\b(?:должен|ценным|обнаружен|неизвестный)\b")),
    PatternRule(75, "machine_exact", "буквальная реакция no response", rx(r"\bответа нет\b"), frozenset({"dialogue", "digitter"})),
    PatternRule(72, "machine_phrase", "буквальная конструкция get past it", rx(r"\bпроб(?:ь|и)[^.!?]{0,30}через (?:него|неё)\b"), frozenset({"dialogue"})),
    PatternRule(70, "machine_phrase", "неестественное приблизиться к зданию", rx(r"\bприблизиться к зданию\b"), frozenset({"dialogue", "digitter"})),
    PatternRule(66, "translationese", "канцелярское в настоящее время", rx(r"\bв настоящее время\b"), frozenset({"dialogue", "digitter"})),
    PatternRule(66, "translationese", "канцелярское на данный момент", rx(r"\bна данный момент\b"), frozenset({"dialogue", "digitter"})),
    PatternRule(66, "translationese", "английский каркас the fact that", rx(r"\b(?:тот факт|факт, что)\b"), frozenset({"dialogue", "digitter"})),
    PatternRule(64, "translationese", "канцелярское осуществить", rx(r"\bосуществ\w*\b"), frozenset({"dialogue", "digitter"})),
    PatternRule(62, "translationese", "тяжёлое удовлетворён/удовлетворение", rx(r"\bудовлетвор\w*\b"), frozenset({"dialogue", "digitter"})),
    PatternRule(60, "translationese", "канцелярское является", rx(r"\bявля(?:ется|ются|лся|лась|лось|лись)\b"), frozenset({"dialogue", "digitter"})),
    PatternRule(58, "translationese", "канцелярское данный", rx(r"\bданн(?:ый|ая|ое|ого|ому|ым|ом|ую|ой)\b"), frozenset({"dialogue", "digitter"})),
    PatternRule(58, "translationese", "канцелярское относительно/касательно", rx(r"\b(?:относительно|касательно)\b"), frozenset({"dialogue", "digitter"})),
    PatternRule(58, "translationese", "канцелярское наличие/присутствие", rx(r"\b(?:наличи[еяю]|присутстви[еяю])\b"), frozenset({"dialogue", "digitter"})),
    PatternRule(56, "anglicism", "сырой игровой англицизм", rx(r"\b(?:ивент|скилл|левел|апгрейд|дамаг|юзать|рандом)\w*\b")),
    PatternRule(54, "translationese", "буквальное в конечном итоге", rx(r"\bв конечном итоге\b"), frozenset({"dialogue", "digitter"})),
    PatternRule(50, "translationese", "тяжёлое в процессе", rx(r"\bв процессе\b"), frozenset({"dialogue", "digitter"})),
    PatternRule(88, "machine_exact", "future holds переведено как «будущая версия держит»", rx(r"будущ(?:ая|ее) (?:версия )?(?:держит|хранит)")),
    PatternRule(88, "machine_exact", "сломанная конструкция when in weapon form", rx(r"\bкогда в оружи[ея] форма\b")),
    PatternRule(86, "agreement", "несогласованное повторяющийся тренировки", rx(r"\bповторяющ(?:ийся|аяся|ееся) тренировк(?:и|ами)\b")),
    PatternRule(86, "machine_exact", "буквальное take place", rx(r"\bвзять место\b")),
    PatternRule(86, "machine_exact", "буквальное make sense", rx(r"\b(?:делать|сделать) смысл(?:а)?\b")),
    PatternRule(86, "machine_exact", "буквальное look forward to", rx(r"\bсмотр(?:ю|им|ит|ят) впер[её]д к\b")),
    PatternRule(84, "machine_exact", "буквальное as long as", rx(r"\bтак долго,? как\b")),
    PatternRule(84, "machine_exact", "буквальное for good", rx(r"\bдля хорошего\b")),
    PatternRule(82, "machine_exact", "буквальное come up with", rx(r"\bприйти с (?:иде|план|решени)")),
    PatternRule(96, "machine_exact", "сломанная фраза «перешёл на эволюционировал»", rx(r"\bпереш[её]л\s+на\s+эволюционировал\b")),
    PatternRule(82, "machine_exact", "буквальное wild things", rx(r"\bдикими были вещи\b")),
]


SOURCE_RULES = [
    SourceRule(94, "source_calque", "not that/like I can → не то чтобы я мог", rx(r"\bnot (?:that|like) i (?:can|could)\b"), rx(r"\bне то чтобы я мог\b")),
    SourceRule(92, "source_calque", "apologize on their behalf → извинения от их имени", rx(r"\bapologi[sz]e on (?:their|his|her) behalf\b"), rx(r"извинения от (?:их|его|её) имени")),
    SourceRule(90, "source_calque", "take your time → возьми своё время", rx(r"\btake your time\b"), rx(r"возьми(?:те)? сво[её] время")),
    SourceRule(90, "source_calque", "feel free → чувствуй себя свободно", rx(r"\bfeel free\b"), rx(r"чувствуй(?:те)? себя свободн")),
    SourceRule(90, "source_calque", "it is up to you → это зависит от тебя", rx(r"\bit(?:'s| is) up to you\b"), rx(r"это зависит от тебя")),
    SourceRule(88, "source_calque", "go ahead → идти вперёд", rx(r"\bgo ahead\b"), rx(r"\b(?:иди|идите|пойти|идти) впер[её]д\b")),
    SourceRule(88, "source_calque", "way to go → путь/способ идти", rx(r"\bway to go\b"), rx(r"\b(?:путь|способ) (?:идти|пойти)\b")),
    SourceRule(88, "source_calque", "by all means → всеми средствами", rx(r"\bby all means\b"), rx(r"\bвсеми средствами\b")),
    SourceRule(86, "source_calque", "never mind → никогда не думай", rx(r"\bnever mind\b"), rx(r"\bникогда не думай(?:те)?\b")),
    SourceRule(84, "source_calque", "how high → как высоко", rx(r"\bhow high\b"), rx(r"\bкак высоко\b")),
    SourceRule(82, "source_calque", "right now усилено дважды", rx(r"\b(?:right now|what(?:'s| is) going on)\b"), rx(r"\bвообще[^.!?]{0,40}прямо сейчас\b")),
    SourceRule(80, "source_calque", "that's right → это верно", rx(r"\bthat(?:'s| is) right\b"), rx(r"^\s*это верно[.!?…]*\s*$")),
    SourceRule(78, "source_calque", "someone did something to you переведено пословно", rx(r"\bsomeone .{0,35}(?:did|done) something to you\b"), rx(r"кто-то что-то с тобой сделал")),
    SourceRule(76, "source_calque", "no response → ответа нет без учёта состояния", rx(r"\b(?:no response|isn't responding|doesn't respond)\b"), rx(r"\bответа нет\b")),
    SourceRule(74, "source_calque", "get past it → пробиться через него/неё", rx(r"\bget past (?:it|this|that)\b"), rx(r"проб[^.!?]{0,30}через (?:него|неё)")),
    SourceRule(70, "source_calque", "currently → в настоящее время", rx(r"\bcurrently\b"), rx(r"\bв настоящее время\b")),
    SourceRule(68, "source_calque", "at this moment → на данный момент", rx(r"\bat (?:this|the) moment\b"), rx(r"\bна данный момент\b")),
    SourceRule(66, "source_calque", "the fact that сохранено буквально", rx(r"\bthe fact that\b"), rx(r"\b(?:тот факт|факт, что)\b")),
    SourceRule(62, "source_calque", "seems to be → кажется, что является", rx(r"\bseems? to be\b"), rx(r"кажется,? что[^.!?]{0,80}явля")),
    SourceRule(60, "source_calque", "there is/are → имеется", rx(r"\bthere (?:is|are|was|were)\b"), rx(r"\bиме(?:ется|ются|лся|лась)\b")),
    SourceRule(92, "source_calque", "what the future holds переведено буквально", rx(r"\bwhat (?:its|his|her|their) future holds\b"), rx(r"будущ(?:ая|ее)[^.!?]{0,25}(?:держит|хранит)")),
    SourceRule(90, "source_calque", "when in weapon form переведено с нарушением грамматики", rx(r"\bwhen in weapon form\b"), rx(r"\bкогда в оружи[ея] форма\b")),
    SourceRule(86, "source_calque", "walk toward the other side переведено пословно", rx(r"\bwalk(?:ing|ed)? toward the other side\b"), rx(r"\b(?:идти|идёт|шел|шёл) к другой стороне\b")),
    SourceRule(84, "source_calque", "tempered through repeated training переведено пословно", rx(r"\btempered through repeated training\b"), rx(r"закал[^.!?]{0,35}через[^.!?]{0,35}трениров")),
    SourceRule(82, "source_calque", "composition is enough to deem it переведено пословно", rx(r"\bcomposition is enough to deem it\b"), rx(r"состав[^.!?]{0,35}достаточен[^.!?]{0,35}считать")),
    SourceRule(80, "source_calque", "while repairing space-time → во время ремонта", rx(r"\bwhile repairing space-time\b"), rx(r"\bво время ремонта пространства-времени\b")),
    SourceRule(76, "source_calque", "ability it possesses сохранено тяжёлым оборотом", rx(r"\bability .{0,35} it possesses\b"), rx(r"способност[^.!?]{0,50}которой он обладает")),
    SourceRule(90, "source_calque", "take place переведено буквально", rx(r"\btake place\b"), rx(r"\b(?:взять|занять) место\b")),
    SourceRule(90, "source_calque", "make sense переведено буквально", rx(r"\bmake sense\b"), rx(r"\b(?:делать|сделать) смысл\b")),
    SourceRule(90, "source_calque", "look forward to переведено буквально", rx(r"\blook forward to\b"), rx(r"\bсмотр[^.!?]{0,20}впер[её]д к\b")),
    SourceRule(88, "source_calque", "as long as переведено буквально", rx(r"\bas long as\b"), rx(r"\bтак долго,? как\b")),
    SourceRule(88, "source_calque", "for good переведено буквально", rx(r"\bfor good\b"), rx(r"\bдля хорошего\b")),
    SourceRule(86, "source_calque", "come up with переведено буквально", rx(r"\bcome up with\b"), rx(r"\bприйти с (?:иде|план|решени)")),
    SourceRule(84, "source_calque", "be my guest переведено буквально", rx(r"\bbe my guest\b"), rx(r"\bбуд(?:ь|ьте) моим гостем\b")),
]


TEMPLATE_RULES = [
    ("medium", "actually → действительно/на самом деле", rx(r"\bactually\b"), rx(r"\b(?:действительно|на самом деле)\b")),
    ("low", "really → действительно", rx(r"\breally\b"), rx(r"\bдействительно\b")),
    ("low", "quite → довольно", rx(r"\bquite\b"), rx(r"\bдовольно\b")),
    ("low", "various → различные", rx(r"\bvarious\b"), rx(r"\bразличн\w*\b")),
    ("medium", "right now → прямо сейчас", rx(r"\bright now\b"), rx(r"\bпрямо сейчас\b")),
    ("low", "some kind of → какой-то", rx(r"\bsome kind of\b"), rx(r"\bкак(?:ой|ая|ое|ие)-то\b")),
    ("medium", "in the end → в конечном итоге", rx(r"\bin the end\b"), rx(r"\bв конечном итоге\b")),
    ("low", "seems → кажется, что", rx(r"\bseems?\b"), rx(r"\bкажется,? что\b")),
    ("medium", "as for → что касается", rx(r"\bas for\b"), rx(r"\bчто касается\b")),
    ("medium", "regarding → относительно/касательно", rx(r"\bregarding\b"), rx(r"\b(?:относительно|касательно)\b")),
    ("medium", "currently → в настоящее время", rx(r"\bcurrently\b"), rx(r"\bв настоящее время\b")),
    ("medium", "presence → наличие/присутствие", rx(r"\bpresence\b"), rx(r"\b(?:наличи[еяю]|присутстви[еяю])\b")),
    ("low", "process → в процессе", rx(r"\bprocess\b"), rx(r"\bв процессе\b")),
    ("medium", "seems to be → кажется, что является", rx(r"\bseems? to be\b"), rx(r"кажется,? что[^.!?]{0,80}явля")),
]


def clean_text(value: str) -> str:
    return "\n".join(
        line.rstrip()
        for line in value.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    )


def text_column(relative: Path, row: list[str]) -> int | None:
    if "message" in relative.parts:
        return 2 if len(row) > 2 else None
    if "text" in relative.parts:
        return 1 if len(row) > 1 else None
    return None


def scope_for(relative: Path) -> str:
    rel = relative.as_posix().lower()
    if rel.startswith("message/"):
        return "dialogue"
    if "digitter" in rel:
        return "digitter"
    if "profile" in rel:
        return "profile"
    if "tutorial" in rel or "help" in rel:
        return "tutorial/help"
    if any(name in rel for name in ("info_message", "common_message", "yes_no")):
        return "ui/system"
    return "text"


def original_path(package: str, relative: Path) -> Path:
    return ORIGINAL_ROOT / package / "csv" / relative


def read_original(path: Path) -> dict[str, list[str]]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return {row[0]: row for row in csv.reader(handle) if row}


def source_rows_for(package: str, relative: Path) -> dict[str, list[str]]:
    rows: dict[str, list[str]] = {}
    if package == "patch_text01":
        rows.update(read_original(original_path("app_text01", relative)))
    rows.update(read_original(original_path(package, relative)))
    return rows


def load_entries() -> tuple[list[Entry], Counter[str]]:
    entries: list[Entry] = []
    coverage: Counter[str] = Counter()
    for package_root in sorted(path for path in CSV_ROOT.iterdir() if path.is_dir()):
        package = package_root.name
        for path in sorted(package_root.rglob("*.csv")):
            relative = path.relative_to(package_root)
            if not ({"message", "text"} & set(relative.parts)):
                continue
            source_rows = source_rows_for(package, relative)
            if not source_rows:
                coverage["files_without_source"] += 1
            with path.open("r", encoding="utf-8-sig", newline="") as handle:
                current_rows = list(csv.reader(handle))
            file_entries: list[Entry] = []
            for line_no, row in enumerate(current_rows, 1):
                if not row or (line_no == 1 and row[0].startswith("string")):
                    continue
                column = text_column(relative, row)
                if column is None or len(row) <= column or not row[column].strip():
                    continue
                source_row = source_rows.get(row[0], [])
                source = source_row[column] if len(source_row) > column else ""
                coverage["rows"] += 1
                coverage["rows_with_source" if source else "rows_without_source"] += 1
                file_entries.append(
                    Entry(
                        package=package,
                        relative=relative.as_posix(),
                        line=line_no,
                        key=row[0],
                        speaker=row[1] if "message" in relative.parts and len(row) > 1 else "",
                        ru=clean_text(row[column]),
                        en=clean_text(source),
                        scope=scope_for(relative),
                    )
                )
            for index, entry in enumerate(file_entries):
                if index:
                    entry.prev_ru = file_entries[index - 1].ru
                if index + 1 < len(file_entries):
                    entry.next_ru = file_entries[index + 1].ru
            entries.extend(file_entries)
    return entries, coverage


def add_issue(entry: Entry, score: int, category: str, reason: str, evidence: str) -> None:
    issue = Issue(score, category, reason, clean_text(evidence)[:220])
    if issue not in entry.issues:
        entry.issues.append(issue)


def apply_target_rules(entry: Entry) -> None:
    for rule in TARGET_RULES:
        if rule.scopes and entry.scope not in rule.scopes:
            continue
        match = rule.ru_pattern.search(entry.ru)
        if match:
            add_issue(entry, rule.score, rule.category, rule.reason, match.group(0))


def apply_source_rules(entry: Entry) -> None:
    if not entry.en:
        return
    for rule in SOURCE_RULES:
        en_match = rule.en_pattern.search(entry.en)
        ru_match = rule.ru_pattern.search(entry.ru)
        if en_match and ru_match:
            add_issue(
                entry,
                rule.score,
                rule.category,
                rule.reason,
                f"EN: {en_match.group(0)} | RU: {ru_match.group(0)}",
            )

    paired_amplifiers = [
        (r"\bactually\b", r"\b(?:действительно|на самом деле)\b", "actually переведено шаблонно"),
        (r"\breally\b", r"\bдействительно\b", "really → действительно"),
        (r"\bquite\b", r"\bдовольно\b", "quite → довольно"),
        (r"\bvarious\b", r"\bразличн\w*\b", "various → различные"),
    ]
    for en_pattern, ru_pattern, reason in paired_amplifiers:
        if re.search(en_pattern, entry.en, re.I) and re.search(ru_pattern, entry.ru, re.I):
            add_issue(entry, 24, "literal_lexeme", reason, reason)


def apply_punctuation_rules(entry: Entry) -> None:
    checks = [
        (92, "пробел перед знаком препинания", r"[ \t]+[?!]"),
        (84, "повтор запятой/двоеточия", r"[,;:]{2,}"),
        (82, "две точки вместо многоточия", r"(?<![.?!])\.\.(?!\.)"),
        (72, "двойной пробел", r"(?<!\n)[ \t]{2,}"),
    ]
    for score, reason, pattern in checks:
        if reason == "двойной пробел" and entry.scope not in {"dialogue", "digitter"}:
            continue
        match = re.search(pattern, entry.ru, re.I)
        if match:
            add_issue(entry, score, "punctuation", reason, match.group(0))

    duplicate = re.search(r"\b([А-Яа-яЁё]{3,})\b(?!-)\s+\1\b(?!-)", entry.ru, re.I)
    if duplicate:
        word = duplicate.group(1).lower()
        expressive = {"ага", "ах", "вау", "да", "инори", "кхе", "нет", "ну", "ой", "ох", "ха", "хе", "эй"}
        source_repeats = bool(re.search(r"\b([A-Za-z]{2,})\b(?:[,.!?…]*\s+)\1\b", entry.en, re.I))
        if word not in expressive and not source_repeats:
            add_issue(entry, 90, "punctuation", "двойное слово", duplicate.group(0))


def apply_agreement_rules(entry: Entry) -> None:
    checks = [
        (90, "она + форма мужского рода", r"\bона\b[^,.!?;\n]{0,45}\b(?:был|готов|должен|сказал|сделал|решил|смог|пришёл|ушёл|нашёл|понял|увидел|знал|думал|хотел)\b"),
        (90, "он + форма женского рода", r"\bон\b[^,.!?;\n]{0,45}\b(?:была|готова|должна|сказала|сделала|решила|смогла|пришла|ушла|нашла|поняла|увидела|знала|думала|хотела)\b"),
        (88, "они + форма единственного числа", r"\bони\b[^,.!?;\n]{0,45}\b(?:был|была|готов|готова|должен|должна)\b"),
        (48, "женский предмет + мужское местоимение", r"\b(?:дверь|крыша|атака|форма|система|битва|миссия|капсула|машина|комната)\b[^.!?\n]{0,85}\b(?:он|его|нему|нём)\b"),
        (48, "средний предмет + женское местоимение", r"\b(?:здание|устройство|существо|сообщение|оружие|состояние)\b[^.!?\n]{0,85}\b(?:она|её|ней)\b"),
    ]
    for score, reason, pattern in checks:
        match = re.search(pattern, entry.ru, re.I)
        if match:
            add_issue(entry, score, "agreement", reason, match.group(0))

    singular = re.search(r"\b(?:ты|тебя|тебе|тобой|твой|твоя|твоё|твои)\b", entry.ru, re.I)
    formal = re.search(r"\b(?:вы|вас|вам|вами|ваш|ваша|ваше|ваши)\b", entry.ru, re.I)
    if singular and formal:
        add_issue(
            entry,
            76,
            "address",
            "смешение ты/вы в одной реплике",
            f"{singular.group(0)} / {formal.group(0)}",
        )


def apply_repetition_rules(entry: Entry) -> None:
    compact = re.sub(r"\s+", " ", TAG_RE.sub(" ", entry.ru)).strip()
    repeated_subject = re.search(
        r"\b(я|мы|ты|вы|он|она|они)\s+(?:долж\w+|буд\w+|мож\w+)[^.!?]{0,120}[.!?…]+\s*\1\s+(?:долж\w+|буд\w+|мож\w+)",
        compact,
        re.I,
    )
    if repeated_subject:
        add_issue(entry, 54, "repetition", "повтор английского подлежащего/модального каркаса", repeated_subject.group(0))

    stacked = re.search(
        r"\b(?:действительно|фактически|на самом деле)\b[^.!?]{0,70}\b(?:действительно|фактически|на самом деле)\b",
        compact,
        re.I,
    )
    if stacked:
        add_issue(entry, 72, "repetition", "дублирование усилителей", stacked.group(0))

    time_stack = re.search(
        r"\b(?:прямо сейчас|в настоящий момент|на данный момент)\b[^.!?]{0,70}\b(?:прямо сейчас|в настоящий момент|на данный момент)\b",
        compact,
        re.I,
    )
    if time_stack:
        add_issue(entry, 78, "repetition", "дублирование указания времени", time_stack.group(0))

    if len(compact) <= 260 and len(re.findall(r"\bэто\b", compact, re.I)) >= 4:
        add_issue(entry, 44, "repetition", "перегруз местоимением «это»", "это × 4+")


def apply_latin_rules(entry: Entry) -> None:
    cleaned = TAG_RE.sub(" ", entry.ru)
    for phrase in sorted(ALLOW_LATIN_PHRASES, key=len, reverse=True):
        cleaned = re.sub(re.escape(phrase), " ", cleaned, flags=re.I)
    cleaned = re.sub(r"\b[IVXLCDM]{2,}\b", " ", cleaned)
    cleaned = re.sub(r"\b(?:ui|vo|char|icon|tutorial|quest|field|main|sub|dlc|s|m|d|f|g|r|t)_?[A-Za-z0-9_]+\b", " ", cleaned)
    unknown = [
        word
        for word in LATIN_WORD_RE.findall(cleaned)
        if word not in ALLOW_LATIN and word.upper() not in ALLOW_LATIN
    ]
    if not unknown:
        return
    common = [word for word in unknown if word.lower() in COMMON_ENGLISH_WORDS]
    if CYRILLIC_RE.search(cleaned) and (len(unknown) >= 2 or common):
        add_issue(entry, 76 if common else 60, "english_tail", "английский хвост в русской строке", ", ".join(sorted(set(unknown))[:12]))
    elif not CYRILLIC_RE.search(cleaned) and len(unknown) >= 4:
        add_issue(entry, 52, "english_full", "возможно, строка осталась английской", ", ".join(sorted(set(unknown))[:12]))


def apply_length_divergence(entry: Entry) -> None:
    if not entry.en or entry.scope not in {"dialogue", "digitter", "profile"}:
        return
    en_words = re.findall(r"[A-Za-z]+", TAG_RE.sub(" ", entry.en))
    ru_words = normalized_words(entry.ru)
    if len(en_words) < 10 or not ru_words:
        return
    ratio = len(ru_words) / len(en_words)
    if ratio <= 0.20:
        add_issue(entry, 60, "source_divergence", "русская реплика намного короче оригинала", f"words RU/EN = {len(ru_words)}/{len(en_words)} ({ratio:.2f})")
    elif ratio >= 1.38:
        add_issue(entry, 54, "source_divergence", "русская реплика намного длиннее оригинала", f"words RU/EN = {len(ru_words)}/{len(en_words)} ({ratio:.2f})")


def score_entry(entry: Entry) -> int:
    if not entry.issues:
        return 0
    scores = sorted((issue.score for issue in entry.issues), reverse=True)
    score = scores[0]
    if len(scores) > 1:
        score += min(12, sum(max(0, value - 20) for value in scores[1:]) // 12)
    if any(issue.category == "source_calque" for issue in entry.issues):
        score += 3
    return min(100, score)


def priority_for(score: int) -> tuple[str, str]:
    if score >= 86:
        return "P1", "высокая (ориентир 85–95%, проверить контекст)"
    if score >= 68:
        return "P2", "средне-высокая (ориентир 65–85%)"
    if score >= 50:
        return "P3", "средняя (ориентир 45–70%)"
    return "P4", "низкая (только выборочная проверка)"


def audit_entries(entries: list[Entry]) -> list[dict[str, str | int]]:
    output: list[dict[str, str | int]] = []
    for entry in entries:
        apply_target_rules(entry)
        apply_source_rules(entry)
        apply_punctuation_rules(entry)
        apply_agreement_rules(entry)
        apply_repetition_rules(entry)
        apply_latin_rules(entry)
        apply_length_divergence(entry)
        suppressed = REVIEWED_FALSE_POSITIVE_CATEGORIES.get(
            (entry.package, entry.relative, entry.key), set()
        )
        if suppressed:
            entry.issues[:] = [
                issue for issue in entry.issues if issue.category not in suppressed
            ]
        score = score_entry(entry)
        if score < 44:
            continue
        priority, confidence = priority_for(score)
        issues = sorted(entry.issues, key=lambda item: (-item.score, item.category, item.reason))
        output.append(
            {
                "priority": priority,
                "score": score,
                "confidence": confidence,
                "categories": " | ".join(dict.fromkeys(issue.category for issue in issues)),
                "reasons": " | ".join(dict.fromkeys(issue.reason for issue in issues)),
                "evidence": " | ".join(dict.fromkeys(issue.evidence for issue in issues)),
                "scope": entry.scope,
                "package": entry.package,
                "file": entry.relative,
                "line": entry.line,
                "key": entry.key,
                "speaker": entry.speaker,
                "source_en": entry.en,
                "current_ru": entry.ru,
                "previous_ru": entry.prev_ru,
                "next_ru": entry.next_ru,
            }
        )
    output.sort(key=lambda row: (-int(row["score"]), str(row["scope"]), str(row["package"]), str(row["file"]), str(row["key"])))
    return output


def normalized_words(text: str) -> list[str]:
    cleaned = TAG_RE.sub(" ", text).replace("ё", "е").lower()
    return [word for word in WORD_RE.findall(cleaned) if CYRILLIC_RE.search(word)]


def normalized_line(text: str) -> str:
    return " ".join(normalized_words(text))


def normalized_target_exact(text: str) -> str:
    cleaned = TAG_RE.sub(" ", text).replace("ё", "е").lower()
    return " ".join(re.findall(r"[A-Za-zА-Яа-яЁё]+(?:[-'][A-Za-zА-Яа-яЁё]+)*|\d+", cleaned))


def normalized_source(text: str) -> str:
    cleaned = TAG_RE.sub(" ", text).lower()
    return " ".join(WORD_RE.findall(cleaned))


def canonical_source(text: str) -> str:
    words = normalized_source(text).split()
    forms = {
        "are": "be",
        "is": "be",
        "was": "be",
        "were": "be",
        "has": "have",
        "had": "have",
    }
    return " ".join(forms.get(word, word) for word in words)


def source_identifiers(text: str) -> frozenset[str]:
    cleaned = TAG_RE.sub(" ", text)
    cleaned = re.sub(r"(?<![A-Za-z])A\s+(?=[A-Za-z])", " ", cleaned)
    identifiers: set[str] = set(re.findall(r"(?<!\d)\d+(?!\d)", cleaned))
    for token in re.findall(r"(?<![A-Za-z])[A-Z]{1,3}(?![A-Za-z])", cleaned):
        if token in {"I", "Y"}:
            continue
        identifiers.update(token)
    return frozenset(identifiers)


def build_template_report(entries: list[Entry]) -> list[dict[str, str | int]]:
    report: list[dict[str, str | int]] = []
    for risk, label, en_pattern, ru_pattern in TEMPLATE_RULES:
        group = [entry for entry in entries if entry.en and en_pattern.search(entry.en) and ru_pattern.search(entry.ru)]
        if not group:
            continue
        files = {f"{entry.package}/{entry.relative}" for entry in group}
        source_variants = {normalized_source(entry.en) for entry in group}
        examples = group[:6]
        report.append(
            {
                "type": "source_aligned_pattern",
                "risk": risk,
                "occurrences": len(group),
                "source_variants": len(source_variants),
                "files": len(files),
                "template": label,
                "example_keys": " | ".join(f"{entry.package}:{entry.key}" for entry in examples),
                "source_examples": " | ".join(dict.fromkeys(entry.en for entry in examples)),
                "note": "Системный буквальный шаблон; оценить выборку в разных сценах, не заменять автоматически.",
            }
        )

    exact: dict[str, list[Entry]] = defaultdict(list)
    for entry in entries:
        words = normalized_words(entry.ru)
        if entry.en and 5 <= len(words) <= 35:
            exact[normalized_target_exact(entry.ru)].append(entry)

    for normalized, group in exact.items():
        source_variants = {canonical_source(entry.en) for entry in group if entry.en}
        files = {f"{entry.package}/{entry.relative}" for entry in group}
        if len(group) < 2 or len(source_variants) < 2:
            continue
        examples = group[:5]
        identifier_variants = {source_identifiers(entry.en) for entry in group}
        identifier_collision = len(identifier_variants) > 1 and all(identifier_variants)
        report.append(
            {
                "type": "identifier_collision" if identifier_collision else "same_ru_different_en",
                "risk": "high" if identifier_collision else "medium",
                "occurrences": len(group),
                "source_variants": len(source_variants),
                "files": len(files),
                "template": examples[0].ru,
                "example_keys": " | ".join(f"{entry.package}:{entry.key}" for entry in examples),
                "source_examples": " | ".join(dict.fromkeys(entry.en for entry in examples)),
                "note": (
                    "Одинаковый русский текст скрывает разные номера/буквы оригинала; вероятна потеря идентификатора."
                    if identifier_collision
                    else "Одинаковая русская формула скрывает разные английские реплики; проверить потерю оттенков."
                ),
            }
        )

    ngrams: dict[str, list[Entry]] = defaultdict(list)
    seen_pairs: set[tuple[str, str, str]] = set()
    for entry in entries:
        words = normalized_words(entry.ru)
        if not entry.en or len(words) < 7:
            continue
        for size in (5, 6):
            for start in range(len(words) - size + 1):
                gram_words = words[start : start + size]
                if sum(word not in TEMPLATE_STOPWORDS for word in gram_words) < 3:
                    continue
                gram = " ".join(gram_words)
                marker = (gram, entry.package, entry.key)
                if marker in seen_pairs:
                    continue
                seen_pairs.add(marker)
                ngrams[gram].append(entry)

    for gram, group in ngrams.items():
        files = {f"{entry.package}/{entry.relative}" for entry in group}
        source_variants = {canonical_source(entry.en) for entry in group if entry.en}
        if len(group) < 8 or len(source_variants) < 4:
            continue
        examples = group[:5]
        report.append(
            {
                "type": "repeated_ngram",
                "risk": "low",
                "occurrences": len(group),
                "source_variants": len(source_variants),
                "files": len(files),
                "template": gram,
                "example_keys": " | ".join(f"{entry.package}:{entry.key}" for entry in examples),
                "source_examples": " | ".join(dict.fromkeys(entry.en for entry in examples)),
                "note": "Повторяемый шаблон; проверять выборочно, массовая замена запрещена.",
            }
        )

    report.sort(
        key=lambda row: (
            {"identifier_collision": 0, "same_ru_different_en": 1, "source_aligned_pattern": 2, "repeated_ngram": 3}.get(str(row["type"]), 4),
            -int(row["source_variants"]),
            -int(row["occurrences"]),
            str(row["template"]),
        )
    )
    return report[:400]


def write_csv(path: Path, rows: list[dict[str, str | int]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_summary(rows: list[dict[str, str | int]], templates: list[dict[str, str | int]], coverage: Counter[str]) -> None:
    priorities = Counter(str(row["priority"]) for row in rows)
    categories: Counter[str] = Counter()
    scopes = Counter(str(row["scope"]) for row in rows)
    reasons: Counter[str] = Counter()
    template_types = Counter(str(row["type"]) for row in templates)
    for row in rows:
        categories.update(str(row["categories"]).split(" | "))
        reasons.update(str(row["reasons"]).split(" | "))

    source_percent = 100 * coverage["rows_with_source"] / max(1, coverage["rows"])
    with OUT_SUMMARY.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write("# Аудит хвостов машинного перевода v117\n\n")
        handle.write(f"- Проверено строк: {coverage['rows']}\n")
        handle.write(f"- Сопоставлено с английским оригиналом: {coverage['rows_with_source']} ({source_percent:.1f}%)\n")
        handle.write(f"- Без доступного оригинала: {coverage['rows_without_source']} строк в {coverage['files_without_source']} файлах\n")
        handle.write(f"- Кандидатов для ручной проверки: {len(rows)}\n")
        handle.write(f"- Повторных шаблонов/коллизий: {len(templates)}\n")
        handle.write(f"- Вероятных потерь номера/буквы: {template_types['identifier_collision']}\n\n")
        handle.write("## Приоритеты\n\n")
        for priority in ("P1", "P2", "P3", "P4"):
            handle.write(f"- {priority}: {priorities[priority]}\n")
        handle.write("\nP1/P2 — очередь адресной проверки по английскому оригиналу и соседним репликам. ")
        handle.write("P3 — полезная выборка, P4 — шумная диагностическая выборка. Проценты в CSV — ориентир, а не измеренная точность.\n\n")
        handle.write("## Категории\n\n")
        for category, count in categories.most_common():
            handle.write(f"- {category}: {count}\n")
        handle.write("\n## Области\n\n")
        for scope, count in scopes.most_common():
            handle.write(f"- {scope}: {count}\n")
        handle.write("\n## Частые причины\n\n")
        for reason, count in reasons.most_common(25):
            handle.write(f"- {reason}: {count}\n")
        handle.write("\n## Как разбирать\n\n")
        handle.write("1. Сначала P1: кодировка, HP/SP, точные кальки, явное рассогласование и пунктуация.\n")
        handle.write("2. Затем P2: сверять `source_en`, `previous_ru` и `next_ru`; исправлять только подтверждённые случаи.\n")
        handle.write("3. Сначала проверить `identifier_collision`, затем `same_ru_different_en` на потерю характера и оттенков.\n")
        handle.write("4. `repeated_ngram` использовать только для выборки: совпадение само по себе не является ошибкой.\n")
        handle.write("5. Не заменять массово «действительно», «довольно», «данный» и местоимения без контекста.\n")


def main() -> None:
    entries, coverage = load_entries()
    rows = audit_entries(entries)
    templates = build_template_report(entries)
    write_csv(
        OUT_CSV,
        rows,
        [
            "priority",
            "score",
            "confidence",
            "categories",
            "reasons",
            "evidence",
            "scope",
            "package",
            "file",
            "line",
            "key",
            "speaker",
            "source_en",
            "current_ru",
            "previous_ru",
            "next_ru",
        ],
    )
    write_csv(
        OUT_TEMPLATES,
        templates,
        [
            "type",
            "risk",
            "occurrences",
            "source_variants",
            "files",
            "template",
            "example_keys",
            "source_examples",
            "note",
        ],
    )
    write_summary(rows, templates, coverage)
    print(f"Rows checked: {coverage['rows']}")
    print(f"Source aligned: {coverage['rows_with_source']} / {coverage['rows']}")
    print(f"Candidates: {len(rows)}")
    print("Priorities:", dict(Counter(str(row['priority']) for row in rows)))
    print(f"Templates: {len(templates)}")


if __name__ == "__main__":
    main()

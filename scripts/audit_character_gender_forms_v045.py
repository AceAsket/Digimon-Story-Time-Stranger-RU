from __future__ import annotations

import csv
import re
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CSV_ROOT = ROOT / "csv" / "patch_text01"
OUT_PATH = ROOT / "exports" / "character_gender_form_audit_v045.csv"


FEMALE_CHARS = {
    "char_INORI",
    "char_HIROKO",
    "char_HIROKO_8YEARSLATER",
    "char_HIROKO_FIRST",
    "char_TOUDO",
    "char_TOUDO_B",
    "char_TOUDO_8YEARSLATER",
    "char_SIMMONS",
    "char_MONIKA_SIMMONS",
    "char_MIREI",
    "char_MIREI_CHILD",
    "char_MAYBE_INORI_VOICE",
    "char_WOMEN_HOLDING_A_LOLLIPOP",
    "char_WOMAN_IN_SUIT",
    "char_HOMEROS_SLEEPY_GIRL",
    "char_YGGDRASILL_SELFISH_GIRL",
    "char_GIRL_VOICE",
    "char_MYSTERIOUS_GIRL",
    "char_PROTECTED_GIRL",
    "char_PASSERBY_WOMAN",
    "char_HIGH_SCHOOL_GIRL",
}


MALE_CHARS = {
    "char_TAKEMIYA",
    "char_TAKEMIYA_8YEARSLATER",
    "char_KUREMI",
    "char_SUMERAGI",
    "char_SUMERAGI_8YEARSLATER",
    "char_KUGA",
    "char_DR_KUGA",
    "char_YUUTA",
    "char_MAN_ON_THE_PHONE",
    "char_SUMERAGI_VOICE",
    "char_SAWABE",
    "char_SAWABE_VOICE",
    "char_KYOSUKE",
    "char_CAPTAIN_VOICE",
    "char_MAN_IN_SUIT",
    "char_GLASSES_WEARING_MAN",
    "char_PASSERBY_MAN",
    "char_HIGH_SCHOOL_BOY",
    "char_TOUHO_CALM_BOY",
    "char_POLICEMAN",
    "char_CAPTAIN",
    "char_OPERATOR_M",
}


DIGIMON_FEMALE_CHARS = {
    "char_LILITHMON",
    "char_LADYDEVIMON",
    "char_ANGEWOMON",
    "char_JUNOMON",
    "char_JUNOMON_HYSTERICMODE",
    "char_VENUSMON",
    "char_MERVAMON",
    "char_BEELSTARMON",
    "char_ARCHNEMON",
    "char_SIRENMON",
    "char_MINERVAMON",
    "char_DIANAMON",
    "char_RANAMON",
    "char_CALAMARAMON",
}


MALE_FORMS = [
    "был",
    "хотел",
    "смог",
    "уверен",
    "готов",
    "рад",
    "обнаружил",
    "услышал",
    "захотел",
    "пришел",
    "пришёл",
    "нашел",
    "нашёл",
    "видел",
    "понял",
    "думал",
    "сказал",
    "пытался",
    "стал",
    "решил",
    "получил",
    "сделал",
    "потерял",
    "устал",
    "остался",
    "прибыл",
    "родился",
    "встретил",
    "заметил",
    "создал",
    "отправился",
    "вернулся",
    "помог",
    "согласен",
    "виноват",
]


FEMALE_FORMS = [
    "была",
    "хотела",
    "смогла",
    "уверена",
    "готова",
    "рада",
    "обнаружила",
    "услышала",
    "захотела",
    "пришла",
    "нашла",
    "видела",
    "поняла",
    "думала",
    "сказала",
    "пыталась",
    "стала",
    "решила",
    "получила",
    "сделала",
    "потеряла",
    "устала",
    "осталась",
    "прибыла",
    "родилась",
    "встретила",
    "заметила",
    "создала",
    "отправилась",
    "вернулась",
    "помогла",
    "согласна",
    "виновата",
]


def unpack_text(s: str) -> str:
    bs = bytearray()
    for ch in s:
        try:
            bs.extend(ch.encode("cp1251"))
        except UnicodeEncodeError:
            code = ord(ch)
            if code < 256:
                bs.append(code)
            else:
                return s
    try:
        return bs.decode("utf-8")
    except UnicodeDecodeError:
        return s


def read_rows(path: Path) -> list[list[str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.reader(f))


def char_names() -> dict[str, str]:
    path = CSV_ROOT / "text" / "char_name.mbe" / "000_Sheet1.csv"
    names: dict[str, str] = {}
    for row in read_rows(path)[1:]:
        if len(row) > 1:
            names[row[0]] = unpack_text(row[1])
    return names


def gender_for(char_id: str) -> tuple[str | None, str]:
    if char_id in FEMALE_CHARS:
        return "female", "human"
    if char_id in MALE_CHARS:
        return "male", "human"
    if char_id in DIGIMON_FEMALE_CHARS:
        return "female", "digimon_low_confidence"
    return None, ""


def context_pattern(forms: list[str]) -> re.Pattern[str]:
    group = "|".join(re.escape(form) for form in sorted(forms, key=len, reverse=True))
    return re.compile(
        rf"(?iu)(?:^|[.!?…]\s*|\n)\s*(?:я(?:\s+\S+){{0,3}}\s+|мне\s+бы\s+)?(?:не\s+)?(?P<form>{group})\b"
    )


MALE_RE = context_pattern(MALE_FORMS)
FEMALE_RE = context_pattern(FEMALE_FORMS)


def hits_for(text: str, forms_re: re.Pattern[str]) -> list[str]:
    hits = []
    for match in forms_re.finditer(text):
        start = max(0, match.start() - 35)
        end = min(len(text), match.end() + 55)
        hits.append(text[start:end].replace("\n", " / "))
    return hits


def main() -> None:
    names = char_names()
    audit_rows = [[
        "severity",
        "expected_gender",
        "confidence",
        "speaker_id",
        "speaker_name",
        "relative_path",
        "row_id",
        "found",
        "text",
    ]]
    counts: Counter[tuple[str, str]] = Counter()
    by_speaker: defaultdict[str, int] = defaultdict(int)

    for path in sorted((CSV_ROOT / "message").rglob("000_Sheet1.csv")):
        relative = path.relative_to(CSV_ROOT).as_posix()
        for row in read_rows(path)[1:]:
            if len(row) <= 2:
                continue
            row_id, speaker_id = row[0], row[1]
            expected, confidence = gender_for(speaker_id)
            if not expected:
                continue
            text = unpack_text(row[2])
            wrong_re = MALE_RE if expected == "female" else FEMALE_RE
            for found in hits_for(text, wrong_re):
                severity = "review" if confidence == "digimon_low_confidence" else "likely_error"
                audit_rows.append([
                    severity,
                    expected,
                    confidence,
                    speaker_id,
                    names.get(speaker_id, ""),
                    relative,
                    row_id,
                    found,
                    text,
                ])
                counts[(severity, expected)] += 1
                by_speaker[speaker_id] += 1

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUT_PATH.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f, lineterminator="\n")
        writer.writerows(audit_rows)

    print(f"wrote {OUT_PATH.relative_to(ROOT)}")
    print(f"hits: {len(audit_rows) - 1}")
    for (severity, expected), count in sorted(counts.items()):
        print(f"{severity}/{expected}: {count}")
    for speaker_id, count in sorted(by_speaker.items(), key=lambda item: (-item[1], item[0]))[:20]:
        print(f"{speaker_id}\t{names.get(speaker_id, '')}\t{count}")


if __name__ == "__main__":
    main()

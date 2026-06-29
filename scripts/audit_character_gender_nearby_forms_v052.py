from __future__ import annotations

import csv
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CSV_ROOT = ROOT / "csv" / "patch_text01"
OUT_PATH = ROOT / "exports" / "character_gender_nearby_forms_v052.csv"


FEMALE_CHARS = {
    "char_INORI",
    "char_HIROKO",
    "char_HIROKO_8YEARSLATER",
    "char_HIROKO_FIRST",
    "char_TOUDO",
    "char_TOUDO_B",
    "char_TOUDO_8YEARSLATER",
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


MALE_CHARS = {
    "char_TAKEMIYA",
    "char_TAKEMIYA_8YEARSLATER",
    "char_SIMMONS",
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


MALE_SELF_WORDS = {
    "был",
    "хотел",
    "смог",
    "уверен",
    "готов",
    "рад",
    "прав",
    "виноват",
    "должен",
    "согласен",
    "полезным",
    "невредимым",
    "замаскирован",
    "обманут",
    "пытался",
    "растерялся",
    "нервничал",
    "наблюдал",
    "слышал",
    "нашел",
    "нашёл",
    "видел",
    "понял",
    "думал",
    "сказал",
    "получил",
    "сделал",
    "стал",
}


FEMALE_SELF_WORDS = {
    "была",
    "хотела",
    "смогла",
    "уверена",
    "готова",
    "рада",
    "права",
    "виновата",
    "должна",
    "согласна",
    "полезной",
    "невредимой",
    "замаскирована",
    "обманута",
    "пыталась",
    "растерялась",
    "нервничала",
    "наблюдала",
    "слышала",
    "нашла",
    "видела",
    "поняла",
    "думала",
    "сказала",
    "получила",
    "сделала",
    "стала",
}


WORD_RE = re.compile(r"[А-Яа-яЁё]+")


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


def expected_gender(char_id: str) -> str | None:
    if char_id in FEMALE_CHARS:
        return "female"
    if char_id in MALE_CHARS:
        return "male"
    return None


def sentence_for_word(text: str, word: str) -> str:
    text = text.replace("\r\n", "\n")
    lower = text.lower()
    idx = lower.find(word)
    if idx < 0:
        return text.replace("\n", " / ")
    start = max(lower.rfind(".", 0, idx), lower.rfind("!", 0, idx), lower.rfind("?", 0, idx), lower.rfind("\n", 0, idx))
    end_candidates = [pos for pos in (lower.find(".", idx), lower.find("!", idx), lower.find("?", idx), lower.find("\n", idx)) if pos >= 0]
    end = min(end_candidates) if end_candidates else len(text)
    return text[start + 1 : end].strip().replace("\n", " / ")


def main() -> None:
    names = char_names()
    out_rows = [[
        "expected_gender",
        "speaker_id",
        "speaker_name",
        "relative_path",
        "row_id",
        "word",
        "context",
        "text",
    ]]

    for path in sorted((CSV_ROOT / "message").rglob("000_Sheet1.csv")):
        relative = path.relative_to(CSV_ROOT).as_posix()
        for row in read_rows(path)[1:]:
            if len(row) <= 2:
                continue
            row_id, speaker_id = row[0], row[1]
            expected = expected_gender(speaker_id)
            if not expected:
                continue
            text = unpack_text(row[2])
            words = {word.lower() for word in WORD_RE.findall(text)}
            wrong_words = MALE_SELF_WORDS if expected == "female" else FEMALE_SELF_WORDS
            for word in sorted(words & wrong_words):
                out_rows.append([
                    expected,
                    speaker_id,
                    names.get(speaker_id, ""),
                    relative,
                    row_id,
                    word,
                    sentence_for_word(text, word),
                    text,
                ])

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUT_PATH.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f, lineterminator="\n")
        writer.writerows(out_rows)

    print(f"wrote {OUT_PATH.relative_to(ROOT)}")
    print(f"hits: {len(out_rows) - 1}")


if __name__ == "__main__":
    main()

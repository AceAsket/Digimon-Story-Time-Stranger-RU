#!/usr/bin/env python3
"""Audit explicit first-person gender forms for fixed speakers.

This deliberately avoids the broad "any gendered word in a line" heuristic:
only a short first-person construction beginning with ``я`` is considered.
Generated runtime M/F rows and selectable protagonist speakers are excluded.
"""

from __future__ import annotations

import csv
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CSV_ROOT = ROOT / "csv"
OUT_PATH = ROOT / "exports" / "fixed_speaker_gender_audit_v076.csv"


FEMALE_SPEAKERS = {
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
    "char_FEMALE_STUDENT",
    "char_WOMAN",
    "char_YOUNG_WOMAN",
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
    "char_LILLYMON",
    "char_LILAMON",
    "char_LUNAMON",
    "char_TAILMON",
    "char_ROSEMON",
    "char_ROSEMON_BM",
    "char_SAKUYAMON",
    "char_FAIRYMON",
    "char_SHUTUMON",
    "char_OPHANIMON",
}


MALE_SPEAKERS = {
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
    "char_MAN",
    "char_YOUNG_MAN",
    "char_BOY",
    "char_MISTER",
}


MALE_FORMS = {
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
    "подслушал",
    "услышал",
    "знал",
    "думал",
    "решил",
    "ожидал",
    "нашёл",
    "нашел",
    "получил",
    "сказал",
    "увидел",
    "заметил",
    "пытался",
    "встретил",
    "вернулся",
    "пришёл",
    "пришел",
    "ушёл",
    "ушел",
    "сделал",
    "поймал",
    "родился",
    "стал",
    "остался",
    "вспомнил",
    "обнаружил",
    "создал",
    "отправился",
}


FEMALE_FORMS = {
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
    "подслушала",
    "услышала",
    "знала",
    "думала",
    "решила",
    "ожидала",
    "нашла",
    "получила",
    "сказала",
    "увидела",
    "заметила",
    "пыталась",
    "встретила",
    "вернулась",
    "пришла",
    "ушла",
    "сделала",
    "поймала",
    "родилась",
    "стала",
    "осталась",
    "вспомнила",
    "обнаружила",
    "создала",
    "отправилась",
}


FILLERS = {
    "бы",
    "не",
    "никогда",
    "уже",
    "ещё",
    "еще",
    "тоже",
    "так",
    "почти",
    "просто",
    "только",
    "совсем",
    "давно",
    "всегда",
    "снова",
    "всё",
    "все",
    "едва",
}

WORD_RE = re.compile(r"[А-Яа-яЁё]+", re.UNICODE)

# Hiroko is reading aloud first-person lines written/spoken by the male
# character Saburo/Mr. Miura.  Their masculine grammar must remain intact.
INTENTIONAL_MALE_QUOTES = {
    ("patch_text01", "message/s910_169.mbe/000_Sheet1.csv", "s910_169_320"),
    ("patch_text01", "message/s910_169.mbe/000_Sheet1.csv", "s910_169_370"),
    ("patch_text01", "message/s910_169.mbe/000_Sheet1.csv", "s910_169_400"),
}


def self_forms(text: str, forms: set[str]) -> list[tuple[str, str]]:
    words = list(WORD_RE.finditer(text))
    found: list[tuple[str, str]] = []
    for index, word_match in enumerate(words):
        if word_match.group(0).lower() != "я":
            continue
        for following in words[index + 1 : index + 6]:
            word = following.group(0).lower()
            if word in forms:
                start = max(0, word_match.start() - 25)
                end = min(len(text), following.end() + 55)
                found.append((word, text[start:end].replace("\n", " / ")))
                break
            if word not in FILLERS:
                break
    return found


def main() -> None:
    output: list[dict[str, str]] = []
    excluded_quotes = 0
    for package_root in sorted(path for path in CSV_ROOT.iterdir() if path.is_dir()):
        message_root = package_root / "message"
        if not message_root.exists():
            continue
        for path in sorted(message_root.rglob("000_Sheet1.csv")):
            relative = path.relative_to(package_root).as_posix()
            with path.open("r", encoding="utf-8-sig", newline="") as handle:
                rows = list(csv.reader(handle))
            for row in rows[1:]:
                if len(row) <= 2 or row[0].endswith(("__H", "__F")):
                    continue
                row_id, speaker, text = row[0], row[1], row[2]
                identity = (package_root.name, relative, row_id)
                if identity in INTENTIONAL_MALE_QUOTES:
                    excluded_quotes += 1
                    continue
                if speaker in FEMALE_SPEAKERS:
                    expected, wrong_forms = "female", MALE_FORMS
                elif speaker in MALE_SPEAKERS:
                    expected, wrong_forms = "male", FEMALE_FORMS
                else:
                    continue
                for form, context in self_forms(text, wrong_forms):
                    output.append(
                        {
                            "expected_gender": expected,
                            "package": package_root.name,
                            "file": relative,
                            "row_id": row_id,
                            "speaker": speaker,
                            "found": form,
                            "context": context,
                            "text": text,
                        }
                    )

    fieldnames = [
        "expected_gender",
        "package",
        "file",
        "row_id",
        "speaker",
        "found",
        "context",
        "text",
    ]
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUT_PATH.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(output)
    print(f"Fixed-speaker first-person candidates: {len(output)}")
    print(f"Intentional quoted-male exclusions: {excluded_quotes}")
    print(f"Wrote: {OUT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()

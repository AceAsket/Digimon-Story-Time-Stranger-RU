from __future__ import annotations

import csv
import re
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CSV_ROOT = ROOT / "csv" / "patch_text01"
OUT_ALL = ROOT / "exports" / "operator_lines_v055.csv"
OUT_AUDIT = ROOT / "exports" / "operator_audit_v055.csv"
GENDER_DATASET = ROOT / "exports" / "dynamic_gender_confirmed_variants_v066.csv"


OPERATOR_IDS = {"char_OPERATOR_M", "char_OPERATOR_F", "char_OPERATOR"}

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
    "подслушал",
    "услышал",
    "добавил",
    "знал",
    "думал",
    "решил",
    "ожидал",
    "нашел",
    "нашёл",
    "получил",
    "сказал",
    "увидел",
    "заметил",
    "проанализировал",
    "проследил",
    "улавливаю",
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
    "подслушала",
    "услышала",
    "добавила",
    "знала",
    "думала",
    "решила",
    "ожидала",
    "нашла",
    "получила",
    "сказала",
    "увидела",
    "заметила",
    "проанализировала",
    "проследила",
}

ENGLISH_RE = re.compile(r"[A-Za-z]{2,}")
WORD_RE = re.compile(r"[А-Яа-яЁё]+")
TAG_RE = re.compile(r"\{[^{}]*\}")


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


def reviewed_operator_rows() -> set[tuple[str, str]]:
    with GENDER_DATASET.open("r", encoding="utf-8-sig", newline="") as handle:
        return {
            (row["file"], row["base_id"])
            for row in csv.DictReader(handle)
            if row["package"] == "patch_text01" and row["role"] == "operator"
        }


def sentence_for_word(text: str, word: str) -> str:
    text = text.replace("\r\n", "\n")
    lower = text.lower()
    idx = lower.find(word)
    if idx < 0:
        return text.replace("\n", " / ")
    starts = [lower.rfind(mark, 0, idx) for mark in (".", "!", "?", "…", "\n")]
    start = max(starts)
    end_candidates = [lower.find(mark, idx) for mark in (".", "!", "?", "…", "\n")]
    end_candidates = [pos for pos in end_candidates if pos >= 0]
    end = min(end_candidates) if end_candidates else len(text)
    return text[start + 1 : end].strip().replace("\n", " / ")


def has_self_context(context: str) -> bool:
    words = [word.lower() for word in WORD_RE.findall(context)]
    return "я" in words or "мне" in words or "меня" in words or "мной" in words


def main() -> None:
    reviewed_operator = reviewed_operator_rows()
    all_rows = [[
        "speaker_id",
        "relative_path",
        "row_id",
        "tags",
        "text",
    ]]
    audit_rows = [[
        "kind",
        "speaker_id",
        "relative_path",
        "row_id",
        "word",
        "context",
        "text",
    ]]
    counts: Counter[str] = Counter()

    for path in sorted((CSV_ROOT / "message").rglob("000_Sheet1.csv")):
        relative = path.relative_to(CSV_ROOT).as_posix()
        for row in read_rows(path)[1:]:
            if len(row) <= 2:
                continue
            row_id, speaker_id = row[0], row[1]
            if speaker_id not in OPERATOR_IDS:
                continue
            tags = row[3] if len(row) > 3 else ""
            text = unpack_text(row[2])
            visible_text = TAG_RE.sub("", text)
            all_rows.append([speaker_id, relative, row_id, unpack_text(tags), text])
            counts[speaker_id] += 1

            # Generated __H/__F rows are validated as pairs by the dynamic
            # gender builder and Lua tests; auditing either side in isolation
            # would intentionally report its gendered first-person forms.
            if (
                not row_id.endswith(("__H", "__F"))
                and (relative, row_id) not in reviewed_operator
            ):
                words = {word.lower() for word in WORD_RE.findall(visible_text)}
                for kind, word_set in (("male_self_form", MALE_SELF_WORDS), ("female_self_form", FEMALE_SELF_WORDS)):
                    for word in sorted(words & word_set):
                        context = sentence_for_word(visible_text, word)
                        if has_self_context(context):
                            audit_rows.append([kind, speaker_id, relative, row_id, word, context, text])

            # Formatting controls such as {player} and {fc9...} are not
            # visible English text and must not become localization findings.
            english_hits = sorted(set(ENGLISH_RE.findall(visible_text)) - {"ADAMAS", "D", "SAT"})
            if english_hits:
                audit_rows.append([
                    "latin",
                    speaker_id,
                    relative,
                    row_id,
                    " ".join(english_hits),
                    text.replace("\r\n", " / ").replace("\n", " / "),
                    text,
                ])

            if "Дигимон " in text or "Дигимон," in text:
                audit_rows.append([
                    "digimon_case",
                    speaker_id,
                    relative,
                    row_id,
                    "Дигимон",
                    text.replace("\r\n", " / ").replace("\n", " / "),
                    text,
                ])

    OUT_ALL.parent.mkdir(parents=True, exist_ok=True)
    for path, rows in ((OUT_ALL, all_rows), (OUT_AUDIT, audit_rows)):
        with path.open("w", encoding="utf-8-sig", newline="") as f:
            writer = csv.writer(f, lineterminator="\n")
            writer.writerows(rows)

    print(f"wrote {OUT_ALL.relative_to(ROOT)}")
    print(f"wrote {OUT_AUDIT.relative_to(ROOT)}")
    print(f"operator lines: {len(all_rows) - 1}")
    for speaker_id, count in counts.items():
        print(f"{speaker_id}: {count}")
    print(f"audit hits: {len(audit_rows) - 1}")


if __name__ == "__main__":
    main()

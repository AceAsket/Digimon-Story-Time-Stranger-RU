from __future__ import annotations

import csv
import re
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CSV_ROOT = ROOT / "csv" / "patch_text01" / "message"
OUT_PATH = ROOT / "exports" / "mf_alias_gender_variants_v057.csv"


WORD_RE = re.compile(r"[А-Яа-яЁё]+")

GENDERED_MARKERS = {
    "был",
    "была",
    "готов",
    "готова",
    "рад",
    "рада",
    "прав",
    "права",
    "должен",
    "должна",
    "хотел",
    "хотела",
    "смог",
    "смогла",
    "знал",
    "знала",
    "думал",
    "думала",
    "решил",
    "решила",
    "сказал",
    "сказала",
    "видел",
    "видела",
    "увидел",
    "увидела",
    "нашёл",
    "нашла",
    "нашел",
    "получил",
    "получила",
    "испугался",
    "испугалась",
    "потрясён",
    "потрясена",
    "отправлен",
    "отправлена",
    "ранен",
    "ранена",
    "уверен",
    "уверена",
}

PLAYER_PRONOUNS = {"ты", "тебя", "тебе", "твой", "твоё", "твое", "твою", "твои", "вы", "вас", "вам", "ваш", "ваша", "ваше", "ваши"}
SELF_PRONOUNS = {"я", "мне", "меня", "мной", "мой", "моё", "мое", "мою", "мои"}


def unpack_text(text: str) -> str:
    bs = bytearray()
    for ch in text:
        try:
            bs.extend(ch.encode("cp1251"))
        except UnicodeEncodeError:
            code = ord(ch)
            if code < 256:
                bs.append(code)
            else:
                return text
    try:
        return bs.decode("utf-8")
    except UnicodeDecodeError:
        return text


def read_rows(path: Path) -> list[list[str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.reader(f))


def alias_pair(tags: str) -> tuple[str, str] | None:
    tokens = tags.split()
    m_tokens = [token for token in tokens if token.endswith("_M")]
    f_tokens = [token for token in tokens if token.endswith("_F")]
    if len(m_tokens) == 1 and len(f_tokens) == 1:
        return m_tokens[0], f_tokens[0]
    return None


def variant_type(speaker_id: str) -> str:
    if speaker_id == "char_PLAYER_M":
        return "player"
    if speaker_id == "char_OPERATOR_M":
        return "operator"
    return "other"


def words(text: str) -> set[str]:
    return {word.lower() for word in WORD_RE.findall(text)}


def suggested_speakers(speaker_id: str) -> tuple[str, str]:
    if speaker_id == "char_PLAYER_M":
        return "char_PLAYER_M", "char_PLAYER_F"
    if speaker_id == "char_OPERATOR_M":
        # The suffix appears to refer to the selected protagonist:
        # _M = male protagonist Dan, so the operator is female Kanan.
        # _F = female protagonist Kanan, so the operator is male Dan.
        return "char_OPERATOR_F", "char_OPERATOR_M"
    return speaker_id, speaker_id


def main() -> None:
    out_rows = [[
        "relative_path",
        "row_id",
        "speaker_id",
        "variant_type",
        "alias_m",
        "alias_f",
        "suggested_speaker_for_M_alias",
        "suggested_speaker_for_F_alias",
        "gender_markers",
        "has_self_pronoun",
        "has_player_pronoun",
        "text",
    ]]

    counts: Counter[str] = Counter()

    for path in sorted(CSV_ROOT.rglob("000_Sheet1.csv")):
        relative = path.relative_to(CSV_ROOT).as_posix()
        for row in read_rows(path)[1:]:
            if len(row) < 4:
                continue
            pair = alias_pair(unpack_text(row[3]))
            if pair is None:
                continue
            row_id = unpack_text(row[0])
            speaker_id = unpack_text(row[1])
            text = unpack_text(row[2])
            token_words = words(text)
            markers = sorted(token_words & GENDERED_MARKERS)
            kind = variant_type(speaker_id)
            speaker_m, speaker_f = suggested_speakers(speaker_id)
            counts[kind] += 1
            counts[f"{kind}_with_gender_markers"] += bool(markers)

            out_rows.append([
                relative,
                row_id,
                speaker_id,
                kind,
                pair[0],
                pair[1],
                speaker_m,
                speaker_f,
                " ".join(markers),
                "yes" if token_words & SELF_PRONOUNS else "",
                "yes" if token_words & PLAYER_PRONOUNS else "",
                text,
            ])

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUT_PATH.open("w", encoding="utf-8-sig", newline="") as f:
        csv.writer(f, lineterminator="\n").writerows(out_rows)

    print(f"wrote {OUT_PATH.relative_to(ROOT)}")
    for key, count in sorted(counts.items()):
        print(f"{key}: {count}")
    print(f"total: {len(out_rows) - 1}")


if __name__ == "__main__":
    main()

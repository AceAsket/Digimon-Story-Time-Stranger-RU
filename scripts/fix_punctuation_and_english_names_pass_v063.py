from __future__ import annotations

import csv
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CSV_ROOT = ROOT / "csv"
LOG_PATH = ROOT / "logs" / "fix_punctuation_and_english_names_pass_v063.log"
REVIEW_PATH = ROOT / "exports" / "english_mixed_review_v063_decisions.csv"


SPACE_BEFORE_PUNCT_RE = re.compile(r"(?<=\S)\s+(?=(?:\.\.\.|[,.;:!?]))")

TEXT_REPLACEMENTS: dict[str, str] = {
    "рядом с Синдзюку AltaVision": "у экрана AltaVision в Синдзюку",
    "Станция Акихабара: южный выход Electric Town": "Станция Акихабара: южный выход Электрик-Таун",
    "Гоуинг! Ухожу! Душа моя!! (От Digimon Savers - Digimon Savers)": "Gouing! Going! My soul!! (из Digimon Savers / Digimon Data Squad)",
    "Верующий (От Digimon Savers - Digimon Savers)": "Believer (из Digimon Savers / Digimon Data Squad)",
    "Небагиба! (Из Digimon Xros Wars - Битв Digimon Xros Wars Battles)": "Nebagiba! (из Digimon Xros Wars / Digimon Fusion Battles)",
    "МЫ - сердце Xros! (Из Digimon Xros Wars - Digimon Xros Wars Battles)": "WE ARE Xros Heart! (из Digimon Xros Wars / Digimon Fusion Battles)",
    "DIGIFARM (от Cyber Sleuth)": "DIGIFARM (из Digimon Story: Cyber Sleuth)",
    "Новинка-Футболка Game Center": "Сувенирная футболка игрового центра",
    "Героическая статуя (Central Town Bros., 1)": "Героическая статуя (братья из Центрального города, 1)",
    "Героическая статуя (Central Town Bros 2)": "Героическая статуя (братья из Центрального города, 2)",
}


REVIEW_DECISIONS: list[tuple[str, str, str]] = [
    ("Omega inForce", "keep", "официальное название способности; сверено с Wikimon"),
    ("Omni inForce", "keep/source", "официальная англ. форма в Digimon Web; в текущем RU оставляем связку Omega inForce по принятому Omegamon/Omega naming"),
    ("Alter-S / Alter-B / Zwart Defeat", "keep", "официальные суффиксы форм Омегамона"),
    ("Olympus XII", "keep", "официальное имя группы"),
    ("ZERO-ARMS", "keep", "официальное имя оружия/системы"),
    ("BAN-TYO", "keep", "официальное кодовое имя из профиля Darkdramon"),
    ("Photon Spreads / Gurei Tou / Garuru Hou", "keep", "официальные названия элементов/приёмов Omegamon: Merciful Mode"),
    ("GAKU-RAN / Golden Bats / Black Hickeys", "keep", "официальные термины профиля BanchoMamemon"),
    ("Accel Arm / Blitz Arm / Critical Arm", "keep", "официальные режимы рук Justimon"),
    ("Nightmare Assemble / Kanshaku Dust / Freeze Bomber", "keep", "официальные названия приёмов"),
    ("Taiko no Tatsujin / Tales of Arise / THE IDOLM@STER / DIGIMON BEATBREAK", "keep", "брендовые названия коллаборационных футболок"),
    ("Digimon Story: Cyber Sleuth", "keep", "официальное название игры"),
    ("Digimon Savers / Digimon Data Squad / Digimon Xros Wars / Digimon Fusion Battles", "keep", "официальные названия серий"),
    ("AltaVision", "fixed", "оформлено как название экрана AltaVision"),
    ("Electric Town", "fixed", "локализовано как Электрик-Таун"),
    ("Game Center", "fixed", "переведено как игровой центр"),
    ("Central Town Bros", "fixed", "переведено как братья из Центрального города"),
]


def decode_bytes(data: bytes) -> tuple[str, str]:
    if data.startswith(b"\xef\xbb\xbf"):
        return data.decode("utf-8-sig"), "utf-8-sig"
    return data.decode("utf-8"), "utf-8"


def process_file(path: Path) -> tuple[int, int]:
    data = path.read_bytes()
    text, encoding = decode_bytes(data)

    punctuation_hits = len(SPACE_BEFORE_PUNCT_RE.findall(text))
    updated = SPACE_BEFORE_PUNCT_RE.sub("", text)

    replacement_hits = 0
    for old, new in TEXT_REPLACEMENTS.items():
        count = updated.count(old)
        if count:
            updated = updated.replace(old, new)
            replacement_hits += count

    if updated != text:
        path.write_text(updated, encoding=encoding, newline="")

    return punctuation_hits, replacement_hits


def main() -> None:
    rows: list[list[str]] = [["decision", "term", "note"]]
    rows.extend([[decision, term, note] for term, decision, note in REVIEW_DECISIONS])
    REVIEW_PATH.parent.mkdir(parents=True, exist_ok=True)
    with REVIEW_PATH.open("w", encoding="utf-8", newline="") as f:
        csv.writer(f, lineterminator="\n").writerows(rows)

    changed: list[str] = []
    punctuation_total = 0
    replacement_total = 0
    for path in sorted(CSV_ROOT.rglob("000_Sheet1.csv")):
        punctuation_hits, replacement_hits = process_file(path)
        if punctuation_hits or replacement_hits:
            punctuation_total += punctuation_hits
            replacement_total += replacement_hits
            changed.append(
                f"{path.relative_to(ROOT).as_posix()}: punctuation={punctuation_hits}, replacements={replacement_hits}"
            )

    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    LOG_PATH.write_text(
        "\n".join(
            [
                f"punctuation_spaces_removed={punctuation_total}",
                f"name_replacements={replacement_total}",
                "changed_files:",
                *changed,
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(f"punctuation_spaces_removed={punctuation_total}")
    print(f"name_replacements={replacement_total}")
    print(f"changed_files={len(changed)}")


if __name__ == "__main__":
    main()

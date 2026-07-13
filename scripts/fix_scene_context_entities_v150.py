#!/usr/bin/env python3
"""Fix source-confirmed entity-name substitutions and one speaker-gender error."""

from __future__ import annotations

from pathlib import Path

from fix_reported_sidequests_v120 import digest, read_document, write_document


ROOT = Path(__file__).resolve().parents[1]
CSV_ROOT = ROOT / "csv"

# package, relative CSV, row id, text column, expected SHA-256, replacement
UPDATES: list[tuple[str, str, str, int, str, str]] = [
    (
        "patch_text01", "message/d03.mbe/000_Sheet1.csv", "f_d0302_0400_0010", 2,
        "60155a76482f70674414cd406b22a8e0dfedeefcc8127eec02fa69ec49e8f243",
        "Ах, МастерБлимпмон... Старый морской волк вроде меня всё бы отдал,\n"
        "лишь бы поплавать на таком красавце!",
    ),
    (
        "patch_text01", "message/d09.mbe/000_Sheet1.csv", "f_d0903_0045_0230", 2,
        "b313ce353b7303f366662bd138d150b161f14b47fa7885f29ca2560c45e52755",
        "Я тоже должна вас поблагодарить. Вы защитили лорда Бахусмона\n"
        "и всех остальных.",
    ),
    (
        "patch_text01", "message/d09.mbe/000_Sheet1.csv", "f_d0904_0100_0020", 2,
        "7c43a44487b625e1ba7c8500faaa06e8409cd96d54a7a1727501fb001da01fa5",
        "О, я защищу Маринангемона от любой опасности!",
    ),
    (
        "patch_text01", "message/d09.mbe/000_Sheet1.csv", "f_d0907_0020_0010", 2,
        "7825afe137f162f9b0618e154151943cc0a3cc1bc2620962ffb75abc39cf192a",
        "Разве не удивительно, что озорные Братья Бермоны оказались\n"
        "здесь в миг, когда решалась судьба мира?",
    ),
    (
        "patch_text01", "message/d12.mbe/000_Sheet1.csv", "f_d1204_0700_0010", 2,
        "602fb3e97dbe4c55909137b49151831f80b14ead73046f99b97961815bb5a7a3",
        "Так, где же Маленький Медвежонок?..",
    ),
    (
        "patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "aruda_001_1_replay", 2,
        "59b7050ca050e4e395438b67c116a6731a8d06c3e28d152d06a72692a3f208ec",
        "Вритрамон.",
    ),
    (
        "patch_text01", "message/s050_043.mbe/000_Sheet1.csv", "s050_043_240", 2,
        "a891ed510eb55aa15bcfe867c6ece689db70d6bb43209bc69e04f7ae87e77827",
        "Иди и одолей ПлатинаНумемона! Покажи, что сумеешь\n"
        "воспользоваться этой возможностью!",
    ),
    (
        "patch_text01", "message/s095_077.mbe/000_Sheet1.csv", "s095_077_060", 2,
        "8e2f7ae8cb90b9e2fcad04e0dfe7bd6e3ef8dec43d7831839596789dbb115007",
        "Мы потеряли связь с Лоадер Лиомоном, который возит\n"
        "сырьё из шахт.",
    ),
    (
        "patch_text01", "message/s095_077.mbe/000_Sheet1.csv", "s095_077_240", 2,
        "bd74ddf416fc31e9ad0cf1cdcc55e17f4989ee368ed7d3f72901f769bf643ad9",
        "Я всё ещё не могу связаться с Лоадер Лиомоном в шахтах.\n"
        "Доставка хрондигизойтовой руды задерживается.",
    ),
]


def main() -> None:
    documents: dict[tuple[str, str], list[list[str]]] = {}
    formats: dict[tuple[str, str], tuple[str, bool]] = {}
    dirty: set[tuple[str, str]] = set()
    changed = current = 0
    for package, relative, row_id, column, expected_hash, replacement in UPDATES:
        marker = (package, relative)
        path = CSV_ROOT / package / relative
        if marker not in documents:
            rows, encoding, quote_all = read_document(path)
            documents[marker] = rows
            formats[marker] = (encoding, quote_all)
        matches = [row for row in documents[marker] if row and row[0] == row_id]
        if len(matches) != 1 or len(matches[0]) <= column:
            raise SystemExit(f"Missing or ambiguous row {package}:{relative}:{row_id}")
        row = matches[0]
        if row[column] == replacement:
            current += 1
        elif digest(row[column]) == expected_hash:
            row[column] = replacement
            changed += 1
            dirty.add(marker)
        else:
            raise SystemExit(f"Unexpected text {package}:{relative}:{row_id}: {row[column]!r}")
    for marker in sorted(dirty):
        package, relative = marker
        encoding, quote_all = formats[marker]
        write_document(CSV_ROOT / package / relative, documents[marker], encoding, quote_all)
    print(f"Targets: {len(UPDATES)}")
    print(f"Changed: {changed}")
    print(f"Already current: {current}")
    print(f"Files written: {len(dirty)}")


if __name__ == "__main__":
    main()

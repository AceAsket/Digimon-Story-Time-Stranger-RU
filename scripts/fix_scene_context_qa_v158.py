#!/usr/bin/env python3
"""Apply final source-context QA fixes after the v157 scene pass."""

from __future__ import annotations

from pathlib import Path

from fix_reported_sidequests_v120 import digest, read_document, write_document


ROOT = Path(__file__).resolve().parents[1]
CSV_ROOT = ROOT / "csv"

UPDATES: list[tuple[str, str, str, int, str, str]] = [
    (
        "addcont_03_text01",
        "message/d330.mbe/000_Sheet1.csv",
        "d330_030_040",
        2,
        "e182a64d290526da016e78152ba8cb8dc942fafd47303ffb820bdba6937fa846",
        "«Возвращайся ко мне в помощники.\nВот и всё, что я хотела тебе сказать».",
    ),
    (
        "patch_text01",
        "message/d03.mbe/000_Sheet1.csv",
        "f_d0305_0060_0010",
        2,
        "eb9ab771a622d05e6e9e01196e7d5959e11b36a330e9394b0635287ef454d19f",
        "Похоже, ты очнулся. Некоторое время твоё состояние\n"
        "оставалось довольно тяжёлым.",
    ),
    (
        "patch_text01",
        "message/d05.mbe/000_Sheet1.csv",
        "f_d0502_0130_0040",
        2,
        "f6448244ef429224e405b9656bb5a9221142eb168874091f62b0dc3d5f508201",
        "Прости за хлопоты... Искренне благодарю тебя.",
    ),
    (
        "patch_text01",
        "message/s010_180.mbe/000_Sheet1.csv",
        "s010_180_340",
        2,
        "aea8e85b019449e3d432bf683ca2fe45692ea923a8e055d0c1147229122f91b4",
        "Спасибо, что спасла меня, БлэкГатомон. Теперь позволь спросить:\n"
        "ты станешь моей подругой—",
    ),
    (
        "patch_text01",
        "message/s020_019.mbe/000_Sheet1.csv",
        "s020_019_500",
        2,
        "68ce7966c849b8ae6fbe82d5a4568f2addf48bc8117d6bdfa27398efcb211612",
        "Превосходно. Всё прошло именно так, как я надеялся.\n"
        "ДжамбоГамемон, ты не ранен?",
    ),
    (
        "patch_text01",
        "message/s020_019.mbe/000_Sheet1.csv",
        "s020_019_510",
        2,
        "2ecd64ccabbfadfc8a4552acce07550d42bbd6c0fecd188bd2e813185d9eab36",
        "ДжамбоГамемон... в порядке.",
    ),
    (
        "patch_text01",
        "message/s020_019.mbe/000_Sheet1.csv",
        "s020_019_640",
        2,
        "7bd0b662cc732b3d280d0e08b29db20ae7d88061bd951639615624b87c4943fd",
        "Благодаря вам удалось спасти ДжамбоГамемона и найти\n"
        "жилу хрондигизойта.",
    ),
    (
        "patch_text01",
        "message/s110_108.mbe/000_Sheet1.csv",
        "s110_108_840",
        2,
        "2877d5ccab6a996bf80b4f3e66d601de287387fc9c09e15bb818bb96cc6b90cd",
        "Уверена, вернувшись к прежнему размеру, ты сможешь проявить\n"
        "всю свою силу. Желаю тебе успеха.",
    ),
    (
        "patch_text01",
        "message/s910_170.mbe/000_Sheet1.csv",
        "s910_170_1490",
        2,
        "73ef7b1905e951cd461bce5a393690485c0aae78ac17abd84b511aa8cde0074f",
        "Я только что отправила вас обратно... Постойте. На этот раз\n"
        "вы прибыли из несколько иного времени, верно?",
    ),
    (
        "patch_text01",
        "message/d03.mbe/000_Sheet1.csv",
        "f_d0302_0400_0010",
        2,
        "f5707b4fa89f140a963123bc1a29b4b574170178ae649d7913be66617031aa69",
        "Ах, МастерБлимпмон... Я, старый морской волк, всё бы отдал,\n"
        "лишь бы поплавать на таком красавце!",
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
            raise SystemExit(
                f"Unexpected text {package}:{relative}:{row_id}: {row[column]!r}"
            )

    for marker in sorted(dirty):
        package, relative = marker
        encoding, quote_all = formats[marker]
        write_document(
            CSV_ROOT / package / relative,
            documents[marker],
            encoding,
            quote_all,
        )

    print(f"Targets: {len(UPDATES)}")
    print(f"Changed: {changed}")
    print(f"Already current: {current}")
    print(f"Files written: {len(dirty)}")


if __name__ == "__main__":
    main()

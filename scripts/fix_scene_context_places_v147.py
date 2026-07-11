#!/usr/bin/env python3
"""Fix scene-context omissions, wrong locations and the lost Digi Beetle gag."""

from __future__ import annotations

from pathlib import Path

from fix_reported_sidequests_v120 import digest, read_document, write_document


ROOT = Path(__file__).resolve().parents[1]
CSV_ROOT = ROOT / "csv"

# package, relative CSV, row id, text column, expected SHA-256, replacement
UPDATES: list[tuple[str, str, str, int, str, str]] = [
    (
        "patch_text01", "message/d02.mbe/000_Sheet1.csv", "f_d0201_0040_0010", 2,
        "b5c3983692c1e0430dfb0d8c94289537bb8d34b872f97cf506dce444100aa730",
        "О! Незнакомое лицо. Да и выглядите вы необычно...\nВы здесь недавно?",
    ),
    (
        "patch_text01", "message/d02.mbe/000_Sheet1.csv", "f_d0201_0040_0030", 2,
        "77f5c65df2360548921136d51c7839c7c8120ccfb1011904a01659c19c55ba7d",
        "Идите прямо — выйдете к привокзальной площади.\n"
        "Каждому гостю Центрального города стоит увидеть башню.",
    ),
    (
        "patch_text01", "message/m390.mbe/000_Sheet1.csv", "m390_067_010", 2,
        "f94f93951acd67d77d51b8a2392177cdb5500d16314a578eb21e4a2ed9ecbbb7",
        "Вся эта смута и конфликты... Возможно, всё это было нужно,\n"
        "чтобы я стал сильнее.",
    ),
    (
        "patch_text01", "text/quest_outline.mbe/000_Sheet1.csv", "39", 1,
        "b797d2f7c38e41552e8c3023dacfe791f8a1c9e29ad86835e0b38a24a6276bc6",
        "Мой драгоценный молот в беде... Без него мне не жить!\n"
        "Приходи в магазин в Центральном городе. Очень тебя прошу!",
    ),
    (
        "patch_text01", "text/quest_outline.mbe/000_Sheet1.csv", "41", 1,
        "ff804c4bc0b28768ee36f6576b8881ee2a4c88b9b4781c08fcc79fc9f7d97d9e",
        "Мой напарник, следящий за Центральной башней, не вернулся.\n"
        "Мы должны были встретиться в центре города. Он опять отлынивает?",
    ),
    (
        "patch_text01", "text/quest_outline.mbe/000_Sheet1.csv", "55", 1,
        "270b0d83db11cd9997576700bc8ec75f113825cb3f692e4ab5c73f4bd3a597c7",
        "Хм... Может ли любовь и правда изменить человека?.. Хочешь\n"
        "поговорить? Я буду ждать в Деревне восстания.",
    ),
    (
        "patch_text01", "text/quest_outline.mbe/000_Sheet1.csv", "59", 1,
        "c637177ffa339b09caa68bcbe3568d5c9bb4fa6d97e4aefb62766b5d8b6841e2",
        "Я хочу отправиться в путешествие с Блимпмоном. Нельзя же\n"
        "вечно оставаться в Центральном городе!",
    ),
    (
        "patch_text01", "text/quest_outline.mbe/000_Sheet1.csv", "60", 1,
        "70666b353cddf77d6467d9a10eb20945e944f1018a19c8d5027cf8927e221386",
        "Я так больше не могу... Мне нужен твой совет.\n"
        "Буду ждать в Центральном городе.",
    ),
    (
        "patch_text01", "text/quest_outline.mbe/000_Sheet1.csv", "91", 1,
        "b1f72c46cd57cd79e8ca0c1a015a923288fd14327c07734b89a95102cf1c9679",
        "Мы убегали от чего-то страшного, но мой друг не успел!\n"
        "Он остался в Центральном городе. Пожалуйста, помоги!",
    ),
    (
        "patch_text01", "text/quest_outline.mbe/000_Sheet1.csv", "148", 1,
        "07da8c6f3f6868de9d2e5b0c3e3104bddee3407042133f8ccf55d649968469a1",
        "Некоторые дигимоны очень боятся людей. Приходи на склад\n"
        "в Центральном городе — там я всё расскажу.",
    ),
    (
        "patch_text01", "text/quest_outline.mbe/000_Sheet1.csv", "152", 1,
        "a4f4e3aec337dee6ee9113afce1a19e9f00d8c1b1c94a2016ba60c8a750ce4aa",
        "Мне нужна твоя помощь. Буду ждать тебя\n"
        "в центре Центрального города.",
    ),
]

DIGI_BEETLE_IDS = [
    "f_d0701_0070_0060", "f_d0701_0080_0060", "f_d0701_0090_0060",
    "f_d0701_0100_0060", "f_d0701_0110_0060", "f_d0701_0120_0060",
    "f_d0703_0140_0060", "f_d0703_0150_0060", "f_d0703_0160_0060",
    "f_d0703_0170_0060", "f_d0703_0180_0060", "f_d0703_0190_0060",
    "f_d0703_0200_0060", "f_d0703_0210_0060", "f_d0703_0220_0060",
    "f_d0703_0230_0060", "f_d0703_0240_0060", "f_d0703_0250_0060",
]
UPDATES.extend(
    (
        "patch_text01",
        "message/d07.mbe/000_Sheet1.csv",
        row_id,
        2,
        "0c8bb308fb8f3d869ee3d935644e8b8b16b768ec74fdc0c694331adf988a7149",
        "Чёрт! Я не здесь припарковал свой Диги-жук!",
    )
    for row_id in DIGI_BEETLE_IDS
)


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

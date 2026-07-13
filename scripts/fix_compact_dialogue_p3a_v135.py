#!/usr/bin/env python3
"""Apply the manually reviewed first block of compact-dialogue P3 fixes."""

from __future__ import annotations

from pathlib import Path

from fix_reported_sidequests_v120 import digest, read_document, write_document


ROOT = Path(__file__).resolve().parents[1]
CSV_ROOT = ROOT / "csv"

UPDATES: list[tuple[str, str, str, int, str, str]] = [
    ("addcont_02_text01", "message/d230.mbe/000_Sheet1.csv", "d230_020_150", 2,
     "4d96e1ef9b21d2d6b5785b25cb07960b6c54844872e8e8610486e33048cad945",
     "Но я чувствовал: этот человек ни на миг не сдавался.\n"
     "Его голос продолжал звучать."),
    ("patch_text01", "message/d03.mbe/000_Sheet1.csv", "f_d0302_0240_0040", 2,
     "da43e9286f3a4247104bbc2495850f3dc97113f9fdaf32cb30e2e55131202eac",
     "Говоришь, Область Бездны будет уничтожена?\n"
     "А в вине яд...?!"),
    ("patch_text01", "message/s110_111.mbe/000_Sheet1.csv", "s110_111_160", 2,
     "3ee96bd086e299cdb90a42a378c23a2e6d0c02f526b0c9a6227da1525d39a180",
     "Давно пора!.. Значит, Джесмона нашли благодаря тебе?"),
    ("patch_text01", "message/d02.mbe/000_Sheet1.csv", "f_d0216_0010_0010", 2,
     "306ae78b4cbc32c9968805b44d205afdd8771b97b2abf264bda9b6ef91662011",
     "Сейчас я не могу пропустить тебя в Центральный город.\n"
     "Подожди, пока Меркуримон не выскажется."),
    ("patch_text01", "message/field_text.mbe/000_Sheet1.csv", "g_degi_h0813_0010", 2,
     "6d231597ef4ce793b13b4cc496f037fe6670ccc217519b0a126e3ff1fb90c750",
     "Моё мастерство оттачивалось тысячелетиями...\n"
     "Теперь я понимаю: всё ради этого поединка."),
    ("patch_text01", "message/m410.mbe/000_Sheet1.csv", "m400_050_070", 2,
     "6d65b234495589017081944cbdd81db230c537d2f655c5843108271d5f92e954",
     "Но не зазнавайтесь! Я пока не собираюсь\n"
     "отставать от вас двоих!"),
    ("patch_text01", "message/s080_059.mbe/000_Sheet1.csv", "s080_059_630", 2,
     "35c1e294ddb02e492f9845ed3dd27e42d29e555a5c076921eabe0c90370be9e3",
     "Это лишь слухи. Сходи туда и расспроси местных,\n"
     "где именно искать."),
    ("patch_text01", "message/d04.mbe/000_Sheet1.csv", "f_d0401_0080_0030", 2,
     "5004b2188aa0d996082c690a7a63deb1bebd51d1df4805fa5db537280a3a4db1",
     "Я не против, если ты пойдёшь с нами. Но учти:\n"
     "мы сильны. Сможешь ли ты за нами угнаться?.."),
    ("patch_text01", "message/d09.mbe/000_Sheet1.csv", "f_d0904_0220_0090", 2,
     "93626955b07f7d5e7a55d9da88d8a1ab82796867ca12af3200788b7ee910504d",
     "Медицинская бригада готова! Прибудем на место —\n"
     "сразу займёмся ранеными!"),
    ("patch_text01", "message/m100.mbe/000_Sheet1.csv", "m100_060_060", 2,
     "2f2c1aa9f8828c3605ee1132271407514435ef331891c2bfd110c1e5e3fc53f4",
     "Люди нам не соперники! Не нравится —\n"
     "попробуйте что-нибудь сделать!"),
    ("patch_text01", "message/m350.mbe/000_Sheet1.csv", "m350_130_040", 2,
     "b873d843acd05c283c73bb31fd95feded92b79d9eea7a49497008dcfda860d37",
     "Наконец вернувшись домой, народ Меркуримона\n"
     "не покладая рук восстанавливал разрушенный город..."),
    ("addcont_03_text01", "message/d310.mbe/000_Sheet1.csv", "d310_040_110", 2,
     "55b1ad9adb77f08dcdcf95ea561ffe161c5dc6079b4c25f87086f8b897de1af7",
     "Значит, вы оказались в том же положении, что и мы.\n"
     "Мы внезапно очнулись в этом странном белом пространстве..."),
    ("patch_text01", "message/d09.mbe/000_Sheet1.csv", "f_d0904_0470_0010", 2,
     "e2f69126ef8523822ab4c70e062ebc491f125b3dd3b10f44bb15f5e6b8259135",
     "Медицинская бригада лечит раненых и не может сражаться.\n"
     "Так что с врагом придётся разобраться тебе, ясно?"),
    ("patch_text01", "message/m150.mbe/000_Sheet1.csv", "m150_160_140", 2,
     "2d8a89f599a01e7a41d9c6e3d6f119ac89c43ba88b71921f80587030278925f5",
     "Если так, лишь остановив конфликт в Цифровом мире,\n"
     "мы сможем предотвратить новые трагедии."),
    ("patch_text01", "message/m410.mbe/000_Sheet1.csv", "m410_105_040", 2,
     "0058a50e87651197d4f4b6c723171b0cf69753db50b0dc9c63ee52eb916d3fc1",
     "Чем больше в мире хаоса, тем вероятнее, что ты услышишь её.\n"
     "Иронично: хаос порождает и чудеса, не правда ли?"),
    ("addcont_02_text01", "message/d210.mbe/000_Sheet1.csv", "d210_030_020", 2,
     "72ca0705bcc4ba7833fcba3d43e8f05fedbe9182219ce3e79e354224ec9b6c73",
     "Похоже, он создал сеть Акашических бэкдоров\n"
     "и с её помощью перемещается в пространстве-времени."),
    ("addcont_03_text01", "message/d350.mbe/000_Sheet1.csv", "d350_001_030", 2,
     "e542f9bb5081e1266f8fa43ddc726aa09e9e3d2252edd44ef95690d4bf37700a",
     "Всем идти нельзя: будет слишком трудно координироваться.\n"
     "Выберите двух бойцов для участия в битве."),
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

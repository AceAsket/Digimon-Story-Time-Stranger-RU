#!/usr/bin/env python3
"""Apply source-confirmed fixes found by the example-driven v122 audit."""

from __future__ import annotations

from pathlib import Path

from fix_reported_sidequests_v120 import digest, read_document, write_document


ROOT = Path(__file__).resolve().parents[1]
CSV_ROOT = ROOT / "csv"

# package, relative CSV, row id, text column, expected SHA-256, replacement
UPDATES: list[tuple[str, str, str, int, str, str]] = [
    ("patch_text01", "message/d05.mbe/000_Sheet1.csv", "f_d0505_0080_0020", 2,
     "76fed0487cff271190dea8cd158add63a2bc7b5d6a10f62ded70d0320f76cf59",
     "Теперь можно воспользоваться лифтом снаружи.\nОн доставит вас обратно в деревню."),
    ("patch_text01", "message/d09.mbe/000_Sheet1.csv", "f_d0905_0010_0160", 2,
     "e48ed7b4de922c1bb567ebb24b2c2d1a93a9e1a1fac22fdd653a6e92c53465e8",
     "По недостроенному мосту можно добраться до Цумемона."),
    ("patch_text01", "message/d11.mbe/000_Sheet1.csv", "f_d1102_0100_0020", 2,
     "631bd24035b70dbaafacee4a62e2526ee5eded15ad981916c2561d95fded34e2",
     "Небольшого ремонта хватит, чтобы запустить генератор."),
    ("patch_text01", "message/d13.mbe/000_Sheet1.csv", "f_d1304_0010_0010", 2,
     "f10181ab2a44e55b37a56f560eb0e02f9d466cb1e7ee48c681d53e475aa075b2",
     "Через этот проход мы сможем выбраться."),
    ("patch_text01", "message/field_text.mbe/000_Sheet1.csv", "g_theater_0010_0010", 2,
     "0de6ea74bfe10eb6317807a98e80ed0e16697cf09b60b34a4c09d4ac2432c7a2",
     "Отсюда можно попасть в Промежуточный театр."),
    ("patch_text01", "message/m040.mbe/000_Sheet1.csv", "m040_100_090", 2,
     "7e2dab669e84f4b0c993cb70abafaa294e311a8adca1dcb06dfd965cfbf89216",
     "Этим путём можно выбраться. Скорее!"),
    ("patch_text01", "message/s100_178.mbe/000_Sheet1.csv", "s100_178_220", 2,
     "bb02ed8261181a8ddbcc8cd0f01b70aa224ad59d6971d99016cdb09520bee01f",
     "После выхода из театра это должно заработать.\nСоветую проверить."),
    ("patch_text01", "message/m280.mbe/000_Sheet1.csv", "m280_120_220", 2,
     "eec3fcd21b7efb36467a7ec44ded32587d8036cde61a15ccab339535c2c6857b",
     "Те, кого ты спасёшь, со временем станут апостолами Илиад,\nа твои узы — сосудом для Священного Потока."),
    ("patch_text01", "message/d03.mbe/000_Sheet1.csv", "f_d0308_0100_0010", 2,
     "ec5b6cb9b583b91e2a960f1fa8de75f4b149bc7194b9ca7361a90b895347f58b",
     "Боюсь, сейчас я не могу уйти... Прошу прощения."),
    ("patch_text01", "message/d09.mbe/000_Sheet1.csv", "f_d0907_0010_0040", 2,
     "263fada500aec79cca0d7ebec3013e4ed7e980fea114de79280c1320889c17a4",
     "Даже во сне я постоянно ощущала, что ты рядом.\nСловами не выразить моей благодарности... Но сейчас не время."),
    ("patch_text01", "message/m285.mbe/000_Sheet1.csv", "m285_070_030", 2,
     "39df9f2903d927bb517d7db81ce953de120f3103210c256a6e545e65f100a406",
     "Если честно, боюсь, теперь надежды уже нет..."),
    ("patch_text01", "message/s050_152.mbe/000_Sheet1.csv", "s050_152_020", 2,
     "470d6e438c277e26fb6438b2cf2811bbdc664aafabb3b471d661f66092a514d9",
     "Я призываю всех не падать духом. Пока это всё,\nчто я могу..."),
    ("patch_text01", "message/s050_176.mbe/000_Sheet1.csv", "s050_176_340", 2,
     "506c8c9c81f50276ebd73fa50b137cd00a2f208414a6c206e28de25d8c861a4d",
     "Прости, но сейчас я слишком занят."),
    ("patch_text01", "message/s100_088.mbe/000_Sheet1.csv", "s100_088_090", 2,
     "27c0d20c5d0ce7b9db369577eb4c82af3c38a31e9ed86855ebc4b9112285b1c6",
     "Обычно я взял бы с собой Тентей Хатибусю,\nно сейчас они заняты."),
    ("patch_text01", "message/s110_102.mbe/000_Sheet1.csv", "s110_102_580", 2,
     "2e62b8f8e998d478e8adeb106c36252ff73c1ec7e679d56becf2ad3a585cf4d0",
     "Простите, лорд Нептунемон, что мне приходится пока\nзабрать у вас этого человека..."),
    ("patch_text01", "message/s030_183.mbe/000_Sheet1.csv", "s030_183_270", 2,
     "35097669a51f80b130c63905ec3b511c2aec10e5b7bbc940077444f6ab18955c",
     "Это ощущение... Здесь точно кто-то есть.\nКак вовремя вы пришли! Прошу, идёмте со мной!"),
    ("patch_text01", "text/digitter_message.mbe/000_Sheet1.csv", "main_290_060_010", 1,
     "ff7c7e6d94ac0aeaf8bc5dc8b58594b6bcc208188a67a2ae5e9865fd999284f8",
     "Судя по поступающим данным, в деревне что-то не так.\nБудь осторожнее."),
    ("patch_text01", "message/d02.mbe/000_Sheet1.csv", "f_d0201_0660_0030", 2,
     "356101f2bfb100f2bc333f12ebbdd123e95cbfcb23a5123ab2ec7c6324ec6ea3",
     "Им ещё спасибо мне сказать надо — я обеспечил их работой!"),
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

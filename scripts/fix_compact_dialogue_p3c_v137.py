#!/usr/bin/env python3
"""Apply the manually reviewed third block of compact-dialogue P3 fixes."""

from __future__ import annotations

from pathlib import Path

from fix_reported_sidequests_v120 import digest, read_document, write_document


ROOT = Path(__file__).resolve().parents[1]
CSV_ROOT = ROOT / "csv"

UPDATES: list[tuple[str, str, str, int, str, str]] = [
    ("patch_text01", "message/d02.mbe/000_Sheet1.csv", "f_d0204_0360_0030", 2,
     "328d1a5a21d1329d7356a75d9e88109244d5e864ed9e293dd7d0b69be0157cc6",
     "Что ты делаешь?! Только не говори, что ты на нашей стороне...?"),
    ("patch_text01", "message/m170.mbe/000_Sheet1.csv", "m170_165_050", 2,
     "b39d74ace495d72b9d802681b53cff353a3e1802bd51787bb488ea053513d573",
     "Береги себя. Знай: где-то в Илиаде\n"
     "я буду молиться за тебя.\""),
    ("patch_text01", "message/m300.mbe/000_Sheet1.csv", "m300_130_200", 2,
     "4a4cf2e2541c205f8536064eb9bbf61e5a5cee5cd4ec5edba40307b779d68c3c",
     "...мир, каким мы его знаем, перестал бы существовать.\n"
     "История погрузилась бы в непоправимый хаос...!"),
    ("patch_text01", "message/s080_059.mbe/000_Sheet1.csv", "s080_059_050", 2,
     "eb31f3ef15464b69c0b864d4a504c10877db9a2b8f530f86fdf183d9bf9522a8",
     "Ну да, конечно могу! Я ещё многого добьюсь.\n"
     "Вот увидишь!"),
    ("addcont_01_text01", "message/d150.mbe/000_Sheet1.csv", "d150_020_060", 2,
     "2da31e139d23811f6cab9050ee4b4f46a11539d539a12b0594055e1a914c92a1",
     "Если не поспешишь выбраться оттуда,\n"
     "можешь исчезнуть в дальнем уголке пространства-времени."),
    ("addcont_02_text01", "message/d220.mbe/000_Sheet1.csv", "d220_060_070", 2,
     "79df7794ccacf5191291e8ec32d3dfb26104f63877d361ace3ebe91e760a439b",
     "Эту связь выковывают, стукнувшись кулаками."),
    ("addcont_02_text01", "message/d240.mbe/000_Sheet1.csv", "d240_030_010", 2,
     "ad2c9a44d7a9f2b467c216f8293108c394b2e2bff7b980d29a5d020b4e172a5a",
     "Возможно, этот мир откликнется на твою волю.\n"
     "Давай. Попробуй загадать желание."),
    ("addcont_03_text01", "message/d310.mbe/000_Sheet1.csv", "d310_100_060", 2,
     "2eba18270f04dfac2a4d6208dbf41a5313985d12fa2d3d1bdaf87a9fed375118",
     "Честно говоря, трудно представить, что у программы,\n"
     "грозящей уничтожить наш вид, найдётся много сторонников."),
    ("patch_text01", "message/m150.mbe/000_Sheet1.csv", "m150_070_390", 2,
     "ddeb2f626012916c2a62f6c178530fca255b35cc91249947894d14599f35b404",
     "Чтобы добраться до нижнего уровня, понадобится помощь\n"
     "деревенского Кокувамона. Но сейчас он может отказать."),
    ("patch_text01", "message/s200_149.mbe/000_Sheet1.csv", "s200_149_260", 2,
     "0ade8a8ec6634fb2c5f516f0b16f60f754065cf19dfa66f808792fbb8f3faa11",
     "...Ага! Так и знала: ещё одно сообщение!\n"
     "И пришло так вовремя, будто за нами следят."),
    ("addcont_03_text01", "message/d310.mbe/000_Sheet1.csv", "d310_060_010", 2,
     "8d3af870556f77fbf046525b89dcaf99be91553f828160b78f31c864ef63f33d",
     "До встречи с вами мы немного изучили это место,\n"
     "и на основе собранных данных я выдвинула несколько теорий."),
    ("patch_text01", "message/d02.mbe/000_Sheet1.csv", "f_d0201_1090_0010", 2,
     "f59a4947132d66fe0c7f7a590cfa72883ce3d4a78ffb88fcb1a945973765b93d",
     "О, теперь я в безопасности...!\n"
     "Спасибо за помощь с этим грубияном!"),
    ("patch_text01", "message/m220.mbe/000_Sheet1.csv", "m220_030_020", 2,
     "b3a17b832be44da26572adc4c7b3d97e7a4a8ed7fc106826b33af4949ebad11e",
     "Их создало высшее существо, сотворившее этот мир.\n"
     "Детские формы нужны им лишь для взаимодействия с нами."),
    ("patch_text01", "message/m350.mbe/000_Sheet1.csv", "m350_050_050", 2,
     "e89921ddd97594db6246da15f63e2b5fddd41f753f1d0d7e054272b0911850e8",
     "Ингредиенты у меня есть — зелье приготовится быстро.\n"
     "Остаётся надеяться, что оно будет готово вовремя...!"),
    ("patch_text01", "message/m390.mbe/000_Sheet1.csv", "m390_070_010", 2,
     "27362eb9863d50ec2a6464fd76a5c06673ffa0fca0e9822ce87a572625131f15",
     "Эгиомон был демоном, созданным Хрономоном как его преемник,\n"
     "чтобы унаследовать власть над временем."),
    ("patch_text01", "message/m400.mbe/000_Sheet1.csv", "m400_011_040", 2,
     "1a14a8ef8078f448a16dcf8296b3e0d7a175f096b01c6e809da18ae63fd120ce",
     "Я слышал, леди Минервамон, прежде выступавшую посредницей,\n"
     "где-то заточили. Теперь мирить их некому."),
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

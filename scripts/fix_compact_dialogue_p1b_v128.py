#!/usr/bin/env python3
"""Apply the manually reviewed second half of compact-dialogue P1 fixes."""

from __future__ import annotations

from pathlib import Path

from fix_reported_sidequests_v120 import digest, read_document, write_document


ROOT = Path(__file__).resolve().parents[1]
CSV_ROOT = ROOT / "csv"

UPDATES: list[tuple[str, str, str, int, str, str]] = [
    ("patch_text01", "message/m350.mbe/000_Sheet1.csv", "m350_020_070", 2,
     "13f5bef328230676cf3d75d7163263515f0b043a9e9940189cb1ba1c031c430b",
     "Стоит службе общественной безопасности применить своё оружие —\nначнётся трёхсторонний бой. Вот бы знать, что это за рука..."),
    ("patch_text01", "message/d02.mbe/000_Sheet1.csv", "f_d0201_0480_0010", 2,
     "d0799f71d230f32ce91dd7554f4f3b444edd4c950c618df60c0fbf34cd7c86a5",
     "Центральная башня позволяет связываться с другими местами,\nа ещё это одна из главных достопримечательностей города."),
    ("patch_text01", "message/d09.mbe/000_Sheet1.csv", "f_d0903_0010_0170", 2,
     "d1f0ee02761ac57d968a547fc4340113b5bfd78a6f8f3ebafbf4bcd81672098e",
     "Не поспоришь. Бедняжке Сиренмон досталось из-за меня...\nТеперь, когда её нет, я особенно ясно это понимаю."),
    ("patch_text01", "message/arena01.mbe/000_Sheet1.csv", "arena01_f001_002_040", 2,
     "601b72c45970a1a743b2ab51d8b578778f0c55b111ba8ea299b6e8ac46843e91",
     "Взгляни на мой карапакс! Ну же, смотри!\nВидишь, какой он твёрдый и прочный?!"),
    ("patch_text01", "message/arena01.mbe/000_Sheet1.csv", "arena01_f001_002_041", 2,
     "453c2908c3bdb82f0722bb24bb4fb84bd632c363ad83e3f22d690aa8b80165b1",
     "Не говори «карапакс»! Лучше просто «панцирь», как у всех!\nКого ты обманешь такими заумными словечками?"),
    ("patch_text01", "message/t03.mbe/000_Sheet1.csv", "f_t0304_0020_0100", 2,
     "ac78e82d77a31b050a8d9a940f16be4f4b8ac5153d26fffbe2901580dacb7e57",
     "Ведь АДАМАС уже точно так же пытался уничтожить Дигимонов,\nспособных путешествовать во времени, словно чужеродные тела."),
    ("patch_text01", "message/t03.mbe/000_Sheet1.csv", "f_t0304_0040_0050", 2,
     "ac78e82d77a31b050a8d9a940f16be4f4b8ac5153d26fffbe2901580dacb7e57",
     "Ведь АДАМАС уже точно так же пытался уничтожить Дигимонов,\nспособных путешествовать во времени, словно чужеродные тела."),
    ("patch_text01", "message/arena01.mbe/000_Sheet1.csv", "arena01_m320_040_030", 2,
     "f14836ca28d4ae9697167476485ecf3df382fd39f90caed9a2366e1bc016baa2",
     "Этот слаженный дуэт терпеть не может улун!\nМаксимум милоты — «Близнецы-терьеры»!"),
    ("addcont_01_text01", "message/d140.mbe/000_Sheet1.csv", "d140_026_010", 2,
     "2405d18d9d5fcf0b079836c16817b83aa9f1a3dc7707cfb675912caa1cd9da81",
     "Мы тоже сделаем всё возможное... чтобы быть тебе под стать!"),
    ("patch_text01", "message/d03.mbe/000_Sheet1.csv", "f_d0305_9000_0030", 2,
     "8cf873105b0ab5c8947b7f91a86aa6c52f10e211b4155a8036cc4dc076b6a4c3",
     "Драться — здорово, но сейчас я подсел на карточные бои!\nНе хочешь сыграть — проваливай!"),
    ("patch_text01", "message/s200_149.mbe/000_Sheet1.csv", "s200_149_870", 2,
     "a15c15a8df9544fc69f415a5027bbc012ea76e260dc2daee339f08eee42d0219",
     "Думаю, много. Наверняка там есть лишь им известные сведения:\nо связях, чувствах и планах."),
    ("patch_text01", "message/d05.mbe/000_Sheet1.csv", "f_d0501_0260_0080", 2,
     "1a82374803e4d35ea985c20f4a3aa386870fcef2cef6d0e9c14bf63998d70713",
     "Вы когда-нибудь ездили по железной дороге Локомона?\nБез него не обойтись в поездках между регионами."),
    ("patch_text01", "message/s040_160.mbe/000_Sheet1.csv", "s040_160_230", 2,
     "cfa4b1c1204f0e77f809746839cedca1ef78c34bff99bed14723724fe9db14a5",
     "Ха-ха. Больно слышать... Но в этом есть смысл.\nВ настоящем бою противник жаждет крови."),
    ("addcont_02_text01", "message/d250.mbe/000_Sheet1.csv", "d250_030_120", 2,
     "d0e78899852f36cf7b2e07b38372d125c1498f523f8c72ee0800717555ec2538",
     "Не знаю, есть ли в моём мире те, к кому ты взываешь,\nно я сделаю всё, чтобы передать им твоё послание."),
    ("patch_text01", "message/d03.mbe/000_Sheet1.csv", "f_d0302_9010_0030", 2,
     "59afc30bc9547a5b1bf8196a5db21968cd24025a7155adcee1603346f437a5f7",
     "Понимаю, у тебя есть дела. Тогда я пока останусь здесь\nи за всем присмотрю."),
    ("patch_text01", "message/d09.mbe/000_Sheet1.csv", "f_d0901_0010_0050", 2,
     "0362003f890c0b31c4a08501a768e7211976eb63c8c5c49eb8c01f377e72d44d",
     "Клянусь честью Титана: я проложу путь вперёд.\nЗадача не из лёгких, так что выиграйте для меня время."),
    ("patch_text01", "message/s080_059.mbe/000_Sheet1.csv", "s080_059_710", 2,
     "bbfafa30735d61a7fd6d3788dc2ed50aa2c6a48695c90774569d6d783bca4816",
     "Блимпмон! Правда, теперь ты можешь попасть\nв Космическую область? А с виду и не скажешь..."),
    ("addcont_01_text01", "message/d110.mbe/000_Sheet1.csv", "d110_030_020", 2,
     "688e63fa6438bd56515506136933f952a4e6437c0434d66d98e019097140b9c7",
     "Похоже, он превратил Акашический бэкдор в своё гнездо\nи через него перемещается по пространству-времени."),
    ("addcont_02_text01", "message/d230.mbe/000_Sheet1.csv", "d230_020_220", 2,
     "a36addfc54cc917a6df1df8d49735656c58bd8ff1dd773570d208fd72c712a73",
     "...если кто-то хочет вернуться в прошлое,\nПараллельмон исполняет это желание, изменяя пространство-время."),
    ("patch_text01", "message/d04.mbe/000_Sheet1.csv", "f_d0403_0030_0080", 2,
     "1b07bfa81990a9d5852b9f20ca14ca2367f5666b4ae775a81593990126e65fa2",
     "А если попадём в беду, мы рассчитываем, что вы нас спасёте!"),
    ("addcont_03_text01", "message/d320.mbe/000_Sheet1.csv", "d320_030_020", 2,
     "7f1f8c9449029572909f35d45bbf6521aa4f62127d2d5132c94005445bccd027",
     "Кое в чём этот мир похож на наш."),
    ("patch_text01", "message/d12.mbe/000_Sheet1.csv", "f_d1206_0040_0230", 2,
     "5b344cdc99246ae154d575ff0f6bed4eea1b26a0d2070817e69cb5464b67ad58",
     "Вы сказали, война Дигимонов привела мир к краху, да?\nТак вот, сейчас здесь происходит то же самое."),
    ("patch_text01", "message/m090.mbe/000_Sheet1.csv", "m090_010_020", 2,
     "06fa03c84ac7455a1ee0f2b85d1e9cc29bea15ddd3bfd93f0f60858ca3c198d1",
     "Прости, я случайно услышал... Тебя задели слова\nИнори Мисоно?"),
    ("patch_text01", "message/s200_149.mbe/000_Sheet1.csv", "s200_149_820", 2,
     "c722c6c9d0f13660f045ded8d7489f13efe242911d73672916949bc898dc778f",
     "Клиент — «Камисиро Текнолоджи»? «Мы добьёмся цели\nлюбыми средствами». Хм... Это настораживает."),
    ("patch_text01", "message/s910_169.mbe/000_Sheet1.csv", "s910_169_620", 2,
     "6ddeeb94c722fc4db5bf73700acf07461bcbbce7eb4b28ca11ddc05a90134d0b",
     "Она была в парке Синдзюку, затем спустилась в канализацию\nи исчезла. Рекомендую немедленно ей помочь."),
    ("patch_text01", "message/sow_202.mbe/000_Sheet1.csv", "sow_202_070", 2,
     "ec3cfe16689f8332060d598561cbef60861f968f362c533dd4d866b3d38df501",
     "Разберись, пожалуйста, с Курамоном, которого Куга\nпослал рыскать по Токио."),
    ("patch_text01", "message/s910_171.mbe/000_Sheet1.csv", "s910_171_770", 2,
     "62433f6c905bb15bed1f85f1fd706e59b50bd3d6f226575e1ae744b42796415a",
     "Без нас тебе вряд ли удалось бы справиться..."),
    ("addcont_03_text01", "message/d320.mbe/000_Sheet1.csv", "d320_050_030", 2,
     "7be579a848224f6e191a793cae26193e9d19cc8cf0c9a27da8e5c5a1e1ed2315",
     "«Вы хотите, чтобы я тоже ушла из общественной безопасности?»"),
    ("patch_text01", "message/d09.mbe/000_Sheet1.csv", "f_d0904_0280_0100", 2,
     "dbdb040a021cb57d283cdc1839f44f5cba63e3ab42abeb14ab2f0f188c064cfb",
     "Ребята, сразитесь вместе с нами? Нужно выиграть время,\nчтобы раненые оправились и смогли спастись..."),
    ("patch_text01", "message/d09.mbe/000_Sheet1.csv", "f_d0905_0010_0090", 2,
     "36592f9a170ceaace3f803d4210951630d44598dbcfd74cb0227b80d5f3f0888",
     "Мы использовали все доступные технологии, чтобы построить\nособый мост и безопасно добраться до врат!"),
    ("patch_text01", "message/field_text.mbe/000_Sheet1.csv", "g_shop103_0010_0010", 2,
     "be7e4efed75065e0e2ec998214fef3ed5b1a79794754f1145d8317a279aff77c",
     "Мясо, мясо и ещё раз мясо! Иногда и овощи!\nУ меня найдётся еда на любой вкус!"),
    ("patch_text01", "message/m360.mbe/000_Sheet1.csv", "m360_080_011", 2,
     "0ec5fc50ba51cc14d5817527d5d848d4e746259c00a3b2749600d8127de7aa16",
     "Хрономон владел временем и безраздельно правил Илиадой."),
    ("patch_text01", "message/d09.mbe/000_Sheet1.csv", "f_d0903_0045_0070", 2,
     "87e6505a6d1c456efd9b37b2b4b36da10f736831aaca7a5f3f919af13cfdc601",
     "Неужели этих врагов призвали Хроники Акаши?"),
    ("addcont_03_text01", "message/d320.mbe/000_Sheet1.csv", "d320_040_020", 2,
     "b9741b640aee16bf69173faf5506c1791f502a02c2ec6d0f0e2780c65821581d",
     "Мы больше не будем их красть.\nПожалуйста, позвольте нам оставить свои X-антитела!"),
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

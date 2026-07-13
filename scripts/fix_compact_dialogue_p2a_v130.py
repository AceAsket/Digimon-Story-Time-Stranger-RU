#!/usr/bin/env python3
"""Apply the manually reviewed first block of compact-dialogue P2 fixes."""

from __future__ import annotations

from pathlib import Path

from fix_reported_sidequests_v120 import digest, read_document, write_document


ROOT = Path(__file__).resolve().parents[1]
CSV_ROOT = ROOT / "csv"

UPDATES: list[tuple[str, str, str, int, str, str]] = [
    ("patch_text01", "message/d09.mbe/000_Sheet1.csv", "f_d0900_0010_0050", 2,
     "694b3ed954a0da2bbaa037628530197a83c426994fbb6e95fee7f7ce5c0d606a",
     "В любом случае, увидев тебя, я ощутил странное\n"
     "чувство долга... Может, поэтому я здесь?"),
    ("patch_text01", "message/d12.mbe/000_Sheet1.csv", "f_d1205_0220_0010", 2,
     "25d44b72feb2d4a987a1219b064716908beb6bc1dd34ceb0aeba6a5dede84b3c",
     "По словам доктора Куги, Дайанамон снабжала службу\n"
     "общественной безопасности Дигимонами для опытов."),
    ("patch_text01", "message/d13.mbe/000_Sheet1.csv", "f_d1301_0260_0040", 2,
     "a07c19ec684ef6dab6bf23835fe9950b47497bfaf87238b314bcd64a6998b24e",
     "Когда я там работала, никаких модных приложений не было.\n"
     "Всё было неудобно... Штаб будто застрял в каменном веке."),
    ("patch_text01", "message/s110_108.mbe/000_Sheet1.csv", "s110_108_640", 2,
     "a106a7d6eb9dd53651ceccbfc53b3f7917497e9e1b1495cd67a1a53ac7512a13",
     "Я снова обычного размера, хотя столько сил потратил,\n"
     "чтобы стать маленьким."),
    ("patch_text01", "message/d09.mbe/000_Sheet1.csv", "f_d0903_0280_0010", 2,
     "6f96100290108292d77dd33bc1d4f26ae542eaacea1557c3609fdc8f11ea6d5b",
     "Неужели ловлей фруктов можно зарабатывать на жизнь?\n"
     "Может, и мне поискать такую работу."),
    ("patch_text01", "message/d02.mbe/000_Sheet1.csv", "f_d0201_0270_0020", 2,
     "e76fb4a58d55de9f4ab8fdc732e8a06fb8bf51cc12c9325ac82cdb7cf6eece8c",
     "Гр-р! Всю славу себе загребаете! Но скоро и я стану\n"
     "сильным, вот увидите! Так что берегитесь!"),
    ("patch_text01", "message/d07.mbe/000_Sheet1.csv", "f_d0701_0010_0380", 2,
     "55a63a4d78b9ca612ea867601a8c3d49dc8dce3fd9280475093e5de7dffc0ff9",
     "С лордом Плутомоном творится неладное, глурп.\n"
     "Я лишь подчинённый, но уже начинаю тревожиться, глурп..."),
    ("patch_text01", "message/s200_149.mbe/000_Sheet1.csv", "s200_149_1040", 2,
     "814063548b51569a3cc78cc033c5da709110993fcfd54e2861fbfc9aaeab8029",
     "Да, выглядит жутко подозрительно, но на нём аккуратно\n"
     "выведено красным: «Это безопасно»..."),
    ("addcont_01_text01", "message/d130.mbe/000_Sheet1.csv", "d130_040_040", 2,
     "e13007f3b7d9d2e2847057be7a001d9dd74e0e9ed75fffadf08c0bb54301340f",
     "Его партнёр, вероятно, тоже заперт в одном из этих\n"
     "пузырей."),
    ("addcont_02_text01", "message/d230.mbe/000_Sheet1.csv", "d230_020_370", 2,
     "c84034ddf7ff7caae3d58430728b79afcde96d96babeb3f0392f10b1199f6530",
     "Я чувствую силу духа каждого из вас!\n"
     "Но на всякий случай нам стоит разделить силы."),
    ("addcont_03_text01", "message/d310.mbe/000_Sheet1.csv", "d310_080_100", 2,
     "62efccced492f39793ac9b082e92c39a67ac67d8670bda0bffe675d65af134c8",
     "Если они считают свой путь единственно верным, им ещё\n"
     "многому предстоит научиться. Сотрудничать будет непросто."),
    ("patch_text01", "message/field_text.mbe/000_Sheet1.csv", "g_tutorial_1000_0010", 2,
     "1373d770fae156d461dc96d520be95fff2894e0494851193990acafec72c4e2d",
     "Побеждая Дигимонов одного вида, ты повышаешь\n"
     "уровень анализа и прогресс сканирования для Конвертации."),
    ("patch_text01", "message/s910_171.mbe/000_Sheet1.csv", "s910_171_500", 2,
     "52faa676c84859ed7cbb283b0557fff7fb2e1472761a64a7572f350cdcecee85",
     "Лаборатория «Гениус»... Мы ведь знаем кое-кого,\n"
     "кто знаком с этим институтом, верно?"),
    ("addcont_02_text01", "message/d230.mbe/000_Sheet1.csv", "d230_020_130", 2,
     "2e9f1548f4c9f568b40ad381e1834d7c89628b7b943fadfaaf922827d470cc88",
     "Я не мог сопротивляться: они продолжали вытягивать\n"
     "из меня энергию. Но потом... что-то изменилось."),
    ("addcont_02_text01", "message/d230.mbe/000_Sheet1.csv", "d230_020_270", 2,
     "db0ffd132f7a3aa5f70c24a5075930c00b5cfb5fa98b093f9f845587e0a1d112",
     "Раз механизм управления воплощён в кристаллах,\n"
     "логично предположить, что их ёмкость ограничена."),
    ("addcont_03_text01", "message/d320.mbe/000_Sheet1.csv", "d320_050_110", 2,
     "469e570c4436600bd8c6f6a5dd628f209f3e336349885cf484be98747fa29f01",
     "«Именно. Как я и думал, от тебя ничто не ускользнёт»."),
    ("patch_text01", "message/d02.mbe/000_Sheet1.csv", "f_d0201_0420_0020", 2,
     "13e939adfa27543c0603bd3b5e93ea661a6410dcc1cece74bd1c1485b4f8ebc5",
     "Знаешь что? Блимпмон доставит тебя туда, где нет станций\n"
     "Локомона! Но сейчас он отдыхает. Приходи позже!"),
    ("patch_text01", "message/d06.mbe/000_Sheet1.csv", "f_d0604_0130_0070", 2,
     "748712ecba91bd040a809e315107624cabc51be75873edabf9dd53c01d3b82cf",
     "Хорошо. Сначала нужно добраться до Гамма-устройства,\n"
     "которое управляет клетками. Оно наверху."),
    ("patch_text01", "message/d02.mbe/000_Sheet1.csv", "f_d0204_0300_0010", 2,
     "2b1bf9edd889eb2f7849719f96267694491fdbd491bddb3dbcb52ac09cf52fa9",
     "В ПОСЛЕДНЕЕ ВРЕМЯ НАМ ХВАТАЕТ ХЛОПОТ С БУЙНЫМИ ТИТАНАМИ.\n"
     "МНОГИЕ ИЗ НАС ТЕПЕРЬ НАЧЕКУ..."),
    ("patch_text01", "message/field_text.mbe/000_Sheet1.csv", "g_hazama_0000_0100", 2,
     "85c51358ff87bc9310340a64b7b89fb09bc1dce533fcfe4726dc02e9466d1d84",
     "Поздравляю с прохождением всех серий испытаний!\n"
     "Как разработчик, искренне благодарю тебя за игру."),
    ("patch_text01", "message/s080_059.mbe/000_Sheet1.csv", "s080_059_480", 2,
     "6ac63ef7cb39b5b003d53c7bb68762ba69764bf971d69db6603c1e7aea2f3799",
     "Это лишь слухи, но говорят, в той деревне пользуются\n"
     "кулерами."),
    ("patch_text01", "message/s910_171.mbe/000_Sheet1.csv", "s910_171_300", 2,
     "06e935898d66998ce0f9028116bacc6eba142c6864e3f4d11eaf2c196770d3f2",
     "Я родился в лаборатории «Гениус» и живу там по сей день."),
    ("addcont_02_text01", "message/d240.mbe/000_Sheet1.csv", "d240_061_050", 2,
     "ba03bcb64bd25a53b7b4e6a2ca7ee7f87906b53066aee9b1f66e3516f13bb472",
     "«Если ты сможешь проанализировать его данные,\n"
     "то, возможно…»"),
    ("patch_text01", "message/d09.mbe/000_Sheet1.csv", "f_d0901_0010_0020", 2,
     "ff9a07504100ae11895f275b36e6910b0a9166a339993ca293a90c878f93e25c",
     "Из-за моей слабости как лидера Хрономон сумел втянуть\n"
     "в конфликт многих Титанов."),
    ("patch_text01", "message/d07.mbe/000_Sheet1.csv", "f_d0703_0110_0010", 2,
     "086d6b6c0fdc8046a3b3c4378c78f872ea41e193d6e50013b3f1521e94977666",
     "Эй, знаешь что?! *икает* Говорят, трактирщик —\n"
     "тот ещё крепкий орешек!"),
    ("patch_text01", "message/d09.mbe/000_Sheet1.csv", "f_d0903_0230_0010", 2,
     "4c7b43a61d3933a35ea65d86e262d07ebc6ff1f7f1e4c7a593054cad2ad401e5",
     "*зевает* Меня клонит в сон... Если срочно не съем\n"
     "чего-нибудь бодрящего, то усну..."),
    ("patch_text01", "message/t01.mbe/000_Sheet1.csv", "f_t0103_0100_0030", 2,
     "a48d2de59d2fb15b66ac37f50fd5bf5369a986dd8c1cdbebb584cef8c0743c0a",
     "Все выглядели так напуганно, что я решил остаться.\n"
     "Теперь я здесь вроде местной достопримечательности."),
    ("patch_text01", "message/s910_171.mbe/000_Sheet1.csv", "s910_171_880", 2,
     "c18be73403e6d3d58ba7eff7eb01a15edd6719e5c57cce613a642c6e2f716894",
     "Я об этом думал, но киберзащита лаборатории «Гениус»\n"
     "на высшем уровне."),
    ("patch_text01", "message/d09.mbe/000_Sheet1.csv", "f_d0904_0600_0020", 2,
     "66334042f688ecc7fc99f7cbadbe4bb0fca49df1094e35a374d48d9ea0ec4e79",
     "Но я всё равно им горжусь... Стой. Ты что,\n"
     "подслушиваешь?! Немедленно всё забудь!"),
    ("patch_text01", "message/d12.mbe/000_Sheet1.csv", "f_d1204_0190_0040", 2,
     "0058a9c29871c22286137ad76b77b49ee5a548d3e414ac7c4bbc84a9ab2217a3",
     "Я тревожусь за них, но сейчас мы и сами едва\n"
     "держимся на плаву."),
    ("patch_text01", "message/d12.mbe/000_Sheet1.csv", "f_d1206_0040_0110", 2,
     "a249ff964b78889c9cc5c6b9446f04f4013bc49b46c2dbbd88152ee381473eeb",
     "На моей родине сериал был так популярен, что сняли ремейк\n"
     "с живыми актёрами. Кстати, открою тебе один секрет..."),
    ("patch_text01", "message/m050.mbe/000_Sheet1.csv", "m050_060_110", 2,
     "c14f4c044efc7fe29148009727dbb6417408e7c842b940915179307c361bdcef",
     "Раз тебя забросило в прошлое, вся надежда на тебя.\n"
     "Возможно, тебе удастся предотвратить нашу гибель."),
    ("patch_text01", "message/field_text.mbe/000_Sheet1.csv", "g_degi_h0812_0020", 2,
     "66e2646486efe22a8df57f4324a3339133aa480b4342e1f19ccad707ca93778f",
     "Похоже, места не хватает... Эх. Рядом с тобой я чувствую\n"
     "себя ненужной обузой..."),
    ("patch_text01", "message/d010.mbe/000_Sheet1.csv", "d010_010_060", 2,
     "2102962aacb56f4ded41a8b3e635ffd015317f8fe8adb7d49cbcee1c28d94909",
     "...поэтому я обратилась только к тебе. Если возьмёшься,\n"
     "воспользуйся здешним лифтом."),
    ("patch_text01", "message/m120.mbe/000_Sheet1.csv", "m120_040_080", 2,
     "519ffb118a6750c9db910e4be4aa0ff1fb72cd82c00c507cf4e858963de48d73",
     "Происхождение большинства аномалий неизвестно...\n"
     "Но часть из них можно объяснить иными мирами и измерениями."),
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

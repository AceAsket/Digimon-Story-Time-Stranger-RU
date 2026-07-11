#!/usr/bin/env python3
"""Apply the manually reviewed third block of compact-dialogue P2 fixes."""

from __future__ import annotations

from pathlib import Path

from fix_reported_sidequests_v120 import digest, read_document, write_document


ROOT = Path(__file__).resolve().parents[1]
CSV_ROOT = ROOT / "csv"

UPDATES: list[tuple[str, str, str, int, str, str]] = [
    ("patch_text01", "message/field_text.mbe/000_Sheet1.csv", "g_degi_h0810_0020", 2,
     "f01e81755253ae1007bd33688f55e393825461e05884ca3c33c9451afaf720a2",
     "Нет места?! Га-га?! Не смей обижать малыша —\n"
     "пеной оболью! Гу-гу!"),
    ("patch_text01", "message/d09.mbe/000_Sheet1.csv", "f_d0904_0210_0180", 2,
     "166763cae65835ce27a31058b969eb621687f0f22de0bf0194be8bc2ee4ccb6e",
     "Я согласна с этим планом. Большая группа лишь замедлит нас\n"
     "и задержит спасательную операцию."),
    ("patch_text01", "message/field_text.mbe/000_Sheet1.csv", "g_hazama_0000_0060", 2,
     "70b36b6fe245486c128ae458f293adfa8225bfce961605e82c858ae3010abadc",
     "Жаль, что ни одну игру ещё не прошли. Но как разработчик\n"
     "скажу: работа вышла отличная, правда?"),
    ("patch_text01", "message/m210.mbe/000_Sheet1.csv", "m210_010_270", 2,
     "0dd1f6da4895122081f1dadf0c59aafb3ec17609fcea6af715c547513472adc3",
     "...зато другая половина в восторге! Не терпится испытать\n"
     "эти генераторы — плоды моих исследований!"),
    ("patch_text01", "message/s200_150.mbe/000_Sheet1.csv", "s200_150_100", 2,
     "0ba4b23c3d989266fafc3a9c06128f210b9097d550c0de4163d8c02645f08712",
     "Ну, иногда всё же стоит одеваться как следует.\n"
     "Не хватало ещё простудиться!"),
    ("addcont_03_text01", "message/d310.mbe/000_Sheet1.csv", "d310_060_180", 2,
     "322ed1ab579abe5249759b1bd0eb09679cdd1ec766054e9f693b1de42da53711",
     "Да, именно так. Раскол лишь углубляется,\n"
     "и теперь каждая группа действует сама по себе."),
    ("patch_text01", "message/d05.mbe/000_Sheet1.csv", "f_d0513_0020_0030", 2,
     "0869f131de39e7f142279826ae8d85ba97474dc86fc5316dbfdfad961ce33029",
     "Ещё я участвую ради Старшего брата. Те, кто остался,\n"
     "должны продолжать традицию боёв дигимонов."),
    ("patch_text01", "message/d12.mbe/000_Sheet1.csv", "f_d1204_0260_0010", 2,
     "c85d6bc08970a8269feb1a633aea3eef6fab9298621ba63b5379d050d4a9efeb",
     "Не все жители Центрального города успели выбраться.\n"
     "Надеюсь, с оставшимися всё в порядке..."),
    ("patch_text01", "message/d13.mbe/000_Sheet1.csv", "f_d1301_0060_0020", 2,
     "e8c9f69140d67475c9fee871ef31e19db5c8ef56818501e79f92bf26c0b6fc91",
     "Вот твой новый ID, но это уже смешно.\n"
     "Сколько раз его ещё перевыпускать?"),
    ("patch_text01", "message/m400.mbe/000_Sheet1.csv", "m400_040_130", 2,
     "eeee70c956d52f462c74f2b65a56b64b8fcda044defc3423c953190f1c09d8d6",
     "Я уже не понимала, кто на нашей стороне...\n"
     "Сомневалась даже в тебе, моей второй половине..."),
    ("patch_text01", "message/arena01.mbe/000_Sheet1.csv", "arena01_f001_010_047", 2,
     "55a2dcdf446e032855a6ad1a4762717d567739a1dcef9e6d91a146cb19969b4a",
     "Нет, даже близко! С дурацким выражением лица ты сказал:\n"
     "«Когда наши могучие силы объединятся...»"),
    ("patch_text01", "message/d12.mbe/000_Sheet1.csv", "f_d1204_0470_0020", 2,
     "eccb99a3e1d366efc0366d04909442d1a04f8b47bad51f822e466954e5345bbf",
     "Но для успеха им не хватает настоящей силы.\n"
     "Пожалуй, придётся самому присоединиться к ним и помочь..."),
    ("patch_text01", "message/m210.mbe/000_Sheet1.csv", "m210_020_246", 2,
     "4db664699005bd71b18bebdd0449864922fcb54f926e63d974c0f0c8a373bb0c",
     "У твоего отца был тот же взгляд, когда он ушёл со службы.\n"
     "Я умоляла его передумать, но он был непреклонен."),
    ("addcont_01_text01", "message/d120.mbe/000_Sheet1.csv", "d120_070_020", 2,
     "0a91bf7dc167fa96d0cb8ee8600229c9944e140e6d7a1ce0906ac78a8d9a772f",
     "«Похоже, мне нужна физиотерапия. Но даже она не гарантирует,\n"
     "что я полностью восстановлю подвижность»."),
    ("patch_text01", "message/m170.mbe/000_Sheet1.csv", "m170_210_160", 2,
     "ca3cff6f8acd0c9c02bfcdc3f98fbc76af2d5ed53115d23333ea443526ac1d2f",
     "А вы, люди... Теперь мы знаем, что Титаны охотятся за Течением.\n"
     "Вратами нужно пользоваться ещё осторожнее."),
    ("patch_text01", "message/s050_176.mbe/000_Sheet1.csv", "s050_176_200", 2,
     "3b6ad1c7e4e652cc12778bd7e66169238b7e399ead383517c0c2afb23af3f953",
     "Битва за Центральный город закончилась, прежде чем мы\n"
     "оправились. Мы ничем не смогли помочь..."),
    ("patch_text01", "message/s910_169.mbe/000_Sheet1.csv", "s910_169_890", 2,
     "76883de8e7abfe95b5670eff85c56dc4b76770dc471ffb7eb63e0dc8eec4e51b",
     "Поэтому я решила сама прочесть книгу. Я была уверена,\n"
     "что ты придёшь меня искать."),
    ("patch_text01", "message/d03.mbe/000_Sheet1.csv", "f_d0301_0180_0040", 2,
     "117b0a37d2bcda8818a459eebfda6fe1f0bd318b21a81d68356d394ca663bd86",
     "Хочу поскорее эволюционировать и наконец приносить пользу,\n"
     "но такими темпами неизвестно, когда это случится."),
    ("patch_text01", "message/d04.mbe/000_Sheet1.csv", "f_d0404_0020_0010", 2,
     "1ebeb9a1d93980adf596e800eb00793679d42e615bb906d2574090fc8b5e1103",
     "Не думала, что сам Поток можно изменить...\n"
     "Нужно разобраться, пока не стало слишком поздно."),
    ("patch_text01", "message/d06.mbe/000_Sheet1.csv", "f_d0606_0050_0020", 2,
     "4bd221a765534395113f0fb96c412519f881b2264ec8082bafafc3ac01bbed28",
     "Так что попасть туда можно лишь по железной дороге Локомона.\n"
     "Она снова работает — можем отправляться."),
    ("patch_text01", "message/s910_171.mbe/000_Sheet1.csv", "s910_171_1300", 2,
     "4140930d7a44dc2fca748688d7c7feeb3bd14d487d53c4e171d6971eb162bb97",
     "Принуждать приматов к эволюции, чтобы создавать\n"
     "искусственных гениев? В этом нет ни капли красоты..."),
    ("addcont_01_text01", "message/d140.mbe/000_Sheet1.csv", "d140_040_200", 2,
     "d84193b3a6ab0f4bb3f3fef39a3921f8ce62c4fc0afb1443fdfd1a41bc811317",
     "Мы постараемся быть достойными\n"
     "твоего сострадания!"),
    ("patch_text01", "message/m040.mbe/000_Sheet1.csv", "m040_020_120", 2,
     "411587a060c84d31de5f268dbad351eff009ca0c56424dc9252e22e6f72233d7",
     "Послушайте, нам нельзя допустить новых происшествий.\n"
     "Прошу, позвольте нам присмотреть за вашей дочерью."),
    ("addcont_01_text01", "message/d110.mbe/000_Sheet1.csv", "d110_120_060", 2,
     "a89f9c03c6eaae447c5aaf371c86f8a23ced0f8117c0fcf4aebc7e7621296453",
     "Наконец-то... дигимон, с которым можно поговорить."),
    ("addcont_03_text01", "message/d330.mbe/000_Sheet1.csv", "d330_040_130", 2,
     "3b23ef61555002a2af982a68122bd8c059493d46a1c3e8b442a7f19b4eb1aa0e",
     "«Нет! D-SAT потерпели крах, потому что... потому что мне\n"
     "не хватило таланта и умения создать это оружие как следует!»"),
    ("patch_text01", "message/battle.mbe/000_Sheet1.csv", "1200020152", 2,
     "b39ece0f4e88b9cf28eb3bbc0c610514eac303fdde80026e1cacb14d7942e8b2",
     "После такого я не могу зваться их старшей сестрой...!"),
    ("patch_text01", "message/field_text.mbe/000_Sheet1.csv", "g_shop313_0010_0010", 2,
     "ebba10ade7459c03f2a777e63dfb90225fc774e4e067bc8ff0e0cb84b2f393e3",
     "Я номер 2 из 160 братьев Вейдемонов. Хочешь участвовать\n"
     "в гонке Пекмонов — придётся купить {fc9Пропуск Вейда}!"),
    ("patch_text01", "message/s020_013.mbe/000_Sheet1.csv", "s020_013_110", 2,
     "0a52718bf1a8aecfab5f17fa22ff0e19425c30161b22c60df5ddbea56839e58b",
     "Затем из оставшегося синего хромдигизоидного металла\n"
     "я попробовал сделать то, что вы называете «кольцом»."),
    ("patch_text01", "message/m060.mbe/000_Sheet1.csv", "m060_020_140", 2,
     "901ead8f342d7e200ed4fe5fca3b8033948d116bc265445a817e82d286beb230",
     "Не могу оставить без внимания ни одного\n"
     "паранормального явления.{next}"),
    ("patch_text01", "message/d09.mbe/000_Sheet1.csv", "f_d0903_0240_0010", 2,
     "4dab701f5de03c48272e353667934124968477ac7b5865acf5c449eddc494974",
     "Нам срочно нужен фиолетовый фрукт!\n"
     "Ещё немного — и лорд Бахусмон потеряет сознание!"),
    ("addcont_01_text01", "message/d150.mbe/000_Sheet1.csv", "d150_050_030", 2,
     "a99c168f2fdf98c4a71a248afd9c85d854f0f64fa0159b59ffc2867062fe4dd4",
     "Но Параллельмон способен путешествовать\n"
     "сквозь пространство-время."),
    ("patch_text01", "message/d06.mbe/000_Sheet1.csv", "f_d0607_0010_0020", 2,
     "61fbe998aa4a28729ed13d01d4489cca741674076c241e1f2e7b3a003d2affbc",
     "Пожалуйста... Только ты можешь остановить Хрономона!"),
    ("addcont_03_text01", "message/d330.mbe/000_Sheet1.csv", "d330_030_090", 2,
     "75071145ee351ad158213dc0dfa943dac7e7eb880f629076a69afae71956d242",
     "«Если бы мир стал таким лишь из-за твоей работы...\n"
     "это была бы отличная новость»."),
    ("patch_text01", "message/d04.mbe/000_Sheet1.csv", "f_d0403_0060_0040", 2,
     "041134d95fad930fca3952a6072aa6c995b3182b4ae4bee5026cf46e67b535e8",
     "Буду благодарна за дальнейшую поддержку —\n"
     "она поможет и лесу!"),
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

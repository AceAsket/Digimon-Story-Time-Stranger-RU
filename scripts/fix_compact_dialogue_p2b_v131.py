#!/usr/bin/env python3
"""Apply the manually reviewed second block of compact-dialogue P2 fixes."""

from __future__ import annotations

from pathlib import Path

from fix_reported_sidequests_v120 import digest, read_document, write_document


ROOT = Path(__file__).resolve().parents[1]
CSV_ROOT = ROOT / "csv"

UPDATES: list[tuple[str, str, str, int, str, str]] = [
    ("patch_text01", "message/m280.mbe/000_Sheet1.csv", "m280_120_210", 2,
     "5999ccf39bfa5b9f81e5ad7b78c0d490c6026f0986545d540a06f7e2f8a42f78",
     "Чтобы овладеть этой силой, собери единомышленников.\n"
     "Те, кого только что удалось спасти, — лишь начало. Смотри."),
    ("addcont_03_text01", "message/d310.mbe/000_Sheet1.csv", "d310_100_260", 2,
     "bd2a313ac9ea363bcfae7afcea2ada00e0394936c148e926ffa603f1b16a93a6",
     "Чтобы вернуться домой, нам всем придётся действовать сообща..."),
    ("patch_text01", "message/m050.mbe/000_Sheet1.csv", "m050_040_050", 2,
     "9bac871ba92af2b663eaeafd219a5fe81ece386b36248804c7ae148bf55dc4dd",
     "Исследования АДАМАСА в области путешествий во времени\n"
     "приостановили после череды инцидентов на раннем этапе..."),
    ("patch_text01", "message/m340.mbe/000_Sheet1.csv", "m340_020_190", 2,
     "6e33b8b2488058ce8c817aef25fa1a744bbfd693a3c7180ae5366dc0afdc4f1a",
     "Что ж, если мой агент на месте отказывается действовать,\n"
     "я мало что могу сделать со своей стороны."),
    ("patch_text01", "message/d02.mbe/000_Sheet1.csv", "f_d0201_850_0020", 2,
     "6aabdb8ce3d59f043100fdd3016b15f54391f502d708ba35b92d6e81f0ffe6f1",
     "Обычно он сама невинность, а в бою — просто сталь!\n"
     "*вздох* Я от него так и таю!"),
    ("patch_text01", "message/d05.mbe/000_Sheet1.csv", "f_d0501_0130_0030", 2,
     "63d922bba68b7529a0f9db25671f0eb2e8bc2792a83a99b1d678fc6c29b0e6e2",
     "Привет! Прошло немало времени, но я снова могу двигаться.\n"
     "И всё благодаря вам, ребята! Огромное спасибо!"),
    ("patch_text01", "message/s050_039.mbe/000_Sheet1.csv", "s050_039_200", 2,
     "a7625d2cdf9706756299733d80d6365a9919e35d5cdec9d112ee6fc7b39df2b7",
     "Итак, твоя цель — Факториальная область.\n"
     "Там нужно найти хрондигизойтовый металл."),
    ("patch_text01", "message/d02.mbe/000_Sheet1.csv", "f_d0204_0280_0020", 2,
     "8f315a967becedc7459a49eb71cb8bbf16b495111da62569027bcc687db350e8",
     "Выйдите с базы и идите направо — к Центральной башне.\n"
     "Там будут мои подчинённые, так что вы не заблудитесь."),
    ("patch_text01", "message/d02.mbe/000_Sheet1.csv", "f_d0204_0280_0050", 2,
     "8f315a967becedc7459a49eb71cb8bbf16b495111da62569027bcc687db350e8",
     "Выйдите с базы и идите направо — к Центральной башне.\n"
     "Там будут мои подчинённые, так что вы не заблудитесь."),
    ("patch_text01", "message/d09.mbe/000_Sheet1.csv", "f_d0905_0010_0030", 2,
     "a504ac5c914077e6bebb0e47a10ae67c1eadc3f7b86ad263d9b192c987abfac6",
     "Простите, лорд Вулканусмон, но его украли,\n"
     "потому что ВЫ за ним не уследили..."),
    ("patch_text01", "message/s200_146.mbe/000_Sheet1.csv", "s200_146_180", 2,
     "44c1693035875dda7ec4b3bf82a280fb221c2b3154fcca4fa5373871488359e6",
     "Хочу попросить тебя помочь нам исследовать здешние подземелья.\n"
     "Некоторые участки всё ещё нестабильны."),
    ("patch_text01", "message/m340.mbe/000_Sheet1.csv", "m340_030_050", 2,
     "17fe98bbbbf41aa1d65eacfb7522926401fdf748507f3473711683f1a025409e",
     "В моей временной линии пространственно-временные возмущения\n"
     "возникают постоянно. Попадёшь в одно — домой не вернёшься."),
    ("patch_text01", "message/s080_059.mbe/000_Sheet1.csv", "s080_059_880", 2,
     "61328b18cee3c2289f1871e4b13047e7e225c71a1ab003e2d74ddee15001eaa6",
     "Я достала это для Коронамона: он хотел путешествовать.\n"
     "Но теперь отдам тебе."),
    ("addcont_03_text01", "message/d310.mbe/000_Sheet1.csv", "d310_060_220", 2,
     "de588a9129a5deeb108d0143b5ef054dfc3fb4d9bdcee1a6bd1b1b2c74ba7bdc",
     "Если даже МЫ смогли вернуться в прежнюю организацию,\n"
     "то и эти дигимоны смогут сражаться сообща вопреки разногласиям."),
    ("addcont_03_text01", "message/d330.mbe/000_Sheet1.csv", "d330_030_050", 2,
     "74fc0401486be0f665d1fcc9928015098b7c9186004a96fd37b1c70d92584946",
     "«Постой!.. Т-ты и правда так легко меня отпустишь?!»"),
    ("patch_text01", "message/battle.mbe/000_Sheet1.csv", "1090010002", 2,
     "a2ed40412c637268c61f899a75e714653fb42634bcb46239314da8b1a5597e1d",
     "Раз уж вы здесь, самое время навести тут порядок.\n"
     "Давно мне не доводилось как следует подраться!"),
    ("patch_text01", "message/d010.mbe/000_Sheet1.csv", "d010_010_050", 2,
     "9bcd09e5ea99ee7af94b5c946db6eb73941c7a5f9858c19cb6daec8318075b20",
     "Нельзя допустить, чтобы другие люди вмешивались в аномальное\n"
     "пространство-время: последствия могут быть серьёзными..."),
    ("patch_text01", "message/d06.mbe/000_Sheet1.csv", "f_d0604_0300_0070", 2,
     "b65af4aee73facb8d81e4bab4cafc5fee9a2eede7dc4304f10c9e38a23c3645a",
     "Ещё я слышала, что из-за ваших выходок\n"
     "там подняли уровень безопасности до максимума."),
    ("patch_text01", "message/d09.mbe/000_Sheet1.csv", "f_d0902_0030_0200", 2,
     "27d8fe39609fe0deac72612514630b399ae205b7ad4f64f8633c69ac4e8b80c1",
     "Ты всегда меня защищал, а теперь я сам за себя постою...\n"
     "Так что не буду выполнять твои «приказы»!"),
    ("patch_text01", "message/d09.mbe/000_Sheet1.csv", "f_d0904_0310_0080", 2,
     "2e46dc28b4e3a79eca6310737c25d77c28f99b2c852367a178461e6cdba303cc",
     "Иного выбора нет: я доведу дело до конца.\n"
     "Даже если мне суждена могила в морской пучине..."),
    ("patch_text01", "message/m110.mbe/000_Sheet1.csv", "m110_010_020", 2,
     "6767ac261157d694b45eb99b8e15da4731329d721a8cea9bedd16ac3aa4a9bc3",
     "Если мир узнает о паранормальных явлениях, которые мы изучаем,\n"
     "начнётся хаос. А это нам ни к чему."),
    ("addcont_01_text01", "message/d120.mbe/000_Sheet1.csv", "d120_010_050", 2,
     "06d7469e21838398e578f377732595016efc9f97ce9c81b85eab5d0308ce9f3b",
     "Понимаю твоё беспокойство за партнёров.\n"
     "Без Инори рядом мне тоже вряд ли хватило бы сил."),
    ("addcont_02_text01", "message/d250.mbe/000_Sheet1.csv", "d250_030_190", 2,
     "32a2aca5a85446f0af0a2026c2be8bcaf8b4a655907278c7740eb53dab9cda35",
     "Честно говоря... мне было страшно, но я старалась держаться...\n"
     "Но теперь, когда я встретила здесь всех вас..."),
    ("patch_text01", "message/battle.mbe/000_Sheet1.csv", "1040020004", 2,
     "ffae74d1fca3180b268dc3002113bc0698833a4274e97283e44a6a7c8bfb73d7",
     "И это тебя не остановило, да?.. Тогда я создам оружие,\n"
     "идеально подходящее твоим способностям!"),
    ("patch_text01", "message/d05.mbe/000_Sheet1.csv", "f_d0501_0260_0100", 2,
     "c6a43200372c929e9d75b05095b05efc4a7bc431171e5e0cd35eea2599f72807",
     "Заслуги Локомона не так заметны, как заслуги Кокувамона,\n"
     "но без него эта земля не стала бы такой, как сейчас."),
    ("patch_text01", "message/m050.mbe/000_Sheet1.csv", "m050_030_270", 2,
     "3d1e99530acff8a6c4aa00e196f1ebed49c7b2b4e01689c3cf7913502ec9f3a8",
     "Но, полагаю, этого следовало ожидать.\n"
     "Судя по анализу, тебя перенесло на восемь лет в прошлое."),
    ("patch_text01", "message/s050_038.mbe/000_Sheet1.csv", "s050_038_0140", 2,
     "106abb513fb64ef272323a27afefeb3526dfad23c0f0ea333cad7cc2a299ee91",
     "Я пришлю список нужных материалов на твой Дигивайс.\n"
     "Проверь его позже."),
    ("addcont_01_text01", "message/d110.mbe/000_Sheet1.csv", "d110_050_020", 2,
     "620b974577fa0f9555123561297891b973a5609c5f4ade5d0e20a70051fc6957",
     "Я не особо разбираюсь в аниме.\n"
     "А вот об оккультизме могу говорить целыми днями."),
    ("patch_text01", "message/d02.mbe/000_Sheet1.csv", "f_d0202_0270_0060", 2,
     "ea9b6a55496e05734f9c77ba7967928e185cebcdbaf04e8f328a7eebd9c7f0f6",
     "Мало того, говорят, тебе довелось сражаться бок о бок\n"
     "с повелителем Меркуримоном! Как же я завидую!"),
    ("patch_text01", "message/s080_059.mbe/000_Sheet1.csv", "s080_059_930", 2,
     "71c3b38885550799c6db9794491293edc67b5093a90b330456f96a433c448f03",
     "Если тебе нужен кулер, сегодня твой счастливый день."),
    ("patch_text01", "message/s095_078.mbe/000_Sheet1.csv", "s095_078_140", 2,
     "9f9197e2f8fb3fc27ae76f1e1293f00567a6a0b0403fd91cd7dd6d6e84dc8cce",
     "Магазины Центрального города обновили ассортимент!\n"
     "Обязательно загляни!"),
    ("patch_text01", "message/d11.mbe/000_Sheet1.csv", "f_d1101_0130_0020", 2,
     "e1d91195d9560363819525f185a77bd42de4e47fcf3dc63c1f988a151d623d24",
     "Я знала, что доктор Симмонс контактирует с дигимонами,\n"
     "но не думала, что кто-то из них может помогать людям..."),
    ("patch_text01", "message/d14.mbe/000_Sheet1.csv", "f_d1407_0050_0010", 2,
     "3a7742f3eb5a2c839c804424dcacf4e590d13490cab7032137c9b74d14668530",
     "Нельзя предсказать, что ждёт тебя впереди. Готовься к худшему\n"
     "и не забывай о {fc9Конвертации} и {fc9эволюции}."),
    ("patch_text01", "message/field_text.mbe/000_Sheet1.csv", "g_degi_h0511_0020", 2,
     "5bbc6104fb1b8af203b94af41ccc6a13ea2a1d69ffbea13add9c1328ad823ea3",
     "А? Похоже, места не осталось. Лучше с этим разобраться!"),
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

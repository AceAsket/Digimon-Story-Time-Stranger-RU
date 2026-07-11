#!/usr/bin/env python3
"""Fix source-confirmed register shifts and nearby context errors."""

from __future__ import annotations

from pathlib import Path

from fix_reported_sidequests_v120 import digest, read_document, write_document


ROOT = Path(__file__).resolve().parents[1]
CSV_ROOT = ROOT / "csv"

UPDATES: list[tuple[str, str, str, int, str, str]] = [
    ("addcont_02_text01", "message/d220.mbe/000_Sheet1.csv", "d220_060_120", 2,
     "796fb2e00c637c0095d6f0a04602b113ea122c2d3d66280b41851c15b42b4024",
     "На площади отдыхает мой друг.\nТебе тоже стоит немного восстановить силы."),
    ("addcont_02_text01", "message/d220.mbe/000_Sheet1.csv", "d220_070_030", 2,
     "639fc54d07f343d6b5e4703f2950beae3ea60c62e22feeea149800a8945c2403",
     "День за днём я снимала как одержимая."),
    ("addcont_02_text01", "message/dlcep002_field.mbe/000_Sheet1.csv", "dlcep002_0110_0010", 2,
     "c6b0384705ce04b3a8f189e6075f4869352358e4ceded4bde9be468197bb5890",
     "Вам предстоит сразиться с Параллельмоном.\nПриготовьтесь к битве."),
    ("addcont_03_text01", "message/d330.mbe/000_Sheet1.csv", "d330_030_040", 2,
     "07a98c13028d3c95bcff428f47987d2b1b4384147c8f29de463370f6e25e2eec",
     "«Возвращайся ко мне помощником.\nЭто всё, что я могу тебе сказать»."),
    ("patch_text01", "message/d02.mbe/000_Sheet1.csv", "f_d0204_0150_0020", 2,
     "3b565958e2417cf288d845765193898ff27a59cb199061932c54e937858c1d08",
     "Тебе стоит успокоиться. Мы здесь не ради развлечения."),
    ("patch_text01", "message/d03.mbe/000_Sheet1.csv", "f_d0305_0060_0010", 2,
     "7cb51fdab8fd3ea0819bc54938c52aa17b5a7bc309eac8aecade011fb09132e1",
     "Похоже, ты очнулся. Некоторое время твоё состояние\nбыло довольно опасным."),
    ("patch_text01", "message/d05.mbe/000_Sheet1.csv", "f_d0502_0130_0010", 2,
     "3e6f409c32d75db8486cc1d271ed932cc08ec0ea75d0899eb2edbaabf62137ee",
     "Эй, ты! Помоги! Эти двое внезапно обезумели,\nи я не могу их остановить!"),
    ("patch_text01", "message/d05.mbe/000_Sheet1.csv", "f_d0502_0130_0030", 2,
     "48109a10bab371fbf2e5c237aef43e6fdabe0dd1e8d225d8b2928fd4ad967a8c",
     "Вот это сила! Спасибо!"),
    ("patch_text01", "message/d05.mbe/000_Sheet1.csv", "f_d0502_0130_0040", 2,
     "8faeba7444e35d10204b97eca8308e9a28e566603da296ba73721464ada5ebed",
     "Прости за хлопоты... И искренне спасибо тебе."),
    ("patch_text01", "message/d05.mbe/000_Sheet1.csv", "f_d0502_0130_0050", 2,
     "5e5dfda8e2ec0e8b3f849cc9229022f5ed016611748622369d345f4a08792032",
     "Вот, держи. Это тебе за труды!"),
    ("patch_text01", "message/m100.mbe/000_Sheet1.csv", "m100_060_040", 2,
     "c48c8ea45bc4d6cbca69800c54af3fbd3e68077cf6dc527cf8db26791f30fe70",
     "Не-а, ни за что! Хотите вернуть — попробуйте отнять!\nНья-ха-ха!"),
    ("patch_text01", "message/m100.mbe/000_Sheet1.csv", "m100_060_050", 2,
     "38bff7a4218c769a5bed6ea5729e5508e2edd3674ed91424775cd27542f95e89",
     "Не ваше дело! Мне нравится смотреть на лица слабаков,\nкогда я отбираю их драгоценности!"),
    ("patch_text01", "message/m100.mbe/000_Sheet1.csv", "m100_060_060", 2,
     "243715598889b0b75204089e6d3806ef75047f0371b756637791a305cb7dedcd",
     "Люди нам не соперники! Не нравится — попробуйте нас остановить!"),
    ("patch_text01", "message/m100.mbe/000_Sheet1.csv", "m100_060_070", 2,
     "185debf8ab32d096db05104eabdf380ff7fa580a9876aae48a1a2b24ae7031f8",
     "Что вы несёте?! Вы всего лишь глупые людишки!\n"
     "Не позволю таким, как вы, портить мне веселье!"),
    ("patch_text01", "message/m100.mbe/000_Sheet1.csv", "m100_060_080", 2,
     "88ce5b347184341fbc7d31c8e3384e85aa6010b9fcea4cfe423d438ff75bb8bd",
     "Мы играем с вами именно потому, что люди так слабы.\n"
     "Игрушкам следует помалкивать!"),
    ("patch_text01", "message/m300.mbe/000_Sheet1.csv", "m300_050_010", 2,
     "9349ef27aa5176cfdb08c2d4c9562a610ca14bb2492d0484f5997e1da61b3d1a",
     "Ого, кто это у нас? Похоже, вы спите чутко."),
    ("patch_text01", "message/s010_003.mbe/000_Sheet1.csv", "s010_003_160", 2,
     "74809a4c3e50f7a2980ee3be3d232b662c95358a3ba11dbdbbf09359850e8293",
     "Вам нечего меня бояться, пока вы не мешаете мне\nделать мою работу."),
    ("patch_text01", "message/s010_180.mbe/000_Sheet1.csv", "s010_180_340", 2,
     "8e75c57343a9a454f300e0c41380ec2048f2009c96f1586c50090b7722122978",
     "Спасибо, что спасла меня, БлэкГатомон. Теперь позволь спросить:\n"
     "ты станешь моим другом—"),
    ("patch_text01", "message/s020_019.mbe/000_Sheet1.csv", "s020_019_500", 2,
     "2d33d803ebbf9127d1b49875bc37b0aa0fbf66914cbd78bd0c67858b93eb266b",
     "Превосходно. Всё прошло именно так, как я надеялся.\n"
     "ДжамбоГамемемон, ты не ранен?"),
    ("patch_text01", "message/s020_019.mbe/000_Sheet1.csv", "s020_019_510", 2,
     "a491c9e22bfaf200d5f00e229f0558301b14cb5710039af476f428c0e93beceb",
     "ДжамбоГамемемон... в порядке."),
    ("patch_text01", "message/s020_019.mbe/000_Sheet1.csv", "s020_019_520", 2,
     "0087d5d0a305bcaa8c6993156db4979ea34148bd0c084e516447812bb435df8e",
     "Значит, здесь есть жила хрондигизойтовой руды!\nИ ты её нашёл? Молодец!"),
    ("patch_text01", "message/s020_019.mbe/000_Sheet1.csv", "s020_019_620", 2,
     "a902a1d9305a7d82f25c5265a7e8942f5cc9575e3fd3fc713f37ba8339c4cfe8",
     "Да. Приглашаю тебя жить в Святилище Бездны.\nБуду рад видеть тебя там."),
    ("patch_text01", "message/s020_019.mbe/000_Sheet1.csv", "s020_019_640", 2,
     "5c412c1ce808f1db1e840789e4a87b2a1d02f32772591dbb2d5b348a4bfafa1e",
     "Благодаря вам ДжамбоГамемемон спасён, а жила\nхрондигизойта найдена."),
    ("patch_text01", "message/s050_152.mbe/000_Sheet1.csv", "s050_152_200", 2,
     "c4948bc1527150b2c27514ba5b28ad74585e1d5139caa002d5692615986f9205",
     "Правда? Большое тебе спасибо! Теперь я смогу\nещё лучше отточить свои навыки!"),
    ("patch_text01", "message/s050_152.mbe/000_Sheet1.csv", "s050_152_210", 2,
     "7f8e3f64c1cf81ecf67a48170d32ed73f7f96c152a01d97fca20f298244da97e",
     "Отлично, всё получилось. Благодаря тебе я смогу\nподбадривать союзников."),
    ("patch_text01", "message/s050_152.mbe/000_Sheet1.csv", "s050_152_220", 2,
     "467ff0924bf8f25b9a5079306909b0867b7b3872a66adf7cdcafad98033ddb5c",
     "Здесь мы закончили. Пора возвращаться."),
    ("patch_text01", "message/s110_108.mbe/000_Sheet1.csv", "s110_108_840", 2,
     "ddba8f81d5fbd92570616676f92b26eaea1aa59f073d99083dfa4193371014ac",
     "Уверена, в таком размере ты сможешь проявить всю свою силу.\n"
     "Желаю тебе успеха."),
    ("patch_text01", "message/s110_108.mbe/000_Sheet1.csv", "s110_108_850", 2,
     "a9cf0be507661884614aeee34acf163a184f779b12d590633805e94ec69396c2",
     "И всё же... по-моему, твой обычный размер подходит тебе лучше."),
    ("patch_text01", "message/s200_146.mbe/000_Sheet1.csv", "s200_146_240", 2,
     "353e267aef4e8cab810d1b084c00f53e43a4b9c4eaae06d770d4b736306744b5",
     "Как ты доложишь начальству, что позволила гражданскому\nпомочь нам?"),
    ("patch_text01", "message/s200_146.mbe/000_Sheet1.csv", "s200_146_260", 2,
     "7ed9d524a75cfe606a4ffe1dc6d19ce6de1c29408b2dad640087c693edc0d27a",
     "Я понимаю твои чувства, но..."),
    ("patch_text01", "message/s910_170.mbe/000_Sheet1.csv", "s910_170_1490", 2,
     "570253d4b50f9d68d8db31291b09ff2ca82675a789f65e6207c2fde14a2bd7a8",
     "Я только что отправила вас обратно... Постойте. Это немного\n"
     "другое время, чем в прошлый раз, верно?"),
    ("patch_text01", "message/s910_171.mbe/000_Sheet1.csv", "s910_171_730", 2,
     "4f8c4e0cdc4ea3db7e93517682cdee5015e3b1209a9b2b1eafbeb0ef6baf1012",
     "Удивительно, как спокойно вы держитесь после нападения..."),
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

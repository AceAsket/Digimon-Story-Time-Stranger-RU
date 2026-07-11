#!/usr/bin/env python3
"""Apply the manually reviewed first half of compact-dialogue P1 fixes."""

from __future__ import annotations

from pathlib import Path

from fix_reported_sidequests_v120 import digest, read_document, write_document


ROOT = Path(__file__).resolve().parents[1]
CSV_ROOT = ROOT / "csv"

UPDATES: list[tuple[str, str, str, int, str, str]] = [
    ("patch_text01", "message/arena01.mbe/000_Sheet1.csv", "arena01_f001_019_040", 2,
     "7e9c1163bf85b2c21762e9c5443029306a18ad3385d2e017ce4deedb6c00e094",
     "Никогда ещё тренировки не были такими весёлыми!\nХочешь остановить меня и мастеров — сперва победи нас!"),
    ("patch_text01", "message/m170.mbe/000_Sheet1.csv", "m170_210_230", 2,
     "805833c04cb98efe369410c88feb0e60c4d6074315014bcde453c71c580a4cbb",
     "Поэтому прошу понять: я не открою ворота,\nпока здесь не восстановят порядок."),
    ("patch_text01", "message/d09.mbe/000_Sheet1.csv", "f_d0907_0020_0020", 2,
     "eb885cdfa9a43f2a99d928a78b72819cf588fdd27aec4d66453915833ee52d94",
     "Большой брат выбился из сил и теперь отдыхает.\nОн велел мне как следует навалять Хрономону."),
    ("patch_text01", "message/battle.mbe/000_Sheet1.csv", "1190120008", 2,
     "9883909a8ec36ee473e14a5afa740c4144d9f70709ed4e691f969fd25f974a69",
     "...но одного из Семи Великих Повелителей Демонов я не ожидал.\nК счастью, это подделка. Уничтожим её!"),
    ("patch_text01", "message/d12.mbe/000_Sheet1.csv", "f_d1206_0040_0200", 2,
     "29773e32a2609c75f53c522e9a7af27a01411eddf4875743c33222e4cde98cf8",
     "Я считаю, что будущее расходится на разные пути.\nИначе говоря, существует множество миров."),
    ("patch_text01", "message/d14.mbe/000_Sheet1.csv", "f_d1407_0050_0050", 2,
     "0c8f3c31bdbcaae657d439d2705b794cddf3da1af0407c4e45a7e8ce33eee1b0",
     "Ты носишь его имя, и никто лучше тебя не продолжит его дело.\nВ совершенстве овладей {fc9Конвертацией} и {fc9эволюцией}!"),
    ("patch_text01", "message/d09.mbe/000_Sheet1.csv", "f_d0907_0090_0030", 2,
     "f87a595ad21f61b120624436cfa52530114b0dd9b9ca385f4961b3dfb19236f0",
     "Обрести свободу значило разрушить порядок этого мира\nценой своей жизни. Ради этого он манипулировал Титанами."),
    ("addcont_02_text01", "message/d210.mbe/000_Sheet1.csv", "d210_040_030", 2,
     "8731ce627478c5a68517839b175efe67a774e74115aeb7515856b0f9cc53d869",
     "Я... А-А-А-А-А-А-А-А-А-А-А-А-А!"),
    ("patch_text01", "message/d02.mbe/000_Sheet1.csv", "f_d0201_0550_0010", 2,
     "4f3659bfd2452eb6b91160178484d7360bc6da22a0c4d24b9861a3d177fb8501",
     "Жить без нужды, конечно, здорово,\nно когда всё слишком просто, мне становится скучно..."),
    ("patch_text01", "message/m320.mbe/000_Sheet1.csv", "m320_080_290", 2,
     "4b544f120b1f6b0224d8c911a70e90bcf6679c3afc765e1af1f70731c1438355",
     "Нельзя исключать, что именно они вызывают коллапс.\nПосле встречи с этими двумя случилось слишком много странного."),
    ("addcont_03_text01", "message/d330.mbe/000_Sheet1.csv", "d330_010_110", 2,
     "d1a9c587426caf6e808dba2b7314e6cd401f25e66f364cffef62128d5c496cc9",
     "Путешествуя сквозь пространство-время, мы можем раскрыть\nистоки Программы X. Возможно, так найдём путь вперёд."),
    ("patch_text01", "message/d05.mbe/000_Sheet1.csv", "f_d0506_9000_0010", 2,
     "742f9daa1799d0192621f92e4e1a62dfd1a88c1d2fa1aa836a77a296cc3beec6",
     "В драке важны не только мускулы — надо и башкой думать.\nНу что, устроим карточный бой?"),
    ("patch_text01", "message/d05.mbe/000_Sheet1.csv", "f_d0506_0220_0070", 2,
     "75d27e3206df6146a5fb1e6d03abb59ca293723515f87c0e8a34056efab2f0a7",
     "Я оставлю это место открытым для тебя…\nЗаходи, если захочешь с кем-нибудь взять реванш."),
    ("patch_text01", "message/battle.mbe/000_Sheet1.csv", "1200020063", 2,
     "ed0978d3a91c2e267ac2e1f814ea1c58fe44fc1e1fc36217b96da962442bc9ab",
     "Оно должно было разжечь твою ненависть к миру и судьбе\nи дать тебе решимость уничтожить всё."),
    ("patch_text01", "message/m060.mbe/000_Sheet1.csv", "m060_030_068", 2,
     "9ec3a0b04388517c52d1ed4bfccbdceb4f9b36a57c5168b67dbe7c6cc8bbc615",
     "Шоу старое, но тебе подходит как нельзя лучше!\nЯ его фанатка и просто обязана звать тебя «Агентом», правда?"),
    ("patch_text01", "message/d09.mbe/000_Sheet1.csv", "f_d0903_0410_0030", 2,
     "f1bcb96b35ce5244329bec8fcea55d83e674b940d2c98c53a23bb25c2551cb73",
     "К счастью, мы были под землёй и не пострадали.\nНо лишь вопрос времени, когда разлом дойдёт до нас."),
    ("patch_text01", "message/d02.mbe/000_Sheet1.csv", "f_d0202_0590_0020", 2,
     "2384f329aa7e75cdcb8faf654d1de9a6e50a7134385e0dc0eabfee60148b4c04",
     "Похоже, мне ещё есть куда расти... Уф..."),
    ("addcont_02_text01", "message/d220.mbe/000_Sheet1.csv", "d220_060_040", 2,
     "ae4eaf75ac24bf20f644cb744f3f0bf4ee9ffeabba67d1762b8ac979dcef791b",
     "В твоих ударах я тоже ощутил благородство.\nТеперь сразимся плечом к плечу... Нет, погоди..."),
    ("addcont_02_text01", "message/d210.mbe/000_Sheet1.csv", "d210_010_040", 2,
     "96a606045d59cb1c93378b0262bf15f416d7b5c325275b06f2ff746521f3c3b1",
     "А я буду передавать нужные сведения через ваше устройство.\nРассчитываю на сотрудничество."),
    ("addcont_02_text01", "message/d220.mbe/000_Sheet1.csv", "d220_080_140", 2,
     "daf451fe7a72c15627593600e7970e17e20c94b7990f01d5b435153ca5b09480",
     "Говори что хочешь — свою неуверенность от меня не скроешь.\nТакие Дигимоны, как ты, только лают, но не кусают."),
    ("addcont_03_text01", "message/d310.mbe/000_Sheet1.csv", "d310_010_040", 2,
     "96a606045d59cb1c93378b0262bf15f416d7b5c325275b06f2ff746521f3c3b1",
     "А я буду передавать нужные сведения через ваше устройство.\nРассчитываю на сотрудничество."),
    ("patch_text01", "message/d02.mbe/000_Sheet1.csv", "f_d0204_0610_0010", 2,
     "1186a58a138ff95656bfab15618914a5d9ed82546290bf8aebacb5f9e945bb64",
     "Плутомон обитает в месте под названием «Тёмное поле».\nЯ пока не могу уйти, поэтому прошу вас отправиться туда."),
    ("patch_text01", "message/d03.mbe/000_Sheet1.csv", "f_d0304_0040_0050", 2,
     "2be91e3056ad0310218862520632ffa5c86795b413b6e72eb92506e0560a068e",
     "Пойду патрулировать округу, чтобы парни, перекрывшие дорогу,\nне натворили бед... Увидимся."),
    ("patch_text01", "message/d09.mbe/000_Sheet1.csv", "f_d0902_0030_0240", 2,
     "e63f4a2f19cc6a18a0036cffde562c0b26bc434a934938d1e57997e6e828723d",
     "Мы не умрём, Большой брат. В этот раз я тебя защищу.\nА вы, остальные, спешите к Хрономону!"),
    ("patch_text01", "message/d09.mbe/000_Sheet1.csv", "f_d0904_0280_0160", 2,
     "7e44adc9c537e8a429dcea127e23691f5e1a560e4239807ecff5a8f174ddb318",
     "Я бы ещё поболтал с тобой, но давай ударим по рукам —\nто есть по плавникам. Идёт?"),
    ("patch_text01", "message/m180.mbe/000_Sheet1.csv", "m180_010_130", 2,
     "2d0aff463d57310ed81e1a8b8a9df7710ed283d6a74119436eb362154538ca84",
     "Раньше её не увлекали мистика и городские легенды.\nПо крайней мере, до того, как я потеряла маму и брата."),
    ("addcont_02_text01", "message/d240.mbe/000_Sheet1.csv", "d240_020_150", 2,
     "74075b336b05881409b390dc89bc07d1b8ef245bc87940f2379111ae2d2dbdd8",
     "Ты вряд ли этого хотела, но обрела влияние на этот мир.\nОн должен откликнуться на твоё заветное желание."),
    ("addcont_03_text01", "message/d320.mbe/000_Sheet1.csv", "d320_040_070", 2,
     "f871d51bce75cc77d2299287d4b5533a449d10345cb2763eec40ab6337c54c2a",
     "Как ни печально, надо признать: данное нам испытание\nприведёт к эволюции Дигимонов как вида."),
    ("patch_text01", "message/m050.mbe/000_Sheet1.csv", "m050_055_010", 2,
     "de31570f21d36e5fe27efc78debba0af769bd030828bf77f39f7ed66cff929ec",
     "Добро пожаловать в Промежуточный театр — особое место\nмежду разными пространственно-временными измерениями."),
    ("patch_text01", "message/m240.mbe/000_Sheet1.csv", "m240_020_160", 2,
     "eac0537aa0ade8cc52fd5c1b2af28e409a499b7f349b74926a05062d6ef26772",
     "Мы должны дать отпор обеим угрозам, иначе будущего не будет.\nРади этого придётся поставить на кон само наше существование."),
    ("patch_text01", "message/s910_171.mbe/000_Sheet1.csv", "s910_171_210", 2,
     "5c513f88b885d732044dda9e23f9c06d62eb2ea7cf4b24d77d22c9ba3b9f1dff",
     "Конечно, у него всегда были лучшие оценки.\nЕщё в начальной школе он на отлично сдавал экзамены в вуз."),
    ("addcont_03_text01", "message/d320.mbe/000_Sheet1.csv", "d320_050_320", 2,
     "d4a9a66c12f7c78264dea876a1e0e0d911a44c2beb370871057a21ac986308d5",
     "Прошу прощения, но спорить мы не намерены.\nЕсли попытаетесь остановить нас силой, мы не станем сдерживаться."),
    ("patch_text01", "message/d09.mbe/000_Sheet1.csv", "f_d0904_0550_0010", 2,
     "c6c3569c3b8a07cdd48749773b35cbba30096690ce0bb8b9e2b45bd93f387ce8",
     "Правитель обязан отплатить за оказанную услугу.\nБлагодаря тебе я вступил в эту битву. Я искренне благодарен."),
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

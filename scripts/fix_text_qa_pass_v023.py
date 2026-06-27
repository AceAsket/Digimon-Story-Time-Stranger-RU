from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CSV_ROOT = ROOT / "csv"
CSV_ROOTS = [
    path for path in sorted(CSV_ROOT.iterdir()) if path.is_dir() and ((path / "message").exists() or (path / "text").exists())
]


TARGETED_ROWS: dict[tuple[str, str], str] = {
    ("message/s010_003.mbe/000_Sheet1.csv", "s010_003_041"): "{next}Ты ведь знаешь, о чём я попрошу.",
    ("message/s010_003.mbe/000_Sheet1.csv", "s010_003_042"): "{end}Прости! Тут кое-что важное вспомнилось!",
    ("message/s010_003.mbe/000_Sheet1.csv", "s010_003_090"): "{next}Да. Прости, что пришлось ждать.",
    ("message/s010_156.mbe/000_Sheet1.csv", "s010_156_071"): "{next}Может, он не может сказать это прямо?",
    ("message/s010_156.mbe/000_Sheet1.csv", "s010_156_072"): "{next}Может, это память о его путешествиях.",
    ("message/s010_156.mbe/000_Sheet1.csv", "s010_156_131"): "{next}Может, это ключ от камеры хранения?",
    ("message/s010_156.mbe/000_Sheet1.csv", "s010_156_132"): "{next}Может, это ключ от сейфа в офисе?",
    ("message/s010_156.mbe/000_Sheet1.csv", "s010_156_230"): "{next}Какая-то машинная деталь?",
    ("message/s010_156.mbe/000_Sheet1.csv", "s010_156_300"): "{next}Вспомни. У тебя получится!",
    ("message/s010_156.mbe/000_Sheet1.csv", "s010_156_360"): "{next}Значит, отец Инори украл улику?",
    ("message/s010_156.mbe/000_Sheet1.csv", "s010_156_431"): "{next}И все просто поверили версии о просадке грунта?",
    ("message/s010_156.mbe/000_Sheet1.csv", "s010_156_432"): "{next}Некоторые верят всему, что слышат.",
    ("message/s010_156.mbe/000_Sheet1.csv", "s010_156_520"): "{next}Может, это случилось из-за открытия врат?",
    ("message/s010_156.mbe/000_Sheet1.csv", "s010_156_521"): "{next}Может, причиной стало столкновение дигимонов?",
    ("message/s010_156.mbe/000_Sheet1.csv", "s010_156_522"): "{next}Может, это был удар метеорита.",
    ("message/s010_156.mbe/000_Sheet1.csv", "s010_156_814"): "{end}Дай-ка я ещё раз всё обдумаю.",
    ("message/s010_156.mbe/000_Sheet1.csv", "s010_156_910"): "{next}Победим его столько раз, сколько понадобится!",
    ("message/s010_156.mbe/000_Sheet1.csv", "s010_156_911"): "{next}Этот дигимон и обрушил здание?",
    ("message/s010_156.mbe/000_Sheet1.csv", "s010_156_912"): "{next}Нужно разобрать его прямо сейчас.",
    ("message/s010_156.mbe/000_Sheet1.csv", "s010_156_971"): "{next}Может, он хотел, чтобы мы узнали правду.",
    ("message/s010_156.mbe/000_Sheet1.csv", "s010_156_972"): "{next}Может, ему просто было лень.",
    ("message/s010_159.mbe/000_Sheet1.csv", "s010_159_022"): "{next}Оказаться на пороге тридцати.",
    ("message/s010_159.mbe/000_Sheet1.csv", "s010_159_081"): "{next}Что не так с моей одеждой?",
    ("message/s010_159.mbe/000_Sheet1.csv", "s010_159_241"): "{next}К вершине двадцатилетия лёгких путей нет.",
    ("message/s010_159.mbe/000_Sheet1.csv", "s010_159_242"): "{next}Как готовить без дорогих ингредиентов?",
    ("message/s010_159.mbe/000_Sheet1.csv", "s010_159_370"): "{next}Выглядишь очень внушительно.",
    ("message/s010_159.mbe/000_Sheet1.csv", "s010_159_372"): "{next}Проклятое оружие тоже бывает мощным.",
    ("message/s010_180.mbe/000_Sheet1.csv", "s010_180_041"): "{next}Почему их костюмы были такими удачными?",
    ("message/s010_180.mbe/000_Sheet1.csv", "s010_180_042"): "{next}Наверняка можно было хоть что-то сказать!",
    ("message/s010_180.mbe/000_Sheet1.csv", "s010_180_442"): "{next}В-вы меня с кем-то путаете...",
    ("message/s020_013.mbe/000_Sheet1.csv", "s020_013_020"): "{next}Не проблема. Скажи, чем помочь.",
    ("message/s020_013.mbe/000_Sheet1.csv", "s020_013_061"): "{next}Я уже начинаю терять терпение...",
    ("message/s020_013.mbe/000_Sheet1.csv", "s020_013_171"): "{next}Да. Так кто тебе дороже всех?",
    ("message/s020_013.mbe/000_Sheet1.csv", "s020_013_172"): "{next}И ты отдаёшь это мне?",
    ("message/s020_013.mbe/000_Sheet1.csv", "s020_013_220"): "{next}Об этом можно не переживать.",
    ("message/s020_013.mbe/000_Sheet1.csv", "s020_013_221"): "{next}Люди не дарят кольца так быстро.",
    ("message/s020_013.mbe/000_Sheet1.csv", "s020_013_271"): "{next}Точно не хочешь добавить послание?",
    ("message/s020_013.mbe/000_Sheet1.csv", "s020_013_370"): "{next}Это знак благодарности.",
    ("message/d04.mbe/000_Sheet1.csv", "f_d0403_0010_0010"): "Ну и ну! Палмон, растяпа! Ты всё-таки добралась!",
    ("message/d04.mbe/000_Sheet1.csv", "f_d0403_0010_0030"): "Но не расслабляйтесь: это как раз то самое место!",
    ("message/d04.mbe/000_Sheet1.csv", "f_d0403_0020_0070"): "Они сбежали! Вот трусы.",
    ("message/d04.mbe/000_Sheet1.csv", "f_d0403_0020_0080"): "Д-думаешь, у нас правда есть шанс...?!",
    ("message/d04.mbe/000_Sheet1.csv", "f_d0403_0030_0030"): "Простите, что я раньше в вас сомневалась.",
    ("message/d04.mbe/000_Sheet1.csv", "f_d0403_0030_0110"): "Спорю, они кому угодно что угодно выболтают.",
    ("message/d04.mbe/000_Sheet1.csv", "f_d0403_0060_0040"): "Буду очень благодарна за дальнейшую поддержку. Она поможет и лесу!",
    ("message/d04.mbe/000_Sheet1.csv", "f_d0404_0070_0010"): "Лорд Бахусмон вечно пьян. Разве так ведёт себя вождь? Тьфу.",
    ("message/d04.mbe/000_Sheet1.csv", "f_d0404_0100_0020"): "Хм? Где Бахусмон? Вон там, на другой стороне площади.\n*зевает*",
    ("message/d04.mbe/000_Sheet1.csv", "f_d0404_0120_0050"): "Я не могу полагаться на других. Мне нужно эволюционировать и стать\nсильнее...!",
    ("message/d10.mbe/000_Sheet1.csv", "f_d1001_0050_0010"): "Похоже, пока мы оторвались. Поторопимся.",
    ("message/m010.mbe/000_Sheet1.csv", "m010_040_010"): "Вижу, ты на нужных координатах. Доложи обстановку.",
    ("message/d03.mbe/000_Sheet1.csv", "f_d0303_0040_0080"): "Точно стоит отпускать Дивер-Мона? В конце концов,\nДивер-Мон - титан.",
    ("message/d05.mbe/000_Sheet1.csv", "f_d0501_0010_0020"): "{next}Откуда ты знаешь?",
    ("message/m050.mbe/000_Sheet1.csv", "m050_060_010"): "С тобой всё в порядке? Где ты сейчас? Я на какое-то время\nпотерял с тобой связь.",
    ("message/m070.mbe/000_Sheet1.csv", "m070_100_060"): "Подумать только! После твоей встречи с этой девушкой сами основы\nвремени перевернулись с ног на голову.",
    ("message/m390.mbe/000_Sheet1.csv", "m390_060_051"): "Попытки спасти Инори всё продолжались?{next}",
    ("message/m410.mbe/000_Sheet1.csv", "m410_021_101"): "Как получилось так уменьшиться...?{next}",
    ("message/m420.mbe/000_Sheet1.csv", "m420_090_020"): "А твоё тело создано из одной из тех тёмных теней.",
    ("message/m440.mbe/000_Sheet1.csv", "m440_010_030"): "Плутомоном управляли по твоей воле!{next}",
    ("message/m440.mbe/000_Sheet1.csv", "m440_010_031"): "Юномон управляли по твоей воле!{next}",
    ("message/digimon_chat.mbe/000_Sheet1.csv", "alfak_001_1_replay"): "Как всё дошло до такого?",
    ("message/digimon_chat.mbe/000_Sheet1.csv", "bab_001_2_replay"): "Есть хочешь?",
    ("message/digimon_chat.mbe/000_Sheet1.csv", "chro_001_3_replay"): "Теперь ты свободное существо.",
    ("message/digimon_chat.mbe/000_Sheet1.csv", "common004_2_replay"): "Ты замечательно выглядишь.",
    ("message/digimon_chat.mbe/000_Sheet1.csv", "common013_2_replay"): "Точно это не просто игра воображения?",
    ("message/digimon_chat.mbe/000_Sheet1.csv", "common020_2_replay"): "Что тут случилось?",
    ("message/digimon_chat.mbe/000_Sheet1.csv", "common022_2_replay"): "Точно сила не важнее всего?",
    ("message/digimon_chat.mbe/000_Sheet1.csv", "common043_2_replay"): "Точно?",
    ("message/digimon_chat.mbe/000_Sheet1.csv", "exbui_001_1_replay"): "Силы заметно прибавилось.",
    ("message/digimon_chat.mbe/000_Sheet1.csv", "gaji_001_4_replay"): "Я хочу, чтобы мы сработались.",
    ("message/digimon_chat.mbe/000_Sheet1.csv", "guraleo_001_4_replay"): "Не хочу отпускать тебя на тренировку.",
    ("message/digimon_chat.mbe/000_Sheet1.csv", "koro_001_4_replay"): "Пока лучше не ввязываться в драки.",
    ("message/digimon_chat.mbe/000_Sheet1.csv", "mash_001_2_replay"): "Какие розыгрыши уже были?",
    ("message/digimon_chat.mbe/000_Sheet1.csv", "megas_001_2_replay"): "Было бы ещё лучше, если бы с этим разобрались.",
    ("message/digimon_chat.mbe/000_Sheet1.csv", "mel_001_3_replay"): "Вот для чего всё это.",
    ("message/digimon_chat.mbe/000_Sheet1.csv", "metma_001_1_replay"): "Зависит от твоей силы.",
    ("message/digimon_chat.mbe/000_Sheet1.csv", "nep_001_4_replay"): "Лучше оставь это мне.",
    ("message/digimon_chat.mbe/000_Sheet1.csv", "panja_001_4_replay"): "Было бы здорово, если бы меня согрели!",
    ("message/digimon_chat.mbe/000_Sheet1.csv", "pata_001_2_replay"): "Что-то пошло не так?",
    ("message/digimon_chat.mbe/000_Sheet1.csv", "rigra_001_2_replay"): "Ты замечательно выглядишь.",
    ("message/digimon_chat.mbe/000_Sheet1.csv", "ulbra_001_3_replay"): "Хочется увидеть тебя ещё крупнее.",
    ("message/digimon_chat.mbe/000_Sheet1.csv", "vuli_001_3_replay"): "Точно после этого от них ничего не осталось?",
    ("text/help_message.mbe/000_Sheet1.csv", "help_systemmenu_04"): "Выбрать фоновую музыку для игры.",
    ("text/help_message.mbe/000_Sheet1.csv", "help_bgm_01"): "Изменить фоновую музыку, которая играет во время исследования локаций.",
    ("text/yes_no_message.mbe/000_Sheet1.csv", "yesno_hazamagate_0010"): "Вернуться в реальный мир? Вас перенесёт в мир,\nгде проходит ваша основная миссия.",
    ("text/yes_no_message.mbe/000_Sheet1.csv", "yesno_digifarm_0040"): "Этот дигимон всё ещё тренируется.\nПотратить иены, чтобы завершить тренировку сразу?",
    ("text/yes_no_message.mbe/000_Sheet1.csv", "yesno_digifarm_0050"): "Этот дигимон всё ещё тренируется.\nОтменить его обучение?",
    ("text/yes_no_message.mbe/000_Sheet1.csv", "yesno_title_0020"): "Перенести следующие данные и начать игру заново?\n\n{fc9Уровни сканирования дигимонов\nНавыки агента\nОчки аномалий\nПредметы (кроме ключевых)\nДеньги\nКарты}",
    ("message/d04.mbe/000_Sheet1.csv", "f_d0401_0040_0010"): "Ну и ну. Палмон, растяпа! Я думал, ты в патруле?",
    ("message/s090_072.mbe/000_Sheet1.csv", "s090_072_700"): "О боже! Как тебе удалось это узнать? Я немного удивлена.",
    ("message/s020_013.mbe/000_Sheet1.csv", "s020_013_372"): "{next}Мне сказали, что послание не нужно.",
    ("message/s020_013.mbe/000_Sheet1.csv", "s020_013_450"): "{next}В ответ на благодарность.",
    ("message/s020_013.mbe/000_Sheet1.csv", "s020_013_451"): "{next}Венусмон решила, что кольцо - рождественский подарок.",
    ("message/s020_013.mbe/000_Sheet1.csv", "s020_013_452"): "{next}Потому что объяснений не было.",
    ("message/s020_018.mbe/000_Sheet1.csv", "s020_018_042"): "{next}Пойдём куда-нибудь вместе!",
    ("message/s020_018.mbe/000_Sheet1.csv", "s020_018_100"): "{next}Туда им и дорога, этим титанам!",
    ("message/s020_018.mbe/000_Sheet1.csv", "s020_018_101"): "{next}Звучит так, будто есть подвох.",
    ("message/s020_018.mbe/000_Sheet1.csv", "s020_018_170"): "{next}Такое вполне возможно.",
    ("message/s020_018.mbe/000_Sheet1.csv", "s020_018_171"): "{next}Как думаешь, чего они добивались?",
    ("message/s020_018.mbe/000_Sheet1.csv", "s020_018_172"): "{next}Ты слишком усложняешь!",
    ("message/s020_018.mbe/000_Sheet1.csv", "s020_018_242"): "{next}По вкусу воды было понятно.",
    ("message/s020_018.mbe/000_Sheet1.csv", "s020_018_520"): "{next}Это важно. Надо прочитать.",
    ("message/s020_018.mbe/000_Sheet1.csv", "s020_018_521"): "{next}Вот это да, у Шеллмона был дневник.",
    ("message/s020_018.mbe/000_Sheet1.csv", "s020_018_590"): "{next}Так мы сможем проверить качество воды.",
    ("message/s020_018.mbe/000_Sheet1.csv", "s020_018_591"): "{next}Значит, подойдёт любое водное растение?",
    ("message/s020_018.mbe/000_Sheet1.csv", "s020_018_592"): "{next}Давай узнаем ещё секреты Шеллмона!",
    ("message/s020_018.mbe/000_Sheet1.csv", "s020_018_670"): "{next}Можно проплыть вокруг и проверить.",
    ("message/s020_018.mbe/000_Sheet1.csv", "s020_018_671"): "{next}Ладно, так... что ещё нужно сделать?",
    ("message/s020_018.mbe/000_Sheet1.csv", "s020_018_672"): "{next}Черепаха, которая не умеет плавать?",
    ("message/s020_018.mbe/000_Sheet1.csv", "s020_018_730"): "{next}Хорошо. Осмотрюсь ещё.",
    ("message/s020_018.mbe/000_Sheet1.csv", "s020_018_731"): "{end}Извини, нужно срочно уйти.",
    ("message/s020_018.mbe/000_Sheet1.csv", "s020_018_830"): "{next}Здесь под водой есть фиолетовое растение.",
    ("message/s020_018.mbe/000_Sheet1.csv", "s020_018_981"): "{next}Фиолетовый - вода в порядке, верно?",
    ("message/s020_018.mbe/000_Sheet1.csv", "s020_018_982"): "{next}Розовый - запаха нет, верно?",
    ("message/s020_019.mbe/000_Sheet1.csv", "s020_019_181"): "{next}Что случилось раньше?",
    ("message/s020_019.mbe/000_Sheet1.csv", "s020_019_182"): "{end}Я подумаю, как тебя спасти, и вернусь.",
    ("message/s020_019.mbe/000_Sheet1.csv", "s020_019_371"): "{end}Нужно ещё немного подготовиться.",
    ("message/s020_019.mbe/000_Sheet1.csv", "s020_019_411"): "{end}Продолжить спасение.",
    ("message/s020_173.mbe/000_Sheet1.csv", "s020_173_040"): "{next}Главное - не лениться и всё проверить.",
    ("message/s020_173.mbe/000_Sheet1.csv", "s020_173_041"): "{next}Можно остановиться и передохнуть.",
    ("message/s020_173.mbe/000_Sheet1.csv", "s020_173_210"): "{next}Да, с поверхности... И что?",
    ("message/s020_173.mbe/000_Sheet1.csv", "s020_173_212"): "{next}Не слишком ли ты сгущаешь краски?",
    ("message/s020_173.mbe/000_Sheet1.csv", "s020_173_282"): "{next}Сейчас ты вроде в порядке.",
    ("message/s020_173.mbe/000_Sheet1.csv", "s020_173_341"): "{next}Хочешь ещё глотнуть?",
    ("message/s020_173.mbe/000_Sheet1.csv", "s020_173_342"): "{next}Тогда скорее в лес!",
    ("message/s020_173.mbe/000_Sheet1.csv", "s020_173_411"): "{next}Твои поклонники тебя ждут.",
    ("message/s030_029.mbe/000_Sheet1.csv", "s030_029_052"): "{next}Но где ты найдёшь разведчика?",
    ("message/s030_029.mbe/000_Sheet1.csv", "s030_029_111"): "{next}Ты в этом уверен?",
    ("message/s030_029.mbe/000_Sheet1.csv", "s030_029_201"): "{next}Думаешь, это правда настолько хорошо?",
    ("message/s030_029.mbe/000_Sheet1.csv", "s030_029_300"): "{next}Верно. Объединим усилия!",
    ("message/s030_029.mbe/000_Sheet1.csv", "s030_029_301"): "{next}Хочешь объединить усилия?!",
    ("message/s030_029.mbe/000_Sheet1.csv", "s030_029_302"): "{end}Давай подумаем над другим планом.",
    ("message/s030_029.mbe/000_Sheet1.csv", "s030_029_421"): "{next}Значит, дело сделано?",
    ("message/s030_030.mbe/000_Sheet1.csv", "s030_030_040"): "{next}Похоже, у тебя проблемы.",
    ("message/s030_030.mbe/000_Sheet1.csv", "s030_030_141"): "{end}Буду скучать по этому месту...",
    ("message/s030_030.mbe/000_Sheet1.csv", "s030_030_202"): "{next}Что это были за фальшивые ульи?",
    ("message/s030_030.mbe/000_Sheet1.csv", "s030_030_391"): "{next}Советую жить с остальными в мире.",
    ("message/s030_031.mbe/000_Sheet1.csv", "s030_031_022"): "{next}Вот это да! Говорящий росток?!",
    ("message/s030_031.mbe/000_Sheet1.csv", "s030_031_090"): "{next}Группа снова в сборе.",
    ("message/s030_031.mbe/000_Sheet1.csv", "s030_031_091"): "{next}Можешь описать эти голоса?",
    ("message/s030_031.mbe/000_Sheet1.csv", "s030_031_151"): "{next}Хочешь послушать их вместе?",
    ("message/s030_031.mbe/000_Sheet1.csv", "s030_031_230"): "{next}Сиренмон хочет услышать, как ты поёшь!",
    ("message/s030_031.mbe/000_Sheet1.csv", "s030_031_312"): "{next}Им не хватает духа.",
    ("message/s030_031.mbe/000_Sheet1.csv", "s030_031_361"): "{next}Где найти Семена духа?",
    ("message/s030_031.mbe/000_Sheet1.csv", "s030_031_362"): "{next}Может, поискать их самостоятельно?",
    ("message/s040_160.mbe/000_Sheet1.csv", "s040_160_031"): "{next}Выгорание?",
    ("message/s040_160.mbe/000_Sheet1.csv", "s040_160_032"): "{end}Я... зайду в другой раз.",
    ("message/s040_160.mbe/000_Sheet1.csv", "s040_160_090"): "{next}Ну... можно попробовать посмотреть фильм.",
    ("message/digimon_chat_dlc01.mbe/000_Sheet1.csv", "omeb_001_2_replay"): "Откуда этот чёрный окрас?",
    ("message/digimon_chat_dlc17.mbe/000_Sheet1.csv", "omez_001_4_replay"): "Словно тьма поглотила тебя.",
    ("message/d320.mbe/000_Sheet1.csv", "d320_040_130"): "Нет, это испытание, которое нам предстоит преодолеть.",
    ("message/d320.mbe/000_Sheet1.csv", "d320_040_200"): "Хм... Я чувствую чужое присутствие. Похоже, поблизости есть\nи другие дигимоны, охотящиеся за X-антителом.",
    ("message/d320.mbe/000_Sheet1.csv", "d320_050_180"): "«Чудеса и правда случаются. То, что вы только что сказали,\nпохоже не на данные или факты, а на вашу мечту».",
    ("message/d320.mbe/000_Sheet1.csv", "d320_080_020"): "«Да... Их забрал Куга! Эти данные могут стать ключом\nк фундаментальной теории путешествий в пространстве-времени».",
    ("message/d320.mbe/000_Sheet1.csv", "d320_080_030"): "«Я не знаю его мотивов, но это катастрофа!\nЭти данные могли стать нашим билетом из этого кошмара!»",
    ("message/d330.mbe/000_Sheet1.csv", "d330_010_130"): "Хватит! Вы все повторяете одну и ту же ошибку!\nДанные Параллельмона изначально нам не принадлежат!",
    ("message/d330.mbe/000_Sheet1.csv", "d330_050_010"): "Я никогда не отдам эти данные! Только я смогу\nправильно распорядиться этим талантом!",
    ("message/d330.mbe/000_Sheet1.csv", "d330_050_060"): "Они и правда собираются забрать данные силой...\nЭтот человек в опасности. Нужно помочь!",
}


def read_rows(path: Path) -> list[list[str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.reader(f))


def write_rows(path: Path, rows: list[list[str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, lineterminator="\n")
        writer.writerows(rows)


def text_column(relative: str, row: list[str]) -> int | None:
    if relative.startswith("message/"):
        return 2 if len(row) > 2 else None
    return 1 if len(row) > 1 else None


def apply_targeted_rows() -> list[str]:
    changed: list[str] = []
    by_file: dict[str, dict[str, str]] = {}
    for (relative, key), value in TARGETED_ROWS.items():
        by_file.setdefault(relative, {})[key] = value

    for root in CSV_ROOTS:
        if not root.exists():
            continue
        for relative, replacements in by_file.items():
            path = root / relative
            if not path.exists():
                continue
            rows = read_rows(path)
            touched = False
            for row in rows:
                if not row:
                    continue
                value = replacements.get(row[0])
                index = text_column(relative, row)
                if value is None or index is None or row[index] == value:
                    continue
                row[index] = value
                touched = True
                changed.append(f"{root.name}/{relative}:{row[0]}")
            if touched:
                write_rows(path, rows)
    return changed


def main() -> None:
    changed = apply_targeted_rows()
    print(f"targeted_rows={len(changed)}")
    for item in changed:
        print(f"  {item}")


if __name__ == "__main__":
    main()

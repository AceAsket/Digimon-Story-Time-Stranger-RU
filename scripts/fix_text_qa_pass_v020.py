from __future__ import annotations

import csv
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CSV_ROOTS = [
    ROOT / "csv" / "app_text01",
    ROOT / "csv" / "patch_text01",
]


TARGETED_ROWS: dict[tuple[str, str], dict[str, str]] = {
    ("text/info_message.mbe/000_Sheet1.csv", "info_message_playername"): {
        "app_text01": "Впишите своё имя — и вы возродитесь в нижнем мире...\n\n<{fc9{d0} Юки}>",
        "patch_text01": "Впишите своё имя — и вы возродитесь в нижнем мире...\n\n<{fc9{d0} Юки}>",
    },
    ("message/m010.mbe/000_Sheet1.csv", "m010_001_030"): {
        "app_text01": "Впиши себе новое имя — и переродись в этом мире.",
        "patch_text01": "Впиши себе новое имя — и переродись в этом мире.",
    },
    ("message/m010.mbe/000_Sheet1.csv", "m010_020_040"): {
        "app_text01": (
            "Я подаю запрос на бюджет для новой формы, но в этой миссии\n"
            "тебе нужно не привлекать внимания."
        ),
        "patch_text01": (
            "Я подаю запрос на бюджет для новой формы, но в этой миссии\n"
            "тебе нужно не привлекать внимания."
        ),
    },
    ("message/m010.mbe/000_Sheet1.csv", "m010_020_190"): {
        "app_text01": "Ясно.{next}",
        "patch_text01": "Ясно.{next}",
    },
    ("message/m010.mbe/000_Sheet1.csv", "m010_020_191"): {
        "app_text01": "Повторим успех?",
        "patch_text01": "Повторим успех?",
    },
    ("message/m010.mbe/000_Sheet1.csv", "m010_020_230"): {
        "app_text01": (
            "Результаты нашей последней миссии меня не устроили: цель\n"
            "ушла в последнюю минуту..."
        ),
        "patch_text01": (
            "Результаты нашей последней миссии меня не устроили: цель\n"
            "ушла в последнюю минуту..."
        ),
    },
    ("message/m010.mbe/000_Sheet1.csv", "m010_020_260"): {
        "app_text01": (
            "Эта миссия не исключение. Действуй максимально осторожно:\n"
            "секретность должна быть сохранена."
        ),
        "patch_text01": (
            "Эта миссия не исключение. Действуй максимально осторожно:\n"
            "секретность должна быть сохранена."
        ),
    },
    ("message/m010.mbe/000_Sheet1.csv", "m010_040_010"): {
        "app_text01": "Вижу, ты на указанных координатах. Доложи обстановку.",
        "patch_text01": "Вижу, ты на указанных координатах. Доложи обстановку.",
    },
    ("message/m010.mbe/000_Sheet1.csv", "m010_040_080"): {
        "app_text01": (
            "Явления, ради которых нас сюда отправили, чаще всего\n"
            "наблюдаются вокруг этой Стены. Похоже, придётся изучить и то,\n"
            "что находится внутри."
        ),
        "patch_text01": (
            "Явления, ради которых нас сюда отправили, чаще всего\n"
            "наблюдаются вокруг этой Стены. Похоже, придётся изучить и то,\n"
            "что находится внутри."
        ),
    },
    ("message/m010.mbe/000_Sheet1.csv", "m010_040_140"): {
        "app_text01": (
            "Вот почему мы так спешим. Но боюсь, из-за этой спешки мы\n"
            "раскрыли миру своё существование..."
        ),
        "patch_text01": (
            "Вот почему мы так спешим. Но боюсь, из-за этой спешки мы\n"
            "раскрыли миру своё существование..."
        ),
    },
    ("message/m010.mbe/000_Sheet1.csv", "m010_040_150"): {
        "app_text01": (
            "Но главная задача остаётся прежней: понять, как эти аномалии\n"
            "связаны с трагедиями, которые следуют за ними."
        ),
        "patch_text01": (
            "Но главная задача остаётся прежней: понять, как эти аномалии\n"
            "связаны с трагедиями, которые следуют за ними."
        ),
    },
    ("message/m010.mbe/000_Sheet1.csv", "m010_080_020"): {
        "app_text01": "У этого человека уже есть разрешение на связь с твоим Дигивайсом.",
        "patch_text01": "У этого человека уже есть разрешение на связь с твоим Дигивайсом.",
    },
    ("message/m010.mbe/000_Sheet1.csv", "m010_080_030"): {
        "app_text01": (
            "Обычно я бы решил, что это кто-то из организации... В любом\n"
            "случае, сделай всё возможное, чтобы обезопасить его."
        ),
        "patch_text01": (
            "Обычно я бы решил, что это кто-то из организации... В любом\n"
            "случае, сделай всё возможное, чтобы обезопасить его."
        ),
    },
    ("message/m010.mbe/000_Sheet1.csv", "m010_090_010"): {
        "app_text01": "Похоже, рядом несколько фазово-электронных форм жизни.",
        "patch_text01": "Похоже, рядом несколько фазово-электронных форм жизни.",
    },
    ("message/m010.mbe/000_Sheet1.csv", "m010_090_100"): {
        "app_text01": (
            "Если окажешься в бою, не сомневайся. Главное — выполнить\n"
            "миссию."
        ),
        "patch_text01": (
            "Если окажешься в бою, не сомневайся. Главное — выполнить\n"
            "миссию."
        ),
    },
    ("message/m010.mbe/000_Sheet1.csv", "m010_200_100"): {
        "app_text01": (
            "Полагаю... она и есть цель дополнительного задания. Правда,\n"
            "объясняет она не слишком много..."
        ),
        "patch_text01": (
            "Полагаю... она и есть цель дополнительного задания. Правда,\n"
            "объясняет она не слишком много..."
        ),
    },
    ("message/m010.mbe/000_Sheet1.csv", "m010_200_120"): {
        "app_text01": (
            "Меня всё ещё интересует, почему ей уже разрешили связаться\n"
            "с твоим Дигивайсом."
        ),
        "patch_text01": (
            "Меня всё ещё интересует, почему ей уже разрешили связаться\n"
            "с твоим Дигивайсом."
        ),
    },
    ("message/m010.mbe/000_Sheet1.csv", "m010_200_130"): {
        "app_text01": (
            "Я ещё раз проверю базу данных. Если что-нибудь выясню,\n"
            "сразу выйду на связь."
        ),
        "patch_text01": (
            "Я ещё раз проверю базу данных. Если что-нибудь выясню,\n"
            "сразу выйду на связь."
        ),
    },
    ("message/m010.mbe/000_Sheet1.csv", "m010_200_140"): {
        "app_text01": (
            "Она меня заинтересовала... но сначала надо разобраться с этим\n"
            "гигантским Дигимоном."
        ),
        "patch_text01": (
            "Она меня заинтересовала... но сначала надо разобраться с этим\n"
            "гигантским Дигимоном."
        ),
    },
    ("message/m010.mbe/000_Sheet1.csv", "m010_200_150"): {
        "app_text01": (
            "Нельзя позволить ему прорваться в город. Пока продолжай\n"
            "основную миссию."
        ),
        "patch_text01": (
            "Нельзя позволить ему прорваться в город. Пока продолжай\n"
            "основную миссию."
        ),
    },
    ("message/m010.mbe/000_Sheet1.csv", "m010_200_160"): {
        "app_text01": "Принято. Беру цель под защиту и продолжаю миссию!{next}",
        "patch_text01": "Принято. Беру цель под защиту и продолжаю миссию!{next}",
    },
    ("message/d14.mbe/000_Sheet1.csv", "f_d1405_0050_0010"): {
        "app_text01": (
            "Ответа нет... Пиёмон говорил что-то о войне между\n"
            "Дигимонами..."
        ),
        "patch_text01": (
            "Ответа нет... Пиёмон говорил что-то о войне между\n"
            "Дигимонами..."
        ),
    },
    ("message/d14.mbe/000_Sheet1.csv", "f_d1405_0060_0010"): {
        "app_text01": "Ответа нет... Между Дигимонами правда идёт война?",
        "patch_text01": "Ответа нет... Между Дигимонами правда идёт война?",
    },
    ("message/d14.mbe/000_Sheet1.csv", "f_d1405_0070_0010"): {
        "app_text01": "Этот Дигимон без сознания... Его атаковал другой Дигимон?",
        "patch_text01": "Этот Дигимон без сознания... Его атаковал другой Дигимон?",
    },
    ("message/m020.mbe/000_Sheet1.csv", "m020_050_030"): {
        "app_text01": "Тот Дигимон — крупнейший из когда-либо встречавшихся.",
        "patch_text01": "Тот Дигимон — крупнейший из когда-либо встречавшихся.",
    },
    ("message/m020.mbe/000_Sheet1.csv", "m020_120_010"): {
        "app_text01": "Ааах!",
        "patch_text01": "Ааах!",
    },
    ("message/m020.mbe/000_Sheet1.csv", "m020_120_020"): {
        "app_text01": "Ииии!",
        "patch_text01": "Ииии!",
    },
    ("message/m020.mbe/000_Sheet1.csv", "m020_120_030"): {
        "app_text01": "Мгх...!",
        "patch_text01": "Мгх...!",
    },
    ("message/m020.mbe/000_Sheet1.csv", "m020_120_040"): {
        "app_text01": "А...?",
        "patch_text01": "А...?",
    },
    ("message/m020.mbe/000_Sheet1.csv", "m020_120_050"): {
        "app_text01": "Ой!",
        "patch_text01": "Ой!",
    },
    ("message/m020.mbe/000_Sheet1.csv", "m020_120_060"): {
        "app_text01": "Эй! Сюда!",
        "patch_text01": "Эй! Сюда!",
    },
    ("message/m020.mbe/000_Sheet1.csv", "m020_120_070"): {
        "app_text01": "Эй! Я здесь!",
        "patch_text01": "Эй! Я здесь!",
    },
    ("message/m020.mbe/000_Sheet1.csv", "m020_120_080"): {
        "app_text01": "Я в порядке!",
        "patch_text01": "Я в порядке!",
    },
    ("message/m020.mbe/000_Sheet1.csv", "m020_130_010"): {
        "app_text01": "Ч-что?! Что вообще происходит?!",
        "patch_text01": "Ч-что?! Что вообще происходит?!",
    },
    ("message/m020.mbe/000_Sheet1.csv", "m020_130_020"): {
        "app_text01": "Что ты здесь делаешь?{next}",
        "patch_text01": "Что ты здесь делаешь?{next}",
    },
    ("message/m020.mbe/000_Sheet1.csv", "m020_130_021"): {
        "app_text01": "Ты кто?",
        "patch_text01": "Ты кто?",
    },
    ("message/m020.mbe/000_Sheet1.csv", "m020_130_022"): {
        "app_text01": "Здесь произошло странное нападение.",
        "patch_text01": "Здесь произошло странное нападение.",
    },
    ("message/m020.mbe/000_Sheet1.csv", "m020_130_030"): {
        "app_text01": "Я? Я же Пиёмон!",
        "patch_text01": "Я? Я же Пиёмон!",
    },
    ("message/m020.mbe/000_Sheet1.csv", "m020_130_040"): {
        "app_text01": (
            "Обломки вдруг рухнули сверху — казалось,\n"
            "мне уже не выбраться!"
        ),
        "patch_text01": (
            "Обломки вдруг рухнули сверху — казалось,\n"
            "мне уже не выбраться!"
        ),
    },
    ("message/m020.mbe/000_Sheet1.csv", "m020_130_050"): {
        "app_text01": (
            "А потом завал исчез благодаря тебе! Я всё равно\n"
            "не понимаю, что происходит!"
        ),
        "patch_text01": (
            "А потом завал исчез благодаря тебе! Я всё равно\n"
            "не понимаю, что происходит!"
        ),
    },
    ("message/m020.mbe/000_Sheet1.csv", "m020_130_060"): {
        "app_text01": (
            "Атака? Это из-за неё был тот грохот?\n"
            "Всё здание так трясло!"
        ),
        "patch_text01": (
            "Атака? Это из-за неё был тот грохот?\n"
            "Всё здание так трясло!"
        ),
    },
    ("message/m020.mbe/000_Sheet1.csv", "m020_130_070"): {
        "app_text01": (
            "Обломки вдруг рухнули сверху — казалось,\n"
            "мне уже не выбраться!"
        ),
        "patch_text01": (
            "Обломки вдруг рухнули сверху — казалось,\n"
            "мне уже не выбраться!"
        ),
    },
    ("message/m020.mbe/000_Sheet1.csv", "m020_130_080"): {
        "app_text01": (
            "А потом завал исчез благодаря тебе! Я всё равно\n"
            "не понимаю, что происходит!"
        ),
        "patch_text01": (
            "А потом завал исчез благодаря тебе! Я всё равно\n"
            "не понимаю, что происходит!"
        ),
    },
    ("message/m020.mbe/000_Sheet1.csv", "m020_130_090"): {
        "app_text01": "Не знаю! Вдруг всё вокруг посыпалось...",
        "patch_text01": "Не знаю! Вдруг всё вокруг посыпалось...",
    },
    ("message/m020.mbe/000_Sheet1.csv", "m020_130_100"): {
        "app_text01": "Я просто хочу вернуться к друзьям!",
        "patch_text01": "Я просто хочу вернуться к друзьям!",
    },
    ("message/m020.mbe/000_Sheet1.csv", "m020_130_110"): {
        "app_text01": "Сможешь перелететь на ту сторону?{next}",
        "patch_text01": "Сможешь перелететь на ту сторону?{next}",
    },
    ("message/m020.mbe/000_Sheet1.csv", "m020_130_111"): {
        "app_text01": "Выберемся отсюда вместе?",
        "patch_text01": "Выберемся отсюда вместе?",
    },
    ("message/m020.mbe/000_Sheet1.csv", "m020_130_112"): {
        "app_text01": "Ну... тогда удачи.",
        "patch_text01": "Ну... тогда удачи.",
    },
    ("message/m020.mbe/000_Sheet1.csv", "m020_130_120"): {
        "app_text01": "А? П-почему ты спрашиваешь?",
        "patch_text01": "А? П-почему ты спрашиваешь?",
    },
    ("message/m020.mbe/000_Sheet1.csv", "m020_130_130"): {
        "app_text01": (
            "Не думаю... Только взгляни,\n"
            "какие у меня крошечные крылья!"
        ),
        "patch_text01": (
            "Не думаю... Только взгляни,\n"
            "какие у меня крошечные крылья!"
        ),
    },
    ("message/m020.mbe/000_Sheet1.csv", "m020_130_140"): {
        "app_text01": (
            "Но завал ведь исчез благодаря тебе...\n"
            "И, может, мне только кажется, но..."
        ),
        "patch_text01": (
            "Но завал ведь исчез благодаря тебе...\n"
            "И, может, мне только кажется, но..."
        ),
    },
    ("message/m020.mbe/000_Sheet1.csv", "m020_130_145"): {
        "app_text01": (
            "...у меня такое чувство, будто мы уже встречались.\n"
            "Так что, наверное, ты не плохой человек."
        ),
        "patch_text01": (
            "...у меня такое чувство, будто мы уже встречались.\n"
            "Так что, наверное, ты не плохой человек."
        ),
    },
    ("message/m020.mbe/000_Sheet1.csv", "m020_130_150"): {
        "app_text01": "Ладно. Попробую!",
        "patch_text01": "Ладно. Попробую!",
    },
    ("message/m020.mbe/000_Sheet1.csv", "m020_130_160"): {
        "app_text01": "Выбраться отсюда? К-как?!",
        "patch_text01": "Выбраться отсюда? К-как?!",
    },
    ("message/m020.mbe/000_Sheet1.csv", "m020_130_170"): {
        "app_text01": (
            "Но... завал исчез благодаря тебе...\n"
            "значит, наверное, тебе можно доверять..."
        ),
        "patch_text01": (
            "Но... завал исчез благодаря тебе...\n"
            "значит, наверное, тебе можно доверять..."
        ),
    },
    ("message/m020.mbe/000_Sheet1.csv", "m020_130_180"): {
        "app_text01": "Ладно. Я с тобой!",
        "patch_text01": "Ладно. Я с тобой!",
    },
    ("message/m020.mbe/000_Sheet1.csv", "m020_130_190"): {
        "app_text01": "Э-эй...!",
        "patch_text01": "Э-эй...!",
    },
    ("message/m020.mbe/000_Sheet1.csv", "m020_140_010"): {
        "app_text01": "П-прямо отсюда? На ту сторону?",
        "patch_text01": "П-прямо отсюда? На ту сторону?",
    },
    ("message/m020.mbe/000_Sheet1.csv", "m020_140_020"): {
        "app_text01": "Пожалуйста. Ты моя единственная надежда.{next}",
        "patch_text01": "Пожалуйста. Ты моя единственная надежда.{next}",
    },
    ("message/m020.mbe/000_Sheet1.csv", "m020_140_021"): {
        "app_text01": "Да... Похоже, далековато...{next}",
        "patch_text01": "Да... Похоже, далековато...{next}",
    },
    ("message/m020.mbe/000_Sheet1.csv", "m020_140_022"): {
        "app_text01": "Пока не будем.{end}",
        "patch_text01": "Пока не будем.{end}",
    },
    ("message/m020.mbe/000_Sheet1.csv", "m020_140_030"): {
        "app_text01": "Что?! Точно?",
        "patch_text01": "Что?! Точно?",
    },
    ("message/m020.mbe/000_Sheet1.csv", "m020_140_040"): {
        "app_text01": "Н-но другого выхода правда нет, да...?",
        "patch_text01": "Н-но другого выхода правда нет, да...?",
    },
    ("message/m020.mbe/000_Sheet1.csv", "m020_140_050"): {
        "app_text01": "Ладно, попробую... но ничего не обещаю!",
        "patch_text01": "Ладно, попробую... но ничего не обещаю!",
    },
    ("message/m020.mbe/000_Sheet1.csv", "m020_140_060"): {
        "app_text01": "Хватайся... Полетели!",
        "patch_text01": "Хватайся... Полетели!",
    },
    ("message/m020.mbe/000_Sheet1.csv", "m020_140_070"): {
        "app_text01": "Ай! Не выходит!",
        "patch_text01": "Ай! Не выходит!",
    },
    ("message/m020.mbe/000_Sheet1.csv", "m020_140_080"): {
        "app_text01": "Придётся садиться аварийно... вот туда!",
        "patch_text01": "Придётся садиться аварийно... вот туда!",
    },
    ("message/digimon_chat.mbe/000_Sheet1.csv", "zplu_001_4_reaction_char_UNDEADPLUTOMON"): {
        "app_text01": (
            "Теперь мы союзники, значит, придётся потерпеть.\n"
            "Возьми меня с собой — так я отвлекусь от голода."
        ),
        "patch_text01": (
            "Теперь мы союзники, значит, придётся потерпеть.\n"
            "Возьми меня с собой — так я отвлекусь от голода."
        ),
    },
    ("message/digimon_chat.mbe/000_Sheet1.csv", "koro_001_1_reaction_char_KOROMON"): {
        "app_text01": (
            "Значит, мне надо эволюционировать?\n"
            "Я выложусь на полную, так что поддержи меня!"
        ),
        "patch_text01": (
            "Значит, мне надо эволюционировать?\n"
            "Я выложусь на полную, так что поддержи меня!"
        ),
    },
    ("message/digimon_chat.mbe/000_Sheet1.csv", "common010_1_replay"): {
        "app_text01": "Я уже твой друг.",
        "patch_text01": "Я уже твой друг.",
    },
    ("message/digimon_chat.mbe/000_Sheet1.csv", "common010_2_replay"): {
        "app_text01": "Не заставляй себя.",
        "patch_text01": "Не заставляй себя.",
    },
    ("text/help_message.mbe/000_Sheet1.csv", "1004"): {
        "app_text01": "Просматривайте и используйте предметы из инвентаря.",
        "patch_text01": "Просматривайте и используйте предметы из инвентаря.",
    },
    ("text/help_message.mbe/000_Sheet1.csv", "1029"): {
        "app_text01": "Выберите костюм для персонажа.",
        "patch_text01": "Выберите костюм для персонажа.",
    },
    ("text/common_message.mbe/000_Sheet1.csv", "710"): {
        "app_text01": "Настройки",
        "patch_text01": "Настройки",
    },
    ("text/common_message.mbe/000_Sheet1.csv", "104"): {
        "app_text01": "Инвентарь",
        "patch_text01": "Инвентарь",
    },
    ("text/common_message.mbe/000_Sheet1.csv", "10073"): {
        "app_text01": "Личн. навык",
        "patch_text01": "Личн. навык",
    },
    ("text/common_message_dx11.mbe/000_Sheet1.csv", "1019014"): {
        "app_text01": "К настройкам",
        "patch_text01": "К настройкам",
    },
    ("text/key_help_text.mbe/000_Sheet1.csv", "key_help_0068"): {
        "app_text01": " Настройки",
        "patch_text01": " Настройки",
    },
    ("text/key_help_text.mbe/000_Sheet1.csv", "key_help_0020"): {
        "app_text01": " Снять",
        "patch_text01": " Снять",
    },
    ("text/key_help_text.mbe/000_Sheet1.csv", "key_help_0097"): {
        "app_text01": " Экипировать",
        "patch_text01": " Экипировать",
    },
    ("text/key_help_text.mbe/000_Sheet1.csv", "key_help_0125"): {
        "app_text01": " Экипировать все",
        "patch_text01": " Экипировать все",
    },
    ("text/item_name.mbe/000_Sheet1.csv", "812"): {
        "app_text01": "Футболка с пиксельной графикой Дигимон (Пиёмон)",
        "patch_text01": "Футболка с пиксельной графикой Дигимон (Пиёмон)",
    },
    ("text/item_ruby.mbe/000_Sheet1.csv", "812"): {
        "app_text01": "Футболка с пиксельной графикой Дигимон (Пиёмон)",
        "patch_text01": "Футболка с пиксельной графикой Дигимон (Пиёмон)",
    },
    ("text/main_quest_step.mbe/000_Sheet1.csv", "440013"): {
        "app_text01": "Поговори с Пиёмоном.",
        "patch_text01": "Поговори с Пиёмоном.",
    },
    ("text/quest_title.mbe/000_Sheet1.csv", "153"): {
        "app_text01": "Священное испытание Пиёмона",
        "patch_text01": "Священное испытание Пиёмона",
    },
    ("text/skill_name.mbe/000_Sheet1.csv", "30261"): {
        "app_text01": "Святой свет I",
        "patch_text01": "Святой свет I",
    },
    ("text/skill_name.mbe/000_Sheet1.csv", "30262"): {
        "app_text01": "Святой свет II",
        "patch_text01": "Святой свет II",
    },
    ("text/skill_name.mbe/000_Sheet1.csv", "30263"): {
        "app_text01": "Святой свет III",
        "patch_text01": "Святой свет III",
    },
    ("text/jogress_skill_name.mbe/000_Sheet1.csv", "30261"): {
        "app_text01": "Святой свет I",
        "patch_text01": "Святой свет I",
    },
    ("text/jogress_skill_name.mbe/000_Sheet1.csv", "30262"): {
        "app_text01": "Святой свет II",
        "patch_text01": "Святой свет II",
    },
    ("text/jogress_skill_name.mbe/000_Sheet1.csv", "30263"): {
        "app_text01": "Святой свет III",
        "patch_text01": "Святой свет III",
    },
    ("text/skill_ruby.mbe/000_Sheet1.csv", "30261"): {
        "app_text01": "Святой свет I",
        "patch_text01": "Святой свет I",
    },
    ("text/skill_ruby.mbe/000_Sheet1.csv", "30262"): {
        "app_text01": "Святой свет II",
        "patch_text01": "Святой свет II",
    },
    ("text/skill_ruby.mbe/000_Sheet1.csv", "30263"): {
        "app_text01": "Святой свет III",
        "patch_text01": "Святой свет III",
    },
    ("text/tutorial_title.mbe/000_Sheet1.csv", "tutorial_title_Status_01"): {
        "app_text01": "Характеристики, навыки и снаряжение",
        "patch_text01": "Характеристики, навыки и снаряжение",
    },
    ("text/tutorial_title.mbe/000_Sheet1.csv", "tutorial_title_EquipmentChange_01"): {
        "app_text01": "Снаряжение",
        "patch_text01": "Снаряжение",
    },
    ("text/tutorial_title.mbe/000_Sheet1.csv", "tutorial_title_PersonalitySkill_01"): {
        "app_text01": "Личн. навык",
        "patch_text01": "Личн. навык",
    },
    ("text/tutorial_title.mbe/000_Sheet1.csv", "tutorial_title_Talent_01"): {
        "app_text01": "Техника эволюции 1: Талант",
        "patch_text01": "Техника эволюции 1: Талант",
    },
    ("text/tutorial_title.mbe/000_Sheet1.csv", "tutorial_title_Accumulation_01"): {
        "app_text01": "Техника эволюции 2: Накопленные статы",
        "patch_text01": "Техника эволюции 2: Накопленные статы",
    },
    ("text/tutorial_title.mbe/000_Sheet1.csv", "tutorial_title_Friendship_01"): {
        "app_text01": "Техника эволюции 3: Связь",
        "patch_text01": "Техника эволюции 3: Связь",
    },
    ("text/tutorial_title.mbe/000_Sheet1.csv", "tutorial_title_EvolutionTechnique_01"): {
        "app_text01": "Техника эволюции 1: Талант",
        "patch_text01": "Техника эволюции 1: Талант",
    },
    ("text/tutorial_title.mbe/000_Sheet1.csv", "tutorial_title_EvolutionTechnique_02"): {
        "app_text01": "Техника эволюции 2: Накопленные статы",
        "patch_text01": "Техника эволюции 2: Накопленные статы",
    },
    ("text/tutorial_title.mbe/000_Sheet1.csv", "tutorial_title_EvolutionTechnique_03"): {
        "app_text01": "Техника эволюции 3: Связь",
        "patch_text01": "Техника эволюции 3: Связь",
    },
    ("text/tutorial_explanation.mbe/000_Sheet1.csv", "tutorial_exp_Evolution_01_002"): {
        "app_text01": (
            "И наоборот, процесс сжатия данных Дигимона называется\n"
            "«деволюцией».\n\n"
            "{fc9Для деволюции должно быть выполнено одно из условий:\n"
            "- форма уже зарегистрирована в Полевом руководстве;\n"
            "- форма имеет ту же личность.}\n\n"
            "Это помогает направить эволюцию Дигимона к другой форме."
        ),
    },
    ("text/tutorial_explanation.mbe/000_Sheet1.csv", "tutorial_exp_Evolution_01_003"): {
        "app_text01": (
            "Существуют секретные техники эволюции и деволюции.\n\n"
            "Откройте на Дигивайсе:\n"
            "Система > Обучение > Тренировка,\n"
            "чтобы просмотреть:\n"
            "{fc9Техника эволюции 1: Талант\n"
            "Техника эволюции 2: Накопленные статы\n"
            "Техника эволюции 3: Связь}"
        ),
    },
    ("text/tutorial_explanation.mbe/000_Sheet1.csv", "tutorial_exp_Evolution_01_005"): {
        "patch_text01": (
            "Существуют секретные техники эволюции и деволюции.\n\n"
            "Откройте на Дигивайсе:\n"
            "Система > Обучение > Тренировка,\n"
            "чтобы просмотреть:\n"
            "{fc9Техника эволюции 1: Талант\n"
            "Техника эволюции 2: Накопленные статы\n"
            "Техника эволюции 3: Связь}"
        ),
    },
    ("text/tutorial_explanation.mbe/000_Sheet1.csv", "tutorial_exp_Status_01_001"): {
        "app_text01": (
            "Внимательно изучайте данные союзных дигимонов.\n\n"
            "Так вы лучше поймёте их скрытую силу\n"
            "и найдёте подсказки для дальнейшей тренировки.\n\n"
            "Возможно, это подскажет новые стратегии.\n\n"
            "{fc9Дигимонов можно усиливать,\n"
            "меняя дополнительные навыки и снаряжение.\n"
            "Получили диск навыка или предмет снаряжения?\n"
            "Не забудьте поставить его.}"
        ),
        "patch_text01": (
            "Внимательно изучайте данные союзных дигимонов.\n\n"
            "Так вы лучше поймёте их скрытую силу\n"
            "и найдёте подсказки для дальнейшей тренировки.\n\n"
            "Возможно, это подскажет новые стратегии.\n\n"
            "{fc9Дигимонов можно усиливать,\n"
            "меняя дополнительные навыки и снаряжение.\n"
            "Получили диск навыка или предмет снаряжения?\n"
            "Не забудьте поставить его.}"
        ),
    },
    ("text/tutorial_explanation.mbe/000_Sheet1.csv", "tutorial_exp_SkillChange_01_002"): {
        "app_text01": (
            "Чтобы настроить дополнительные навыки,\n"
            "откройте на Дигивайсе:\n"
            "Дигимоны > Настройки > {sub2}\n"
            "Характеристики/навыки.\n\n"
            "Затем выберите слот дополнительных навыков.\n\n"
            "{fc9Диски навыков можно снимать\n"
            "и ставить другим дигимонам.}\n\n"
            "Используйте дополнительные навыки,\n"
            "чтобы закрывать слабости,\n"
            "усиливать сильные стороны\n"
            "и решать проблемы совместимости."
        ),
        "patch_text01": (
            "Чтобы настроить дополнительные навыки,\n"
            "откройте на Дигивайсе:\n"
            "Дигимоны > Настройки > {sub2}\n"
            "Характеристики/навыки.\n\n"
            "Затем выберите слот дополнительных навыков.\n\n"
            "{fc9Диски навыков можно снимать\n"
            "и ставить другим дигимонам.}\n\n"
            "Используйте дополнительные навыки,\n"
            "чтобы закрывать слабости,\n"
            "усиливать сильные стороны\n"
            "и решать проблемы совместимости."
        ),
    },
    ("text/tutorial_explanation.mbe/000_Sheet1.csv", "tutorial_exp_EquipmentChange_01_001"): {
        "app_text01": (
            "Снаряжение — это патчи улучшения,\n"
            "которые усиливают дигимона.\n\n"
            "Чтобы поставить снаряжение,\n"
            "откройте на Дигивайсе:\n"
            "Дигимоны > Настройки > {sub2}\n"
            "Снаряжение/навыки.\n\n"
            "Затем выберите слот снаряжения.\n\n"
            "{fc9Снаряжение можно снимать\n"
            "и ставить другим дигимонам.}\n\n"
            "Его можно купить в магазинах,\n"
            "найти в сундуках или получить\n"
            "от некоторых дигимонов."
        ),
        "patch_text01": (
            "Снаряжение — это патчи улучшения,\n"
            "которые усиливают дигимона.\n\n"
            "Чтобы поставить снаряжение,\n"
            "откройте на Дигивайсе:\n"
            "Дигимоны > Настройки > {sub2}\n"
            "Снаряжение/навыки.\n\n"
            "Затем выберите слот снаряжения.\n\n"
            "{fc9Снаряжение можно снимать\n"
            "и ставить другим дигимонам.}\n\n"
            "Его можно купить в магазинах,\n"
            "найти в сундуках или получить\n"
            "от некоторых дигимонов."
        ),
    },
    ("text/tutorial_explanation.mbe/000_Sheet1.csv", "tutorial_exp_SkillDisc_01_001"): {
        "app_text01": (
            "Эти предметы позволяют менять\n"
            "дополнительные навыки\n"
            "союзных дигимонов.\n\n"
            "{fc9Чтобы изменить дополнительные навыки,\n"
            "откройте на Дигивайсе:\n"
            "Дигимоны > Настройки.}\n"
            "Примечание: подробнее см. в обучении:\n"
            "Бои > Дополнительные навыки.\n\n"
            "Диски навыков можно найти в сундуках\n"
            "или купить в магазине."
        ),
        "patch_text01": (
            "Эти предметы позволяют менять\n"
            "дополнительные навыки\n"
            "союзных дигимонов.\n\n"
            "{fc9Чтобы изменить дополнительные навыки,\n"
            "откройте на Дигивайсе:\n"
            "Дигимоны > Настройки.}\n"
            "Примечание: подробнее см. в обучении:\n"
            "Бои > Дополнительные навыки.\n\n"
            "Диски навыков можно найти в сундуках\n"
            "или купить в магазине."
        ),
    },
}

TARGETED_ROWS.update(
    {
        ("text/battle_info_message.mbe/000_Sheet1.csv", "19"): {
            "app_text01": "Замена: {d0}!",
            "patch_text01": "Замена: {d0}!",
        },
        ("text/info_message.mbe/000_Sheet1.csv", "3602"): {
            "app_text01": "Изменено.",
            "patch_text01": "Изменено.",
        },
        ("text/common_message.mbe/000_Sheet1.csv", "1000"): {
            "app_text01": "Пусто",
            "patch_text01": "Пусто",
        },
        ("text/common_message.mbe/000_Sheet1.csv", "1011"): {
            "app_text01": "Пусто",
            "patch_text01": "Пусто",
        },
        ("text/common_message.mbe/000_Sheet1.csv", "ui_kizunaskill_0055"): {
            "app_text01": "{is26}{image(ui_icon_personal01_03)} Стратег",
            "patch_text01": "{is26}{image(ui_icon_personal01_03)} Стратег",
        },
        ("text/common_message.mbe/000_Sheet1.csv", "ui_digimonchat_personality_302"): {
            "app_text01": "{is28}{image(ui_icon_personal01_03)} Стратег",
            "patch_text01": "{is28}{image(ui_icon_personal01_03)} Стратег",
        },
        ("text/personality_name.mbe/000_Sheet1.csv", "14"): {
            "app_text01": "Стратег",
            "patch_text01": "Стратег",
        },
        ("text/tamer_skill_name.mbe/000_Sheet1.csv", "167"): {
            "app_text01": "Барьер стратега",
            "patch_text01": "Барьер стратега",
        },
        ("text/tamer_skill_name.mbe/000_Sheet1.csv", "172"): {
            "app_text01": "Совершенство стратега",
            "patch_text01": "Совершенство стратега",
        },
        ("text/tamer_skill_name.mbe/000_Sheet1.csv", "203"): {
            "app_text01": "Применение КП: Стратег",
            "patch_text01": "Применение КП: Стратег",
        },
        ("text/tamer_skill_name.mbe/000_Sheet1.csv", "209"): {
            "app_text01": "Применение КП: Стратег",
            "patch_text01": "Применение КП: Стратег",
        },
        ("text/tamer_skill_name.mbe/000_Sheet1.csv", "219"): {
            "app_text01": "Применение КП: Стратег",
            "patch_text01": "Применение КП: Стратег",
        },
    }
)


EXACT_REPLACEMENTS = {
    "Пртестуешь": "Протестуешь",
    "Тебя устраивают страшилки?": "Любишь страшные истории?",
    "В полном порядке.": "Да, люблю.",
    "Личные навыки": "Личн. навык",
    "Бийомон": "Пиёмон",
    "Biyomon": "Пиёмон",
    "Они рухнули... Это было делом рук другого Дигимона?": "Этот Дигимон без сознания... Его атаковал другой Дигимон?",
    "Что такое друзья? Не лучше ли их иметь?": "Друзья... Лучше с ними?",
    "Ты уже это делаешь. Я твой друг.": "Я уже твой друг.",
    "Я не думаю, что тебе нужно форсировать это.": "Не заставляй себя.",
    "Оборудовать Все": "Экипировать все",
    "Оборудовать все": "Экипировать все",
    "В коробке": "Инвентарь",
    "В Боксе": "Инвентарь",
    "цифровой революции": "эволюции",
    "цифровая революция": "эволюция",
    "цифровой трансформации": "эволюции",
    "цифровая трансформация": "эволюция",
    "Equip it and feel the pride! ♪": "Надень и почувствуй гордость! ♪",
}

DIGIMON_CHAT_LINE_LIMIT = 70
DIGIMON_CHAT_WRAP_WIDTH = 68


def read_rows(path: Path) -> list[list[str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.reader(f))


def write_rows(path: Path, rows: list[list[str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, lineterminator="\n")
        writer.writerows(rows)


def package_name(root: Path) -> str:
    return root.name


def text_column(relative: str, row: list[str]) -> int:
    if relative.startswith("message/") and len(row) > 2:
        return 2
    return 1


def fix_message_speakers() -> list[str]:
    changed: list[str] = []
    for root in CSV_ROOTS:
        if not root.exists():
            continue
        for path in sorted((root / "message").glob("*.mbe/000_Sheet1.csv")):
            rows = read_rows(path)
            touched = False
            for row in rows:
                if len(row) < 3 or "_char_" not in row[0]:
                    continue
                expected = f"char_{row[0].rsplit('_char_', 1)[1]}"
                if row[1] and not row[1].startswith("char_"):
                    row[1] = expected
                    touched = True
                    changed.append(f"{path.relative_to(ROOT)}:{row[0]}->{expected}")
            if touched:
                write_rows(path, rows)
    return changed


def set_targeted_rows() -> list[str]:
    changed: list[str] = []
    for root in CSV_ROOTS:
        package = package_name(root)
        if not root.exists():
            continue
        by_file: dict[str, dict[str, str]] = {}
        for (relative, key), values in TARGETED_ROWS.items():
            if package in values:
                by_file.setdefault(relative, {})[key] = values[package]

        for relative, replacements in by_file.items():
            path = root / relative
            if not path.exists():
                continue
            rows = read_rows(path)
            touched = False
            for row in rows:
                if len(row) < 2:
                    continue
                value = replacements.get(row[0])
                if value is None:
                    continue
                index = text_column(relative, row)
                if len(row) <= index:
                    continue
                if row[index] != value:
                    row[index] = value
                    touched = True
                    changed.append(f"{package}/{relative}:{row[0]}")
            if touched:
                write_rows(path, rows)
    return changed


def replace_exact_text() -> list[str]:
    changed: list[str] = []
    for root in CSV_ROOTS:
        if not root.exists():
            continue
        for path in root.rglob("*.csv"):
            rows = read_rows(path)
            touched = False
            for row in rows:
                for index, value in enumerate(row):
                    new_value = value
                    for old, new in EXACT_REPLACEMENTS.items():
                        new_value = new_value.replace(old, new)
                    if new_value != value:
                        row[index] = new_value
                        touched = True
            if touched:
                write_rows(path, rows)
                changed.append(str(path.relative_to(ROOT)))
    return changed


def normalize_spaces(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def wrap_balanced_two_lines(text: str, width: int) -> str:
    flat = normalize_spaces(text)
    if len(flat) <= width:
        return flat

    words = flat.split(" ")
    best: tuple[int, str, str] | None = None
    for split_at in range(1, len(words)):
        left = " ".join(words[:split_at])
        right = " ".join(words[split_at:])
        if len(left) <= width and len(right) <= width:
            score = abs(len(left) - len(right))
            if best is None or score < best[0]:
                best = (score, left, right)
    if best is not None:
        return f"{best[1]}\n{best[2]}"

    lines: list[str] = []
    current = ""
    for word in words:
        candidate = word if not current else f"{current} {word}"
        if len(candidate) <= width:
            current = candidate
            continue
        if current:
            lines.append(current)
        current = word
    if current:
        lines.append(current)
    return "\n".join(lines)


def wrap_long_digimon_chat() -> list[str]:
    changed: list[str] = []
    for path in sorted((ROOT / "csv").glob("*/message/*digimon_chat*.mbe/000_Sheet1.csv")):
        rows = read_rows(path)
        touched = False
        for row in rows:
            if len(row) < 3 or not row[0] or row[0] == "string2 0":
                continue
            lines = row[2].splitlines() or [""]
            if max(len(line) for line in lines) <= DIGIMON_CHAT_LINE_LIMIT and len(lines) <= 2:
                continue
            wrapped = wrap_balanced_two_lines(row[2], DIGIMON_CHAT_WRAP_WIDTH)
            if wrapped != row[2]:
                row[2] = wrapped
                touched = True
                changed.append(f"{path.relative_to(ROOT)}:{row[0]}")
        if touched:
            write_rows(path, rows)
    return changed


def main() -> None:
    fixed_speakers = fix_message_speakers()
    changed_rows = set_targeted_rows()
    changed_files = replace_exact_text()
    wrapped_chat = wrap_long_digimon_chat()

    print(f"fixed_message_speakers={len(fixed_speakers)}")
    for item in fixed_speakers:
        print(f"  {item}")
    print(f"targeted_rows={len(changed_rows)}")
    for item in changed_rows:
        print(f"  {item}")
    print(f"exact_replacement_files={len(changed_files)}")
    for item in changed_files:
        print(f"  {item}")
    print(f"wrapped_digimon_chat_rows={len(wrapped_chat)}")
    for item in wrapped_chat:
        print(f"  {item}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Apply the contextual player/Operator, Digimon Chat, and generic-NPC pass.

Unlike a global pronoun replacement, every row in this pass is address-based
and source-checked.  Direct Player <-> Operator speech uses informal Russian;
plural speech to a group and genuinely plural Digimon remains plural.
"""

from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CSV_ROOT = ROOT / "csv"


UPDATES: dict[tuple[str, str, str], str] = {
    # Player <-> Operator: direct address is consistently informal.
    ("patch_text01", "message/battle.mbe/000_Sheet1.csv", "1011030004"): (
        "Этот противник явно сильнее других дигимонов...\n"
        "Тебе разрешено использовать {fc9кросс-арты}."
    ),
    ("patch_text01", "message/battle.mbe/000_Sheet1.csv", "1011030005"): (
        "Используй Дигивайс как катализатор: сфокусируй энергию\n"
        "своего дигимона в одной точке и высвободи её."
    ),
    ("patch_text01", "message/battle.mbe/000_Sheet1.csv", "1011030006"): (
        "Сумеешь ли ты завоевать доверие своих союзников,\n"
        "зависит только от тебя."
    ),
    ("patch_text01", "message/battle.mbe/000_Sheet1.csv", "1081020003"): (
        "Слушай внимательно, агент {player}. У меня есть результаты\n"
        "анализа твоей текущей ситуации."
    ),
    ("patch_text01", "message/battle.mbe/000_Sheet1.csv", "1081020009"): (
        "У тебя есть устройство от доктора Симмонс, которое генерирует\n"
        "специальную электромагнитную сеть, верно?"
    ),
    ("patch_text01", "message/d03.mbe/000_Sheet1.csv", "f_d0302_0230_0020"): (
        "Пожалуйста, продолжай собирать информацию."
    ),
    ("patch_text01", "message/d03.mbe/000_Sheet1.csv", "f_d0303_0040_0100"): (
        "Не исключай возможности ловушки и не теряй бдительности."
    ),
    ("patch_text01", "message/d10.mbe/000_Sheet1.csv", "f_d1001_0120_0040"): (
        "Все там в опасности! Тебе нужно поторопиться!"
    ),
    ("patch_text01", "message/d10.mbe/000_Sheet1.csv", "f_d1002_0030_0010"): (
        "Нет времени возвращаться. Направляйся к зданию правительства."
    ),
    ("patch_text01", "message/d10.mbe/000_Sheet1.csv", "f_d1003_0010_0010"): (
        "Что ты делаешь? Координаты цели указаны в другой стороне."
    ),
    ("patch_text01", "message/d10.mbe/000_Sheet1.csv", "f_d1003_0010_0020"): (
        "Используй способности своего дигимона-партнёра, чтобы\n"
        "устранить все препятствия на своём пути."
    ),
    ("patch_text01", "message/d10.mbe/000_Sheet1.csv", "f_d1003_0020_0020"): (
        "Это позволяет тебе приказать союзникам нанести упреждающий\n"
        "удар по враждебному дигимону. Продолжай. Попробуй."
    ),
    ("patch_text01", "message/d11.mbe/000_Sheet1.csv", "f_d1102_0120_0120"): (
        "Анализ местных каналов связи показал: доктор Симмонс\n"
        "находится на площади водопадов в парке Синдзюку. Сходи туда."
    ),
    ("patch_text01", "message/d11.mbe/000_Sheet1.csv", "f_d1102_0170_0020"): (
        "Согласно журналам, ты не впервые бываешь в этом акведуке.\n"
        "Должно быть, это было, когда связь не работала."
    ),
    ("patch_text01", "message/d11.mbe/000_Sheet1.csv", "f_d1102_0170_0040"): (
        "Я вижу поблизости возмущение магнитного поля. Это\n"
        "подозрительно. Я отмечу место на карте — сможешь всё проверить."
    ),
    ("patch_text01", "message/d14.mbe/000_Sheet1.csv", "f_d1401_0030_0010"): (
        "Ты пользуешься лестницей, чтобы подняться на крышу? Почему бы\n"
        "не воспользоваться лифтом?"
    ),
    ("patch_text01", "message/d14.mbe/000_Sheet1.csv", "f_d1401_0040_0020"): (
        "Твой Дигивайс использует электронные аспекты дигимонов, чтобы\n"
        "призвать их к действию."
    ),
    ("patch_text01", "message/d14.mbe/000_Sheet1.csv", "f_d1401_0060_0030"): (
        "Мы не можем это игнорировать. Отбрось здравый смысл.\n"
        "Аномалии всегда преподносят сюрпризы."
    ),
    ("patch_text01", "message/d14.mbe/000_Sheet1.csv", "f_d1401_0070_0010"): (
        "Сейчас тебе следует подняться на крышу\n"
        "правительственного здания."
    ),
    ("patch_text01", "message/d14.mbe/000_Sheet1.csv", "f_d1402_0030_0010"): (
        "У меня для тебя отчёт, агент. Для твоего Дигивайса доступно\n"
        "последнее обновление."
    ),
    ("patch_text01", "message/d14.mbe/000_Sheet1.csv", "f_d1402_0030_0020"): (
        "Теперь у тебя есть доступ к навыкам агента. Они здорово\n"
        "помогут в выполнении твоей миссии. Попробуй их в деле."
    ),
    ("patch_text01", "message/d14.mbe/000_Sheet1.csv", "f_d1403_0020_0020"): (
        "Он мгновенно сканирует твоё окружение и отмечает всё\n"
        "подозрительное. В этом помогают дигимоны из твоего Дигивайса."
    ),
    ("patch_text01", "message/d14.mbe/000_Sheet1.csv", "f_d1403_0020_0030"): (
        "Их зрение и обоняние помогают точно находить проблемные места.\n"
        "Полезная функция, если не знаешь, куда идти."
    ),
    ("patch_text01", "message/d14.mbe/000_Sheet1.csv", "f_d1405_0040_0050"): (
        "Возможно, у тебя уже есть несколько дигимонов, готовых\n"
        "к эволюции. Проверь свой Дигивайс и посмотри."
    ),
    ("patch_text01", "message/d14.mbe/000_Sheet1.csv", "f_d1406_0010_0050"): (
        "Возможно, у тебя уже есть несколько дигимонов, готовых\n"
        "к эволюции. Проверь свой Дигивайс и посмотри."
    ),
    ("patch_text01", "message/d14.mbe/000_Sheet1.csv", "f_d1407_0030_0010"): (
        "Держись! Впереди обнаружена аномалия!"
    ),
    ("patch_text01", "message/d14.mbe/000_Sheet1.csv", "f_d1407_0040_0010"): (
        "Обязательно восстанови своих дигимонов и подготовься ко всему,\n"
        "что произойдёт дальше!"
    ),
    ("patch_text01", "message/field_text.mbe/000_Sheet1.csv", "g_tutorial_1000_0020"): (
        "Как только прогресс сканирования достигнет 100%, ты сможешь\n"
        "конвертировать эти файлы в дигимона и добавить его в свой отряд."
    ),
    ("patch_text01", "message/field_text.mbe/000_Sheet1.csv", "g_tutorial_1000_0030"): (
        "Чем ближе прогресс сканирования к 200%, тем мощнее будет новый\n"
        "дигимон, поэтому не забудь выполнить конвертацию в нужное время."
    ),
    ("patch_text01", "message/field_text.mbe/000_Sheet1.csv", "g_tutorial_1000_0040"): (
        "Это также полезно для анализа аномалий, поэтому обязательно\n"
        "участвуй в боях, чтобы улучшать анализ и сканирование."
    ),
    ("patch_text01", "message/field_text.mbe/000_Sheet1.csv", "g_tutorial_1001_0010"): (
        "Похоже, дигимон уже достаточно хорошо проанализирован и готов\n"
        "к преобразованию. Попробуй функцию {fc9Конвертация} прямо сейчас."
    ),
    ("patch_text01", "message/field_text.mbe/000_Sheet1.csv", "g_tutorial_1001_0040"): (
        "Ты можешь узнать больше о личности каждого дигимона в разделе\n"
        "«Дигимоны» > «Настройка» своего Дигивайса."
    ),
    ("patch_text01", "message/field_text.mbe/000_Sheet1.csv", "g_tutorial_1001_0050"): (
        "Понимание индивидуальности каждого дигимона будет жизненно важно\n"
        "для успеха твоей миссии."
    ),
    ("patch_text01", "message/field_text.mbe/000_Sheet1.csv", "g_tutorial_1002_0010"): (
        "Я не могу предсказать, что тебя ждёт. Готовься к худшему\n"
        "и не забывай о {fc9Конвертации} и {fc9эволюции}."
    ),
    ("patch_text01", "message/field_text.mbe/000_Sheet1.csv", "g_tutorial_1002_0050"): (
        "Ты носишь фамилию «Юки» и лучше всех продолжишь его дело,\n"
        "так что освой в совершенстве {fc9Конвертацию} и {fc9эволюцию}!"
    ),
    ("patch_text01", "message/h03.mbe/000_Sheet1.csv", "f_h0301_0030_0010"): (
        "Значит, причина во враждебных дигимонах в подземелье Синдзюку?\n"
        "Здесь нет того, что нам нужно. Продолжай искать."
    ),
    ("patch_text01", "message/m010.mbe/000_Sheet1.csv", "m010_120_020"): (
        "Дигивайс активирован! Выполни программу призыва дигимона!"
    ),
    ("patch_text01", "message/m050.mbe/000_Sheet1.csv", "m050_040_020"): (
        "И, конечно, нельзя исключать,\n"
        "что и тебя перенесло во времени."
    ),
    ("patch_text01", "message/m050.mbe/000_Sheet1.csv", "m050_040_060"): (
        "Твой приёмный отец, доктор Юки, был вовлечён в один\n"
        "из таких инцидентов и—"
    ),
    ("patch_text01", "message/m050.mbe/000_Sheet1.csv", "m050_060_020"): (
        "Я анализирую данные, поступающие из твоего Дигивайса. Похоже,\n"
        "вернуться к исходной временной шкале будет непросто."
    ),
    ("patch_text01", "message/m050.mbe/000_Sheet1.csv", "m050_060_130"): (
        "У меня, конечно, нет доказательств. Никто раньше не пытался\n"
        "переписать прошлое. Нам остаётся только верить в тебя."
    ),
    ("patch_text01", "message/m110.mbe/000_Sheet1.csv", "m110_010_015"): (
        "С самого основания АДАМАСА наши учредители требовали\n"
        "секретности. Среди них был и твой приёмный отец, доктор Юки."
    ),
    ("patch_text01", "message/m110.mbe/000_Sheet1.csv", "m110_010_030"): (
        "Похоже, нельзя недооценивать доктора Монику Симмонс...\n"
        "Следи, чтобы случайно не выдать никаких сведений."
    ),
    ("patch_text01", "message/m110.mbe/000_Sheet1.csv", "m110_040_060"): (
        "Причина скопления враждебных дигимонов в подземелье Синдзюку\n"
        "может быть впереди. Продолжай расследование."
    ),
    ("patch_text01", "message/m120.mbe/000_Sheet1.csv", "m120_040_010"): (
        "Агент {player}... Только что удалось перехватить связь.\n"
        "Ты в мире дигимонов? Я правильно понимаю?"
    ),
    ("patch_text01", "message/m120.mbe/000_Sheet1.csv", "m120_040_110"): (
        "Одно это открытие гарантирует тебе повышение в АДАМАСЕ. Если,\n"
        "конечно, вернёшься без единой царапины..."
    ),
    ("patch_text01", "message/m120.mbe/000_Sheet1.csv", "m120_040_140"): (
        "Разлом появился над правительственным зданием во время Ада\n"
        "Синдзюку. Если он был связан с миром, где ты сейчас находишься..."
    ),
    ("patch_text01", "message/m120.mbe/000_Sheet1.csv", "m120_040_160"): (
        "Это становится самой важной миссией в истории АДАМАСА. Собирай\n"
        "как можно больше информации. От этого зависит будущее."
    ),
    ("patch_text01", "message/m120.mbe/000_Sheet1.csv", "m120_060_170"): (
        "Присылай мне любую полученную информацию, какой бы\n"
        "незначительной она ни казалась."
    ),
    ("patch_text01", "message/m120.mbe/000_Sheet1.csv", "m120_100_010"): (
        "Я анализирую полученные от тебя данные и, честно говоря,\n"
        "не нахожу слов."
    ),
    ("patch_text01", "message/m120.mbe/000_Sheet1.csv", "m120_100_030"): (
        "Полученные от тебя данные совпадают со многими записями в\n"
        "базе АДАМАСА о неопознанных мистических животных."
    ),
    ("patch_text01", "message/m120.mbe/000_Sheet1.csv", "m120_100_070"): (
        "Но для уверенности данных нужно больше. Собирай всё возможное."
    ),

    # Digimon Chat: the protagonist and a single Digimon speak informally.
    # These answers are not covered by the runtime gender resolver, so the
    # protagonist's own phrasing must also remain gender-neutral.
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "aigiog_001_1_replay"): "Давай сделаем оружие из всех этих шипов.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "aigiog_001_2_replay"): "Давай соберём лепестки для ванны.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "aigioh_001_1_replay"): "Не-а. Прости.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "loco_001_4_replay"): "Давай отправимся на край света!",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "yupira_001_1_replay"): "Перебор, если хочешь знать моё мнение.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "mine_001_1_replay"): "Пока можешь так думать.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "mine_001_2_replay"): "Тебя это не утомляет?",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "vulca_001_3_replay"): "Протянуть тебе руку помощи?",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "cere_001_4_replay"): "Давай искать вместе.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "zplu_001_4_replay"): "Пожалуйста, прояви немного сдержанности.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "omega_001_1_replay"): "Давай сражаться вместе.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "oga_001_2_replay"): "Тогда давай споём.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "puka_001_1_replay"): "Попробуй!",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "puka_001_2_replay"): "Давай придумаем стратегию.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "otama_001_1_replay"): "Продолжай в том же духе!",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "otama_001_4_replay"): "Просто пой от всего сердца!",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "syako_001_1_replay"): "Твои мощные атаки!",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "syako_001_2_replay"): "Твоя тактика, сбивающая врагов с толку!",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "kame_001_1_replay"): "Замени шлем на новый!",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "dago_001_4_replay"): "Тебя легко найти даже в темноте.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "shaw_001_1_replay"): "Почему бы нам не поискать эту твою реку?",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "shaw_001_2_replay"): "Тогда давай разберёмся, как очистить реки.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "mari_001_3_replay"): "Давай вместе придумаем, как это сделать.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "piyo_001_3_replay"): "Тебя ждут новые друзья!",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "piyo_001_4_replay"): "Давай выясним это вместе.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "flo_001_2_replay"): "Если пить воду понемногу, она лучше усваивается.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "aquila_001_2_replay"): "Твой ум — огромное подспорье.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "wood_001_4_replay"): "Итак, что же тебя восхищает?",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "wasp_001_1_replay"): "На тебя и правда можно положиться!",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "wasp_001_2_replay"): "Откуда такая бдительность?",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "wasp_001_4_replay"): "Спасибо, что так стараешься.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "garuda_001_1_replay"): "Прости за все эти хлопоты.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "garuda_001_2_replay"): "Тебе не кажется, что всё выглядит немного хаотично?",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "garuda_001_4_replay"): "Давай вместе охранять мир.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "tono_001_1_replay"): "Тебе явно нужно больше тренироваться.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "kuwa_001_2_replay"): "Твоя продуманная боевая стратегия.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "tyrant_001_2_replay"): "Значит, ты напрямую управляешь дигимонами-насекомыми?",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "pal_001_1_replay"): "Давай сиять ещё ярче!",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "pal_001_3_replay"): "Как у тебя с защитой от ультрафиолета?",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "hag_001_3_replay"): "Тебе не по себе?",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "gotsu_001_3_replay"): "Поиграй в пятнашки.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "aruma_001_1_replay"): "Переедать вредно.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "guard_001_2_replay"): "Давай сначала придумаем стратегию.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "ankylo_001_2_replay"): "Тебе трудно передвигаться?",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "mame_001_3_replay"): "Твой размер — часть очарования Мамемона!",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "andro_001_2_replay"): "Только не переусердствуй.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "hiand_001_1_replay"): "Конечно. Всегда держи его наготове.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "megag_001_3_replay"): "Давай попробуем совместную атаку.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "mera_001_1_replay"): "Давай вспыхнем вместе.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "mera_001_2_replay"): "Что подпитывает твой огонь?",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "mera_001_4_replay"): "Только осторожнее, не переусердствуй.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "gaoga_001_1_replay"): "Чего тебе ещё не хватает?",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "bear_001_1_replay"): "Давай устроим спарринг.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "bear_001_3_replay"): "Давай устроим гонку.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "shout_001_1_replay"): "Выкрути на полную.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "shout_001_4_replay"): "Споём дуэтом!",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "machg_001_3_replay"): "Не терпится увидеть, что ты с ними сделаешь.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "giza_001_4_replay"): "Наберись терпения.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "toko_001_2_replay"): "Я тебя поддерживаю!",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "ange_001_1_replay"): "Прости, не стоило брать твои закуски.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "tail_001_4_replay"): "Только не потеряй его!",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "uni_001_4_replay"): "Давай отправимся прямо сейчас!",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "holyan_001_4_replay"): "Вообще-то, следуй за мной.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "chiri_001_1_replay"): "И что именно ты с этим сделаешь?",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "chiri_001_2_replay"): "Но будь в этом смысл, ты бы так поступил?",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "claan_001_1_replay"): "Оставляю это на твоё усмотрение.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "ofa_001_1_replay"): "Я могу чем-нибудь тебе помочь?",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "ofa_001_2_replay"): "В чём твой долг?",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "serap_001_1_replay"): "Я могу чем-нибудь тебе помочь?",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "serap_001_2_replay"): "Разве это делает тебя выдающимся?",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "sola_001_2_replay"): "Ты Хагурумон?",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "agni_001_2_replay"): "Ты можешь сжигать мусор?",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "agni_001_3_replay"): "А пожары ты тоже умеешь тушить?",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "agni_001_4_replay"): "Ты можешь нагреть воду?",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "shakko_001_1_replay"): "Тогда оставляю это на твоё усмотрение.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "shakko_001_3_replay"): "Рассчитываю на твою защиту.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "shakko_001_4_replay"): "Большое тебе спасибо.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "houo_001_3_replay"): "Не очищай меня!",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "mumm_001_3_replay"): "Тебе не обязательно их чинить.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "viki_001_4_replay"): "Твой мех выглядит таким мягким и тёплым.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "raidora_001_2_replay"): "Давай побежим вместе!",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "ldevi_001_4_replay"): "Хитрую тактику оставляю тебе.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "asta_001_1_replay"): "Используй и то и другое.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "asta_001_4_replay"): "Не используй ни то ни другое.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "elec_001_2_replay"): "Сколько их у тебя?",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "gabe_001_1_replay"): "Продолжай убеждать всех быть бережливее.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "gabe_001_2_replay"): "Сортируй мой мусор и правильно сдавай его на переработку.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "gabe_001_3_replay"): "Давай вместе поищем вещи для повторного использования.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "deta_001_2_replay"): "Сначала изучи место и конкурентов.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "deta_001_4_replay"): "Ещё бы! Да я каждый день буду там есть!",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "monza_001_2_replay"): "Попробуй проанализировать их реакцию.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "guraleo_001_3_replay"): "Давай устроим спарринг!",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "belsta_001_2_replay"): "Обрати это прозвище себе на пользу.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "belsta_001_3_replay"): "Твой партнёр стоит прямо здесь.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "mgra_001_3_replay"): "Ты почти не изменился?",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "rapi_001_3_replay"): "Ты уверен, что это не «Кролик»?",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "lasty_001_2_replay"): "Нужно знать противника, с которым сталкиваешься.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "chaos_001_3_replay"): "Давай сыграем в карточную игру!",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "gabu_001_2_replay"): "Устрой конкурс викторин.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "gabu_001_3_replay"): "Предложи всем вместе нарисовать общую картину.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "omsha_001_1_replay"): "Ты двигаешься со скоростью света?",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "omsha_001_4_replay"): "Может, ты движешься слишком быстро, чтобы что-то разглядеть.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "wogra_001_2_replay"): "Обмани врагов, применив ложный манёвр.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "wogra_001_3_replay"): "Проведи совместную атаку с друзьями!",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "impe_001_2_replay"): "Всё зависит от того, как ты используешь силу.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "impe_001_3_replay"): "Друзья всегда помогут тебе держать себя в руках.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "exa_001_2_replay"): "И ум у тебя под стать размерам.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "jies_001_1_replay"): "Возглавь атаку!",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "jies_001_3_replay"): "Поддержи наших союзников.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "levi_001_2_replay"): "Ты достаточно силён, чтобы тебе завидовали?",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "magul_001_2_replay"): "Ты двигаешься со скоростью света?",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "mgulb_001_2_replay"): "А как же твоё оружие?",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "lokni_001_2_replay"): "Ты рассуждаешь неправильно.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "duna_001_4_replay"): "Тебе стоит больше ценить свою жизнь.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "duft_001_3_replay"): "Да ну? Расскажи о своих стратегиях...",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "duft_001_4_replay"): "Какой бы ни была твоя стратегия, можешь на меня рассчитывать.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "holyd_001_1_replay"): "Да, пожалуйста, сделай это.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "holyd_001_3_replay"): "Давай прольём этот свет вместе.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "lilis_001_3_replay"): "Давай вместе стремиться к большему.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "belfrm_001_2_replay"): "Если тебя это расстраивает, почему бы снова не лечь спать?",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "common005_2_replay"): "Из-за этого приходится больше беспокоиться.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "common007_2_replay"): "Из-за этого приходится больше беспокоиться.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "common023_1_replay"): "Тогда давай попробуем разобраться в некоторых из этих вещей.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "common026_2_replay"): "Это чувство замедлит тебя в бою.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "common039_1_replay"): "Так у тебя будет больше вариантов.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "common040_1_replay"): "Они пробуждают любопытство к разным вещам.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "common040_2_replay"): "От чтения тебя клонит в сон.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "common046_2_replay"): "Может, у тебя просто стало острее зрение.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "common048_1_replay"): "Твоя забота очень обнадёживает.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "common052_2_replay"): "«Бодрость и энергия» звучит старомодно, не находишь?",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "common055_2_replay"): "Ты точно так думаешь?",

    # Digimon Chat: gender-neutral protagonist answers (the chat table is not
    # hooked by the dynamic M/F resolver).
    ("addcont_01_text01", "message/digimon_chat_dlc01.mbe/000_Sheet1.csv", "omed_001_2_replay"): "Даже по твоей просьбе не соглашусь.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "chaos_001_2_replay"): "Мне пришлось прочитать уйму книг.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "guraleo_001_2_replay"): "Мне пришлось прочитать много книг.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "pal_001_2_replay"): "Должно быть, это помогает фотосинтезу.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "chiri_001_4_replay"): "С этим не поспоришь.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "duna_001_3_replay"): "Что ж, уважаю такую преданность.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "deta_001_3_replay"): "Мне бы тоже хотелось там работать!",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "claan_001_2_replay"): "Боюсь забыть запереть дверь.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "hawk_001_2_replay"): "Сначала выясню, что их беспокоит.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "hawk_001_3_replay"): "Постараюсь их подбодрить.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "hawk_001_4_replay"): "Просто обниму их!",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "levi_001_1_replay"): "Ох, зависть берёт.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "luna_001_1_replay"): "Это я тебя подбадриваю!",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "luna_001_4_replay"): "Я просто говорю: «Привет»!",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "magul_001_1_replay"): "С удовольствием на это посмотрю!",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "mgaob_001_3_replay"): "Во всяком случае, в планы это не входило.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "migao_001_2_replay"): "С удовольствием на это посмотрю!",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "mochi_001_1_replay"): "С удовольствием на это посмотрю!",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "mumm_001_2_replay"): "С удовольствием посмотрю, как это работает.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "octa_001_1_replay"): "Я не против поохотиться за сокровищами.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "omsha_001_3_replay"): "С удовольствием на это посмотрю!",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "rose_001_4_replay"): "Мне хотелось тебя найти, потому что ты мне нравишься.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "shaw_001_4_replay"): "Твоя река будет под моей защитой.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "tail_001_1_replay"): "Лучше не использовать его без необходимости.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "tyran_001_4_replay"): "Это даже не бросилось мне в глаза.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "uni_001_3_replay"): "Вот бы научиться летать.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "yuki_001_1_replay"): "С удовольствием поселюсь с тобой.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "bird_001_2_replay"): "Хочу научиться сохранять такое же спокойствие.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "luna_001_2_replay"): "Просто мысли вслух.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "ikka_001_4_replay"): "Толком не могу сказать.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "fuga_001_3_replay"): "Да, занимаюсь.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "chu_001_4_replay"): "Да, очень!",
    ("patch_text01", "message/m130.mbe/000_Sheet1.csv", "m130_010_100"): (
        "Странный квест тебе достался... Но если он поможет\n"
        "воссоединиться с Минервамон, сделка не так уж плоха."
    ),
    ("patch_text01", "message/m130.mbe/000_Sheet1.csv", "m130_010_120"): (
        "Если это принесёт новые сведения, время будет потрачено не зря.\n"
        "И всё же будь осторожнее, агент {player}."
    ),
    ("patch_text01", "message/m130.mbe/000_Sheet1.csv", "m130_100_150"): (
        "Титаны, говоришь...? Похоже, дигимоны воюют между собой."
    ),
    ("patch_text01", "message/m130.mbe/000_Sheet1.csv", "m130_100_190"): (
        "Мы, возможно, приближаемся к истине. Постарайся\n"
        "выяснить как можно больше в этом мире."
    ),
    ("patch_text01", "message/m140.mbe/000_Sheet1.csv", "m140_010_430"): (
        "Агент {player}, помни, что произошло во время Ада Синдзюку."
    ),
    ("patch_text01", "message/m140.mbe/000_Sheet1.csv", "m140_020_070"): (
        "Например, твой приёмный отец, доктор Юки, бесследно\n"
        "исчез из этого мира."
    ),
    ("patch_text01", "message/m140.mbe/000_Sheet1.csv", "m140_020_090"): (
        "Продолжай внимательно наблюдать за этим миром. Шансы найти\n"
        "кого-то из пропавших всё ещё есть."
    ),
    ("patch_text01", "message/m140.mbe/000_Sheet1.csv", "m140_100_080"): (
        "Мне жаль, но придётся попросить тебя поторопиться. Время\n"
        "нашего мира на исходе."
    ),
    ("patch_text01", "message/m150.mbe/000_Sheet1.csv", "m150_070_440"): (
        "Как только наши запасы иссякнут, всему конец... Тебе нужно\n"
        "переписать будущее до того, как это случится."
    ),
    ("patch_text01", "message/m150.mbe/000_Sheet1.csv", "m150_160_130"): (
        "Не сомневайся. Тот аномальный инцидент произошёл из-за того,\n"
        "что конфликт дигимонов достиг точки кипения."
    ),
    ("patch_text01", "message/m150.mbe/000_Sheet1.csv", "m150_160_150"): (
        "...Помни об этом, ладно, агент {player}?"
    ),
    ("patch_text01", "message/m170.mbe/000_Sheet1.csv", "m170_010_040"): (
        "Мы проверили полученную от тебя информацию и, как уже\n"
        "упоминалось, выдвинули одну теорию."
    ),
    ("patch_text01", "message/m170.mbe/000_Sheet1.csv", "m170_010_080"): (
        "Твоё расследование раскроет правду об этом мире и, возможно,\n"
        "поможет найти выход из кризиса через восемь лет."
    ),
    ("patch_text01", "message/m170.mbe/000_Sheet1.csv", "m170_010_090"): (
        "Верить в это — наш единственный выход.\n"
        "Я рассчитываю на тебя, агент {player}."
    ),
    ("patch_text01", "message/m170.mbe/000_Sheet1.csv", "m170_070_080"): (
        "Если так, то происходящее сейчас похоже на ужасное событие\n"
        "в мире людей восемь лет спустя..."
    ),
    ("patch_text01", "message/m170.mbe/000_Sheet1.csv", "m170_070_090"): (
        "...возможно, это не простое совпадение. Помни об этом,\n"
        "исследуя местность."
    ),
    ("patch_text01", "message/m170.mbe/000_Sheet1.csv", "m170_070_100"): (
        "Имей это в виду, исследуя местность. Я сделаю всё возможное\n"
        "для анализа полученных данных."
    ),
    ("patch_text01", "message/m170.mbe/000_Sheet1.csv", "m170_150_110"): (
        "Но это значит, что надежда ещё есть. Ты можешь помешать\n"
        "этому случиться."
    ),
    ("patch_text01", "message/m180.mbe/000_Sheet1.csv", "m180_110_060"): (
        "Там должны быть ключи к разгадке истины.\n"
        "Продолжай копать, агент {player}."
    ),
    ("patch_text01", "message/m200.mbe/000_Sheet1.csv", "m200_020_100"): (
        "Что ж! Похоже, возвращение в мир людей прошло успешно. Но вместе\n"
        "с тобой появились эти враждебные «Титаны»."
    ),
    ("patch_text01", "message/m200.mbe/000_Sheet1.csv", "m200_020_130"): (
        "Не сомневайся. Это аномальное явление."
    ),
    ("patch_text01", "message/m200.mbe/000_Sheet1.csv", "m200_020_140"): (
        "Но... именно для этого наша организация и существует. Во имя\n"
        "чести АДАМАСА уничтожь эту угрозу в зародыше!"
    ),
    ("patch_text01", "message/m210.mbe/000_Sheet1.csv", "m210_060_030"): (
        "Пространственно-временное возмущение быстро растёт! Оставаться\n"
        "на твоём текущем месте опасно! Убирайся оттуда!"
    ),
    ("patch_text01", "message/m230.mbe/000_Sheet1.csv", "m230_010_120"): (
        "Так с тобой всё в порядке... Какое облегчение!"
    ),
    ("patch_text01", "message/m230.mbe/000_Sheet1.csv", "m230_010_130"): (
        "Похоже, путешествие во времени прошло без последствий.\n"
        "Есть какие-нибудь физические недомогания?"
    ),
    ("patch_text01", "message/m230.mbe/000_Sheet1.csv", "m230_010_140"): (
        "Нет? Хорошо. Теперь я расскажу тебе о явлениях,\n"
        "которые наблюдаю."
    ),
    ("patch_text01", "message/m230.mbe/000_Sheet1.csv", "m230_010_150"): (
        "Во-первых, ты находишься в Синдзюку до Ада — на восемь лет\n"
        "позже того момента, откуда началось путешествие."
    ),
    ("patch_text01", "message/m230.mbe/000_Sheet1.csv", "m230_010_160"): (
        "Твоя временная ось немного рассинхронизирована с моей:\n"
        "в моём мире Ад Синдзюку уже произошёл."
    ),
    ("patch_text01", "message/m230.mbe/000_Sheet1.csv", "m230_010_170"): (
        "Короче говоря, до полного возвращения домой ещё далеко. Но,\n"
        "в любом случае..."
    ),
    ("patch_text01", "message/m230.mbe/000_Sheet1.csv", "m230_010_180"): (
        "...твой приказ предотвратить Ад Синдзюку остаётся в силе. Я всё\n"
        "ещё рассчитываю на тебя, агент {player}!"
    ),
    ("patch_text01", "message/m240.mbe/000_Sheet1.csv", "m240_020_170"): (
        "Похоже, ты в ситуации «пан или пропал»."
    ),
    ("patch_text01", "message/m240.mbe/000_Sheet1.csv", "m240_020_210"): (
        "И ты находишься прямо в его эпицентре."
    ),
    ("patch_text01", "message/m240.mbe/000_Sheet1.csv", "m240_020_220"): (
        "Тебе нужно положить конец этой войне. Сделай всё, что в твоих\n"
        "силах, чтобы добиться перемирия между тремя сторонами."
    ),
    ("patch_text01", "message/m285.mbe/000_Sheet1.csv", "m285_030_140"): (
        "Своего рода «богоподобная сила», если хочешь."
    ),
    ("patch_text01", "message/m285.mbe/000_Sheet1.csv", "m285_030_160"): (
        "Тебе лучше пристально следить за этим дигимоном\n"
        "по имени Эгиомон..."
    ),
    ("patch_text01", "message/m285.mbe/000_Sheet1.csv", "m285_040_070"): (
        "Разве ты не видишь, как ужасно было бы, если бы кто-то мог\n"
        "так манипулировать историей?"
    ),
    ("patch_text01", "message/m285.mbe/000_Sheet1.csv", "m285_040_080"): (
        "Представь: в один миг человек существует... А в следующий —\n"
        "пуф! Как будто его никогда и не было."
    ),
    ("patch_text01", "message/m285.mbe/000_Sheet1.csv", "m285_040_090"): (
        "Я предлагаю тебе уже сейчас продумать наихудшие сценарии,\n"
        "пока ещё можешь..."
    ),
    ("patch_text01", "message/m310.mbe/000_Sheet1.csv", "m310_010_160"): (
        "Встанет ли он на сторону добра или зла? Если последнее... тогда\n"
        "другого выхода не останется: придётся устранить его."
    ),
    ("patch_text01", "message/m340.mbe/000_Sheet1.csv", "m340_020_095"): (
        "Уклоняясь от сил общественной безопасности, ты разлучаешься с\n"
        "Эгиомоном. Тебе каким-то образом удаётся выбраться на поверхность..."
    ),
    ("patch_text01", "message/m340.mbe/000_Sheet1.csv", "m340_020_096"): (
        "Осторожнее. Твои текущие координаты находятся на уровне\n"
        "земли внутри Стены. Возможно, это Район дигимонов."
    ),
    ("patch_text01", "message/m340.mbe/000_Sheet1.csv", "m340_020_140"): (
        "Это означает устранение наиболее вероятного источника аномалии.\n"
        "Немедленно отправляйся и ликвидируй Эгиомона и Инори Мисоно."
    ),
    ("patch_text01", "message/m340.mbe/000_Sheet1.csv", "m340_020_150"): (
        "Пожалуйста, просто дай нам ещё немного времени!{next}"
    ),
    ("patch_text01", "message/m340.mbe/000_Sheet1.csv", "m340_020_250"): (
        "А пока... сделай всё возможное, чтобы предотвратить Ад\n"
        "Синдзюку!"
    ),
    ("patch_text01", "message/s910_169.mbe/000_Sheet1.csv", "s910_169_650"): (
        "Как и предполагалось, сигнал Хироко улавливается дальше.\n"
        "Продолжай двигаться этим курсом."
    ),
    ("patch_text01", "message/t01.mbe/000_Sheet1.csv", "f_t0108_0020_0060"): (
        "Калибровка проходит хорошо. Пожалуйста, двигайся к финальной\n"
        "точке."
    ),
    ("patch_text01", "message/t03.mbe/000_Sheet1.csv", "f_t0302_0130_0020"): (
        "Я посмотрю, что смогу о ней выяснить. Свяжусь с тобой, как\n"
        "только что-нибудь узнаю, так что жди."
    ),
    ("patch_text01", "message/t03.mbe/000_Sheet1.csv", "f_t0302_0170_0010"): (
        "Хорошая работа. Калибровка завершена, и теперь мы можем\n"
        "с высокой точностью определять твои координаты."
    ),
    ("patch_text01", "message/t03.mbe/000_Sheet1.csv", "f_t0302_0170_0020"): (
        "Вокруг говорят об аномальных явлениях, верно? Я\n"
        "снова просматриваю посты в интернете восьмилетней давности."
    ),
    ("patch_text01", "message/t03.mbe/000_Sheet1.csv", "f_t0302_0170_0030"): (
        "Похоже, слухи об аномалиях в Синдзюку начались примерно\n"
        "в то время, куда тебя занесло. Совпадение?"
    ),
    ("patch_text01", "message/t03.mbe/000_Sheet1.csv", "f_t0302_0170_0050"): (
        "Так что это твоя следующая миссия. Направляйся в этот переулок\n"
        "в Кабукитё, Синдзюку."
    ),
    ("patch_text01", "message/t03.mbe/000_Sheet1.csv", "f_t0304_0020_0010"): (
        "Не годится. Тебя окружают бесчисленные мощные сигналы. Найди\n"
        "другой маршрут. Откуда вообще эти дигимоны?"
    ),
    ("patch_text01", "message/t03.mbe/000_Sheet1.csv", "f_t0304_0020_0020"): (
        "Мир вокруг тебя определённо полон более враждебных\n"
        "дигимонов, чем тот, который я знаю."
    ),
    ("patch_text01", "message/t03.mbe/000_Sheet1.csv", "f_t0304_0020_0090"): (
        "Хочешь знать, почему у меня такая дикая теория?"
    ),
    ("patch_text01", "message/t03.mbe/000_Sheet1.csv", "f_t0304_0020_0110"): (
        "Впереди многочисленные сигналы враждебных дигимонов. Найди\n"
        "другой маршрут!"
    ),
    ("patch_text01", "message/t03.mbe/000_Sheet1.csv", "f_t0304_0030_0010"): (
        "Район содержания дигимонов службы общественной безопасности...\n"
        "Впереди много врагов. Найди другой путь!"
    ),
    ("patch_text01", "message/t03.mbe/000_Sheet1.csv", "f_t0304_0030_0020"): (
        "Мир вокруг тебя определённо полон более враждебных\n"
        "дигимонов, чем тот, который я знаю."
    ),
    ("patch_text01", "message/t03.mbe/000_Sheet1.csv", "f_t0304_0040_0040"): (
        "Хочешь знать, почему у меня такая дикая теория?"
    ),
    ("patch_text01", "message/t03.mbe/000_Sheet1.csv", "f_t0304_0040_0060"): (
        "Впереди многочисленные сигналы враждебных дигимонов. Найди\n"
        "другой маршрут!"
    ),
    ("patch_text01", "message/t04.mbe/000_Sheet1.csv", "f_t0404_0240_0010"): (
        "В систему добавлена функция, усиливающая синергию\n"
        "с твоим дигимоном-партнёром и укрепляющая связь между вами."
    ),
    ("patch_text01", "message/t04.mbe/000_Sheet1.csv", "f_t0404_0240_0030"): (
        "Навыки агента улучшаются по мере твоего прогресса, позволяя\n"
        "ускорять эволюцию и усиливать способности кросс-артов."
    ),
    ("patch_text01", "message/t04.mbe/000_Sheet1.csv", "f_t0404_0240_0040"): (
        "Освой эту функцию и используй её для выполнения\n"
        "своих миссий."
    ),

    # Digimon Chat: source-confirmed single-Digimon lines missed by the
    # first outbound T/V candidate scan (including DLC tables).
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "panja_001_4_replay"): (
        "Было бы здорово, если бы ты меня согрел!"
    ),
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "megas_001_2_replay"): (
        "Было бы ещё лучше, если бы ты за ним ухаживал."
    ),
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "toge_001_3_replay"): (
        "А как тебе такая забавная рожица?"
    ),
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "banleo_001_3_replay"): (
        "Давай сражаться, пока не достигнем взаимопонимания."
    ),
    ("addcont_02_text01", "message/digimon_chat_dlc02.mbe/000_Sheet1.csv", "banma_001_3_replay"): (
        "Ты и так делаешь более чем достаточно."
    ),
    ("addcont_03_text01", "message/digimon_chat_dlc03.mbe/000_Sheet1.csv", "mugx_001_3_replay"): (
        "Давай тренироваться вместе!"
    ),
}


# Digimon Chat: Digimon -> protagonist.  Every ID below was checked against
# the English source in its one-on-one chat context.  The protagonist remains
# gender-neutral because this table is not handled by the runtime M/F hook.
DIGIMON_CHAT_INBOUND_UPDATES: dict[tuple[str, str, str], str] = {
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "aigioh_001_3_reaction_char_AEGIOCHUSMON_HOLLY"): "Значит, ты всё-таки сомневаешься?\nЯ помогу тебе избавиться от неуверенности.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "Seire_001_0_char_SIRENMON"): "Что тебе больше нравится: птицы или рыбы?",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "Seire_001_1_reaction_char_SIRENMON"): "Так ты не из моих поклонников?\nУслышишь мою песню — и сразу изменишь мнение.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "Seire_001_2_reaction_char_SIRENMON"): "Любишь море? Тогда тебе понравится петь в океанских глубинах —\nэто невероятное ощущение.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "Seire_001_4_reaction_char_SIRENMON"): "Тогда позволь мне спеть тебе с небес\nсеренаду своей птичьей трелью.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "loco_001_3_reaction_char_LOCOMON"): "Далеко ли, близко ли — обещаю тебе\nплавное и приятное путешествие.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "yupira_001_1_reaction_char_JUPITERMON_WRATHMODE"): "Очевидно, твоё суждение ошибочно. Я лишь хладнокровно решаю,\nнасколько суровым должно быть наказание.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "yupira_001_4_reaction_char_JUPITERMON_WRATHMODE"): "Именно! Похоже, ты понимаешь,\nкакое хладнокровие скрывается за моим гневом.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "mars_001_1_reaction_char_MARSMON"): "Мои победы защищают мир в Цифровом мире.\nМне очень пригодится и твоя помощь!",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "mars_001_2_reaction_char_MARSMON"): "Я защищаю Цифровой мир,\nтак что твои доводы здесь не работают. Победа — это всё.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "mel_001_2_reaction_char_MERCURYMON"): "Тебе может так показаться, но мне по душе жизнь странника.\nВ ней есть свои прелести.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "nep_001_4_reaction_char_NEPTUNEMON"): "Я ценю твои чувства, но это мой долг.\nИ всё же давай работать вместе.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "venus_001_2_reaction_char_VENUSMON"): "Смотрю я на тебя намеренно или нет,\nвсё равно замечаю каждую твою черту.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "yuno_001_2_reaction_char_JUNOMON"): "Мне приятно это слышать.\nИ всё же интересно, на чём основаны твои слова...",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "yuno_001_3_reaction_char_JUNOMON"): "Такой ответ беспокоит меня ещё сильнее. Но я ценю твою доброту.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "yunoh_001_2_reaction_char_JUNOMON_HYSTERICMODE"): "Но подумай: какой смысл в красоте,\nесли нельзя встретиться с тем, кого любишь?",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "yunoh_001_3_reaction_char_JUNOMON_HYSTERICMODE"): "По крайней мере, постараюсь не доставить тебе неприятностей.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "cere_001_3_reaction_char_CERESMON"): "Я ценю твою мысль, но ищу по-настоящему чарующий голос,\nа не обычное человеческое пение.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "cerem_001_2_reaction_char_CERESMON_MEDIUM"): "Да, похоже на то.\nЗначит, вот как выглядит настоящее довольство.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "pluto_001_1_reaction_char_PLUTOMON"): "Избыток лести тебя погубит.\nУжас и насилие должны внушать должный страх.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "gnov_001_0_char_GRACENOVAMON"): "Интересуешься путешествиями по галактике?",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "gnov_001_1_reaction_char_GRACENOVAMON"): "Устреми мысли к новым мирам —\nи однажды твои мечты станут реальностью.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "gnov_001_2_reaction_char_GRACENOVAMON"): "Сверхпространство внутри меня трудно описать,\nно оно покажет тебе новые миры.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "gnov_001_3_reaction_char_GRACENOVAMON"): "Галактика Цифрового мира может\nотличаться от твоей, но я помогу тебе.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "gnov_001_4_reaction_char_GRACENOVAMON"): "Так ты говоришь, но я и есть галактика.\nЗначит, твоё путешествие уже началось.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "gloco_001_2_reaction_char_GROUNDLOCOMON"): "Я хочу пройти всю Сеть из конца в конец\nи показать тебе весь Цифровой мир!",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "omega_001_1_reaction_char_OMEGAMON"): "Похоже, твоя решимость окрепла.\nТеперь мы товарищи, и наши сердца и помыслы едины.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "omega_001_2_reaction_char_OMEGAMON"): "Битвы ради искоренения зла не избежать,\nно я с радостью выслушаю любой твой план.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "omega_001_3_reaction_char_OMEGAMON"): "Тебе тоже довелось увидеть немало кровавых битв.\nКогда-нибудь я хотел бы услышать твои истории.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "omega_001_4_reaction_char_OMEGAMON"): "Предлагаю отбросить браваду.\nЛучше позволь мне поддержать то, к чему стремится твоё сердце.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "gob_001_1_reaction_char_GOBURIMON"): "...Ч-что?! Может, до тебя ещё не дошло:\nнужно мужество, чтобы понять, когда пора бежать!",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "chro_001_3_reaction_char_CHRONOMON"): "Так ты это воспринимаешь?\nВозможно, всё дело в моём взгляде на вещи...",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "chro_001_4_reaction_char_CHRONOMON"): "Боюсь, ты просто пытаешься меня утешить,\nно я ценю твою поддержку.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "chdes_001_0_char_CHRONOMON_DESTROY"): "Веришь в судьбу или, быть может, в предначертание?",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "chdes_001_4_reaction_char_CHRONOMON_DESTROY"): "И что ты будешь с этим делать?\nЕсли решишь сопротивляться, я хотел бы помочь.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "hoe_001_4_reaction_char_WHAMON"): "Эти слова облегчают боль лучше любого лекарства.\nСпасибо тебе за доброту.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "shaw_001_1_reaction_char_SHAWUJINMON"): "Звучит здорово! Пожалуй, я и правда приму твоё предложение.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "presi_001_0_char_PLESIOMON"): "Позволь мне услышать о твоих амбициях.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "presi_001_4_reaction_char_PLESIOMON"): "Хм. Если таково твоё желание — пусть будет так.\nЯ такую цель не осуждаю.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "bab_001_3_reaction_char_BUBBMON"): "Угадано! Теперь придётся лепетать вместе со мной!\nГугу! Давай! Давай споём! Гага!",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "bab_001_4_reaction_char_BUBBMON"): "Угадано! А теперь скажи: «Боль, боль, уходи!» Гугу!",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "pyoko_001_1_reaction_char_PYOCOMON"): "Я эволюционирую в форму, прекрасную,\nкак цветы твоего мира. Вот увидишь!",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "tane_001_1_reaction_char_TANEMON"): "Как грубо. Он не сухой, а полон жизненной силы!\nТебе не помешало бы у него поучиться!",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "tane_001_3_reaction_char_TANEMON"): "Не могу тебе сказать, но это наверняка станет\nключом к моей эволюции! Следи за мной внимательно!",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "tane_001_4_reaction_char_TANEMON"): "О, как это мило! Но не волнуйся:\nмоя эволюция в любом случае будет прекрасна!",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "hawk_001_0_char_HAWKMON"): "Как поступишь, если встретишь кого-нибудь в беде?",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "hawk_001_3_reaction_char_HAWKMON"): "Все мы иногда попадаем в беду.\nНеудивительно, что тебе хочется их утешить.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "hawk_001_4_reaction_char_HAWKMON"): "К-какие крайние меры...!\nНо, пожалуй, так твои намерения будут понятнее всего...",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "lala_001_1_reaction_char_LALAMON"): "О да! В эту песню вложено всё моё мужество.\nКак приятно, что она нашла в тебе отклик!",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "aquila_001_0_char_AQUILAMON"): "Интересно... Как тебе моё выступление?",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "aquila_001_1_reaction_char_AQUILAMON"): "Какая доброта! Я и дальше буду выкладываться ради тебя!",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "aquila_001_3_reaction_char_AQUILAMON"): "Спасибо! Для меня большая честь, что ты считаешь меня ровней!",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "wasp_001_2_reaction_char_WASPMON"): "Почему, спрашиваешь...? Наверное, дело в привычке.\nМне стоит чаще думать своей головой.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "garuda_001_2_reaction_char_GARUDAMON"): "Так тебе кажется? Что ж, мне тоже стоит это обдумать.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "garuda_001_4_reaction_char_GARUDAMON"): "Такие чувства можно только приветствовать.\nУверен, тебе многое по силам.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "atlaka_001_0_char_ATLURKABUTERIMON"): "У меня вопрос: что ты хочешь защитить?",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "atlaka_001_2_reaction_char_ATLURKABUTERIMON"): "Без воспоминаний исчезнет всё,\nчто делало тебя собой... Страшная мысль.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "jure_001_0_char_JYUREIMON"): "Прошу тебя защищать и беречь этот густой зелёный лес.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "jure_001_2_reaction_char_JYUREIMON"): "Твои познания в этом вопросе обнадёживают меня —\nпока они не становятся чрезмерными.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "lyla_001_1_reaction_char_LILAMON"): "На твоём месте я бы не относилась к этому так легкомысленно.\nОсторожнее: не дай красоте сбить тебя с пути.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "lyla_001_3_reaction_char_LILAMON"): "Прости, но я не согласна. Будем надеяться,\nчто эти слова ещё не вернутся к тебе бумерангом.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "lili_001_0_char_LILLYMON"): "Скажи, как я выгляжу с твоей точки зрения?",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "lili_001_4_reaction_char_LILLYMON"): "Спасибо! Надеюсь, ты будешь всё больше на меня полагаться.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "herac_001_4_reaction_char_HERCULESKABUTERIMON"): "Согласен. Или один может быть у тебя,\nа другой — у твоего друга. Было бы жаль остаться без обоих.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "syuri_001_2_reaction_char_SHURIMON"): "От этого мало пользы, если ты не умеешь вытягивать конечности,\nкак я. Но всё же смотри!",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "kuwa_001_4_reaction_char_KUWAGAMON"): "Чтобы защищать тех, кто нуждается в защите,\nтебе нужно самое сильное сердце на свете.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "tyrant_001_3_reaction_char_TYRANTKABUTERIMON"): "Конечно. Для тебя должно быть честью иметь\nсреди друзей такого доблестного воина.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "roto_001_1_reaction_char_LOTOSMON"): "Не заставляй себя.\nЯ всё равно приглашу тебя в благословенный мир иллюзий.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "pal_001_2_reaction_char_PALMON"): "Ага. Надеюсь, благодаря мне тебе\nдостанется море свежего кислорода!",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "pal_001_4_reaction_char_PALMON"): "Тебя эта мысль может ужасать, но меня — нет.\nСтолько солнца означает прекрасный фотосинтез!",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "roseb_001_2_reaction_char_ROSEMON_BM"): "Сначала хорошо подумай,\nчто нужно для исполнения этого ненасытного желания.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "metma_001_3_reaction_char_METALMAMEMON"): "Можешь взглянуть поближе, если хочешь!",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "andro_001_3_reaction_char_ANDROMON"): "Я ОСТАВЛЮ ЭТИ СИТУАЦИИ НА ТВОЁ УСМОТРЕНИЕ.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "muged_001_3_reaction_char_MUGENDRAMON"): "ЕСЛИ ТЫ ПРИМЕШЬ МЕНЯ, Я ВСЕГДА БУДУ\nОКАЗЫВАТЬ ТЕБЕ СВОЮ НЕПОКОЛЕБИМУЮ ПОДДЕРЖКУ.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "megag_001_1_reaction_char_MEGAGROWLMON"): "Просто полетать? Спорим, стоит тебе подняться в воздух,\nкак сразу захочется подраться.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "ulbra_001_3_reaction_char_ULTIMATEBRAKIMON"): "Если я стану ещё больше, двигаться будет трудно.\nНо с твоей поддержкой, возможно, справлюсь.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "parrot_001_0_char_PARROTMON"): "Какой цвет тебе больше нравится:\nкрасный, синий, жёлтый или зелёный?",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "panja_001_1_reaction_char_PANJYAMON"): "Тогда тебе стоит тренироваться на полярном морозе.\nНаверняка скоро привыкнешь.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "panja_001_2_reaction_char_PANJYAMON"): "Главное — убедись, что сможешь повторить\nэто даже на арктическом морозе.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "panja_001_4_reaction_char_PANJYAMON"): "Если ты предлагаешь согреться\nсовместной разминкой, я с удовольствием!",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "machg_001_4_reaction_char_MACHGAOGAMON"): "Я ценю твою заботу. Не терпится их продемонстрировать!",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "tyran_001_4_reaction_char_TYRANNOMON"): "Наверное, в бою это неважно.\nИ всё же уделяй этому больше внимания...",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "aird_001_2_reaction_char_AIRDRAMON"): "Мы с тобой по-разному понимаем слово «далеко»,\nтак что сначала стоит определиться.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "kuda_001_2_reaction_char_KUDAMON"): "Я сам выбираю, кого катать, спасибо.\nА буду ли катать тебя — ещё вопрос.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "ange_001_1_reaction_char_ANGEMON"): "Хвалю за смелость признаться. Но больше никогда так не делай.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "ange_001_2_reaction_char_ANGEMON"): "Если тебе хватает хитрости,\nвообще не стоило связываться со злом.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "tail_001_1_reaction_char_TAILMON"): "Если всё останется спокойно, тебе, вероятно,\nне придётся этого делать. Но добиться мира ещё труднее.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "angew_001_1_reaction_char_ANGEWOMON"): "Я хочу видеть тебя во главе наших усилий.\nПоэтому именно я должна тебе помогать.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "holyan_001_0_char_HOLYANGEMON"): "Я иду путём праведности. Пойдёшь ли ты по нему вместе со мной?",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "holyan_001_1_reaction_char_HOLYANGEMON"): "Тогда я настаиваю, чтобы мы прошли этот путь вместе.\nНачни с преодоления собственных страхов.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "holyan_001_2_reaction_char_HOLYANGEMON"): "Если твоя решимость тверда, путь вперёд откроется.\nТогда и начнётся обучение!",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "holyan_001_4_reaction_char_HOLYANGEMON"): "Я надеялся, что однажды ты возьмёшь на себя инициативу.\nРад, что этот день настал.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "knight_001_0_char_KNIGHTMON"): "Клянусь тебе в верности, мой сеньор.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "knight_001_3_reaction_char_KNIGHTMON"): "Я должен быть предан своему сеньору.\nМне незачем претендовать на твоё место.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "glade_001_1_reaction_char_GRADEMON"): "Я предпочитаю сам быть в авангарде,\nно для тебя могу сделать исключение.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "glade_001_2_reaction_char_GRADEMON"): "Мне не терпится увидеть, какую стратегию ты разработаешь.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "glade_001_3_reaction_char_GRADEMON"): "Когда Золотой Метеор ринется вперёд,\nты увидишь фехтование невиданной скорости.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "claan_001_0_char_CLAVISANGEMON"): "Не забудь всё запереть.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "claan_001_1_reaction_char_CLAVISANGEMON"): "Я должен охранять Врата Зенита.\nА запирать собственные двери — твоя ответственность.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "claan_001_2_reaction_char_CLAVISANGEMON"): "Всегда перепроверяй. А ещё лучше — подтверждай вслух.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "claan_001_4_reaction_char_CLAVISANGEMON"): "Я справлюсь с охраной Врат Зенита в одиночку.\nНо ценю твою заботу.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "ofa_001_1_reaction_char_OPHANIMON"): "Меня порадует, если ты расскажешь всему\nЦифровому миру о моей любви и милосердии.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "pega_001_3_reaction_char_PEGASMON"): "Лучше не делай этого без причины.\nНо ради правого дела я соглашусь.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "pega_001_4_reaction_char_PEGASMON"): "Уверяю тебя, это рефлекс.\nХотя, возможно, твоё особое присутствие его подавит?",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "nefe_001_4_reaction_char_NEFERTIMON"): "Другие люди говорили то же самое —\nи тоже были загипнотизированы. Та же участь ждёт и тебя.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "mug_001_0_char_MAGNAMON"): "Веришь в чудеса?",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "mug_001_1_reaction_char_MAGNAMON"): "Если захочешь преодолеть какую-либо трудность,\nдоверься мне — я помогу пройти до конца.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "mug_001_3_reaction_char_MAGNAMON"): "Сила чудес реальна.\nНикогда не сдавайся, какой бы тяжёлой ни была ситуация.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "bird_001_0_char_BIRDRAMON"): "Я могу что-нибудь для тебя сделать?",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "bird_001_1_reaction_char_BIRDRAMON"): "Сила духа рождается внутри,\nтак что с этой задачей справишься только ты.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "agni_001_3_reaction_char_AGNIMON"): "Это непростая просьба...\nНо даю слово: я потушу любой устроенный мной пожар.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "agni_001_4_reaction_char_AGNIMON"): "Я могу нагреть что угодно. Захочешь горячей воды — она будет.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "vuli_001_3_reaction_char_VRITRAMON"): "После лазера, способного соперничать с солнцем,\nна его пути ничего не останется! Поверь мне.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "shakko_001_4_reaction_char_SHAKKOUMON"): "Я РАД ПОЛУЧИТЬ ТВОЮ БЛАГОДАРНОСТЬ.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "houo_001_2_reaction_char_HOUOUMON"): "Я не могу позволить злу процветать! И всё же давай\nвместе выберем лучшее время для твоего очищения...",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "houo_001_3_reaction_char_HOUOUMON"): "Тебя мучает совесть?\nТогда тем более нужно что-то с этим делать!",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "houo_001_4_reaction_char_HOUOUMON"): "Когда придёт время, я мигом очищу тебя от зла.\nВыбор момента оставь мне.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "megi_001_2_reaction_char_MEGIDRAMON"): "Не понимаю, что тут можно понять неправильно.\nНикогда не недооценивай силу тьмы.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "yuki_001_2_reaction_char_YUKIDARUMON"): "Надеюсь, ты увидишь, за что я люблю жизнь среди льда и снега.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "moja_001_1_reaction_char_MOJYAMON"): "Встретиться со мной в глуши можно в любое время!\nХотя для людей там, пожалуй, слишком сурово.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "mete_001_0_char_METALETEMON"): "Какое слово, по-твоему,\nлучше всего описывает твоего покорного слугу?",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "mete_001_1_reaction_char_METALETEMON"): "П-прошу прощения?! Но ты не ошибаешься.\nЭто вообще лучший комплимент на свете!",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "horus_001_2_reaction_char_HOLSMON"): "Впечатлило бы, если бы человеческие глаза могли за мной\nуследить. Но ты наверняка быстро потеряешь меня из виду.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "devi_001_3_reaction_char_DEVIMON"): "Веский довод. Люди порой действуют вопреки всякой логике.\nВозможно, и ты тоже...",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "vande_001_0_char_VAMDEMON"): "Тебя хоть немного интересуют тёмные искусства?",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "vande_001_4_reaction_char_VAMDEMON"): "Ты и правда попытаешься перевоспитать такого порочного типа,\nкак я? Смешно! Но жду твоей попытки.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "ldevi_001_1_reaction_char_LADYDEVIMON"): "Скажешь то же самое, даже оказавшись в ловушке?\nЖду случая это проверить.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "demon_001_2_reaction_char_DEMON"): "Тогда немедленно избавься от этого заблуждения.\nОтсутствие должного страха приведёт тебя к гибели.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "pie_001_0_char_PIEDMON"): "Как тебе партия в карты?",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "aruda_001_2_reaction_char_ALDAMON"): "Наши лица и правда похожи.\nНо присмотрись внимательнее и пойми, чем мы отличаемся.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "paid_001_0_char_PAILDRAMON"): "Посмотри, что получится,\nесли скрестить лучшие черты дракона и насекомого!",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "migao_001_2_reaction_char_MIRAGEGAOGAMON"): "Но при моей скорости ты успеешь заметить\nлишь отблеск остаточного изображения.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "mdora_001_1_reaction_char_MEGADRAMON"): "Понятно. Значит, люди сражаются, несмотря на хрупкость.\nЭто и есть то, что ты называешь «силой сердца»?",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "mdora_001_3_reaction_char_MEGADRAMON"): "Даже маленькие угольки могут разжечь костёр.\nПредставь, как ярко мы с тобой вспыхнем вместе.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "cydora_001_0_char_CYBERDRAMON"): "Есть враги, которых хочешь удалить?",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "cydora_001_4_reaction_char_CYBERDRAMON"): "Невозможно. Я найду и сотру твоих врагов\nвместе с окружающим их пространством.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "rave_001_2_reaction_char_RAVEMON"): "Очень смешно... Но, пожалуй, в твоих словах есть смысл.\nНе всё можно так чётко разделить.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "justi_001_0_char_JUSTIMON"): "Что думаешь о моём красном шарфе? Он мне очень идёт, правда?",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "justi_001_3_reaction_char_JUSTIMON"): "Большое тебе спасибо. Должен сказать,\nничто так не говорит «Джастимон», как красный шарф.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "pec_001_0_char_PECKMON"): "Говорю тебе: бегать НАМНОГО быстрее, чем летать!",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "sting_001_2_reaction_char_STINGMON"): "Ты передашь историю будущим поколениям.\nЯ тоже буду сражаться, чтобы защитить руины!",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "sting_001_3_reaction_char_STINGMON"): "Да, друзья дороже золота и серебра!\nЯ счастлив быть одним из твоих друзей!",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "kyubi_001_2_reaction_char_KYUBIMON"): "Не усложняй. Ты ведь тоже желаешь мира.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "kyubi_001_3_reaction_char_KYUBIMON"): "У тебя есть всё необходимое,\nчтобы вместе со мной стремиться к миру. Я в тебя верю.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "garumu_001_0_char_GARUMMON"): "Клянусь тебе в верности, мой сеньор.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "garumu_001_1_reaction_char_GARUMMON"): "Я хочу, чтобы мы вместе боролись за справедливость,\nпоэтому рассчитываю именно на тебя.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "garumu_001_2_reaction_char_GARUMMON"): "Защищай всё хорошее в Цифровом мире.\nИ поделись со мной своими мыслями.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "garumu_001_4_reaction_char_GARUMMON"): "Именно эта искренность привлекла меня к тебе.\nДавай вместе сокрушим зло.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "omsha_001_0_char_OMEGASHOUTMON"): "Если заметишь блестящее остаточное\nизображение, это могу быть я!",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "omsha_001_3_reaction_char_OMEGASHOUTMON"): "Если справишься со мной и моим неистовым рвением,\nобязательно это увидишь!",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "omsha_001_4_reaction_char_OMEGASHOUTMON"): "Если хочешь меня разглядеть, могу немного притормозить.\nНо только на миг.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "god_001_3_reaction_char_GODDRAMON"): "Возрождение приходит лишь после разрушения.\nЕсли сможешь принять эту истину, давай двигаться вперёд.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "exa_001_0_char_EXAMON"): "Не ошибись: огромная фигура —\nдалеко не всё, что во мне велико! Понимаешь?",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "jies_001_4_reaction_char_JESMON"): "Ты настолько мне доверяешь?! Конечно!\nСчитай, что твой тыл неприступен!",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "sleip_001_0_char_SLEIPMON"): "С чем тебе проще иметь дело:\nс палящей жарой или пронизывающим холодом?",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "mgaob_001_1_reaction_char_MIRAGEGAOGAMON_BM"): "Тогда советую тебе отойти.\nМоя энергия планетарного уровня — не шутка.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "magul_001_0_char_MAGNAGARURUMON"): "Я покажу тебе, как на самом деле выглядит скорость света.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "magul_001_1_reaction_char_MAGNAGARURUMON"): "Удивлюсь, если ты вообще разглядишь моё остаточное изображение.\nЯ мгновенно взмываю ввысь.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "magul_001_4_reaction_char_MAGNAGARURUMON"): "Когда начинается битва, по небу проносится\nослепительная вспышка. Так ты узнаешь, что я здесь.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "ravebu_001_4_reaction_char_RAVEMON_BM"): "Тебя пугает, что эта энергия может захлестнуть?\nНе волнуйся, я её контролирую.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "chadu_001_0_char_CHAOSDUKEMON"): "Стоит тебе пасть — и тьма с унынием\nуже не кажутся такими плохими.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "mduke_001_0_char_MEDIEVALDUKEMON"): "Знаешь о Цифровом мире в другом измерении?",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "mduke_001_2_reaction_char_MEDIEVALDUKEMON"): "Цифровой мир, который ты знаешь,\nне единственный. Есть и другие.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "mduke_001_3_reaction_char_MEDIEVALDUKEMON"): "Тогда тебе следует знать и обо мне:\nСредневековый Дюкмон, Генерал Вихря.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "alfa_001_2_reaction_char_ALPHAMON"): "Мои битвы — не развлечение,\nи твои глаза всё равно уловят лишь мгновение.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "alfa_001_3_reaction_char_ALPHAMON"): "Очень тактично для человека.\nЕсли бы все святые воины были такими, как ты.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "alfa_001_4_reaction_char_ALPHAMON"): "Прошлое редко удаётся изменить. Но раз именно тебе\nдовелось меня увидеть, я не слишком беспокоюсь.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "lokni_001_1_reaction_char_LOADKNIGHTMON"): "Что я только что сказал? Впрочем, можешь иметь любое мнение.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "lokni_001_2_reaction_char_LOADKNIGHTMON"): "Что я только что сказал? Говори что хочешь.\nВсе твои мнения для меня — чепуха.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "lokni_001_4_reaction_char_LOADKNIGHTMON"): "А как иначе? Дерзость я не одобряю,\nно признаю: мне небезразлично твоё мнение.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "duna_001_2_reaction_char_DYNASMON"): "Я не призываю тебя расстаться с жизнью.\nПросто действуй согласно своим убеждениям.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "duna_001_3_reaction_char_DYNASMON"): "Многие люди этого не понимают, но ты, похоже, понимаешь.\nВижу, наша дружба будет прочной.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "duna_001_4_reaction_char_DYNASMON"): "Твоя забота о моём благополучии радует меня,\nно мой сеньор превыше всего.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "duft_001_2_reaction_char_DUFTMON"): "Так оправдывается тот, кому недостаёт стратегического видения.\nСкоро я докажу, насколько ты заблуждаешься.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "duft_001_4_reaction_char_DUFTMON"): "Глупо соглашаться, не зная деталей.\nНо доверять мне — верное решение.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "duftrm_001_3_reaction_char_DUFTMON_LM"): "Мудрое решение. Жалеть не придётся.\nЦени своих хороших союзников.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "duftrm_001_4_reaction_char_DUFTMON_LM"): "У меня есть и стратегический ум, и боевая доблесть.\nЭто заслуживает твоего уважения.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "holyd_001_3_reaction_char_HOLYDRAMON"): "Пожалуйста, оставь это мне.\nТебе недостаёт подходящей для задачи техники.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "belbl_001_4_reaction_char_BEELZEMON_BM"): "У тебя неверное представление. Никто из тех,\nкто видел меня в гневе, не выжил, чтобы рассказать.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "lilis_001_2_reaction_char_LILITHMON"): "...Не уверена, что это значит,\nно, возможно, тебе стоит ещё немного разобраться в себе?",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "lilis_001_3_reaction_char_LILITHMON"): "Если хочешь достичь больших высот\nнечестивыми средствами — я помогу.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "ruches_001_1_reaction_char_LUCEMON_SM"): "Какая искренность... Но это невозможно.\nЯ всего лишь тень Люсемона.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "ruches_001_2_reaction_char_LUCEMON_SM"): "Перечитай древние тексты. Верить им или нет — решать тебе.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "lena_001_0_char_RENAMON"): "Кого из дигимонов ты считаешь по-настоящему сильным?",
}


# These common replies are stored once per protagonist affinity/voice variant.
# Generate only the exact, source-checked IDs; this is intentionally not a
# textual search-and-replace over the chat table.
DIGIMON_CHAT_VARIANTS = (
    "child_courage",
    "male_courage",
    "female_courage",
    "old_courage",
    "child_love",
    "male_love",
    "female_love",
    "old_love",
    "child_friendship",
    "male_friendship",
    "female_friendship",
    "old_friendship",
    "child_knowledge",
    "male_knowledge",
    "female_knowledge",
    "old_knowledge",
)

_DIGIMON_CHAT_COMMON_INBOUND_TEMPLATES = {
    "common033_0_{variant}": "Что для тебя значит мужество? Чувствую, это нечто очень важное.",
    "common036_0_{variant}": "Есть ли что-то, что ты хочешь защитить, даже ценой боли?",
    "common042_0_{variant}": "Бросишься ли ты в любую опасность ради друга?",
    "common042_1_reaction_{variant}": "Друзья — это здорово.\nОни помогают тебе достичь новых высот силы.",
    "common043_2_reaction_{variant}": "А вот и попытка уйти от темы. Теперь мне хочется узнать больше.",
    "common045_0_{variant}": "Я хочу приносить тебе ещё больше пользы!",
    "common046_2_reaction_{variant}": "...О, возможно, в твоих словах есть смысл.\nЯ и правда замечаю, что в последнее время глаза устают меньше.",
    "common054_1_reaction_{variant}": "Знание — это сокровище? Очень приятно слышать это от тебя!",
    "common056_0_{variant}": "Чем больше знаешь, тем лучше понимаешь, как мало тебе известно.",
    "common056_2_reaction_{variant}": "ДА. Скоро ты это поймёшь.",
}

for id_template, replacement in _DIGIMON_CHAT_COMMON_INBOUND_TEMPLATES.items():
    for variant in DIGIMON_CHAT_VARIANTS:
        key = (
            "patch_text01",
            "message/digimon_chat.mbe/000_Sheet1.csv",
            id_template.format(variant=variant),
        )
        if key in DIGIMON_CHAT_INBOUND_UPDATES:
            raise ValueError(f"duplicate inbound Digimon Chat key: {key}")
        DIGIMON_CHAT_INBOUND_UPDATES[key] = replacement


# The English source explicitly addresses a group in these rows.  Keeping this
# set beside the update table prevents a future formal->informal sweep from
# accidentally changing genuine plural speech.
DIGIMON_CHAT_INBOUND_PLURAL_EXCLUSIONS = {
    (
        "patch_text01",
        "message/digimon_chat.mbe/000_Sheet1.csv",
        "kokuw_001_0_char_KOKUWAMON",
    ),
    (
        "patch_text01",
        "message/digimon_chat.mbe/000_Sheet1.csv",
        "moja_001_3_reaction_char_MOJYAMON",
    ),
    (
        "patch_text01",
        "message/digimon_chat.mbe/000_Sheet1.csv",
        "ruche_001_2_reaction_char_LUCEMON",
    ),
}

for id_template in (
    "common049_2_reaction_{variant}",
    "common051_1_reaction_{variant}",
    "common054_2_reaction_{variant}",
):
    DIGIMON_CHAT_INBOUND_PLURAL_EXCLUSIONS.update(
        (
            "patch_text01",
            "message/digimon_chat.mbe/000_Sheet1.csv",
            id_template.format(variant=variant),
        )
        for variant in DIGIMON_CHAT_VARIANTS
    )

if len(DIGIMON_CHAT_INBOUND_UPDATES) != 344:
    raise ValueError(
        "expected 344 source-checked inbound Digimon Chat updates, got "
        f"{len(DIGIMON_CHAT_INBOUND_UPDATES)}"
    )
if len(DIGIMON_CHAT_INBOUND_PLURAL_EXCLUSIONS) != 51:
    raise ValueError(
        "expected 51 source-plural inbound Digimon Chat exclusions, got "
        f"{len(DIGIMON_CHAT_INBOUND_PLURAL_EXCLUSIONS)}"
    )
if DIGIMON_CHAT_INBOUND_UPDATES.keys() & DIGIMON_CHAT_INBOUND_PLURAL_EXCLUSIONS:
    raise ValueError("inbound Digimon Chat update overlaps a plural exclusion")


# A separate bounded pass for one-on-one lines whose formality is expressed
# only by a plural verb (for example, "скажите" or "давайте"), without an
# explicit вы/вам/ваш pronoun.  Each row was checked against the English line
# and the surrounding four-option Digimon Chat exchange.
DIGIMON_CHAT_VERB_FORM_UPDATES: dict[tuple[str, str, str], str] = {
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "loco_001_1_reaction_char_LOCOMON"): "Я постараюсь свести турбулентность к минимуму,\nтак что постарайся справиться со страхом.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "mars_001_3_reaction_char_MARSMON"): "Пойми: если ради спасения Цифрового мира\nпридётся нарушить правила, я это сделаю.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "diana_001_4_reaction_char_DIANAMON"): "Вот как я выгляжу? Что ж, ничего не поделаешь.\nНо постарайся увидеть и другую мою сторону.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "venus_001_1_reaction_char_VENUSMON"): "Конечно. Но имей в виду: я вижу всё —\nи то, что на поверхности, и то, что скрыто внутри.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "bacc_001_3_reaction_char_BACCHUSMON"): "Мне нравится свежая кислинка вин из таких фруктов.\nДавай устроим соревнование по выпивке!",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "cere_001_1_reaction_char_CERESMON"): "Пожалуй, нет... Но сдаваться я не собираюсь,\nтак что помоги мне с поисками.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "cere_001_2_reaction_char_CERESMON"): "Именно так и поступлю. Давай вместе послушаем голоса с высоты!",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "cerem_001_1_reaction_char_CERESMON_MEDIUM"): "Принимай дары Гайи с благодарностью.\nСоберёшь слишком много — может случиться беда.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "gob_001_2_reaction_char_GOBURIMON"): "Говори что хочешь!\nМы с приятелями просто дерёмся с умом, вот и всё!",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "oga_001_1_reaction_char_ORGEMON"): "Я в лучшем настроении, когда злюсь!\nРазозли меня ещё сильнее — и я кого-нибудь отправлю в полёт!",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "chdes_001_3_reaction_char_CHRONOMON_DESTROY"): "Верить легко. Но вера приносит и боль.\nК этому стоит подготовиться.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "puka_001_2_reaction_char_PUKAMON"): "Да, давай разберёмся, как это работает.\nЯ готов действовать по правилам!",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "goma_001_4_reaction_char_GOMAMON"): "Спасибо, вот это меня радует!\nДавай найдём несколько штук и съедим их вместе!",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "seado_001_3_reaction_char_SEADRAMON"): "Совместные тренировки... Звучит весело. Я счастлив...",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "dago_001_2_reaction_char_DAGOMON"): "Справедливый вопрос. А ответ... Ищи его самостоятельно.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "mochi_001_2_reaction_char_MOCHIMON"): "Людям это, кажется, нравится. Смотри сколько хочешь!",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "mucho_001_3_reaction_char_MUCHOMON"): "Вкусно, но кожура — это не шутка.\nДавай попробуем расколоть этот фрукт вместе!",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "mucho_001_4_reaction_char_MUCHOMON"): "Этот фрукт очень легко помять.\nОбращайся с ним осторожно, ладно?",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "wasp_001_0_char_WASPMON"): "Стой! Кто идёт?! А... Прости. Просто привычка после патрулей.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "sunf_001_4_reaction_char_SUNFLOWMON"): "Да, отличная мысль! Давай немного поспим,\nа утром соберёмся с силами!",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "jure_001_4_reaction_char_JYUREIMON"): "Я был бы рад, если бы все так думали.\nПрисматривай за лесом, держась на почтительном расстоянии.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "tyrant_001_1_reaction_char_TYRANTKABUTERIMON"): "Склонись в благоговении перед славой моей\nнепробиваемой оболочки из хрондигизоида.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "tyrant_001_2_reaction_char_TYRANTKABUTERIMON"): "Запомни: монарх никогда не занимается такими делами лично.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "muged_001_0_char_MUGENDRAMON"): "ХОЧЕШЬ УВИДЕТЬ ПРИМЕР БЕЗГРАНИЧНОЙ СИЛЫ?",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "kote_001_1_reaction_char_KOTEMON"): "Вот это настрой! Освой у меня все приёмы, какие только сможешь.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "gal_001_2_reaction_char_GARGOMON"): "Хорошо. Тогда в следующий раз делай заметки,\nпока я бегаю и летаю, а потом сравним.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "zudo_001_0_char_ZUDOMON"): "Полюбуйся на эти мышцы!",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "zudo_001_3_reaction_char_ZUDOMON"): "Любуйся сколько хочешь. Я не против.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "pata_001_1_reaction_char_PATAMON"): "...Я так и знал. Надо набраться смелости и извиниться.\nПрости за странный вопрос.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "pro_001_0_char_PLOTMON"): "Слушай, а что такое «щенок»?",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "ange_001_3_reaction_char_ANGEMON"): "...Пожалуйста, не приставай ко мне\nс такими банальными выходками.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "uni_001_0_char_YUNIMON"): "Давай вместе объедем весь мир!",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "serap_001_1_reaction_char_SERAPHIMON"): "Не позволяй злу существовать в этом мире.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "coro_001_1_reaction_char_CORONAMON"): "Солнце на моей стороне,\nтак что моё пламя непобедимо! Давай сразимся!",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "sola_001_1_reaction_char_SOLARMON"): "Ги-ги-ги... Это жар моего Дигиядра.\nПрости за духоту. Считай это тренировкой!",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "shakko_001_1_reaction_char_SHAKKOUMON"): "ДА. НЕ СОМНЕВАЙСЯ. Я МОГУ АТАКОВАТЬ ВО ВСЕХ НАПРАВЛЕНИЯХ.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "yuki_001_1_reaction_char_YUKIDARUMON"): "Всегда пожалуйста! Только не простудись.\nДля людей там прохладновато.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "moja_001_2_reaction_char_MOJYAMON"): "Глубоко в заснеженных горах.\nНо это священная земля, так что не топчись там.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "demon_001_3_reaction_char_DEMON"): "Бойся меня — Злого короля дигимонов!\nМне служит множество злых дигимонов и тёмных ангелов.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "aruda_001_1_reaction_char_ALDAMON"): "Да, наши когти и хвосты похожи.\nА кто из нас сильнее — решать тебе.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "elec_001_3_reaction_char_ELECMON"): "Можешь копировать меня, если хочешь!",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "rapi_001_0_char_RAPIDMON"): "Я «Рэпидмон», а не «Раббитмон». Не перевирай!",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "kyubi_001_1_reaction_char_KYUBIMON"): "Желать мира — первый шаг к действию.\nДавай пройдём этот путь вместе.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "god_001_4_reaction_char_GODDRAMON"): "Эти две силы поддерживают равновесие мира.\nДавай вместе создавать будущее.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "kaigra_001_2_reaction_char_KAISERGREYMON"): "Во мне сила девяти драконьих вен. Смотри, на что она способна!",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "kaigra_001_3_reaction_char_KAISERGREYMON"): "Разумеется! Смотри, как я добавляю\nк собственной мощи силу восьми драконьих вен!",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "mgulb_001_3_reaction_char_MAGNAGARURUMON_SEPARATION"): "Спасибо. С верой друзей я способен на всё.\nОцени мою сверхсветовую скорость!",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "chadu_001_1_reaction_char_CHAOSDUKEMON"): "Говори что хочешь, но я, Хаосгаллантмон,\nпринесу Цифровому миру катастрофу!",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "duft_001_3_reaction_char_DUFTMON"): "Ну, например... Стоп! Я едва не раскрыл карты.\nПридётся быть осторожнее...",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "diana_001_1_reaction_char_DIANAMON"): "Что ж, учти: иногда я и правда могу показаться холодной.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "fanbi_001_1_reaction_char_FUNBEEMON"): "Конечно, оставь это мне! Я умею таскать вещи!",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "jure_001_3_reaction_char_JYUREIMON"): "Я не требую многого.\nПросто не мешай природе идти своим чередом — и она всё даст.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "megag_001_0_char_MEGAGROWLMON"): "Воздушные атаки оставь мне.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "glade_001_0_char_GRADEMON"): "Авангард оставь мне.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "pega_001_2_reaction_char_PEGASMON"): "«Больно» — слишком мягко сказано.\nПредставь себе по-настоящему жестокий удар.",
}

_DIGIMON_CHAT_COMMON_VERB_FORM_TEMPLATES = {
    "common020_1_reaction_{variant}": "Правда? Тогда прости — и спасибо!",
    "common022_1_reaction_{variant}": "В бою нужно думать головой. Хорошо, что наши мнения сходятся!",
    "common036_2_reaction_{variant}": "Наверное, на такой вопрос трудно ответить сразу.\nНо всё же немного подумай.",
    "common046_1_reaction_{variant}": "Разве любовь может быть ещё прекраснее?\nТолько посмотри, как всё вокруг сияет!",
}

for id_template, replacement in _DIGIMON_CHAT_COMMON_VERB_FORM_TEMPLATES.items():
    for variant in DIGIMON_CHAT_VARIANTS:
        key = (
            "patch_text01",
            "message/digimon_chat.mbe/000_Sheet1.csv",
            id_template.format(variant=variant),
        )
        if key in DIGIMON_CHAT_VERB_FORM_UPDATES:
            raise ValueError(f"duplicate verb-form Digimon Chat key: {key}")
        DIGIMON_CHAT_VERB_FORM_UPDATES[key] = replacement

for personality_suffix in range(4):
    key = (
        "patch_text01",
        "message/digimon_chat.mbe/000_Sheet1.csv",
        f"digimon_chat_ps_2{personality_suffix}",
    )
    DIGIMON_CHAT_VERB_FORM_UPDATES[key] = "Давай освоим новый Личностный Навык!"

DIGIMON_CHAT_VERB_FORM_PLURAL_EXCLUSIONS = {
    (
        "patch_text01",
        "message/digimon_chat.mbe/000_Sheet1.csv",
        "piyo_001_3_reaction_char_PIYOMON",
    ),
}

if len(DIGIMON_CHAT_VERB_FORM_UPDATES) != 123:
    raise ValueError(
        "expected 123 source-checked verb-form Digimon Chat updates, got "
        f"{len(DIGIMON_CHAT_VERB_FORM_UPDATES)}"
    )
if DIGIMON_CHAT_VERB_FORM_UPDATES.keys() & DIGIMON_CHAT_INBOUND_UPDATES.keys():
    raise ValueError("verb-form Digimon Chat update overlaps an inbound update")


# Generic speaker labels.  These are source-checked semantic corrections, not
# title-case normalization: several old strings had translated character roles
# as literal actions (for example, In-Training as "training").
NPC_NAME_UPDATES: dict[tuple[str, str, str], str] = {
    ("patch_text01", "text/char_name.mbe/000_Sheet1.csv", "char_MAMEMONS"): "Несколько Мамемонов",
    ("patch_text01", "text/char_name.mbe/000_Sheet1.csv", "char_KOKUWAMON_AUN"): "Кокувамон А и Б",
    ("patch_text01", "text/char_name.mbe/000_Sheet1.csv", "char_CHILDHOOD_DIGIMONS"): "Несколько дигимонов-малышей",
    ("patch_text01", "text/char_name.mbe/000_Sheet1.csv", "char_CHILDHOOD_DIGIMON_FAIL_TO_ESCAPE"): "Отставший дигимон-малыш",
    ("patch_text01", "text/char_name.mbe/000_Sheet1.csv", "char_MAN"): "Мужчина",
    ("patch_text01", "text/char_name.mbe/000_Sheet1.csv", "char_GIRL"): "Девочка",
    ("patch_text01", "text/char_name.mbe/000_Sheet1.csv", "char_ABDUCTED_GIRL"): "Девочка",
    ("patch_text01", "text/char_name.mbe/000_Sheet1.csv", "char_SALESPERSON"): "Продавец",
    ("patch_text01", "text/char_name.mbe/000_Sheet1.csv", "char_SHOP_CLERK"): "Продавец",
    ("patch_text01", "text/char_name.mbe/000_Sheet1.csv", "char_PROPRIETOR"): "Хозяин заведения",
    ("patch_text01", "text/char_name.mbe/000_Sheet1.csv", "char_POLICEMAN"): "Полицейский",
    ("patch_text01", "text/char_name.mbe/000_Sheet1.csv", "char_PUBLIC_SECURITY_PERSONNEL"): "Сотрудник общественной безопасности",
    ("patch_text01", "text/char_name.mbe/000_Sheet1.csv", "char_PUBLIC_SECURITY_PERSONNEL_A"): "Сотрудник общественной безопасности A",
    ("patch_text01", "text/char_name.mbe/000_Sheet1.csv", "char_PUBLIC_SECURITY_PERSONNEL_B"): "Сотрудник общественной безопасности B",
    ("patch_text01", "text/char_name.mbe/000_Sheet1.csv", "char_PUBLIC_SECURITY_PERSONNEL_C"): "Сотрудник общественной безопасности C",
    ("patch_text01", "text/char_name.mbe/000_Sheet1.csv", "char_PUBLICSAFETY_MOB_B"): "Сотрудник общественной безопасности B",
    ("patch_text01", "text/char_name.mbe/000_Sheet1.csv", "char_PUBLICSAFETY_MOB_C"): "Сотрудник общественной безопасности C",
    ("patch_text01", "text/char_name.mbe/000_Sheet1.csv", "char_NEWS_AUDIO"): "Диктор новостей",
    ("patch_text01", "text/char_name.mbe/000_Sheet1.csv", "char_CHIEF_OF_PUBLIC_SECURITY"): "Капитан общественной безопасности",
    ("patch_text01", "text/char_name.mbe/000_Sheet1.csv", "char_MAD_VOICE_SINGER"): "Забавный певец",
    ("patch_text01", "text/char_name.mbe/000_Sheet1.csv", "char_SECURITY"): "Система безопасности",
    ("patch_text01", "text/char_name.mbe/000_Sheet1.csv", "char_MAN_IN_WAIT"): "Мужчина, которого не дождались",
    ("patch_text01", "text/char_name.mbe/000_Sheet1.csv", "char_LOST_GAMER"): "Растерянный геймер",
    ("patch_text01", "text/char_name.mbe/000_Sheet1.csv", "char_NUISANCE_DOUGER"): "Назойливый стример",
    ("patch_text01", "text/char_name.mbe/000_Sheet1.csv", "char_CAFE_ASSISTANT"): "Сотрудник кафе",
    ("patch_text01", "text/char_name.mbe/000_Sheet1.csv", "char_FRONTCLERK"): "Администратор",
    ("patch_text01", "text/char_name.mbe/000_Sheet1.csv", "char_RECEPTION"): "Администратор приёмной",
    ("patch_text01", "text/char_name.mbe/000_Sheet1.csv", "char_BIG_STUFFED_TOY"): "Большая плюшевая игрушка",
    ("patch_text01", "text/char_name.mbe/000_Sheet1.csv", "char_STUFFED_TOY_?"): "Плюшевая игрушка?",
    ("patch_text01", "text/char_name.mbe/000_Sheet1.csv", "char_SELF_PROCLAIMED_STUFFED_TOY"): "Самопровозглашённая плюшевая игрушка",
    ("patch_text01", "text/char_name.mbe/000_Sheet1.csv", "char_UNKNOWN_USER"): "Неизвестный пользователь",
    ("patch_text01", "text/char_name.mbe/000_Sheet1.csv", "char_BIRDRA_TRANSPORT_EMPLOYEE"): "Сотрудник транспортной службы Бирдрамона",
    ("patch_text01", "text/char_name.mbe/000_Sheet1.csv", "char_BIRDRA_TRANSPORT_OWNER"): "Владелец транспортной службы Бирдрамона",
    ("patch_text01", "text/char_name.mbe/000_Sheet1.csv", "char_MAYBE_LEADER"): "Мужчина (вероятно, лидер)",
    ("patch_text01", "text/char_name.mbe/000_Sheet1.csv", "char_MAN_ON_THE_PHONE"): "Мужчина, говорящий по телефону",
    ("patch_text01", "text/char_name.mbe/000_Sheet1.csv", "char_CALLER"): "Собеседник по телефону",
    ("patch_text01", "text/char_name.mbe/000_Sheet1.csv", "char_MAID"): "Официантка-мэйд",
    ("patch_text01", "text/char_name.mbe/000_Sheet1.csv", "char_OTAKU"): "Фанат аниме",
    ("patch_text01", "text/char_name.mbe/000_Sheet1.csv", "char_OUT_OTAKU"): "Творческий анимешник",
    ("patch_text01", "text/char_name.mbe/000_Sheet1.csv", "char_YOUNG_MAN_STANDING"): "Скучающий парень",
    ("patch_text01", "text/char_name.mbe/000_Sheet1.csv", "char_NAMELESS_RUNNER"): "Безымянный бегун",
    ("patch_text01", "text/char_name.mbe/000_Sheet1.csv", "char_VOICES_OF_ONLOOKERS_HEARD_IN_THE_DISTANCE"): "Голоса зрителей вдали",
    ("patch_text01", "text/char_name.mbe/000_Sheet1.csv", "char_TICKET_COLLECTOR"): "Билетёр",
    ("patch_text01", "text/char_name.mbe/000_Sheet1.csv", "char_ELEVATORSTAFF"): "Лифтёрша",
    ("patch_text01", "text/char_name.mbe/000_Sheet1.csv", "char_SPECIAL_FORCES"): "Боец спецназа",
    ("patch_text01", "text/char_name.mbe/000_Sheet1.csv", "char_OFFICE_WORKER"): "Офисный сотрудник",
}


# Fixed shop templates.  The time-traveler bartender's gendered greeting is
# deliberately absent: its M/F forms belong to the runtime gender dataset.
NPC_FIELD_UPDATES: dict[tuple[str, str, str], str] = {
    **{
        ("patch_text01", "message/field_text.mbe/000_Sheet1.csv", row_id): "Здравствуйте."
        for row_id in (
            "g_shop001_0010_0010",
            "g_shop003_0010_0010",
            "g_shop004_0010_0010",
            "g_shop005_0010_0010",
            "g_shop010_0010_0010",
            "g_shop012_0010_0010",
            "g_shop105_0010_0010",
        )
    },
    **{
        ("patch_text01", "message/field_text.mbe/000_Sheet1.csv", row_id): "Спасибо, что заглянули. Приходите ещё."
        for row_id in (
            "g_shop001_0020_0010",
            "g_shop003_0020_0010",
            "g_shop004_0020_0010",
            "g_shop011_0020_0010",
            "g_shop012_0020_0010",
            "g_shop105_0020_0010",
        )
    },
    **{
        ("patch_text01", "message/field_text.mbe/000_Sheet1.csv", row_id): "Спасибо за покупку."
        for row_id in (
            "g_shop001_0030_0010",
            "g_shop002_0030_0010",
            "g_shop003_0030_0010",
            "g_shop004_0030_0010",
            "g_shop005_0030_0010",
            "g_shop007_0030_0010",
            "g_shop012_0030_0010",
            "g_shop105_0030_0010",
            "g_shop201_0030_0010",
        )
    },
    **{
        ("patch_text01", "message/field_text.mbe/000_Sheet1.csv", row_id): "Я куплю это у вас."
        for row_id in (
            "g_shop001_0040_0010",
            "g_shop002_0040_0010",
            "g_shop003_0040_0010",
            "g_shop004_0040_0010",
            "g_shop005_0040_0010",
            "g_shop007_0040_0010",
            "g_shop012_0040_0010",
            "g_shop105_0040_0010",
            "g_shop201_0040_0010",
        )
    },
    ("patch_text01", "message/field_text.mbe/000_Sheet1.csv", "g_shop005_0020_0010"): "Спасибо, что заглянули. Берегите себя.",
    ("patch_text01", "message/field_text.mbe/000_Sheet1.csv", "g_shop007_0010_0010"): "Добро пожаловать в круглосуточный магазин «Тёмный Аристократ»!",
    ("patch_text01", "message/field_text.mbe/000_Sheet1.csv", "g_shop008_0010_0010"): "Заходи, погляди...",
    ("patch_text01", "message/field_text.mbe/000_Sheet1.csv", "g_shop008_0020_0010"): "Заглядывай ещё...",
    ("patch_text01", "message/field_text.mbe/000_Sheet1.csv", "g_shop008_0030_0010"): "Сейчас всё соберу...",
    ("patch_text01", "message/field_text.mbe/000_Sheet1.csv", "g_shop008_0040_0010"): "Та-ак...",
    ("patch_text01", "message/field_text.mbe/000_Sheet1.csv", "g_shop009_0010_0010"): "...Привет.",
    ("patch_text01", "message/field_text.mbe/000_Sheet1.csv", "g_shop009_0040_0010"): "Мы покупаем почти всё...",
    ("patch_text01", "message/field_text.mbe/000_Sheet1.csv", "g_shop010_0030_0010"): "Установите этот диск, чтобы защититься от вредоносных вирусов!",
    ("patch_text01", "message/field_text.mbe/000_Sheet1.csv", "g_shop010_0040_0010"): "Если у вас есть редкие предметы, мы охотно их купим!",
    ("patch_text01", "message/field_text.mbe/000_Sheet1.csv", "g_shop011_0010_0010"): "Здравствуйте. Какую одежду вы ищете?",
    ("patch_text01", "message/field_text.mbe/000_Sheet1.csv", "g_shop011_0030_0010"): "Вам очень идёт.",
    ("patch_text01", "message/field_text.mbe/000_Sheet1.csv", "g_shop096_0020_0010"): "Где мы встретимся в следующий раз — в прошлом или будущем?\nПомни: тебе здесь всегда рады.",
    ("patch_text01", "message/field_text.mbe/000_Sheet1.csv", "g_shop096_0030_0010"): "Это то, что тебе нужно?",
    ("patch_text01", "message/field_text.mbe/000_Sheet1.csv", "g_shop096_0040_0010"): "С радостью заберу.",
    ("patch_text01", "message/field_text.mbe/000_Sheet1.csv", "g_shop099_0020_0010"): "Где мы встретимся в следующий раз — в прошлом или будущем?\nПомни: тебе здесь всегда рады.",
    ("patch_text01", "message/field_text.mbe/000_Sheet1.csv", "g_shop099_0030_0010"): "Это то, что тебе нужно?",
    ("patch_text01", "message/field_text.mbe/000_Sheet1.csv", "g_shop099_0040_0010"): "С радостью заберу.",
    ("patch_text01", "message/field_text.mbe/000_Sheet1.csv", "g_shop154_0020_0010"): "Если захочешь ещё что-нибудь обменять, я буду ждать!",
    ("patch_text01", "message/field_text.mbe/000_Sheet1.csv", "g_shop154_0030_0010"): "Береги эту карту, ладно?!",
    ("patch_text01", "message/field_text.mbe/000_Sheet1.csv", "g_shop154_0040_0010"): "Обменяю вот на это.",
    ("patch_text01", "message/field_text.mbe/000_Sheet1.csv", "g_shop201_0010_0010"): "Здравствуйте. Это магазин карт.",
    ("patch_text01", "message/field_text.mbe/000_Sheet1.csv", "g_shop201_0020_0010"): "Будем рады видеть вас снова!",
}


# Ambient human NPCs and arena spectators.  Protest chants consistently use
# plural "вы": they address the authorities as a body, not the protagonist.
NPC_RUMOR_UPDATES: dict[tuple[str, str, str], str] = {
    ("patch_text01", "message/rumor_npc.mbe/000_Sheet1.csv", "r_t0101_0010_0050"): "Наверное, поеду домой на такси.",
    ("patch_text01", "message/rumor_npc.mbe/000_Sheet1.csv", "r_t0101_0010_0070"): "Не пройти? Серьёзно?..",
    ("patch_text01", "message/rumor_npc.mbe/000_Sheet1.csv", "r_t0101_0010_0080"): "Что, здесь нельзя пройти?..",
    ("patch_text01", "message/rumor_npc.mbe/000_Sheet1.csv", "r_t0101_0010_0100"): "Мне уже не по себе...",
    ("patch_text01", "message/rumor_npc.mbe/000_Sheet1.csv", "r_t0101_0010_0110"): "Что вообще происходит?",
    ("patch_text01", "message/rumor_npc.mbe/000_Sheet1.csv", "r_t0101_0010_0140"): "Не может быть! Дигимон?!",
    ("patch_text01", "message/rumor_npc.mbe/000_Sheet1.csv", "r_t0102_0010_0270"): "Что это за ребёнок?",
    ("patch_text01", "message/rumor_npc.mbe/000_Sheet1.csv", "r_t0102_0010_0360"): "Эй, это не та самая из интернета?",
    ("patch_text01", "message/rumor_npc.mbe/000_Sheet1.csv", "r_t0103_0010_0010"): "Куда бы пойти?..",
    ("patch_text01", "message/rumor_npc.mbe/000_Sheet1.csv", "r_t0103_0010_0020"): "Что-то она задерживается...",
    ("patch_text01", "message/rumor_npc.mbe/000_Sheet1.csv", "r_t0103_0010_0050"): "Вот же! Отсюда ничего не видно...",
    ("patch_text01", "message/rumor_npc.mbe/000_Sheet1.csv", "r_t0103_0010_0053"): "Что-то у меня дурное предчувствие...",
    ("patch_text01", "message/rumor_npc.mbe/000_Sheet1.csv", "r_t0103_0010_0054"): "Пожалуй, лучше держаться отсюда подальше...",
    ("patch_text01", "message/rumor_npc.mbe/000_Sheet1.csv", "r_t0103_0010_0056"): "Сфотографирую просто так.",
    ("patch_text01", "message/rumor_npc.mbe/000_Sheet1.csv", "r_t0103_0010_0062"): "Выложу это в сеть!",
    ("patch_text01", "message/rumor_npc.mbe/000_Sheet1.csv", "r_t0103_0010_0065"): "Оно только что пошевелилось!",
    ("patch_text01", "message/rumor_npc.mbe/000_Sheet1.csv", "r_t0103_0010_0070"): "Не толкайтесь!",
    ("patch_text01", "message/rumor_npc.mbe/000_Sheet1.csv", "r_t0103_0010_0120"): "Диги... мон?",
    ("patch_text01", "message/rumor_npc.mbe/000_Sheet1.csv", "r_t0103_0010_0130"): "Не думал, что оно умеет ходить...",
    ("patch_text01", "message/rumor_npc.mbe/000_Sheet1.csv", "r_t0103_0010_0160"): "Хм? Это что, оно?..",
    ("patch_text01", "message/rumor_npc.mbe/000_Sheet1.csv", "r_t0103_0010_0175"): "Ты меня игнорируешь?",
    ("patch_text01", "message/rumor_npc.mbe/000_Sheet1.csv", "r_t0103_0010_0180"): "Я хочу расспросить тебя о дигимонах!",
    ("patch_text01", "message/rumor_npc.mbe/000_Sheet1.csv", "r_t0103_0010_0185"): "Эй, да ладно! Это займёт всего секунду!",
    ("patch_text01", "message/rumor_npc.mbe/000_Sheet1.csv", "r_t0103_0010_0195"): "Эй, не игнорируй! Обидно вообще-то!",
    ("patch_text01", "message/rumor_npc.mbe/000_Sheet1.csv", "r_t0103_0010_0200"): "Всего пара вопросов! Ну же!",
    ("patch_text01", "message/rumor_npc.mbe/000_Sheet1.csv", "r_t0104_0010_0010"): "Турникеты внизу по лестнице, да?",
    ("patch_text01", "message/rumor_npc.mbe/000_Sheet1.csv", "r_t0104_0010_0050"): "У них уже появилась новая книга!",
    ("patch_text01", "message/rumor_npc.mbe/000_Sheet1.csv", "r_t0104_0010_0080"): "На этой станции чёрт ногу сломит...!",
    ("patch_text01", "message/rumor_npc.mbe/000_Sheet1.csv", "r_t0104_0010_0090"): "В сети появились видео со странными явлениями...",
    ("patch_text01", "message/rumor_npc.mbe/000_Sheet1.csv", "r_t0104_0010_0110"): "Эвакуируйтесь в эту сторону!",
    ("patch_text01", "message/rumor_npc.mbe/000_Sheet1.csv", "r_t0104_0010_0130"): "Что это за аппарат?!",
    ("patch_text01", "message/rumor_npc.mbe/000_Sheet1.csv", "r_t0104_0010_0150"): "Что значит «эвакуироваться»?..",
    ("patch_text01", "message/rumor_npc.mbe/000_Sheet1.csv", "r_t0107_0010_0010"): "Скажите нам правду!",
    ("patch_text01", "message/rumor_npc.mbe/000_Sheet1.csv", "r_t0107_0010_0090"): "Ответьте нам!",
    ("patch_text01", "message/rumor_npc.mbe/000_Sheet1.csv", "r_t0107_0010_0100"): "Мы знаем, что вы что-то скрываете!",
    ("patch_text01", "message/rumor_npc.mbe/000_Sheet1.csv", "r_t0107_0010_0110"): "Правда всё равно выйдет наружу!",
    ("patch_text01", "message/rumor_npc.mbe/000_Sheet1.csv", "r_t0107_0010_0150"): "Просто расскажите нам всё!",
    ("patch_text01", "message/rumor_npc.mbe/000_Sheet1.csv", "r_t0107_0010_0160"): "Вы не сможете вечно скрывать правду!",
    ("patch_text01", "message/rumor_npc.mbe/000_Sheet1.csv", "r_t0107_0020_0010"): "Почему вы молчите?!",
    ("patch_text01", "message/rumor_npc.mbe/000_Sheet1.csv", "r_t0107_0020_0020"): "С меня хватит!",
    ("patch_text01", "message/rumor_npc.mbe/000_Sheet1.csv", "r_t0107_0020_0040"): "Уважайте наши гражданские права!",
    ("patch_text01", "message/rumor_npc.mbe/000_Sheet1.csv", "r_t0107_0020_0120"): "Громче! Пусть нас услышат!",
    ("patch_text01", "message/rumor_npc.mbe/000_Sheet1.csv", "r_t0107_0020_0180"): "Как долго вы будете лгать народу?!",
    ("patch_text01", "message/rumor_npc.mbe/000_Sheet1.csv", "r_t0107_0020_0230"): "Разве вы не должны защищать людей?!",
    ("patch_text01", "message/rumor_npc.mbe/000_Sheet1.csv", "r_t0107_0020_0260"): "Покажем им наш гнев!",
    ("patch_text01", "message/rumor_npc.mbe/000_Sheet1.csv", "r_t0107_0020_0280"): "Вы не можете решать всё за нас!",
    ("patch_text01", "message/rumor_npc.mbe/000_Sheet1.csv", "r_t0107_0020_0290"): "Вы хотите отнять у нас свободу?!",
    ("patch_text01", "message/rumor_npc.mbe/000_Sheet1.csv", "r_t0107_0020_0300"): "Мы не позволим вам выйти сухими из воды!",
    ("patch_text01", "message/rumor_npc.mbe/000_Sheet1.csv", "r_t0107_0020_0310"): "Не дайте правительству уйти от ответа!",
    ("patch_text01", "message/rumor_npc.mbe/000_Sheet1.csv", "r_t0107_0020_0320"): "Мы требуем открытости!",
    ("patch_text01", "message/rumor_npc.mbe/000_Sheet1.csv", "r_t0107_0020_0350"): "Чего вы так боитесь?!",
    ("patch_text01", "message/rumor_npc.mbe/000_Sheet1.csv", "r_t0107_0020_0400"): "Мы знаем, что вы что-то скрываете!",
    ("patch_text01", "message/rumor_npc.mbe/000_Sheet1.csv", "r_t0107_0020_0440"): "Какого чёрта?! Свидание сорвано!",
    ("patch_text01", "message/rumor_npc.mbe/000_Sheet1.csv", "r_t0107_0020_0450"): "Вы держите нас за дураков?!",
    ("patch_text01", "message/rumor_npc.mbe/000_Sheet1.csv", "r_t0107_0020_0490"): "Это были кадры из-за Стены?!",
    ("patch_text01", "message/rumor_npc.mbe/000_Sheet1.csv", "r_t0107_0020_0520"): (
        "Неужели ОккультТокио ТВ показывает,\n"
        "что происходит на самом деле?!"
    ),
    ("patch_text01", "message/rumor_npc.mbe/000_Sheet1.csv", "r_t0107_0020_0540"): "Я слышал, в сеть утекли кадры из-за Стены!",
    ("patch_text01", "message/rumor_npc.mbe/000_Sheet1.csv", "r_t0107_0020_0560"): "Верните нам прежний город!",
    ("patch_text01", "message/rumor_npc.mbe/000_Sheet1.csv", "r_t0107_0020_0570"): "Мы просто хотим вернуть прежнюю жизнь!",
    ("patch_text01", "message/rumor_npc.mbe/000_Sheet1.csv", "r_t0107_0020_0600"): "Мы вам не стадо овец!",
    ("patch_text01", "message/rumor_npc.mbe/000_Sheet1.csv", "r_t0107_0020_0610"): "Вы что, нас не слышите?!",
    ("patch_text01", "message/rumor_npc.mbe/000_Sheet1.csv", "r_t0108_0010_0010"): "Где собираются на протест?..",
    ("patch_text01", "message/rumor_npc.mbe/000_Sheet1.csv", "r_t0108_0010_0020"): "Где бы скоротать время?..",
    ("patch_text01", "message/rumor_npc.mbe/000_Sheet1.csv", "r_t0108_0010_0040"): "И здесь не пройти.",
    ("patch_text01", "message/rumor_npc.mbe/000_Sheet1.csv", "r_t0108_0010_0060"): "И правда нужны такие меры?",
    ("patch_text01", "message/rumor_npc.mbe/000_Sheet1.csv", "r_t0108_0010_0080"): "Кстати, раз уж речь зашла о странностях...",
    ("patch_text01", "message/rumor_npc.mbe/000_Sheet1.csv", "r_d1103_0010_0010"): "В строй!",
    ("patch_text01", "message/rumor_npc.mbe/000_Sheet1.csv", "r_t0121_0010_0020"): "Так держать!..",
    ("patch_text01", "message/rumor_npc.mbe/000_Sheet1.csv", "r_t0121_0010_0040"): "Пожалуйста! Ну же! Я умоляю!..",
    ("patch_text01", "message/rumor_npc.mbe/000_Sheet1.csv", "r_t0121_0010_0050"): "Вот чёрт...",
    ("patch_text01", "message/rumor_npc.mbe/000_Sheet1.csv", "r_t0121_0020_0010"): "Тише едешь — дальше будешь!",
    ("patch_text01", "message/rumor_npc.mbe/000_Sheet1.csv", "r_t0121_0030_0010"): "Хм... Да, отличное выступление.",
    ("patch_text01", "message/rumor_npc.mbe/000_Sheet1.csv", "r_t0121_0030_0030"): "Будущее туманно...",
    ("patch_text01", "message/rumor_npc.mbe/000_Sheet1.csv", "r_t0121_0030_0040"): "Ну же! Не подведи меня...",
    ("patch_text01", "message/rumor_npc.mbe/000_Sheet1.csv", "r_t0121_0040_0010"): "Когда же они выйдут?! Хочу сделать идеальный снимок!",
    ("patch_text01", "message/rumor_npc.mbe/000_Sheet1.csv", "r_t0121_0050_0020"): "Не знаю, как теперь смотреть жене в глаза...",
}


# Source-checked lines spoken by unnamed human NPCs in field, story, and side
# quest tables.  Gender-neutral rewrites are used when the line addresses the
# selectable protagonist and no runtime M/F form is necessary.
NPC_DIALOGUE_UPDATES: dict[tuple[str, str, str], str] = {
    # Tokyo field NPCs.
    ("patch_text01", "message/t01.mbe/000_Sheet1.csv", "f_t0101_9000_0060"): (
        "Полный разгром... Вот это да! Придётся полностью\n"
        "пересобрать колоду!"
    ),
    ("patch_text01", "message/t01.mbe/000_Sheet1.csv", "f_t0101_0190_0030"): (
        "И вот наконец вышел ремейк! Команда, работавшая над ним,\n"
        "наверное, была счастлива."
    ),
    ("patch_text01", "message/t01.mbe/000_Sheet1.csv", "f_t0102_0030_0010"): (
        "За Стеной Надежды явно кроется какой-то заговор!\n"
        "Надо присоединиться к протесту и выяснить правду!"
    ),
    ("patch_text01", "message/t01.mbe/000_Sheet1.csv", "f_t0102_0160_0020"): (
        "Дальше опасные дигимоны. Пожалуйста, не подходите!"
    ),
    ("patch_text01", "message/t01.mbe/000_Sheet1.csv", "f_t0102_0170_0010"): (
        "Дигимоны ещё не проникли под землю. Пользуйтесь подземными\n"
        "путями для эвакуации и передвижения."
    ),
    ("patch_text01", "message/t01.mbe/000_Sheet1.csv", "f_t0102_0210_0030"): (
        "Вы те ребята, что были здесь раньше! Курой и Широки\n"
        "переживали за вас."
    ),
    ("patch_text01", "message/t01.mbe/000_Sheet1.csv", "f_t0102_0210_0040"): (
        "Нас проинформировали. Цель — в переулке впереди! Удачи!"
    ),
    ("patch_text01", "message/t01.mbe/000_Sheet1.csv", "f_t0102_0240_0010"): (
        "Сюда нельзя... Скоро эта штука придёт в движение..."
    ),
    ("patch_text01", "message/t01.mbe/000_Sheet1.csv", "f_t0103_0010_0020"): (
        "Сходи туда и проверь!"
    ),
    ("patch_text01", "message/t01.mbe/000_Sheet1.csv", "f_t0103_0120_0030"): (
        "К счастью, в том районе держали мирных дигимонов.\n"
        "Серьёзного ущерба пока нет."
    ),
    ("patch_text01", "message/t01.mbe/000_Sheet1.csv", "f_t0103_0120_0040"): (
        "Дигимоны быстро заполняют город. Это чрезвычайная ситуация!\n"
        "Мы из D-SAT должны скорее их поймать!"
    ),
    ("patch_text01", "message/t01.mbe/000_Sheet1.csv", "f_t0103_0130_0010"): (
        "Фух. Хорошо, что сбежавшие из района дигимоны\n"
        "оказались не такими агрессивными."
    ),
    ("patch_text01", "message/t01.mbe/000_Sheet1.csv", "f_t0103_0150_0020"): (
        "От этих существ можно ждать чего угодно."
    ),
    ("patch_text01", "message/t01.mbe/000_Sheet1.csv", "f_t0104_9000_0010"): (
        "Эй, ты! Вижу, у тебя есть карты! Сыграем? Не пожалеешь!"
    ),
    ("patch_text01", "message/t01.mbe/000_Sheet1.csv", "f_t0104_9000_0030"): (
        "Тьфу, с тобой неинтересно. Зря только уговаривал."
    ),
    ("patch_text01", "message/t01.mbe/000_Sheet1.csv", "f_t0107_0020_0010"): (
        "Вы явно что-то скрываете! Хватит оправдываться —\n"
        "расскажите нам правду!"
    ),
    ("patch_text01", "message/t01.mbe/000_Sheet1.csv", "f_t0107_0080_0010"): (
        "Ты тоже на протест? Не стой в стороне!\n"
        "Поднимайся и дай им себя услышать!"
    ),
    ("patch_text01", "message/t01.mbe/000_Sheet1.csv", "f_t0108_0010_0010"): (
        "В последнее время в сеть выкладывают множество видео\n"
        "со странными происшествиями в Ниси-Синдзюку..."
    ),
    ("patch_text01", "message/t01.mbe/000_Sheet1.csv", "f_t0108_0010_0030"): (
        "...и огромных тенях, бродящих по ночным улицам!\n"
        "Видео всегда быстро удаляют — значит, они настоящие!"
    ),
    ("patch_text01", "message/t01.mbe/000_Sheet1.csv", "f_t0108_0010_0050"): (
        "Значит, в Ниси-Синдзюку творится что-то подозрительное!\n"
        "Иначе и быть не может! Я это точно знаю!"
    ),
    ("patch_text01", "message/t01.mbe/000_Sheet1.csv", "f_t0108_0020_0010"): (
        "Странные явления? Хм, да. В последнее время\n"
        "об этом часто говорят..."
    ),
    ("patch_text01", "message/t01.mbe/000_Sheet1.csv", "f_t0108_0020_0020"): (
        "Но такое ведь всегда случалось, да? Хотя в последнее время\n"
        "как-то слишком часто!"
    ),
    ("patch_text01", "message/t01.mbe/000_Sheet1.csv", "f_t0108_0020_0030"): (
        "А про странную дверь в переулке Кабукитё знаешь?"
    ),
    ("patch_text01", "message/t01.mbe/000_Sheet1.csv", "f_t0108_0020_0050"): (
        "Жутко, да? Но мне всё равно хочется её увидеть!\n"
        "Где она — не знаю, а любопытно ужасно!"
    ),
    ("patch_text01", "message/t01.mbe/000_Sheet1.csv", "f_t0108_0070_0010"): (
        "Так, граждане, дальше дорога перекрыта.\n"
        "Не прикасайтесь к машинам экстренных служб."
    ),
    ("patch_text01", "message/t01.mbe/000_Sheet1.csv", "f_t0108_0090_0010"): (
        "Сейчас на станцию нельзя. Приносим извинения."
    ),
    ("patch_text01", "message/t01.mbe/000_Sheet1.csv", "f_t0108_0150_0010"): (
        "Причина перекрытия неизвестна. По слухам в сети, всё из-за\n"
        "операции службы общественной безопасности, но кто знает?"
    ),
    ("patch_text01", "message/t01.mbe/000_Sheet1.csv", "f_t0108_0160_0010"): (
        "У протестующих сбор впереди!\n"
        "Пора вывести этих мошенников на чистую воду!"
    ),
    ("patch_text01", "message/t01.mbe/000_Sheet1.csv", "f_t0109_9000_0030"): (
        "Похоже, у тебя дела. Тогда в другой раз."
    ),
    ("patch_text01", "message/t01.mbe/000_Sheet1.csv", "f_t0121_040_0020"): (
        "Да, здесь оживлённо, продажи идут хорошо. Но скоро\n"
        "пора искать новых участников."
    ),

    ("patch_text01", "message/t02.mbe/000_Sheet1.csv", "f_t0201_0010_0010"): (
        "Магазин карт закрыт на реконструкцию."
    ),
    ("patch_text01", "message/t02.mbe/000_Sheet1.csv", "f_t0201_0030_0010"): (
        "Ищешь даму в лабораторном халате? Ну ладно, так и быть!\n"
        "Сейчас открою третий глаз и—"
    ),
    ("patch_text01", "message/t02.mbe/000_Sheet1.csv", "f_t0201_0030_0020"): (
        "А? Н-не нужно?.. Понятно..."
    ),
    ("patch_text01", "message/t02.mbe/000_Sheet1.csv", "f_t0201_0150_0020"): (
        "Не хотите побаловать себя кусочком торта? Не пожалеете."
    ),
    ("patch_text01", "message/t02.mbe/000_Sheet1.csv", "f_t0201_0160_0010"): (
        "Ого! Косплей по новому аниме? Когда оно выходит?!"
    ),
    ("patch_text01", "message/t02.mbe/000_Sheet1.csv", "f_t0201_0180_0020"): (
        "Надеюсь, она строгая и воспитанная. Хотя пацанки тоже хороши...\n"
        "Хм, а может, холодная и неприступная?"
    ),
    ("patch_text01", "message/t02.mbe/000_Sheet1.csv", "f_t0201_0190_0010"): (
        "Извините, но что бы вы ни продавали, мне ничего не нужно."
    ),
    ("patch_text01", "message/t02.mbe/000_Sheet1.csv", "f_t0201_9000_0030"): (
        "Ничего страшного. Заходите как-нибудь ещё."
    ),
    ("patch_text01", "message/t02.mbe/000_Sheet1.csv", "f_t0201_9000_0040"): (
        "Эх! Пора снова учить основы карточных боёв."
    ),
    ("patch_text01", "message/t02.mbe/000_Sheet1.csv", "f_t0201_9010_0010"): (
        "Столько карт собрал — пора испытать их в деле. Сыграем?"
    ),
    ("patch_text01", "message/t02.mbe/000_Sheet1.csv", "f_t0201_9010_0040"): (
        "Чёрт! Проигрывать паршиво, но было весело!"
    ),
    ("patch_text01", "message/t02.mbe/000_Sheet1.csv", "f_t0201_9010_0050"): (
        "Ого, я выиграл! Как же весело играть с живым соперником!"
    ),
    ("patch_text01", "message/t02.mbe/000_Sheet1.csv", "f_t0201_9020_0010"): (
        "Как насчёт партии против моей колоды из редких карт?\n"
        "Давай, дай мне немного похвастаться!"
    ),
    ("patch_text01", "message/t02.mbe/000_Sheet1.csv", "f_t0201_9020_0040"): (
        "Мои редкие карты проиграли?.. Не могу поверить..."
    ),
    ("patch_text01", "message/t02.mbe/000_Sheet1.csv", "f_t0203_0040_0010"): (
        "Дальше по плану парк Синдзюку.\n"
        "Заодно прихвачу что-нибудь для доктора."
    ),
    ("patch_text01", "message/t02.mbe/000_Sheet1.csv", "f_t0203_9000_0030"): (
        "Нет?.. Эх, а на работу так не хочется..."
    ),

    ("patch_text01", "message/t03.mbe/000_Sheet1.csv", "f_t0302_0010_0010"): (
        "Что за люди? И из-за чего весь шум вокруг машины на площади?"
    ),
    ("patch_text01", "message/t03.mbe/000_Sheet1.csv", "f_t0302_0020_0010"): (
        "Что это за машина и люди? Никогда их не видел...\n"
        "А вокруг уже собралась толпа зевак."
    ),
    ("patch_text01", "message/t03.mbe/000_Sheet1.csv", "f_t0302_0100_0010"): (
        "Токийская мэрия просто огромная! Посмотри, какая высокая!"
    ),
    ("patch_text01", "message/t03.mbe/000_Sheet1.csv", "f_t0302_0100_0030"): (
        "В Японии с законом и порядком всё хорошо!\n"
        "Пусть в последнее время и творится всякое..."
    ),
    ("patch_text01", "message/t03.mbe/000_Sheet1.csv", "f_t0302_0110_0030"): (
        "Доктор Симмонс?"
    ),
    ("patch_text01", "message/t03.mbe/000_Sheet1.csv", "f_t0302_0110_0060"): (
        "В такое время шляется по Акихабаре в поисках деталей...\n"
        "Кто знает, что у неё в голове?"
    ),
    ("patch_text01", "message/t03.mbe/000_Sheet1.csv", "f_t0302_0190_0010"): (
        "Мы собрали много полезных данных, но этого всё ещё мало.\n"
        "Нужно поговорить с доктором."
    ),
    ("patch_text01", "message/t03.mbe/000_Sheet1.csv", "f_t0302_9000_0030"): (
        "Жаль. Пожалуй, пойду скоротаю время в местном кафе..."
    ),
    ("patch_text01", "message/t03.mbe/000_Sheet1.csv", "f_t0302_9000_0040"): (
        "Надо же, не ожидал проиграть. Оказывается,\n"
        "эта игра куда глубже, чем кажется."
    ),
    ("patch_text01", "message/t03.mbe/000_Sheet1.csv", "f_t0302_9000_0050"): (
        "Получилось! Я победил! Похоже, сегодня будет отличный день!"
    ),
    ("patch_text01", "message/t03.mbe/000_Sheet1.csv", "f_t0303_0030_0010"): (
        "Постойте! Выслушайте меня, прошу!"
    ),
    ("patch_text01", "message/t03.mbe/000_Sheet1.csv", "f_t0303_0050_0030"): (
        "Я пришла за ними, но нигде не могу их найти... Погодите.\n"
        "Это ведь вы играли с ними вчера?"
    ),
    ("patch_text01", "message/t03.mbe/000_Sheet1.csv", "f_t0303_0050_0040"): (
        "Что? Ах да... Погодите. Это ведь вы играли с ними вчера?"
    ),
    ("patch_text01", "message/t03.mbe/000_Sheet1.csv", "f_t0303_0050_0060"): (
        "Погодите. Это вы вчера играли с ними?"
    ),
    ("patch_text01", "message/t03.mbe/000_Sheet1.csv", "f_t0303_0130_0030"): (
        "Моя дочь застряла внутри. Похоже, её затянуло в ту аномалию,\n"
        "о которой ходят слухи."
    ),
    ("patch_text01", "message/t03.mbe/000_Sheet1.csv", "f_t0303_0130_0100"): (
        "С вашей силой у меня появился бы шанс! Прошу,\n"
        "пойдёмте со мной!"
    ),
    ("patch_text01", "message/t03.mbe/000_Sheet1.csv", "f_t0303_0140_0020"): (
        "И всё же... если сможете пойти со мной,\n"
        "я буду безмерно благодарен..."
    ),

    ("patch_text01", "message/t04.mbe/000_Sheet1.csv", "f_t0401_0010_0010"): (
        "Добро пожаловать! Если ищете одежду, вы по адресу!"
    ),
    ("patch_text01", "message/t04.mbe/000_Sheet1.csv", "f_t0401_0030_0010"): (
        "О, это вы! Заходите, заходите."
    ),
    ("patch_text01", "message/t04.mbe/000_Sheet1.csv", "f_t0401_0030_0020"): (
        "Если ищете одежду, вы по адресу!"
    ),
    ("patch_text01", "message/t04.mbe/000_Sheet1.csv", "f_t0401_0150_0020"): (
        "Хм? Ты про этот крокет? Хочешь попробовать?"
    ),
    ("patch_text01", "message/t04.mbe/000_Sheet1.csv", "f_t0401_9000_0010"): (
        "Эй! Сыграй со мной! Здесь никто не может дать мне\n"
        "достойный отпор!"
    ),
    ("patch_text01", "message/t04.mbe/000_Sheet1.csv", "f_t0401_9000_0030"): (
        "Тьфу, с тобой скучно! Ладно, найду кого-нибудь другого."
    ),
    ("patch_text01", "message/t04.mbe/000_Sheet1.csv", "f_t0401_9000_0070"): (
        "А я уже приготовился к бою! Ну что за скука?!"
    ),
    ("patch_text01", "message/t04.mbe/000_Sheet1.csv", "f_t0401_9000_0080"): (
        "Ого! Вот это победа! Для новичка неплохо."
    ),

    # Public-safety staff and anonymous news audio.
    ("patch_text01", "message/d10.mbe/000_Sheet1.csv", "f_d1001_0110_0010"): (
        "Я всё слышал от доктора Симмонс. Здесь почти всё под контролем."
    ),
    ("patch_text01", "message/d10.mbe/000_Sheet1.csv", "f_d1001_0110_0020"): (
        "Отправляйтесь помогать на другие точки установки."
    ),
    ("patch_text01", "message/d10.mbe/000_Sheet1.csv", "f_d1001_0120_0020"): (
        "Неприятно полагаться на гражданских, но выбора нет.\n"
        "Рассчитываю на вас."
    ),
    ("patch_text01", "message/d11.mbe/000_Sheet1.csv", "f_d1101_0120_0030"): (
        "Я знаю! Но что нам делать?!"
    ),
    ("patch_text01", "message/d11.mbe/000_Sheet1.csv", "f_d1101_0170_0010"): (
        "Не думал, что придётся эвакуировать гражданских именно сюда..."
    ),
    ("patch_text01", "message/d11.mbe/000_Sheet1.csv", "f_d1101_0170_0020"): (
        "Эй, вы! Сюда нельзя. Всем укрыться на площади позади."
    ),
    ("patch_text01", "message/d11.mbe/000_Sheet1.csv", "f_d1101_0170_0030"): (
        "Я слышал от доктора Симмонс, что пришлют подкрепление, но...\n"
        "Вы и есть подкрепление?"
    ),
    ("patch_text01", "message/d11.mbe/000_Sheet1.csv", "f_d1101_0170_0040"): (
        "А за вами... дигимон? Об этом я тоже слышал, но..."
    ),
    ("patch_text01", "message/d11.mbe/000_Sheet1.csv", "f_d1101_0170_0050"): (
        "Выбирать не приходится. Спасибо за помощь."
    ),
    ("patch_text01", "message/d11.mbe/000_Sheet1.csv", "f_d1104_0010_0030"): (
        "Похоже, его уже нет на подземной площади.\n"
        "Но терять бдительность нельзя..."
    ),
    ("patch_text01", "message/d11.mbe/000_Sheet1.csv", "f_d1104_0010_0040"): (
        "Вы тоже будьте начеку. Никто не знает,\n"
        "какой монстр здесь рыщет."
    ),
    ("patch_text01", "message/m090.mbe/000_Sheet1.csv", "m090_020_030"): (
        "Поступили сообщения о странном явлении в Синдзюку.\n"
        "На улицах Кабукитё обнаружено пространственное искажение."
    ),
    ("patch_text01", "message/m090.mbe/000_Sheet1.csv", "m090_020_040"): (
        "Некоторые считают, что это очередное паранормальное явление\n"
        "из тех, что участились в последнее время."
    ),
    ("patch_text01", "message/m090.mbe/000_Sheet1.csv", "m090_020_050"): (
        "На место направлены подразделения полиции\n"
        "по борьбе с беспорядками."
    ),
    ("patch_text01", "message/m200.mbe/000_Sheet1.csv", "m200_010_030"): "А-а-а!",
    ("patch_text01", "message/m210.mbe/000_Sheet1.csv", "m210_020_071"): (
        "Входящее сообщение от доктора Симмонс! Она говорит, что отдала\n"
        "батареи этим детям. Возьмите у них одну."
    ),
    ("patch_text01", "message/m235.mbe/000_Sheet1.csv", "m235_030_070"): (
        "Я почти не замечаю, что доктора Симмонс нет."
    ),
    ("patch_text01", "message/rumor_npc.mbe/000_Sheet1.csv", "r_d1001_0010_0010"): (
        "Уф... Упустили..."
    ),

    # Side quests with generic human labels.
    ("patch_text01", "message/s010_001.mbe/000_Sheet1.csv", "s010_001_300"): (
        "О, Хироко! Это ты. Как тебе эти джинсы? Стильные, правда?"
    ),
    ("patch_text01", "message/s010_001.mbe/000_Sheet1.csv", "s010_001_320"): (
        "Ах да... Рубашки словно оживают\n"
        "и сами вылетают из магазина!"
    ),
    ("patch_text01", "message/s010_001.mbe/000_Sheet1.csv", "s010_001_340"): (
        "Точно! Клянусь! Это случилось только что.\n"
        "Я как закричу: «Вор вернулся!»"
    ),
    ("patch_text01", "message/s010_001.mbe/000_Sheet1.csv", "s010_001_520"): (
        "Какое облегчение! Столько было переживаний.\n"
        "Заходите ещё, сделаю скидку!"
    ),
    ("patch_text01", "message/s010_179.mbe/000_Sheet1.csv", "s010_179_010"): (
        "Здравствуйте. Чем могу помочь? А... туалет?\n"
        "Боюсь, он сейчас занят."
    ),
    ("patch_text01", "message/s010_179.mbe/000_Sheet1.csv", "s010_179_020"): (
        "Вообще-то это уже проблема: последний посетитель\n"
        "зашёл и никак не выходит."
    ),
    ("patch_text01", "message/s010_179.mbe/000_Sheet1.csv", "s010_179_030"): (
        "И он вовсе не болен. Только бормочет про\n"
        "«капитана», «провал» и «месть»."
    ),
    ("patch_text01", "message/s010_179.mbe/000_Sheet1.csv", "s010_179_050"): (
        "Подождите. Серьёзно?! Тогда скажите ему, что пора выходить!"
    ),
    ("patch_text01", "message/s010_179.mbe/000_Sheet1.csv", "s010_179_060"): (
        "Пожалуй, я приму вашу помощь... Он выглядел пугающе,\n"
        "и мне не хочется с ним спорить."
    ),
    ("patch_text01", "message/s010_179.mbe/000_Sheet1.csv", "s010_179_080"): (
        "Понимаю, что прошу о многом, но вы очень поможете,\n"
        "если поговорите с ним."
    ),
    ("patch_text01", "message/s010_179.mbe/000_Sheet1.csv", "s010_179_090"): (
        "Я больше ничего не могу сделать. Пожалуйста,\n"
        "уговорите посетителя выйти из уборной."
    ),
    ("patch_text01", "message/s010_179.mbe/000_Sheet1.csv", "s010_179_100"): (
        "Ну и дела. Как просить людей заказывать ещё,\n"
        "если они не могут сходить в туалет?"
    ),
    ("patch_text01", "message/s010_179.mbe/000_Sheet1.csv", "s010_179_430"): (
        "Он вышел из уборной после ваших слов, верно? Спасибо!"
    ),

    ("patch_text01", "message/s095_082.mbe/000_Sheet1.csv", "s095_082_290"): (
        "Добро пожаловать! Чем могу помочь?\n"
        "Хм? Похоже на деталь фигурки..."
    ),
    ("patch_text01", "message/s095_082.mbe/000_Sheet1.csv", "s095_082_300"): (
        "Даже за двадцать лет работы не могу определить\n"
        "происхождение по одной руке."
    ),
    ("patch_text01", "message/s095_082.mbe/000_Sheet1.csv", "s095_082_310"): (
        "Но одна моя постоянная клиентка разбирается лучше меня.\n"
        "Может, спросите у неё?"
    ),
    ("patch_text01", "message/s095_082.mbe/000_Sheet1.csv", "s095_082_420"): (
        "Вам нужна подвижная фигурка\n"
        "«Милая волшебница Саёри»?"
    ),
    ("patch_text01", "message/s095_082.mbe/000_Sheet1.csv", "s095_082_430"): (
        "Вам повезло! Осталась последняя!"
    ),
    ("patch_text01", "message/s095_082.mbe/000_Sheet1.csv", "s095_082_440"): (
        "Разумеется, такая редкость стоит недёшево...\n"
        "Цена — 600 000 иен."
    ),
    ("patch_text01", "message/s095_082.mbe/000_Sheet1.csv", "s095_082_460"): (
        "Боюсь, ниже не могу. Такие товары трудно доставать..."
    ),
    ("patch_text01", "message/s095_082.mbe/000_Sheet1.csv", "s095_082_470"): (
        "Фигурку быстро раскупают. Я и так продаю её\n"
        "почти без прибыли."
    ),
    ("patch_text01", "message/s095_082.mbe/000_Sheet1.csv", "s095_082_480"): (
        "Понимаю вас, но дешевле этот товар отдать не могу."
    ),
    ("patch_text01", "message/s095_082.mbe/000_Sheet1.csv", "s095_082_490"): (
        "Это окончательная цена. Берёте?"
    ),
    ("patch_text01", "message/s095_082.mbe/000_Sheet1.csv", "s095_082_530"): (
        "Спасибо за покупку!"
    ),
    ("patch_text01", "message/s095_082.mbe/000_Sheet1.csv", "s095_082_540"): (
        "Ого... Я собирался просто поставить её на витрину.\n"
        "Не думал, что её и правда купят!"
    ),
    ("patch_text01", "message/s095_082.mbe/000_Sheet1.csv", "s095_082_560"): (
        "Вот ваша покупка и чек. Обращайтесь с ней бережно!"
    ),

    ("patch_text01", "message/s110_092.mbe/000_Sheet1.csv", "s110_092_390"): (
        "Сливки сладкие ровно в меру!\n"
        "А в тесте, кажется, есть соль?"
    ),
    ("patch_text01", "message/s110_092.mbe/000_Sheet1.csv", "s110_092_410"): (
        "А, Отец Синдзюку... Значит, дело касается дигимона.\n"
        "Расскажи, что тебя тревожит."
    ),
    ("patch_text01", "message/s110_092.mbe/000_Sheet1.csv", "s110_092_560"): (
        "Несмотря на грозный вид, Плутомон охотно слушает.\n"
        "Просто попробуй с ним поговорить."
    ),
    ("patch_text01", "message/s110_112.mbe/000_Sheet1.csv", "s110_112_010"): (
        "Этот дигимон опять в очереди. Ему бы сначала выучить\n"
        "заклинание, а потом приходить."
    ),
    ("patch_text01", "message/s110_113.mbe/000_Sheet1.csv", "s110_113_290"): (
        "У-у! Что будешь пить — розовое или золотое?\n"
        "Открою любое, какое захочешь!"
    ),
    ("patch_text01", "message/s110_113.mbe/000_Sheet1.csv", "s110_113_320"): (
        "Лады! Без проблем! Я самый богатый парень в городе! *ик*"
    ),
    ("patch_text01", "message/s110_113.mbe/000_Sheet1.csv", "s110_113_340"): (
        "Конечно, 48 000 диги. Пустяки—"
    ),
    ("patch_text01", "message/s110_113.mbe/000_Sheet1.csv", "s110_113_410"): (
        "Неплохо... Погоди! Мы же виделись прошлой ночью!\n"
        "Эм... не одолжишь денег?"
    ),
    ("patch_text01", "message/s110_113.mbe/000_Sheet1.csv", "s110_113_430"): (
        "С этими официантками так весело... Хочу остаться ещё!"
    ),
    ("patch_text01", "message/s110_113.mbe/000_Sheet1.csv", "s110_113_450"): "2 000 иен!",
    ("patch_text01", "message/s110_113.mbe/000_Sheet1.csv", "s110_113_480"): (
        "Я тратил деньги здесь и не заметил, как всё дошло до такого..."
    ),
    ("patch_text01", "message/s110_113.mbe/000_Sheet1.csv", "s110_113_490"): (
        "Эти деньги предназначались на учёбу ребёнка... Жена меня убьёт!"
    ),
    ("patch_text01", "message/s110_113.mbe/000_Sheet1.csv", "s110_113_500"): (
        "Устрой договорной бой на арене! Прибыль поделим. Неплохо, а?"
    ),
    ("patch_text01", "message/s110_113.mbe/000_Sheet1.csv", "s110_113_690"): (
        "Ура! Давай! Если заведение закроют, счёт можно не платить!"
    ),
    ("patch_text01", "message/s110_113.mbe/000_Sheet1.csv", "s110_113_750"): (
        "Обещаю. Неловко просить, но одолжишь на поезд? Скоро верну..."
    ),

    ("patch_text01", "message/s200_147.mbe/000_Sheet1.csv", "s200_147_100"): (
        "Здравствуйте. Большое спасибо,\n"
        "что помогаете искать мою подругу!"
    ),
    ("patch_text01", "message/s200_147.mbe/000_Sheet1.csv", "s200_147_120"): (
        "Итак... Примерно в это время она была здесь в костюме."
    ),
    ("patch_text01", "message/s200_147.mbe/000_Sheet1.csv", "s200_147_150"): (
        "Наверное, потому что здесь много удачных мест для фото."
    ),
    ("patch_text01", "message/s200_147.mbe/000_Sheet1.csv", "s200_147_180"): (
        "Эм... Вспомнила! На ней был костюм точь-в-точь\n"
        "как у человека рядом с вами."
    ),
    ("patch_text01", "message/s200_147.mbe/000_Sheet1.csv", "s200_147_290"): (
        "А-а! Погодите... Вы... люди?"
    ),
    ("patch_text01", "message/s200_147.mbe/000_Sheet1.csv", "s200_147_340"): (
        "Бегите! Вам нужно выбраться отсюда!\n"
        "Этот монстр скоро вернётся!"
    ),
    ("patch_text01", "message/s200_147.mbe/000_Sheet1.csv", "s200_147_450"): (
        "Нет, я видела только того монстра...\n"
        "Эм, простите, но кто вы такие?.."
    ),
    ("patch_text01", "message/s200_147.mbe/000_Sheet1.csv", "s200_147_620"): (
        "Это награда за выполнение моей просьбы. Пожалуйста, примите."
    ),
    ("patch_text01", "message/s200_147.mbe/000_Sheet1.csv", "s200_147_640"): (
        "Да, уверена, это был просто сон. Забудь о нём и отдохни."
    ),
}


# The fortune-teller quest deliberately uses human disguise labels.  These
# lines distinguish the disguise's sex from the selectable player's sex and
# remove the original pass's frequent accidental shifts between ты/вы.
NPC_DISGUISE_UPDATES: dict[tuple[str, str, str], str] = {
    ("patch_text01", "message/s090_072.mbe/000_Sheet1.csv", "s090_072_040"): (
        "Итак... Позволь взглянуть, что уготовила тебе судьба.\n"
        "Начнём с юной леди?"
    ),
    ("patch_text01", "message/s090_072.mbe/000_Sheet1.csv", "s090_072_060"): (
        "Твоя мечта — прославиться как стример. Понятно."
    ),
    ("patch_text01", "message/s090_072.mbe/000_Sheet1.csv", "s090_072_070"): (
        "Ты внимательно изучаешь мир вокруг и замечаешь аномалии.\n"
        "Похвально."
    ),
    ("patch_text01", "message/s090_072.mbe/000_Sheet1.csv", "s090_072_100"): (
        "Но будь добра ко всем, кого встретишь.\n"
        "Ко всем существам, не только к людям."
    ),
    ("patch_text01", "message/s090_072.mbe/000_Sheet1.csv", "s090_072_140"): (
        "Итак. Что ты хочешь узнать о своей судьбе?"
    ),
    ("patch_text01", "message/s090_072.mbe/000_Sheet1.csv", "s090_072_160"): (
        "О... У тебя необычная судьба. Со временем на твои плечи\n"
        "ляжет невообразимо тяжёлое бремя."
    ),
    ("patch_text01", "message/s090_072.mbe/000_Sheet1.csv", "s090_072_180"): (
        "Я всего лишь простой предсказатель.\n"
        "Человек я или нет — не всё ли равно?"
    ),
    ("patch_text01", "message/s090_072.mbe/000_Sheet1.csv", "s090_072_190"): (
        "Я знал, что сегодня ты придёшь. И хочу кое о чём попросить."
    ),
    ("patch_text01", "message/s090_072.mbe/000_Sheet1.csv", "s090_072_210"): (
        "Найди и защити их. Что скажешь? Возьмёшься?"
    ),
    ("patch_text01", "message/s090_072.mbe/000_Sheet1.csv", "s090_072_230"): (
        "Вижу, ты понимаешь, что нужно делать. Отлично."
    ),
    ("patch_text01", "message/s090_072.mbe/000_Sheet1.csv", "s090_072_240"): (
        "Хотелось бы, чтобы всё было так просто, но...\n"
        "Скажем так: обстоятельства не позволяют."
    ),
    ("patch_text01", "message/s090_072.mbe/000_Sheet1.csv", "s090_072_250"): (
        "Раз прямого отказа не прозвучало, значит, ты всё-таки\n"
        "понимаешь свою роль."
    ),
    **{
        ("patch_text01", "message/s090_072.mbe/000_Sheet1.csv", row_id):
        "Я определю, где находятся потерявшиеся дигимоны.\n"
        "Тебе нужно будет их защитить."
        for row_id in ("s090_072_260",)
    },
    ("patch_text01", "message/s090_072.mbe/000_Sheet1.csv", "s090_072_270"): (
        "Когда найдёшь их, приведи сюда.\n"
        "Я отправлю их обратно в Цифровой мир."
    ),
    ("patch_text01", "message/s090_072.mbe/000_Sheet1.csv", "s090_072_280"): (
        "Теперь следующий... Я обязательно его найду.\n"
        "Хм... Где же он? Хм-м-м..."
    ),
    ("patch_text01", "message/s090_072.mbe/000_Sheet1.csv", "s090_072_290"): "А! Вот он...!",
    ("patch_text01", "message/s090_072.mbe/000_Sheet1.csv", "s090_072_300"): "Нашёл! Теперь вижу!",
    ("patch_text01", "message/s090_072.mbe/000_Sheet1.csv", "s090_072_310"): (
        "К сожалению, больше гадание ничего не покажет.\n"
        "Дальше придётся справляться самостоятельно."
    ),
    ("patch_text01", "message/s090_072.mbe/000_Sheet1.csv", "s090_072_320"): (
        "А теперь позаботься о нём."
    ),
    ("patch_text01", "message/s090_072.mbe/000_Sheet1.csv", "s090_072_330"): (
        "Мы вернули ещё не всех. Найти следующего?"
    ),
    ("patch_text01", "message/s090_072.mbe/000_Sheet1.csv", "s090_072_350"): (
        "Благодарю за помощь. Сейчас погадаю, где искать следующего."
    ),
    ("patch_text01", "message/s090_072.mbe/000_Sheet1.csv", "s090_072_360"): (
        "Рад твоему рвению. Сейчас погадаю, где искать следующего."
    ),
    ("patch_text01", "message/s090_072.mbe/000_Sheet1.csv", "s090_072_370"): (
        "Хо-хо-хо! Сейчас погадаю, где искать следующего."
    ),
    ("patch_text01", "message/s090_072.mbe/000_Sheet1.csv", "s090_072_380"): (
        "Сейчас некогда? Возвращайся, когда освободишься."
    ),
    ("patch_text01", "message/s090_072.mbe/000_Sheet1.csv", "s090_072_390"): (
        "С делами покончено? Теперь можешь помочь с поисками?"
    ),
    ("patch_text01", "message/s090_072.mbe/000_Sheet1.csv", "s090_072_410"): (
        "Я ждал тебя. Сейчас погадаю, где искать следующего."
    ),
    ("patch_text01", "message/s090_072.mbe/000_Sheet1.csv", "s090_072_420"): (
        "У тебя всё ещё дела? Хорошо.\n"
        "Возвращайся, когда освободишься."
    ),
    ("patch_text01", "message/s090_072.mbe/000_Sheet1.csv", "s090_072_430"): (
        "Ну что? Есть успехи в поисках?"
    ),
    ("patch_text01", "message/s090_072.mbe/000_Sheet1.csv", "s090_072_440"): (
        "Похоже, дело ещё не закончено. Напомнить, где искать?"
    ),
    ("patch_text01", "message/s090_072.mbe/000_Sheet1.csv", "s090_072_460"): (
        "Понятно. Тогда позаботься о нём."
    ),
    ("patch_text01", "message/s090_072.mbe/000_Sheet1.csv", "s090_072_470"): (
        "Хорошо. Погадаю, где искать первого.\n"
        "Хм... Где же ты? Хм-м-м..."
    ),
    ("patch_text01", "message/s090_072.mbe/000_Sheet1.csv", "s090_072_480"): (
        "Первый потерявшийся — под эстакадой в Синдзюку.\n"
        "Там шумно и много рекламы..."
    ),
    ("patch_text01", "message/s090_072.mbe/000_Sheet1.csv", "s090_072_490"): (
        "И одновременно темно и светло... Ночная улица? Хм..."
    ),
    ("patch_text01", "message/s090_072.mbe/000_Sheet1.csv", "s090_072_500"): (
        "В чём дело? Вам чем-нибудь помочь?"
    ),
    ("patch_text01", "message/s090_072.mbe/000_Sheet1.csv", "s090_072_530"): (
        "...Ага, так ты знаешь. Я так и думал."
    ),
    ("patch_text01", "message/s090_072.mbe/000_Sheet1.csv", "s090_072_540"): (
        "Ошиблись человеком? Ладно, до свидания."
    ),
    ("patch_text01", "message/s090_072.mbe/000_Sheet1.csv", "s090_072_550"): (
        "Тогда незачем оставаться в этом облике.\n"
        "Но сначала отойдём в другое место."
    ),
    ("patch_text01", "message/s090_072.mbe/000_Sheet1.csv", "s090_072_630"): (
        "Вижу, первый потерявшийся уже найден.\n"
        "Я отправил его домой. Отличная работа!"
    ),
    ("patch_text01", "message/s090_072.mbe/000_Sheet1.csv", "s090_072_650"): (
        "И... я чувствую рядом растение.\n"
        "Оно скрыто от солнца?.."
    ),
    ("patch_text01", "message/s090_072.mbe/000_Sheet1.csv", "s090_072_670"): (
        "О, здравствуйте... Вам чем-то помочь?"
    ),
    ("patch_text01", "message/s090_072.mbe/000_Sheet1.csv", "s090_072_680"): (
        "{next}...Заблудилась?"
    ),
    ("patch_text01", "message/s090_072.mbe/000_Sheet1.csv", "s090_072_682"): (
        "{end}Извини, не та. До свидания."
    ),
    ("patch_text01", "message/s090_072.mbe/000_Sheet1.csv", "s090_072_690"): (
        "Кто ты? И откуда знаешь, что я потерялась?"
    ),
    ("patch_text01", "message/s090_072.mbe/000_Sheet1.csv", "s090_072_720"): (
        "Так ты уже знаешь. Да, я дигимон."
    ),
    ("patch_text01", "message/s090_072.mbe/000_Sheet1.csv", "s090_072_730"): (
        "Но вокруг слишком много людей. Давай отойдём."
    ),
    ("patch_text01", "message/s090_072.mbe/000_Sheet1.csv", "s090_072_740"): (
        "В этой форме и правда удобнее. Ах, теперь я гораздо спокойнее!"
    ),
    ("patch_text01", "message/s090_072.mbe/000_Sheet1.csv", "s090_072_750"): (
        "Я не могу вернуться домой. Ты можешь мне помочь?"
    ),
    ("patch_text01", "message/s090_072.mbe/000_Sheet1.csv", "s090_072_761"): (
        "{next}И чем ты занималась всё это время?"
    ),
    ("patch_text01", "message/s090_072.mbe/000_Sheet1.csv", "s090_072_780"): (
        "Я заходила в несколько магазинов, но так нервничала,\n"
        "что почти всё время пряталась."
    ),
    ("patch_text01", "message/s090_072.mbe/000_Sheet1.csv", "s090_072_790"): (
        "Домой, конечно! Здесь есть другие дигимоны,\n"
        "но мне тут не по себе."
    ),
    ("patch_text01", "message/s090_072.mbe/000_Sheet1.csv", "s090_072_805"): (
        "Отличная работа. Я уже отправил потерявшегося дигимона домой."
    ),
    ("patch_text01", "message/s090_072.mbe/000_Sheet1.csv", "s090_072_810"): (
        "Следующий — у восточного выхода станции Синдзюку.\n"
        "Этот успокаивающий аромат... Знакомый!"
    ),
    ("patch_text01", "message/s090_072.mbe/000_Sheet1.csv", "s090_072_820"): (
        "Ещё я вижу текстуру дерева... Мебель?"
    ),
    ("patch_text01", "message/s090_072.mbe/000_Sheet1.csv", "s090_072_870"): (
        "Что? Вот это да! Как тебе удалось меня раскрыть?\n"
        "Я был уверен, что никто не заметит!"
    ),
    ("patch_text01", "message/s090_072.mbe/000_Sheet1.csv", "s090_072_890"): (
        "Вот это да! Пожалуй, мне больше не нужно оставаться\n"
        "в этом облике."
    ),
    ("patch_text01", "message/s090_072.mbe/000_Sheet1.csv", "s090_072_900"): (
        "Но людей слишком много, отойдём в сторону!"
    ),
    ("patch_text01", "message/s090_072.mbe/000_Sheet1.csv", "s090_072_920"): (
        "Но... как тебе удалось узнать, что я дигимон?"
    ),
    ("patch_text01", "message/s090_072.mbe/000_Sheet1.csv", "s090_072_940"): (
        "Так ты дружишь с дигимонами? Значит, и я твой друг!"
    ),
    ("patch_text01", "message/s090_072.mbe/000_Sheet1.csv", "s090_072_950"): (
        "Люди пугают, поэтому я сидел тихо.\n"
        "Но с детьми хотелось поиграть."
    ),
    ("patch_text01", "message/s090_072.mbe/000_Sheet1.csv", "s090_072_960"): (
        "Ха-ха! Смешно! Неужели инстинкт подсказал тебе,\n"
        "что я дигимон?"
    ),
    ("patch_text01", "message/s090_072.mbe/000_Sheet1.csv", "s090_072_970"): (
        "Хорошо, я готов домой. Пошли!"
    ),
    ("patch_text01", "message/s090_072.mbe/000_Sheet1.csv", "s090_072_980"): (
        "Наконец-то домой! Я так счастлив!"
    ),
    ("patch_text01", "message/s090_072.mbe/000_Sheet1.csv", "s090_072_1000"): (
        "Последний... кажется, возле правительственного здания?\n"
        "Я уже выдохся..."
    ),
    ("patch_text01", "message/s090_072.mbe/000_Sheet1.csv", "s090_072_1020"): (
        "Хм... Прямо по этой дороге?.. Или надо было повернуть\n"
        "направо на прошлом перекрёстке?.."
    ),
    ("patch_text01", "message/s090_072.mbe/000_Sheet1.csv", "s090_072_1030"): (
        "Хм? Тебе чем-нибудь помочь?"
    ),
    ("patch_text01", "message/s090_072.mbe/000_Sheet1.csv", "s090_072_1040"): (
        "У тебя дело к старику?"
    ),
    ("patch_text01", "message/s090_072.mbe/000_Sheet1.csv", "s090_072_1060"): (
        "Как любезно! Но ты знаешь, где мой дом?.."
    ),
    ("patch_text01", "message/s090_072.mbe/000_Sheet1.csv", "s090_072_1080"): (
        "Что? Ошиблись человеком? Ну, до свидания."
    ),
    ("patch_text01", "message/s090_072.mbe/000_Sheet1.csv", "s090_072_1110"): (
        "Не иначе судьба свела нас. Я застрял здесь и не могу\n"
        "вернуться. Поможешь?"
    ),
    ("patch_text01", "message/s090_072.mbe/000_Sheet1.csv", "s090_072_1140"): (
        "Я сидел на скамейках и гулял. Никто ничего не заподозрил."
    ),
    ("patch_text01", "message/s090_072.mbe/000_Sheet1.csv", "s090_072_1150"): (
        "Здесь не так плохо, как я думал, но для меня слишком шумно."
    ),
    ("patch_text01", "message/s090_072.mbe/000_Sheet1.csv", "s090_072_1160"): (
        "Ну что же. Поможешь мне вернуться? Я совсем вымотался."
    ),
    ("patch_text01", "message/s090_072.mbe/000_Sheet1.csv", "s090_072_1170"): (
        "Благодаря тебе все потерявшиеся дигимоны спасены.\n"
        "Я искренне благодарен."
    ),
    ("patch_text01", "message/s090_072.mbe/000_Sheet1.csv", "s090_072_1180"): (
        "Теперь мне пора отплатить за помощь и рассказать правду."
    ),
    ("patch_text01", "message/s090_072.mbe/000_Sheet1.csv", "s090_072_1190"): (
        "Только не удивляйся. На самом деле... я дигимон!"
    ),
    ("patch_text01", "message/s090_072.mbe/000_Sheet1.csv", "s090_072_1230"): (
        "Такое удивление даже обидно.\n"
        "Неужели ничего не показалось странным?"
    ),
    ("patch_text01", "message/s090_072.mbe/000_Sheet1.csv", "s090_072_1240"): (
        "Я — Древний Вайзмон. Моя роль здесь окончена."
    ),
    ("patch_text01", "message/s090_072.mbe/000_Sheet1.csv", "s090_072_1250"): (
        "Прими это в благодарность за спасение моих собратьев."
    ),
    ("patch_text01", "message/s090_072.mbe/000_Sheet1.csv", "s090_072_1260"): (
        "В мире людей было весело, но пора домой.\n"
        "Уверен, мы ещё встретимся."
    ),
    ("patch_text01", "message/s090_072.mbe/000_Sheet1.csv", "s090_072_1270"): (
        "Вот мы и снова встретились! Я тот самый предсказатель,\n"
        "которого звали «Отцом Синдзюку»."
    ),
    ("patch_text01", "message/s090_072.mbe/000_Sheet1.csv", "s090_072_1280"): (
        "Хо-хо-хо! Похоже, дел невпроворот.\n"
        "Говорят, в молодости трудности полезны."
    ),
}


# Broad source-checked pass over unnamed human NPCs and the surrounding rows
# that must change with them for a scene to remain coherent.  Player-facing
# gender traps in static tables are phrased naturally without grammatical
# gender; runtime M/F rows are reserved for lines where neutral phrasing would
# lose characterization or meaning.
NPC_WIDE_EXTRA_UPDATES: dict[tuple[str, str, str], str] = {
    ("patch_text01", "message/t01.mbe/000_Sheet1.csv", "f_t0101_9000_0080"): (
        "Похоже, я проиграла. Отличная партия!"
    ),
    ("patch_text01", "message/t01.mbe/000_Sheet1.csv", "f_t0103_0060_0020"): (
        "Послушай... С таким нарядом тебе придётся\n"
        "пройти со мной в участок."
    ),
    ("patch_text01", "message/t01.mbe/000_Sheet1.csv", "f_t0103_0090_0010"): (
        "Андромон ведёт прямой репортаж на знаменитой театральной\n"
        "площади?! Вот это да! Надо сфотографировать!"
    ),
    ("patch_text01", "message/t01.mbe/000_Sheet1.csv", "f_t0103_9000_0030"): (
        "Нет? Хм! Ну ладно. Но серьёзно, сколько ещё он будет\n"
        "заставлять меня ждать?!"
    ),
    ("patch_text01", "message/t01.mbe/000_Sheet1.csv", "f_t0108_0180_0060"): (
        "Не могу поверить, что ты хочешь туда идти,\n"
        "когда вокруг творится такое..."
    ),
    ("patch_text01", "message/t01.mbe/000_Sheet1.csv", "f_t0104_0010_0010"): (
        "Дальше идти опасно. Не приближайтесь."
    ),
    ("patch_text01", "message/t01.mbe/000_Sheet1.csv", "f_t0107_0070_0010"): (
        "Что происходит?! Дело плохо... Неужели они стали ещё активнее?!"
    ),

    ("patch_text01", "message/t02.mbe/000_Sheet1.csv", "f_t0201_0140_0040"): (
        "И чего он так долго? Заблудился, что ли?"
    ),
    ("patch_text01", "message/t02.mbe/000_Sheet1.csv", "f_t0201_0170_0070"): (
        "Я только что видела её под эстакадой. Знаете дорогу\n"
        "рядом с аптекой?"
    ),
    ("patch_text01", "message/t02.mbe/000_Sheet1.csv", "f_t0201_9000_0050"): (
        "Похоже, я победил. Может, купите новые карты,\n"
        "если хотите взять реванш?"
    ),
    ("patch_text01", "message/t02.mbe/000_Sheet1.csv", "f_t0201_9020_0050"): (
        "Ха-ха! Мои карты не только красивы, они ещё и приносят победу!\n"
        "Не зря я спустил на них всю зарплату!"
    ),
    ("patch_text01", "message/t03.mbe/000_Sheet1.csv", "f_t0302_0110_0090"): (
        "А теперь уходите. Здесь с минуты на минуту\n"
        "снова всё перекроют."
    ),
    ("patch_text01", "message/t03.mbe/000_Sheet1.csv", "f_t0303_0130_0040"): (
        "Не могли бы вы пойти со мной и помочь? Если с моей девочкой\n"
        "что-то случится, я себе этого не прощу!"
    ),
    ("patch_text01", "message/t03.mbe/000_Sheet1.csv", "f_t0303_0130_0080"): (
        "Ладно, идёмте искать мою непослушную дочь!"
    ),
    ("patch_text01", "message/d01.mbe/000_Sheet1.csv", "f_d0107_0100_0030"): (
        "Понял, босс. За дело!"
    ),
    ("patch_text01", "message/d11.mbe/000_Sheet1.csv", "f_d1103_0030_0010"): (
        "Дальше идти опасно. Не приближайтесь."
    ),
    ("patch_text01", "message/m010.mbe/000_Sheet1.csv", "m010_200_060"): (
        "Ну... Может, он ушёл вперёд. Давай, нужно скорее\n"
        "подняться на крышу здания столичного правительства Токио!"
    ),
    ("patch_text01", "message/m010.mbe/000_Sheet1.csv", "m010_200_090"): (
        "Нам нужно попасть на крышу здания\n"
        "столичного правительства Токио!"
    ),
    ("patch_text01", "message/m070.mbe/000_Sheet1.csv", "m070_090_020"): (
        "Ничего себе, вот это скорость! Просто супер!"
    ),
    ("patch_text01", "message/s010_179.mbe/000_Sheet1.csv", "s010_179_440"): (
        "Он попросил передать это вам. Вообще-то должен был отдать сам,\n"
        "но уже ушёл."
    ),
    ("patch_text01", "message/s010_179.mbe/000_Sheet1.csv", "s010_179_450"): (
        "В общем, держите. Теперь всё, хорошо?"
    ),

    ("patch_text01", "message/s090_072.mbe/000_Sheet1.csv", "s090_072_520"): (
        "Значит, причина всё-таки есть. Похоже, ты понимаешь,\n"
        "что происходит."
    ),
    ("patch_text01", "message/s110_113.mbe/000_Sheet1.csv", "s110_113_400"): (
        "Привет! Как поживаешь?"
    ),
    ("patch_text01", "message/s110_113.mbe/000_Sheet1.csv", "s110_113_540"): (
        "Учитель, похоже, для окончательного суда над человечеством\n"
        "вы выбрали весьма необычного человека."
    ),
    ("patch_text01", "message/s110_113.mbe/000_Sheet1.csv", "s110_113_670"): (
        "Люди — такие забавные существа.\n"
        "Я не позволю дигимонам их уничтожить."
    ),
    ("patch_text01", "message/s110_113.mbe/000_Sheet1.csv", "s110_113_700"): (
        "Ни за что! Эти типы спятили! Помоги мне, Кузухамон!"
    ),

    ("patch_text01", "message/s200_147.mbe/000_Sheet1.csv", "s200_147_010"): (
        "А, вот и ты! Мне сообщили, что здесь пропала косплеерша."
    ),
    ("patch_text01", "message/s200_147.mbe/000_Sheet1.csv", "s200_147_020"): (
        "{next}Может, к этому причастен дигимон."
    ),
    ("patch_text01", "message/s200_147.mbe/000_Sheet1.csv", "s200_147_021"): (
        "{next}Может, её похитили."
    ),
    ("patch_text01", "message/s200_147.mbe/000_Sheet1.csv", "s200_147_022"): (
        "{next}Может, её унесло потусторонней силой."
    ),
    ("patch_text01", "message/s200_147.mbe/000_Sheet1.csv", "s200_147_030"): (
        "Да. Тот «призрак», которого в последнее время часто видят,\n"
        "выглядит весьма подозрительно."
    ),
    ("patch_text01", "message/s200_147.mbe/000_Sheet1.csv", "s200_147_040"): (
        "Это самая правдоподобная версия. Наверное,\n"
        "стоит обратиться в полицию."
    ),
    ("patch_text01", "message/s200_147.mbe/000_Sheet1.csv", "s200_147_050"): (
        "Этот парк известен, так что незаметным такой шаг не будет...\n"
        "Зато ролик об этой истории может разлететься по сети."
    ),
    ("patch_text01", "message/s200_147.mbe/000_Sheet1.csv", "s200_147_080"): (
        "Ладно. А пока осмотримся: вдруг заметим\n"
        "что-нибудь подозрительное."
    ),
    ("patch_text01", "message/s200_147.mbe/000_Sheet1.csv", "s200_147_140"): (
        "Терпеть жару и холод — часть косплея.\n"
        "Она всегда так говорила."
    ),
    ("patch_text01", "message/s200_147.mbe/000_Sheet1.csv", "s200_147_160"): (
        "В это время людей немного, да и она говорила,\n"
        "что все от неё разбегаются."
    ),
    ("patch_text01", "message/s200_147.mbe/000_Sheet1.csv", "s200_147_170"): (
        "Понятно... Кстати, кого она косплеила?"
    ),
    ("patch_text01", "message/s200_147.mbe/000_Sheet1.csv", "s200_147_190"): (
        "Как у тебя? Так будет проще... Надень это и пройдись вон там."
    ),
    ("patch_text01", "message/s200_147.mbe/000_Sheet1.csv", "s200_147_202"): (
        "{next}Сама надевай."
    ),
    ("patch_text01", "message/s200_147.mbe/000_Sheet1.csv", "s200_147_210"): (
        "Возможно, воссоздание обстоятельств\n"
        "поможет разгадать тайну."
    ),
    ("patch_text01", "message/s200_147.mbe/000_Sheet1.csv", "s200_147_230"): (
        "К сожалению, этот костюм мне маловат."
    ),
    ("patch_text01", "message/s200_147.mbe/000_Sheet1.csv", "s200_147_260"): (
        "Я что-то чувствую... Неужели это оно?!"
    ),
    ("patch_text01", "message/s200_147.mbe/000_Sheet1.csv", "s200_147_280"): (
        "Где мы?.."
    ),
    ("patch_text01", "message/s200_147.mbe/000_Sheet1.csv", "s200_147_310"): (
        "Да. Твоя подруга попросила нас тебя найти!"
    ),
    ("patch_text01", "message/s200_147.mbe/000_Sheet1.csv", "s200_147_360"): (
        "Отлично! Наконец-то я поймал тамера!"
    ),
    ("patch_text01", "message/s200_147.mbe/000_Sheet1.csv", "s200_147_370"): (
        "...Стоп. Почему вас так много?"
    ),
    ("patch_text01", "message/s200_147.mbe/000_Sheet1.csv", "s200_147_390"): (
        "Ты ходишь с дигимоном — значит, ты тамер!"
    ),
    ("patch_text01", "message/s200_147.mbe/000_Sheet1.csv", "s200_147_400"): (
        "Человек, который повсюду водит с собой дигимонов, как ты.\n"
        "И даже этого не знаешь?!"
    ),
    ("patch_text01", "message/s200_147.mbe/000_Sheet1.csv", "s200_147_430"): (
        "Что ж, мы как-то справились... Интересно, кто его хозяин."
    ),
    ("patch_text01", "message/s200_147.mbe/000_Sheet1.csv", "s200_147_440"): (
        "Ты здесь уже давно. Не знаешь, кто это?"
    ),
    ("patch_text01", "message/s200_147.mbe/000_Sheet1.csv", "s200_147_461"): (
        "{next}Стримерша со своей командой."
    ),
    ("patch_text01", "message/s200_147.mbe/000_Sheet1.csv", "s200_147_470"): (
        "Да, хороший ответ. Она явно растеряна,\n"
        "так что давай её успокоим."
    ),
    ("patch_text01", "message/s200_147.mbe/000_Sheet1.csv", "s200_147_500"): (
        "Как я уже сказала, твоя подруга попросила нас тебя найти."
    ),
    ("patch_text01", "message/s200_147.mbe/000_Sheet1.csv", "s200_147_510"): (
        "Но об этом потом. Сначала выберемся отсюда—"
    ),
    ("patch_text01", "message/s200_147.mbe/000_Sheet1.csv", "s200_147_600"): (
        "Да, похоже, у них есть главарь, который приказывает\n"
        "разыскивать и ловить так называемых «тамеров»."
    ),
    ("patch_text01", "message/s200_147.mbe/000_Sheet1.csv", "s200_147_670"): (
        "Да, всё было на самом деле. Дигимоны расставляют\n"
        "в этом парке ловушки, чтобы ловить людей!"
    ),
    ("patch_text01", "message/s200_147.mbe/000_Sheet1.csv", "s200_147_690"): (
        "Я вернусь в офис монтировать сегодняшний ролик.\n"
        "Куй железо, пока горячо, верно?"
    ),
    ("patch_text01", "message/s200_147.mbe/000_Sheet1.csv", "s200_147_710"): (
        "Позвонить Хироко и начать расследование?"
    ),
    ("patch_text01", "message/s200_147.mbe/000_Sheet1.csv", "s200_147_720"): (
        "{next}[Позвонить ей.]"
    ),

    ("patch_text01", "message/t04.mbe/000_Sheet1.csv", "f_t0401_9000_0050"): (
        "Похоже, и тут достойного соперника не нашлось.\n"
        "Может, пора участвовать в турнире."
    ),
    ("patch_text01", "message/t04.mbe/000_Sheet1.csv", "f_t0401_9000_0090"): (
        "Да! Я выиграл! Новичкам вроде тебя меня не победить!"
    ),
    ("patch_text01", "message/rumor_npc.mbe/000_Sheet1.csv", "r_t0103_0010_0210"): (
        "Тут кто-то сказал «дигимон»?"
    ),
    ("patch_text01", "message/rumor_npc.mbe/000_Sheet1.csv", "r_t0108_0010_0070"): (
        "Ну, надо было лучше следить за обстановкой..."
    ),
}


# Final bounded source pass over two side-quest scenes whose non-generic rows
# share terminology and address style with the generic NPC lines above.
SCENE_POLISH_UPDATES: dict[tuple[str, str, str], str] = {
    ("patch_text01", "message/s095_082.mbe/000_Sheet1.csv", "s095_082_010"): (
        "Рад тебя видеть! Знаешь... Я должен извиниться\n"
        "за прежнюю грубость."
    ),
    ("patch_text01", "message/s095_082.mbe/000_Sheet1.csv", "s095_082_020"): (
        "Буду рад, если отныне изделия этой мастерской\n"
        "сослужат тебе добрую службу."
    ),
    ("patch_text01", "message/s095_082.mbe/000_Sheet1.csv", "s095_082_030"): (
        "За материалы и работу придётся платить,\n"
        "но все наши изделия высшего качества."
    ),
    ("patch_text01", "message/s095_082.mbe/000_Sheet1.csv", "s095_082_050"): (
        "Конечно! Выбирай."
    ),
    ("patch_text01", "message/s095_082.mbe/000_Sheet1.csv", "s095_082_060"): (
        "Да, совет... Взгляни на это. Его совсем недавно\n"
        "прибило к берегу."
    ),
    ("patch_text01", "message/s095_082.mbe/000_Sheet1.csv", "s095_082_070"): (
        "Похоже на кисть от фигурки. Но какая проработка!\n"
        "Кажется, она вот-вот оживёт!"
    ),
    ("patch_text01", "message/s095_082.mbe/000_Sheet1.csv", "s095_082_080"): (
        "Ты ведь тоже ценишь тонкую работу мастера?"
    ),
    ("patch_text01", "message/s095_082.mbe/000_Sheet1.csv", "s095_082_110"): (
        "Вот это глаз! Как видишь, каждый палец\n"
        "воссоздан мастерски."
    ),
    ("patch_text01", "message/s095_082.mbe/000_Sheet1.csv", "s095_082_120"): (
        "Что ж, не все люди разбираются\n"
        "в искусстве коллекционных фигурок."
    ),
    ("patch_text01", "message/s095_082.mbe/000_Sheet1.csv", "s095_082_130"): (
        "Что? Думаешь, это настоящая человеческая рука?\n"
        "Ха-ха, не может быть... По крайней мере, надеюсь."
    ),
    ("patch_text01", "message/s095_082.mbe/000_Sheet1.csv", "s095_082_140"): (
        "В любом случае, работа замечательная.\n"
        "В ней чувствуется страсть мастера."
    ),
    ("patch_text01", "message/s095_082.mbe/000_Sheet1.csv", "s095_082_150"): (
        "Если возможно, я хотел бы получить фигурку\n"
        "из той же серии, что и эта деталь."
    ),
    ("patch_text01", "message/s095_082.mbe/000_Sheet1.csv", "s095_082_160"): (
        "Может, съездишь в Акихабару и поищешь её там?"
    ),
    ("patch_text01", "message/s095_082.mbe/000_Sheet1.csv", "s095_082_180"): (
        "О, значит, возьмёшься? Не терпится увидеть,\n"
        "что тебе удастся найти."
    ),
    ("patch_text01", "message/s095_082.mbe/000_Sheet1.csv", "s095_082_190"): (
        "В Акихабаре можно найти все последние новинки,\n"
        "так что искать лучше там."
    ),
    ("patch_text01", "message/s095_082.mbe/000_Sheet1.csv", "s095_082_200"): (
        "Понимаю, у тебя полно дел. Возвращайся, когда будет время."
    ),
    ("patch_text01", "message/s095_082.mbe/000_Sheet1.csv", "s095_082_210"): (
        "Я снова тебя прошу... Съездишь ради меня в Акихабару?"
    ),
    ("patch_text01", "message/s095_082.mbe/000_Sheet1.csv", "s095_082_230"): (
        "О, значит, возьмёшься? Не терпится увидеть,\n"
        "что тебе удастся найти."
    ),
    ("patch_text01", "message/s095_082.mbe/000_Sheet1.csv", "s095_082_240"): (
        "Всё ещё нет времени? Хорошо. Возвращайся,\n"
        "когда освободишься."
    ),
    ("patch_text01", "message/s095_082.mbe/000_Sheet1.csv", "s095_082_250"): (
        "Вот, возьми эту деталь для сравнения."
    ),
    ("patch_text01", "message/s095_082.mbe/000_Sheet1.csv", "s095_082_260"): (
        "Кстати... Вместе с этой деталью к берегу\n"
        "прибило кое-что ещё."
    ),
    ("patch_text01", "message/s095_082.mbe/000_Sheet1.csv", "s095_082_270"): (
        "Похоже, это чек из магазина моделей.\n"
        "Сначала загляни туда."
    ),
    ("patch_text01", "message/s095_082.mbe/000_Sheet1.csv", "s095_082_280"): (
        "Что ж, удачи!"
    ),
    ("patch_text01", "message/s095_082.mbe/000_Sheet1.csv", "s095_082_330"): (
        "Что это у тебя?.. А? Погоди... О!"
    ),
    ("patch_text01", "message/s095_082.mbe/000_Sheet1.csv", "s095_082_340"): (
        "Это часть лимитированной версии «За перекусом» фигурки\n"
        "из серии «Милая волшебница Саёри»!"
    ),
    ("patch_text01", "message/s095_082.mbe/000_Sheet1.csv", "s095_082_360"): (
        "Конечно! О ней тогда только и говорили.\n"
        "Неужели ты её не знаешь?!"
    ),
    ("patch_text01", "message/s095_082.mbe/000_Sheet1.csv", "s095_082_370"): (
        "Посмотри на кончики пальцев. Крошки доказывают,\n"
        "что это версия «За перекусом»."
    ),
    ("patch_text01", "message/s095_082.mbe/000_Sheet1.csv", "s095_082_380"): (
        "Фигурки — это искусство, которым, по-моему,\n"
        "должен интересоваться каждый."
    ),
    ("patch_text01", "message/s095_082.mbe/000_Sheet1.csv", "s095_082_390"): (
        "Значит, кто-то оценил тонкую проработку и попросил тебя\n"
        "найти эту фигурку?"
    ),
    ("patch_text01", "message/s095_082.mbe/000_Sheet1.csv", "s095_082_400"): (
        "Советую купить подвижную фигурку Саёри.\n"
        "Тот человек будет в восторге."
    ),
    ("patch_text01", "message/s095_082.mbe/000_Sheet1.csv", "s095_082_410"): (
        "Кстати, я хотела бы когда-нибудь встретиться с этим человеком.\n"
        "Думаю, нам нашлось бы о чём поговорить."
    ),
    ("patch_text01", "message/s095_082.mbe/000_Sheet1.csv", "s095_082_415"): (
        "Если представится случай, познакомь нас, пожалуйста.\n"
        "Думаю, нам нашлось бы о чём поговорить."
    ),
    ("patch_text01", "message/s095_082.mbe/000_Sheet1.csv", "s095_082_500"): (
        "Я только что услышала ваш разговор. Цена заметно выросла\n"
        "с тех пор, как я видела эту фигурку в последний раз."
    ),
    ("patch_text01", "message/s095_082.mbe/000_Sheet1.csv", "s095_082_510"): (
        "Я знаю, тебя попросили найти фигурку.\n"
        "Но это как-то связано с дигимоном?"
    ),
    ("patch_text01", "message/s095_082.mbe/000_Sheet1.csv", "s095_082_520"): (
        "Если она для дигимона, я её тебе куплю...\n"
        "Пожалуйста, заверните для нас."
    ),
    ("patch_text01", "message/s095_082.mbe/000_Sheet1.csv", "s095_082_550"): (
        "И чек, пожалуйста."
    ),
    ("patch_text01", "message/s095_082.mbe/000_Sheet1.csv", "s095_082_570"): (
        "Вот, держи. Подвижная фигурка Саёри теперь твоя."
    ),
    ("patch_text01", "message/s095_082.mbe/000_Sheet1.csv", "s095_082_580"): (
        "Когда-нибудь расскажешь, зачем тебе это понадобилось."
    ),
    ("patch_text01", "message/s095_082.mbe/000_Sheet1.csv", "s095_082_590"): (
        "Фигурка передана Вулканусмону."
    ),
    ("patch_text01", "message/s095_082.mbe/000_Sheet1.csv", "s095_082_600"): (
        "Ты вернулся. И что это у тебя?"
    ),
    ("patch_text01", "message/s095_082.mbe/000_Sheet1.csv", "s095_082_610"): (
        "Спасибо. Посмотрим... Погоди, неужели это то,\n"
        "о чём я думаю?!"
    ),
    ("patch_text01", "message/s095_082.mbe/000_Sheet1.csv", "s095_082_620"): (
        "Ого! Э-это невероятно! Глазам не верю!"
    ),
    ("patch_text01", "message/s095_082.mbe/000_Sheet1.csv", "s095_082_640"): (
        "«Впечатлён» — это ещё мягко сказано!\n"
        "Меня переполняют эмоции!"
    ),
    ("patch_text01", "message/s095_082.mbe/000_Sheet1.csv", "s095_082_650"): (
        "Можно объяснять целую вечность. Проработка безупречна —\n"
        "фигурка словно живая!"
    ),
    ("patch_text01", "message/s095_082.mbe/000_Sheet1.csv", "s095_082_660"): (
        "Т-тебе надоело? Что ж, я просто рад,\n"
        "что такая удивительная вещь всё-таки нашлась."
    ),
    ("patch_text01", "message/s095_082.mbe/000_Sheet1.csv", "s095_082_670"): (
        "Мастерство умельцев Акихабары превзошло все мои ожидания.\n"
        "Я обязан изучить эту фигурку."
    ),
    ("patch_text01", "message/s095_082.mbe/000_Sheet1.csv", "s095_082_680"): (
        "Работа выполнена превосходно. Огромное спасибо!\n"
        "Прими это в знак благодарности."
    ),
    ("patch_text01", "message/s095_082.mbe/000_Sheet1.csv", "s095_082_690"): (
        "Должен сказать... Акихабара — настоящий рай,\n"
        "если там полно таких вещей!"
    ),
    ("patch_text01", "message/s095_082.mbe/000_Sheet1.csv", "s095_082_700"): (
        "Не могу вечно просить других ходить вместо меня.\n"
        "Когда-нибудь сам побываю в Акихабаре!"
    ),

    ("patch_text01", "message/s110_113.mbe/000_Sheet1.csv", "s110_113_010"): (
        "А, вот и ты. Я тебя ждал."
    ),
    ("patch_text01", "message/s110_113.mbe/000_Sheet1.csv", "s110_113_030"): (
        "Внутри мой друг. Думаю зайти и проведать его."
    ),
    ("patch_text01", "message/s110_113.mbe/000_Sheet1.csv", "s110_113_050"): (
        "Ты о том, нормально ли дигимону дружить с человеком?\n"
        "У меня много друзей среди людей. Никаких проблем."
    ),
    ("patch_text01", "message/s110_113.mbe/000_Sheet1.csv", "s110_113_060"): (
        "Он человек, но настоящего имени никто толком не знает.\n"
        "Он пользуется множеством псевдонимов."
    ),
    ("patch_text01", "message/s110_113.mbe/000_Sheet1.csv", "s110_113_070"): (
        "Для обычного человека — да. Но мой друг не из слабых.\n"
        "Уверен, с ним всё хорошо."
    ),
    ("patch_text01", "message/s110_113.mbe/000_Sheet1.csv", "s110_113_090"): (
        "Из всех людей я лучше всего знаю именно его,\n"
        "так что хочу проведать."
    ),
    ("patch_text01", "message/s110_113.mbe/000_Sheet1.csv", "s110_113_100"): (
        "По результатам я решу, кого поддержать: Альфамона,\n"
        "который оценивает людей, или Короля Драсила — их защитника."
    ),
    ("patch_text01", "message/s110_113.mbe/000_Sheet1.csv", "s110_113_140"): (
        "Вы с Джесмоном станете свидетелями\n"
        "со стороны людей и дигимонов!"
    ),
    ("patch_text01", "message/s110_113.mbe/000_Sheet1.csv", "s110_113_160"): (
        "Я люблю действовать напролом. Наверное, поэтому\n"
        "мы с этим человеком так хорошо ладим."
    ),
    ("patch_text01", "message/s110_113.mbe/000_Sheet1.csv", "s110_113_200"): (
        "Ну что, теперь всё готово? Тогда идём."
    ),
    ("patch_text01", "message/s110_113.mbe/000_Sheet1.csv", "s110_113_210"): (
        "С возвращением! В нашем баре — 4 000 диги в час.\n"
        "Заходите?"
    ),
    ("patch_text01", "message/s110_113.mbe/000_Sheet1.csv", "s110_113_230"): (
        "Иначе говоря, иены! Но надо же поддерживать атмосферу,\n"
        "правда? Поэтому здесь мы называем их «диги»!"
    ),
    ("patch_text01", "message/s110_113.mbe/000_Sheet1.csv", "s110_113_240"): (
        "Ну зачем говорить об этом вслух? Так неинтересно! ♪"
    ),
    ("patch_text01", "message/s110_113.mbe/000_Sheet1.csv", "s110_113_270"): (
        "Погодите. Это что, облава?.."
    ),
    ("patch_text01", "message/s110_113.mbe/000_Sheet1.csv", "s110_113_280"): (
        "Не-а, ничего подобного. Я просто хочу кое-что проверить...\n"
        "Эй, вот он!"
    ),
    ("patch_text01", "message/s110_113.mbe/000_Sheet1.csv", "s110_113_310"): (
        "Ой, как мило! Но сначала оплати счёт,\n"
        "а потом закажем ещё, хорошо?"
    ),
    ("patch_text01", "message/s110_113.mbe/000_Sheet1.csv", "s110_113_370"): (
        "Он в своём репертуаре. Пойду-ка поговорю с ним."
    ),
    ("patch_text01", "message/s110_113.mbe/000_Sheet1.csv", "s110_113_380"): (
        "Что-то тут не так. Пойду расспрошу его."
    ),
    ("patch_text01", "message/s110_113.mbe/000_Sheet1.csv", "s110_113_390"): (
        "Теперь не вмешивайся. Моё решение должно быть беспристрастным."
    ),
    ("patch_text01", "message/s110_113.mbe/000_Sheet1.csv", "s110_113_420"): (
        "Смотря зачем. На что тебе деньги?"
    ),
    ("patch_text01", "message/s110_113.mbe/000_Sheet1.csv", "s110_113_440"): (
        "Вот как? И сколько у тебя сейчас?"
    ),
    ("patch_text01", "message/s110_113.mbe/000_Sheet1.csv", "s110_113_460"): (
        "Странно. Это правда всё, что у тебя осталось?"
    ),
    ("patch_text01", "message/s110_113.mbe/000_Sheet1.csv", "s110_113_510"): (
        "Хм... Вот, значит, как..."
    ),
    ("patch_text01", "message/s110_113.mbe/000_Sheet1.csv", "s110_113_520"): (
        "{next}Вот образцовый мерзавец."
    ),
    ("patch_text01", "message/s110_113.mbe/000_Sheet1.csv", "s110_113_550"): (
        "Почему вы так радуетесь?! Вы и всё человечество\n"
        "сейчас в большой опасности!"
    ),
    ("patch_text01", "message/s110_113.mbe/000_Sheet1.csv", "s110_113_560"): (
        "Что ж, решение принято. Теперь я знаю о людях всё, что нужно."
    ),
    ("patch_text01", "message/s110_113.mbe/000_Sheet1.csv", "s110_113_570"): (
        "П-подождите, учитель! Прошу, передумайте!\n"
        "Люди бывают разными!"
    ),
    ("patch_text01", "message/s110_113.mbe/000_Sheet1.csv", "s110_113_580"): (
        "Например, этот человек любезно объяснил мне,\n"
        "как заказывать рамен!"
    ),
    ("patch_text01", "message/s110_113.mbe/000_Sheet1.csv", "s110_113_590"): (
        "Знаю, идиот. Я говорю, что не могу бросить\n"
        "таких слабых существ на произвол судьбы!"
    ),
    ("patch_text01", "message/s110_113.mbe/000_Sheet1.csv", "s110_113_640"): (
        "Похоже, его отвратительное поведение разбудило\n"
        "в учителе желание взяться за его воспитание."
    ),
    ("patch_text01", "message/s110_113.mbe/000_Sheet1.csv", "s110_113_650"): (
        "Всё-таки учитель из тех, кто способен подружиться\n"
        "с таким странным типом..."
    ),
    ("patch_text01", "message/s110_113.mbe/000_Sheet1.csv", "s110_113_660"): (
        "Если честно, по-моему, его всё-таки признали виновным.\n"
        "Учитель точно поступает правильно?.."
    ),
    ("patch_text01", "message/s110_113.mbe/000_Sheet1.csv", "s110_113_680"): (
        "Я тебе помогу, приятель. Прикроем эту лавочку!"
    ),
    ("patch_text01", "message/s110_113.mbe/000_Sheet1.csv", "s110_113_710"): (
        "Господа, вы что-то слишком расшалились.\n"
        "Плохих мальчиков нужно наказывать, верно?"
    ),
    ("patch_text01", "message/s110_113.mbe/000_Sheet1.csv", "s110_113_720"): (
        "Я нагоню на вас такого страху, что вы больше\n"
        "никогда не будете безобразничать!"
    ),
    ("patch_text01", "message/s110_113.mbe/000_Sheet1.csv", "s110_113_740"): (
        "Запомни сегодняшний урок: больше никогда\n"
        "не трогай деньги, отложенные для ребёнка."
    ),
    ("patch_text01", "message/s110_113.mbe/000_Sheet1.csv", "s110_113_760"): (
        "Конечно. Но верни всё до копейки, иначе я приду за долгом\n"
        "к тебе домой, когда жена будет там."
    ),
    ("patch_text01", "message/s110_113.mbe/000_Sheet1.csv", "s110_113_770"): (
        "Фух. Этих денег я, похоже, больше не увижу.\n"
        "Но ему об этом не скажу."
    ),
    ("patch_text01", "message/s110_113.mbe/000_Sheet1.csv", "s110_113_780"): (
        "Так или иначе, я решил поддержать человечество.\n"
        "А значит, поддержу и ТЕБЯ!"
    ),
    ("patch_text01", "message/s110_113.mbe/000_Sheet1.csv", "s110_113_790"): (
        "Что ж, Джесмон, идём к месту встречи.\n"
        "В том бою я заметил, как сильно ты вырос."
    ),
}


for group_name, group in (
    ("DIGIMON_CHAT_INBOUND_UPDATES", DIGIMON_CHAT_INBOUND_UPDATES),
    ("DIGIMON_CHAT_VERB_FORM_UPDATES", DIGIMON_CHAT_VERB_FORM_UPDATES),
    ("NPC_NAME_UPDATES", NPC_NAME_UPDATES),
    ("NPC_FIELD_UPDATES", NPC_FIELD_UPDATES),
    ("NPC_RUMOR_UPDATES", NPC_RUMOR_UPDATES),
    ("NPC_DIALOGUE_UPDATES", NPC_DIALOGUE_UPDATES),
    ("NPC_DISGUISE_UPDATES", NPC_DISGUISE_UPDATES),
    ("NPC_WIDE_EXTRA_UPDATES", NPC_WIDE_EXTRA_UPDATES),
    ("SCENE_POLISH_UPDATES", SCENE_POLISH_UPDATES),
):
    overlap = UPDATES.keys() & group.keys()
    if overlap:
        raise ValueError(f"duplicate update keys in {group_name}: {sorted(overlap)}")
    UPDATES.update(group)


def serialization(path: Path) -> tuple[str, str, bool]:
    raw = path.read_bytes()
    bom = raw.startswith(b"\xef\xbb\xbf")
    body = raw.removeprefix(b"\xef\xbb\xbf")
    newline = "\r\n" if b"\r\n" in body else "\n"
    lines = body.splitlines()
    quote_all = len(lines) > 1 and lines[1].lstrip().startswith(b'"')
    return ("utf-8-sig" if bom else "utf-8"), newline, quote_all


def write_rows(path: Path, rows: list[list[str]]) -> None:
    encoding, newline, quote_all = serialization(path)
    with path.open("w", encoding=encoding, newline="") as handle:
        writer = csv.writer(
            handle,
            lineterminator=newline,
            quoting=csv.QUOTE_ALL if quote_all else csv.QUOTE_MINIMAL,
        )
        if quote_all:
            csv.writer(handle, lineterminator=newline).writerow(rows[0])
            writer.writerows(rows[1:])
        else:
            writer.writerows(rows)


def text_column(relative_path: str) -> int:
    return 2 if relative_path.startswith("message/") else 1


def apply_updates() -> tuple[int, int]:
    grouped: dict[tuple[str, str], dict[str, str]] = defaultdict(dict)
    for (package, relative_path, row_id), text in UPDATES.items():
        grouped[(package, relative_path)][row_id] = text

    changed = current = 0
    for (package, relative_path), wanted in grouped.items():
        path = CSV_ROOT / package / relative_path
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.reader(handle))
        column = text_column(relative_path)
        found: set[str] = set()
        dirty = False
        for row in rows[1:]:
            if not row or row[0] not in wanted:
                continue
            found.add(row[0])
            replacement = wanted[row[0]]
            if row[column] == replacement:
                current += 1
            else:
                row[column] = replacement
                changed += 1
                dirty = True
        missing = set(wanted) - found
        if missing:
            raise RuntimeError(f"Missing target rows in {path}: {sorted(missing)}")
        if dirty:
            write_rows(path, rows)
    return changed, current


def main() -> None:
    changed, current = apply_updates()
    print(f"Targets: {len(UPDATES)}")
    print(f"Changed: {changed}")
    print(f"Already current: {current}")


if __name__ == "__main__":
    main()

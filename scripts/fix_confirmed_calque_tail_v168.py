#!/usr/bin/env python3
"""Apply context-checked EN/RU calque fixes found after the v0.1.47 release."""

from __future__ import annotations

import csv
import io
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CSV_ROOT = ROOT / "csv"
BASELINE_REF = "v0.1.47"

# package, relative CSV, row id, text column, replacement
UPDATES: list[tuple[str, str, str, int, str]] = []


def add(
    relative: str,
    row_id: str,
    replacement: str,
    *,
    package: str = "patch_text01",
    column: int | None = None,
) -> None:
    if column is None:
        column = 2 if relative.startswith("message/") else 1
    UPDATES.append((package, relative, row_id, column, replacement))


# Blimpmon and Vademon scene: preserve speaker intent and shop banter.
add(
    "message/s080_059.mbe/000_Sheet1.csv",
    "s080_059_020",
    "Простите за беспокойство. Теперь я как новенький\n"
    "и снова могу летать куда угодно!",
)
add(
    "message/s080_059.mbe/000_Sheet1.csv",
    "s080_059_1030",
    "Не испытывай моё терпение, малыш...\nЯ тебе не нянька.",
)
add(
    "message/s080_059.mbe/000_Sheet1.csv",
    "s080_059_1040",
    "Такому скряге мне продавать нечего. Но если настаиваешь,\n"
    "цена — 10 000 иен.",
)
add("message/s080_059.mbe/000_Sheet1.csv", "s080_059_1070", "Хм. Приходи позавчера.")
add("message/s080_059.mbe/000_Sheet1.csv", "s080_059_1100", "Привет. Что тебе сегодня нужно?")
add(
    "message/s080_059.mbe/000_Sheet1.csv",
    "s080_059_1170",
    "Надо было сразу сказать. Ладно, продам тебе кулер.",
)


# Confirmed source-context failures and literal idioms.
add(
    "message/d310.mbe/000_Sheet1.csv",
    "d310_100_240",
    "Кстати... что они имели в виду, когда говорили, что используют\n"
    "силу Параллельмона ради своей цели?",
    package="addcont_03_text01",
)
add(
    "message/d310.mbe/000_Sheet1.csv",
    "d310_100_250",
    "Для меня это такая же загадка, как и для тебя.\n"
    "Предлагаю снова разыскать их и расспросить.",
    package="addcont_03_text01",
)
add(
    "message/d02.mbe/000_Sheet1.csv",
    "f_d0204_0440_0020",
    "Клянусь, эти сопляки такие хилые и никчёмные...",
)
add(
    "message/d02.mbe/000_Sheet1.csv",
    "f_d0204_0450_0010",
    "*вздох* Ну вот... прощай, мой перерыв...",
)
add(
    "message/d02.mbe/000_Sheet1.csv",
    "f_d0204_0450_0020",
    "Но если им не подыграть, потом проблем не оберёшься... Тьфу...",
)
add(
    "message/d05.mbe/000_Sheet1.csv",
    "f_d0506_0080_0060",
    "И восходящие звёзды, за которыми следит вся арена, —\n"
    "Стингмон и ИксВи-мон!",
)
add(
    "message/d05.mbe/000_Sheet1.csv",
    "f_d0506_0080_0070",
    "Вот с какими громилами тебе придётся сражаться на этой арене!\n"
    "А теперь будь умницей и проваливай!",
)
add(
    "message/d05.mbe/000_Sheet1.csv",
    "f_d0506_0140_0090",
    "Побеждай, добейся известности — и тогда, может быть,\n"
    "заслужишь бой с чемпионом Колизея.",
)
add(
    "message/d05.mbe/000_Sheet1.csv",
    "f_d0506_0140_0140",
    "Бахахаха! Вот тебе и чемпион СДГП...!",
)
add("message/d05.mbe/000_Sheet1.csv", "f_d0550_0010_0010", "Вот это да! Ну и повезло же нам!")
add(
    "message/d05.mbe/000_Sheet1.csv",
    "f_d0550_0010_0020",
    "И не говори! Обычно здесь предохранитель\nднём с огнём не сыщешь.",
)
add(
    "message/d05.mbe/000_Sheet1.csv",
    "f_d0550_0010_0030",
    "Вот это весело! Ещё немного вправо... Есть! Хватай!",
)
add(
    "message/s200_149.mbe/000_Sheet1.csv",
    "s200_149_750",
    "Уф! Раз уж мы ввязались, надо идти до конца, верно?\n"
    "Ну... была не была!",
)
add(
    "message/digimon_chat.mbe/000_Sheet1.csv",
    "ruche_001_1_reaction_char_LUCEMON",
    "Вот как? Одними чувствами превзойти прежнюю силу!\n"
    "Какие же люди странные.",
)
add(
    "message/digimon_chat.mbe/000_Sheet1.csv",
    "guard_001_0_char_GUARDROMON",
    "Если дело дойдёт до боя, положись на меня.",
)
add(
    "message/d220.mbe/000_Sheet1.csv",
    "d220_110_100",
    "Я знаю таких, как ты: позёр и подражатель. Накупил лучшей\n"
    "экипировки, а сам ей не соответствуешь.",
    package="addcont_02_text01",
)


# The complete broken Gekomon battle exchange, not just the two screenshot-like idioms.
add("message/battle.mbe/000_Sheet1.csv", "1120001001", "Я люблю всё: и зверушек, и растения, и даже придорожные камушки!")
add("message/battle.mbe/000_Sheet1.csv", "1120001002", "П-погоди секунду. У меня закончились заготовки...!")
add(
    "message/battle.mbe/000_Sheet1.csv",
    "1120001004",
    "Ой-ой-ой, ГЛУРП! И надо же было выдохнуться\n"
    "именно сейчас, глурп!",
)
add(
    "message/battle.mbe/000_Sheet1.csv",
    "1120001006",
    "Эх, и это в самый решающий момент, глурп...\n"
    "Ну что же такое, глурп?!",
)
add("message/battle.mbe/000_Sheet1.csv", "1120001007", "Э-эй, глурп... На нас надвигается что-то плохое, глурп!")
add(
    "message/battle.mbe/000_Sheet1.csv",
    "1120001009",
    "Туман лорда Плутомона рассеялся! Но... эти пасти...\n"
    "Их что, четыре?!",
)
add("message/battle.mbe/000_Sheet1.csv", "1120001011", "Сейчас будет мощная атака! Нам конец, глурп!")
add(
    "message/battle.mbe/000_Sheet1.csv",
    "1120001017",
    "...Ладно, нашепчи мне сладкую банальность — такую неловкую,\n"
    "чтобы мы мигом дали отсюда дёру, глурп!",
)
add(
    "message/battle.mbe/000_Sheet1.csv",
    "1120001018",
    "Слабенький пустой комплимент не сработает! Давай, быстрее!\n"
    "Скажи так, будто правда это чувствуешь!",
)
add("message/battle.mbe/000_Sheet1.csv", "1120001020", "Вот теперь я это чувствую! Пожалуй, спою во весь голос!")
add(
    "message/battle.mbe/000_Sheet1.csv",
    "1120001021",
    "Э-этот туман... Сила лорда Плутомона совсем вышла\n"
    "из-под контроля!",
)
add(
    "message/battle.mbe/000_Sheet1.csv",
    "1120001022",
    "Не могу видеть его в таком состоянии... Всё, решено!\n"
    "Теперь я иду до конца, глурп!",
)
add(
    "message/battle.mbe/000_Sheet1.csv",
    "1120001024",
    "Глурп?! Да ладно, серьёзно?! Получается?! И правда получается!\n"
    "Неплохо, глурп!",
)
add(
    "message/battle.mbe/000_Sheet1.csv",
    "1120001025",
    "Фух! Ещё бы чуть-чуть, глурп... Я едва не обмочился!\n"
    "Попади это в нас — нам был бы конец, глурп...",
)
add(
    "message/battle.mbe/000_Sheet1.csv",
    "1120001026",
    "Глурп... Ещё один сильный удар!\nМы долго так не протянем, глурп...",
)


# Additional source-aligned scene fixes.
add(
    "message/s030_029.mbe/000_Sheet1.csv",
    "s030_029_180",
    "Ты всё ещё не решаешься? Послушай, я ведь прошу о малом.\n"
    "Помоги мне, ладно?",
)
add(
    "message/s910_169.mbe/000_Sheet1.csv",
    "s910_169_490",
    "Мне нужно кое-что проверить, так что просто подожди здесь.",
)
add(
    "message/s910_169.mbe/000_Sheet1.csv",
    "s910_169_500",
    "Я свяжусь с тобой, если что-нибудь узнаю. А пока отдохни.",
)
add(
    "message/m170.mbe/000_Sheet1.csv",
    "m170_065_310",
    "Оставь это нам! Узнаем, что случилось!",
)
add(
    "message/m170.mbe/000_Sheet1.csv",
    "m170_065_320",
    "Для начала выясним, что происходит.\nПохоже, случилось что-то серьёзное.",
)
add(
    "message/d12.mbe/000_Sheet1.csv",
    "f_d1204_0600_0040",
    "Асуна наверняка лучше знает дорогу отсюда.\nПусть она нас ведёт.",
)
add(
    "message/d330.mbe/000_Sheet1.csv",
    "d330_040_040",
    "«Почему ты отказываешься действовать,\nкогда ответ у тебя перед глазами?»",
    package="addcont_03_text01",
)
add(
    "message/d330.mbe/000_Sheet1.csv",
    "d330_040_050",
    "«Параллельмон способен свободно перемещаться\n"
    "в пространстве-времени — как ты и предсказывала!»",
    package="addcont_03_text01",
)
add(
    "message/d330.mbe/000_Sheet1.csv",
    "d330_040_060",
    "«Если мы обуздаем эту силу, то, возможно, сумеем\n"
    "изменить этот обречённый мир!»",
    package="addcont_03_text01",
)
add(
    "message/s020_018.mbe/000_Sheet1.csv",
    "s020_018_1070",
    "Я присмотрю за растением и заодно буду следить за морем.\n"
    "Не волнуйся, я справлюсь.",
)
add(
    "message/s020_018.mbe/000_Sheet1.csv",
    "s020_018_1080",
    "И тебе удачи! Я хоть и остаюсь здесь, но буду думать о тебе!",
)
add(
    "message/s910_170.mbe/000_Sheet1.csv",
    "s910_170_1450",
    "Всё нормально. Здорово было встретиться с тобой...\n"
    "или, вернее, с самим собой?",
)
add(
    "message/d09.mbe/000_Sheet1.csv",
    "f_d0905_0010_0210",
    "Без неудач не бывает изобретений.\nСледующая версия будет ещё лучше.",
)
add(
    "message/d12.mbe/000_Sheet1.csv",
    "f_d1204_0530_0040",
    "Но Меркуримон всё равно не хочет полномасштабной войны,\n"
    "поэтому самые воинственные уже ушли.",
)
add(
    "message/t03.mbe/000_Sheet1.csv",
    "f_t0302_0160_0090",
    "Путь от парка к правительственному зданию уже расчищен.\n"
    "Возьмите устройство и двигайтесь туда.",
)
add(
    "message/m210.mbe/000_Sheet1.csv",
    "m210_050_020",
    "Судя по показаниям Дигивайса, вероятно, началось крайне слабое\n"
    "пространственно-временное возмущение.",
)


# Kamemon clinic exchange: restore the Digivolution term and natural motivation.
add(
    "message/d03.mbe/000_Sheet1.csv",
    "f_d0301_0250_0010",
    "Уф... Столько дел, что я уже не справляюсь!\nДаже мне становится тяжело!",
)
add(
    "message/d03.mbe/000_Sheet1.csv",
    "f_d0301_0250_0020",
    "Вы только подумайте! Я должен пробиваться сквозь огонь и леса\n"
    "и сражаться со злодеями!",
)
add(
    "message/d03.mbe/000_Sheet1.csv",
    "f_d0301_0250_0030",
    "Я хочу сражаться и эволюционировать, но из-за пациентов\n"
    "совсем не успеваю тренироваться!",
)
add("message/d03.mbe/000_Sheet1.csv", "f_d0301_0250_0040", "Ну ведь я прав?!")
add(
    "message/d03.mbe/000_Sheet1.csv",
    "f_d0301_0250_0050",
    "Правда же? Разве я не должен быть там\nи сражаться изо всех сил?!",
)
add(
    "message/d03.mbe/000_Sheet1.csv",
    "f_d0301_0250_0060",
    "Но и бросить клинику я не могу — совесть не позволяет...",
)
add(
    "message/d03.mbe/000_Sheet1.csv",
    "f_d0301_0250_0100",
    "Кстати, я слышал, что после ухода Сякомона\n"
    "его рыбное хозяйство в бухте закрылось.",
)
add(
    "message/d03.mbe/000_Sheet1.csv",
    "f_d0301_0250_0110",
    "Там столько места! При первой же возможности\n"
    "обязательно схожу туда поплавать.",
)


# High-confidence idiom and semantic mismatches from the full aligned corpus.
add(
    "message/d02.mbe/000_Sheet1.csv",
    "f_d0201_0610_0010",
    "Эй, стой! Это же слишком дорого! Ты о чём вообще?!",
)
add(
    "message/d03.mbe/000_Sheet1.csv",
    "f_d0301_0190_0020",
    "Постой. Ты ведь не умеешь плавать?!\nЗдесь слишком опасно! Проваливай!",
)
add(
    "message/d14.mbe/000_Sheet1.csv",
    "f_d1407_0030_0010",
    "Стой! Впереди обнаружена аномалия!",
)
add(
    "message/d02.mbe/000_Sheet1.csv",
    "f_d0204_0120_0050",
    "О, правда? Что ж, тогда сам с ней и разбирайся!",
)
add(
    "message/s040_160.mbe/000_Sheet1.csv",
    "s040_160_410",
    "Ха! Я тоже не ожидал так раскиснуть.\nНаверное, всё потому, что я давно не ел.",
)
add(
    "message/s040_160.mbe/000_Sheet1.csv",
    "s040_160_420",
    "Точно. Может, я просто был не в духе из-за голода.",
)
add(
    "message/d09.mbe/000_Sheet1.csv",
    "f_d0905_0060_0010",
    "Вперёд — покажи им, кто тут главный! Победа у тебя в кармане!",
)
add(
    "message/d05.mbe/000_Sheet1.csv",
    "f_d0502_0260_0020",
    "Ещё бы! Костюм будто стал легче — я справлюсь!",
)
add(
    "message/d02.mbe/000_Sheet1.csv",
    "f_d0208_0030_0010",
    "Эй, растяпа! На работе ничего не роняй!",
)
add(
    "message/s020_018.mbe/000_Sheet1.csv",
    "s020_018_1120",
    "Эй, хочешь новость? Ты не поверишь: говорят, сюда течением\n"
    "приносит всякую всячину!",
)
add(
    "text/digitter_message.mbe/000_Sheet1.csv",
    "sub_seekhiroko_020_010",
    "Что такое? Странные сны больше не снятся! А я была ТАААК\n"
    "близка к сенсации! Ну ничего, продолжу искать тему!",
)
add(
    "message/s010_156.mbe/000_Sheet1.csv",
    "s010_156_850",
    "Не заблуждайтесь: я взялся за оружие не ради спасения\n"
    "человечества, а потому, что жажду этой битвы!",
)
add(
    "message/d07.mbe/000_Sheet1.csv",
    "f_d0703_0090_0010",
    "Нашёл! Вот это да — не ожидал увидеть это здесь!\nЯ просто в шоке!",
)
add(
    "message/d310.mbe/000_Sheet1.csv",
    "d310_040_050",
    "Асуна, просьба совсем ненаучная, только не смейся...\n"
    "Ущипнёшь меня за щёку?",
    package="addcont_03_text01",
)
add(
    "message/d310.mbe/000_Sheet1.csv",
    "d310_050_090",
    "Но в этих обстоятельствах мы, возможно, сможем забыть\n"
    "о разногласиях и сражаться вместе.",
    package="addcont_03_text01",
)
add(
    "message/d320.mbe/000_Sheet1.csv",
    "d320_050_330",
    "Похоже, нам вообще не найти общего языка.",
    package="addcont_03_text01",
)
add(
    "message/s200_149.mbe/000_Sheet1.csv",
    "s200_149_700",
    "В любом случае, не стоит торчать здесь у всех на виду.",
)
add(
    "message/field_text.mbe/000_Sheet1.csv",
    "g_shop152_0110_0010",
    "Если понадобится что-нибудь изготовить в мастерской,\n"
    "я воспользуюсь опытом помощника и выполню заказ.",
)
add(
    "message/d09.mbe/000_Sheet1.csv",
    "f_d0906_0080_0010",
    "Эта штука... Нет, это всего лишь копия оригинала!",
)
add(
    "message/d09.mbe/000_Sheet1.csv",
    "f_d0906_0090_0030",
    "Я понимаю, что сейчас скажу, пожалуй, самое ненаучное\n"
    "в своей жизни, но...",
)
add(
    "message/m070.mbe/000_Sheet1.csv",
    "m070_060_020",
    "Тебе нужно лишь атаковать этих офицеров в полную силу.",
)
add(
    "message/m420.mbe/000_Sheet1.csv",
    "m420_090_030",
    "Как в круговороте времени, равновесие сохраняется, пока всё\n"
    "остаётся взаимосвязано.",
)
add(
    "message/m440.mbe/000_Sheet1.csv",
    "m440_130_030",
    "Тогда война не начнётся, и всё потерянное Инори к ней вернётся.",
)
add(
    "message/s110_211.mbe/000_Sheet1.csv",
    "s110_211_750",
    "Я пытаюсь понять, что такое справедливость.\nПозвольте взглянуть ещё раз.",
)
add(
    "message/s110_091.mbe/000_Sheet1.csv",
    "s110_091_340",
    "Забирай. Не уверен, что она нам пригодится.",
)
add(
    "message/s050_043.mbe/000_Sheet1.csv",
    "s050_043_160",
    "Тут без тебя не обойтись, Большой брат!\nПокажи, на что способен!",
)
add(
    "message/s910_171.mbe/000_Sheet1.csv",
    "s910_171_1020",
    "Такой информацией даже я не решилась бы делиться.",
)
add(
    "message/d120.mbe/000_Sheet1.csv",
    "d120_080_040",
    "Наверное... хотя мне с ними точно не везло.",
    package="addcont_01_text01",
)
add(
    "message/s910_169.mbe/000_Sheet1.csv",
    "s910_169_050",
    "Судя по началу, пожалуй, да. Но, похоже, всё не так просто.",
)
add(
    "message/m110.mbe/000_Sheet1.csv",
    "m110_010_010",
    "Подумать только, она узнала о самом существовании АДАМАС!\n"
    "Разумеется, о нашей работе нельзя рассказывать публике.",
)
add(
    "message/d02.mbe/000_Sheet1.csv",
    "f_d0201_0420_0010",
    "А знаешь что? Блимпмон доставит тебя даже туда, где нет\n"
    "станций Локомона! Он каждый день перевозит уйму грузов!",
)


# Systematic leave-it-to / «предоставить» calques.
add(
    "message/battle.mbe/000_Sheet1.csv",
    "1190120016",
    "Гехехе... Оставь это мне, я справлюсь!",
)
add(
    "message/d09.mbe/000_Sheet1.csv",
    "f_d0901_0040_0020",
    "Мы почти у цели! Остальное оставь мне!",
)
add(
    "message/d09.mbe/000_Sheet1.csv",
    "f_d0901_0080_0020",
    "Без проблем, глурп. Я справлюсь, глурп!\nНу, начали, глурп!",
)
add(
    "message/d09.mbe/000_Sheet1.csv",
    "f_d0902_0100_0010",
    "Благодаря тебе я снова встретилась с младшим братом. Спасибо.\n"
    "А теперь оставь всё нам!",
)
add(
    "message/d09.mbe/000_Sheet1.csv",
    "f_d0903_0020_0090",
    "Оставьте всё нам. И пользуйтесь нашими услугами сколько\n"
    "захотите — за счёт заведения.",
)
add("message/d09.mbe/000_Sheet1.csv", "f_d0906_0010_0085", "Я разберусь с ними!")
add(
    "message/d09.mbe/000_Sheet1.csv",
    "f_d0906_0060_0220",
    "Идите скорее, а здесь мы сами разберёмся!",
)
add(
    "message/d13.mbe/000_Sheet1.csv",
    "f_d1304_0020_0010",
    "Оставьте это мне: я отлично знаю это место.",
)
add(
    "message/digimon_chat.mbe/000_Sheet1.csv",
    "geko_001_3_reaction_char_GEKOMON",
    "Положись на меня, глурп! У меня есть зажигательный номер,\n"
    "под который все пустятся в пляс, глурп!",
)
add(
    "message/digimon_chat.mbe/000_Sheet1.csv",
    "andro_001_1_reaction_char_ANDROMON",
    "ОСТАЛЬНОЕ ОСТАВЬ МНЕ.",
)
add("message/field_text.mbe/000_Sheet1.csv", "g_shop103_0040_0010", "Я всё устрою!")
add("message/field_text.mbe/000_Sheet1.csv", "g_shop104_0040_0010", "Я всё устрою!")
add(
    "message/rumor_npc.mbe/000_Sheet1.csv",
    "r_d0903_0010_0060",
    "Я сама поймаю!",
)
add(
    "message/s010_156.mbe/000_Sheet1.csv",
    "s010_156_740",
    "Хорошо... Этот бой оставь мне.\nПора показать мою истинную силу!",
)
add(
    "message/s050_176.mbe/000_Sheet1.csv",
    "s050_176_350",
    "Придётся поручить это тебе.\nПроверишь их силы в бою вместо меня?",
)
add(
    "message/s110_098.mbe/000_Sheet1.csv",
    "s110_098_240",
    "Нет, с этим мы с Габумоном разберёмся.",
)


# Repeated Digimon-chat templates where English "thing/stuff" leaked literally.
for _age in ("child", "male", "female", "old"):
    for _trait in ("courage", "love", "friendship", "knowledge"):
        add(
            "message/digimon_chat.mbe/000_Sheet1.csv",
            f"common023_0_{_age}_{_trait}",
            "В последнее время я всё чаще понимаю,\nсколько всего ещё не знаю...",
        )
        add(
            "message/digimon_chat.mbe/000_Sheet1.csv",
            f"common037_2_reaction_{_age}_{_trait}",
            "Значит, важнее всего сила? Понятно.",
        )

add("message/digimon_chat.mbe/000_Sheet1.csv", "common029_1_replay", "Самое важное.")
add(
    "message/digimon_chat.mbe/000_Sheet1.csv",
    "common042_2_replay",
    "Нет. О таком нельзя просить.",
)


# Player choices and the directly dependent replies that exposed literal syntax.
add("message/d02.mbe/000_Sheet1.csv", "f_d0202_0080_0020", "{next}Хорошо, спасибо.")
add("message/d02.mbe/000_Sheet1.csv", "f_d0202_0080_0040", "Ну что ж, держись крепче!")
add("message/d03.mbe/000_Sheet1.csv", "f_d0302_0130_0020", "{next}Здесь выживший!")
add(
    "message/field_text.mbe/000_Sheet1.csv",
    "g_confirmation_1000_0021",
    "{next}Все дела сделаны. Отдохну до вечера.",
)
add(
    "message/m050.mbe/000_Sheet1.csv",
    "m050_030_196",
    "Погодите. Так мы с вами коллеги?{next}",
)
add(
    "message/m050.mbe/000_Sheet1.csv",
    "m050_030_200",
    "Не напрягайся. Я лишь хочу узнать, что тебе известно.",
)
add(
    "message/m060.mbe/000_Sheet1.csv",
    "m060_030_082",
    "Надеюсь, это хоть немного приблизит нас к спасению мира.{next}",
)
add(
    "message/m060.mbe/000_Sheet1.csv",
    "m060_040_081",
    "Нельзя оставлять аномалию без расследования.{next}",
)
add(
    "message/m090.mbe/000_Sheet1.csv",
    "m090_020_080",
    "Не стоит так за него переживать.{next}",
)
add(
    "message/m090.mbe/000_Sheet1.csv",
    "m090_020_100",
    "То, что случилось вчера, похоже, сильно его потрясло...",
)
add(
    "message/m110.mbe/000_Sheet1.csv",
    "m110_010_102",
    "Там мы столкнулись с тем опасным дигимоном.{next}",
)
add("message/m120.mbe/000_Sheet1.csv", "m120_040_061", "Мы вообще-то на задании.{next}")
add(
    "message/m120.mbe/000_Sheet1.csv",
    "m120_060_071",
    "Похоже, у них своя культура и общественный уклад.{next}",
)
add(
    "message/m170.mbe/000_Sheet1.csv",
    "m170_020_112",
    "Столько хлопот ради одних врат.{next}",
)
add("message/m170.mbe/000_Sheet1.csv", "m170_020_140", "Хи-хи! Похоже на то, да?")
add("message/m170.mbe/000_Sheet1.csv", "m170_020_150", "Но всё важное обычно даётся нелегко.")
add(
    "message/m230.mbe/000_Sheet1.csv",
    "m230_010_060",
    "Это Синдзюку восемь лет спустя.{next}",
)
add(
    "message/m230.mbe/000_Sheet1.csv",
    "m230_010_061",
    "Мы перенеслись на восемь лет в будущее.{next}",
)
add(
    "message/m230.mbe/000_Sheet1.csv",
    "m230_010_062",
    "Это Стена Надежды — через восемь лет после нашего времени.{next}",
)
add("message/m230.mbe/000_Sheet1.csv", "m230_010_070", "Через восемь лет?!")
add(
    "message/m230.mbe/000_Sheet1.csv",
    "m230_010_080",
    "То есть это твоё время, {player}?",
)
add(
    "message/m240.mbe/000_Sheet1.csv",
    "m240_020_341",
    "Тогда моя следующая задача — убедить Титанов отступить!{next}",
)
add("message/m260.mbe/000_Sheet1.csv", "m260_030_050", "Как там Шеллмон?{next}")
add(
    "message/m260.mbe/000_Sheet1.csv",
    "m260_080_290",
    "Хорошо, возьмёмся за это поручение.{next}",
)
add(
    "message/m310.mbe/000_Sheet1.csv",
    "m310_010_192",
    "Я в отличной физической форме.{next}",
)
add(
    "message/m310.mbe/000_Sheet1.csv",
    "m310_040_050",
    "Почему он напал на зрителей?{next}",
)
add(
    "message/m340.mbe/000_Sheet1.csv",
    "m340_010_260",
    "Тогда начнётся настоящая война.{next}",
)
add(
    "message/m350.mbe/000_Sheet1.csv",
    "m350_020_041",
    "Именем АДАМАС я доведу дело до конца.{next}",
)
add(
    "message/m390.mbe/000_Sheet1.csv",
    "m390_060_051",
    "Так ты всё это время пытался спасти Инори?{next}",
)
add(
    "message/m390.mbe/000_Sheet1.csv",
    "m390_060_060",
    "Столько раз, что я сбился со счёта. И в конце концов всё понял.",
)
add("message/m390.mbe/000_Sheet1.csv", "m390_080_080", "Однозначно нет.{next}")
add("message/s010_002.mbe/000_Sheet1.csv", "s010_002_151", "{next}Только если мне заплатят.")
add("message/s020_018.mbe/000_Sheet1.csv", "s020_018_522", "{next}Хм... Дай-ка посмотрю...")
add(
    "message/s020_018.mbe/000_Sheet1.csv",
    "s020_018_550",
    "Ч-что с тобой? Мог бы хоть сделать вид, что тебе неловко,\n"
    "даже если нам и правда придётся это прочитать...",
)
add(
    "message/s030_029.mbe/000_Sheet1.csv",
    "s030_029_201",
    "{next}Думаешь, он и правда так хорош?",
)
add(
    "message/s030_183.mbe/000_Sheet1.csv",
    "s030_183_210",
    "{next}Почему всё задрожало?",
)
add(
    "message/s030_183.mbe/000_Sheet1.csv",
    "s030_183_210__H",
    "{next}Почему всё задрожало?",
)
add(
    "message/s030_183.mbe/000_Sheet1.csv",
    "s030_183_210__F",
    "{next}Почему всё задрожало?",
)
add(
    "message/d12.mbe/000_Sheet1.csv",
    "f_d1204_0540_0010",
    "Наши силы объединились, но... Я всё равно волнуюсь...",
)
add(
    "message/d12.mbe/000_Sheet1.csv",
    "f_d1204_0540_0020",
    "Эй, без пораженческих речей! Сейчас всё решится! Ясно?!",
)
add(
    "message/d12.mbe/000_Sheet1.csv",
    "f_d1204_0540_0030",
    "Ладно-ладно, понял! Только успокойся!",
)


# Full context pass for the side quest that used many broken ShogunGekomon names.
add(
    "message/s030_029.mbe/000_Sheet1.csv",
    "s030_029_013",
    "Теперь, когда лесная деревня в безопасности,\n"
    "я хочу устроить для всех шумную вечеринку!",
)
add(
    "message/s030_029.mbe/000_Sheet1.csv",
    "s030_029_020",
    "Я уже собрал хор. Добровольцев много. Но... нет солиста.",
)
add(
    "message/s030_029.mbe/000_Sheet1.csv",
    "s030_029_030",
    "Но я знаю дигимона, чей голос сразит всех наповал!\n"
    "Тоносама Гэкомон!",
)
add(
    "message/s030_029.mbe/000_Sheet1.csv",
    "s030_029_040",
    "Вот я и ищу того, кто пригласит Тоносама Гэкомона\n"
    "стать нашим солистом.",
)
add("message/s030_029.mbe/000_Sheet1.csv", "s030_029_060", "Вижу, ты быстро схватываешь. Люблю сообразительных людей.")
add(
    "message/s030_029.mbe/000_Sheet1.csv",
    "s030_029_070",
    "Разумеется, ты! Иди и поговори с Тоносама Гэкомоном!",
)
add(
    "message/s030_029.mbe/000_Sheet1.csv",
    "s030_029_090",
    "Но, господин Бахусмон, где Тоносама Гэкомон?",
)
add(
    "message/s030_029.mbe/000_Sheet1.csv",
    "s030_029_100",
    "Перед выступлением Тоносама Гэкомон закаляет дух и разум.\n"
    "Ищи его в святилище.",
)
add(
    "message/s030_029.mbe/000_Sheet1.csv",
    "s030_029_120",
    "Если кто-то отвлекает Тоносама Гэкомона,\n"
    "уведи его подальше от нашей звезды!",
)
add(
    "message/s030_029.mbe/000_Sheet1.csv",
    "s030_029_130",
    "Если Тоносама Гэкомона там нет, найди его!\nПоможешь мне, ладно?",
)
add(
    "message/s030_029.mbe/000_Sheet1.csv",
    "s030_029_140",
    "Нет? Ну и ненадёжный же ты... Я ведь прошу о малом.\n"
    "Помоги, ладно?",
)
add(
    "message/s030_029.mbe/000_Sheet1.csv",
    "s030_029_150",
    "Тоносама Гэкомон должен быть в святилище — там он закаляет\n"
    "дух и разум перед выступлением. Приведи его сюда!",
)
add(
    "message/s030_029.mbe/000_Sheet1.csv",
    "s030_029_170",
    "Если кто-то отвлекает Тоносама Гэкомона,\n"
    "уведи его подальше от нашей звезды!",
)
add(
    "message/s030_029.mbe/000_Sheet1.csv",
    "s030_029_190",
    "Я тоже поищу Тоносама Гэкомона. Мне любопытно,\n"
    "насколько хорош его голос.",
)
add(
    "message/s030_029.mbe/000_Sheet1.csv",
    "s030_029_210",
    "Меня заботит лишь Тоносама Гэкомон.\n"
    "Что станет с вами, людьми, мне безразлично.",
)
add(
    "message/s030_029.mbe/000_Sheet1.csv",
    "s030_029_220",
    "Нет, я разделяю твои сомнения. Полагаю,\n"
    "талант Тоносама Гэкомона следует проверить.",
)
add(
    "message/s030_029.mbe/000_Sheet1.csv",
    "s030_029_230",
    "Возражай сколько хочешь, но я должен услышать его пение.\n"
    "Я отправляюсь в святилище. До встречи.",
)
add(
    "message/s030_029.mbe/000_Sheet1.csv",
    "s030_029_290",
    "Люди, вместе победим ГранКувагамона и насладимся\n"
    "чарующим пением Тоносама Гэкомона!",
)
add(
    "message/s030_029.mbe/000_Sheet1.csv",
    "s030_029_310",
    "Приятно встретить людей, которые так быстро понимают.\n"
    "Долой ГранКувагамона!",
)
add(
    "message/s030_029.mbe/000_Sheet1.csv",
    "s030_029_320",
    "Если тебе эта идея не нравится, поступай как знаешь.\n"
    "А я буду сражаться!",
)
add(
    "message/s030_029.mbe/000_Sheet1.csv",
    "s030_029_330",
    "Не хочешь сражаться? Что ж, думай сколько угодно,\n"
    "пока в тебе не вспыхнет боевой дух.",
)
add(
    "message/s030_029.mbe/000_Sheet1.csv",
    "s030_029_340",
    "ГранКувагамон и правда грозный противник...\nНо я не отступлю!",
)
add(
    "message/s030_029.mbe/000_Sheet1.csv",
    "s030_029_350",
    "Какой великолепный бой! Пение Тоносама Гэкомона\n"
    "придало мне сил.",
)
add(
    "message/s030_029.mbe/000_Sheet1.csv",
    "s030_029_370",
    "А теперь пой от всей души, Тоносама Гэкомон!\nХор тебя поддержит!",
)
add(
    "message/s030_029.mbe/000_Sheet1.csv",
    "s030_029_410",
    "Ах! Идеальная гармония, подчёркивающая голос солиста!\n"
    "Вот это группа!",
)
add("message/s030_029.mbe/000_Sheet1.csv", "s030_029_430", "Воистину. Вот это пение! Вот это музыка!")
add(
    "message/s030_029.mbe/000_Sheet1.csv",
    "s030_029_440",
    "Да. Отличная работа! Без тебя эта группа бы не собралась!",
)
add(
    "message/s030_029.mbe/000_Sheet1.csv",
    "s030_029_460",
    "Ты помог воплотить мою мечту, поэтому прими этот подарок!",
)
add(
    "message/s030_029.mbe/000_Sheet1.csv",
    "s030_029_470",
    "Эти голоса нужно сохранить... Чтобы спасти мир,\n"
    "отправимся в обетованное место!",
)
add(
    "message/s030_031.mbe/000_Sheet1.csv",
    "s030_031_130",
    "Как прекрасен хор Гэкомонов с Тоносама Гэкомоном\n"
    "в роли солиста...",
)
add("text/quest_step.mbe/000_Sheet1.csv", "31010", "Поговори с ростком в святилище.")
add("text/quest_step.mbe/000_Sheet1.csv", "31020", "Поговори с Тоносама Гэкомоном.")
add("text/quest_step.mbe/000_Sheet1.csv", "31030", "Собери семена духа.")
add("text/quest_step.mbe/000_Sheet1.csv", "31040", "Отдай семена духа Тоносама Гэкомону.")
add("text/quest_step.mbe/000_Sheet1.csv", "31050", "Послушай песню Тоносама Гэкомона.")
add(
    "text/digimon_profile.mbe/000_Sheet1.csv",
    "digimon_0376_profile",
    "Улучшенная форма Гэкомона с антенной, похожей\n"
    "на традиционный пучок феодала. Считается, что\n"
    "Тоносама Гэкомон впервые появился в системе\n"
    "оценки караоке-автомата. Рога на его плечах\n"
    "исполняют мелодию, а сам он способен петь на\n"
    "несколько регистров ниже Гэкомона, излучая\n"
    "величественную (?) ауру. Особый приём\n"
    "«Музыкальный Кулак» создаёт голосовыми связками\n"
    "и рогами сверхнизкочастотную волну, повреждающую\n"
    "данные противника. Однако, похоже, на некоторых\n"
    "врагов эти частоты действуют целительно.",
)


def csv_format(raw: bytes) -> str:
    physical_lines = raw.lstrip(b"\xef\xbb\xbf").splitlines()
    nonempty = [line for line in physical_lines if line.strip()]
    if not nonempty:
        return "minimal"
    if nonempty[0].lstrip().startswith(b'"'):
        return "all"
    if len(nonempty) > 1 and nonempty[1].lstrip().startswith(b'"'):
        return "data"
    return "minimal"


def read_document(path: Path) -> tuple[list[list[str]], str, str]:
    raw = path.read_bytes()
    encoding = "utf-8-sig" if raw.startswith(b"\xef\xbb\xbf") else "utf-8"
    with path.open("r", encoding=encoding, newline="") as handle:
        return list(csv.reader(handle)), encoding, csv_format(raw)


def read_baseline(package: str, relative: str) -> tuple[list[list[str]], str]:
    object_name = f"{BASELINE_REF}:csv/{package}/{relative}"
    result = subprocess.run(
        ["git", "show", object_name],
        cwd=ROOT,
        capture_output=True,
        check=False,
    )
    if result.returncode:
        detail = result.stderr.decode("utf-8", errors="replace").strip()
        raise SystemExit(f"Cannot read baseline {object_name}: {detail}")
    text = result.stdout.decode("utf-8-sig")
    rows = list(csv.reader(io.StringIO(text, newline="")))
    return rows, csv_format(result.stdout)


def write_document(path: Path, rows: list[list[str]], encoding: str, csv_mode: str) -> None:
    with path.open("w", encoding=encoding, newline="") as handle:
        if csv_mode == "data" and rows:
            csv.writer(handle, lineterminator="\n", quoting=csv.QUOTE_MINIMAL).writerow(rows[0])
            csv.writer(handle, lineterminator="\n", quoting=csv.QUOTE_ALL).writerows(rows[1:])
        else:
            writer = csv.writer(
                handle,
                lineterminator="\n",
                quoting=csv.QUOTE_ALL if csv_mode == "all" else csv.QUOTE_MINIMAL,
            )
            writer.writerows(rows)


def unique_row(rows: list[list[str]], row_id: str, column: int, label: str) -> list[str]:
    matches = [row for row in rows if row and row[0] == row_id]
    if len(matches) != 1 or len(matches[0]) <= column:
        raise SystemExit(f"Missing or ambiguous target {label}:{row_id}")
    return matches[0]


def main() -> None:
    markers = [(package, relative, row_id, column) for package, relative, row_id, column, _ in UPDATES]
    if len(markers) != len(set(markers)):
        raise SystemExit("Duplicate guarded target in UPDATES")

    documents: dict[tuple[str, str], list[list[str]]] = {}
    formats: dict[tuple[str, str], tuple[str, str]] = {}
    baselines: dict[tuple[str, str], list[list[str]]] = {}
    dirty: set[tuple[str, str]] = set()
    changed = current = 0

    for package, relative, row_id, column, replacement in UPDATES:
        marker = (package, relative)
        if marker not in documents:
            path = CSV_ROOT / package / relative
            rows, encoding, _ = read_document(path)
            documents[marker] = rows
            baseline_rows, baseline_format = read_baseline(package, relative)
            formats[marker] = (encoding, baseline_format)
            baselines[marker] = baseline_rows

        label = f"{package}:{relative}"
        row = unique_row(documents[marker], row_id, column, label)
        baseline_row = unique_row(baselines[marker], row_id, column, f"{BASELINE_REF}:{label}")
        if row[column] == replacement:
            current += 1
        elif row[column] == baseline_row[column]:
            row[column] = replacement
            changed += 1
            dirty.add(marker)
        else:
            raise SystemExit(
                f"Unexpected text {label}:{row_id}:\n"
                f"baseline={baseline_row[column]!r}\n"
                f"current={row[column]!r}\n"
                f"replacement={replacement!r}"
            )

    for marker in sorted(dirty):
        package, relative = marker
        encoding, csv_mode = formats[marker]
        write_document(CSV_ROOT / package / relative, documents[marker], encoding, csv_mode)

    print(f"Baseline: {BASELINE_REF}")
    print(f"Guarded targets: {len(UPDATES)}")
    print(f"Changed: {changed}")
    print(f"Already current: {current}")
    print(f"Files written: {len(dirty)}")


if __name__ == "__main__":
    main()

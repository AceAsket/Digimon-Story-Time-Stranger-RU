#!/usr/bin/env python3
"""Apply only the manually confirmed tail of the v071 style audit.

The frozen review CSV supplies the expected old text; ``REWRITES`` is the
independently reviewed exact-ID allow-list.  The updater preflights every
target before any write and refuses stale, missing, or ambiguous rows.  It is
intentionally separate from the broader v071 contextual pass.
"""

from __future__ import annotations

import csv
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CSV_ROOT = ROOT / "csv"
REVIEW_CSV = ROOT / "exports" / "dialogue_style_confirmed_review_v072.csv"


@dataclass(frozen=True)
class Rewrite:
    replacement: str
    reason: str


REWRITES: dict[tuple[str, str, str], Rewrite] = {
    (
        "addcont_02_text01",
        "message/d220.mbe/000_Sheet1.csv",
        "d220_090_060",
    ): Rewrite(
        "Они наконец поняли друг друга...\n"
        "Похоже, кулаки и правда помогли им договориться!",
        "английская идиома fists did the talking была переведена буквально",
    ),
    (
        "patch_text01",
        "message/arena01.mbe/000_Sheet1.csv",
        "arena01_f001_003_030",
    ): Rewrite(
        "«Монзаэмон и друзья» уже здесь! Они до боли знакомы,\n"
        "но хоть убей — не могу вспомнить!",
        "калька sure do look familiar звучала механически",
    ),
    (
        "patch_text01",
        "message/arena01.mbe/000_Sheet1.csv",
        "arena01_m320_030_020",
    ): Rewrite(
        "Без лишних слов встречаем чемпиона Гран-при подземелья\n"
        "Синдзюку — бойца, по праву достойного этого титула!",
        "лишняя запятая разрывала определение и делала реплику неестественной",
    ),
    (
        "patch_text01",
        "message/battle.mbe/000_Sheet1.csv",
        "1200020150",
    ): Rewrite(
        "Уф... Брат с сестрой выкладываются по полной...",
        "showing up означает хорошо проявлять себя, а не физически являться",
    ),
    (
        "patch_text01",
        "message/d01.mbe/000_Sheet1.csv",
        "f_d0101_0120_0040",
    ): Rewrite(
        "...тогда может появиться ГрейсНовамон.",
        "убраны калька-усилитель и лишний пробел; имя приведено к принятому написанию",
    ),
    (
        "patch_text01",
        "message/d02.mbe/000_Sheet1.csv",
        "f_d0201_810_0030",
    ): Rewrite(
        "Надо признать, тот парень был силён. Я бы с удовольствием\n"
        "сразился с ним ещё раз.",
        "them ошибочно превратило одного соперника во множественное число",
    ),
    (
        "patch_text01",
        "message/d02.mbe/000_Sheet1.csv",
        "f_d0202_0090_0050",
    ): Rewrite(
        "Однако прогнать Титанов непросто... Похоже,\n"
        "люди — очень крепкие создания.",
        "исправлена калька pretty tough creatures и русская связка",
    ),
    (
        "patch_text01",
        "message/d02.mbe/000_Sheet1.csv",
        "f_d0202_0490_0020",
    ): Rewrite(
        "...Но они научили нас сражаться, так что я всё-таки\n"
        "кое-что получила. Странное чувство.",
        "буквальный каркас упрощён; форма получила согласована с Архнемон",
    ),
    (
        "patch_text01",
        "message/d02.mbe/000_Sheet1.csv",
        "f_d0202_0530_0030",
    ): Rewrite(
        "Что ж, вражеский генерал сбежал, так что с этой стороны\n"
        "всё должно быть в порядке.",
        "in this regard было переведено буквальным канцелярским оборотом",
    ),
    (
        "patch_text01",
        "message/d02.mbe/000_Sheet1.csv",
        "f_d0203_0010_0040",
    ): Rewrite(
        "\"Если проголодаетесь, купите немного ДигиМяса в магазине\n"
        "на главной улице. Только не переедайте — оно очень вкусное!\"",
        "исправлены падеж ДигиМяса и буквальная конструкция it's really good",
    ),
    (
        "patch_text01",
        "message/d02.mbe/000_Sheet1.csv",
        "f_d0204_0470_0020",
    ): Rewrite(
        "О, а ты выглядишь аппетитно. С какой бы части начать...",
        "убрана механическая связка теперь, какую часть мне съесть первой",
    ),
    (
        "patch_text01",
        "message/d03.mbe/000_Sheet1.csv",
        "f_d0301_0250_0080",
    ): Rewrite(
        "И всё же, пожалуй, мне не помешал бы перерыв.",
        "starting to think было калькировано как начинаю думать",
    ),
    (
        "patch_text01",
        "message/d03.mbe/000_Sheet1.csv",
        "f_d0302_0160_0030",
    ): Rewrite(
        "Я борюсь! Борюсь за свою жизнь! А ты так и будешь\n"
        "стоять и смотреть?!",
        "are you really gonna stand было переведено громоздкой калькой",
    ),
    (
        "patch_text01",
        "message/d04.mbe/000_Sheet1.csv",
        "f_d0404_0380_0020",
    ): Rewrite(
        "Давно не виделись! Рад тебя видеть. Как видишь, я сильно\n"
        "изменился, но у меня всё хорошо.",
        "my appearance has changed было переведено механически",
    ),
    (
        "patch_text01",
        "message/d05.mbe/000_Sheet1.csv",
        "f_d0501_0080_0020",
    ): Rewrite(
        "Вы точно не Титаны. Но сейчас сюда лучше не соваться.",
        "this really isn't the best time было передано буквальной конструкцией",
    ),
    (
        "patch_text01",
        "message/d05.mbe/000_Sheet1.csv",
        "f_d0551_0020_0010",
    ): Rewrite(
        "Эй, Газимон! В Зале Героя Кокувамона было так весело!",
        "Kokuwamon place — Зал Героя Кокувамона, а не место «в Кокувамоне»",
    ),
    (
        "patch_text01",
        "message/d07.mbe/000_Sheet1.csv",
        "f_d0703_9010_0050",
    ): Rewrite(
        "Наконец-то я победил! Все соперники были мне не по зубам,\n"
        "и поражения шли одно за другим.",
        "out of my league и losing streak были переведены буквальными кальками",
    ),
    (
        "patch_text01",
        "message/d09.mbe/000_Sheet1.csv",
        "f_d0902_0030_0130",
    ): Rewrite(
        "Я всего лишь расстаюсь с жизнью, которая и так висит\n"
        "на волоске. Думаю, это небольшая цена.",
        "rather small price было передано неестественным усилителем",
    ),
    (
        "patch_text01",
        "message/d09.mbe/000_Sheet1.csv",
        "f_d0903_0030_0110",
    ): Rewrite(
        "Этот фрукт тоже висит высоко, так что поступим,\n"
        "как в прошлый раз.",
        "восстановлен предмет разговора и убран механический каркас",
    ),
    (
        "patch_text01",
        "message/d09.mbe/000_Sheet1.csv",
        "f_d0903_0040_0100",
    ): Rewrite(
        "Этот фрукт тоже висит высоко. Но теперь мы знаем,\n"
        "что делать!",
        "восстановлен предмет разговора и естественная формулировка",
    ),
    (
        "patch_text01",
        "message/d09.mbe/000_Sheet1.csv",
        "f_d0904_0210_0020",
    ): Rewrite(
        "Здесь всё очень плохо. Как видите, Нептунемон\n"
        "и остальные уже сражаются.",
        "engaged in battle было переведено канцелярским участвуют в битве",
    ),
    (
        "patch_text01",
        "message/d09.mbe/000_Sheet1.csv",
        "f_d0904_0440_0010",
    ): Rewrite(
        "Простите, но для меня это очень важно. Я хочу помочь\n"
        "всем, чем смогу!",
        "as helpful as I can было переведено буквальной сравнительной конструкцией",
    ),
    (
        "patch_text01",
        "message/d09.mbe/000_Sheet1.csv",
        "f_d0905_0010_0170",
    ): Rewrite(
        "Однако есть одна серьёзная проблема...",
        "rather significant problem не требует громоздкого усилителя",
    ),
    (
        "patch_text01",
        "message/d09.mbe/000_Sheet1.csv",
        "f_d0905_0080_0060",
    ): Rewrite(
        "Точно! Пора включить мост. Мы немного отстаём\n"
        "от графика, так что поторопись, Кокувамон!",
        "Indeed и let's activate были переведены дословно и неразговорно",
    ),
    (
        "patch_text01",
        "message/d09.mbe/000_Sheet1.csv",
        "f_d0905_0120_0020",
    ): Rewrite(
        "Место необычное: если упадёте, вернётесь к началу.\n"
        "Просто пробуйте снова и двигайтесь вперёд.",
        "убрана калька продолжайте пытаться двигаться вперёд",
    ),
    (
        "patch_text01",
        "message/d09.mbe/000_Sheet1.csv",
        "f_d0905_0130_0030",
    ): Rewrite(
        "Прошу прощения за лорда Вулканусмона...\n"
        "Просто сделай всё, что сможешь, ладно?",
        "sorry about Lord Vulcanusmon означает извинение за него, а не сожаление о нём",
    ),
    (
        "patch_text01",
        "message/d12.mbe/000_Sheet1.csv",
        "f_d1205_0020_0040",
    ): Rewrite(
        "Вы — моя единственная надежда. Не хочу вас обременять,\n"
        "но очень прошу помочь.",
        "hate to make trouble и hope you can help были калькированы",
    ),
    (
        "patch_text01",
        "message/field_text.mbe/000_Sheet1.csv",
        "dummy_dlc010_0490",
    ): Rewrite(
        "Я правда... не хочу сражаться...",
        "fight означает сражаться, а не ссориться",
    ),
    (
        "patch_text01",
        "message/field_text.mbe/000_Sheet1.csv",
        "g_tutorial_1002_0020",
    ): Rewrite(
        "Эти функции основаны на теориях доктора Юки.\n"
        "Его изобретения внесли огромный вклад в развитие общества.",
        "убраны буквальные каркасы theories given to us и indeed",
    ),
    (
        "patch_text01",
        "message/m010.mbe/000_Sheet1.csv",
        "m010_040_090",
    ): Rewrite(
        "Страх и гнев толпы чувствуются даже отсюда.",
        "you can feel описывает атмосферу, а не утверждает чувство героя",
    ),
    (
        "patch_text01",
        "message/m040.mbe/000_Sheet1.csv",
        "m040_030_090",
    ): Rewrite(
        "Я о твоём... как это сейчас молодёжь называет? \"Косплей\"?\n"
        "Надо признать, выглядит стильно...",
        "dapper look и I'll give you that были переведены буквальными оборотами",
    ),
    (
        "patch_text01",
        "message/m050.mbe/000_Sheet1.csv",
        "m050_030_070",
    ): Rewrite(
        "Ну, работать я могу когда угодно. У частного сыщика\n"
        "свободный график.",
        "flexible life было калькировано как гибкая жизнь",
    ),
    (
        "patch_text01",
        "message/m070.mbe/000_Sheet1.csv",
        "m070_040_020",
    ): Rewrite(
        "Не верю своим глазам! Ты здесь, прямо передо мной!\n"
        "Настоящая фазово-электронная форма жизни!",
        "двойной буквальный усилитель делал эмоциональную реплику механической",
    ),
    (
        "patch_text01",
        "message/m090.mbe/000_Sheet1.csv",
        "m090_080_260",
    ): Rewrite(
        "Уже поздно. Давайте на сегодня закончим,\n"
        "а завтра решим, что делать дальше.",
        "call it a night требовал разговорной, а не буквальной формулировки",
    ),
    (
        "patch_text01",
        "message/m100.mbe/000_Sheet1.csv",
        "m100_030_190",
    ): Rewrite(
        "Правда, это пока лишь прототип, поэтому он получился\n"
        "довольно громоздким.",
        "убран повтор местоимения и восстановлена естественная причинная связка",
    ),
    (
        "patch_text01",
        "message/m120.mbe/000_Sheet1.csv",
        "m120_030_060",
    ): Rewrite(
        "Получилось! Мы и правда в Цифровом мире!",
        "we made it было ошибочно переведено как мы сделали это",
    ),
    (
        "patch_text01",
        "message/m120.mbe/000_Sheet1.csv",
        "m120_080_110",
    ): Rewrite(
        "Если это правда, принесите мне доказательства.",
        "proof требовало множественной/собирательной формы доказательства",
    ),
    (
        "patch_text01",
        "message/m150.mbe/000_Sheet1.csv",
        "m150_170_060",
    ): Rewrite(
        "Полагаю, вы правы. Вы все оказали нам огромную помощь.\n"
        "Надеюсь, вы благополучно вернётесь в свой мир.",
        "pray здесь означает надежду, а буквальное молюсь звучало неестественно",
    ),
    (
        "patch_text01",
        "message/m160.mbe/000_Sheet1.csv",
        "m160_040_030",
    ): Rewrite(
        "Несомненно, это лишь малая часть истинных возможностей\n"
        "Великого Хранителя. Какой счастливый день...",
        "fortuitous day indeed был переведён калькой с неверным порядком слов",
    ),
    (
        "patch_text01",
        "message/m170.mbe/000_Sheet1.csv",
        "m170_065_140",
    ): Rewrite(
        "...Мне правда очень жаль.",
        "real sorry не требует формального сожалею обо всём этом",
    ),
    (
        "patch_text01",
        "message/m170.mbe/000_Sheet1.csv",
        "m170_090_100",
    ): Rewrite(
        "Я сильно в вас ошибался.",
        "misjudged означает ошибся в оценке, а не обязательно недооценил",
    ),
    (
        "patch_text01",
        "message/m180.mbe/000_Sheet1.csv",
        "m180_030_030",
    ): Rewrite(
        "Если так, надо спешить! Вперёд! Инори, не отходи от меня!",
        "убрана калька we'd really better hurry; stay behind me передано по смыслу",
    ),
    (
        "patch_text01",
        "message/m180.mbe/000_Sheet1.csv",
        "m180_040_020",
    ): Rewrite(
        "Они застали меня врасплох. Без вас мне пришлось бы туго!",
        "пассивная калька была застигнута делала живую реплику механической",
    ),
    (
        "patch_text01",
        "message/m235.mbe/000_Sheet1.csv",
        "m235_010_110",
    ): Rewrite(
        "Раз уж вы об этом заговорили... кажется,\n"
        "я где-то вас видел...",
        "now that you mention it было переведено буквально",
    ),
    (
        "patch_text01",
        "message/m260.mbe/000_Sheet1.csv",
        "m260_040_030",
    ): Rewrite(
        "Если конфликт начался из-за борьбы за этот ресурс,\n"
        "решить его будет непросто.",
        "громоздкий условный каркас был калькой с английского",
    ),
    (
        "patch_text01",
        "message/m400.mbe/000_Sheet1.csv",
        "m400_011_020",
    ): Rewrite(
        "Однако они поссорились, и теперь обстановка\n"
        "крайне напряжённая.",
        "current situation было переведено канцелярским текущая ситуация",
    ),
    (
        "patch_text01",
        "message/rumor_npc.mbe/000_Sheet1.csv",
        "r_d0502_0020_0060",
    ): Rewrite(
        "Ну и огромное же место... Совсем выбился из сил...",
        "wears me out было передано неестественной возвратной конструкцией",
    ),
    (
        "patch_text01",
        "message/s010_156.mbe/000_Sheet1.csv",
        "s010_156_605",
    ): Rewrite(
        "Ты правда собираешься с ним сражаться?! Прости,\n"
        "я могу поддержать тебя только морально. Удачи!",
        "fight ошибочно передано как бороться с этим; убрана калька all I can offer",
    ),
    (
        "patch_text01",
        "message/s010_180.mbe/000_Sheet1.csv",
        "s010_180_070",
    ): Rewrite(
        "Хм... Твой костюм тоже неплох, но тем легендарным\n"
        "косплеерам он всё же уступает.",
        "those legends было переведено буквальным те легенды без опорного слова",
    ),
    (
        "patch_text01",
        "message/s020_013.mbe/000_Sheet1.csv",
        "s020_013_140",
    ): Rewrite(
        "Кольцо было простым, но его сделали из драгоценного\n"
        "синего дигизоида.",
        "материал ошибочно относился к дизайну, а не к кольцу",
    ),
    (
        "patch_text01",
        "message/s020_013.mbe/000_Sheet1.csv",
        "s020_013_290",
    ): Rewrite(
        "Синий хрондигизойт — очень ценный металл.\n"
        "Кольцо скажет всё за меня.",
        "довольно драгоценный — неестественная калька quite precious",
    ),
    (
        "patch_text01",
        "message/s020_013.mbe/000_Sheet1.csv",
        "s020_013_380",
    ): Rewrite(
        "Верно. Нептунемон не стал бы действовать необдуманно...\n"
        "А, придумала!",
        "I have it означает придумала, а не у меня получилось",
    ),
    (
        "patch_text01",
        "message/s020_018.mbe/000_Sheet1.csv",
        "s020_018_1050",
    ): Rewrite(
        "Что ж, мы многому научились. Спасибо за помощь!\n"
        "Вот, возьмите это в награду за труды.",
        "take this for your trouble означает награду, а не плату за беспокойство",
    ),
    (
        "patch_text01",
        "message/s030_030.mbe/000_Sheet1.csv",
        "s030_030_320",
    ): Rewrite(
        "Выходит, мы так усердно скрывали свою базу,\n"
        "что теперь почти невозможно вести переговоры.",
        "overzealous concealment было переведено тяжёлой номинальной калькой",
    ),
    (
        "patch_text01",
        "message/s030_030.mbe/000_Sheet1.csv",
        "s030_030_470",
    ): Rewrite(
        "Спасибо тебе за такую заботу! Квок-квок!",
        "Squawk — птичий возглас, а не повелительное Кричи",
    ),
    (
        "patch_text01",
        "message/s030_030.mbe/000_Sheet1.csv",
        "s030_030_480",
    ): Rewrite(
        "Мои домашние сладости стали очень популярны.\n"
        "Похоже, всем они нравятся. Хе-хе!",
        "убран двойной механический усилитель действительно",
    ),
    (
        "patch_text01",
        "message/s040_160.mbe/000_Sheet1.csv",
        "s040_160_040",
    ): Rewrite(
        "Ещё бы. Мне ведь пришлось одолеть собственного\n"
        "старшего брата...",
        "of course I am отвечало на подавленность; боюсь было смысловой ошибкой",
    ),
    (
        "patch_text01",
        "message/s040_160.mbe/000_Sheet1.csv",
        "s040_160_300",
    ): Rewrite(
        "Ух... Но я ведь немного поработал. Значит,\n"
        "хотя бы перекус заслужил, верно?",
        "английский причинный каркас был перенесён буквально",
    ),
    (
        "patch_text01",
        "message/s050_039.mbe/000_Sheet1.csv",
        "s050_039_140",
    ): Rewrite(
        "Я надеялся, что ты не просто посмотришь,\n"
        "а найдёшь его и принесёшь обратно.",
        "maybe actually find it было переведено неестественной вставкой действительно",
    ),
    (
        "patch_text01",
        "message/s050_043.mbe/000_Sheet1.csv",
        "s050_043_580",
    ): Rewrite(
        "Что? Думаешь, я поверю? Нет здесь никаких...\n"
        "украшений...",
        "here в оборванной реплике ошибочно превратилось в вот",
    ),
    (
        "patch_text01",
        "message/s050_043.mbe/000_Sheet1.csv",
        "s050_043_590",
    ): Rewrite(
        "Оно ярко сверкает и очень красивое. Размером примерно\n"
        "с то, что... у тебя в руках...",
        "got there ошибочно переведено как вот оно",
    ),
    (
        "patch_text01",
        "message/s050_152.mbe/000_Sheet1.csv",
        "s050_152_720",
    ): Rewrite(
        "Да. Именно. Мне не терпится что-нибудь сделать\n"
        "с этими типами...",
        "случайный верхний регистр и калька eager to do something исправлены",
    ),
    (
        "patch_text01",
        "message/s050_176.mbe/000_Sheet1.csv",
        "s050_176_290",
    ): Rewrite(
        "Неужели так можно оценить их мастерство?\n"
        "Впрочем, говорят, каждый сам куёт свою удачу.",
        "one makes one's own luck требовало русской идиомы",
    ),
    (
        "patch_text01",
        "message/s050_176.mbe/000_Sheet1.csv",
        "s050_176_380",
    ): Rewrite(
        "Вот это была битва! Как и ожидалось\n"
        "от верного друга Меркуримона.",
        "fierce fight — ожесточённая битва, а не жестокий бой",
    ),
    (
        "patch_text01",
        "message/s070_056.mbe/000_Sheet1.csv",
        "s070_056_200",
    ): Rewrite(
        "Погоди... Мне так понравился тот мотоцикл из недавнего\n"
        "фильма! Он был просто супер!",
        "исправлены обращение и согласование местоимения с мотоциклом",
    ),
    (
        "patch_text01",
        "message/s070_167.mbe/000_Sheet1.csv",
        "s070_167_620",
    ): Rewrite(
        "Это ты называешь весельем...? Ну ты даёшь!",
        "you really are something else было переведено буквальной калькой",
    ),
    (
        "patch_text01",
        "message/s095_077.mbe/000_Sheet1.csv",
        "s095_077_150",
    ): Rewrite(
        "Именно. За них я беспокоюсь почти так же,\n"
        "как за руду хрондигизойта.",
        "исправлены канцеляризм благополучие и родительный падеж термина",
    ),
    (
        "patch_text01",
        "message/s095_077.mbe/000_Sheet1.csv",
        "s095_077_230",
    ): Rewrite(
        "Именно. Я продолжу ждать вестей от ЛоадерЛеомона.",
        "communication comes in переведено механически; имя было разорвано пробелом",
    ),
    (
        "patch_text01",
        "message/s095_077.mbe/000_Sheet1.csv",
        "s095_077_280",
    ): Rewrite(
        "Именно. Я продолжу ждать вестей от ЛоадерЛеомона.",
        "контекстный дубль той же механической реплики",
    ),
    (
        "patch_text01",
        "message/s100_088.mbe/000_Sheet1.csv",
        "s100_088_130",
    ): Rewrite(
        "Да, но они очень живучие, так что вряд ли\n"
        "с ними что-то случилось.",
        "resilient и come to harm были переведены канцелярскими кальками",
    ),
    (
        "patch_text01",
        "message/s100_088.mbe/000_Sheet1.csv",
        "s100_088_370",
    ): Rewrite(
        "Мои помощники сильны, не правда ли?\n"
        "Уверен, они вам помогут.",
        "исправлены разговорная калька pretty tough и скачок тебе при формальном обращении",
    ),
    (
        "patch_text01",
        "message/s100_178.mbe/000_Sheet1.csv",
        "s100_178_070",
    ): Rewrite(
        "Пожалуй. Всё это весьма хлопотно, не правда ли?",
        "убран двойной буквальный yes и восстановлена манера персонажа",
    ),
    (
        "patch_text01",
        "message/s110_091.mbe/000_Sheet1.csv",
        "s110_091_220",
    ): Rewrite(
        "Похоже, нас заметили... Я предпочёл бы\n"
        "не привлекать внимания!",
        "keep this quiet было переведено буквальным сохранить это в тайне",
    ),
    (
        "patch_text01",
        "message/s110_091.mbe/000_Sheet1.csv",
        "s110_091_240",
    ): Rewrite(
        "Ну и морока... В следующий раз сразу\n"
        "сделаем всё как следует!",
        "quite the chore и properly from the start были переведены механически",
    ),
    (
        "patch_text01",
        "message/s110_093.mbe/000_Sheet1.csv",
        "s110_093_270",
    ): Rewrite(
        "Какая громоздкая броня для такого коротышки.\n"
        "Терпеть не могу жалких самозванцев вроде тебя!",
        "rather big armor было переведено буквальным довольно большая",
    ),
    (
        "patch_text01",
        "message/s110_098.mbe/000_Sheet1.csv",
        "s110_098_430",
    ): Rewrite(
        "Похоже, мы произвели хорошее впечатление.",
        "довольно благоприятное впечатление — канцелярская калька",
    ),
    (
        "patch_text01",
        "message/s110_100.mbe/000_Sheet1.csv",
        "s110_100_750",
    ): Rewrite(
        "И я, и моя броня изрядно потрёпаны,\n"
        "но остренькое меня взбодрило!",
        "spicy kick ошибочно переведено как острый удар вкуса",
    ),
    (
        "patch_text01",
        "message/s110_101.mbe/000_Sheet1.csv",
        "s110_101_450",
    ): Rewrite(
        "Похоже, с цифровыми яйцами непросто работать.",
        "items to work with было переведено буквальным предметы для работы",
    ),
    (
        "patch_text01",
        "message/s110_101.mbe/000_Sheet1.csv",
        "s110_101_470",
    ): Rewrite(
        "Здесь и правда можно выплавлять хрондигизойтовый металл.\n"
        "Но есть ещё одна проблема.",
        "исправлена несогласованная конструкция металл хрондигизойт",
    ),
    (
        "patch_text01",
        "message/s110_102.mbe/000_Sheet1.csv",
        "s110_102_340",
    ): Rewrite(
        "Хм... Верно, это условие поставил соперник.\n"
        "Отказаться было бы невежливо...",
        "condition offered by opponent было переведено тяжёлой пассивной калькой",
    ),
    (
        "patch_text01",
        "message/s200_146.mbe/000_Sheet1.csv",
        "s200_146_160",
    ): Rewrite(
        "Вы знаете о фазово-электронных формах жизни больше нас,\n"
        "и это очень помогает.",
        "it's really helpful было переведено без естественной русской связки",
    ),
    (
        "patch_text01",
        "message/s200_148.mbe/000_Sheet1.csv",
        "s200_148_440",
    ): Rewrite(
        "Да. Я хочу, чтобы мы все были заодно.",
        "on the same team here было калькировано как здесь в одной команде",
    ),
    (
        "patch_text01",
        "message/s200_148.mbe/000_Sheet1.csv",
        "s200_148_450",
    ): Rewrite(
        "Да. Я хочу, чтобы мы все были заодно.",
        "контекстный дубль той же кальки для альтернативного говорящего",
    ),
    (
        "patch_text01",
        "message/s200_149.mbe/000_Sheet1.csv",
        "s200_149_180",
    ): Rewrite(
        "Не хотела этого говорить, но ты всё-таки выделяешься.\n"
        "По крайней мере, твой образ не назовёшь \"кибернетическим\".",
        "you don't look cyber было ошибочно превращено в существительное кибер",
    ),
    (
        "patch_text01",
        "message/s910_170.mbe/000_Sheet1.csv",
        "s910_170_030",
    ): Rewrite(
        "Норио говорит, что прибыл из прошлого.\n"
        "Если это правда, я ничем не могу ему помочь.",
        "can't really offer him any help было переведено громоздкой калькой",
    ),
    (
        "patch_text01",
        "message/s910_170.mbe/000_Sheet1.csv",
        "s910_170_1220",
    ): Rewrite(
        "Ну, для \"гендиректора\" костюм и правда дешёвенький,\n"
        "но я говорю о другом!",
        "эмфаза DOES была механически перенесена на ДЕЙСТВИТЕЛЬНО",
    ),
    (
        "patch_text01",
        "message/s910_170.mbe/000_Sheet1.csv",
        "s910_170_1510",
    ): Rewrite(
        "Я вернулся в своё время? Здесь мне и правда спокойнее.",
        "time period I came from и feel a sense of calm были калькированы",
    ),
    (
        "patch_text01",
        "message/s910_170.mbe/000_Sheet1.csv",
        "s910_170_1520",
    ): Rewrite(
        "Неужели в будущем я стану таким неудачником?\n"
        "Моя судьба уже решена? Нет...",
        "убрана механическая связка неужели действительно буду",
    ),
    (
        "patch_text01",
        "message/s910_170.mbe/000_Sheet1.csv",
        "s910_170_1720",
    ): Rewrite(
        "Думаю, юный Норио испугался за своё будущее\n"
        "и наконец взялся за ум.",
        "got serious в контексте означает взялся за ум, а не стал серьёзным",
    ),
    (
        "patch_text01",
        "message/s910_170.mbe/000_Sheet1.csv",
        "s910_170_330",
    ): Rewrite(
        "Если подумать, здесь мне и правда спокойнее.",
        "двойная калька now that I think и sense of calm сокращена",
    ),
    (
        "patch_text01",
        "message/s910_171.mbe/000_Sheet1.csv",
        "s910_171_1470",
    ): Rewrite(
        "Да, наверное. В те годы я был довольно высокомерен.",
        "убран повтор полагаю в соседних частях одной реплики",
    ),
    (
        "patch_text01",
        "message/s910_171.mbe/000_Sheet1.csv",
        "s910_171_570",
    ): Rewrite(
        "Кстати... Недавно я видела женщину\n"
        "в лабораторном халате.",
        "now that I think about it и a bit ago были переведены буквально",
    ),
    (
        "patch_text01",
        "message/t01.mbe/000_Sheet1.csv",
        "f_t0103_0100_0050",
    ): Rewrite(
        "А город всё-таки интересный.\n"
        "Каждый день встречаешь столько разных людей.",
        "fascinating town и humans to see были переданы механически",
    ),
    (
        "patch_text01",
        "message/d04.mbe/000_Sheet1.csv",
        "f_d0404_9040_0030",
    ): Rewrite(
        "Хмпф! Не хочешь узреть мою мощь?! Ясно.\n"
        "Ты, должно быть, просто боишься!",
        "лишнее начальное многоточие после завершённого вопроса ломало пунктуацию",
    ),
}


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


def load_review() -> dict[tuple[str, str, str], dict[str, str]]:
    with REVIEW_CSV.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))

    confirmed: dict[tuple[str, str, str], dict[str, str]] = {}
    for row in rows:
        key = (row["package"], row["file"], row["row_id"])
        if key in confirmed:
            raise RuntimeError(f"Duplicate review key: {key}")
        confirmed[key] = row

    if set(confirmed) != set(REWRITES):
        missing = sorted(set(REWRITES) - set(confirmed))
        extra = sorted(set(confirmed) - set(REWRITES))
        raise RuntimeError(f"Review/allow-list mismatch; missing={missing}, extra={extra}")

    for key, rewrite in REWRITES.items():
        row = confirmed[key]
        if row["replacement"] != rewrite.replacement:
            raise RuntimeError(f"Replacement drift in review CSV: {key}")
        if row["reason"] != rewrite.reason:
            raise RuntimeError(f"Reason drift in review CSV: {key}")
    return confirmed


def main() -> None:
    review = load_review()
    grouped: dict[tuple[str, str], dict[str, tuple[str, str]]] = defaultdict(dict)
    for (package, relative_path, row_id), row in review.items():
        grouped[(package, relative_path)][row_id] = (
            row["current_ru"],
            row["replacement"],
        )

    # Full preflight: no file is written until every target and expected value
    # has been checked across the complete allow-list.
    loaded: dict[tuple[str, str], tuple[Path, list[list[str]]]] = {}
    changed = current = 0
    for (package, relative_path), wanted in grouped.items():
        path = CSV_ROOT / package / relative_path
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.reader(handle))
        loaded[(package, relative_path)] = (path, rows)

        seen: dict[str, int] = defaultdict(int)
        for row in rows[1:]:
            if row and row[0] in wanted:
                seen[row[0]] += 1
                if len(row) <= 2:
                    raise RuntimeError(f"Missing text column: {path}:{row[0]}")
                expected, replacement = wanted[row[0]]
                if row[2] == expected:
                    changed += 1
                elif row[2] == replacement:
                    current += 1
                else:
                    raise RuntimeError(
                        f"Stale target {path}:{row[0]}: {row[2]!r}; "
                        f"expected {expected!r} or {replacement!r}"
                    )
        bad_counts = {row_id: count for row_id, count in seen.items() if count != 1}
        missing = set(wanted) - set(seen)
        if bad_counts or missing:
            raise RuntimeError(
                f"Target cardinality failure in {path}: "
                f"missing={sorted(missing)}, counts={bad_counts}"
            )

    # Mutate the preflighted in-memory tables, then serialize only dirty files.
    dirty: set[tuple[str, str]] = set()
    for key, (path, rows) in loaded.items():
        wanted = grouped[key]
        for row in rows[1:]:
            if not row or row[0] not in wanted:
                continue
            expected, replacement = wanted[row[0]]
            if row[2] == expected:
                row[2] = replacement
                dirty.add(key)
    for key in sorted(dirty):
        path, rows = loaded[key]
        write_rows(path, rows)

    print(f"Targets: {len(REWRITES)}")
    print(f"Changed: {changed}")
    print(f"Already current: {current}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Apply the source-checked translation cleanup pass performed before v0.1.40."""

from __future__ import annotations

import csv
import re
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CSV_ROOT = ROOT / "csv"
ORIGINAL_ROOT = ROOT / "verify" / "game_build_23514637" / "text_original"
DATASET = ROOT / "exports" / "dynamic_gender_confirmed_variants_v066.csv"


U: dict[tuple[str, str, str], str] = {
    # Broken runtime tags and remaining high-priority audit hits.
    ("addcont_01_text01", "message/d110.mbe/000_Sheet1.csv", "d110_080_030"): "{player}!",
    ("addcont_02_text01", "message/d210.mbe/000_Sheet1.csv", "d210_040_060"): "{player}?!\nН-не может быть...!",
    ("patch_text01", "message/m050.mbe/000_Sheet1.csv", "m050_010_140"): "...Наконец-то связь восстановлена!\nПривет, агент {player}!",
    ("patch_text01", "message/m440.mbe/000_Sheet1.csv", "m440_070_060"): "Верно... Вмешательство извне разрешено...\nлишь один раз...",
    ("patch_text01", "message/s090_072.mbe/000_Sheet1.csv", "s090_072_640"): "Следующий заблудившийся дигимон — у экрана «АльтаВижн»\nв Синдзюку. С ним кто-то говорит... Нет, заигрывает...?!",
    ("patch_text01", "text/quest_step.mbe/000_Sheet1.csv", "72050"): "Поищите потерянного дигимона у экрана «АльтаВижн».",

    # Keep the canonical item spelling consistent in dialogue and Digitter.
    ("patch_text01", "message/d02.mbe/000_Sheet1.csv", "f_d0215_0070_0050"): "Сегодня мы с Лунамон ели ДигиМясо. Было очень вкусно!",
    ("patch_text01", "text/digitter_message.mbe/000_Sheet1.csv", "hazama_99_030_1"): "Третий день с момента моего прибытия. Один дигимон поделился со мной\nчем-то под названием «ДигиМясо».",
    ("patch_text01", "text/digitter_message.mbe/000_Sheet1.csv", "hazama_99_040_1"): "Четвёртый день с момента моего прибытия. Ботамон изменился после того,\nкак я покормил его ДигиМясом.",

    # Compact Digitter log lines for the fixed two-line panel and preserve
    # Minervamon's deliberate mispronunciation of "government" ("gubmint").
    ("patch_text01", "text/digitter_message.mbe/000_Sheet1.csv", "main_060_090_040"): "Все эти враждебные дигимоны находятся в подземелье\nСиндзюку уже восемь лет.",
    ("patch_text01", "text/digitter_message.mbe/000_Sheet1.csv", "main_060_090_050"): "Вероятно, эти дигимоны связаны и с Адом Синдзюку.\nСообщай о любых находках, агент {player}.",
    ("patch_text01", "text/digitter_message.mbe/000_Sheet1.csv", "main_060_090_060"): "Что до «ОккультТокио ТВ»... За восемь лет число\nего подписчиков выросло до двух миллионов.",
    ("patch_text01", "text/digitter_message.mbe/000_Sheet1.csv", "main_060_090_070"): "Похоже, канал начал расти около восьми лет назад.\nВозможно, толчком стали нынешние съёмки.",
    ("patch_text01", "text/digitter_message.mbe/000_Sheet1.csv", "recovery_start"): "Режим регенерации активирован. ОЗ и ОС дигимонов\nполностью восстановятся через {n0} сек...",
    ("patch_text01", "text/digitter_message.mbe/000_Sheet1.csv", "recovery_end"): "Режим регенерации завершён. ОЗ и ОС дигимонов\nполностью восстановлены.",
    ("patch_text01", "message/m030.mbe/000_Sheet1.csv", "m030_010_090"): "Какое-то «здание павительства»... взорвалось?\nТы вообще о чём?",

    # DLC story blocks with broken grammar or lost meaning.
    ("addcont_01_text01", "message/d120.mbe/000_Sheet1.csv", "d120_070_060"): "«Ничего особенного... Я лишь хочу и дальше заботиться\nо жене и дочери».",
    ("addcont_01_text01", "message/d120.mbe/000_Sheet1.csv", "d120_080_030"): "Верно. И многие дигимоны прекрасно ладят с людьми.",
    ("addcont_01_text01", "message/d120.mbe/000_Sheet1.csv", "d120_090_010"): "«Вы уверены? Стоит ли делиться такой конфиденциальной\nинформацией с посторонним?»",
    ("addcont_01_text01", "message/d120.mbe/000_Sheet1.csv", "d120_090_040"): "«Реабилитация идёт хорошо, верно?\nВы уже двигаетесь куда бодрее...»",
    ("addcont_01_text01", "message/d120.mbe/000_Sheet1.csv", "d120_090_050"): "«Восемь лет назад я решил защищать то, что мне дорого».",
    ("addcont_01_text01", "message/d120.mbe/000_Sheet1.csv", "d120_090_060"): "«Ты поймёшь, когда однажды у тебя появится собственная семья».",
    ("addcont_01_text01", "message/d120.mbe/000_Sheet1.csv", "d120_100_150"): "Вообще-то они даже страшнее того дигимона,\nкоторого ты так ненавидишь.",
    ("addcont_01_text01", "message/d130.mbe/000_Sheet1.csv", "d130_060_050"): "«Если я не вернусь живым, расскажи им всё как было».",
    ("addcont_02_text01", "message/d210.mbe/000_Sheet1.csv", "d210_040_170"): "Что скажешь, если мы все объединимся\nи вместе одолеем Параллельмона?",
    ("addcont_02_text01", "message/d210.mbe/000_Sheet1.csv", "d210_040_270"): "Ну ты и кадр! Чувствую, просмотры взлетят до небес!",
    ("addcont_02_text01", "message/d220.mbe/000_Sheet1.csv", "d220_060_110"): "Хотя тебе наверняка крепко досталось —\nстолько моих ударов выдержать.",
    ("addcont_02_text01", "message/d220.mbe/000_Sheet1.csv", "d220_090_070"): "Давайте вместе одолеем Параллельмона.\nКак насчёт небольшой «коллаборации»?",
    ("addcont_02_text01", "message/d220.mbe/000_Sheet1.csv", "d220_090_120"): "Но после нашего боя вам наверняка крепко досталось...",
    ("addcont_02_text01", "message/d220.mbe/000_Sheet1.csv", "d220_100_050"): "Поэтому на обложке презентации я поместил персонажа,\nочень похожего на тебя, {player}.",
    ("addcont_02_text01", "message/d220.mbe/000_Sheet1.csv", "d220_110_120"): "Моя-то куртка настоящая, а значит, твоя — жалкая подделка.",
    ("addcont_03_text01", "message/d310.mbe/000_Sheet1.csv", "d310_020_030"): "Э-это не к добру...!",
    ("addcont_03_text01", "message/d310.mbe/000_Sheet1.csv", "d310_060_170"): "Понятно. Выходит, разногласия вокруг X-программы —\nи практические, и идеологические — раскололи вас.",
    ("addcont_03_text01", "message/d310.mbe/000_Sheet1.csv", "d310_060_210"): "Нет...? С тех пор столько всего произошло, будто это было\nв другой жизни. Впрочем, дело в другом...",
    ("addcont_03_text01", "message/d310.mbe/000_Sheet1.csv", "d310_080_020"): "Я считаю, что из-за стремительного роста популяции дигимонов\nресурсный кризис со временем охватит все миры.",
    ("addcont_03_text01", "message/d310.mbe/000_Sheet1.csv", "d310_080_040"): "Какое тревожное заявление.",
    ("addcont_03_text01", "message/d310.mbe/000_Sheet1.csv", "d310_100_150"): "Если сперва внимательно оценить обстановку, удастся свести потери\nк минимуму. Нужно всё обдумать, прежде чем действовать—",
    ("addcont_03_text01", "message/d320.mbe/000_Sheet1.csv", "d320_030_050"): "Оно внедряется в дигимона, а затем полностью\nстирает его из реальности.",
    ("addcont_03_text01", "message/d320.mbe/000_Sheet1.csv", "d320_040_140"): "Слабые обречены погибнуть... Но если таков божественный закон,\nпо которому нам суждено жить, я хотя бы избавлю их от страданий.",
    ("addcont_03_text01", "message/d320.mbe/000_Sheet1.csv", "d320_070_060"): "«Помнишь, что ты сказал мне, когда я только поступил\nв общественную безопасность?»",
    ("addcont_03_text01", "message/d320.mbe/000_Sheet1.csv", "d320_070_070"): "«Я поступил на службу, потому что хотел творить добро».",
    ("addcont_03_text01", "message/d320.mbe/000_Sheet1.csv", "d320_070_080"): "«Но, оказавшись внутри организации, я начал сомневаться,\nчто же на самом деле правильно».",
    ("addcont_03_text01", "message/d320.mbe/000_Sheet1.csv", "d320_070_090"): "«Я уже не был уверен, что именно человечество\nмы должны защищать...»",
    ("addcont_03_text01", "message/d320.mbe/000_Sheet1.csv", "d320_070_100"): "«Я растерялся, терзался сомнениями и не видел выхода.\nНо ты заметил это и решил меня поддержать».",
    ("addcont_03_text01", "message/d320.mbe/000_Sheet1.csv", "d320_070_120"): "«Нет никого надёжнее тех, кто задаётся вопросом, что правильно.\nИ нет ничего страшнее слепой уверенности в собственной правоте».",
    ("addcont_03_text01", "message/d320.mbe/000_Sheet1.csv", "d320_070_130"): "«Есть вещи важнее, чем превращать праведность в оружие...\nНапример, всегда сомневаться в собственной правоте».",
    ("addcont_03_text01", "message/d320.mbe/000_Sheet1.csv", "d320_070_140"): "«И способность подвергать подобные вещи сомнению —\nтоже своего рода талант».",
    ("addcont_03_text01", "message/d320.mbe/000_Sheet1.csv", "d320_070_160"): "Есть вещи важнее, чем превращать праведность в оружие... Хм...",
    ("addcont_03_text01", "message/d330.mbe/000_Sheet1.csv", "d330_020_050"): "«Не хочу этого признавать, но...\nСиммонс — настоящий профессионал».",

    # Clear idiom and sentence-structure failures in the main story.
    ("patch_text01", "message/arena01.mbe/000_Sheet1.csv", "arena01_m310_020_020"): "Или победа в прошлом бою была случайностью?! Второй матч\nновичков! Ещё одна победа — и станет ясно, чего они стоят!",
    ("patch_text01", "message/battle.mbe/000_Sheet1.csv", "1040020001"): "У тебя наверняка уже не осталось сил сражаться, да?\nНу же, просто выслушай нас!",
    ("patch_text01", "message/battle.mbe/000_Sheet1.csv", "1200020055"): "Этому аду не будет конца, пока\n«один из нас не перестанет существовать»!",
    ("patch_text01", "message/d02.mbe/000_Sheet1.csv", "f_d0201_0040_0010"): "Что ж! Незнакомое лицо. Похоже, вы здесь недавно?",
    ("patch_text01", "message/d02.mbe/000_Sheet1.csv", "f_d0201_0690_0030"): "Да ладно, много не прошу! У такой важной шишки наверняка\nчто-нибудь да найдётся. Верно?!",
    ("patch_text01", "message/d02.mbe/000_Sheet1.csv", "f_d0201_0760_0030"): "В прошлом бою мы и правда продвинулись вперёд, но надеюсь,\nдальше обойдёмся без отговорок.",
    ("patch_text01", "message/d02.mbe/000_Sheet1.csv", "f_d0201_830_0020"): "Ты даже пробился вверх по турнирной лестнице — значит, ты не\nпромах! Мне тоже пора поднажать!",
    ("patch_text01", "message/d02.mbe/000_Sheet1.csv", "f_d0201_840_0010"): "Приветствую, Великий Хранитель. Ты великолепно справился.",
    ("patch_text01", "message/d02.mbe/000_Sheet1.csv", "f_d0201_840_0020"): "Это было давно, но я помню: вы решили проблемы с Центральной\nбашней и задержкой Локомона.",
    ("patch_text01", "message/d02.mbe/000_Sheet1.csv", "f_d0202_0320_0020"): "Ты совсем в этом не разбираешься. Потому и проигрываешь.",
    ("patch_text01", "message/d02.mbe/000_Sheet1.csv", "f_d0202_0350_0050"): "Ну всё! Будете повторять правильный ответ,\nпока все не усвоите!",
    ("patch_text01", "message/d02.mbe/000_Sheet1.csv", "f_d0202_0450_0020"): "Вот так я и пробился на самую вершину, став дигимоном\nмега-уровня. Понятно?",
    ("patch_text01", "message/d02.mbe/000_Sheet1.csv", "f_d0202_0480_0030"): "Но оказалось, что среди Титанов тоже есть неплохие ребята.",
    ("patch_text01", "message/d02.mbe/000_Sheet1.csv", "f_d0202_0650_0010"): "Героические подвиги? Да я всё это время в страхе убегал...\nХотя так складно врать — тоже своего рода подвиг...",
    ("patch_text01", "message/d02.mbe/000_Sheet1.csv", "f_d0202_9010_0040"): "Я... проиграл. У тебя отлично получается.",
    ("patch_text01", "message/d02.mbe/000_Sheet1.csv", "f_d0204_0240_0030"): "Ты... выглядишь довольно аппетитно... *бормочет себе под нос*",
    ("patch_text01", "message/d02.mbe/000_Sheet1.csv", "f_d0204_0480_0020"): "Я вам правда благодарен. Не думал, что ещё увижу это место...",
    ("patch_text01", "message/d02.mbe/000_Sheet1.csv", "f_d0213_0030_0040"): "Я давно не дрался, поэтому теперь и сам оказался\nсреди пациентов. Хахаха...",
    ("patch_text01", "message/d03.mbe/000_Sheet1.csv", "f_d0302_0020_0010"): "Разрази меня гром! Ещё Титаны?! А, нет... Прости за грубость.\nВ последнее время их развелось слишком много.",
    ("patch_text01", "message/d03.mbe/000_Sheet1.csv", "f_d0302_0030_0020"): "Заткнись! Ты всегда был мягкотелым, как гуппи! Вот они и думают,\nчто могут безнаказанно нападать на нас изо дня в день.",
    ("patch_text01", "message/d03.mbe/000_Sheet1.csv", "f_d0304_0030_0050"): "Но Титаны почему-то ведут себя странно. Они совсем\nраспоясались, так что я лучше пойду с вами.",
    ("patch_text01", "message/d03.mbe/000_Sheet1.csv", "f_d0305_9000_0050"): "Я выиграл! Карты у меня что надо!",
    ("patch_text01", "message/d04.mbe/000_Sheet1.csv", "f_d0404_0080_0020"): "Вот именно! Это выглядело очень опасно! Интересно, что это было...",
    ("patch_text01", "message/d04.mbe/000_Sheet1.csv", "f_d0404_0450_0010"): "Ты... раньше был Аквиламоном? Ну и изменился же ты!",
    ("patch_text01", "message/d04.mbe/000_Sheet1.csv", "f_d0404_0460_0010"): "Я давно в этом деле и хорошо разбираюсь в товаре.",
    ("patch_text01", "message/d04.mbe/000_Sheet1.csv", "f_d0404_9010_0040"): "У тебя отлично получается. Мне бы поучиться твоим приёмам.",
    ("patch_text01", "message/d05.mbe/000_Sheet1.csv", "f_d0502_0270_0010"): "ИНФОРМАЦИЯ ПОЛУЧЕНА. РАЗРУШЕНИЯ,\nПО-ВИДИМОМУ, БЫЛИ МАСШТАБНЫМИ.",
    ("patch_text01", "message/d05.mbe/000_Sheet1.csv", "f_d0506_0070_0010"): "Я всё слышу об этом «Каллисмоне». Говорят, он грозный боец.",
    ("patch_text01", "message/d05.mbe/000_Sheet1.csv", "f_d0506_0120_0030"): "Ого! Вот теперь всё по-настоящему серьёзно, да?!",
    ("patch_text01", "message/d05.mbe/000_Sheet1.csv", "f_d0506_0200_0070"): "Отличная работа! Вот это была жаркая битва!",
    ("patch_text01", "message/d05.mbe/000_Sheet1.csv", "f_d0513_0050_0030"): "Вот в чём дело. Новички приходят сюда, мечтая стать такими,\nкак мы. А сражаться с ними, оказывается, весьма занятно.",
    ("patch_text01", "message/d05.mbe/000_Sheet1.csv", "f_d0513_0080_0020"): "Ого... Ты и правда особенный! Я выложился по полной, без шуток.",
    ("patch_text01", "message/d06.mbe/000_Sheet1.csv", "f_d0604_0130_0030"): "Думаю, нам стоит действовать сообща, малыш.\nКажется, я знаю, как открыть камеры.",
    ("patch_text01", "message/d06.mbe/000_Sheet1.csv", "f_d0604_0230_0050"): "Понятно... Это подделка. Ловко они тут всё устроили.",
    ("patch_text01", "message/d06.mbe/000_Sheet1.csv", "f_d0604_0400_0010"): "Понятно... Значит, открыть эту камеру довольно сложно?..",
    ("patch_text01", "message/d06.mbe/000_Sheet1.csv", "f_d0606_0010_0060"): "Реликвия Илиады считается великим сокровищем.\nПоэтому её и защищает барьер.",
    ("patch_text01", "message/d07.mbe/000_Sheet1.csv", "f_d0701_0040_0010"): "Тц! Этот золотой дракон — серьёзный противник.",
    ("patch_text01", "message/d07.mbe/000_Sheet1.csv", "f_d0701_9000_0010"): "Бу! Хочешь сыграть в карты? Предупреждаю: играю я неплохо.",
    ("patch_text01", "message/d09.mbe/000_Sheet1.csv", "f_d0902_0030_0020"): "Брат... Это правда ты?..",
    ("patch_text01", "message/d09.mbe/000_Sheet1.csv", "f_d0902_0040_0010"): "Эх, как же тяжело, бульк... У меня тоже голова болит, бульк.",
    ("patch_text01", "message/d09.mbe/000_Sheet1.csv", "f_d0902_0080_0010"): "Если ты настаиваешь, младший брат...\nтогда будем сражаться плечом к плечу!",
    ("patch_text01", "message/d09.mbe/000_Sheet1.csv", "f_d0904_0430_0010"): "Помочь пострадавшим — самое малое, что я могу сделать для своих\nпоклонников. Оставьте всё мне. Я прекрасно справлюсь!",
    ("patch_text01", "message/d09.mbe/000_Sheet1.csv", "f_d0905_0040_0020"): "Ну как тебе мой голос? Похоже получилось? Хахаха!",
    ("patch_text01", "message/d09.mbe/000_Sheet1.csv", "f_d0906_0080_0020"): "Меня этим не запугать! До настоящего ему далеко!",
    ("patch_text01", "message/d09.mbe/000_Sheet1.csv", "f_d0903_0410_0010"): "А, наконец-то связь установлена! Теперь меня слышно? Это Симмонс.\nЯ связываюсь с тобой по Дигилайну.",
    ("patch_text01", "message/d12.mbe/000_Sheet1.csv", "f_d1204_9000_0050"): "На этот раз удача была на моей стороне, но ты тоже отлично\nиграешь. С тобой нельзя не считаться.",
    ("patch_text01", "message/d12.mbe/000_Sheet1.csv", "f_d1205_0300_0010"): "Зубчатый лес... Он ведь в стороне святилища?\nМеня тревожит, что там сейчас творится.",
    ("patch_text01", "message/d12.mbe/000_Sheet1.csv", "f_d1206_0040_0010"): "Так-так... Прошло восемь лет. Немалый срок.\nПодробности тебе рассказала Асуна?",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "moja_001_3_reaction_char_MOJYAMON"): "Логично. Ведь я встретил вас всех, и теперь мы друзья!",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "imp_001_3_reaction_char_IMPMON"): "Хе-хе! Значит, понимаешь, к чему я клоню?\nДумаю, мы отлично поладим.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "tsuchi_001_2_reaction_char_TUCHIDARUMON"): "Тогда почему бы им просто не потренироваться?",
    ("patch_text01", "message/m170.mbe/000_Sheet1.csv", "m170_065_370"): "Титаны напали! Немедленно уходите оттуда! Все до единого!",
    ("patch_text01", "message/m170.mbe/000_Sheet1.csv", "m170_100_070"): "Вот как? Но раковина-то у тебя...",
    ("patch_text01", "message/m230.mbe/000_Sheet1.csv", "m230_020_140"): "Из эпицентра взрыва хлынули дигимоны. Целые толпы!",
    ("patch_text01", "message/m260.mbe/000_Sheet1.csv", "m260_030_052"): "Выходит, наши друзья и между собой знакомы...",
    ("patch_text01", "message/m285.mbe/000_Sheet1.csv", "m285_070_140"): "Зубчатый лес... Он ведь в стороне святилища?\nТечение там сильно пронизывает почву.",
    ("patch_text01", "message/m330.mbe/000_Sheet1.csv", "m330_080_030"): "Они активируют какое-то огромное неизвестное оружие под городом.",
    ("patch_text01", "message/rumor_npc.mbe/000_Sheet1.csv", "r_d1204_0010_0150"): "Я тебя прикрою!",
    ("patch_text01", "message/rumor_npc.mbe/000_Sheet1.csv", "r_d0202_0030_0040"): "Эй! Держись, напарник!",
    ("patch_text01", "message/rumor_npc.mbe/000_Sheet1.csv", "r_d0501_0010_0070"): "Эй! Держись!",
    ("patch_text01", "message/rumor_npc.mbe/000_Sheet1.csv", "r_h0312_0010_0_2"): "Держись!",
    ("patch_text01", "message/rumor_npc.mbe/000_Sheet1.csv", "r_h0312_0010_2_6"): "Держись!",
    ("patch_text01", "message/s010_156.mbe/000_Sheet1.csv", "s010_156_240"): "Похоже. Во всяком случае, это какая-то механическая деталь,\nно я не знаю, к чему она подходит.",
    ("patch_text01", "message/s010_156.mbe/000_Sheet1.csv", "s010_156_950"): "Как ни крути, неудивительно, что отец Инори расследует\nкатастрофу. Ведь именно так погиб Юу.",
    ("patch_text01", "message/s050_039.mbe/000_Sheet1.csv", "s050_039_250"): "Выходит, я обязан тебе жизнью. Вот, возьми.\nЭто самое малое, что я могу сделать.",
    ("patch_text01", "message/s050_043.mbe/000_Sheet1.csv", "s050_043_400"): "Я не собираюсь сдаваться!\nПросто этот ПлатинаНумемон оказался пустышкой.",
    ("patch_text01", "message/s110_101.mbe/000_Sheet1.csv", "s110_101_530"): "Прошу вас отправиться туда вместе со мной.\nЧто скажете? Поможете?",
    ("patch_text01", "message/s910_169.mbe/000_Sheet1.csv", "s910_169_280"): "Похоже. Он принялся громко читать вслух.",
    ("patch_text01", "message/t04.mbe/000_Sheet1.csv", "f_t0403_0210_0010"): "Пора на сегодня заканчивать?",
    ("patch_text01", "message/d02.mbe/000_Sheet1.csv", "f_d0201_0720_0010"): "Эй, постой! Наконец-то цены снова упали —\nпора что-нибудь купить!",
    ("patch_text01", "message/d02.mbe/000_Sheet1.csv", "f_d0201_870_0020"): "Возьми себя в руки! Мы вернули город — разве этого мало?",
    ("patch_text01", "message/s010_002.mbe/000_Sheet1.csv", "s010_002_360"): "Тогда давайте мы всё осмотрим вместо вас.\nЭти кварталы выглядят не такими уж опасными.",
    ("patch_text01", "message/s200_149.mbe/000_Sheet1.csv", "s200_149_010"): "Фух, как же я рада тебя видеть! В общем, мне пришло странное —\nдаже жуткое — сообщение в Дигилайне.",
    ("patch_text01", "message/s200_149.mbe/000_Sheet1.csv", "s200_149_020"): "Даже меня оно напугало.\nВ одиночку мне с этим точно не справиться.",
    ("patch_text01", "message/s200_149.mbe/000_Sheet1.csv", "s200_149_040"): "В общем... меня просят кое-что сделать.\nПричём почти наверняка незаконное.",
    ("patch_text01", "message/s200_149.mbe/000_Sheet1.csv", "s200_149_050"): "По крайней мере, похоже на наводку. Именно благодаря таким\nподсказкам у меня уже два миллиона подписчиков...",
    ("patch_text01", "message/s200_149.mbe/000_Sheet1.csv", "s200_149_060"): "Ни за что! Вдруг я упущу сенсацию века!",
    ("patch_text01", "message/s200_149.mbe/000_Sheet1.csv", "s200_149_070"): "Не знаю, кто отправитель, но вот что там написано:",

    # Additional source-checked lines previously hidden among soft markers.
    ("patch_text01", "message/d09.mbe/000_Sheet1.csv", "f_d0901_0120_0010"): "До следующей остановки далеко, бульк.\nПуть будет нелёгким, бульк...",
    ("patch_text01", "message/d09.mbe/000_Sheet1.csv", "f_d0903_0045_0240"): "Благодаря тебе мы втроём немного развлеклись.\nДавненько мы так не отдыхали.",
    ("patch_text01", "message/d09.mbe/000_Sheet1.csv", "f_d0903_0300_0010"): "Унгх... Я с голоду помираю...\nХочу набить живот теми фруктами.",
    ("patch_text01", "message/d09.mbe/000_Sheet1.csv", "f_d0904_0310_0140"): "Да, именно эту картину мы оба мечтали увидеть...",
    ("patch_text01", "message/d09.mbe/000_Sheet1.csv", "f_d0905_0080_0150"): "Тогда сразимся! Похоже, он тоже рвётся в бой! Ха-ха!\nДля подделки он весьма агрессивен!",
    ("patch_text01", "message/d13.mbe/000_Sheet1.csv", "f_d1301_0210_0010"): "К сожалению, встреча с хирургами из Хигаси-Синдзюку\nзакончилась довольно неудачно.",
    ("patch_text01", "message/field_text.mbe/000_Sheet1.csv", "g_degi_h0513_0010"): "От тебя исходит невероятный боевой дух... Впечатляет.\nЯ всегда поддержу тебя в бою.",
    ("patch_text01", "message/m050.mbe/000_Sheet1.csv", "m050_030_150"): "Просто мне нужно больше узнать о существах,\nкоторых ты называешь дигимонами.",
    ("patch_text01", "message/m050.mbe/000_Sheet1.csv", "m050_030_290"): "...так получилась самодельная система определения координат.\nРаботает довольно точно.",
    ("patch_text01", "message/m070.mbe/000_Sheet1.csv", "m070_040_091"): "Вы не слишком торопите события? Мы ведь только познакомились.",
    ("patch_text01", "message/m210.mbe/000_Sheet1.csv", "m210_045_030"): "Очень хорошо... Хватит дешёвых трюков!\nТеперь посмотрим, чего ты стоишь!",
    ("patch_text01", "message/m230.mbe/000_Sheet1.csv", "m230_030_070"): "Спасибо, {player}. Из уст человека из будущего\nэто звучит особенно убедительно.",
    ("patch_text01", "message/m280.mbe/000_Sheet1.csv", "m280_040_150"): "Но я и правда принадлежу к умеренному крылу Титанов — и не лгала,\nкогда говорила, что ненавижу эти варварские драки!",
    ("patch_text01", "message/m280.mbe/000_Sheet1.csv", "m280_050_150"): "Если у тебя и правда есть знания о будущем,\nтем более нужно действовать—",
    ("patch_text01", "message/m280.mbe/000_Sheet1.csv", "m280_100_060"): "«Я... правда не хотела сражаться. У меня не было выбора...\nЭто был приказ».",
    ("patch_text01", "message/m310.mbe/000_Sheet1.csv", "m310_010_030"): "Было бы здорово. Если нам всё-таки удастся достичь мира...",
    ("patch_text01", "message/m420.mbe/000_Sheet1.csv", "m420_120_120"): "Получается, в каком-то смысле Хрономон\nжаждет собственного поражения.",
    ("patch_text01", "message/m430.mbe/000_Sheet1.csv", "m430_050_110"): "После этого я ещё долго чувствовала себя как во сне.",
    ("patch_text01", "message/rumor_npc.mbe/000_Sheet1.csv", "r_d0501_0020_0070"): "Они носятся как угорелые!",
    ("patch_text01", "message/s010_156.mbe/000_Sheet1.csv", "s010_156_470"): "Значит, отец Инори и правда расследовал тот инцидент.\nЯ так и думала. Ведь это случилось тогда...",
    ("patch_text01", "message/s020_173.mbe/000_Sheet1.csv", "s020_173_430"): "Если подумать, они тоже все в море.\nВозможно, море — моё истинное место!",
    ("patch_text01", "message/s050_043.mbe/000_Sheet1.csv", "s050_043_250"): "Ты и правда собираешься это сделать? У-удачи!",
    ("patch_text01", "message/s050_043.mbe/000_Sheet1.csv", "s050_043_260"): "Ого... Так тебе удалось победить ПлатинаНумемона! Вот это да!",
    ("patch_text01", "message/s050_152.mbe/000_Sheet1.csv", "s050_152_070"): "Мне трудно выражать свои мысли,\nпоэтому и подбадривать других нелегко.",
    ("patch_text01", "message/s070_056.mbe/000_Sheet1.csv", "s070_056_060"): "После всего, что я узнала, человеческая любовь\nкажется мне по сути ничтожной.",
    ("patch_text01", "message/s070_167.mbe/000_Sheet1.csv", "s070_167_100"): "ДА. Всё очень серьёзно. Поэтому я и позвала вас сюда.",
    ("patch_text01", "message/s100_088.mbe/000_Sheet1.csv", "s100_088_200"): "{next}В Райском колизее довольно весело.",
    ("patch_text01", "message/s110_090.mbe/000_Sheet1.csv", "s110_090_230"): "Я пришёл проверить странные слухи...\nНо ЭТО нельзя оставить без внимания.",
    ("patch_text01", "message/s110_090.mbe/000_Sheet1.csv", "s110_090_400"): "Хотя эти двое были спокойны.\nОни показались мне дружелюбными и приветливыми.",
    ("patch_text01", "message/s110_113.mbe/000_Sheet1.csv", "s110_113_530"): "Предаваться удовольствиям, когда дома тебя ждёт семья...\nЭто серьёзно...",
    ("patch_text01", "message/s200_147.mbe/000_Sheet1.csv", "s200_147_610"): "Ну и аппетиты у тебя!\nНо на этот раз нам и правда пришлось нелегко.",
    ("patch_text01", "message/s200_148.mbe/000_Sheet1.csv", "s200_148_400"): "Я сильно ошибалась насчёт людей...",
    ("patch_text01", "message/s200_148.mbe/000_Sheet1.csv", "s200_148_500"): "Ты всем нравишься. Именно ты, а не только твои наряды.",
    ("patch_text01", "message/s200_148.mbe/000_Sheet1.csv", "s200_148_510"): "Ты всем нравишься. Именно ты, а не только твои наряды.",
    ("patch_text01", "message/s200_149.mbe/000_Sheet1.csv", "s200_149_300"): "О, сообщение! «Я слежу за вами».\nНу вот, это уже и правда жутко!",
    ("patch_text01", "message/s200_149.mbe/000_Sheet1.csv", "s200_149_370"): "Эта штука может оказаться очень ценной!\nИли ты, случаем, рассчитываешь перекусить?",
    ("patch_text01", "message/s200_149.mbe/000_Sheet1.csv", "s200_149_480"): "Ну ты даёшь! Мне бы у тебя поучиться стримингу...\nХотя нет, забудь.",
    ("patch_text01", "message/s910_170.mbe/000_Sheet1.csv", "s910_170_900"): "Привет, моя будущая версия! Вот это да,\nя и правда разговариваю сам с собой!",
    ("patch_text01", "message/t04.mbe/000_Sheet1.csv", "f_t0403_0180_0030"): "Кстати, этот напиток... Как он называется? Чай? Неплохой.",
    ("patch_text01", "message/s010_002.mbe/000_Sheet1.csv", "s010_002_010"): "Хи-хи... Мой канал набирает обороты.\nЭту наводку мне прислали через соцсети!",
    ("patch_text01", "message/s010_002.mbe/000_Sheet1.csv", "s010_002_390"): "Хм... На стрим тут материала не хватит,\nно куб хотя бы можно отнести тому офицеру.",
    ("patch_text01", "message/s020_013.mbe/000_Sheet1.csv", "s020_013_520"): "Я сохраню лекарство как знак её признательности.\nМне важен сам этот жест.",
    ("patch_text01", "message/s050_042.mbe/000_Sheet1.csv", "s050_042_0300"): "Мы добыли перо Парротмона,\nда ещё и обрели бесстрашного последователя.",
    ("patch_text01", "message/d02.mbe/000_Sheet1.csv", "f_d0201_0480_0030"): "Но там легко оступиться: кругом одни стальные балки.\nДобраться до смотровой площадки будет непросто! Хахаха!",
    ("addcont_02_text01", "message/d220.mbe/000_Sheet1.csv", "d220_030_090"): "Полагаю, эта женщина прибыла из будущего, где уже начался\nглобальный коллапс, — из мира после Ада Синдзюку.",
    ("addcont_03_text01", "message/d310.mbe/000_Sheet1.csv", "d310_080_050"): "Они считают Программу X благом и полагают, что её следует\nпринять как часть естественного отбора.",
    ("addcont_02_text01", "message/d210.mbe/000_Sheet1.csv", "d210_040_310"): "Отлично, удар кулаком принят. Давайте устроим «коллаборацию».\nТолько убедись, что камера снимет мою куртку на ветру.",
    ("patch_text01", "message/m060.mbe/000_Sheet1.csv", "m060_050_010"): "Я чувствую... паранормальное зовёт нас!\nА я набью на этом просмотры!",
    ("patch_text01", "message/s200_147.mbe/000_Sheet1.csv", "s200_147_050"): "Этот парк известен, так что осторожным такой шаг не назовёшь...\nЗато ролик об этой истории может разлететься по сети.",
    ("addcont_01_text01", "message/d120.mbe/000_Sheet1.csv", "d120_100_040"): "«Некоторые пострадали от взрыва над зданием правительства.\nОстальные погибли из-за аномальных явлений...»",
    ("addcont_01_text01", "message/d120.mbe/000_Sheet1.csv", "d120_100_080"): "«Отдел общественной безопасности уже практически не работает,\nно кто-то должен действовать...»",
    ("addcont_01_text01", "message/d130.mbe/000_Sheet1.csv", "d130_030_070"): "«Он выглядел как пистолет и принадлежал агенту\nиз какой-то неизвестной страны...»",
    ("addcont_02_text01", "message/d240.mbe/000_Sheet1.csv", "d240_041_090"): "«Юу и его мама так и не вернулись домой в тот день.\nИх поглотило аномальное явление...»",
    ("addcont_03_text01", "message/d320.mbe/000_Sheet1.csv", "d320_060_030"): "«Некоторые пострадали от взрыва над зданием правительства.\nОстальные погибли из-за аномальных явлений...»",
    ("addcont_03_text01", "message/d320.mbe/000_Sheet1.csv", "d320_060_070"): "«Отдел общественной безопасности уже практически не работает,\nно кто-то должен действовать...»",
    ("addcont_03_text01", "message/d320.mbe/000_Sheet1.csv", "d320_060_110"): "«Я буду сражаться. Я встречусь с врагами лицом к лицу,\nкаким бы страшным ни оказался вражеский дигимон!»",
    # Final source-checked tail from the pre-release machine-translation audit.
    ("addcont_02_text01", "message/d220.mbe/000_Sheet1.csv", "d220_060_040"): "Я тоже почувствовал благородство в твоих ударах. А теперь будем сражаться\nплечом к плечу— Нет, погоди...",
    ("patch_text01", "message/t02.mbe/000_Sheet1.csv", "f_t0203_0030_0010"): "Оружие, скорее всего, прямо сейчас везут к зданию правительства.",
    ("patch_text01", "message/s020_019.mbe/000_Sheet1.csv", "s020_019_530"): "Но ты наверняка устал. Прошу, пойдём со мной.\nЯ заглажу свою вину за все эти переживания—",
    ("patch_text01", "message/d09.mbe/000_Sheet1.csv", "f_d0901_0070_0040"): "Я пойду следом за тобой. Мы ещё встретимся у Хроник Акаши!",
    ("patch_text01", "message/s030_030.mbe/000_Sheet1.csv", "s030_030_130"): "Прошу! Отправляйтесь к назначенному месту дуэли и объясните,\nчто всё это лишь большое недоразумение!",
    ("patch_text01", "message/s050_038.mbe/000_Sheet1.csv", "s050_038_0140"): "Я отправлю список нужных материалов на твой Дигивайс. Посмотри позже.",
    ("patch_text01", "message/s110_101.mbe/000_Sheet1.csv", "s110_101_500"): "На шахте ЛоадерЛеомона, где вы уже были, всё ещё не добыли достаточно руды.",
    ("patch_text01", "message/s110_101.mbe/000_Sheet1.csv", "s110_101_580"): "Я осмотрю шахту и встречу вас там, когда будете готовы.",
    ("patch_text01", "message/battle.mbe/000_Sheet1.csv", "1120001017"): "...Ладно, нашепчи мне на ушко сладкие глупости — всю эту неловкую\nромантическую чушь, и валим отсюда, глурп!",
    ("patch_text01", "message/d07.mbe/000_Sheet1.csv", "f_d0703_0110_0010"): "Эй, знаешь что?! *икает* Говорят, трактирщик — тот ещё крепкий орешек!",
    ("patch_text01", "message/d07.mbe/000_Sheet1.csv", "f_d0703_0110_0030"): "Хотел бы я однажды увидеть трактирщика в деле! *икает*",
    ("addcont_01_text01", "message/d110.mbe/000_Sheet1.csv", "d110_050_180"): "Пространственно-временные искажения будут множиться,\nпока мир окончательно не утратит свою форму.",
    ("addcont_02_text01", "message/d210.mbe/000_Sheet1.csv", "d210_040_140"): "Пространственно-временные искажения будут множиться,\nпока мир окончательно не утратит свою форму.",
    ("patch_text01", "message/arena01.mbe/000_Sheet1.csv", "arena01_m320_040_030"): "Этот динамичный дуэт терпеть не может улун! Встречайте максимум милоты —\n«Близнецы-терьеры»!",
    ("patch_text01", "message/arena01.mbe/000_Sheet1.csv", "arena01_m320_030_030"): "Он пылает так яростно, что прошлое меркнет! Страж Райского колизея\nвыходит на арену в огненном обличье!",
    ("patch_text01", "message/s110_101.mbe/000_Sheet1.csv", "s110_101_790"): "Хорошо, тогда полагаюсь на вас! Я вернусь как можно скорее,\nа вы держитесь!",
    ("patch_text01", "message/d05.mbe/000_Sheet1.csv", "f_d0513_0080_0030"): "Любой другой наверняка прикончил бы меня.\nНо с тобой мне удалось какое-то время продержаться.",
    ("patch_text01", "message/d09.mbe/000_Sheet1.csv", "f_d0907_0070_0030"): "Но я давно поняла, что слишком мягкосердечна.\nПоэтому сама вызвалась отправиться в мир людей.",
    ("patch_text01", "message/t30.mbe/000_Sheet1.csv", "f_t3001_0130_0010"): "Хотите открыть {pf(PlayStation®Store/Microsoft Store/Nintendo eShop/the Online Store)}?\nЗдесь также можно проверить наборы предметов.",

    # item_name/item_ruby pairs whose English source and ID are identical.
    ("patch_text01", "text/item_ruby.mbe/000_Sheet1.csv", "1"): "Капсула ОЗ I",
    ("patch_text01", "text/item_ruby.mbe/000_Sheet1.csv", "2"): "Капсула ОЗ II",
    ("patch_text01", "text/item_ruby.mbe/000_Sheet1.csv", "3"): "Капсула ОЗ III",
    ("patch_text01", "text/item_ruby.mbe/000_Sheet1.csv", "8"): "Капсула ОС II",
    ("patch_text01", "text/item_ruby.mbe/000_Sheet1.csv", "9"): "Капсула ОС III",
    ("patch_text01", "text/item_ruby.mbe/000_Sheet1.csv", "19"): "Средство от пикселизации",

    # Quest clients whose English name exactly matches an authoritative
    # char_name entry; the old values were literal MT or stale transliterations.
    ("patch_text01", "text/quest_client.mbe/000_Sheet1.csv", "13"): "Нептунмон",
    ("patch_text01", "text/quest_client.mbe/000_Sheet1.csv", "19"): "ДжамбоГамемон",
    ("patch_text01", "text/quest_client.mbe/000_Sheet1.csv", "47"): "Танэмон",
    ("patch_text01", "text/quest_client.mbe/000_Sheet1.csv", "48"): "КатчМамаемон",
    ("patch_text01", "text/quest_client.mbe/000_Sheet1.csv", "49"): "ВерГарурумон",
    ("patch_text01", "text/quest_client.mbe/000_Sheet1.csv", "52"): "Скалл Сатамон",
    ("patch_text01", "text/quest_client.mbe/000_Sheet1.csv", "53"): "Скалл Сатамон",
    ("patch_text01", "text/quest_client.mbe/000_Sheet1.csv", "62"): "Дианамон",
    ("patch_text01", "text/quest_client.mbe/000_Sheet1.csv", "73"): "Древний Вайзмон",
    ("patch_text01", "text/quest_client.mbe/000_Sheet1.csv", "74"): "Хоукмон",
    ("patch_text01", "text/quest_client.mbe/000_Sheet1.csv", "77"): "Гардромон",
    ("patch_text01", "text/quest_client.mbe/000_Sheet1.csv", "94"): "Бакэмон",
    ("patch_text01", "text/quest_client.mbe/000_Sheet1.csv", "99"): "Дюкмон",
    ("patch_text01", "text/quest_client.mbe/000_Sheet1.csv", "100"): "Ви-мон",
    ("patch_text01", "text/quest_client.mbe/000_Sheet1.csv", "102"): "Алфорс Ви-драмон",
    ("patch_text01", "text/quest_client.mbe/000_Sheet1.csv", "105"): "Динасмон",
    ("patch_text01", "text/quest_client.mbe/000_Sheet1.csv", "106"): "Слейпмон",
    ("patch_text01", "text/quest_client.mbe/000_Sheet1.csv", "111"): "Гэнкумон",
    ("patch_text01", "text/quest_client.mbe/000_Sheet1.csv", "113"): "Гэнкумон",
    ("patch_text01", "text/quest_client.mbe/000_Sheet1.csv", "153"): "Бёрдрамон",
    ("patch_text01", "text/quest_client.mbe/000_Sheet1.csv", "159"): "Зубаигермон",
    ("patch_text01", "text/quest_client.mbe/000_Sheet1.csv", "172"): "Хангёмон",
    ("patch_text01", "text/quest_client.mbe/000_Sheet1.csv", "173"): "Маринангемон",
    ("patch_text01", "text/quest_client.mbe/000_Sheet1.csv", "300"): "Волкамон",

    # Standard controller terminology; the old strings translated hardware
    # controls as clothing buttons, gun triggers and mouse clicks.
    ("patch_text01", "text/steam_input.mbe/000_Sheet1.csv", "steam_input_explanation_001"): "Официальная раскладка геймпада",
    ("patch_text01", "text/steam_input.mbe/000_Sheet1.csv", "steam_input_name_001"): "Стик",
    ("patch_text01", "text/steam_input.mbe/000_Sheet1.csv", "steam_input_name_002"): "Кнопка A",
    ("patch_text01", "text/steam_input.mbe/000_Sheet1.csv", "steam_input_name_003"): "Кнопка B",
    ("patch_text01", "text/steam_input.mbe/000_Sheet1.csv", "steam_input_name_004"): "Кнопка X",
    ("patch_text01", "text/steam_input.mbe/000_Sheet1.csv", "steam_input_name_005"): "Кнопка Y",
    ("patch_text01", "text/steam_input.mbe/000_Sheet1.csv", "steam_input_name_006"): "Левый бампер (LB)",
    ("patch_text01", "text/steam_input.mbe/000_Sheet1.csv", "steam_input_name_007"): "Правый бампер (RB)",
    ("patch_text01", "text/steam_input.mbe/000_Sheet1.csv", "steam_input_name_008"): "Левый триггер (LT)",
    ("patch_text01", "text/steam_input.mbe/000_Sheet1.csv", "steam_input_name_009"): "Правый триггер (RT)",
    ("patch_text01", "text/steam_input.mbe/000_Sheet1.csv", "steam_input_name_010"): "Кнопка Start",
    ("patch_text01", "text/steam_input.mbe/000_Sheet1.csv", "steam_input_name_011"): "Кнопка Select",
    ("patch_text01", "text/steam_input.mbe/000_Sheet1.csv", "steam_input_name_012"): "Нажатие левого стика (L3)",
    ("patch_text01", "text/steam_input.mbe/000_Sheet1.csv", "steam_input_name_013"): "Нажатие правого стика (R3)",
    ("patch_text01", "text/steam_input.mbe/000_Sheet1.csv", "steam_input_name_014"): "Крестовина: вверх",
    ("patch_text01", "text/steam_input.mbe/000_Sheet1.csv", "steam_input_name_015"): "Крестовина: вниз",
    ("patch_text01", "text/steam_input.mbe/000_Sheet1.csv", "steam_input_name_016"): "Крестовина: влево",
    ("patch_text01", "text/steam_input.mbe/000_Sheet1.csv", "steam_input_name_017"): "Крестовина: вправо",

    # Source-checked Digimon Chat dialogue polish and fixed-speaker gender.
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "lena_001_3_reaction_char_RENAMON"): "Спасибо. Я одолел немало сильных дигимонов и скопировал их данные,\nтак что в своей силе не сомневаюсь.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "mine_001_0_char_MINERVAMON"): "А проводить время с человеком вовсе неплохо.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "mine_001_1_reaction_char_MINERVAMON"): "Вот как? Если хочешь показать мне себя с другой стороны, тогда не тяни!",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "mine_001_2_reaction_char_MINERVAMON"): "Вовсе нет! Мне нравится узнавать, как проходит твой день.\nХочу узнать о тебе ещё больше!",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "mine_001_3_reaction_char_MINERVAMON"): "Это ты держишься отстранённо и слишком церемонишься.\nДавай будем откровенны друг с другом.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "mine_001_4_reaction_char_MINERVAMON"): "Конечно. Теперь я уже не представляю себя вдали от тебя.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "meruv_001_2_reaction_char_MERVAMON"): "Не можешь? Я говорю не о теле, а о внутренней зрелости.\nВсё дело в настрое.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "piko_001_2_reaction_char_PICODEVIMON"): "Всё, что захочешь. Честно! А всякие подлые проделки — мой конёк!",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "coro_001_1_replay"): "А кроме смелости у тебя что-нибудь есть?",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "sylphy_001_2_reaction_char_SILPHYMON"): "Верно подмечено. В любой момент могу поделиться данными\nс радара и нашлемного дисплея.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "presi_001_1_reaction_char_PLESIOMON"): "Странствовать по огромному миру? Прекрасная цель —\nболее того, прекрасная мечта.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "exbui_001_3_reaction_char_XV-MON"): "Точно! Мне остаётся только тренироваться! Я хочу эволюционировать\nдальше, так что поддерживай меня!",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "gani_001_0_char_GANIMON"): "Эй, давай сыграем в человеческую игру «камень, ножницы, бумага»!\nРаз, два...",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "gani_001_1_replay"): "Без пощады... Камень!",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "gani_001_2_replay"): "А вот так?.. Непобедимый приём!",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "gani_001_2_reaction_char_GANIMON"): "Ух ты! Сразу камень, ножницы и бумага!\nМне ещё многому нужно научиться...",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "aigiog_001_0_char_AEGIOCHUSMON_GREEN"): "Недавно я увидел сад, полный роз. Красота была невероятная.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "vulca_001_0_char_VULCANUSMON"): "Гр-р-р! Я так занят, что рук на всё не хватает!",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "yuno_001_4_reaction_char_JUNOMON"): "Понятно... Постараюсь не слишком к тебе привязываться.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "belsta_001_4_reaction_char_BEELSTARMON"): "Хи-хи. Я так и знала, что ты это скажешь!",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "rigra_001_4_reaction_char_RIZEGREYMON"): "Значит, раньше я выглядел превосходно? Даже не знаю,\nрадоваться этому или огорчаться...",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "mame_001_3_reaction_char_MAMEMON"): "Ха. Наверное, будь я большим, это был бы уже не тот Мамемон,\nкоторого все знают и любят, да?",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "lili_001_2_reaction_char_LILLYMON"): "Хи-хи. Ты даже не представляешь, какой зрелой красавицей я стала.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "luna_001_1_reaction_char_LUNAMON"): "Я так и думала! Решила, что ты обращаешься к кому-то другому...\nСпасибо! Давай постараемся!",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "luna_001_2_reaction_char_LUNAMON"): "Правда? Тогда лучше поговори со мной.\nУверена, мне есть чему у тебя поучиться.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "luna_001_3_reaction_char_LUNAMON"): "Мне показалось, что я слышала твой голос. Ошиблась.\nИногда мой слух играет со мной злую шутку...",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "luna_001_4_reaction_char_LUNAMON"): "Я так и думала. Спасибо! Я была уверена, что узнаю твой голос.\nРада, что не ошиблась!",

    # Recruitment/field conversations with literal MT failures.
    ("patch_text01", "message/field_text.mbe/000_Sheet1.csv", "g_degi_h0210_0010"): "Я... хочу... выбраться отсюда... Можно мне... пойти с тобой?",
    ("patch_text01", "message/field_text.mbe/000_Sheet1.csv", "g_degi_h0212_0010"): "*принюхивается* Пахнет морским бризом! Инстинкты разбушевались!\nОтвезёшь меня к морю?",
    ("patch_text01", "message/field_text.mbe/000_Sheet1.csv", "g_degi_h0212_0020"): "Места не хватает? Прости, что я такой огромный...",
    ("patch_text01", "message/field_text.mbe/000_Sheet1.csv", "g_degi_h0415_0010"): "Я — серп и обожаю рубить! А я — милая и всеми любимая ласка!\nВместе мы — Реппамон!",
    ("patch_text01", "message/field_text.mbe/000_Sheet1.csv", "g_degi_h0417_0020"): "Эй, у тебя нет свободного места! Всегда нужно быть начеку —\nодна ошибка может стать роковой.",
    ("patch_text01", "message/field_text.mbe/000_Sheet1.csv", "g_degi_h0511_0020"): "А? Похоже, места не осталось. На твоём месте я бы с этим разобрался!",
    ("patch_text01", "message/field_text.mbe/000_Sheet1.csv", "g_degi_h0513_0020"): "Похоже, у тебя недостаточно свободного места...\nНеужели моё первое впечатление оказалось ошибочным?",
    ("patch_text01", "message/field_text.mbe/000_Sheet1.csv", "g_degi_h0810_0020"): "Нет места?! Га-га?! Будешь обижать малыша — получишь пузырей! Гу-гу!",
    ("patch_text01", "message/field_text.mbe/000_Sheet1.csv", "g_degi_h0811_0010"): "ПРИНЯТО. ПЕРЕЗАГРУЗКА СИСТЕМЫ. ЗАПРАШИВАЮ РАЗРЕШЕНИЕ\nСОПРОВОЖДАТЬ ВАС, ЧТОБЫ УСТАНОВИТЬ ПОСЛЕДНЕЕ ОБНОВЛЕНИЕ.",
    ("patch_text01", "message/field_text.mbe/000_Sheet1.csv", "g_degi_h0811_0020"): "ПРЕДУПРЕЖДЕНИЕ. НЕДОСТАТОЧНО СВОБОДНОГО МЕСТА ДЛЯ МОЕГО ПРИЁМА.\nРЕКОМЕНДУЮ ОСВОБОДИТЬ МЕСТО.",
    ("patch_text01", "message/field_text.mbe/000_Sheet1.csv", "g_degi_h0812_0010"): "Мне приснилось, будто я без конца таскаю вещи туда-сюда.\nНе хочу больше здесь оставаться. Поможешь?",

    # Fixed Digimon speaker gender in story and side conversations.
    ("addcont_01_text01", "message/d120.mbe/000_Sheet1.csv", "d120_050_020"): "«Лишь потому, что я родилась Титаном, меня вынудили участвовать\nв битве, в которой я не желаю сражаться».",
    ("patch_text01", "message/d06.mbe/000_Sheet1.csv", "f_d0604_0270_0060"): "Началась какая-то суматоха, и я решила воспользоваться случаем,\nчтобы сбежать.",
    ("patch_text01", "message/m160.mbe/000_Sheet1.csv", "m160_040_060"): "И ты сказал, что увидел яйцо, когда впервые открыл глаза...\nЯ ведь сама видела твою невероятную силу.",
    ("patch_text01", "message/s070_167.mbe/000_Sheet1.csv", "s070_167_210"): "Мне не с кем поговорить...",
    ("patch_text01", "message/s010_180.mbe/000_Sheet1.csv", "s010_180_140"): "Я тогда едва знала слова! Да и доверять дигимонам ты не спешила.",
    ("patch_text01", "message/d02.mbe/000_Sheet1.csv", "f_d0201_0550_0050"): "Вот только я ещё не решил, куда отправиться...\nХм, где было бы неплохо?",
    ("patch_text01", "message/d03.mbe/000_Sheet1.csv", "f_d0301_0140_0010"): "Эх, я бы тоже хотел плавать как рыба в воде...",
    ("patch_text01", "message/d09.mbe/000_Sheet1.csv", "f_d0903_0040_0040"): "О, это тоже было очень вкусно!\nНо я всё равно мог бы съесть ещё немного...",
    ("patch_text01", "message/s020_173.mbe/000_Sheet1.csv", "s020_173_480"): "О! Так это от тебя морская вода.\nБлагодаря тебе я решил вернуться домой.",
    ("patch_text01", "message/s110_211.mbe/000_Sheet1.csv", "s110_211_210"): "Я бы хотел сходить за сладостями и немного взбодриться.",
    ("patch_text01", "message/s200_148.mbe/000_Sheet1.csv", "s200_148_330"): "Ну, я никогда раньше не видел людей...\nНо теперь, когда привык к тебе, мне уже не страшно!",
    ("patch_text01", "message/rumor_npc.mbe/000_Sheet1.csv", "r_d0906_0020_0030"): "О, это ветер? Я его почти не почувствовала!",

    # Item categories, descriptions and bundle names.
    ("patch_text01", "text/item_auto_explanation.mbe/000_Sheet1.csv", "1"): "Расходные предметы",
    ("patch_text01", "text/item_auto_explanation.mbe/000_Sheet1.csv", "3"): "Предметы Дигифермы",
    ("patch_text01", "text/item_auto_explanation.mbe/000_Sheet1.csv", "7"): "/Предмет для обмена",
    ("patch_text01", "text/item_auto_explanation.mbe/000_Sheet1.csv", "8"): "/Предмет Дигифермы",
    ("patch_text01", "text/item_auto_explanation.mbe/000_Sheet1.csv", "9"): "/Для Дигифермы",
    ("patch_text01", "text/item_auto_explanation.mbe/000_Sheet1.csv", "10"): "Использование: в бою и на поле",
    ("patch_text01", "text/item_auto_explanation.mbe/000_Sheet1.csv", "11"): "Использование: в бою",
    ("patch_text01", "text/item_auto_explanation.mbe/000_Sheet1.csv", "12"): "Использование: на поле",
    ("patch_text01", "text/item_explanation.mbe/000_Sheet1.csv", "83"): "Драгоценный камень, добываемый из моллюсков. Не путать с чёрным\nжемчугом, который производит Сякомон. Можно продать по высокой цене.",
    ("patch_text01", "text/item_explanation.mbe/000_Sheet1.csv", "729"): "Большая раковина, полученная от Шеллмона.\nИспользуется для призыва Уэмона.",
    ("patch_text01", "text/item_explanation.mbe/000_Sheet1.csv", "731"): "Плод из Карпоса Хуле — леса, известного самыми сладкими\nфруктами в Цифровом мире.",
    ("patch_text01", "text/item_explanation.mbe/000_Sheet1.csv", "770"): "Редкое водное растение. Говорят, его находка приносит удачу\nв денежных делах.",
    ("patch_text01", "text/item_explanation.mbe/000_Sheet1.csv", "794"): "Пропуск в лабораторию, полученный от доктора Симмонс.",
    ("patch_text01", "text/item_explanation.mbe/000_Sheet1.csv", "1085"): "Усиление урона нейтральной стихии и снижение стоимости ОС её навыков\n/Снаряжение",
    ("patch_text01", "text/item_explanation.mbe/000_Sheet1.csv", "1114"): "Поглощает ОС противника при атаке\n/Снаряжение",
    ("patch_text01", "text/item_explanation.mbe/000_Sheet1.csv", "1120"): "Атаки наносят магический урон. *Несколько предметов, меняющих тип атаки, не суммируются*\n/Снаряжение",
    ("patch_text01", "text/item_explanation.mbe/000_Sheet1.csv", "1121"): "Атаки наносят урон, зависящий от СКР. *Несколько предметов, меняющих тип атаки, не суммируются*\n/Снаряжение",
    ("patch_text01", "text/item_explanation.mbe/000_Sheet1.csv", "1132"): "Повышает урон по целям в состоянии пробития\n/Снаряжение",
    ("patch_text01", "text/item_explanation.mbe/000_Sheet1.csv", "1134"): "Повышает урон кросс-артов (эффект суммируется по числу владельцев)\n/Снаряжение",
    ("patch_text01", "text/item_explanation.mbe/000_Sheet1.csv", "1135"): "Повышает урон рывка атаки (эффект суммируется по числу владельцев)\n/Снаряжение",
    ("patch_text01", "text/item_explanation.mbe/000_Sheet1.csv", "1136"): "Повышает начальное значение шкалы рывка (эффект суммируется по числу владельцев)\n/Снаряжение",
    ("patch_text01", "text/item_explanation.mbe/000_Sheet1.csv", "1137"): "Усиливает все эффекты во время пробития\n/Снаряжение",
    ("patch_text01", "text/item_explanation.mbe/000_Sheet1.csv", "1145"): "ИНТ +300. ДУХ +300.\nВосстанавливает ОС в размере 5% полученного физического урона.",
    ("patch_text01", "text/item_explanation.mbe/000_Sheet1.csv", "1154"): "Макс. ОЗ +1000.\nНейтрализует {is28}{image(ui_icon_btlStatus_002)} Смятение/\n{is28}{image(ui_icon_btlStatus_007)} Хаос.\nПовышает сопротивление {is28}{image(ui_icon_skill_000)} нейтральной стихии.",
    ("patch_text01", "text/item_explanation.mbe/000_Sheet1.csv", "29002"): "Тренировочный предмет Дигифермы. Повышает ОС.\nСмещает личность в сторону понимания.",
    ("patch_text01", "text/item_explanation.mbe/000_Sheet1.csv", "29019"): "Тренировочный предмет Дигифермы. Значительно повышает ИНТ.",
    ("patch_text01", "text/item_pack_name.mbe/000_Sheet1.csv", "5"): "Предмет для Дигифермы «Золотой моаи»",
    ("patch_text01", "text/item_pack_name.mbe/000_Sheet1.csv", "6"): "Агумон и Габумон с особыми ранними эволюциями",
    ("patch_text01", "text/item_pack_name.mbe/000_Sheet1.csv", "7"): "Специальный набор припасов",
    ("patch_text01", "text/item_pack_name.mbe/000_Sheet1.csv", "17"): "Агумон (чёрный), Габумон (чёрный) и набор предметов для приключений",
    ("patch_text01", "text/item_pack_name.mbe/000_Sheet1.csv", "19"): "Набор предметов для приключений",
    ("patch_text01", "text/item_pack_name.mbe/000_Sheet1.csv", "21"): "Набор предметов для тренировок",

    # Critical system/UI meanings and control labels.
    ("patch_text01", "text/yes_no_message.mbe/000_Sheet1.csv", "yesno_gameover_0040"): "Весь несохранённый прогресс будет потерян.\nВернуться на титульный экран?",
    ("patch_text01", "text/info_message.mbe/000_Sheet1.csv", "10007"): "Это сообщение заблокировано.\n{fc9Условие разблокировки: добраться до цели, не столкнувшись\nс врагами или препятствиями 3 раза или более.}",
    ("patch_text01", "text/info_message.mbe/000_Sheet1.csv", "info_message_kizunaskill_03"): "Ранг агента повышен до {fc9 {d0}}.\n\n{fc15Совет: проверьте меню эволюции — возможно, для ваших\nдигимонов открылись новые варианты эволюции.}",
    ("patch_text01", "text/common_message.mbe/000_Sheet1.csv", "ui_end_demo_0030"): "Данные сохранения из демоверсии можно перенести в полную\nверсию игры.\n\n— История об узах людей и дигимонов, охватывающая разные миры\nи преодолевающая границы времени и пространства. —\n\nУзнайте продолжение этой захватывающей истории в полной версии.",
    ("patch_text01", "text/common_message.mbe/000_Sheet1.csv", "19083"): "Этот режим отдаёт приоритет {fc9частоте кадров}.\nИгра работает с частотой {fc9до 60 кадров/с}.\nПримечание: режим можно изменить позже.",
    ("patch_text01", "text/info_message.mbe/000_Sheet1.csv", "10021"): "{fc9Пропуск Вейда} взорвался с громким хлопком.",
    ("patch_text01", "text/skill_name.mbe/000_Sheet1.csv", "10012"): "{d0}: {is28}{image(ui_icon_btlStatus_043)} защита повышена!",
    ("patch_text01", "text/skill_name.mbe/000_Sheet1.csv", "23701"): "Ледяной удар абсолютного нуля",
    ("patch_text01", "text/key_help_text.mbe/000_Sheet1.csv", "key_help_0067"): "Переместить в бокс",
    ("patch_text01", "text/key_help_text.mbe/000_Sheet1.csv", "key_help_0122"): "Открыть магазин",
    ("patch_text01", "text/key_help_text.mbe/000_Sheet1.csv", "key_help_0123"): "На титульный экран",
    ("patch_text01", "text/key_help_text.mbe/000_Sheet1.csv", "key_help_0125"): "Снять всё",
    ("patch_text01", "text/key_help_text.mbe/000_Sheet1.csv", "key_help_0128"): "Вернуть в бокс",

    # Main/side quest objectives with literal or reversed meanings.
    ("patch_text01", "text/main_quest_step.mbe/000_Sheet1.csv", "50070"): "Проверьте показания в переулке Кабукичо.",
    ("patch_text01", "text/main_quest_step.mbe/000_Sheet1.csv", "90025"): "Проберитесь через толпу вперёд.",
    ("patch_text01", "text/main_quest_step.mbe/000_Sheet1.csv", "150025"): "Доберитесь до Фабричного района верхом на Блимпмоне.",
    ("patch_text01", "text/main_quest_step.mbe/000_Sheet1.csv", "150030"): "Поговорите с Гардромоном (золотым).",
    ("patch_text01", "text/main_quest_step.mbe/000_Sheet1.csv", "150160"): "Доложите Гардромону (золотому).",
    ("patch_text01", "text/main_quest_step.mbe/000_Sheet1.csv", "190010"): "Победите титанов и доберитесь до первого вагона.",
    ("patch_text01", "text/main_quest_step.mbe/000_Sheet1.csv", "190020"): "Уберите ГранКувагамона с пути с помощью Дигиатаки.",
    ("patch_text01", "text/main_quest_step.mbe/000_Sheet1.csv", "280030"): "Сядьте на Уэмона.",
    ("patch_text01", "text/main_quest_step.mbe/000_Sheet1.csv", "390110"): "Отправляйтесь в сектор B.",
    ("patch_text01", "text/main_quest_step.mbe/000_Sheet1.csv", "390160"): "Сбегите вместе с Вулканусмоном.",
    ("patch_text01", "text/main_quest_step.mbe/000_Sheet1.csv", "400060"): "Приложите Семя тепла к замёрзшим шестерням.",
    ("patch_text01", "text/main_quest_step.mbe/000_Sheet1.csv", "400080"): "Используйте Семя холода на огненной стене.",
    ("patch_text01", "text/main_quest_step.mbe/000_Sheet1.csv", "410050"): "Переключите тумблер на Альфа-устройстве.",
    ("patch_text01", "text/main_quest_step.mbe/000_Sheet1.csv", "410060"): "Переключите тумблер на Бета-устройстве.",
    ("patch_text01", "text/main_quest_step.mbe/000_Sheet1.csv", "410070"): "Используйте Гамма-устройство.",
    ("patch_text01", "text/main_quest_step.mbe/000_Sheet1.csv", "440023"): "Отправляйтесь вместе с Гэкомоном в следующий мир.",
    ("patch_text01", "text/main_quest_step.mbe/000_Sheet1.csv", "440025"): "Отправляйтесь вместе с Пегасмоном в следующий мир.",
    ("patch_text01", "text/main_quest_step.mbe/000_Sheet1.csv", "440120"): "Отправляйтесь к Венусмону.",
    ("patch_text01", "text/main_quest_step.mbe/000_Sheet1.csv", "440122"): "Расчистите путь Дигиатакой.",
    ("patch_text01", "text/main_quest_step.mbe/000_Sheet1.csv", "440126"): "Отправляйтесь спасать следующего дигимона.",
    ("patch_text01", "text/main_quest_step.mbe/000_Sheet1.csv", "440145"): "Отнесите батарею Вулканусмону.",
    ("patch_text01", "text/main_quest_step.mbe/000_Sheet1.csv", "440200"): "Поговорите с Минервамон и Дианамон. * Не используется",
    ("patch_text01", "text/quest_step.mbe/000_Sheet1.csv", "910000"): "Отряд разбит.",
    ("patch_text01", "text/quest_step.mbe/000_Sheet1.csv", "910001"): "Время вышло.",
    ("patch_text01", "text/quest_step.mbe/000_Sheet1.csv", "910005"): "Витчмон первой добирается до цели.",
    ("patch_text01", "text/quest_step.mbe/000_Sheet1.csv", "101020"): "Получите разрешение починить Дигиментал.",
    ("patch_text01", "text/quest_title.mbe/000_Sheet1.csv", "42"): "Испытание",
    ("patch_text01", "text/quest_title.mbe/000_Sheet1.csv", "108"): "Зов невидимого",
    ("patch_text01", "text/quest_title.mbe/000_Sheet1.csv", "148"): "Знание убивает страх",
    ("patch_text01", "text/main_quest_title.mbe/000_Sheet1.csv", "100"): "Междумирье",
    ("patch_text01", "text/quest_outline.mbe/000_Sheet1.csv", "82"): "Я раздобыл деталь для потрясающей коллекционной фигурки,\nно мне нужен совет. Приходите ко мне в Фабричное ядро.",
    ("patch_text01", "text/quest_outline.mbe/000_Sheet1.csv", "179"): "Вот так проблема. Кто-то заперся в туалете и не выходит.\nК тому же он всё время бормочет о каком-то капитане\nи каком-то оружии...",
    ("patch_text01", "text/quest_outline.mbe/000_Sheet1.csv", "920"): "Тут полно скользких дигимонов! Постарайтесь не испачкаться\nв их слизи и какашках! Продержитесь до конца — и победа ваша!",
    ("patch_text01", "text/quest_outline.mbe/000_Sheet1.csv", "921"): "Они такие крутые и свирепые! Я собрал всех своих любимых\nдигимонов! Продержитесь до конца — и победа ваша!",
    ("patch_text01", "text/quest_outline.mbe/000_Sheet1.csv", "922"): "Океан полон тайн! Здесь совсем другая экосистема, чем на суше!\nПродержитесь до конца — и победа ваша!",
    ("patch_text01", "text/quest_outline.mbe/000_Sheet1.csv", "923"): "Берегитесь палящего пламени, которое сжигает всё, чего касается!\nОдно прикосновение мгновенно обратит вас в пепел.\nПродержитесь до конца, уклоняясь от него, — и победа ваша!",
    ("patch_text01", "text/quest_outline.mbe/000_Sheet1.csv", "950"): "Защитите лучшее гигантское ДигиМясо от дигимонов!\nЛетающих дигимонов легко не заметить, так что будьте осторожны!\nПобедите всех врагов — и вы выиграете!",
    ("patch_text01", "text/quest_outline.mbe/000_Sheet1.csv", "951"): "Защитите лучшее гигантское ДигиМясо от дигимонов!\nОстерегайтесь вспыльчивых дигимонов: они будут атаковать вас.\nПобедите всех врагов — и вы выиграете!",
    ("patch_text01", "text/quest_outline.mbe/000_Sheet1.csv", "952"): "Защитите лучшее гигантское ДигиМясо от дигимонов!\nОсобое внимание обратите на СкаллМаммона: он медлительный,\nно очень выносливый. Победите всех врагов — и вы выиграете!",
    ("patch_text01", "text/quest_outline.mbe/000_Sheet1.csv", "953"): "Защитите лучшее гигантское ДигиМясо от дигимонов!\nОстерегайтесь резких рывков летающих дигимонов.\nПобедите всех врагов — и вы выиграете!",

    # Map markers, tutorial headings and location names.
    ("patch_text01", "text/minimap_marker_help_text.mbe/000_Sheet1.csv", "minimap_marker_name_0041"): "Магазин предметов фермы",
    ("patch_text01", "text/minimap_marker_help_text.mbe/000_Sheet1.csv", "minimap_marker_name_0045"): "Магазин карт",
    ("patch_text01", "text/minimap_marker_help_text.mbe/000_Sheet1.csv", "minimap_marker_name_0047"): "Мастерская",
    ("patch_text01", "text/minimap_marker_help_text.mbe/000_Sheet1.csv", "minimap_marker_name_0080"): "Станция Локомона",
    ("patch_text01", "text/minimap_marker_help_text.mbe/000_Sheet1.csv", "minimap_marker_name_0100"): "Переход между районами",
    ("patch_text01", "text/minimap_marker_help_text.mbe/000_Sheet1.csv", "minimap_marker_name_0110"): "Порт летающих дигимонов",
    ("patch_text01", "text/minimap_marker_help_text.mbe/000_Sheet1.csv", "minimap_marker_name_0120"): "Диги-Кооп",
    ("patch_text01", "text/minimap_marker_help_text.mbe/000_Sheet1.csv", "minimap_marker_name_0190"): "Сменить локацию",
    ("patch_text01", "text/tutorial_title.mbe/000_Sheet1.csv", "tutorial_title_Boss_01"): "КО врага",
    ("patch_text01", "text/tutorial_title.mbe/000_Sheet1.csv", "tutorial_title_Convert_01"): "Конвертация и уровень сканирования",
    ("patch_text01", "text/tutorial_title.mbe/000_Sheet1.csv", "tutorial_title_Synthetic_01"): "Усиление синтезом",
    ("patch_text01", "text/tutorial_title.mbe/000_Sheet1.csv", "tutorial_title_PartyAegiomon_02"): "Эгиомон: эволюция",
    ("patch_text01", "text/tutorial_title.mbe/000_Sheet1.csv", "tutorial_title_FieldAttack_01"): "Дигиатаки",
    ("patch_text01", "text/tutorial_title.mbe/000_Sheet1.csv", "tutorial_title_BackAttack_01"): "Атаки со спины",
    ("patch_text01", "text/tutorial_title.mbe/000_Sheet1.csv", "tutorial_title_GimmickRide_01"): "Диги-Кооп",
    ("patch_text01", "text/tutorial_title.mbe/000_Sheet1.csv", "tutorial_title_MiniQuest_01"): "Свободные миссии",
    ("patch_text01", "text/tutorial_title.mbe/000_Sheet1.csv", "tutorial_title_Digitter_01"): "Дигилайн",
    ("patch_text01", "text/tutorial_title.mbe/000_Sheet1.csv", "tutorial_title_FarmGoodsShop_01"): "Магазин синтеза предметов фермы",
    ("patch_text01", "text/tutorial_title.mbe/000_Sheet1.csv", "tutorial_title_FarmDigicare_01"): "Дигиуход",
    ("patch_text01", "text/tutorial_title.mbe/000_Sheet1.csv", "tutorial_title_WorldView_004"): "Ваш Дигивайс",
    ("patch_text01", "text/tutorial_title.mbe/000_Sheet1.csv", "tutorial_title_EvolutionTechnique_01"): "Техника деволюции 1: очки таланта",
    ("patch_text01", "text/tutorial_title.mbe/000_Sheet1.csv", "tutorial_title_EvolutionTechnique_02"): "Техника деволюции 2: очки связи",
    ("patch_text01", "text/tutorial_title.mbe/000_Sheet1.csv", "tutorial_title_EvolutionTechnique_03"): "Техника деволюции 3: накопленные характеристики",
    ("patch_text01", "text/field_name.mbe/000_Sheet1.csv", "10110"): "Станция Синдзюку: восточный выход",
    ("patch_text01", "text/field_name.mbe/000_Sheet1.csv", "10111"): "Подземный Синдзюку: променад",
    ("patch_text01", "text/field_name.mbe/000_Sheet1.csv", "20108"): "Космический холод: область полулуния",
    ("patch_text01", "text/field_name.mbe/000_Sheet1.csv", "20404"): "Деревня Зубчатого леса",
    ("patch_text01", "text/field_name.mbe/000_Sheet1.csv", "20504"): "Фабричный туннель: шахты у ядра",
    ("patch_text01", "text/field_name.mbe/000_Sheet1.csv", "20505"): "Фабричное ядро",
    ("patch_text01", "text/field_name.mbe/000_Sheet1.csv", "20510"): "Райский колизей: проход",
    ("patch_text01", "text/field_name.mbe/000_Sheet1.csv", "20511"): "Райский колизей: проход",
    ("patch_text01", "text/field_name.mbe/000_Sheet1.csv", "20512"): "Райский колизей: проход",
    ("patch_text01", "text/field_name.mbe/000_Sheet1.csv", "21304"): "Подземная база спецназа: эстакада",
    ("patch_text01", "text/field_name.mbe/000_Sheet1.csv", "40005"): "Железная дорога Хранителя",
    ("patch_text01", "text/worldmap_place_explanation.mbe/000_Sheet1.csv", "201"): "Ворота Акихабары — об этом сразу говорит реклама для местных\nгиков. У выхода со станции расположены игровые автоматы\nи другие места для любителей поп-культуры.",
    ("patch_text01", "text/worldmap_place_explanation.mbe/000_Sheet1.csv", "10101"): "Здесь находится особая точка, позволяющая перемещаться между\nКосмической жарой и Космическим холодом.",
    ("patch_text01", "text/worldmap_place_explanation.mbe/000_Sheet1.csv", "10401"): "Площадь у станции Зубчатого леса железной дороги Локомона.\nГоворят, празднества в соседней деревне слышны даже отсюда.",
    ("patch_text01", "text/worldmap_place_explanation.mbe/000_Sheet1.csv", "10501"): "Площадь у станции Фабричного города железной дороги Локомона.\nЗдесь пахнет маслом и грохочут механизмы.",
    ("patch_text01", "text/worldmap_place_explanation.mbe/000_Sheet1.csv", "10521"): "Промышленный район Цифрового мира Илиады. Под управлением\nВулканусмона он снабжает весь край электричеством.",

    # DLC Digitter blocks that were still essentially raw machine translation.
    ("addcont_01_text01", "text/digitter_message_dlc01.mbe/000_Sheet1.csv", "dlc_010_040_10"): "Подобно зверю, который тайно расширяет подземное логово,\nПараллельмон раздвигает границы своей территории, прячась\nв карманах пространства-времени.",
    ("addcont_01_text01", "text/digitter_message_dlc01.mbe/000_Sheet1.csv", "dlc_010_040_20"): "Этот огромный коридор можно назвать дорогой сквозь само\nпространство-время. Похоже, он извивается, проходя через\nразрывы во времени и пространстве.",
    ("addcont_01_text01", "text/digitter_message_dlc01.mbe/000_Sheet1.csv", "dlc_010_050_10"): "Это место бесконечно расширяется и соединяется с бесчисленными\nизмерениями... Оно похоже на конечную станцию, где в одной точке\nсходится множество железнодорожных линий.",
    ("addcont_01_text01", "text/digitter_message_dlc01.mbe/000_Sheet1.csv", "dlc_010_050_20"): "Тем, кто впервые попадает на станцию Синдзюку, она часто кажется\nлабиринтом, верно? Здесь почти то же самое. Разница лишь в том...",
    ("addcont_01_text01", "text/digitter_message_dlc01.mbe/000_Sheet1.csv", "dlc_010_050_30"): "...что, если здесь заблудиться, миру просто придёт конец...",
    ("addcont_01_text01", "text/digitter_message_dlc01.mbe/000_Sheet1.csv", "dlc_010_060_10"): "Все обломки Акаши, которые мы видели до сих пор, объединяет одно:\nкаждый из них связан с отцом одной из этих двух девушек.",
    ("addcont_01_text01", "text/digitter_message_dlc01.mbe/000_Sheet1.csv", "dlc_010_060_20"): "Если подобные воспоминания будут появляться и дальше, возможно,\nих притягивает какая-то общая причина.",
    ("addcont_01_text01", "text/digitter_message_dlc01.mbe/000_Sheet1.csv", "dlc_010_070_10"): "Например, чувства этих девушек к своим отцам. Возможно, эти\nвоспоминания притягивают их «узы» и «любовь»?",
    ("addcont_01_text01", "text/digitter_message_dlc01.mbe/000_Sheet1.csv", "dlc_010_070_20"): "Но в случае с девушкой по имени Кёко Куреми всё, похоже,\nсовсем иначе... Скорее, всё ровно наоборот.",
    ("addcont_01_text01", "text/digitter_message_dlc01.mbe/000_Sheet1.csv", "dlc_010_080_10"): "Когда Кёко Куреми заговорила об отце, её лицо помрачнело.\nСтоит отношениям между людьми испортиться — и они превращаются\nв связь, которую трудно разорвать.",
    ("addcont_01_text01", "text/digitter_message_dlc01.mbe/000_Sheet1.csv", "dlc_010_080_20"): "Узы между людьми не всегда приносят радость. Когда любовь\nисчезает, на её месте возникает водоворот чувств, который люди\nназывают ненавистью.",
    ("addcont_01_text01", "text/digitter_message_dlc01.mbe/000_Sheet1.csv", "dlc_010_090_10"): "Продолжай искать Параллельмона. Если так пойдёт и дальше,\nнас ждёт хаос.",
    ("addcont_03_text01", "text/digitter_message_dlc03.mbe/000_Sheet1.csv", "dlc_030_010_10"): "Вы оказались в странном месте...",
    ("addcont_03_text01", "text/digitter_message_dlc03.mbe/000_Sheet1.csv", "dlc_030_010_20"): "Неужели законы природы в этом мире начинают рушиться...?\nЭто уже результат? Или, быть может, предвестие того, что ещё\nтолько случится...?",
    ("addcont_03_text01", "text/digitter_message_dlc03.mbe/000_Sheet1.csv", "dlc_030_010_30"): "Словно сцена из первобытных времён...",
    ("addcont_03_text01", "text/digitter_message_dlc03.mbe/000_Sheet1.csv", "dlc_030_020_10"): "Хаос — владения Параллельмона... Полагаю, он хочет расширить\nих ещё больше.",
    ("addcont_03_text01", "text/digitter_message_dlc03.mbe/000_Sheet1.csv", "dlc_030_020_20"): "Если вырвать могущественное существо из другого измерения,\nэто само по себе непременно породит искажение.",
    ("addcont_03_text01", "text/digitter_message_dlc03.mbe/000_Sheet1.csv", "dlc_030_020_30"): "Одно лишь столкновение двух существ, которым не суждено было\nвстретиться, способно разрушить саму логику мира. Думаю,\nдля Параллельмона это как музыка для ушей...",
    ("addcont_03_text01", "text/digitter_message_dlc03.mbe/000_Sheet1.csv", "dlc_030_020_40"): "Возможно, в каком-то ином будущем, где порядок рухнул,\nподобные картины встречаются повсюду.",
    ("addcont_03_text01", "text/digitter_message_dlc03.mbe/000_Sheet1.csv", "dlc_030_020_50"): "Само существование превращается в крошечную точку\nпространства-времени, обнажая свою основу.",

    # Tutorial articles with mixed forms of address or lost mechanical meaning.
    ("patch_text01", "text/tutorial_explanation.mbe/000_Sheet1.csv", "tutorial_exp_Escape_01_001"): "{fc9Удерживайте {r1} во время боя, чтобы сбежать от враждебных\nдигимонов.}\nДля агента нет ничего постыдного в том, чтобы проявить\nосмотрительность во время миссии.\n\nОднако постоянные побеги ничего вам не дадут. Кроме того,\nот некоторых врагов сбежать невозможно. Поэтому важно\nнабираться опыта и быть готовым к таким ситуациям.\n\nТщательно взвешивайте свои решения.",
    ("patch_text01", "text/tutorial_explanation.mbe/000_Sheet1.csv", "tutorial_exp_Boss_01_002"): "Враг может получать критические очки разными способами.\n\n{fc9Особенно много КО враг получает, когда атакует слабое место\nсоюзного дигимона.}\n\nВы можете уменьшить КО врага, выполняя действия, которые\nповышают ваши собственные КО.\n\n{fc9Действия, повышающие КО одной стороны, одновременно\nснижают КО другой.}",
    ("patch_text01", "text/tutorial_explanation.mbe/000_Sheet1.csv", "tutorial_exp_Personality_01_002"): "Тип личности влияет на дигимона несколькими способами.\n\n{fc9- Некоторые характеристики растут быстрее.\n- Меняется набор навыков личности.\n- Меняется эффект удара.}\n\nВыбирайте тип личности дигимона в соответствии с тем,\nв каком направлении хотите его развивать.",
    ("patch_text01", "text/tutorial_explanation.mbe/000_Sheet1.csv", "tutorial_exp_AgentLevel_01_001"): "Это числовое выражение опыта и уровня мастерства агента.\n\n{fc9Ранг агента повышается по мере того, как вы тратите очки аномалии\nна изучение навыков агента.}\n\nОт ранга агента зависят различные возможности, например:\n- усиление эффектов навыков агента;\n- условия эволюции дигимонов-партнёров.\n\nПродолжайте повышать свой ранг.",
    ("patch_text01", "text/tutorial_explanation.mbe/000_Sheet1.csv", "tutorial_exp_CrossArtsChange_01_001"): "{fc9С помощью навыка агента «Узы верности» можно изучать\nэффекты кросс-артов.}\n\nПереключать изученные кросс-арты можно в разделе\n«Агент > Настройки кросс-артов» на Дигивайсе.\n\nВыбирайте кросс-арты в соответствии со своей боевой стратегией.",
    ("patch_text01", "text/tutorial_explanation.mbe/000_Sheet1.csv", "tutorial_exp_Encounter_01_001"): "При контакте с враждебным дигимоном начинается бой.\n\nБои бывают суровыми, но получаемый в них опыт необходим:\nон помогает развивать дигимона-партнёра и повышает уровень\nсканирования для конвертации. Без сражений вам не преодолеть\nиспытания, которые ждут во время миссии.\n\nВступайте в бои и становитесь сильнее, агент.",
    ("patch_text01", "text/tutorial_explanation.mbe/000_Sheet1.csv", "tutorial_exp_PecmonRace_01_001"): "В этом состязании вам предстоит оседлать Пекмона и прийти\nк финишу раньше соперников.\n\nПомните:\n- ДигиМясо повышает скорость и временно делает вас неуязвимыми.\n- Столкновения с соперниками и препятствиями замедляют вас.\n- Все Пекмоны хорошо обучены и здоровы, однако организаторы\nне несут ответственности за возможные несчастные случаи.",
    ("patch_text01", "text/tutorial_explanation.mbe/000_Sheet1.csv", "tutorial_exp_GimmickRide_01_001"): "Это полевое действие позволяет заручиться помощью ближайших\nдигимонов и преодолеть препятствия, которые иначе были бы\nнепроходимы. Оно необходимо для выполнения миссий.\n{fc9Места для Диги-Коопа отмечены на карте специальным значком.}\n\nЕсли вы не знаете, как пройти дальше, поищите поблизости\nдигимона, который сможет помочь.",
    ("patch_text01", "text/tutorial_explanation.mbe/000_Sheet1.csv", "tutorial_exp_Digivaice_01_001"): "Этот портативный терминал — вершина технологий АДАМАС.\nВ нём есть множество функций, полезных при выполнении миссий.\nВся найденная во время миссии информация сохраняется\nна вашем Дигивайсе, помогая вам в работе.",
    ("patch_text01", "text/tutorial_explanation.mbe/000_Sheet1.csv", "tutorial_exp_SubQuest_01_001"): "Так называют просьбы, которые поступают от местных жителей\nв реальном времени. Когда обнаружена побочная миссия,\nвы получите уведомление по Дигилайну.\n\n{fc9Чтобы выбрать приоритетную миссию, откройте на Дигивайсе\n«Миссии > Побочные миссии» и нажмите\n{decision} «Отметить текущую цель».}\n\nСледите, чтобы эти просьбы не мешали вашим основным обязанностям.",
    ("patch_text01", "text/tutorial_explanation.mbe/000_Sheet1.csv", "tutorial_exp_DigisterDescripution_01_001"): "На Дигиферме можно повышать характеристики дигимона-партнёра\nи менять его личность.\n{fc9Даже находясь здесь, дигимоны получают столько же опыта,\nсколько дигимоны в вашем боксе.}",
    ("patch_text01", "text/tutorial_explanation.mbe/000_Sheet1.csv", "tutorial_exp_DigisterDescripution_01_003"): "Поиск материалов\nВаши дигимоны могут находить материалы на ферме.\nЭто занимает время, поэтому рекомендуется заходить на ферму\nмежду приключениями.\n\nРазмещение предметов фермы\nВы можете свободно обустраивать свою ферму.\n{fc9Это не влияет на тренировки дигимонов.}",
    ("patch_text01", "text/tutorial_explanation.mbe/000_Sheet1.csv", "tutorial_exp_CardsRule_01_004"): "[Таинственное дублирование после боёв JUCG]\n{fc9После карточного боя использованные карты, которых у вас ещё нет,\nдублируются, и вы можете выбрать одну из них.}\n\nЧем больше раундов вы выиграете, тем больше карт получите.\n5 побед = 3 карты\n3–4 победы = 2 карты\n1–2 победы = 1 карта\n0 побед = 0 карт",
    ("patch_text01", "text/tutorial_explanation.mbe/000_Sheet1.csv", "tutorial_exp_BattleCommand_03_001"): "Боевая команда. Нажмите {left} во время хода дигимона,\nчтобы поддержать его предметом.\n\n{fc9Использование предмета не расходует ход дигимона:\nпосле этого он всё равно сможет выполнить другую команду.}\n\nВсегда держите предметы наготове, чтобы дигимон-партнёр\nмог сражаться в полную силу.",
    ("patch_text01", "text/tutorial_explanation.mbe/000_Sheet1.csv", "tutorial_exp_Items_01_001"): "Предметы агента делятся на следующие категории.\n\nВосстановление: восстанавливают дигимона-партнёра.\nУсиление: повышают его характеристики.\nОсобые: дорого продаются или используются при особых условиях.\nСнаряжение: экипируется на дигимона-партнёра.\nМатериалы: используются в мастерской.\nФерма: используются на Дигиферме.\nЦенности: важны для выполнения миссий.",
    ("patch_text01", "text/tutorial_explanation.mbe/000_Sheet1.csv", "tutorial_exp_EvolutionTechnique_02_001"): "К накопленным характеристикам при эволюции или деволюции\nдобавляется 1% характеристик предыдущей формы.\n{fc9Чем выше связь дигимона, тем больше раз можно переносить\nнакопленные характеристики.}\n\nПовышайте связь дигимона и используйте эволюцию и деволюцию,\nчтобы сделать его ещё сильнее.",
    ("patch_text01", "text/tutorial_explanation.mbe/000_Sheet1.csv", "tutorial_exp_EvolutionTechnique_03_001"): "Значения характеристик, повышенных предметами усиления,\nтакже входят в накопленные характеристики.\n\nПри эволюции или деволюции к ним добавляется 1% характеристик\nпредыдущей формы.\n\n{fc9Связь определяет, сколько раз накопленные характеристики\nможно перенести после эволюции или деволюции. Заранее повышайте\nих как можно сильнее, чтобы максимально использовать связь.}",

    # Fixed female Asuna Shiroki / Dr. Simmons context missed by the broad pass.
    ("patch_text01", "message/d11.mbe/000_Sheet1.csv", "f_d1102_0100_0025"): "Я сделаю это сама. Мы не можем допустить, чтобы их усилия\nпропали даром.",
    ("patch_text01", "message/s110_090.mbe/000_Sheet1.csv", "s110_090_450"): "Я просто пошутила. В любом случае посмотрю, не осталось ли\nчего-нибудь.",
    ("patch_text01", "message/s910_171.mbe/000_Sheet1.csv", "s910_171_610"): "Доктор Симмонс была здесь совсем недавно.",
    ("patch_text01", "message/s010_180.mbe/000_Sheet1.csv", "s010_180_120"): "И не говори. Знаешь, забавно: никогда бы не подумала,\nчто буду вот так разговаривать с ТОБОЙ.",
    ("patch_text01", "message/s010_180.mbe/000_Sheet1.csv", "s010_180_130"): "Когда ты ещё была БлэкГатомон, общение явно не было\nтвоей сильной стороной.",
    ("patch_text01", "message/s010_180.mbe/000_Sheet1.csv", "s010_180_150"): "Но я твёрдо решила с тобой подружиться!",
    ("patch_text01", "message/s010_180.mbe/000_Sheet1.csv", "s010_180_170"): "Это случилось, когда я ремонтировала генератор электромагнитной\nсети, верно?",
    ("patch_text01", "message/s010_180.mbe/000_Sheet1.csv", "s010_180_280"): "Ты... хочешь... со мной подружиться?",
    ("patch_text01", "message/s010_180.mbe/000_Sheet1.csv", "s010_180_310"): "Дигимон... и человек? Друзья? Я... никогда даже не думала,\nчто такое возможно.",
    ("patch_text01", "message/s010_180.mbe/000_Sheet1.csv", "s010_180_320"): "Но с тобой... Да, думаю, мы могли бы подружиться.",
    ("patch_text01", "message/s010_180.mbe/000_Sheet1.csv", "s010_180_370"): "Мы только что подружились! Мы даже ещё толком не поговорили!",
    ("patch_text01", "message/s010_180.mbe/000_Sheet1.csv", "s010_180_420"): "А ты полностью изменила мои взгляды. Я хочу ещё много раз\nвот так с тобой поговорить.",
    ("patch_text01", "text/tutorial_explanation.mbe/000_Sheet1.csv", "tutorial_exp_Accumulation_01_002"): "Способы повысить накопленные характеристики:\n\n{fc9- Использование предметов усиления\nВ зависимости от предмета его прибавка к определённой\nхарактеристике также войдёт в накопленные характеристики.\n\n- Эволюция и деволюция\nК накопленным характеристикам добавляется 10% характеристик\nпредыдущей формы, полученных за уровни и тренировки на ферме.\n\n- Усиление синтезом\nПередаётся часть накопленных характеристик дигимона,\nиспользованного как материал усиления.}",

    # Grammatical cases after unifying Paradise Colosseum terminology.
    ("patch_text01", "message/arena01.mbe/000_Sheet1.csv", "arena01_f001_018_020"): "Кто сильнейший участник Райского колизея?\nЭти заклятые соперники вот-вот это выяснят!",
    ("patch_text01", "message/s010_159.mbe/000_Sheet1.csv", "s010_159_410"): "Я хочу испытать новую силу в Райском колизее.\nБуду ждать твоего вызова!",
    ("patch_text01", "message/s040_160.mbe/000_Sheet1.csv", "s040_160_470"): "Встретимся в Райском колизее. Я буду сражаться с тобой\nизо всех сил, готовясь к большой битве.",
    ("patch_text01", "message/s040_160.mbe/000_Sheet1.csv", "s040_160_530"): "Пора отработать всё съеденное на тренировке!\nУвидимся в Райском колизее!",
    ("patch_text01", "message/s050_176.mbe/000_Sheet1.csv", "s050_176_300"): "Хм. Пожалуй, лучше всего испытать их в бою\nв Райском колизее.",
    ("patch_text01", "message/s110_112.mbe/000_Sheet1.csv", "s110_112_080"): "Хозяин, с которым я должен встретиться в Райском колизее,\nнаверняка уже в ярости. Я опаздываю...",
    ("patch_text01", "text/quest_outline.mbe/000_Sheet1.csv", "111"): "Фу, как скучно. Куда, чёрт возьми, запропастился Джесмон?\nРазве мы не договаривались встретиться в Райском колизее?",
    ("patch_text01", "text/quest_outline.mbe/000_Sheet1.csv", "160"): "Конечно, я стал сильнее. Но теперь этот Большой Брат...\nЧто же нам делать с Райским колизеем?",
}


# Exact source/translation pairs: only these known mechanical stage directions
# are rewritten.  The source check prevents a Russian word from being changed
# merely because it happens to look similar outside the reviewed context.
REMARK_REWRITES: dict[tuple[str, str], str] = {
    ("hurl", " швырять"): "тошнит",
    ("retch", " рвота"): "тошнит",
    ("retch", "рвота"): "тошнит",
    ("hiccup", " иккинг"): "икает",
    ("hiccup", " иккинг "): "икает",
    ("hiccup", "иккинг"): "икает",
    ("hiccup", "иккинг "): "икает",
    ("hiccup", "\nиккинг"): "икает",
    ("munch, munch", " жуй, жуй"): "жуёт",
    ("munch, munch", " жуй, жуй "): "жуёт",
    ("munch, munch", "жуй, жуй"): "жуёт",
    ("cough", " кашель"): "кашляет",
    ("cough", "кашель"): "кашляет",
    ("tremble", " дрожать"): "дрожит",
    ("shudder", "\nсодрогнись"): "вздрагивает",
    ("shudder", " содрогнись"): "вздрагивает",
    ("wink", " подмигивание"): "подмигивает",
    ("sniff, sniff", " нюхай, нюхай"): "принюхивается",
    ("mumbling", " бормоча"): "бормочет",
    ("whispering", " шепот"): "шёпотом",
    ("whispering", "шепот"): "шёпотом",
    ("crash", " крах "): "грохот",
}


EXTRA_VARIANTS: dict[tuple[str, str, str], dict[str, str]] = {}


# Full-scene rechecks showed that these lines address fixed Digimon rather
# than the selectable protagonist: JumboGamemon and BanchoLillymon.
OBSOLETE_VARIANTS = {
    ("addcont_02_text01", "message/d220.mbe/000_Sheet1.csv", "d220_030_150"),
    ("patch_text01", "message/battle.mbe/000_Sheet1.csv", "1200020126"),
    ("patch_text01", "message/battle.mbe/000_Sheet1.csv", "1200020170"),
    ("patch_text01", "message/d01.mbe/000_Sheet1.csv", "f_d0101_0140_0020"),
    ("patch_text01", "message/d02.mbe/000_Sheet1.csv", "f_d0201_0650_0060"),
    ("patch_text01", "message/d02.mbe/000_Sheet1.csv", "f_d0204_0260_0030"),
    ("patch_text01", "message/m110.mbe/000_Sheet1.csv", "m110_050_120"),
    ("patch_text01", "message/m120.mbe/000_Sheet1.csv", "m120_100_230"),
    ("patch_text01", "message/m130.mbe/000_Sheet1.csv", "m130_090_020"),
    ("patch_text01", "message/m170.mbe/000_Sheet1.csv", "m170_065_100"),
    ("patch_text01", "message/m170.mbe/000_Sheet1.csv", "m170_090_030"),
    ("patch_text01", "message/m170.mbe/000_Sheet1.csv", "m170_130_010"),
    ("patch_text01", "message/m170.mbe/000_Sheet1.csv", "m170_130_050"),
    ("patch_text01", "message/m190.mbe/000_Sheet1.csv", "m190_070_090"),
    ("patch_text01", "message/s020_019.mbe/000_Sheet1.csv", "s020_019_530"),
    ("patch_text01", "message/t03.mbe/000_Sheet1.csv", "f_t0302_0110_0120"),
}


SPURIOUS_ALIAS_CLEARS = {
    ("patch_text01", "message/d02.mbe/000_Sheet1.csv", "f_d0201_870_0020"),
    ("patch_text01", "message/field_text.mbe/000_Sheet1.csv", "g_hazama_0020_0020"),
    ("patch_text01", "message/field_text.mbe/000_Sheet1.csv", "g_hazama_0020_0030"),
    ("patch_text01", "message/field_text.mbe/000_Sheet1.csv", "g_hazama_0020_0040"),
    ("patch_text01", "message/field_text.mbe/000_Sheet1.csv", "g_hazama_0020_0050"),
    ("patch_text01", "message/field_text.mbe/000_Sheet1.csv", "g_hazama_0020_0080"),
}


TERM_REPLACEMENTS = (
    ("Парадизский колизей", "Райский колизей"),
    ("Парадизском Колизее", "Райском колизее"),
    ("Парадизского Колизея", "Райского колизея"),
    ("Парадизский Колизей", "Райский колизей"),
    ("Парадиз-Колизее", "Райском колизее"),
    ("Парадиз Колизее", "Райском колизее"),
    ("Парадайз Колизей", "Райский колизей"),
    ("Парадиз Колизей", "Райский колизей"),
    ("Высотном колизее", "Райском колизее"),
    ("Колизее Парадайз", "Райском колизее"),
    ("Райский Колизей", "Райский колизей"),
    ("Райского Колизея", "Райского колизея"),
)


EXACT_SOURCE_TEXT_REWRITES = (
    (
        "patch_text01",
        "text/item_explanation.mbe/000_Sheet1.csv",
        "A card with a Digimon printed on it.",
        "Карточка с напечатанным на ней цифровым символом.",
        "Карта с изображением дигимона.",
        459,
    ),
    (
        "patch_text01",
        "text/item_explanation.mbe/000_Sheet1.csv",
        "A farm item.\r\nUse this to customize your Digifarm to your liking.",
        "Товар для фермы. Используйте его, чтобы настроить Дигиферму по своему вкусу.",
        "Предмет для Дигифермы.\nИспользуйте его, чтобы оформить Дигиферму по своему вкусу.",
        103,
    ),
    (
        "patch_text01",
        "text/item_explanation.mbe/000_Sheet1.csv",
        "Food for Digimon.\r\nGive it to Digimon on the Digifarm to increase their Bond\r\nbit by bit.",
        "Еда для дигимона. Дай её дигимону на Дигиферме, / чтобы постепенно укреплять связь с ним.",
        "Еда для дигимонов.\nДайте её дигимону на Дигиферме, чтобы постепенно укреплять связь с ним.",
        12,
    ),
    (
        "patch_text01",
        "message/digimon_chat.mbe/000_Sheet1.csv",
        "I had a feeling that was the case. Having friends gives me strength!",
        "У меня было предчувствие, что так оно и есть. Наличие друзей\nпридает мне сил!",
        "Так и есть! Друзья и правда придают мне сил!",
        16,
    ),
)


TARGETED_CELL_REWRITES = (
    (
        "patch_text01",
        "text/item_explanation.mbe/000_Sheet1.csv",
        tuple(str(value) for value in (*range(204, 210), 212, *range(214, 222))),
        ((
            "Любимая еда дигимона / для использования на Дигиферме",
            "Любимая еда дигимонов\n/Для Дигифермы",
        ),),
    ),
    (
        "patch_text01",
        "text/item_explanation.mbe/000_Sheet1.csv",
        tuple(str(value) for value in range(901, 912)),
        (("Цифровое яйцо с выгравированным", "Дигиментал с выгравированным"),),
    ),
    (
        "patch_text01",
        "text/item_auto_explanation.mbe/000_Sheet1.csv",
        tuple(str(value) for value in (13, 14, 19, 20, 38, 39, 57, *range(62, 68), 70, 71, *range(76, 82))),
        (("HP", "ОЗ"), ("SP", "ОС")),
    ),
)


ITEM_BOTH_NAME_UPDATES = {
    "47": "Дружба S",
    "203": "ДигиМясо",
    "210": "ДигиЯблоко",
    "211": "ДигиМорковь",
    "213": "ДигиБанан",
    "222": "ДигиРыба",
    "223": "ДигиПротеин",
    "750": "Диги-предохранитель",
    "791": "Семя тепла",
    "792": "Семя холода",
    "794": "Лабораторный пропуск",
    "798": "Частичка души Этемона",
    "799": "Дамп ядра доктора Куги",
    "10921": "Карта: Краниуммон + Энбаррмон",
    "1144": "Бигуди для горячей завивки Хироко",
    "1146": "Талисман Клавис Ангемона",
    "1155": "Бочка бога вина",
    "1175": "Копия значка исследователя",
    "20512": "Металлическая бочка",
    "20520": "Светофор",
    "20521": "Качели-балансир",
    "20523": "Горка",
    "20524": "Изогнутый рукоход",
    "20535": "Молочный бидон",
    "20536": "Вагонетка",
    "20541": "Стопка шин",
    "20613": "Героическая статуя (Кокувамон А и Б)",
    "20615": "Героическая статуя (Хангёмон)",
    "20617": "Героическая статуя (Гэкомон)",
    "22010": "Пропуск Вейда",
    "912": "Человеческий дух пламени",
    "913": "Звериный дух пламени",
    "914": "Человеческий дух света",
    "915": "Звериный дух света",
    "804": "Футболка с пиксель-артом (Агумон)",
    "807": "Футболка с пиксель-артом (Габумон)",
    "808": "Футболка с пиксель-артом (Гомамон)",
    "809": "Футболка с пиксель-артом (Тейлмон)",
    "810": "Футболка с пиксель-артом (Тентомон)",
    "811": "Футболка с пиксель-артом (Патамон)",
    "812": "Футболка с пиксель-артом (Пиёмон)",
    "813": "Футболка с пиксель-артом (Пальмон)",
    "814": "Футболка сотрудника раменной",
    "806": "Форма службы общественной безопасности",
    "818": "Футболка с принтом артхаусного фильма",
    "819": "Памятная футболка к аниме-фильму",
}


ITEM_NAME_ONLY_UPDATES = {
    "22001": "Таинственное устройство (красное)",
    "22002": "Таинственное устройство (золотое)",
    "22003": "Таинственное устройство (синее)",
    "22004": "Таинственное устройство (белое)",
    "22005": "Таинственное устройство (чёрное)",
}


ITEM_RUBY_ONLY_UPDATES = {
    "22001": "Маятник (красный)",
    "22002": "Маятник (золотой)",
    "22003": "Маятник (синий)",
    "22004": "Маятник (белый)",
    "22005": "Маятник (чёрный)",
    "785": "Фэнзин Вулканусмона",
    "787": "Фигурка Вулканусмона B",
}


REMARK_RE = re.compile(r"\*([^*]+)\*")


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
        if quote_all:
            csv.writer(handle, lineterminator=newline).writerow(rows[0])
            csv.writer(handle, lineterminator=newline, quoting=csv.QUOTE_ALL).writerows(rows[1:])
        else:
            csv.writer(handle, lineterminator=newline).writerows(rows)


def rewrite_remarks(source: str, translated: str) -> tuple[str, int]:
    source_remarks = list(REMARK_RE.finditer(source))
    translated_remarks = list(REMARK_RE.finditer(translated))
    if not source_remarks or len(source_remarks) != len(translated_remarks):
        return translated, 0

    source_iter = iter(source_remarks)
    exact_rewrites = 0

    def replace(match: re.Match[str]) -> str:
        nonlocal exact_rewrites
        source_content = next(source_iter).group(1)
        translated_content = match.group(1)
        replacement = REMARK_REWRITES.get((source_content, translated_content))
        if replacement is not None:
            exact_rewrites += 1
        else:
            replacement = translated_content.strip()
        return f"*{replacement}*"

    return REMARK_RE.sub(replace, translated), exact_rewrites


def apply_source_checked_patterns() -> tuple[int, int, int]:
    """Fix source-confirmed ellipses and mechanical stage directions."""

    if not ORIGINAL_ROOT.exists():
        print(f"Source snapshot absent; skipped source-pair cleanup: {ORIGINAL_ROOT}")
        return 0, 0, 0

    changed_rows = ellipses = exact_remarks = 0
    translated_root = CSV_ROOT / "patch_text01" / "message"
    source_root = ORIGINAL_ROOT / "patch_text01" / "csv" / "message"
    for path in sorted(translated_root.glob("*.mbe/000_Sheet1.csv")):
        source_path = source_root / path.parent.name / path.name
        if not source_path.exists():
            continue
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.reader(handle))
        with source_path.open("r", encoding="utf-8-sig", newline="") as handle:
            source_rows = {row[0]: row for row in csv.reader(handle) if row}

        dirty = False
        for row in rows[1:]:
            source_row = source_rows.get(row[0]) if row else None
            if not source_row or len(row) < 3 or len(source_row) < 3:
                continue
            before = row[2]
            if source_row[2].startswith("...") and re.match(r"^\.\.[^.]", row[2]):
                row[2] = "." + row[2]
                ellipses += 1
            row[2], rewritten = rewrite_remarks(source_row[2], row[2])
            exact_remarks += rewritten
            if row[2] != before:
                changed_rows += 1
                dirty = True
        if dirty:
            write_rows(path, rows)
    return changed_rows, ellipses, exact_remarks


def upsert_extra_variants() -> tuple[int, int]:
    fields = (
        "package",
        "file",
        "base_id",
        "role",
        "male_protagonist_text",
        "female_protagonist_text",
        "confidence",
        "basis",
    )
    with DATASET.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != fields:
            raise RuntimeError(f"Unexpected dynamic-gender columns: {reader.fieldnames}")
        rows = list(reader)

    by_key = {(row["package"], row["file"], row["base_id"]): row for row in rows}
    changed = current = 0
    for key in OBSOLETE_VARIANTS:
        if key in by_key:
            del by_key[key]
            changed += 1
        else:
            current += 1
    for key, values in EXTRA_VARIANTS.items():
        wanted = dict(zip(fields[:3], key)) | values
        if by_key.get(key) == wanted:
            current += 1
            continue
        by_key[key] = wanted
        changed += 1

    if changed:
        ordered = sorted(by_key.values(), key=lambda row: (row["package"], row["file"], row["base_id"]))
        with DATASET.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
            writer.writeheader()
            writer.writerows(ordered)
    return changed, current


def remove_obsolete_generated_rows() -> tuple[int, int]:
    grouped: dict[tuple[str, str], set[str]] = defaultdict(set)
    for package, filename, base_id in OBSOLETE_VARIANTS:
        grouped[(package, filename)].update({f"{base_id}__H", f"{base_id}__F"})

    removed = absent = 0
    for (package, filename), generated_ids in grouped.items():
        path = CSV_ROOT / package / filename
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.reader(handle))
        present = {row[0] for row in rows if row and row[0] in generated_ids}
        if present:
            rows = [row for row in rows if not row or row[0] not in generated_ids]
            removed += len(present)
            write_rows(path, rows)
        absent += len(generated_ids - present)
    return removed, absent


def clear_spurious_aliases() -> tuple[int, int]:
    grouped: dict[tuple[str, str], set[str]] = defaultdict(set)
    for package, filename, row_id in SPURIOUS_ALIAS_CLEARS:
        grouped[(package, filename)].add(row_id)

    changed = current = 0
    for (package, filename), wanted in grouped.items():
        path = CSV_ROOT / package / filename
        source_path = ORIGINAL_ROOT / package / "csv" / filename
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.reader(handle))
        with source_path.open("r", encoding="utf-8-sig", newline="") as handle:
            source = {row[0]: row for row in csv.reader(handle) if row}
        found: set[str] = set()
        dirty = False
        for row in rows[1:]:
            if not row or row[0] not in wanted:
                continue
            found.add(row[0])
            original = source.get(row[0])
            if not original or len(original) != 4 or original[3] != "":
                raise RuntimeError(f"Refusing alias clear without empty source column: {path}:{row[0]}")
            if len(row) != 4:
                raise RuntimeError(f"Expected four MBE columns: {path}:{row[0]}")
            if row[3] == "":
                current += 1
            else:
                row[3] = ""
                changed += 1
                dirty = True
        if found != wanted:
            raise RuntimeError(f"Missing alias rows in {path}: {sorted(wanted - found)}")
        if dirty:
            write_rows(path, rows)
    return changed, current


def apply_confirmed_terminology() -> tuple[int, int]:
    changed_rows = replacements = 0
    for path in sorted(CSV_ROOT.rglob("*.csv")):
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.reader(handle))
        dirty = False
        for row in rows[1:]:
            before = list(row)
            for index, value in enumerate(row):
                for source, target in TERM_REPLACEMENTS:
                    count = value.count(source)
                    if count:
                        value = value.replace(source, target)
                        replacements += count
                row[index] = value
            if row != before:
                changed_rows += 1
                dirty = True
        if dirty:
            write_rows(path, rows)
    return changed_rows, replacements


def apply_exact_source_text_rewrites() -> tuple[int, int]:
    changed = current = 0
    for package, filename, source_text, before, after, expected in EXACT_SOURCE_TEXT_REWRITES:
        path = CSV_ROOT / package / filename
        source_path = ORIGINAL_ROOT / package / "csv" / filename
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.reader(handle))
        with source_path.open("r", encoding="utf-8-sig", newline="") as handle:
            source = {row[0]: row for row in csv.reader(handle) if row}
        column = 2 if filename.startswith("message/") else 1
        matched = 0
        dirty = False
        for row in rows[1:]:
            original = source.get(row[0]) if row else None
            if not original or len(original) <= column or original[column] != source_text:
                continue
            matched += 1
            if len(row) <= column:
                raise RuntimeError(f"Missing text column: {path}:{row[0]}")
            if row[column] == after:
                current += 1
            elif row[column] == before:
                row[column] = after
                changed += 1
                dirty = True
            else:
                raise RuntimeError(
                    f"Unexpected translation for exact source pair: {path}:{row[0]}={row[column]!r}"
                )
        if matched != expected:
            raise RuntimeError(f"Expected {expected} exact source rows in {path}, found {matched}")
        if dirty:
            write_rows(path, rows)
    return changed, current


def apply_targeted_cell_rewrites() -> tuple[int, int]:
    changed = current = 0
    for package, filename, row_ids, replacements in TARGETED_CELL_REWRITES:
        path = CSV_ROOT / package / filename
        wanted = set(row_ids)
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.reader(handle))
        column = 2 if filename.startswith("message/") else 1
        found: set[str] = set()
        dirty = False
        for row in rows[1:]:
            if not row or row[0] not in wanted:
                continue
            found.add(row[0])
            before = row[column]
            after = before
            for source, target in replacements:
                after = after.replace(source, target)
            if after != before:
                row[column] = after
                changed += 1
                dirty = True
            elif any(target in before for _, target in replacements):
                current += 1
            else:
                raise RuntimeError(f"No expected targeted text in {path}:{row[0]}={before!r}")
        if found != wanted:
            raise RuntimeError(f"Missing targeted rows in {path}: {sorted(wanted - found)}")
        if dirty:
            write_rows(path, rows)
    return changed, current


def apply_item_name_updates() -> tuple[int, int]:
    changed = current = 0
    tables = (
        ("text/item_name.mbe/000_Sheet1.csv", ITEM_BOTH_NAME_UPDATES | ITEM_NAME_ONLY_UPDATES),
        ("text/item_ruby.mbe/000_Sheet1.csv", ITEM_BOTH_NAME_UPDATES | ITEM_RUBY_ONLY_UPDATES),
    )
    for filename, updates in tables:
        path = CSV_ROOT / "patch_text01" / filename
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.reader(handle))
        found: set[str] = set()
        dirty = False
        for row in rows[1:]:
            if not row or row[0] not in updates:
                continue
            found.add(row[0])
            if row[1] == updates[row[0]]:
                current += 1
            else:
                row[1] = updates[row[0]]
                changed += 1
                dirty = True
        if found != set(updates):
            raise RuntimeError(f"Missing item-name rows in {path}: {sorted(set(updates) - found)}")
        if dirty:
            write_rows(path, rows)
    return changed, current


def main() -> None:
    grouped: dict[tuple[str, str], dict[str, str]] = defaultdict(dict)
    for (package, filename, row_id), text in U.items():
        grouped[(package, filename)][row_id] = text
    changed = current = 0
    for (package, filename), wanted in grouped.items():
        path = CSV_ROOT / package / filename
        encoding, newline, quote_all = serialization(path)
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.reader(handle))
        found: set[str] = set()
        dirty = False
        column = 2 if filename.startswith("message/") else 1
        for row in rows[1:]:
            if row and row[0] in wanted:
                found.add(row[0])
                if len(row) <= column:
                    raise RuntimeError(f"{path}:{row[0]} has only {len(row)} columns")
                if row[column] == wanted[row[0]]:
                    current += 1
                else:
                    row[column] = wanted[row[0]]
                    changed += 1
                    dirty = True
        missing = set(wanted) - found
        if missing:
            raise RuntimeError(f"{path}: missing {sorted(missing)}")
        if dirty:
            write_rows(path, rows)
    pattern_rows, ellipses, exact_remarks = apply_source_checked_patterns()
    variant_changed, variant_current = upsert_extra_variants()
    obsolete_removed, obsolete_absent = remove_obsolete_generated_rows()
    alias_changed, alias_current = clear_spurious_aliases()
    term_rows, term_replacements = apply_confirmed_terminology()
    source_changed, source_current = apply_exact_source_text_rewrites()
    targeted_changed, targeted_current = apply_targeted_cell_rewrites()
    item_name_changed, item_name_current = apply_item_name_updates()
    print(f"Targets: {len(U)}")
    print(f"Changed: {changed}")
    print(f"Already current: {current}")
    print(
        "Source-pair cleanup: "
        f"{pattern_rows} changed rows, {ellipses} ellipses, {exact_remarks} exact remarks"
    )
    print(f"Extra dynamic variants: {variant_changed} changed, {variant_current} current")
    print(f"Obsolete generated variants: {obsolete_removed} removed, {obsolete_absent} absent")
    print(f"Spurious aliases: {alias_changed} cleared, {alias_current} current")
    print(f"Terminology: {term_rows} changed rows, {term_replacements} replacements")
    print(f"Exact source batches: {source_changed} changed, {source_current} current")
    print(f"Targeted cell rewrites: {targeted_changed} changed, {targeted_current} current")
    print(f"Item names/ruby: {item_name_changed} changed, {item_name_current} current")


if __name__ == "__main__":
    main()

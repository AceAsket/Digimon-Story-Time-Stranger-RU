from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CSV_ROOT = ROOT / "csv"
LOG_PATH = ROOT / "logs" / "fix_dialogue_gender_and_style_v064.log"


# These lines were checked against the English tables from Steam build
# 23514637. Most were produced by treating a layout newline as the end of an
# English sentence, which left the second Russian line grammatically detached.
STRUCTURE_UPDATES: dict[tuple[str, str, str], str] = {
    ("addcont_01_text01", "message/d110.mbe/000_Sheet1.csv", "d110_090_010"):
        "Тебя тоже задел луч того дигимона,\n{player}?",
    ("addcont_01_text01", "message/d120.mbe/000_Sheet1.csv", "d120_030_090"):
        "Этот взгляд... Не припомню, чтобы при семье\nу него бывало такое лицо.",
    ("addcont_01_text01", "message/d120.mbe/000_Sheet1.csv", "d120_030_120"):
        "Бесчисленные фрагменты пространства-времени погребены\nза пределами Акашического бэкдора.",
    ("addcont_01_text01", "message/d120.mbe/000_Sheet1.csv", "d120_030_140"):
        "Пусть эта сила и невелика, но она тянет существ обратно —\nк фрагментам пространства-времени, от которых их отрезало.",
    ("addcont_01_text01", "message/d120.mbe/000_Sheet1.csv", "d120_030_160"):
        "Можно сказать, именно так и работают\nявления, которые вы сейчас наблюдаете.",
    ("addcont_01_text01", "message/d120.mbe/000_Sheet1.csv", "d120_070_100"):
        "«Ага. Пора покончить с тем,\nиз-за чего я столько потерял и перенёс».",
    ("addcont_01_text01", "message/d120.mbe/000_Sheet1.csv", "d120_070_110"):
        "Твоего отца тяжело ранил дигимон —\nпоследствия тех травм мучили его ещё долго.",
    ("addcont_01_text01", "message/d120.mbe/000_Sheet1.csv", "d120_070_120"):
        "Полагаю, поэтому ты ненавидишь дигимонов\nвсей душой...",
    ("addcont_01_text01", "message/d120.mbe/000_Sheet1.csv", "d120_080_010"):
        "Некоторые дигимоны нападают на людей — как те, с которыми\nмы только что сражались. Но мы не такие.",
    ("addcont_01_text01", "message/d120.mbe/000_Sheet1.csv", "d120_100_050"):
        "«Многие люди до сих пор числятся пропавшими,\nно одно мы знаем наверняка».",
    ("addcont_01_text01", "message/d120.mbe/000_Sheet1.csv", "d120_100_060"):
        "«Каждый из них делал всё возможное,\nчтобы выполнить свою миссию».",
    ("addcont_01_text01", "message/d120.mbe/000_Sheet1.csv", "d120_100_140"):
        "Когда ты смотришь на отца, у тебя такой взгляд...\nМне становится страшно.",
    ("addcont_01_text01", "message/d120.mbe/000_Sheet1.csv", "d120_110_110"):
        "Я слышал, он выступил против Параллельмона,\nкогда тот устроил погром в Синдзюку.",
    ("addcont_01_text01", "message/d120.mbe/000_Sheet1.csv", "d120_110_150"):
        "Наверное, он забыл, насколько тяжело\nего когда-то ранил дигимон...",
    ("addcont_01_text01", "message/d130.mbe/000_Sheet1.csv", "d130_050_020"):
        "«Так точно, сэр. Это враждебный дигимон,\nо котором нам пока почти ничего не известно».",
    ("addcont_01_text01", "message/d130.mbe/000_Sheet1.csv", "d130_050_040"):
        "«Понятно... Тогда нужно действовать\nкак можно скорее».",
    ("addcont_01_text01", "message/d130.mbe/000_Sheet1.csv", "d130_060_090"):
        "«Транквилизаторные пули не ранят дигимонов,\nа лишь ненадолго усмиряют их».",
    ("addcont_01_text01", "message/d140.mbe/000_Sheet1.csv", "d140_040_190"):
        "Спасибо. За веру в дигимонов...\nи в нас.",
    ("addcont_02_text01", "message/d210.mbe/000_Sheet1.csv", "d210_040_100"):
        "Я о том, что крупные города уже почти не работают,\nа отсчёт до апокалипсиса начался.",
    ("addcont_02_text01", "message/d210.mbe/000_Sheet1.csv", "d210_040_110"):
        "Большинство людей сдались и просто ждут гибели.\nА ты всё это время чем занимался?!",
    ("addcont_02_text01", "message/d210.mbe/000_Sheet1.csv", "d210_040_230"):
        "Вероятно, его тоже перенесли сюда из другого мира —\nбезымянного белого воина...",
    ("addcont_02_text01", "message/d220.mbe/000_Sheet1.csv", "d220_030_020"):
        "За такими дверями прошлое, настоящее и будущее\nперемешиваются и сливаются воедино, не считаясь с порядком.",
    ("addcont_02_text01", "message/d220.mbe/000_Sheet1.csv", "d220_030_050"):
        "Перед нами прежний Синдзюку...\nещё до того, как в дверь постучался апокалипсис!",
    ("addcont_02_text01", "message/d220.mbe/000_Sheet1.csv", "d220_030_100"):
        "Именно тот инцидент, который вы называете Адом Синдзюку,\nпомог Параллельмону набрать силу.",
    ("addcont_02_text01", "message/d220.mbe/000_Sheet1.csv", "d220_040_100"):
        "БанчоЛилимон, вернись на площадь, где мы встретили\nвоина в белом, и немного отдохни.",
    ("addcont_02_text01", "message/d220.mbe/000_Sheet1.csv", "d220_050_050"):
        "Думаю, он — ещё одна жертва Параллельмона,\nперенесённая сюда из другого мира.",
    ("addcont_02_text01", "message/d220.mbe/000_Sheet1.csv", "d220_050_170"):
        "«Кто настоящий Банчо?! Два мира сходятся\nв поединке один на один! Кто же победит?!»",
    ("addcont_02_text01", "message/d220.mbe/000_Sheet1.csv", "d220_070_080"):
        "Не знаю... Похоже, остаётся только\nпродолжить расследование.",
    ("addcont_02_text01", "message/d220.mbe/000_Sheet1.csv", "d220_100_040"):
        "Я хотела, чтобы мои работы увидел весь мир...\nчтобы они дошли до Инори и остальных.",
    ("addcont_02_text01", "message/d220.mbe/000_Sheet1.csv", "d220_110_110"):
        "Слушай, мне приятно, что ты мной восхищаешься,\nно ГАКУ-РАНы на деревьях не растут.",
    ("addcont_02_text01", "message/d220.mbe/000_Sheet1.csv", "d220_130_050"):
        "Мне повезло укрыться под землёй...\nно с того дня жизнь превратилась в ад.",
    ("addcont_02_text01", "message/d230.mbe/000_Sheet1.csv", "d230_020_090"):
        "Во сне я видел всё...\nв том числе ваши поединки.",
    ("addcont_02_text01", "message/d230.mbe/000_Sheet1.csv", "d230_020_230"):
        "Похоже, сила твоего желания, твоего сердца...\nпревзошла ожидания Параллельмона.",
    ("addcont_02_text01", "message/d240.mbe/000_Sheet1.csv", "d240_071_030"):
        "Стать посланником сквозь время и пространство...\nДонести мой голос до Инори и остальных.",
    ("addcont_02_text01", "message/d250.mbe/000_Sheet1.csv", "d250_030_150"):
        "Вот это будет настоящий коллаб —\nсвязь между теми, кто понимает друг друга без слов!",
    ("addcont_03_text01", "message/d310.mbe/000_Sheet1.csv", "d310_040_170"):
        "Для этого нужно вновь найти четырёх дигимонов,\nс которыми мы потерялись после переноса сюда.",
    ("addcont_03_text01", "message/d310.mbe/000_Sheet1.csv", "d310_060_090"):
        "Огромный объём данных пожирал ресурсы Цифрового мира\nс невыносимой для него скоростью.",
    ("addcont_03_text01", "message/d310.mbe/000_Sheet1.csv", "d310_060_100"):
        "А затем внезапно запустили Программу X — словно для истребления\nчрезмерно разросшейся популяции дигимонов.",
    ("addcont_03_text01", "message/d310.mbe/000_Sheet1.csv", "d310_060_160"):
        "Стороны уже договорились о встрече,\nно прежде нас перенесло сюда.",
    ("addcont_03_text01", "message/d310.mbe/000_Sheet1.csv", "d310_080_080"):
        "Связь естественного отбора с эволюцией —\nмысль радикальная, но не лишённая логики.",
    ("addcont_03_text01", "message/d310.mbe/000_Sheet1.csv", "d310_100_090"):
        "Похоже, они тоже считают,\nчто с Программой X нужно что-то делать...",
    ("addcont_03_text01", "message/d320.mbe/000_Sheet1.csv", "d320_020_050"):
        "«Я обязана воплотить это устройство в жизнь, иначе дигимоны —\nфазово-электронные формы жизни — станут угрозой человечеству!»",
    ("addcont_03_text01", "message/d320.mbe/000_Sheet1.csv", "d320_030_080"):
        "Из-за X-антитела решается вопрос жизни и смерти,\nпоэтому многие пытаются отнять его силой.",
    ("addcont_03_text01", "message/d320.mbe/000_Sheet1.csv", "d320_040_080"):
        "X-антитело полностью нейтрализует Программу X,\nно его действие не вечно.",
    ("addcont_03_text01", "message/d320.mbe/000_Sheet1.csv", "d320_040_110"):
        "Понятно. Значит, те дигимоны рисковали жизнью,\nпытаясь завладеть антителом.",
    ("addcont_03_text01", "message/d320.mbe/000_Sheet1.csv", "d320_050_100"):
        "«...Именно этим сейчас\nи занимается общественная безопасность».",
    ("addcont_03_text01", "message/d320.mbe/000_Sheet1.csv", "d320_060_040"):
        "«Многие люди до сих пор числятся пропавшими,\nно одно мы знаем наверняка».",
    ("addcont_03_text01", "message/d320.mbe/000_Sheet1.csv", "d320_060_050"):
        "«Каждый из них делал всё возможное,\nчтобы выполнить свою миссию».",
    ("addcont_03_text01", "message/d320.mbe/000_Sheet1.csv", "d320_070_020"):
        "«Так точно, сэр. Это враждебный дигимон,\nо котором нам пока почти ничего не известно».",
    ("addcont_03_text01", "message/d320.mbe/000_Sheet1.csv", "d320_070_040"):
        "«Понятно... Тогда нужно действовать\nкак можно скорее».",
    ("addcont_03_text01", "message/d320.mbe/000_Sheet1.csv", "d320_070_060"):
        "«Помнишь, что ты сказал мне\nв мои первые дни в общественной безопасности?»",
    ("addcont_03_text01", "message/d320.mbe/000_Sheet1.csv", "d320_070_200"):
        "Бесчисленные фрагменты пространства-времени погребены\nза пределами Акашического бэкдора.",
    ("addcont_03_text01", "message/d320.mbe/000_Sheet1.csv", "d320_070_220"):
        "Пусть эта сила и невелика, но она тянет существ обратно —\nк фрагментам пространства-времени, от которых их отрезало.",
    ("addcont_03_text01", "message/d320.mbe/000_Sheet1.csv", "d320_070_240"):
        "Можно сказать, именно так и работают\nявления, которые вы сейчас наблюдаете.",
    ("addcont_03_text01", "message/d330.mbe/000_Sheet1.csv", "d330_040_110"):
        "«Почему у вас столько таланта...\nи почему вы отказываетесь направить его на правое дело?!»",
    ("addcont_03_text01", "message/d340.mbe/000_Sheet1.csv", "d340_010_034"):
        "Ты прикрываешься этой «божественной волей»...\nа тем временем твои собратья гибнут.",
    ("addcont_03_text01", "message/d350.mbe/000_Sheet1.csv", "d350_010_050"):
        "Можешь твердить, что судьбу не победить, но...\nмы уже однажды её одолели.",
    ("addcont_03_text01", "message/d350.mbe/000_Sheet1.csv", "d350_020_160"):
        "Возможно, сейчас от этого мало пользы...\nно однажды это поможет нам воссоединиться.",
    ("patch_text01", "message/arena01.mbe/000_Sheet1.csv", "arena01_f001_020_020"):
        "Единственный, кто способен одолеть следующего противника...\nнаш могучий чемпион!",
    ("patch_text01", "message/d01.mbe/000_Sheet1.csv", "f_d0101_0040_0030"):
        "Прошу, успокойтесь, добрые дигимоны! Это...\nэ-э... мой помощник! Да, именно!",
    ("patch_text01", "message/d01.mbe/000_Sheet1.csv", "f_d0101_0110_0020"):
        "Я... я не понимаю, что произошло...\nТы говоришь, спор уже улажен?",
    ("patch_text01", "message/d06.mbe/000_Sheet1.csv", "f_d0601_0030_0010"):
        "Наверное, вас удивляет...\nчто всё обернулось именно так.",
    ("patch_text01", "message/d09.mbe/000_Sheet1.csv", "f_d0904_0520_0010"):
        "Эй, проследи, чтобы Дивермон... то есть Нептунемон...\nвернулся оттуда живым, понял?",
    ("patch_text01", "message/d11.mbe/000_Sheet1.csv", "f_d1102_0120_0115"):
        "Если дигимоны — антитела, то мы — чужеродная субстанция...\nВозможно, потому что познали законы времени?",
    ("patch_text01", "message/d12.mbe/000_Sheet1.csv", "f_d1204_0250_0010"):
        "Я пришёл сюда лишь затем, чтобы избежать несчастья, но...\nзнаешь, здесь не так уж плохо. Может, и осяду.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "banleo_001_4_reaction_char_BANCHOLEOMON"):
        "Хех. Даже в притче не хочешь видеть меня врагом. Мягкосердечность...\nно именно это мне в тебе и нравится.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "kabute_001_3_reaction_char_KABUTERIMON"):
        "Помогать друг другу... Этому я научился благодаря тебе.\nДрузья... так важны.",
    ("patch_text01", "message/h06.mbe/000_Sheet1.csv", "f_h0601_0030_0060"):
        "«Правильный» способ, уверена, не сработает.\nТак почему бы в этом мире не поступить наоборот?",
    ("patch_text01", "message/m020.mbe/000_Sheet1.csv", "m020_130_170"):
        "Но... благодаря тебе завала больше нет...\nЗначит, тебе всё-таки можно доверять.",
    ("patch_text01", "message/m040.mbe/000_Sheet1.csv", "m040_130_150"):
        "Ты вечно твердишь: «Ты хоть знаешь, сколько ей лет?»\nи «Держись подальше от моей дочери!»...",
    ("patch_text01", "message/m050.mbe/000_Sheet1.csv", "m050_010_170"):
        "А Синдзюку перед моими глазами...\nнастоящий ад. Словами не передать.",
    ("patch_text01", "message/m050.mbe/000_Sheet1.csv", "m050_030_090"):
        "Так вот в чём дело. По разным причинам мне известно то,\nчего не знает большинство гражданских.",
    ("patch_text01", "message/m050.mbe/000_Sheet1.csv", "m050_040_020"):
        "И, конечно, нельзя исключать,\nчто вы тоже переместились во времени.",
    ("patch_text01", "message/m070.mbe/000_Sheet1.csv", "m070_020_070"):
        "Поверь, она не плохой человек.\nПросто немного... эксцентричная, вот и всё.",
    ("patch_text01", "message/m150.mbe/000_Sheet1.csv", "m150_160_070"):
        "Он говорил, что они оказались втянуты в конфликт\nмежду фазово-электронными формами жизни.",
    ("patch_text01", "message/m210.mbe/000_Sheet1.csv", "m210_050_170"):
        "Я так долго носила в сердце ненависть к прошлому...\nБольше я никого не хочу ненавидеть.",
    ("patch_text01", "message/m260.mbe/000_Sheet1.csv", "m260_080_180"):
        "И всё же сама мысль покинуть это место немыслима —\nособенно сейчас.",
    ("patch_text01", "message/m300.mbe/000_Sheet1.csv", "m300_130_070"):
        "Мне весело. Надеюсь, мы и дальше сможем возвращать миру покой...\nвот так, вместе.",
    ("patch_text01", "message/m310.mbe/000_Sheet1.csv", "m310_010_080"):
        "Может, моё призвание — стать мостом между двумя видами...\nТолько я могу его исполнить.",
    ("patch_text01", "message/m310.mbe/000_Sheet1.csv", "m310_032_110"):
        "Что бы ни случилось и куда бы ни завела тебя дорога... просто...\nобязательно возвращайся. Хорошо?",
    ("patch_text01", "message/m360.mbe/000_Sheet1.csv", "m360_070_040"):
        "В тебе ещё теплится жизнь, верно?\nТогда ты мне ещё пригодишься.",
    ("patch_text01", "message/m390.mbe/000_Sheet1.csv", "m390_067_020"):
        "Я лишь запасная часть, созданная исполнить желание Хрономона...\nдеталь, которая с каждой минутой становится всё совершеннее.",
    ("patch_text01", "message/m410.mbe/000_Sheet1.csv", "m410_030_030"):
        "Если бы пришлось гадать, я бы сказала: близится финал...\nи встреча с тем, кто стоит за всем этим.",
    ("patch_text01", "message/m440.mbe/000_Sheet1.csv", "m440_070_060"):
        "Верно... Вмешательство извне разрешено...\n...лишь один раз...",
    ("patch_text01", "message/s010_179.mbe/000_Sheet1.csv", "s010_179_110"):
        "...всё это моя вина... Будь я сильнее...\nКапитан...!",
    ("patch_text01", "message/s010_179.mbe/000_Sheet1.csv", "s010_179_230"):
        "Нет, с животом всё нормально. Боль...\nгде-то выше.",
    ("patch_text01", "message/s010_179.mbe/000_Sheet1.csv", "s010_179_240"):
        "А, точно. Тогда я скоро выйду. Только...\nне сейчас.",
    ("patch_text01", "message/s050_043.mbe/000_Sheet1.csv", "s050_043_760"):
        "Погоди... Что это сейчас было? Ты отдаёшь это нам...\nбесплатно?",
    ("patch_text01", "message/s070_055.mbe/000_Sheet1.csv", "s070_055_420"):
        "Я хочу понять, что значит любить кого-то...\nчто значит влюбиться.",
    ("patch_text01", "message/s110_103.mbe/000_Sheet1.csv", "s110_103_250"):
        "Вызываю тебя на честный поединок.\nДа начнётся битва!",
    ("patch_text01", "message/t01.mbe/000_Sheet1.csv", "f_t0121_080_0030"):
        "А, наш новый чемпион. Ждём от тебя\nновых захватывающих поединков.",
}


# Player choices are shared by both protagonists. Until the optional dynamic
# Lua selector is production-ready, these lines must remain natural in either
# gender. The same rule is used for the Operator, whose gender is opposite to
# the selected protagonist.
GENDER_UPDATES: dict[tuple[str, str, str], str] = {
    ("addcont_01_text01", "message/digimon_chat_dlc01.mbe/000_Sheet1.csv", "kugul_001_1_replay"):
        "Вот бы и мне золотой меч!",
    ("addcont_01_text01", "message/digimon_chat_dlc01.mbe/000_Sheet1.csv", "omed_001_3_replay"):
        "Что бы тогда произошло?",
    ("addcont_02_text01", "message/digimon_chat_dlc02.mbe/000_Sheet1.csv", "banma_001_4_replay"):
        "Не хочется тебя беспокоить.",
    ("addcont_02_text01", "message/digimon_chat_dlc02.mbe/000_Sheet1.csv", "omem_001_4_replay"):
        "Хочу помочь.",
    ("patch_text01", "message/d02.mbe/000_Sheet1.csv", "f_d0203_0010_0174"):
        "Как хорошо, что с тобой всё в порядке.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "aigiog_001_4_replay"):
        "Хочу подарить тебе все розы.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "angew_001_4_replay"):
        "Я делаю это даже в одиночестве.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "anwi_001_4_replay"):
        "Вот бы и мне так.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "chu_001_1_replay"):
        "Не знаю.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "hiand_001_2_replay"):
        "Лучше по возможности этого избежать.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "holyan_001_3_replay"):
        "Я сделаю. Иначе нельзя!",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "holyan_001_4_replay"):
        "Вообще-то, прошу вас следовать за мной.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "kaigra_001_4_replay"):
        "Хочу помочь.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "knight_001_1_replay"):
        "Значит, попроси я тебя умереть за меня — ты бы согласился?",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "kokuw_001_2_replay"):
        "Я использую возобновляемые источники энергии.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "kyubi_001_1_replay"):
        "Мне тоже хочется быть среди них.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "lilis_001_1_replay"):
        "Хочу попробовать.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "luna_001_3_replay"):
        "От меня — ни слова.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "megi_001_3_replay"):
        "Полностью поддерживаю.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "mug_001_2_replay"):
        "В смысле, мне бы этого хотелось...",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "nep_001_3_replay"):
        "Хочу помочь.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "pen_001_2_replay"):
        "По-моему, здесь скорее холодно.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "raidora_001_3_replay"):
        "Думаю, я откажусь.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "ravebu_001_1_replay"):
        "Если бы это было возможно.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "tail_001_2_replay"):
        "Даже не представляю, как им пользоваться.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "teri_001_1_replay"):
        "По-моему, нам пора стать серьёзнее.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "tyran_001_2_replay"):
        "По-моему, они слишком короткие.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "viki_001_2_replay"):
        "По-моему, здесь скорее холодно.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "yupi_001_4_replay"):
        "Жаль, что тебе приходится это делать.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "yupira_001_2_replay"):
        "Да, похоже на то.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "zplu_001_3_replay"):
        "Даже если и есть, тебе я не скажу.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "zudo_001_2_replay"):
        "Вот бы мне такое тело, как у тебя.",
    ("patch_text01", "message/field_text.mbe/000_Sheet1.csv", "dummy_dlc020_0430"):
        "Сначала мне нужно поговорить с Хироко.",
    ("patch_text01", "message/m040.mbe/000_Sheet1.csv", "m040_110_061"):
        "Как хорошо, что с тобой всё в порядке!{next}",
    ("patch_text01", "message/m080.mbe/000_Sheet1.csv", "m080_020_101"):
        "Вы двое — аномалии класса А, так что мне нужно за вами следить.",
    ("patch_text01", "message/m120.mbe/000_Sheet1.csv", "m120_040_090"):
        "Заблудиться в фантастическом мире, встретить нереальных\nсуществ... Прямо как в истории об Алисе.",
    ("patch_text01", "message/m160.mbe/000_Sheet1.csv", "m160_010_032"):
        "Я помогу тебе вернуться к отцу.{next}",
    ("patch_text01", "message/m180.mbe/000_Sheet1.csv", "m180_040_202"):
        "Жаль, что мы не можем жить втроём как семья...{next}",
    ("patch_text01", "message/m410.mbe/000_Sheet1.csv", "m410_110_070"):
        "Но из Яйца появился не я.{next}",
    ("patch_text01", "message/rumor_npc.mbe/000_Sheet1.csv", "r_t0102_0010_0110"):
        "Мне нужно догнать остальных членов банды...",
    ("patch_text01", "message/rumor_npc.mbe/000_Sheet1.csv", "r_t0102_0010_0140"):
        "Во что бы сыграть сегодня...?",
    ("patch_text01", "message/rumor_npc.mbe/000_Sheet1.csv", "r_t0403_0010_0030"):
        "Нет значит нет!",
    ("patch_text01", "message/s010_001.mbe/000_Sheet1.csv", "s010_001_021"):
        "{next}Мне попалось твоё сообщение в ДигиЛинии.",
    ("patch_text01", "message/s010_180.mbe/000_Sheet1.csv", "s010_180_441"):
        "{next}А вот и я!",
    ("patch_text01", "message/s070_055.mbe/000_Sheet1.csv", "s070_055_090"):
        "{next}Пожалуй, да.",
    ("patch_text01", "message/s110_211.mbe/000_Sheet1.csv", "s110_211_041"):
        "{next}Не знаю наверняка.",
}


STYLE_UPDATES: dict[tuple[str, str, str], str] = {
    # Reppamon's tail/head joke was translated word for word, including the
    # English idioms "window dressing", "get it straight" and "2-in-1 deal".
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "reppa_001_0_char_REPPAMON"):
        "Эй, приятель! Ты куда смотришь?! Я здесь!\nРеппамон — это хвост!",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "reppa_001_1_replay"):
        "А разве не голова?",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "reppa_001_1_reaction_char_REPPAMON"):
        "Нет! Это я рублю и рассекаю!\nА голова — так, бесхребетная декорация!",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "reppa_001_2_replay"):
        "А хвост разве не просто клинок?",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "reppa_001_2_reaction_char_REPPAMON"):
        "«Просто клинок»?! Да это я и есть — Реппамон!\nЗаруби себе на носу!",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "reppa_001_3_replay"):
        "Мне всё равно. Для меня вы одно целое.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "reppa_001_3_reaction_char_REPPAMON"):
        "Смотри: я — хвост, а тело с головой болтаются на мне,\nсловно... хвост. Теперь ясно?",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "reppa_001_4_replay"):
        "Но вы же оба — Реппамон. Два в одном.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "reppa_001_4_reaction_char_REPPAMON"):
        "Будь моя воля, я бы просто отсёк вторую половину.\nНо ладно, считай как хочешь.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "Seire_001_1_replay"):
        "И то и другое — так себе...",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "vulca_001_1_reaction_char_VULCANUSMON"):
        "Даже моих рук не всегда хватает для по-настоящему хорошей работы.\nНо мне грех жаловаться — пора пустить их в дело.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "zplu_001_2_reaction_char_UNDEADPLUTOMON"):
        "У твоих друзей, похоже, славные ДигиЯдра...\nНо, пожалуй, зря я спрашиваю об этом человека.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "fuga_001_2_reaction_char_FUGAMON"):
        "Тебе до меня далеко. Людям нужны человеческие тренировки.\nПонимаешь? Вот и подумай.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "fuga_001_3_reaction_char_FUGAMON"):
        "По тебе не скажешь. Хотя с моим накачанным телом\nвообще мало кого сравнишь.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "hyoga_001_1_reaction_char_HYOUGAMON"):
        "Может, устроим небольшую потасовку?\nМой Снежный Удар неслабо припекает!",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "hoe_001_1_reaction_char_WHAMON"):
        "А, понятно! Если съем что-то не то, можно хорошенько\nглотнуть воды и всё это вымыть, да?",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "megas_001_1_reaction_char_MEGASEADRAMON"):
        "Ты... понимаешь. Клинок сильный! Клинок КРУТОЙ!",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "megas_001_2_reaction_char_MEGASEADRAMON"):
        "Ухаживать... за ним? Я об этом не думать... Я... научусь.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "bab_001_1_reaction_char_BUBBMON"):
        "Раз так думаешь — поднимай кулаки! Гугу!\nНу, держись! Гага!",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "tent_001_0_char_TENTOMON"):
        "Старый добрый Сол сегодня жарит как надо! Вот это благодать!",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "tent_001_1_replay"):
        "Пора сиять во всю силу!",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "tent_001_1_reaction_char_TENTOMON"):
        "Рвёшься в путь, да? Твой запал и меня захватил!",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "tent_001_2_replay"):
        "Сол? А кто такой Сол?",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "tent_001_2_reaction_char_TENTOMON"):
        "Да солнце же, приятель! Хе-хе.\nКупол у меня не только для красоты!",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "tent_001_3_reaction_char_TENTOMON"):
        "Ага... *Зевает* Может, в следующий раз устроим сиесту?",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "tent_001_4_reaction_char_TENTOMON"):
        "Не, со мной всё хорошо. Но спасибо за заботу, приятель.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "toge_001_4_reaction_char_TOGEMON"):
        "Ай, улыбка всё-таки вырвалась! Значит, мне засчитано поражение...\nВпрочем, так проиграть совсем не обидно. Вот уж правда!",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "jure_001_2_replay"):
        "Но умеренная вырубка леса всё же необходима.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "rose_001_4_reaction_char_ROSEMON"):
        "Твои чувства я принимаю. Но знай: моё очарование\nнавеки пленит тебя целиком — и тело, и душу.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "pino_001_3_reaction_char_PINOCHIMON"):
        "Верно. Больше никогда-никогда не совру...\nУпс! Опять соврал.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "tunk_001_1_reaction_char_TANKMON"):
        "Вызов принят!.. Ха! Ага, как же!\nС какой стати мне с тобой драться?!",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "metma_001_1_reaction_char_METALMAMEMON"):
        "Моя сила — не шутка. Я ещё покажу тебе, насколько я крут!",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "poyo_001_2_reaction_char_POYOMON"):
        "Я... хороший дигимон!",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "holyan_001_1_replay"):
        "Боюсь, мне это не по силам.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "chiri_001_3_reaction_char_TYILINMON"):
        "Виновный должен раскаяться и больше никогда без необходимости\nне отнимать чужую жизнь.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "megi_001_0_char_MEGIDRAMON"):
        "Читать мне проповеди о добре — пустая трата времени.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "ikka_001_1_reaction_char_IKKAKUMON"):
        "Да, я не самый быстрый, но пухлый? Это не жир —\nпросто «Гарпунной торпеде» нужно место.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "asta_001_1_reaction_char_ASTAMON"):
        "Да, хорошая мысль. Заодно пущу в ход и тёмную энергию.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "skuba_001_4_reaction_char_SKULLBALUCHIMON"):
        "Я РАД, ЧТО МНЕ НЕ ПРИДЁТСЯ ВИДЕТЬ,\nКАК ТЫ ДРОЖИШЬ ПЕРЕД ЛИЦОМ СМЕРТИ.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "doru_001_4_reaction_char_DORUMON"):
        "Эй, друзей я не кусаю. Но если тебе очень хочется,\nмогу сделать исключение...",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "imp_001_2_reaction_char_IMPMON"):
        "Понял. Мне просто нужно относиться к тебе с уважением, да?\nТогда и ты надо мной не смейся.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "banleo_001_0_char_BANCHOLEOMON"):
        "Покажи, чего ты стоишь!\nЧто будешь делать, если я встану перед тобой как враг?!",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "belsta_001_2_reaction_char_BEELSTARMON"):
        "Никогда об этом не думала... У имени и правда могут быть\nсвои преимущества. А ты неплохо соображаешь.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "mgra_001_3_reaction_char_METALGREYMON"):
        "Правда? Ну тогда мне придётся эволюционировать\nв ещё более крутую форму!",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "mgra_001_4_reaction_char_METALGREYMON"):
        "Ах ты... Погоди. Ты надо мной смеёшься?\nСкажи уже, что на самом деле думаешь!",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "justi_001_4_reaction_char_JUSTIMON"):
        "Впервые слышу такое мнение. Но уверен: со временем\nтебе это понравится.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "volf_001_3_reaction_char_WOLFMON"):
        "Это относилось не к тебе. Но всё же нет ничего лучше,\nчем идти по праведному пути.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "gall_001_2_reaction_char_GARURUMON"):
        "Надо же, вот это наблюдательность!\nМоя главная прелесть — в моих знаниях!",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "wagall_001_0_char_WEREGARURUMON"):
        "Классные джинсы, правда?",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "ruchef_001_1_reaction_char_LUCEMON_FM"):
        "Хе-хе... А смелости тебе не занимать. Так и быть, в награду\nпозволю тебе ещё немного побыть со мной.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "jies_001_0_char_JESMON"):
        "Хочу быть полезным в общем бою. Какую роль мне взять на себя?",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "mgaob_001_3_reaction_char_MIRAGEGAOGAMON_BM"):
        "Рад это слышать. Когда закончу дела и выйду из Режима Взрыва,\nвстретимся снова.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "lilis_001_0_char_LILITHMON"):
        "Хочешь пасть вместе со мной?",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "lilis_001_1_reaction_char_LILITHMON"):
        "Ты понимаешь, что значит пасть вместе со мной?\nСначала как следует всё обдумай.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "aero_001_2_reaction_char_AEROVEEDRAMON"):
        "Эй, я тоже никогда не видел облаков вблизи.\nБыло бы интересно посмотреть, как они образуются!",
    ("addcont_01_text01", "message/d120.mbe/000_Sheet1.csv", "d120_070_070"):
        "«Может, станешь частным детективом?\nЯ познакомлю тебя с несколькими клиентами».",
    ("addcont_02_text01", "message/d210.mbe/000_Sheet1.csv", "d210_030_110"):
        "Давай объединимся — так у обоих будет шанс вернуться домой.",
    ("addcont_03_text01", "message/d310.mbe/000_Sheet1.csv", "d310_050_070"):
        "Нас с остальными четырьмя объединяет одно: в наших телах\nсодержится вещество, известное как «X-антитело».",
    ("patch_text01", "message/d02.mbe/000_Sheet1.csv", "f_d0202_0350_0030"):
        "Идиот...! Раремоны так и делают!",
    ("patch_text01", "message/d03.mbe/000_Sheet1.csv", "f_d0302_9020_0010"):
        "У всех такие мрачные лица... Знаю!\nДавайте-ка развеемся за карточной игрой!",
    ("patch_text01", "message/d05.mbe/000_Sheet1.csv", "f_d0502_0230_0010"):
        "Эй! В следующий раз никаких сбоев, ясно?!",
    ("patch_text01", "message/d06.mbe/000_Sheet1.csv", "f_d0601_0030_0040"):
        "Но что именно её изменило?.. Вот что я хочу выяснить.",
    ("patch_text01", "message/d09.mbe/000_Sheet1.csv", "f_d0902_0020_0040"):
        "Мы едва держимся лишь потому, что сражаемся вместе!\nЕсли бросим вас, тогда вы...!",
    ("patch_text01", "message/d09.mbe/000_Sheet1.csv", "f_d0904_0280_0120"):
        "Тогда оставьте это нам!",
    ("patch_text01", "message/d09.mbe/000_Sheet1.csv", "f_d0906_0010_0110"):
        "Сейчас вы оба намного сильнее меня.\nС этим справитесь только вы!",
    ("patch_text01", "message/d10.mbe/000_Sheet1.csv", "f_d1001_0120_0010"):
        "Нужен инструмент для ремонта генератора электромагнитной сети?\nДля Сироки? Вот то, что вам нужно.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "bab_001_2_reaction_char_BUBBMON"):
        "Раз так думаешь, накорми меня! Гугу!\nУгадай, чего мне хочется! Гага!",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "diana_001_3_reaction_char_DIANAMON"):
        "Вот ты как думаешь?! Да я иногда обнимаю других\nот чистого сердца!",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "fuga_001_1_reaction_char_FUGAMON"):
        "Может, помашешь костяной дубиной, как я?\nМышцами обрастёшь.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "gabu_001_4_replay"):
        "Может, приготовим что-нибудь перекусить?",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "gob_001_4_reaction_char_GOBURIMON"):
        "Раз так думаешь, тогда защищай меня.\nМы ведь друзья, правда? Правда?",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "goma_001_3_reaction_char_GOMAMON"):
        "Вот что я хотел услышать! Наловим целую гору рыбёшки!",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "hyoga_001_3_reaction_char_HYOUGAMON"):
        "Отлично. Может, тоже нарастишь лёд на плечах, как у меня?\nИз него выйдет отличное оружие.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "tyrant_001_4_replay"):
        "За это ты мне и нравишься.",
    ("patch_text01", "message/field_text.mbe/000_Sheet1.csv", "g_shop096_0030_0010"):
        "Это вам нужно?",
    ("patch_text01", "message/field_text.mbe/000_Sheet1.csv", "g_shop099_0030_0010"):
        "Это вам нужно?",
    ("patch_text01", "message/m150.mbe/000_Sheet1.csv", "m150_070_180"):
        "...мы потеряли связь с Вулканусмоном,\nкоторый напрямую управляет реактором!",
    ("patch_text01", "message/m150.mbe/000_Sheet1.csv", "m150_150_210"):
        "Именно это мы и пытались тебе сказать.",
    ("patch_text01", "message/m210.mbe/000_Sheet1.csv", "m210_030_350"):
        "В конце концов, ты всё это время поступал так ради нас...\nПравда, Эгиомон?",
    ("patch_text01", "message/m210.mbe/000_Sheet1.csv", "m210_034_120"):
        "В конце концов, ты всё это время поступал так ради нас...\nПравда, Эгиомон?",
    ("patch_text01", "message/m350.mbe/000_Sheet1.csv", "m350_010_110"):
        "Именно грядущее поражение Меркуримона приводит\nк вторжению Титанов в человеческий мир.",
    ("patch_text01", "message/m440.mbe/000_Sheet1.csv", "m440_120_220"):
        "Именно это Хрономон и планировал с самого начала —\nради этого я и появился на свет.",
    ("patch_text01", "message/s110_211.mbe/000_Sheet1.csv", "s110_211_230"):
        "Конечно, я в деле! Проигравший угощает обоих блинчиками, идёт?",
    ("patch_text01", "message/t02.mbe/000_Sheet1.csv", "f_t0203_0030_0040"):
        "Должен быть способ... Может, попросить дигимона отнести их туда?",
    ("addcont_01_text01", "message/digimon_chat_dlc01.mbe/000_Sheet1.csv", "omea_001_2_replay"):
        "Да, и ты в их числе.",
    ("addcont_03_text01", "message/digimon_chat_dlc03.mbe/000_Sheet1.csv", "alfox_001_3_reaction_char_ULFORCEVDRAMON_X"):
        "Тогда тебе должно быть понятно: обо мне можно не беспокоиться.\nПоручи мне любую задачу.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "aigiod_001_1_reaction_char_AEGIOCHUSMON_DARK"):
        "Так и знал, что ты это скажешь.\nТебя ничем не испугать, верно?",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "belsta_001_3_reaction_char_BEELSTARMON"):
        "Знаешь... И правда! Да... Именно с тобой мне по пути!",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "bui_001_1_reaction_char_V-MON"):
        "Верно. Сначала нужно стать сильнее и эволюционировать!",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "chu_001_0_char_TYUMON"):
        "Эй, тебе нравится, что мы теперь друзья?",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "gao_001_3_replay"):
        "Разве это не очевидно?",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "herac_001_1_reaction_char_HERCULESKABUTERIMON"):
        "Без сильного сердца легко поддаться трусости. Тут не поспоришь.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "hoe_001_3_reaction_char_WHAMON"):
        "Что? Пойдёшь туда ради меня?\nКакая забота... Спасибо.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "impe_001_3_reaction_char_IMPERIALDRAMON_FM"):
        "И правда, я не одинок. Что ж, если когда-нибудь потеряю себя...\nбуду рассчитывать на тебя.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "kame_001_3_reaction_char_KAMEMON"):
        "Ты правда сделаешь всё это ради такого малыша, как я?\nДаже не представляешь, как это меня радует!",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "kiwi_001_2_reaction_char_KIWIMON"):
        "Верно. Если станет страшно, придумаю тысячу способов сбежать!",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "levi_001_0_char_LEVIAMON"):
        "Моей силе можно лишь завидовать.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "lokni_001_3_replay"):
        "И правильно.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "lop_001_4_reaction_char_LOPMON"):
        "Спасибо за доверие! Держу пари, никто бы меня так не называл,\nбудь ты рядом с самого начала.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "lyla_001_4_reaction_char_LILAMON"):
        "Какая осторожность! Честно говоря, от этого даже спокойнее.\nХочу и дальше быть рядом с тобой.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "mari_001_2_reaction_char_MARINEANGEMON"):
        "Верно. Без сочувствия и понимания трудно быть вместе\nи даже просто разговаривать.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "megas_001_4_replay"):
        "Тебе тоже есть чем похвастаться!",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "monza_001_1_reaction_char_MONZAEMON"):
        "Хм... Верно. Всё начинается с разговора.\nПостараюсь набраться смелости!",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "pata_001_0_char_PATAMON"):
        "За плохой поступок нужно извиниться...\nи сделать это как следует. Верно?",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "pino_001_0_char_PINOCHIMON"):
        "Сразу предупреждаю: я немного привираю.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "ruches_001_0_char_LUCEMON_SM"):
        "Хочется запечатать меня?",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "tyran_001_2_reaction_char_TYRANNOMON"):
        "Что? Правда? Самому мне трудно судить.\nХорошо, что спросил!",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "dera_001_4_reaction_char_DELUMON"):
        "Именно. Грустные любовные сонеты, которые я каждую ночь...\nСтоп. Что за чушь я из-за тебя несу?",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "syako_001_1_reaction_char_SHAKOMON"):
        "Ага! Я такой милый, что никому и в голову не придёт,\nкак здорово я дерусь. Ты-то меня понимаешь!",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "teri_001_4_reaction_char_TERRIERMON"):
        "Для меня «слишком» — в самый раз.\nВот умеешь сделать дигимону комплимент!",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "toko_001_0_char_TOKOMON"):
        "Хочу поскорее эволюционировать\nв кого-нибудь по-настоящему сильного!",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "toko_001_3_reaction_char_TOKOMON"):
        "Правда? Тогда, может, вообще не стану эволюционировать...\nХотя нет, очень уж хочется!",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "gaoga_001_3_reaction_char_GAOGAMON"):
        "Ну вот, весь настрой сбит. Твоя взяла.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "vulca_001_3_reaction_char_VULCANUSMON"):
        "Мне нужна только дружба.\nА с восемью руками я отплачу за неё вчетверо!",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "warus_001_1_reaction_char_WARUSEADRAMON"):
        "Продолжай говорить со мной в таком духе —\nтогда я точно разойдусь на полную!",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "pata_001_4_reaction_char_PATAMON"):
        "Как это мило! Тогда так и быть, прощаю.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "sola_001_1_replay"):
        "От тебя прямо жаром пышет, да?",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "devi_001_4_reaction_char_DEVIMON"):
        "Меня ей не обмануть, но любовь и правда не стоит недооценивать...",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "megi_001_1_reaction_char_MEGIDRAMON"):
        "Ничего это не изменит, но забавные же вещи ты говоришь.\nЗа смелость хотя бы похвалю.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "mgra_001_2_reaction_char_METALGREYMON"):
        "Я-то надеялся, что выберешь меня,\nно ты всё равно молодец, правда?",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "ruchef_001_3_reaction_char_LUCEMON_FM"):
        "Мне не нужны друзья. И всё же с тобой интересно.\nПожалуй, могу уделить тебе немного времени.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "skuba_001_1_replay"):
        "Трудно сказать.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "ikka_001_0_char_IKKAKUMON"):
        "Слушай, неужели я и правда такой пухлый?",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "exbui_001_2_replay"):
        "А по-моему, ты и так крут.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "pen_001_4_reaction_char_PENMON"):
        "А по тебе и не скажешь.\nПойдём лучше вместе окунёмся в ледяную воду!",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "dukec_001_1_replay"):
        "А выглядишь ты и правда сильным.",
    ("addcont_01_text01", "message/digimon_chat_dlc01.mbe/000_Sheet1.csv", "omea_001_1_replay"):
        "Именно.",
    ("addcont_01_text01", "message/digimon_chat_dlc01.mbe/000_Sheet1.csv", "omea_001_4_reaction_char_OMEGAMON_ALTER-S"):
        "Противостояние добра и зла устроено просто.\nЕсли это твоя цель, я не возражаю.",
    ("addcont_02_text01", "message/digimon_chat_dlc02.mbe/000_Sheet1.csv", "bango_001_3_replay"):
        "Похоже, мне не хватает силы воли.",
    ("addcont_02_text01", "message/digimon_chat_dlc02.mbe/000_Sheet1.csv", "omem_001_2_replay"):
        "Безжалостно, не находишь?",
    ("addcont_03_text01", "message/digimon_chat_dlc03.mbe/000_Sheet1.csv", "alfox_001_1_replay"):
        "Самоуверенности тебе не занимать, да?",
    ("addcont_17_text01", "message/digimon_chat_dlc17.mbe/000_Sheet1.csv", "omez_001_1_replay"):
        "Выглядит, прямо скажем, по-злодейски.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "aigiob_001_2_replay"):
        "Нет, но звучит интересно.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "aigiog_001_0_char_AEGIOCHUSMON_GREEN"):
        "Недавно я увидела сад, полный роз.\nКрасота была невероятная.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "aigiog_001_1_reaction_char_AEGIOCHUSMON_GREEN"):
        "Ха-ха! Как мои? Верно, шипы у меня очень колючие!",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "aigiou_001_1_reaction_char_AEGIOCHUSMON"):
        "Вот это храбрость! Мне есть чему у тебя поучиться.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "bacc_001_1_reaction_char_BACCHUSMON"):
        "От аромата вина из таких плодов я уже пьянею...\nА ещё от вина становлюсь щедрее!",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "bear_001_1_reaction_char_BEARMON"):
        "Но это же тренировка! Ты ко всему подходишь серьёзно, да?",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "clock_001_2_reaction_char_CLOCKMON"):
        "У тебя всё схвачено. Люблю людей, которые ценят своё время.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "duftrm_001_4_replay"):
        "Самоуверенности тебе не занимать, да?",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "fly_001_4_reaction_char_FLYMON"):
        "Милый?.. Вот уж неожиданность. Но... пожалуй, не неприятная.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "gawa_001_4_replay"):
        "Музыка для тебя — всё, да?",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "gob_001_4_replay"):
        "Скорее уж слабоват.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "hawk_001_2_reaction_char_HAWKMON"):
        "Верно: узнай мы причину, наверняка смогли бы помочь.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "horus_001_3_reaction_char_HOLSMON"):
        "С тобой было бы весело полетать, но сейчас не до игр.\nКак-нибудь в другой раз.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "ikka_001_1_replay"):
        "Да, ты пухловат.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "kuda_001_1_replay"):
        "Наверняка ты тяжёлый.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "lili_001_3_reaction_char_LILLYMON"):
        "Надо же! Как хорошо ты меня понимаешь!",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "loco_001_2_reaction_char_LOCOMON"):
        "С людьми на борту я предельно осторожен.\nДыма лишнего не напускаю.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "magul_001_4_replay"):
        "Наверняка очень ярко светится.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "mame_001_4_reaction_char_MAMEMON"):
        "Т-ты правда так думаешь? Хе-хе!",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "mari_001_3_reaction_char_MARINEANGEMON"):
        "Когда рядом есть тот, на кого можно положиться, мне спокойно.\nДавай держаться вместе!",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "mel_001_1_reaction_char_MERCURYMON"):
        "Человеку не следует об этом шутить. Какая безрассудность.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "mochi_001_4_reaction_char_MOCHIMON"):
        "Ничего подобного. Вообще-то ощущения приятные.\nДавай как-нибудь надуемся вместе!",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "mucho_001_2_reaction_char_MUCHOMON"):
        "Цвет у него странный. Мне пробовать не доводилось,\nно вкус всегда интересовал.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "paid_001_1_replay"):
        "Когти выглядят острыми.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "pata_001_2_reaction_char_PATAMON"):
        "Нет!.. Ну ладно, кое о чём я всё же жалею.\nСпасибо, теперь это стало понятно.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "pega_001_2_replay"):
        "Неужели будет так больно?",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "poyo_001_2_replay"):
        "У тебя отлично получается.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "pro_001_2_reaction_char_PLOTMON"):
        "Люди часто так говорят. Очень интересно, какие они на самом деле!",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "raidora_001_3_reaction_char_LIGHDRAMON"):
        "Но мчаться по земле — одно удовольствие.\nЖаль, не могу тебя прокатить.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "rapi_001_2_reaction_char_RAPIDMON"):
        "«Рапид» значит «стремительный», а не «кролик»!\nРазница огромная, приятель!",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "rigra_001_1_reaction_char_RIZEGREYMON"):
        "Я и так силён, но хочется узнать,\nнасколько сильнее смогу стать.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "rigra_001_1_replay"):
        "Похоже, ты станешь невероятно сильным.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "shaw_001_2_reaction_char_SHAWUJINMON"):
        "О! Мы можем своими руками снова очистить реки? Отличная идея.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "syako_001_3_reaction_char_SHAKOMON"):
        "Да? Так и думал! Отличный у меня панцирь.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "sylphy_001_3_reaction_char_SILPHYMON"):
        "Крылья сразу бросаются в глаза, да? С ними я свободно парю\nи мягко приземляюсь рядом с тобой.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "toge_001_2_reaction_char_TOGEMON"):
        "Звучит... вообще-то разумно. Вот так?",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "tono_001_3_replay"):
        "Ну, ты и правда спал с открытым ртом...",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "venus_001_4_replay"):
        "Ты правда меня видишь?",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "wogra_001_2_reaction_char_WARGREYMON"):
        "О, отличная идея. Если всё получится, никто не пострадает.",
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "yupira_001_4_replay"):
        "А ты, оказывается, спокоен.",
    ("patch_text01", "message/rumor_npc.mbe/000_Sheet1.csv", "r_d0204_0010_0030"):
        "Ну всё, напросились!",
    # The Terriermon Assistant block came from the same literal, sentence-by-
    # sentence pass as the broken DLC lines above.  It also addressed the
    # player in the masculine in one branch, so keep the wording neutral.
    ("patch_text01", "message/d02.mbe/000_Sheet1.csv", "f_d0203_0010_0087"):
        "Кон-Бэджи-Гу! Я Терьермон-ассистент.",
    ("patch_text01", "message/d02.mbe/000_Sheet1.csv", "f_d0203_0010_0089"):
        "Терьермон-ассистент весело говорит по телевизору.",
    ("patch_text01", "message/d02.mbe/000_Sheet1.csv", "f_d0203_0010_0090"):
        "Кон-Бэджи-Гу! Я Терьермон-ассистент.",
    ("patch_text01", "message/d02.mbe/000_Sheet1.csv", "f_d0203_0010_0100"):
        "В этом городе полно дигимонов — лучше места\nдля моих исследований не найти.",
    ("patch_text01", "message/d02.mbe/000_Sheet1.csv", "f_d0203_0010_0110"):
        "Кстати... Ты ведь человек? Что привело тебя сюда?",
    ("patch_text01", "message/d02.mbe/000_Sheet1.csv", "f_d0203_0010_0120"):
        "Наверняка у тебя есть причины. Внешность обманчива:\nв исследованиях я знаю толк, так что всё понимаю.",
    ("patch_text01", "message/d02.mbe/000_Sheet1.csv", "f_d0203_0010_0130"):
        "Вот, возьми. Это один из плодов моих исследований.",
    ("patch_text01", "message/d02.mbe/000_Sheet1.csv", "f_d0203_0010_0140"):
        "Дигимоны всегда меня интересовали,\nно и люди по-своему удивительны.",
    ("patch_text01", "message/d02.mbe/000_Sheet1.csv", "f_d0203_0010_0150"):
        "Сразу видно: у тебя важная цель...",
    ("patch_text01", "message/d02.mbe/000_Sheet1.csv", "f_d0203_0010_0160"):
        "Пусть каждый сделает всё ради своей цели!\nЯ в тебя верю!",
    ("patch_text01", "message/d02.mbe/000_Sheet1.csv", "f_d0203_0010_0180"):
        "Классный значок, правда?\nОсобый подарок от моего наставника.",
    ("patch_text01", "message/d02.mbe/000_Sheet1.csv", "f_d0203_0010_0190"):
        "Я могу увеличить его и метнуть!\nЭтот особый приём называется «Дай-Бэджи-Гу»!",
    ("patch_text01", "message/d02.mbe/000_Sheet1.csv", "f_d0203_0010_0200"):
        "Правда, сам значок не возвращается,\nи потом приходится за ним ходить...",
    ("patch_text01", "message/d02.mbe/000_Sheet1.csv", "f_d0203_0010_0210"):
        "Ух...",
    ("patch_text01", "message/d02.mbe/000_Sheet1.csv", "f_d0203_0010_0220"):
        "Мясо здесь такое вкусное, что я постоянно объедаюсь.",
    ("patch_text01", "message/d02.mbe/000_Sheet1.csv", "f_d0203_0010_0223"):
        "Эй, я здесь не только ради еды!",
    ("patch_text01", "message/d02.mbe/000_Sheet1.csv", "f_d0203_0010_0225"):
        "Нельзя бросать исследования дигимонов... Ух...",
    ("patch_text01", "message/d02.mbe/000_Sheet1.csv", "f_d0203_0010_0227"):
        "Ух...",
    ("patch_text01", "message/d02.mbe/000_Sheet1.csv", "f_d0203_0010_0229"):
        "Так, посмотрим... Вот, например...",
    ("patch_text01", "message/d02.mbe/000_Sheet1.csv", "f_d0203_0010_0230"):
        "Дигимоны и их способность к эволюции\nвсё ещё полны загадок.",
    ("patch_text01", "message/d02.mbe/000_Sheet1.csv", "f_d0203_0010_0235"):
        "Неужели тебе не интересно,\nво что эволюционирует твой дигимон?",
    ("patch_text01", "message/d02.mbe/000_Sheet1.csv", "f_d0203_0010_0240"):
        "Интересно, во что когда-нибудь эволюционирую я?\nНаверное, в Гальгомона.",
    ("patch_text01", "message/d02.mbe/000_Sheet1.csv", "f_d0203_0010_0250"):
        "Хотя с такой милой внешностью и тягой к знаниям\nиз меня может выйти кто-нибудь необычный.",
    ("patch_text01", "message/d02.mbe/000_Sheet1.csv", "f_d0203_0010_0260"):
        "Значит, моя мега-форма будет... Хе-хе-хе...",
    ("patch_text01", "message/d02.mbe/000_Sheet1.csv", "f_d0203_0010_0270"):
        "Мой дом очень-очень далеко отсюда.",
    ("patch_text01", "message/d02.mbe/000_Sheet1.csv", "f_d0203_0010_0280"):
        "Но исследования дигимонов так меня увлекли,\nчто дорога сюда пролетела незаметно.",
    ("patch_text01", "message/d02.mbe/000_Sheet1.csv", "f_d0203_0010_0290"):
        "Интересно, как там дома Терьермон и Лопмон...",
    ("patch_text01", "message/d02.mbe/000_Sheet1.csv", "f_d0203_0010_0300"):
        "Кстати... Отличный был бой\nс теми Титанами!",
    ("patch_text01", "message/d02.mbe/000_Sheet1.csv", "f_d0203_0010_0310"):
        "Спасибо тебе. Теперь я могу\nпродолжить исследования дигимонов.",
    ("patch_text01", "message/d02.mbe/000_Sheet1.csv", "f_d0203_0010_0320"):
        "Пусть сейчас всем нелегко, я сосредоточусь\nна исследованиях и постараюсь помочь.",
    ("patch_text01", "message/d02.mbe/000_Sheet1.csv", "f_d0203_0010_0330"):
        "Это тебе. Давай и дальше стараться!",
    ("patch_text01", "message/d02.mbe/000_Sheet1.csv", "f_d0203_0010_0340"):
        "Глядя на тебя, я убедился: люди и дигимоны могут жить в мире.\nНадеюсь, однажды мне удастся стать мостом между ними.",
    ("patch_text01", "message/d02.mbe/000_Sheet1.csv", "f_d0203_0010_0350"):
        "Как бы ни закончилась эта битва\nи что бы ни ждало нас впереди...",
    ("patch_text01", "message/d02.mbe/000_Sheet1.csv", "f_d0203_0010_0360"):
        "...я не откажусь от своей мечты.\nВот увидишь — она станет явью!",
    ("patch_text01", "message/d02.mbe/000_Sheet1.csv", "f_d0203_0010_0370"):
        "...",
    ("patch_text01", "message/d02.mbe/000_Sheet1.csv", "f_d0203_0010_0380"):
        "Хе-хе-хе... Стоило произнести это вслух — и стало неловко.\nНо я обещаю сделать всё, что в моих силах!",
    ("patch_text01", "message/d07.mbe/000_Sheet1.csv", "f_d0703_0060_0010"):
        "Я всегда считал рассказы Уайземона затянутыми, но\nон так здорово рассказывает, что я ловлю каждое слово.",
    ("patch_text01", "message/s030_031.mbe/000_Sheet1.csv", "s030_031_540"):
        "Мне почти нечем тебя отблагодарить... но, пожалуйста,\nвозьми этот спелый плод Карпос Хуле.",
    ("patch_text01", "message/m140.mbe/000_Sheet1.csv", "m140_020_080"):
        "Существование Цифрового мира, возможно, поможет\nобъяснить подобные явления.",
    ("patch_text01", "message/m285.mbe/000_Sheet1.csv", "m285_040_030"):
        "Что до нашего прошлого разговора... в АДАМАС\nпришли к единому мнению.",
}


# The common Digimon Chat templates are duplicated for voice/age/personality
# variants.  Prefix updates keep each complete block in sync instead of fixing
# one of sixteen visually identical copies.  The expected count guards against
# silently applying a rewrite to a changed game build.
PREFIX_STYLE_UPDATES: dict[tuple[str, str, str], tuple[str, int]] = {
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "common004_1_reaction_"):
        ("Серьёзно? Отлично. Тогда пора как следует подкачаться!", 16),
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "common005_0_"):
        ("Что даёт ум?", 16),
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "common005_2_reaction_"):
        ("Ого, умным быть непросто. Может, мне тогда и не нужно умнеть!", 16),
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "common006_1_reaction_"):
        ("Спасибо, ты очень поможешь!\nВместе мы во всём разберёмся!", 16),
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "common008_1_reaction_"):
        ("Спасибо, ты очень поможешь!\nВместе мы во всём разберёмся!", 16),
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "common010_0_"):
        ("Кто такие друзья? С ними лучше?", 16),
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "common013_1_reaction_"):
        ("О! Значит, любовь — это тепло!", 16),
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "common015_1_reaction_"):
        ("Хорошо... Теперь у меня так тепло на душе!", 16),
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "common019_1_replay"):
        ("Это хорошо.", 1),
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "common023_2_replay"):
        ("У меня тоже.", 1),
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "common049_1_replay"):
        ("Это обнадёживает!", 1),
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "common052_0_"):
        ("Хочу снова почувствовать бодрость!", 16),
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "common052_1_reaction_"):
        ("Эх, сразу вспомнилась бесшабашная молодость!\nХо-хо-хо... Вперёд!", 16),
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "common053_0_"):
        ("Я многое знаю. Как думаешь, мои знания тебе пригодятся?", 16),
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "common053_1_replay"):
        ("Знания — тоже оружие!", 1),
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "common054_0_"):
        ("Не хочешь послушать мои рассказы о былых временах?", 16),
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "common054_2_replay"):
        ("Извини, старые истории мне неинтересны.", 1),
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "common055_0_"):
        ("За долгую жизнь я кое в чём поднаторел.", 16),
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "common055_1_reaction_"):
        ("Теперь придётся отвечать за свои слова.\nПостараюсь помочь тебе знаниями.", 16),
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "common055_2_reaction_"):
        ("Да, наверное, это звучит как ворчание старого дурака...", 16),
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "common059_0_"):
        ("Дружбе возраст не помеха.", 16),
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "common060_1_reaction_"):
        ("Безусловно, говоришь? Хо-хо-хо! Я тоже так думаю.", 16),
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "common060_2_reaction_"):
        ("Возможно, чтобы стать друзьями, достаточно обоюдного желания.", 16),
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "common061_0_"):
        ("В моём возрасте я могу выразить привязанность лишь так:\nотвлечь врага в трудную минуту.", 16),
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "common061_1_reaction_"):
        ("Значит, будешь по мне горевать? Выходит, даже этим старым\nкостям досталось немного любви.", 16),
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "common061_2_reaction_"):
        ("Я и так прожил долгую жизнь.\nХочу лишь передать надежду молодым.", 16),
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "common063_0_"):
        ("*Пыхтит* *Хрипит*... Я просто... немного без сил.", 16),
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "common063_2_reaction_"):
        ("*Пыхтит* *Хрипит*... Так со старшими не обращаются...", 16),
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "digimon_chat_ps_0"):
        ("Может, мне освоить новый Личностный Навык?", 4),
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "common001_1_reaction_"):
        ("Хе-хе, так и есть! Смелость — это здорово. Хочу ещё!", 16),
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "common004_2_reaction_"):
        ("Да, перенапрягаться ни к чему. Лучше оставаться собой!", 16),
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "common009_1_reaction_"):
        ("Наверное, я слишком всё усложняю.\nГлавное, что рядом мой друг... ты!", 16),
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "common010_1_reaction_"):
        ("Так вот что значит дружба! Хе-хе!\nКак же здорово, что ты у меня есть!", 16),
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "common011_1_reaction_"):
        ("Хе-хе! Вот это счастье! Давай навсегда останемся друзьями!", 16),
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "common011_2_reaction_"):
        ("Что?! Откуда такие сомнения?! Как жестоко!", 16),
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "common012_2_reaction_"):
        ("Хм. Раз ты так говоришь, возможно, мне и правда показалось...", 16),
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "common014_2_reaction_"):
        ("Ого, тебе столько всего хочется?\nНе знаю, смогу ли всё это достать...", 16),
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "common016_0_"):
        ("Есть так хочется...", 16),
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "common018_0_"):
        ("Если набраться храбрости, можно преодолеть что угодно!", 16),
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "common018_1_reaction_"):
        ("Вот именно! До конца не отступим!", 16),
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "common020_0_"):
        ("По правде говоря... Мне нужно кое за что извиниться.", 16),
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "common020_2_reaction_"):
        ("Так вот... Твои закуски исчезли из-за меня... П-прости.\nСкоро я принесу ещё!", 16),
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "common021_0_"):
        ("Некоторые люди одержимы знаниями.\nКак думаешь, дигимонам тоже стоит к этому стремиться?", 16),
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "common021_1_reaction_"):
        ("Понятно. Значит, чем больше знаешь, тем больше можешь?\nПожалуй, возьму с людей пример!", 16),
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "common021_2_reaction_"):
        ("То есть сила и мастерство важнее ума? Ясно!", 16),
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "common022_1_reaction_"):
        ("В бою нужно думать головой. Хорошо, что мы согласны!", 16),
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "common022_2_reaction_"):
        ("То есть можно просто всё решать грубой силой?\nЧто ж, зато думать меньше, да?", 16),
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "common024_1_reaction_"):
        ("О, понятно... Хм. Спасибо, буду иметь в виду.", 16),
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "common024_2_reaction_"):
        ("Хм, значит, мне не нужно так напрягаться. Какое облегчение.", 16),
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "common025_1_replay"):
        ("Кто-то незаменимый.", 1),
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "common026_1_replay"):
        ("Да. Это чувство сделает тебя сильнее.", 1),
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "common027_0_"):
        ("Просто интересно: тебе было бы грустно, если бы меня не стало?", 16),
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "common027_1_reaction_"):
        ("Ха-ха! Ясно. Мне тоже было бы грустно,\nесли бы тебя не стало.", 16),
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "common027_2_reaction_"):
        ("Поэтому и говорю «если». Просто хотелось проверить. Вот и всё.", 16),
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "common028_2_replay"):
        ("По-моему, тебе это только кажется.", 1),
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "common029_1_reaction_"):
        ("Значит, ты тоже так думаешь?\nВ последнее время мне всё яснее, как важна любовь.", 16),
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "common030_1_reaction_"):
        ("Иногда чувства придают дополнительных сил, да?\nТогда я открою сердце любви!", 16),
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "common030_2_reaction_"):
        ("Значит, всё решают мощь и мастерство? Понятно.", 16),
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "common032_0_"):
        ("Фух... Нужна передышка. Может, отдохнём?", 16),
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "common032_2_reaction_"):
        ("Нет. Просто показалось, что тебе тоже нужен отдых.", 16),
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "common033_1_reaction_"):
        ("Вот почему тобой можно восхищаться!\nМужество — прекрасное качество.", 16),
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "common034_0_"):
        ("*Всхлип* Прости, что плачу. У меня не получился приём...\nМожет, мне это не по силам.", 16),
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "common034_1_reaction_"):
        ("...Да. Если сейчас сдаться, все усилия пропадут зря.\nНужно продолжать попытки!", 16),
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "common034_2_replay"):
        ("Тогда просто сдавайся уже.", 1),
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "common034_2_reaction_"):
        ("*Всхлип*... Ладно. Может, оно и к лучшему.", 16),
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "common036_1_reaction_"):
        ("О... Вот это сила. Мне бы такую уверенность.", 16),
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "common039_2_reaction_"):
        ("Хи-хи. Верно. Жаль только, что сказать легче, чем сделать.", 16),
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "common045_2_reaction_"):
        ("Понятно. Значит, сила важнее всего.", 16),
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "common050_2_reaction_"):
        ("Верно. Смелость — ещё не всё.\nПожалуй, стоит пересмотреть свои взгляды.", 16),
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "common051_1_replay"):
        ("Возраст — не помеха!", 1),
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "common053_2_reaction_"):
        ("Хм, значит, одних знаний мало?\nПохоже, придётся тренировать и тело...", 16),
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "common012_0_"):
        ("Не знаю почему, но рядом с тобой мне становится спокойнее.", 16),
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "common015_2_reaction_"):
        ("Ладно, попробую... Но такие вещи меня ужасно пугают.", 16),
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "common025_2_replay"):
        ("Честно говоря, не знаю.", 1),
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "common038_0_"):
        ("Каждая новая встреча напоминает мне,\nкак мало я знаю об этом мире.", 16),
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "common040_0_"):
        ("Я часто вижу, как люди читают книги.\nНеужели книги и правда настолько интересные?", 16),
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "common040_1_reaction_"):
        ("Хм, значит, от них и правда не оторваться?\nМожет, мне тоже немного почитать.", 16),
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "common057_2_reaction_"):
        ("Выходит, из-за разницы в возрасте и правда бывает трудно подружиться.", 16),
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "common007_2_reaction_"):
        ("Ого, похоже, много знать — это непросто.\nМожет, тогда мне и не обязательно всё знать!", 16),
}


def read_rows(path: Path) -> list[list[str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.reader(handle))


def write_rows(path: Path, rows: list[list[str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        csv.writer(handle, lineterminator="\n").writerows(rows)


def main() -> None:
    updates = {**STRUCTURE_UPDATES, **GENDER_UPDATES, **STYLE_UPDATES}
    expected_count = len(STRUCTURE_UPDATES) + len(GENDER_UPDATES) + len(STYLE_UPDATES)
    if len(updates) != expected_count:
        raise RuntimeError("Duplicate update keys across v064 update groups")

    by_file: dict[tuple[str, str], dict[str, str]] = defaultdict(dict)
    for (package, relative_file, row_id), text in updates.items():
        by_file[(package, relative_file)][row_id] = text

    prefix_by_file: dict[tuple[str, str], dict[str, tuple[str, int]]] = defaultdict(dict)
    for (package, relative_file, prefix), value in PREFIX_STYLE_UPDATES.items():
        prefix_by_file[(package, relative_file)][prefix] = value

    changed: list[str] = []
    unchanged: list[str] = []
    missing: list[str] = []
    file_keys = sorted(set(by_file) | set(prefix_by_file))
    for package, relative_file in file_keys:
        file_updates = by_file.get((package, relative_file), {})
        prefix_updates = prefix_by_file.get((package, relative_file), {})
        path = CSV_ROOT / package / relative_file
        if not path.exists():
            missing.extend(f"{package}/{relative_file}:{row_id}" for row_id in file_updates)
            missing.extend(f"{package}/{relative_file}:{prefix}*" for prefix in prefix_updates)
            continue

        rows = read_rows(path)
        found: set[str] = set()
        prefix_found: dict[str, int] = defaultdict(int)
        file_changed = False
        for row in rows[1:]:
            if len(row) < 3:
                continue
            row_id = row[0]
            new_text: str | None = None
            if row_id in file_updates:
                found.add(row_id)
                new_text = file_updates[row_id]

            matching_prefixes = [prefix for prefix in prefix_updates if row_id.startswith(prefix)]
            if len(matching_prefixes) > 1:
                raise RuntimeError(f"Overlapping prefix updates for {row_id}: {matching_prefixes}")
            if matching_prefixes:
                prefix = matching_prefixes[0]
                prefix_found[prefix] += 1
                prefix_text, _ = prefix_updates[prefix]
                if new_text is not None and new_text != prefix_text:
                    raise RuntimeError(f"Conflicting ID/prefix updates for {row_id}")
                new_text = prefix_text

            if new_text is not None:
                marker = f"{package}/{relative_file}:{row_id}"
                if row[2] == new_text:
                    unchanged.append(marker)
                else:
                    row[2] = new_text
                    changed.append(marker)
                    file_changed = True

        missing.extend(
            f"{package}/{relative_file}:{row_id}"
            for row_id in sorted(set(file_updates) - found)
        )
        for prefix, (_, expected) in prefix_updates.items():
            actual = prefix_found[prefix]
            if actual != expected:
                missing.append(
                    f"{package}/{relative_file}:{prefix}* expected={expected} actual={actual}"
                )
        if file_changed:
            write_rows(path, rows)

    if missing:
        raise RuntimeError("Missing target rows:\n" + "\n".join(missing))

    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    LOG_PATH.write_text(
        "Changed rows:\n"
        + "\n".join(changed)
        + "\n\nAlready current:\n"
        + "\n".join(unchanged)
        + "\n",
        encoding="utf-8",
    )
    print(f"Changed rows: {len(changed)}")
    print(f"Already current: {len(unchanged)}")
    print(f"Total targets: {len(updates) + sum(value[1] for value in PREFIX_STYLE_UPDATES.values())}")


if __name__ == "__main__":
    main()

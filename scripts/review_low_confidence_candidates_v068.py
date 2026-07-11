#!/usr/bin/env python3
"""Review the 583 low/medium-confidence gender and style candidates.

The script is intentionally fail-closed and tied to the v067 audit.  It:

* classifies every candidate;
* adds M/F runtime variants only for NPC lines that address the selectable
  protagonist;
* keeps fixed-character gender forms out of the runtime resolver;
* applies only manually confirmed fixed-gender and mechanical-style rewrites;
* writes a row-by-row review report for later re-audits.
"""

from __future__ import annotations

import csv
import re
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "exports" / "dialogue_gender_style_audit_v067.csv"
REVIEW = ROOT / "exports" / "dialogue_gender_style_review_v068.csv"
DATASET = ROOT / "exports" / "dynamic_gender_confirmed_variants_v066.csv"
CSV_ROOT = ROOT / "csv"


# Positions in the frozen 201-row v067 gender review that are not grammar
# addressed to the selectable protagonist.  Context was checked in the
# surrounding scene: these are fixed characters, ambient conversations, or
# the protagonist speaking to somebody else.
NON_PLAYER_ADDRESS_POSITIONS = {
    *range(1, 10), 14, *range(17, 24), 25, 26, 29, 34, *range(36, 39), 40, 50, 52, 53, 69,
    92, 93, 97, 99, 100, 101, *range(103, 113), 114, 115, 117, 119, 120,
    *range(122, 130), *range(131, 135), 137, 138, 140, 141, 143, 145, 156,
    165, 169, 174, *range(177, 180), 181, *range(185, 188), 190, 193, 195, 196, 201,
}

# This line is clearer and fully gender-neutral after manual rewriting, so it
# does not need two runtime rows.
NEUTRALIZED_PLAYER_ADDRESS = {
    "f_d0502_0110_0020",
    "g_degi_h0211_0020",
    "m070_060_040",
    "s050_038_0030",
    "s050_038_0120",
    "s050_038_0200",
    "s050_042_0270",
    "s050_042_0280",
    "s200_148_390",
}


FORM_PAIRS = (
    ("готов", "готова"),
    ("был", "была"),
    ("вернулся", "вернулась"),
    ("ранен", "ранена"),
    ("должен", "должна"),
    ("уверен", "уверена"),
    ("смог", "смогла"),
    ("сделал", "сделала"),
    ("знал", "знала"),
    ("один", "одна"),
    ("пришел", "пришла"),
    ("пришёл", "пришла"),
    ("думал", "думала"),
    ("прав", "права"),
    ("нашёл", "нашла"),
    ("нашел", "нашла"),
    ("жив", "жива"),
    ("рад", "рада"),
    ("попал", "попала"),
    ("устал", "устала"),
    ("хотел", "хотела"),
    ("решил", "решила"),
    ("видел", "видела"),
    ("сказал", "сказала"),
    ("родился", "родилась"),
    ("способен", "способна"),
    ("единственным", "единственной"),
    ("единственный", "единственная"),
    ("хорош", "хороша"),
    ("занят", "занята"),
    ("понял", "поняла"),
    ("принёс", "принесла"),
    ("принес", "принесла"),
    ("бывал", "бывала"),
    ("знаменит", "знаменита"),
    ("забыл", "забыла"),
    ("показал", "показала"),
)


def preserve_case(source: str, replacement: str) -> str:
    if source.isupper():
        return replacement.upper()
    if source[:1].isupper():
        return replacement[:1].upper() + replacement[1:]
    return replacement


def replace_form(text: str, source: str, replacement: str) -> str:
    pattern = re.compile(rf"(?<![\w-]){re.escape(source)}(?![\w-])", re.IGNORECASE)
    return pattern.sub(lambda match: preserve_case(match.group(0), replacement), text)


def generic_variants(text: str) -> tuple[str, str]:
    male = text
    # Normalize the handful of source rows currently written for a heroine.
    female_to_male: dict[str, str] = {}
    for masculine, feminine in FORM_PAIRS:
        female_to_male.setdefault(feminine, masculine)
    for feminine, masculine in sorted(female_to_male.items(), key=lambda item: -len(item[0])):
        male = replace_form(male, feminine, masculine)

    female = male
    for masculine, feminine in sorted(FORM_PAIRS, key=lambda item: -len(item[0])):
        female = replace_form(female, masculine, feminine)
    return male, female


# Rows where a global form swap would touch the fixed speaker/third party, or
# where the reviewed text benefits from a small human rewrite.
VARIANT_OVERRIDES: dict[str, tuple[str, str]] = {
    "dlcep001_0030_0012": (
        "Я должна высказать ему всё, что думаю!\nПойдём через дверь. Ты готов?",
        "Я должна высказать ему всё, что думаю!\nПойдём через дверь. Ты готова?",
    ),
    "d210_040_070": (
        "Где ты был?!\nЯ уже думала, что ты погиб!",
        "Где ты была?!\nЯ уже думала, что ты погибла!",
    ),
    "f_d0202_0040_0030": (
        "Скажи, ты знал, что Меркуримон давным-давно был странником?",
        "Скажи, ты знала, что Меркуримон давным-давно был странником?",
    ),
    "f_d0202_0630_0010": (
        "Ну, приветик! О да, я тебя помню... Ты один из моих\nпоклонников, да?!",
        "Ну, приветик! О да, я тебя помню... Ты одна из моих\nпоклонниц, да?!",
    ),
    "f_d0204_0260_0030": (
        "Просыпайся, дорогой клиент! Ты не должен спать посреди пола в\nтаком виде!",
        "Просыпайся, дорогая клиентка! Ты не должна спать посреди пола в\nтаком виде!",
    ),
    "f_d0204_9010_0010": (
        "... Ты следующий? Очень хорошо! Ты готов?!",
        "... Ты следующая? Очень хорошо! Ты готова?!",
    ),
    "f_d0403_9000_0040": (
        "Я думала, у меня есть шанс, но ты оказался слишком хорош.",
        "Я думала, у меня есть шанс, но ты оказалась слишком хороша.",
    ),
    "f_d0404_9010_0050": (
        "Фух, мне всё-таки удалось победить. Ты был непростым\nсоперником!",
        "Фух, мне всё-таки удалось победить. Ты была непростой\nсоперницей!",
    ),
    "f_d0701_0010_0400": (
        "Если бы ты был рядом, я бы, пожалуй, решился, глурп!\nЛадно, я сам отведу тебя к нему!",
        "Если бы ты была рядом, я бы, пожалуй, решился, глурп!\nЛадно, я сам отведу тебя к нему!",
    ),
    "f_d0907_0110_0030": (
        "...но я уверен, что мне не избежать этой участи. Отсюда нет\nпути назад... Ты готов?",
        "...но я уверен, что мне не избежать этой участи. Отсюда нет\nпути назад... Ты готова?",
    ),
    "f_d0907_0110_0060": (
        "Я даже пытался уничтожить яйцо до своего рождения...\nНо помнишь? Ты был единственным, кто меня остановил.",
        "Я даже пытался уничтожить яйцо до своего рождения...\nНо помнишь? Ты была единственной, кто меня остановил.",
    ),
    "m130_090_020": (
        "Ты видел меня? Видел, на что я способен? Хахаха!",
        "Ты видела меня? Видела, на что я способен? Хахаха!",
    ),
    "s010_179_190": (
        "Ты прав. Это я, Курои. Удивлён,\nчто ты меня узнал.",
        "Ты права. Это я, Курои. Удивлён,\nчто ты меня узнала.",
    ),
    "s030_029_080": (
        "Тебе меня не одурачить. Ты и есть тот разведчик, о котором\nя говорил, и по хитрому взгляду видно: ты всё знал!",
        "Тебе меня не одурачить. Ты и есть та разведчица, о которой\nя говорил, и по хитрому взгляду видно: ты всё знала!",
    ),
    "s110_208_110": (
        "Перед тобой великий герой Шамбалы — Сусаномон. Ты должен\nсчитать за честь возможность сразиться с ним.",
        "Перед тобой великий герой Шамбалы — Сусаномон. Ты должна\nсчитать за честь возможность сразиться с ним.",
    ),
    "f_t0103_9000_0040": (
        "Отлично, я выиграла! Уверена, ты думал, что я плохо играю,\nда? Не повезло тебе!",
        "Отлично, я выиграла! Уверена, ты думала, что я плохо играю,\nда? Не повезло тебе!",
    ),
}


# Confirmed fixed-character mistakes and a few nearby agreement errors found
# while checking their scene context.  These never enter the protagonist map.
FIXED_UPDATES: dict[tuple[str, str, str], str] = {
    ("patch_text01", "message/d05.mbe/000_Sheet1.csv", "f_d0502_0110_0020"):
        "Наш товарищ внутри обезумел! Останови его, пожалуйста!",
    ("patch_text01", "message/s050_038.mbe/000_Sheet1.csv", "s050_038_0030"):
        "Да ладно! О тебе говорит весь город — тебя тут знает каждый!",
    ("patch_text01", "message/s050_038.mbe/000_Sheet1.csv", "s050_038_0120"):
        "О, вижу, у тебя дела. Возвращайся, когда освободишься!",
    ("patch_text01", "message/s050_038.mbe/000_Sheet1.csv", "s050_038_0200"):
        "А, вот и ты! И все материалы на месте!",
    ("patch_text01", "message/s050_042.mbe/000_Sheet1.csv", "s050_042_0270"):
        "Перо Пэрротмона у тебя?! Отлично, давай сюда.",
    ("patch_text01", "message/s050_042.mbe/000_Sheet1.csv", "s050_042_0280"):
        "Ну что, хорошо, что мы объединились?\n"
        "Основную работу сделал я, но твою помощь тоже не забуду.",
    ("patch_text01", "message/s200_148.mbe/000_Sheet1.csv", "s200_148_390"):
        "Да... пожалуй! Может, люди не так страшны, как я думала?",
    ("addcont_02_text01", "message/d220.mbe/000_Sheet1.csv", "d220_030_150"):
        "Ты не вернулась, поэтому я начал волноваться.",
    ("patch_text01", "message/battle.mbe/000_Sheet1.csv", "1200020126"):
        "Ты уже должен быть на грани гибели...",
    ("patch_text01", "message/battle.mbe/000_Sheet1.csv", "1200020170"):
        "Держись!",
    ("patch_text01", "message/d01.mbe/000_Sheet1.csv", "f_d0101_0140_0020"):
        "Нам это нужно, чтобы всё изменить! Поверь мне.",
    ("patch_text01", "message/d02.mbe/000_Sheet1.csv", "f_d0201_0650_0060"):
        "Ты правда уволился?! Вот это круто! Гя-ха-ха!",
    ("patch_text01", "message/d02.mbe/000_Sheet1.csv", "f_d0204_0260_0030"):
        "Просыпайся, дорогая клиентка! Нельзя же спать прямо на полу!",
    ("patch_text01", "message/m110.mbe/000_Sheet1.csv", "m110_050_120"):
        "Ты говорил, что знаешь это место. Уже бывал здесь?",
    ("patch_text01", "message/m120.mbe/000_Sheet1.csv", "m120_100_230"):
        "Что вы сказали?!",
    ("patch_text01", "message/m130.mbe/000_Sheet1.csv", "m130_090_020"):
        "Ты видела меня? Видела, на что я способен? Ха-ха-ха!",
    ("patch_text01", "message/m170.mbe/000_Sheet1.csv", "m170_065_100"):
        "Но ведь всё именно так, как ты сказала, правда? Чтобы позаботиться о том, кому больно, причина не нужна.",
    ("patch_text01", "message/m170.mbe/000_Sheet1.csv", "m170_090_030"):
        "Ты права... Теперь им будет ещё труднее это понять...",
    ("patch_text01", "message/m170.mbe/000_Sheet1.csv", "m170_130_010"):
        "Хватит копаться! Течение нашли?",
    ("patch_text01", "message/m170.mbe/000_Sheet1.csv", "m170_130_050"):
        "...! Ты?! Ты жив?!",
    ("patch_text01", "message/m190.mbe/000_Sheet1.csv", "m190_070_090"):
        "Ты точно не хотел там остаться?",
    ("patch_text01", "message/t03.mbe/000_Sheet1.csv", "f_t0302_0110_0120"):
        "Уверена? Я бы ещё немного из него выжала... Так и хочется стиснуть эту башку...",
    ("addcont_01_text01", "message/d110.mbe/000_Sheet1.csv", "d110_080_010"):
        "Что ты сделала с моим хозяином?!",
    ("addcont_01_text01", "message/d120.mbe/000_Sheet1.csv", "d120_060_030"):
        "«Ч-что ты сказал?\nКапитан тяжело ранен?!»",
    ("addcont_01_text01", "message/d120.mbe/000_Sheet1.csv", "d120_060_070"):
        "Я была тогда совсем юной, но до сих пор отчётливо это помню.",
    ("addcont_01_text01", "message/d130.mbe/000_Sheet1.csv", "d130_060_020"):
        "«У меня есть оружие, которое ты сделала.\nС ним у меня хотя бы будет шанс»." ,
    ("addcont_01_text01", "message/d130.mbe/000_Sheet1.csv", "d130_060_070"):
        "«Я закончила техническое обслуживание».",
    ("addcont_01_text01", "message/d130.mbe/000_Sheet1.csv", "d130_060_080"):
        "«И добавила новую функцию».",
    ("addcont_01_text01", "message/d130.mbe/000_Sheet1.csv", "d130_060_110"):
        "«Я... идеалистка».",
    ("addcont_01_text01", "message/d140.mbe/000_Sheet1.csv", "d140_025_120"):
        "Ты пришёл сюда вместе с моей дочерью...\nДля меня этого достаточно.",
    ("addcont_03_text01", "message/d320.mbe/000_Sheet1.csv", "d320_070_110"):
        "«Ты сказал, что для службы в общественной безопасности\nнужны именно такие люди, как я».",
    ("patch_text01", "message/m070.mbe/000_Sheet1.csv", "m070_060_040"):
        "Точной гарантии нет, но с нашим прототипом ты не сможешь\nнанести им серьёзный урон.",
    ("patch_text01", "message/field_text.mbe/000_Sheet1.csv", "g_degi_h0211_0020"):
        "Что такое, места больше нет? Бери пример с моих бутылок —\nони всегда пустые! Хахаха!",
    ("patch_text01", "message/s010_180.mbe/000_Sheet1.csv", "s010_180_200"):
        "Ты ранена?! И всё потому, что защитила меня... Помощь уже\nв пути! Держись!",
    ("patch_text01", "message/s200_147.mbe/000_Sheet1.csv", "s200_147_340"):
        "Беги! Ты должна убираться отсюда! Этот монстр скоро вернётся!",
    ("patch_text01", "message/s910_170.mbe/000_Sheet1.csv", "s910_170_230"):
        "Ч-ч-что это за место?! Ты уверена, что всё правильно?!",
}


FIXED_CONTEXT_STYLE_KEYS = {
    ("addcont_01_text01", "message/d120.mbe/000_Sheet1.csv", "d120_060_030"),
    ("addcont_03_text01", "message/d320.mbe/000_Sheet1.csv", "d320_070_110"),
}


# Mechanical style candidates confirmed against their English source and
# neighbouring Russian lines.  All other style markers are legitimate in
# context and are explicitly marked as such in the review report.
STYLE_UPDATES: dict[str, str] = {
    # "является / являются"
    "d310_080_090": "Но логичность и оптимальность — совсем разные вещи.",
    "d310_100_220": "Это совершенно нелогично, но чувства логике и не подчиняются.",
    "d320_010_050": "X-антитело — не орудие божественной воли.\nЭто всего лишь программа.",
    "d320_040_030": "Похоже, у них X-антитела внешние, а не внутренние.",
    "f_d0905_0080_0130": "Они тоже — порождение Хроник Акаши: убийцы,\nсозданные уничтожать таких незваных гостей, как мы!",
    "f_d1301_0440_0030": "«Так что же несут нам дигимоны: погибель, разрушение и хаос?\nИли, напротив, спасение в час беды?»",
    "f_d1301_0450_0020": "«Если дигимоны — часть иммунного ответа мира на кризис,\nпочему тогда враждебные дигимоны нападают на людей?»",
    "m090_010_060": "Но эмоции не должны мешать делу. Инори Мисоно\nи Эгиомон сами по себе аномалии.",
    "m090_080_090": "Я пришла из Илиады — Цифрового мира, параллельного\nМатериальному миру, где живёте вы.",
    "m170_210_130": "Если Течение — действительно то, к чему стремятся Титаны,\nтогда, скорее всего, они хотят—",
    "m210_050_050": "О таких явлениях почти ничего не известно. Можно лишь предположить,\nчто они буквально нарушают законы времени и пространства.",
    "m310_010_120": "Мы только что установили: Эгиомон — главная угроза\nгомеостазу мира.",
    "m310_010_130": "Поэтому теперь АДАМАС должен ликвидировать\nЭгиомона и его партнёра-человека.",
    "m410_110_130": "...всё это — часть ритуала, который превратит тебя\nв Хранителя времени.",
    "m420_010_183": "...оно тоже стало воплощением горького гнева Хрономона.\nИменно поэтому в него установили ядро дигимона.",
    "m420_010_230": "Если сама война и есть цель... тогда Хрономону, вероятно,\nвсё равно, кто гибнет — дигимоны или люди.",
    "s050_176_440": "Мы сразились с таким могучим воином, как ты, и выстояли.\nЭто само по себе доказывает нашу доблесть!",
    "s100_088_070": "Иными словами, как и король Драсил, я хранитель\nдругого мира.",
    "s110_101_600": "Упомянутая мной шахта — опасное место:\nв последнее время там участились кражи.",
    "s200_146_120": "Вы приобрели эту форму на незаконном аукционе? Незаконный\nоборот казённого снаряжения — серьёзное преступление...",

    # awkward "довольно"
    "arena01_f001_007_030": "Совпадение или хитрый план? Они раз за разом проходили дальше\nбез боя! Хороши ли они? Кто знает? Но запашок от них ещё тот!",
    "arena01_f001_011_040": "Давно не виделись, малыш! Но у меня дел по горло, так что\nдавай покончим с этим побыстрее!",
    "f_d0201_0600_0030": "...но мириться с навязанным ими укладом нам непросто.",
    "f_d0301_0070_0010": "Давно не виделись, брат. В отличие от остальных, я понимаю\nтвои странности.",
    "f_d0703_0070_0550": "...а снежные гоблимоны прекрасно приспособлены к холоду.\nПожалуй, так будет точнее всего.",
    "f_d0903_0040_0060": "В следующий раз принеси ему тот фиолетовый фрукт! На вид он\nядовитый, но наверняка вкус у него что надо!",
    "f_d0903_0045_0250": "Тут вы правы. Приятно было вспомнить старые времена.",
    "m170_070_070": "Мне показалось, что Цифровой мир и мир людей\nсильно влияют друг на друга.",
    "m235_040_050": "У меня тут творился настоящий хаос. Мне пришлось перевестись\nиз управления безопасности в D-SAT...",
    "m260_080_160": "Венусмон, нам нужна твоя помощь. Меркуримон в мире людей\nи, судя по всему, тяжело ранен.",
    "m370_110_010": "А силы тебе не занимать...",
    "s110_101_890": "Похоже, мы его прогнали. А ты не промах!\nНе ожидал, что ты выстоишь!",
    "s110_103_220": "Что-то ты сомневаешься. А эта штука и правда\nведёт себя странно...",
    "s110_103_420": "Сразу видно: сражаешься ты великолепно. Впечатляет.",
    "s110_113_410": "Неплохо... Погоди! Так это мы с тобой встретились прошлой ночью!\nЭм... не одолжишь немного денег?",
    "s110_211_520": "С тобой интересно! Давненько я не получал\nтакого удовольствия от боя.",
    "s110_211_560": "Вот это сила! Благодаря тебе я наконец как следует разогрелся.\nБыло весело!",
    "s910_171_730": "Удивительно, как спокойно ты держишься после нападения...",

    # awkward or grammatically broken "действительно"
    "d220_060_030": "Да, ты настоящий Банчо.",
    "d220_060_130": "Спасибо за заботу. Но и удар у тебя будь здоров.",
    "d220_080_070": "Если ты достоин этого ГАКУ-РАНА...\nПусть за тебя говорят кулаки.",
    "d220_120_020": "Я понял это после нашей стычки.\nТы Банчо, достойный моего уважения.",
    "d320_080_080": "Эта информация нам точно пригодится!",
    "f_d0201_0680_0010": "Хотя с появлением Титанов жизнь здесь, похоже,\nстала богаче...",
    "f_d0202_0560_0010": "Эй! Ты спас наши шкуры! Сразу видно — настоящий профессионал!",
    "f_d0204_0380_0020": "Вот это крутые ребята... Показали мне,\nчто значит уступать в огневой мощи.",
    "f_d0204_0560_0030": "Примите мою искреннюю благодарность!\nСпасибо! Я правда очень благодарен!",
    "f_d0204_9020_0040": "*Ик* Я проиграл. Теперь точно пора выпить.",
    "f_d0301_0010_0040": "Неловко просить, но... сможешь разыскать Камемона?",
    "f_d0301_0070_0050": "А если нет... неужели ты стал предателем?!",
    "f_d0302_0180_0020": "АЙ! Больно же! Да кто ты вообще такой?!",
    "f_d0303_0040_0090": "Неясно, можно ли ему доверять. К тому же он бросил тебя\nв опасном месте...",
    "f_d0404_0030_0020": "Шуримон как следует меня отругал... но у него доброе сердце,\nи ему правда не всё равно...",
    "f_d0502_0200_0120": "...Мы просто меняем предметы местами,\nно юным дигимонам это очень нравится.",
    "f_d0513_0070_0020": "Вот это сила! Но и я ведь был не промах, да?",
    "f_d0903_0045_0210": "Мы знаем, что в бою ты вполне можешь за себя постоять.",
    "f_d0904_0610_0070": "Люди и дигимоны действуют сообща... Мы обязаны победить\nХрономона ради всеобщего блага!",
    "f_d0906_0050_0100": "Ситуация накаляется — и ничего хорошего это не сулит.",
    "f_d1204_0170_0040": "Не знаю, как сказать, но... вдвоём мы здесь\nедва выносим это место.",
    "f_d1204_0610_0010": "Привет! У меня для вас отличные новости!\nИ на этот раз бесплатно!",
    "m170_050_210": "Не могу поверить, что она лжёт. Может... нам всё-таки\nстоит ей довериться?",
    "m180_010_180": "В глубине души Хирока очень добрая. Такая уж она.",
    "m180_040_130": "У тебя доброе сердце, знаешь?",
    "m230_030_040": "Даже я заметил разницу, а уж тебя, её подругу,\nэто наверняка совсем сбивает с толку.",
    "m230_030_050": "Чувствую себя героем не из своего времени, который очнулся\nпосле долгого сна... Теперь мне даже страшновато встречаться с папой.",
    "m230_030_090": "У тебя очень доброе сердце, знаешь?",
    "m240_020_090": "Да, нелегко. Многие здесь считают нас врагами.\nИ ущерб мы нанесли немалый.",
    "m260_080_170": "Это... очень тревожные новости...",
    "m285_030_150": "И если бы такое и правда было возможно...\nсами основы нашего мира перевернулись бы с ног на голову.",
    "m350_120_010": "Ах... Вижу, твоя сила возросла. Какая радость.",
    "m390_110_020": "Фух... Спасибо. Без тебя я бы не справился.",
    "s020_018_560": "Так, посмотрим... Ого! Шеллмон всё отлично разложила!\nСразу всё понятно.",
    "s020_018_1130": "Некоторые такие красивые и блестящие! Заманчиво, правда?\nКак думаешь, сможешь за ними сплавать?",
    "s030_030_300": "Ты зовёшь на помощь побеждённого врага? Хахаха!\nСтранно ты рассуждаешь!",
    "s090_072_590": "Значит, ты и правда понимаешь нас, дигимонов!\nТеперь я наконец смогу вернуться домой, да?!",
    "s090_072_770": "Значит, между тобой и нами, дигимонами, и правда есть связь!\nТеперь я наконец смогу вернуться домой, да?!",
    "s110_211_620": "Вот это сила! Сразись со мной ещё раз!",
    "s200_149_260": "...Ага! Я так и знала! Ещё одно сообщение! Оно пришло так вовремя,\nбудто за нами следят.",
    "s910_171_670": "Хм. Да, талантливейший образец. И всё же ей далеко до меня...",
    "f_t0401_0110_0010": "Кто бы мог подумать, что здесь столько разных товаров?\nМир людей не перестаёт удивлять.",
}


def read_dicts(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def read_rows(path: Path) -> list[list[str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.reader(handle))


def write_rows(path: Path, rows: list[list[str]]) -> None:
    raw = path.read_bytes() if path.exists() else b""
    has_bom = raw.startswith(b"\xef\xbb\xbf")
    newline = "\r\n" if b"\r\n" in raw else "\n"
    physical_lines = raw.removeprefix(b"\xef\xbb\xbf").splitlines()
    quote_all = len(physical_lines) > 1 and physical_lines[1].lstrip().startswith(b'"')
    encoding = "utf-8-sig" if has_bom else "utf-8"
    with path.open("w", encoding=encoding, newline="") as handle:
        if quote_all:
            csv.writer(handle, lineterminator=newline).writerow(rows[0])
            csv.writer(handle, lineterminator=newline, quoting=csv.QUOTE_ALL).writerows(rows[1:])
        else:
            csv.writer(handle, lineterminator=newline).writerows(rows)


def review_key(row: dict[str, str]) -> tuple[str, str, str, str, str]:
    return (row["category"], row["package"], row["file"], row["row_id"], row["marker"])


def apply_updates(updates: dict[tuple[str, str, str], str]) -> tuple[int, int]:
    grouped: dict[tuple[str, str], dict[str, str]] = defaultdict(dict)
    for (package, filename, row_id), text in updates.items():
        grouped[(package, filename)][row_id] = text

    changed = unchanged = 0
    for (package, filename), wanted in grouped.items():
        path = CSV_ROOT / package / filename
        rows = read_rows(path)
        found: set[str] = set()
        dirty = False
        for row in rows[1:]:
            if len(row) != 4 or row[0] not in wanted:
                continue
            found.add(row[0])
            if row[2] == wanted[row[0]]:
                unchanged += 1
            else:
                row[2] = wanted[row[0]]
                changed += 1
                dirty = True
        missing = set(wanted) - found
        if missing:
            raise RuntimeError(f"{path}: missing rows {sorted(missing)}")
        if dirty:
            write_rows(path, rows)
    return changed, unchanged


def main() -> None:
    audit = read_dicts(AUDIT)
    if len(audit) != 583:
        raise RuntimeError(f"Expected 583 v067 candidates, got {len(audit)}")
    gender = [row for row in audit if row["category"] == "possible_player_address_gender"]
    style = [row for row in audit if row["category"] == "style_review"]
    if (len(gender), len(style)) != (201, 382):
        raise RuntimeError(f"Unexpected candidate split: {len(gender)} / {len(style)}")

    player_rows: list[dict[str, str]] = []
    review_by_key: dict[tuple[str, str, str, str, str], dict[str, str]] = {}
    for position, row in enumerate(gender, 1):
        key = (row["package"], row["file"], row["row_id"])
        reviewed = dict(row)
        reviewed.update(disposition="fixed_context_keep", review_note="форма относится не к выбираемому герою", male_text="", female_text="", reviewed_ru="")
        if position not in NON_PLAYER_ADDRESS_POSITIONS:
            if row["row_id"] in NEUTRALIZED_PLAYER_ADDRESS:
                reviewed.update(disposition="neutralized_player_address", review_note="естественная нейтральная формулировка", reviewed_ru=FIXED_UPDATES[(row["package"], row["file"], row["row_id"])])
            else:
                male, female = VARIANT_OVERRIDES.get(row["row_id"], generic_variants(row["current_ru"]))
                if male == female:
                    raise RuntimeError(f"Identical variants for {row['row_id']}: {male!r}")
                reviewed.update(disposition="player_address_variant", review_note="NPC обращается к выбираемому герою", male_text=male, female_text=female, reviewed_ru=male)
                player_rows.append({
                    "package": row["package"],
                    "file": row["file"],
                    "base_id": row["row_id"],
                    "role": "player_address",
                    "male_protagonist_text": male,
                    "female_protagonist_text": female,
                    "confidence": "1.00",
                    "basis": "reviewed_player_address_v068",
                })
        elif key in FIXED_UPDATES:
            if key in FIXED_CONTEXT_STYLE_KEYS:
                reviewed.update(
                    disposition="fixed_context_style_rewrite",
                    review_note="форма относится не к игроку; исправлены пунктуация или стиль",
                    reviewed_ru=FIXED_UPDATES[key],
                )
            else:
                reviewed.update(disposition="fixed_character_correction", review_note="исправлен род фиксированного персонажа", reviewed_ru=FIXED_UPDATES[key])
        review_by_key[review_key(row)] = reviewed

    audit_keys = {(row["package"], row["file"], row["row_id"]): row for row in audit}
    updates = dict(FIXED_UPDATES)
    for reviewed in player_rows:
        key = (reviewed["package"], reviewed["file"], reviewed["base_id"])
        updates[key] = reviewed["male_protagonist_text"]

    style_id_counts: dict[str, int] = defaultdict(int)
    for row in style:
        style_id_counts[row["row_id"]] += 1
    duplicates = sorted(row_id for row_id in STYLE_UPDATES if style_id_counts[row_id] != 1)
    if duplicates:
        raise RuntimeError(f"Style rewrite IDs missing or duplicated in audit: {duplicates}")
    for row in style:
        key = (row["package"], row["file"], row["row_id"])
        reviewed = dict(row)
        if row["row_id"] in STYLE_UPDATES:
            new_text = STYLE_UPDATES[row["row_id"]]
            reviewed.update(disposition="confirmed_style_rewrite", review_note="механическая или грамматически сломанная формулировка", male_text="", female_text="", reviewed_ru=new_text)
            updates[key] = new_text
        else:
            reviewed.update(disposition="style_keep", review_note="маркер естественен в контексте", male_text="", female_text="", reviewed_ru="")
        review_by_key[review_key(row)] = reviewed

    # Every fixed update that belongs to the audit must use its authoritative
    # package/file key.  Extra nearby scene corrections are allowed.
    for key in updates:
        if key in audit_keys:
            continue
        if key not in FIXED_UPDATES:
            raise RuntimeError(f"Unexpected non-audit update: {key}")

    existing = read_dicts(DATASET)
    existing = [row for row in existing if row.get("basis") != "reviewed_player_address_v068"]
    all_dataset = existing + sorted(player_rows, key=lambda row: (row["package"], row["file"], row["base_id"]))
    fields = ["package", "file", "base_id", "role", "male_protagonist_text", "female_protagonist_text", "confidence", "basis"]
    with DATASET.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(all_dataset)

    changed, unchanged = apply_updates(updates)

    review_fields = list(audit[0]) + ["disposition", "review_note", "male_text", "female_text", "reviewed_ru"]
    with REVIEW.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=review_fields, lineterminator="\n")
        writer.writeheader()
        for row in audit:
            writer.writerow(review_by_key[review_key(row)])

    counts: dict[str, int] = defaultdict(int)
    for row in review_by_key.values():
        counts[row["disposition"]] += 1
    print(f"Reviewed candidates: {len(review_by_key)}")
    print(f"New player-address variants: {len(player_rows)}")
    print(f"Style rewrites: {len(STYLE_UPDATES)}")
    print(f"CSV rows changed/already current: {changed}/{unchanged}")
    print("Dispositions: " + ", ".join(f"{key}={counts[key]}" for key in sorted(counts)))
    print(f"Review: {REVIEW}")


if __name__ == "__main__":
    main()

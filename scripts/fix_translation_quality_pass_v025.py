from __future__ import annotations

import csv
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CSV_ROOT = ROOT / "csv"
LOG_PATH = ROOT / "logs" / "fix_translation_quality_pass_v025.log"

CSV_ROOTS = [
    path
    for path in sorted(CSV_ROOT.iterdir())
    if path.is_dir() and ((path / "message").exists() or (path / "text").exists())
]

APP_ROOT = CSV_ROOT / "app_text01"
PATCH_ROOT = CSV_ROOT / "patch_text01"

TARGETED_ROWS: dict[tuple[str, str], str] = {
    ("text/battle_info_message.mbe/000_Sheet1.csv", "8"): "{d0} собирается с силами!",
    ("text/battle_info_message.mbe/000_Sheet1.csv", "9"): "{d0} и команда собираются с силами!",
    ("text/battle_info_message.mbe/000_Sheet1.csv", "13"): "До гибели: {d0} ход(а)...",
    ("text/battle_info_message.mbe/000_Sheet1.csv", "20"): "Сменено на {d0}!",
    ("text/battle_info_message.mbe/000_Sheet1.csv", "21"): "{d0}: деволюция!",
    ("text/battle_info_message.mbe/000_Sheet1.csv", "100021"): "{d0}: деволюция!",
    ("text/battle_info_message.mbe/000_Sheet1.csv", "22"): "{d0}: поколение восстановлено на 1 ступень!",
    ("text/battle_info_message.mbe/000_Sheet1.csv", "100022"): "{d0}: поколение восстановлено на 1 ступень!",
    ("text/battle_info_message.mbe/000_Sheet1.csv", "23"): "Усиления и ослабления {d0} поменялись местами!",
    ("text/battle_info_message.mbe/000_Sheet1.csv", "24"): "Изменения характеристик {d0} поглощены!",
    ("text/key_help_text.mbe/000_Sheet1.csv", "key_help_0004"): " Сортировка",
    ("text/key_help_text.mbe/000_Sheet1.csv", "key_help_0006"): " Подробности",
    ("text/key_help_text.mbe/000_Sheet1.csv", "key_help_0014"): " Вручную",
    ("text/key_help_text.mbe/000_Sheet1.csv", "key_help_0015"): " Поменять",
    ("text/key_help_text.mbe/000_Sheet1.csv", "key_help_0017"): " Защита",
    ("text/key_help_text.mbe/000_Sheet1.csv", "key_help_0018"): " Параметры",
    ("text/key_help_text.mbe/000_Sheet1.csv", "key_help_0019"): " Изменить",
    ("text/key_help_text.mbe/000_Sheet1.csv", "key_help_0022"): " (Удерж.) автонастройки",
    ("text/key_help_text.mbe/000_Sheet1.csv", "key_help_0023"): " Отменить/выбрать все",
    ("text/key_help_text.mbe/000_Sheet1.csv", "key_help_0024"): " Просмотр навыков",
    ("text/key_help_text.mbe/000_Sheet1.csv", "key_help_0025"): " Удалить данные",
    ("text/key_help_text.mbe/000_Sheet1.csv", "key_help_0030"): " Выбрать",
    ("text/key_help_text.mbe/000_Sheet1.csv", "key_help_0035"): " Закрыть",
    ("text/key_help_text.mbe/000_Sheet1.csv", "key_help_0038"): " Сменить дигимона",
    ("text/key_help_text.mbe/000_Sheet1.csv", "key_help_0040"): " Случайное восстановление",
    ("text/key_help_text.mbe/000_Sheet1.csv", "key_help_0041"): " К меню",
    ("text/key_help_text.mbe/000_Sheet1.csv", "key_help_0042"): " К дигимонам",
    ("text/key_help_text.mbe/000_Sheet1.csv", "key_help_0043"): " Сменить дигимона",
    ("text/key_help_text.mbe/000_Sheet1.csv", "key_help_0051"): " Финальный анализ",
    ("text/key_help_text.mbe/000_Sheet1.csv", "key_help_0053"): " Автовыбор",
    ("text/key_help_text.mbe/000_Sheet1.csv", "key_help_0057"): " Отметить цель",
    ("text/key_help_text.mbe/000_Sheet1.csv", "key_help_0058"): " Ввести имя",
    ("text/key_help_text.mbe/000_Sheet1.csv", "key_help_0060"): " Сменить цели",
    ("text/key_help_text.mbe/000_Sheet1.csv", "key_help_0065"): " К текущей миссии",
    ("text/key_help_text.mbe/000_Sheet1.csv", "key_help_0066"): " В реальный мир",
    ("text/key_help_text.mbe/000_Sheet1.csv", "key_help_0067"): " Переместить в инвентарь",
    ("text/key_help_text.mbe/000_Sheet1.csv", "key_help_0069"): " Список дигимонов",
    ("text/key_help_text.mbe/000_Sheet1.csv", "key_help_0070"): " Сменить дигимона",
    ("text/key_help_text.mbe/000_Sheet1.csv", "key_help_0071"): " Остров",
    ("text/key_help_text.mbe/000_Sheet1.csv", "key_help_0072"): " Размер",
    ("text/key_help_text.mbe/000_Sheet1.csv", "key_help_0075"): " Радиус",
    ("text/key_help_text.mbe/000_Sheet1.csv", "key_help_0076"): " Направление",
    ("text/key_help_text.mbe/000_Sheet1.csv", "key_help_0077"): " Выбрать панель",
    ("text/key_help_text.mbe/000_Sheet1.csv", "key_help_0080"): " Выбрать предмет",
    ("text/key_help_text.mbe/000_Sheet1.csv", "key_help_0082"): " Проверить личность",
    ("text/key_help_text.mbe/000_Sheet1.csv", "key_help_0089"): " Получить выбранные карты",
    ("text/key_help_text.mbe/000_Sheet1.csv", "key_help_0091"): " Принять вызов",
    ("text/key_help_text.mbe/000_Sheet1.csv", "key_help_0093"): " Целевой дигимон",
    ("text/key_help_text.mbe/000_Sheet1.csv", "key_help_0094"): " Подробности обучения",
    ("text/key_help_text.mbe/000_Sheet1.csv", "key_help_0096"): " Управление дисками навыков",
    ("text/key_help_text.mbe/000_Sheet1.csv", "key_help_0098"): " Управление снаряжением",
    ("text/key_help_text.mbe/000_Sheet1.csv", "key_help_0099"): " Оседлать",
    ("text/key_help_text.mbe/000_Sheet1.csv", "key_help_0101"): " Автовыкл.",
    ("text/key_help_text.mbe/000_Sheet1.csv", "key_help_0102"): " Эволюция",
    ("text/key_help_text.mbe/000_Sheet1.csv", "key_help_0107"): " Принять",
    ("text/key_help_text.mbe/000_Sheet1.csv", "key_help_0108"): " Отклонить",
    ("text/key_help_text.mbe/000_Sheet1.csv", "key_help_0118"): " Продолжить тренировку",
    ("text/common_message.mbe/000_Sheet1.csv", "107"): "Инвентарь",
    ("text/common_message.mbe/000_Sheet1.csv", "603"): "Инвентарь",
    ("text/common_message.mbe/000_Sheet1.csv", "120102"): "Запасные дигимоны",
    ("text/common_message.mbe/000_Sheet1.csv", "120307"): "Инвентарь",
    ("text/common_message.mbe/000_Sheet1.csv", "190016"): "Вернуть в инвентарь",
    ("text/common_message.mbe/000_Sheet1.csv", "ui_sort_0005"): "Инвентарь",
    ("text/common_message.mbe/000_Sheet1.csv", "ui_title_language_01"): "Японский",
    ("text/common_message.mbe/000_Sheet1.csv", "ui_title_language_02"): "Английский",
    ("text/common_message.mbe/000_Sheet1.csv", "ui_title_language_03"): "Французский",
    ("text/common_message.mbe/000_Sheet1.csv", "ui_title_language_04"): "Испанский",
    ("text/common_message.mbe/000_Sheet1.csv", "ui_title_language_05"): "Немецкий",
    ("text/common_message.mbe/000_Sheet1.csv", "ui_title_language_06"): "Итальянский",
    ("text/common_message.mbe/000_Sheet1.csv", "ui_title_language_07"): "Бразильский португальский",
    ("text/common_message.mbe/000_Sheet1.csv", "ui_title_language_08"): "Корейский",
    ("text/common_message.mbe/000_Sheet1.csv", "ui_title_language_09"): "Китайский (традиционный)",
    ("text/common_message.mbe/000_Sheet1.csv", "ui_title_language_10"): "Китайский (упрощённый)",
    ("text/common_message.mbe/000_Sheet1.csv", "ui_title_language_11"): "Арабский",
    ("text/common_message.mbe/000_Sheet1.csv", "ui_title_language_12"): "Польский",
    ("text/common_message.mbe/000_Sheet1.csv", "ui_title_language_13"): "Русский",
    ("text/common_message.mbe/000_Sheet1.csv", "ui_title_language_14"): "Тайский",
    ("text/common_message.mbe/000_Sheet1.csv", "ui_title_language_15"): "Индонезийский",
    ("text/info_message.mbe/000_Sheet1.csv", "info_message_playername"): "Впишите имя — и переродитесь в мире внизу...\n\n<{fc9{d0} Юки}>",
    ("text/digitter_message.mbe/000_Sheet1.csv", "sub_050_176_1"): "У меня есть одно хлопотное дело. Загляни в таверну,\nкогда будешь в Центральном городе.\nПросмотреть детали миссии {decision}",
    ("text/digitter_message.mbe/000_Sheet1.csv", "main_060_090_060"): "Насчёт ОккультТокио ТВ, о котором шла речь... По данным видно,\nчто за восемь лет число его подписчиков выросло до двух\nмиллионов.",
    ("text/quest_outline.mbe/000_Sheet1.csv", "176"): "У меня есть одно хлопотное дело. Загляни в таверну,\nкогда будешь в Центральном городе.",
    ("message/analyse.mbe/000_Sheet1.csv", "digimonride_ok"): "Этот дигимон может использовать {r1}{fc13ДигиРайд}.",
    ("message/d02.mbe/000_Sheet1.csv", "f_d0202_0300_0010"): "И кто ты такой...? Дигимон стадии Ребёнок?",
    ("message/s010_180.mbe/000_Sheet1.csv", "s010_180_160"): "Я выучила столько слов только ради разговора с тобой.\nСомневаюсь, что справилась бы без эволюции.",
    ("message/s100_178.mbe/000_Sheet1.csv", "s100_178_060"): "{next}...Естественный порядок этого мира начал рушиться?",
    ("message/s110_093.mbe/000_Sheet1.csv", "s110_093_280"): "{next}У тебя получится, Краниамон!",
    ("message/s110_093.mbe/000_Sheet1.csv", "s110_093_471"): "{next}Удачи тебе и Королевским Рыцарям.",
    ("message/s050_152.mbe/000_Sheet1.csv", "s050_152_101"): "{next}Если они эволюционируют, то станут сильнее.",
    ("message/s050_152.mbe/000_Sheet1.csv", "s050_152_140"): "Мне нужны Дигименталы, чтобы помочь им бронеэволюционировать.\nСначала нужен Дигиментал Искренности.",
    ("message/s050_152.mbe/000_Sheet1.csv", "s050_152_430"): "С помощью брони я помог всем союзникам эволюционировать!\nПожалуйста, примите этот знак моей благодарности!",
    ("message/s050_152.mbe/000_Sheet1.csv", "s050_152_1001"): "{next}Дигиментал Света.",
    ("message/s050_152.mbe/000_Sheet1.csv", "s050_152_1010"): "{next}Дигиментал Дружбы.",
    ("message/s050_152.mbe/000_Sheet1.csv", "s050_152_1100"): "{next}Дигиментал Храбрости.",
    ("message/s910_170.mbe/000_Sheet1.csv", "s910_170_020"): "Эм, это офис Хироко? Я, эм... Норио. Я ученик старшей школы,\nточнее, должен был им быть...",
    ("message/d02.mbe/000_Sheet1.csv", "f_d0203_0010_0230"): "До сих пор многое остаётся загадкой: дигимоны и их способность\nк эволюции.",
    ("message/d03.mbe/000_Sheet1.csv", "f_d0301_0180_0040"): "Я бы хотел поскорее эволюционировать и начать реально что-то менять,\nно такими темпами кто знает, когда это случится?",
    ("message/s910_171.mbe/000_Sheet1.csv", "s910_171_030"): "Раньше я этого не замечала, но он тоже есть на фотографии.",
    ("message/s910_171.mbe/000_Sheet1.csv", "s910_171_060"): "Я почти не пересматриваю старые фото. Они напоминают мне\nо людях, которых я потеряла... о тебе, например.",
    ("message/s910_171.mbe/000_Sheet1.csv", "s910_171_100"): "Если бы мы могли вернуться в прошлое, я, возможно, смогла бы\nему помочь. Тем более теперь у нас есть ты.",
    ("message/s910_171.mbe/000_Sheet1.csv", "s910_171_120"): "И всё же я всегда жалела, что не смогла помочь ему найти родителей.",
    ("message/s910_171.mbe/000_Sheet1.csv", "s910_171_130"): "Если бы восемь лет назад у меня была твоя помощь, возможно,\nу меня бы получилось.",
    ("message/s910_171.mbe/000_Sheet1.csv", "s910_171_140"): "Вот это совпадение! Я как раз собиралась тебе звонить.",
    ("message/s910_171.mbe/000_Sheet1.csv", "s910_171_150"): "Не хочешь помочь мне с одним непростым делом?",
    ("message/s910_171.mbe/000_Sheet1.csv", "s910_171_170"): "Познакомься с моим бывшим одноклассником, Кинширо Ериито.\nОн пришёл ко мне с довольно сложной просьбой.",
    ("message/s910_171.mbe/000_Sheet1.csv", "s910_171_180"): "Как тебя зовут? Я запомню.",
    ("message/s910_171.mbe/000_Sheet1.csv", "s910_171_200"): "Как видишь, он немного эксцентричен, но насчёт своего гения\nон буквально прав.",
    ("message/s910_171.mbe/000_Sheet1.csv", "s910_171_240"): "Тут не поспоришь. Думаю, у всего есть обратная сторона,\nдаже у гениальности.",
    ("message/s910_171.mbe/000_Sheet1.csv", "s910_171_250"): "Я бы сказала, да. Высокомерие и грубость для него почти\nрабочий режим по умолчанию.",
    ("message/s910_171.mbe/000_Sheet1.csv", "s910_171_260"): "Эй, я НЕ эксцентричная! Ты правда меня такой видишь?!\nСкажу честно, я потрясена!",
    ("message/s910_171.mbe/000_Sheet1.csv", "s910_171_360"): "Я — развитая форма жизни, следующий шаг в эволюции человека.",
    ("message/s910_171.mbe/000_Sheet1.csv", "s910_171_380"): "Эм... О себе говорите что хотите, но других так называть\nне стоит.",
    ("message/s910_171.mbe/000_Sheet1.csv", "s910_171_510"): "{next}Кто-нибудь из общественной безопасности?",
    ("message/s910_171.mbe/000_Sheet1.csv", "s910_171_520"): "Хм, не уверена. Ты знаешь кого-нибудь, кто расследует это место?",
    ("message/s910_171.mbe/000_Sheet1.csv", "s910_171_530"): "Доктор...? А, тот чудаковатый учёный, о котором ты рассказывал?",
    ("message/s910_171.mbe/000_Sheet1.csv", "s910_171_540"): "Да брось. По твоему лицу было видно, что ты понятия не имеешь,\nкогда он упомянул Genius Lab.",
    ("message/s910_171.mbe/000_Sheet1.csv", "s910_171_550"): "Я ещё не встречалась с доктором Симмонс, но, может быть,\nона что-нибудь знает.",
    ("message/s910_171.mbe/000_Sheet1.csv", "s910_171_690"): "П-прости за это! Давай. Пошли! Я сказала, пошли уже!",
    ("message/s910_171.mbe/000_Sheet1.csv", "s910_171_750"): "Д-да, она определённо такая же странная, как я слышала.\nНужно ей помочь...!",
    ("message/s910_171.mbe/000_Sheet1.csv", "s910_171_770"): "Не уверена, что тебе удалось бы справиться, если бы мы не появились...",
    ("message/s910_171.mbe/000_Sheet1.csv", "s910_171_920"): "Вы правда готовы нам помочь...?",
    ("message/s910_171.mbe/000_Sheet1.csv", "s910_171_940"): "И этого мальчика тоже можно считать жертвой. Так что я помогу —\nи в знак благодарности за вашу сегодняшнюю помощь.",
    ("message/s910_171.mbe/000_Sheet1.csv", "s910_171_960"): "Когда меня что-то заинтересует, мне много времени не нужно.",
    ("message/s910_171.mbe/000_Sheet1.csv", "s910_171_1030"): "Конечно, нет. Именно потому, что всё получилось, я теперь\nнесколько сомневаюсь...",
    ("message/s910_171.mbe/000_Sheet1.csv", "s910_171_1230"): "Дай ему время. Это слишком тяжёлая правда, чтобы принять её сразу.",
    ("message/s910_171.mbe/000_Sheet1.csv", "s910_171_1250"): "Пока это только предположение, но, думаю, изменения начнутся\nпримерно через пять-шесть лет.",
    ("message/s910_171.mbe/000_Sheet1.csv", "s910_171_1280"): "Но я понимаю, каково это — хотеть найти маму и папу\nи поговорить с ними.",
    ("message/s910_171.mbe/000_Sheet1.csv", "s910_171_1290"): "Я уже видела, как друг теряет родителя...",
    ("message/s910_171.mbe/000_Sheet1.csv", "s910_171_1300"): "Заставлять человекообразных обезьян эволюционировать,\nчтобы создавать искусственных гениев? В этом нет ни капли красоты...",
}

SHORT_RESPONSES: dict[str, str] = {
    "A Дигиментал of Courage.": "Дигиментал Храбрости.",
    "A Дигиментал of Friendship.": "Дигиментал Дружбы.",
    "A Дигиментал of Light.": "Дигиментал Света.",
    "A new problem?": "Новая проблема?",
    "A so-called designer baby?": "Так называемый дизайнерский ребёнок?",
    "All right.": "Ладно.",
    "Are those supposed to be earthworms?": "Это что, дождевые черви?",
    "Are you all right?": "Ты в порядке?",
    "Are you feeling all right?": "Ты хорошо себя чувствуешь?",
    "Are you really human?": "Ты правда человек?",
    "Are you sure this is okay?": "Так точно можно?",
    "Are you worried?": "Ты волнуешься?",
    "Balance in any and all things.": "Во всём нужен баланс.",
    "Beat you at what?": "В чём именно тебя победить?",
    "Bye! See you later!": "Пока! Увидимся!",
    "Can I help you?": "Я могу помочь?",
    "Can you even fly?": "А ты вообще умеешь летать?",
    "Can you fly, Plutomon?": "Плутомон, ты умеешь летать?",
    "Could it be a bicycle key?": "Может, это ключ от велосипеда?",
    "Didn't you need some advice?": "Тебе ведь нужен был совет?",
    "Did you fail to hack into the system?": "Не удалось взломать систему?",
    "Do you have any proof?": "У тебя есть доказательства?",
    "Escape from reality.": "Сбежать от реальности.",
    "Forget it. I'm leaving.": "Забудь. Я ухожу.",
    "Having some trouble?": "Какие-то проблемы?",
    "Hope you find LoaderLeomon, then!": "Надеюсь, ЛоудерЛеомон найдётся!",
    "How did you know that?": "Откуда ты это знаешь?",
    "How can we get you to fight?": "Как нам уговорить тебя сразиться?",
    "I accept.": "Принимаю.",
    "I can go visit the host for you.": "Я могу сходить к ведущему за тебя.",
    "I don't believe in fortune telling.": "Я не верю в гадания.",
    "I get it.": "Ясно.",
    "I heard everything.": "Я всё слышал.",
    "I just got here!": "Я только что здесь!",
    "I need a little break.": "Мне нужна небольшая передышка.",
    "I need to take care of other business.": "Мне нужно заняться другим делом.",
    "I need to take care of something else first.": "Сначала мне нужно кое-что сделать.",
    "I refuse.": "Отказываюсь.",
    "I wanna repair Zudomon's hammer.": "Хочу починить молот Зудомона.",
    "If they эволюционировать, then they'll be better fighters.": "Если они эволюционируют, то станут сильнее.",
    "I'm a human.": "Я человек.",
    "I'm afraid I can't right now.": "Боюсь, сейчас не получится.",
    "I'm busy right now. Maybe some other time.": "Сейчас не могу. Может, в другой раз.",
    "I'm looking forward to it.": "Буду ждать с нетерпением.",
    "I'm not a hallucination.": "Я не галлюцинация.",
    "I'm not too sure about this.": "Есть сомнения.",
    "I'm still busy.": "Пока не могу.",
    "I'm too busy right now.": "Сейчас не могу.",
    "Is it a tip for your channel??": "Это наводка для твоего канала?",
    "Is it that busy?": "Всё настолько серьёзно?",
    "Is something wrong?": "Что-то не так?",
    "Is this, like, his default personality?": "Это у него характер по умолчанию?",
    "Isn't that a crime?": "Разве это не преступление?",
    "It must have been from back then...": "Наверное, это ещё с тех времён...",
    "It's like you're a different person.": "Ты будто совсем другой человек.",
    "It's not working?": "Не получается?",
    "Just don't die on us!": "Только не вздумай погибнуть!",
    "Just ignore it.": "Просто не обращай внимания.",
    "Kunlun's envoy.": "Посланник Куньлуня.",
    "Let me look that up for you.": "Сейчас проверю.",
    "Let me think about it.": "Я подумаю.",
    "Let's fight!": "Давай сразимся!",
    "Let's go find the friend.": "Пойдём искать друга.",
    "Let's play a card game.": "Сыграем в карты.",
    "Let's talk again later.": "Поговорим позже.",
    "Long time no see, Hagurumon.": "Давно не виделись, Хагурумон.",
    "Maybe a Дигимон did it.": "Может, это сделал дигимон.",
    "Maybe a kidnapper did it.": "Может, это похититель.",
    "Maybe it has to do with a case?": "Может, это связано с делом?",
    "Maybe it was just a dream?": "Может, это был просто сон?",
    "Maybe it was you?": "Может, это был ты?",
    "Maybe some other time.": "Может, в другой раз.",
    "Maybe the cosplayer was spirited away.": "Может, косплеера унесло потусторонней силой.",
    "Maybe it's just a coincidence?": "Может, это просто совпадение?",
    "Must be a fly.": "Наверное, муха.",
    "Must be a mosquito.": "Наверное, комар.",
    "Must be the wind.": "Наверное, ветер.",
    "Never mind.": "Неважно.",
    "No, thanks.": "Нет, спасибо.",
    "Not now.": "Не сейчас.",
    "Not yet.": "Пока нет.",
    "Nothing right now.": "Пока ничего.",
    "Okay, I confess. I'm in there, too.": "Ладно, признаюсь. Я там тоже есть.",
    "Okay, wait here.": "Хорошо, жди здесь.",
    "Okay.": "Хорошо.",
    "Okay. So long!": "Хорошо. Бывай!",
    "Perfect timing.": "Как раз вовремя.",
    "Probably, yeah.": "Похоже на то.",
    "ShogunGekomon!": "СёгунГекомон!",
    "So her teacher went missing.": "Значит, её учитель пропал.",
    "So you have something I can help with?": "Значит, есть дело, с которым я могу помочь?",
    "So you want me to get materials for you?": "Значит, тебе нужны материалы?",
    "Somone with public safety?": "Кто-нибудь из общественной безопасности?",
    "Sounds creepy.": "Звучит жутко.",
    "Sounds serious.": "Звучит серьёзно.",
    "Sure thing.": "Конечно.",
    "Sure.": "Конечно.",
    "Sure. No problem.": "Конечно. Без проблем.",
    "Take a look.": "Взгляни.",
    "Tell me more about what happened.": "Расскажи подробнее, что случилось.",
    "That person has a big responsibility.": "На этом человеке большая ответственность.",
    "That's bad.": "Плохо дело.",
    "That's right!": "Именно!",
    "The Cosmic Area?": "Космическая зона?",
    "The sea is at peace now.": "Теперь море спокойно.",
    "The what?": "Что-что?",
    "What happened?": "Что случилось?",
    "What is your name?": "Как тебя зовут?",
    "What kind of favor?": "Что за просьба?",
    "What material, you mean?": "Что ты имеешь в виду под материалом?",
    "What should we do?": "Что нам делать?",
    "What sweets do you recommend?": "Какие сладости посоветуешь?",
    "What were you supposed to do?": "Что тебе нужно было сделать?",
    "What's strange about it?": "Что в нём странного?",
    "What's the matter?": "Что случилось?",
    "What's wrong?": "Что не так?",
    "Who're you talking about?": "О ком ты?",
    "Why?": "Почему?",
    "Why can't you do it?": "Почему ты не можешь?",
    "Why do you wanna get stronger?": "Зачем тебе становиться сильнее?",
    "Why don't you go yourself?": "Почему бы тебе не сходить самому?",
    "You found the data?": "Данные нашлись?",
    "You got it.": "Хорошо.",
    "You got the wrong person.": "Не тот человек.",
    "You just need to believe in yourself.": "Тебе просто нужно поверить в себя.",
    "You just now noticed?": "Ты только сейчас заметила?",
    "You nervous?": "Нервничаешь?",
    "You're still human?": "Ты всё ещё человек?",
    "You're hesitant to do so?": "Ты сомневаешься?",
    "You're friends, then?": "Значит, вы друзья?",
    "Wake up!": "Проснись!",
    "Way to go, Solarmon.": "Молодец, Солармон.",
    "Well, good luck to you.": "Ну, удачи.",
    "Well, good luck with that!": "Ну, удачи с этим!",
    "What're you up to these days?": "Чем ты сейчас занимаешься?",
    "What do you know about your parents?": "Что ты знаешь о своих родителях?",
    "What does all that mean?": "Что всё это значит?",
    "Yeah... me!": "Ага... меня!",
    "Yes, please.": "Да, пожалуйста.",
    "Yes, tell me more.": "Да, расскажи подробнее.",
    "A time bomb?": "Бомба с таймером?",
    "Actually, I just wanted to fight.": "Если честно, просто хотелось сразиться.",
    "Am I really the right person for this?": "Я правда подхожу для этого?",
    "And?": "И?",
    "And if I don't go?": "А если я не пойду?",
    "Are there any side effects?": "Есть побочные эффекты?",
    "Are you giving me candy?": "Ты даёшь мне конфеты?",
    "Are you giving me something?": "Ты хочешь мне что-то дать?",
    "Are you Jesmon?": "Ты Джесмон?",
    "Are you okay, Hagurumon?": "Хагурумон, ты в порядке?",
    "Are you one of the Royal Knights?": "Ты из Королевских рыцарей?",
    "As long as it's worth my while.": "Если это того стоит.",
    "Be my ally.": "Стань моим союзником.",
    "Blue for water true.": "Синий — значит вода чистая.",
    "Boo! We're ghosts...": "Бу! Мы призраки...",
    "Can you get up?": "Можешь встать?",
    "Can't we talk this out?": "Может, поговорим?",
    "Come with us.": "Пойдём с нами.",
    "Did he read the book out loud?": "Он читал книгу вслух?",
    "Did she get hit on?": "К ней приставали?",
    "Did you find a Parrotmon plume?": "Ты нашёл перо Парротмона?",
    "Did you just call me a \"Tamer\"?": "Ты только что назвал меня тамером?",
    "Do you often watch movies?": "Ты часто смотришь фильмы?",
    "Don't do anything.": "Ничего не делать.",
    "Don't keep Kunlun waiting.": "Не заставляй Куньлунь ждать.",
    "Don't take too much advantage of me...": "Только не злоупотребляй моей помощью...",
    "Feel better now?": "Теперь легче?",
    "For me?": "Для меня?",
    "Go easy on me.": "Полегче со мной.",
    "Go to Shellmon's house?": "Пойти к дому Шеллмон?",
    "Good point.": "Верно подмечено.",
    "Good thing no one was hurt.": "Хорошо, что никто не пострадал.",
    "Haha. We got you!": "Ха-ха. Попался!",
    "Hang on. Let me give it a whack!": "Погоди. Дай-ка ударю!",
    "Has humanity just been saved?": "Человечество только что спасли?",
    "He probably can't pay.": "Он, наверное, не сможет заплатить.",
    "He looks surprised...": "Он выглядит удивлённым...",
    "Here? Not a great place...": "Здесь? Не лучшее место...",
    "Here's the bill.": "Вот счёт.",
    "Hm... Let me see...": "Хм... Дай подумать...",
    "How about a game of Rock, Paper, Scissors?": "Может, сыграем в камень-ножницы-бумагу?",
    "How about another battle, then?": "Тогда как насчёт ещё одного боя?",
    "How can I get you out?": "Как мне тебя вытащить?",
    "How long ago was this?": "Как давно это было?",
    "How much could a personal diary be worth?": "Сколько может стоить личный дневник?",
    "Humanity is foolish, after all...": "Люди всё-таки глупы...",
    "Humanity will perish...": "Человечество погибнет...",
    "I came here to help.": "Я здесь, чтобы помочь.",
    "I can't go right now.": "Сейчас я не могу.",
    "I could fawn over you.": "Могу тобой повосхищаться.",
    "I don't need your services at the moment.": "Сейчас твои услуги не нужны.",
    "I don't work for free.": "Я не работаю бесплатно.",
    "I felt like cosplaying.": "Захотелось покосплеить.",
    "I had no idea...": "Понятия не было...",
    "I have no idea.": "Понятия не имею.",
    "I need to think about it.": "Мне нужно подумать.",
    "I need to think this through for a while.": "Мне нужно всё обдумать.",
    "I need you to stay here and guard this place.": "Останься здесь и охраняй это место.",
    "I sense hostility.": "Чувствую враждебность.",
    "I still can't.": "Всё ещё не могу.",
    "I think I'd rather leave.": "Я лучше уйду.",
    "I think we deserve a reward.": "Думаю, мы заслужили награду.",
    "I was hoping for a better reward.": "Хотелось награду получше.",
    "I was hoping you'd share some with me.": "Была надежда, что ты поделишься.",
    "I want you on my side.": "Хочу, чтобы ты был на моей стороне.",
    "I'll bring the band here.": "Я приведу сюда группу.",
    "I'll bring the king here.": "Я приведу сюда короля.",
    "I'll get you another one!": "Я достану тебе другой!",
    "I'll just do it without asking.": "Просто сделаю без лишних вопросов.",
    "I'll leave you alone. See you.": "Не буду мешать. Увидимся.",
    "I'll let you have it for free.": "Отдам тебе бесплатно.",
    "I'll look, but that's it.": "Я посмотрю, но только и всего.",
    "I'll sing for you instead.": "Тогда я спою вместо них.",
    "I'll take the glass.": "Я возьму стекло.",
    "I'm fine.": "Я в порядке.",
    "I'm free now.": "Теперь есть время.",
    "I'm glad you remembered.": "Хорошо, что ты вспомнил.",
    "I'm looking for PlatinumNumemon's jewelry.": "Я ищу украшение ПлатинумНумемона.",
    "I'm not telling.": "Не скажу.",
    "I'm responding to Asuna's complaints.": "Я здесь по жалобам Асуны.",
    "I'm sure there's a point.": "Уверен, смысл в этом есть.",
    "I'm sure we'll meet again.": "Уверен, мы ещё встретимся.",
    "Is Gankoomon your master?": "Ганкумон — твой учитель?",
    "Is it really so bad to be normal?": "Разве быть обычным так плохо?",
    "Is it that addictive?": "Это настолько затягивает?",
    "Is there no end to this?": "Этому вообще будет конец?",
    "Isn't it all the same?": "Разве это не одно и то же?",
    "It does sound nice.": "Звучит неплохо.",
    "It is. What do you think it means?": "Да. Как думаешь, что это значит?",
    "It sounds beautiful!": "Звучит красиво!",
    "It's a made-up story, isn't it?": "Это ведь выдуманная история?",
    "It's too dangerous.": "Это слишком опасно.",
    "Let me oil you up.": "Давай смажу тебя маслом.",
    "Let's go.": "Пошли.",
    "Let's go back to the sea.": "Вернёмся к морю.",
    "Let's go check Shinjuku Park.": "Проверим парк Синдзюку.",
    "Let's go home and get some sleep.": "Пойдём домой и выспимся.",
    "Let's go look.": "Пойдём посмотрим.",
    "Let's settle this.": "Пора с этим разобраться.",
    "Let's sing along!": "Давай подпевать!",
    "Let's try attacking.": "Попробуем атаковать.",
    "Let's try poking it.": "Попробуем ткнуть.",
    "Looking at you two together hurts my eyes...": "На вас двоих вместе больно смотреть...",
    "Maybe one of us can act as bait?": "Может, кто-то из нас станет приманкой?",
    "Maybe they're watching even now?": "Может, они следят за нами прямо сейчас?",
    "Maybe we should stop here.": "Может, на этом остановимся.",
    "My outfit stinks?": "От моего костюма воняет?",
    "Nice palette swap!": "Неплохая смена палитры!",
    "Nice to see you, boss.": "Приятно видеть, начальник.",
    "No can do. I'm too busy right now.": "Не выйдет. Сейчас совсем нет времени.",
    "No need.": "Не нужно.",
    "No, not yet.": "Нет, ещё рано.",
    "Not at all. Let's go.": "Ничуть. Пошли.",
    "Not a one. So long.": "Ни одного. Бывай.",
    "Not me?": "Не я?",
    "Not yet. Sorry.": "Пока нет. Прости.",
    "Not yet...": "Пока нет...",
    "Now you tell me!": "И ты говоришь это сейчас!",
    "Oh. In that case, I'm leaving.": "А. Тогда я ухожу.",
    "Oh, I get it! You must be hiding in fear.": "А, ясно! Ты прячешься от страха.",
    "Piece of cake.": "Проще простого.",
    "Regular, please.": "Обычную, пожалуйста.",
    "Remember what your mission is.": "Помни о своей миссии.",
    "Say, \"Regular, please.\"": "Скажи: «Обычную, пожалуйста».",
    "Say, \"With extra garlic.\"": "Скажи: «Побольше чеснока».",
    "Say, \"With extra vegetables.\"": "Скажи: «Побольше овощей».",
    "Should I jazz it up more?": "Может, добавить яркости?",
    "So, how've you been?": "Ну, как ты?",
    "So, what is it?": "Так что случилось?",
    "So it's a monster?": "Значит, это монстр?",
    "So this outfit helped?": "Значит, костюм помог?",
    "So you're the one behind all of this.": "Значит, за всем этим стоишь ты.",
    "Someone like who?": "Кто именно?",
    "Someone was just trying to get their attention.": "Кто-то просто пытался привлечь их внимание.",
    "Spirit Seeds?": "Семена духов?",
    "Sure. Happy to help.": "Конечно. С радостью помогу.",
    "Sure. Just sit tight.": "Конечно. Жди здесь.",
    "Sure, I'll wait.": "Хорошо, подожду.",
    "Sure, let's do it.": "Конечно, сделаем.",
    "That was no dream...": "Это был не сон...",
    "That's a lot of pressure.": "Ответственность немаленькая.",
    "That's a perfect example of a horrible person.": "Отличный пример ужасного человека.",
    "That's disappointing.": "Жаль.",
    "That's fine.": "Меня устраивает.",
    "That's hard to follow...": "Сложно уследить...",
    "That's a wild way of deciding.": "Дикий способ принимать решения.",
    "The king of the sea?": "Король моря?",
    "The Twentiest again?": "Опять «Двадцатка»?",
    "Then let's go back.": "Тогда возвращаемся.",
    "There's something suspicious about you...": "В тебе есть что-то подозрительное...",
    "There's something suspicious going on...": "Тут происходит что-то подозрительное...",
    "To unlock the door?": "Чтобы открыть дверь?",
    "Uh... I'll just be going now.": "Эм... Я, пожалуй, пойду.",
    "We're not dangerous.": "Мы не опасны.",
    "We're not in a position to decide.": "Не нам это решать.",
    "We're your allies.": "Мы твои союзники.",
    "Well, there they go.": "Ну вот, они ушли.",
    "What about you?": "А ты?",
    "What big disaster?": "Какая большая катастрофа?",
    "What could it be?": "Что бы это могло быть?",
    "What do you mean?": "Что ты имеешь в виду?",
    "What do you plan on doing?": "Что ты собираешься делать?",
    "What is it this time?": "Что на этот раз?",
    "What kind of ring?": "Что за кольцо?",
    "What plan?": "Какой план?",
    "What sort of jewelry were you looking for?": "Какое именно украшение тебе нужно?",
    "What's a Tamer?": "Кто такой тамер?",
    "What's it say?": "Что там написано?",
    "What's this \"big find\"?": "Что за «большая находка»?",
    "What's wrong, Hagurumon?": "Хагурумон, что случилось?",
    "Who cares?": "Какая разница?",
    "Who's the friend?": "Что за друг?",
    "Why a red book?": "Почему красная книга?",
    "Why are you doing this?": "Зачем ты это делаешь?",
    "Why are you so bored?": "Почему тебе так скучно?",
    "Why are you so tired?": "Почему ты так устал?",
    "Why here?": "Почему здесь?",
    "Why're you hiding here?": "Почему ты здесь прячешься?",
    "Wish you would've told me first.": "Лучше бы ты сначала сказал.",
    "Y-You don't say...?": "Д-да что ты...?",
    "Yeah, let's go.": "Да, пошли.",
    "Yeah. I'll get right to it.": "Да. Сейчас займусь.",
    "Yeah, maybe.": "Да, возможно.",
    "You can have it.": "Можешь забрать.",
    "You found the data?": "Данные нашлись?",
    "You looked good out there!": "Ты отлично смотрелся!",
    "You learn fast.": "Ты быстро учишься.",
    "You mean time travel?": "Ты о путешествии во времени?",
    "You need my help?": "Тебе нужна моя помощь?",
    "You really chowed down.": "Ты знатно наелся.",
    "You reap what you sow, pal.": "Что посеешь, то и пожнёшь, приятель.",
    "You seem kind of down.": "Ты какой-то подавленный.",
    "You've finally got it, huh?": "Наконец-то дошло?",
    "[Call her.]": "[Позвать её.]",
    "[Don't do anything.]": "[Ничего не делать.]",
    "[Leave the plant.]": "[Оставить растение.]",
    "[Leave.]": "[Уйти.]",
    "[I should leave her alone.]": "[Лучше оставить её в покое.]",
}

SHORT_RESPONSES_MORE: dict[str, str] = {
    "(TBD) {pf(Add-on/Add-ons/Downloadable Content/Downloadable Content)}\ncostumes, etc., to be distributed via Access.": "(Заглушка) {pf(дополнение/дополнения/загружаемый контент/загружаемый контент)}\nкостюмы и прочее, распространяемые через Access.",
    "*sigh*": "*вздох*",
    "...Am I hearing things?": "...Мне послышалось?",
    "...Are you lost?": "...Ты заблудился?",
    "...Huh?": "...А?",
    "...I think I heard something.": "...Кажется, я что-то слышу.",
    "...Lost?": "...Заблудился?",
    "...Must be a fly.": "...Наверное, муха.",
    "...Must be a mosquito.": "...Наверное, комар.",
    "...Must be the wind.": "...Наверное, ветер.",
    "...The natural order of this world has begun to break\ndown?": "...Естественный порядок этого мира начал рушиться?",
    "...The what?": "...Что-что?",
    "...\"Pepperoni\"?": "...«Пепперони»?",
    "...Just... my imagination...?": "...Просто... показалось...?",
    "4,000 \"digi\"?": "Четыре тысячи «диги»?",
    "A perfect example of a horrible person.": "Отличный пример ужасного человека.",
    "A smaller size would be more convenient.": "Маленький размер был бы удобнее.",
    "A streamer and her assistant.": "Стримерша и её помощник.",
    "A surprise \"not guilty\" verdict, huh?": "Неожиданный оправдательный приговор?",
    "Alphamon.": "Альфамон.",
    "And I need to defeat it?": "И мне нужно его победить?",
    "And what if they do set your heart aflutter?": "А если они всё-таки заставят твоё сердце дрогнуть?",
    "Apprentice?": "Ученик?",
    "Are all those shiny things feathers?": "Все эти блестящие штуки — перья?",
    "Are they all right?": "Они в порядке?",
    "Are they lost?": "Они заблудились?",
    "Are you a Royal Knight?": "Ты Королевский Рыцарь?",
    "Are you impressed?": "Впечатляет?",
    "Are you talking about Norio himself?": "Ты про самого Норио?",
    "Are you the ones behind all this?": "Это вы за всем стоите?",
    "Are you gonna start watching us?": "Теперь будешь за нами наблюдать?",
    "Are you sure this is from an action figure?": "Ты уверен, что это от фигурки?",
    "Around.": "Где-то рядом.",
    "Always sad when a beloved tool breaks.": "Жаль, когда любимая вещь ломается.",
    "Be happy with who you are now.": "Цени себя таким, какой ты есть сейчас.",
    "Bon voyage!": "Счастливого пути!",
    "But did we really need to fight?": "Но без боя правда было никак?",
    "But you were curious, too, right?": "Но тебе ведь тоже было любопытно?",
    "Can't we talk for a minute?": "Можно сначала поговорить?",
    "Can't you do something about it?": "Вы ничего не можете с этим сделать?",
    "Can't you fix it on your own?": "Самому никак не починить?",
    "Can't you sell it a bit cheaper than that?!": "Нельзя продать хоть немного дешевле?!",
    "Check? Isn't Beelzemon feeling well?": "Проверка? Бельземону нездоровится?",
    "Chron-what...?": "Хрон... что?..",
    "Craniamon.": "Краниамон.",
    "Did you do something wrong?": "Ты что-то натворил?",
    "Did you let yourself get caught?": "Ты специально дал себя поймать?",
    "Do we really have to fight?": "Нам правда нужно драться?",
    "Do you know who it is?": "Ты знаешь, кто это?",
    "Do you want to be friends?": "Хочешь подружиться?",
    "Does it have to be Akihabara?": "Обязательно Акихабара?",
    "Don't tell me you're thinking of staying?": "Только не говори, что хочешь остаться.",
    "Don't you have any plans?": "У тебя совсем нет планов?",
    "Dragon... Emperor?": "Дракон... император?",
    "Drag... Queen?": "Драг... квин?",
    "Dr. Simmons?": "Доктор Симмонс?",
    "Dynasmon.": "Динасмон.",
    "Examon.": "Экзамон.",
    "Gallantmon.": "Галлантмон.",
    "Gankoomon.": "Ганкумон.",
    "Get you in awesome shape?": "Привести тебя в отличную форму?",
    "Get your friends and try again!": "Позови друзей и попробуй снова!",
    "Gil?": "Гил?",
    "Gil, gil.": "Гил, гил.",
    "Giiil!": "Гииил!",
    "Glad you understand.": "Хорошо, что стало понятно.",
    "Good for you.": "Ну и отлично.",
    "Guardromon is worried.": "Гардромон волнуется.",
    "Guess it was just my imagination...": "Видимо, показалось...",
    "Happy now?": "Теперь доволен?",
    "Have they forgotten their mission?": "Они забыли о своей миссии?",
    "He must've inspired his younger self.": "Похоже, он вдохновил самого себя в прошлом.",
    "He was testing you?": "Он тебя проверял?",
    "He wanted to protect Shinjuku?": "Он хотел защитить Синдзюку?",
    "Hey there, {player}. I'm sorry for any trouble my past and\npresent selves caused.": "Привет, {player}. Прости за все хлопоты, которые доставили\nмои прошлое и нынешнее «я».",
    "Hiroko and {player}, right? Is she telling the truth?": "Хироко и {player}, верно? Она говорит правду?",
    "How could you tell from just the hand?": "Как это можно понять по одной руке?",
    "How do you like the human world?": "Как тебе мир людей?",
    "How many master's are gonna show up?": "Сколько ещё мастеров появится?",
    "I appreciate the help!": "Спасибо за помощь!",
    "I brought some jewelry.": "Вот украшение.",
    "I brought the material for the repairs!": "Вот материал для ремонта!",
    "I brought you a cooler.": "Вот твой кулер.",
    "I can tend to unfinished business now.": "Теперь можно закончить незавершённые дела.",
    "I could use a horse.": "Лошадь бы пригодилась.",
    "I forgot to ask for a reward!": "Надо было спросить про награду!",
    "I got this.": "Я справлюсь.",
    "I just got caught up in all of this...": "Меня просто втянуло во всё это...",
    "I need a little more time.": "Нужно ещё немного времени.",
    "I need to fix Blimpmon.": "Мне нужно починить Блимпмона.",
    "I need to get ready first.": "Сначала нужно подготовиться.",
    "I need to prepare a little more first.": "Сначала нужно немного подготовиться.",
    "I brought you a cooler.": "Вот твой кулер.",
    "I sure hope LoaderLeomon is safe.": "Надеюсь, ЛоудерЛеомон цел.",
    "I take it you're lost?": "Похоже, ты заблудился?",
    "I think I see a budding friendship here.": "Кажется, здесь зарождается дружба.",
    "I wanna buy a cooler.": "Хочу купить кулер.",
    "I wanna help realize our friend's wish.": "Хочу исполнить желание нашего друга.",
    "I want to face off against Beelzemon.": "Хочу сразиться с Бельземоном.",
    "I'd like to know why as well.": "Мне тоже хотелось бы знать почему.",
    "I'd like us to talk.": "Я хочу, чтобы мы поговорили.",
    "I'd say they were sufficient.": "Думаю, вполне достаточно.",
    "I'll be back later.": "Вернусь позже.",
    "I'll go look for LoaderLeomon.": "Пойду искать ЛоудерЛеомона.",
    "I'll go scope things out.": "Пойду разведаю обстановку.",
    "I'll go take a look.": "Пойду посмотрю.",
    "I'll go take a look!": "Пойду посмотрю!",
    "I'll go when I can.": "Пойду, когда смогу.",
    "I'll help you if you treat me to some ramen.": "Помогу, если угостишь рамэном.",
    "I'll just be leaving, then.": "Тогда я, пожалуй, пойду.",
    "I'll mention you to Neptunemon.": "Упомяну тебя при Нептунемоне.",
    "I'll show you the way.": "Покажу дорогу.",
    "I'll take it.": "Беру.",
    "I'm a big fan of yours!": "Я твой большой поклонник!",
    "I'm a little busy...": "Сейчас немного не до этого...",
    "I'm not with the Titans.": "Я не с Титанами.",
    "I'm picking up on an incredible aura, here.": "Здесь ощущается невероятная аура.",
    "I'm ready.": "Можно начинать.",
    "I'm sick of hearing about this!": "Мне уже надоело это слушать!",
    "I'm with the teacher.": "Я с учителем.",
    "In an eating competition?": "В соревновании по еде?",
    "Inori's dad?": "Отец Инори?",
    "Is it a threat, letting us know they're watching?": "Это угроза? Намекают, что следят за нами?",
    "Is it some kind of prank?": "Это какая-то шутка?",
    "Is there any way to fix it?": "Это можно как-то починить?",
    "Is there any way to reach the Cosmic Area?": "Есть способ попасть в Космическую зону?",
    "It can't be...": "Не может быть...",
    "It only seems that way.": "Это только так кажется.",
    "It was all me.": "Это всё моя заслуга.",
    "It's like your body's telling you to live.": "Будто тело само говорит тебе: живи.",
    "It's too late to turn back now.": "Отступать уже поздно.",
    "Jesmon.": "Джесмон.",
    "Just a hunch.": "Просто предчувствие.",
    "Just how strong is it?": "Насколько он силён?",
    "Kentaurosmon.": "Кентауросмон.",
    "La laaa, la la laaaaa! ♪": "Ла-лаа, ла-ла-лаааа! ♪",
    "Leave this to me.": "Оставь это мне.",
    "Leopardmon.": "Леопардмон.",
    "Let me fight alongside you.": "Позволь сражаться рядом с тобой.",
    "Let's at least go scope it out.": "Давай хотя бы разведаем.",
    "Let's go find some.": "Пойдём поищем.",
    "Let's go find their friend.": "Пойдём искать их друга.",
    "Let's just get in.": "Просто войдём.",
    "LordKnightmon.": "ЛордНайтмон.",
    "Looks like my cover's blown.": "Похоже, меня раскрыли.",
    "Looks like there's no excuse for him.": "Похоже, оправданий у него нет.",
    "Looking forward to being your friend.": "Будет приятно подружиться.",
    "Magnamon.": "Магнамон.",
    "Maybe he had some free time on his hands?": "Может, у него было слишком много свободного времени?",
    "Maybe it ran away.": "Может, он сбежал.",
    "Maybe not right now.": "Может, не сейчас.",
    "My acquaintances.": "Мои знакомые.",
    "My future fate.": "Моя будущая судьба.",
    "My partners.": "Мои партнёры.",
    "Neither impressive nor unimpressive.": "Ни хорошо, ни плохо.",
    "Nobody knows.": "Никто не знает.",
    "No work, no food.": "Кто не работает, тот не ест.",
    "No, that won't be necessary.": "Нет, в этом нет нужды.",
    "Not far.": "Недалеко.",
    "Not just yet.": "Пока нет.",
    "Not quite yet.": "Ещё не совсем.",
    "Nothing at all.": "Совсем ничего.",
    "Nothing makes you happy like a full stomach.": "Ничто так не радует, как сытый желудок.",
    "Not so great, really.": "Если честно, не очень.",
    "Now's our chance to take Beelzemon down!": "Сейчас наш шанс одолеть Бельземона!",
    "Okay, I'll help.": "Хорошо, помогу.",
    "Okay, I'll trade it.": "Хорошо, обменяю.",
    "Okay, {player}. Please send me back to my own time.": "Хорошо, {player}. Пожалуйста, отправь меня обратно в моё время.",
    "Okay. I'll take this jewelry and leave, then.": "Хорошо. Тогда заберу это украшение и уйду.",
    "Okay, we'll help you.": "Хорошо, мы поможем.",
    "Okay, you got me. It was me.": "Ладно, поймали. Это я.",
    "Omnimon.": "Омегамон.",
    "Palm-sized was cuter.": "Размером с ладонь было милее.",
    "Paradise.": "Рай.",
    "Please let me buy one.": "Пожалуйста, продай мне один.",
    "Probably just library closing time.": "Наверное, просто библиотека закрывается.",
    "Remember, Enbarrmon is at home in the sky.": "Помни: Энбаррмон в небе как дома.",
    "Should we go, too?": "Нам тоже пойти?",
    "So he's even more quirky than you?": "Значит, он ещё чуднее тебя?",
    "So, that's the theme of this bar, huh?": "Понятно. Значит, такая у бара тема?",
    "So, how do we repair your things, Beelzemon?": "Так как починить твои вещи, Бельземон?",
    "Someday, you'll be able to fight on your own.": "Когда-нибудь ты сможешь сражаться сам.",
    "Someone else might grab the stuff.": "Кто-нибудь другой может забрать вещи.",
    "Some fluffy omelet rice.": "Пышный омурайс.",
    "Sorry. I don't have one on me.": "Прости, у меня такого нет.",
    "Sorry. I still don't have time.": "Прости, времени всё ещё нет.",
    "Sorry. I'm busy right now. Maybe some other time.": "Прости, сейчас нет времени. Может, в другой раз.",
    "Sorry. I'm going out for spicy ramen.": "Прости, я ухожу за острым рамэном.",
    "Sorry. Wrong person. Goodbye.": "Извини, не тот человек. До свидания.",
    "Sorry to have kept you waiting.": "Прости, что заставил ждать.",
    "Superheroes.": "Супергерои.",
    "Sure. Let's go.": "Конечно. Пойдём.",
    "That was a huge compliment.": "Это был большой комплимент.",
    "That was fun!": "Было весело!",
    "That's a tough one.": "Сложный вопрос.",
    "That's right.": "Именно.",
    "That's right. I'm a Tamer.": "Верно. Я тамер.",
    "That's way too much.": "Это слишком дорого.",
    "That's why I'm here.": "Поэтому я здесь.",
    "The costumes did all the work.": "Всё сделали костюмы.",
    "There are places I wanna see again.": "Есть места, которые хочется увидеть снова.",
    "There's a good human right in front of you...": "Хороший человек прямо перед тобой...",
    "There's no shame in trying, at least!": "Попытаться хотя бы не стыдно!",
    "Their thoughts on what?": "Их мысли о чём?",
    "Think those moves would work in a real fight?": "Думаешь, эти приёмы сработают в настоящем бою?",
    "This can be my escape from reality.": "Это может стать моим побегом от реальности.",
    "This is all quite sudden. Can you wait a bit?": "Всё слишком внезапно. Можешь немного подождать?",
    "This is so exciting!": "Как же это волнительно!",
    "Too much energy.": "Слишком много энергии.",
    "Understood.": "Понято.",
    "UlforceVeedramon.": "УльфорсВиидрамон.",
    "Wait a second.": "Подожди секунду.",
    "Wanna ask around?": "Расспросим людей?",
    "Wanna check the area?": "Осмотрим местность?",
    "Wanna hear a funny joke?": "Хочешь услышать смешную шутку?",
    "Was it all a dream?": "Это всё был сон?",
    "Was there an accident?": "Произошёл инцидент?",
    "Wasn't she cold?": "Ей не было холодно?",
    "We did it!": "Получилось!",
    "We request the honor of dueling you.": "Просим чести сразиться с тобой.",
    "We still don't know who this \"master\" is.": "Мы всё ещё не знаем, кто этот «мастер».",
    "Weird, how?": "Странно в каком смысле?",
    "Well, I've got somewhere to be, so...": "Ну, мне пора идти, так что...",
    "Well, obviously.": "Ну, очевидно же.",
    "What do you consider \"worthy,\" Minervamon?": "Что для тебя значит «достойный», Минервамон?",
    "What do you mean by \"material\"?": "Что ты имеешь в виду под «материалом»?",
    "What do you think?": "Как думаешь?",
    "What have you been doing up until now?": "И чем ты занимался всё это время?",
    "What're you doing here?": "Что ты здесь делаешь?",
    "What's gotten into you?": "Что на тебя нашло?",
    "What's so amazing about it?": "И что в этом такого удивительного?",
    "What's the problem?": "В чём проблема?",
    "Whatever you want.": "Как пожелаешь.",
    "Which is where I come in?": "И тут нужен я?",
    "Whoa... No way...": "Ого... Не может быть...",
    "Who are you?": "Кто ты?",
    "Who could you be talking about?": "О ком ты говоришь?",
    "Who said that?": "Кто это сказал?",
    "Whose could it be?": "Чьё это может быть?",
    "Why DID you come back?": "Почему ты всё-таки вернулся?",
    "Why are they out of commission?": "Почему они выбыли из строя?",
    "Why does it cost so much?": "Почему так дорого?",
    "Why is it necessary to fight?": "Почему обязательно драться?",
    "Why not just let them join the next battle?": "Почему просто не выпустить их в следующий бой?",
    "}Why not just let them join the next battle?": "Почему просто не выпустить их в следующий бой?",
    "Why not just stay like that?": "Почему бы не остаться таким?",
    "Why not try getting even bigger?": "Почему бы не стать ещё больше?",
    "Why were you scared?": "Что тебя напугало?",
    "Won't you join us as an ally?": "Не присоединишься к нам?",
    "Would you like me to get you home?": "Хочешь, помогу добраться домой?",
    "Would you like to stay here or go home?": "Хочешь остаться здесь или вернуться домой?",
    "Yeah! Let's do this!": "Да! За дело!",
    "Yeah, that can be scary.": "Да, это может напугать.",
    "Yeah, you are acting a bit sus.": "Да, ты ведёшь себя подозрительно.",
    "Yes, I do.": "Да.",
    "Yes, I'm ready.": "Да, можно начинать.",
    "Yes, please tell me more.": "Да, расскажи подробнее.",
    "Yes, right away.": "Да, сейчас же.",
    "Yes, that might be scary.": "Да, это может быть страшно.",
    "Yes, this original size is the best.": "Да, исходный размер лучше всего.",
    "Yes, we could use your help.": "Да, нам пригодится твоя помощь.",
    "Yes, it's true.": "Да, это правда.",
    "You can do it!": "Ты справишься!",
    "You can't fight with your armor like that.": "В такой броне тебе не сражаться.",
    "You head on back. I'll be right behind you.": "Возвращайся. Я скоро подойду.",
    "You know where this part is from?": "Ты знаешь, откуда эта деталь?",
    "You know, over there.": "Ну, там.",
    "You look really bored.": "Ты выглядишь очень скучающим.",
    "You look sleepy.": "Ты выглядишь сонным.",
    "You mean THAT Mr. Miura?!": "Ты про ТОГО самого господина Миуру?!",
    "You mean you wanna go see Beelzemon?": "То есть ты хочешь увидеться с Бельземоном?",
    "You should accept Neptunemon's terms.": "Тебе стоит принять условия Нептунемона.",
    "You should have some courage yourself.": "И самому бы не помешало набраться смелости.",
    "You should be grateful.": "Тебе стоит быть благодарным.",
    "You sound fully recovered.": "Похоже, ты полностью восстановился.",
    "You wanna just sneak in?": "Хочешь просто пробраться внутрь?",
    "You wanna run for it?": "Хочешь бежать?",
    "You want to time travel again?": "Хочешь снова путешествовать во времени?",
    "You were supposed to go back to normal life.": "Тебе нужно было вернуться к обычной жизни.",
    "You won't help us?": "Ты нам не поможешь?",
    "You're gonna help Beelzemon power up, Minervamon?": "Минервамон, ты поможешь Бельземону стать сильнее?",
    "You're really into this kind of thing.": "Ты правда в этом разбираешься.",
    "You're still here?": "Ты всё ещё здесь?",
    "You're sure it wasn't in a dream?": "Ты уверен, что это был не сон?",
    "You're welcome.": "Не за что.",
    "Your face is scary.": "У тебя страшное лицо.",
    "Your master is amusing.": "Забавный у тебя мастер.",
    "Zzzzz...": "Хр-р-р...",
    "[I should leave it alone.]": "[Лучше не трогать.]",
}

SHORT_RESPONSES.update(SHORT_RESPONSES_MORE)

SHORT_RESPONSES_LATE: dict[str, str] = {
    "An electronics store.": "Магазин электроники.",
    "A stew with fish cakes and daikon.": "Оден с рыбными котлетами и дайконом.",
    "A two-pound steak.": "Стейк на два фунта.",
    "Can I have your autograph?": "Можно автограф?",
    "Feels kinda wrong to read someone's diary.": "Как-то неправильно читать чужой дневник.",
    "Hopefully, you're done horsing around.": "Надеюсь, с дурачествами покончено.",
    "Iced sweet potatoes.": "Мороженый батат.",
    "I don't feel like it right now.": "Сейчас не хочется.",
    "I don't know them.": "Я их не знаю.",
    "I hope we can all be friends.": "Надеюсь, мы все сможем подружиться.",
    "I know some places with good food.": "Я знаю места, где вкусно кормят.",
    "I sense your pride as a public safety officer.": "Чувствуется гордость сотрудника общественной безопасности.",
    "I've got a scary face to show you.": "Сейчас покажу страшное лицо.",
    "I've heard that name before.": "Я слышал это имя раньше.",
    "I-I'm not afraid...": "Я-я не боюсь...",
    "If someone walked around the park wearing this...": "Если кто-нибудь пройдётся по парку в таком виде...",
    "If they're training, isn't that a good thing?": "Если они тренируются, разве это плохо?",
    "Maybe I should talk to Mirei about it...": "Может, поговорить об этом с Мирей...",
    "Maybe LoaderLeomon is just slacking off.": "Может, ЛоудерЛеомон просто отлынивает.",
    "Norio's suit?": "Костюм Норио?",
    "Okay. I'll trade it.": "Хорошо. Обменяю.",
    "Sweets make people happy.": "Сладости делают людей счастливее.",
    "The costumes did all the work.": "Всё сделали костюмы.",
    "Want to try medicine?": "Попробуем лекарство?",
    "Weren't you lonely?": "Тебе не было одиноко?",
    "What?! Are you serious?!": "Что?! Ты серьёзно?!",
    "What are you giving me?": "Что ты мне даёшь?",
    "Who warned you?": "Кто тебя предупредил?",
    "Yes! Praise me more!": "Да! Хвали ещё!",
    "Yes, I want to face off against Beelzemon.": "Да, хочу сразиться с Бельземоном.",
    "You know who to call if you need anything.": "Знаешь, к кому обращаться, если что-то понадобится.",
    "You need to contact Guardromon.": "Тебе нужно связаться с Гардромоном.",
    "You seem pretty tough. Can I have your autograph?": "Ты выглядишь сильным. Можно автограф?",
    "You really can't go on your own?": "Ты правда не можешь пойти сам?",
    "You wear it.": "Сам надень.",
    "So you're trying to make me the bait?": "То есть приманкой буду я?",
    "I'm sure he will.": "Наверняка получится.",
    "I'm busy right now.": "Сейчас не до этого.",
    "Nice palette swap...": "Неплохая смена палитры...",
    "Omnimon?": "Омегамон?",
    "Maybe there is no point.": "Может, смысла и нет.",
    "I see. So that's the theme of this bar, huh?": "Понятно. Значит, такая у бара тема?",
    "You know who to call if you need anything.": "Знаешь, к кому обращаться, если что-то понадобится.",
    "Let's leave it here.": "Оставим это здесь.",
    "Yeah.": "Да.",
    "\"Digizoit\"? Is that like a Дигимон?": "«Дигизоид»? Это что-то вроде дигимона?",
    "The Высотный колизей is pretty fun.": "В Высотном колизее довольно весело.",
    "This isn't a place for Дигимон.": "Это место не для дигимонов.",
    "You got this, Габумон!": "Ты справишься, Габумон!",
    "Why do you want the хрондигизоидная руда?": "Зачем тебе хрондигизоидная руда?",
    "Иггдрасиль is calling for you.": "Иггдрасиль зовёт тебя.",
    "I met Иггдрасиль, by the way.": "Кстати, я встретил Иггдрасиля.",
}

SHORT_RESPONSES.update(SHORT_RESPONSES_LATE)

TEXT_REPLACEMENTS: list[tuple[str, str]] = [
    ("Part of a Дигимон?", "Часть дигимона?"),
    ("It could have been a Дигимон.", "Это мог быть дигимон."),
    ("Another Дигимон.", "Другой дигимон."),
    ("Yet another Дигимон.", "Ещё один дигимон."),
    ("Yet another Дигимон still.", "И всё равно другой дигимон."),
    ("Ask another Дигимон?", "Спросить другого дигимона?"),
    ("Are you a Дигимон?", "Ты дигимон?"),
    ("Maybe we can try dressing like Дигимон?", "Может, попробуем одеться как дигимоны?"),
    ("So you're starting with those Дигимон first?", "Значит, начнёшь сначала с этих дигимонов?"),
    ("But they won't be cute anymore if they эволюционировать.", "Но после эволюции они уже не будут милыми."),
    ("Actually, I have a Дигиментал of Sincerity.", "Вообще-то у меня есть Дигиментал Искренности."),
    ("[Hand over the Дигиментал.]", "[Передать Дигиментал.]"),
    ("Use a Дигиатака {r2} on Cherrymon.", "Используйте ДигиАтаку {r2} на Черримоне."),
    ("I'm Sirenmon.", "Я Сиренмон."),
    ("Why not have them fight in the Высотный колизей?", "Почему бы не выпустить их на бой в Высотном колизее?"),
    ("...Атака! Now!", "...В атаку! Сейчас!"),
    ("MWAHAHAHAHAHAHAHAHA!", "МВА-ХА-ХА-ХА-ХА!"),
    ("Kehehe", "Ке-хе-хе"),
    ("Gehe", "Ге-хе"),
    ("Gigigi", "Ги-ги-ги"),
    ("Urgh, touché", "Ух, туше"),
    ("Urk", "Ух"),
    ("Ulp", "Уф"),
    ("Arrrrr", "Ар-р-р"),
    ("Spirit Seeds", "Семена духов"),
    ("Royal Meister", "Роял Мейстер"),
    ("Mach Stinger V", "Мах Стингер V"),
    ("Master &amp; Puppen Trio", "Мастер и трио Пуппен"),
    ("Shinjuku Dungeon", "Подземелья Синдзюку"),
    ("DigiCore", "Дигиядро"),
    ("DIGICORE", "ДИГИЯДРО"),
    ("Analyze", "Анализ"),
    ("Peckmon Races", "гонках Пекмонов"),
    ("Пекмон Races", "гонках Пекмонов"),
    ("Пекмон\nRaces", "гонках Пекмонов"),
    ("гонки Peckmon", "гонки Пекмонов"),
    ("гонки Пекмон", "гонки Пекмонов"),
    ("Peckmon", "Пекмон"),
    ("гонки гонках Пекмонов", "гонки Пекмонов"),
    ("Guardian", "Хранитель"),
    ("Nanimon", "Нанимон"),
    ("Chuumon", "Тюмон"),
    ("PlatinumSukamon", "ПлатинумСкамон"),
    ("PlatinumNumemon", "ПлатинаНумемон"),
    ("Venusmon", "Венусмон"),
    ("Vulcanusmon", "Вулканусмон"),
    ("MarineAngemon", "Маринангемон"),
    ("ShogunGekomon", "СёгунГэкомон"),
    ("Gekomon", "Гэкомон"),
    ("FunBeemon", "Фанбимон"),
    ("Sirenmon", "Сиренмон"),
    ("Pegasusmon", "Пегасмон"),
    ("Datamon", "Датамон"),
    ("MasterBlimpmon", "МастерБлимпмон"),
    ("Blimpmon", "Блимпмон"),
    ("LoaderLeomon", "Лоадер Лиомон"),
    ("Grademon", "Градемон"),
    ("Witchmon", "Витчмон"),
    ("Cherrymon", "Черримон"),
    ("Parallelmon", "Параллельмон"),
    ("Omnimon Alter-S", "Омегамон Alter-S"),
    ("Omnimon Alter-B", "Омегамон Alter-B"),
    ("Omnimon X", "Омегамон X"),
    ("Omnimon", "Омегамон"),
    ("Alphamon", "Альфамон"),
    ("Justimon", "Джастимон"),
    ("Rapidmon", "Рэпидмон"),
    ("Rabbitmon", "Раббитмон"),
    ("WaruSeadramon", "ВарСидрамон"),
    ("MegaSeadramon", "Мега Сидрамон"),
    ("JumboGamemon", "ДжамбоГамемон"),
    ("Mamemon", "Мамемон"),
    ("Guardromon", "Гардромон"),
    ("Gabumon", "Габумон"),
    ("Agumon", "Агумон"),
    ("Gomamon", "Гомамон"),
    ("Gatomon", "Гатомон"),
    ("Tentomon", "Тентомон"),
    ("Patamon", "Патамон"),
    ("Syakomon", "Сякомон"),
    ("Kokuwamon", "Кокувамон"),
    ("Enbarrmon", "Энбаррмон"),
    ("UlforceVeedramon", "Алфорс Ви-драмон"),
    ("Homeros", "Гомерос"),
    ("Factorial Area", "Факториальная область"),
    ("Future me", "Моё будущее я"),
    ("Norio", "Норио"),
    ("Genius Labs", "лаборатория «Гениус»"),
    ("Genius\nLabs", "лаборатория «Гениус»"),
    ("Genius Lab", "лаборатория «Гениус»"),
    ("хромдигизоит ore", "хрондигизоидная руда"),
    ("главного компьютера East", "главного компьютера Востока"),
    ("BLIMPMON", "БЛИМПМОН"),
    ("East!", "Востока!"),
    ("Overbridge", "Овербридж"),
    ("Alpha", "Альфа"),
    ("Gear Forest", "Зубчатого леса"),
    ("Doranoana", "Дораноана"),
    ("Abyss Area", "Область Бездны"),
    ("Waterfall Plaza", "Площадь у водопада"),
    ("Vision Square", "Площадь Вижн"),
    ("Shinjuku AltaVision", "Синдзюку AltaVision"),
    ("Subnade", "Сабнейд"),
    ("Home Expo", "Home Expo"),
    ("OcculTokyo TV", "ОккультТокио ТВ"),
    ("ОккультТокио TV", "ОккультТокио ТВ"),
    ("ОккультТокио ТВ TV", "ОккультТокио ТВ"),
    ("Digivolving", "эволюции"),
    ("De-эволюционировал", "прошёл деволюцию"),
    ("De-эволюционировать", "провести деволюцию"),
    ("Несколько хлопотное дело", "одно хлопотное дело"),
    ("несколько хлопотное дело", "одно хлопотное дело"),
]

TROPHY_TEXT: dict[str, str] = {
    "trophy_name_001": "Первый бой",
    "trophy_name_002": "Тайны конвертации",
    "trophy_name_003": "Признаки аномалии",
    "trophy_name_004": "Инферно Синдзюку",
    "trophy_name_005": "Странник времени",
    "trophy_name_006": "Добро пожаловать в Промежуточный театр",
    "trophy_name_007": "Гость из Цифрового мира",
    "trophy_name_008": "Мир, где живут дигимоны",
    "trophy_name_009": "Короткая передышка",
    "trophy_name_010": "Энергия без перебоев",
    "trophy_name_011": "Одинокий воин",
    "trophy_name_012": "Великий хранитель",
    "trophy_name_013": "Назад в реальный мир...?",
    "trophy_name_014": "Знак мира",
    "trophy_name_015": "Мир в открытом море",
    "trophy_name_016": "Дыхание великого древа",
    "trophy_name_017": "Чемпион SDGP",
    "trophy_name_018": "Чемпион HRCGT",
    "trophy_name_019": "Центральный город возвращён!",
    "trophy_name_020": "Историческая правда",
    "trophy_name_021": "Фигурки решают",
    "trophy_name_022": "Восстановленная связь",
    "trophy_name_023": "Последний свет",
    "trophy_name_024": "Клятва Эгиомона",
    "trophy_name_025": "В далёкий-далёкий мир",
    "trophy_name_026": "Вершина бытия",
    "trophy_name_027": "Мощный удар",
    "trophy_name_028": "Несравненная сила",
    "trophy_name_029": "Первая эволюция",
    "trophy_name_030": "Первая деволюция",
    "trophy_name_031": "Труд окупается",
    "trophy_name_032": "Дебют в карточной битве",
    "trophy_name_033": "Легендарная карта",
    "trophy_name_034": "Тьма пробуждается",
    "trophy_name_035": "За пределами эволюции",
    "trophy_name_036": "Склонности агента",
    "trophy_name_037": "Элитный агент",
    "trophy_name_038": "Большой шлем",
    "trophy_name_039": "Миллионер",
    "trophy_name_040": "Сон или явь?",
    "trophy_name_041": "Все смотрят на меня!",
    "trophy_name_042": "Тихая зависть",
    "trophy_name_043": "Королевские рыцари, сбор!",
    "trophy_name_044": "Исследователь Промежуточного мира",
    "trophy_name_045": "Решатель проблем",
    "trophy_name_046": "Агент совершенства",
    "trophy_explanation_001": "Победите врага впервые.",
    "trophy_explanation_002": "Сконвертируйте дигимона с уровнем сканирования 200%.",
    "trophy_explanation_003": "Станьте свидетелем признаков аномалии.",
    "trophy_explanation_004": "Попадите во взрыв у здания Токийской мэрии.",
    "trophy_explanation_005": "Переместитесь во времени в прошлое.",
    "trophy_explanation_006": "Посетите особое измерение между мирами пространства-времени — Промежуточный мир.",
    "trophy_explanation_007": "Подружитесь с Минервамон.",
    "trophy_explanation_008": "Посетите Цифровой мир.",
    "trophy_explanation_009": "Верните Центральную башню.",
    "trophy_explanation_010": "Восстановите реактор в Факториальной зоне.",
    "trophy_explanation_011": "Изгоните Титанов из Зоны Бездны.",
    "trophy_explanation_012": "Эволюционируйте в Эгиохусмона.",
    "trophy_explanation_013": "Вернитесь в Синдзюку на восемь лет вперёд.",
    "trophy_explanation_014": "Доставьте вино Нептунемону.",
    "trophy_explanation_015": "Перепишите судьбу Зоны Бездны.",
    "trophy_explanation_016": "Перепишите судьбу Шестерённого леса.",
    "trophy_explanation_017": "Станьте чемпионом SDGP.",
    "trophy_explanation_018": "Станьте чемпионом HRCGT.",
    "trophy_explanation_019": "Верните Центральный город.",
    "trophy_explanation_020": "Узнайте правду от Плутомона.",
    "trophy_explanation_021": "Спасите Вулканусмона.",
    "trophy_explanation_022": "Освободите Юномон от заклинания.",
    "trophy_explanation_023": "Зажгите последний свет световых часов.",
    "trophy_explanation_024": "Обновите клятву, которую Эгиомон дал под звёздным небом.",
    "trophy_explanation_025": "Доведите историю до конца.",
    "trophy_explanation_026": "Пройдите игру на сложности «Супер-Абсолютный».",
    "trophy_explanation_027": "Получите оценку EXCELLENT!!! при атаке по слабому месту врага.",
    "trophy_explanation_028": "Победите врага стадии «Совершенный» или выше одной Дигиатакой.",
    "trophy_explanation_029": "Впервые эволюционируйте дигимона.",
    "trophy_explanation_030": "Впервые проведите деволюцию дигимона.",
    "trophy_explanation_031": "Проведите 30 тренировок дигимонов на Дигиферме.",
    "trophy_explanation_032": "Победите в карточной битве.",
    "trophy_explanation_033": "Получите легендарную карту.",
    "trophy_explanation_034": "Эволюционируйте в Эгиохусмона: Тьма.",
    "trophy_explanation_035": "Зарегистрируйте Хрономона: Режим разрушения в энциклопедии.",
    "trophy_explanation_036": "Соберите десять или больше костюмов.",
    "trophy_explanation_037": "Повысьте ранг агента до максимума.",
    "trophy_explanation_038": "Станьте чемпионом Величайшего OMNI-карнавала.",
    "trophy_explanation_039": "Потратьте 1 000 000 йен в магазинах.",
    "trophy_explanation_040": "Соберите все прозвища Хироко Сагисаки.",
    "trophy_explanation_041": "Соберите все фрагменты души Этемона.",
    "trophy_explanation_042": "Соберите все дампы ядра доктора Куги.",
    "trophy_explanation_043": "Призовите всех Королевских рыцарей в Центральную башню.",
    "trophy_explanation_044": "Откройте все Внешние подземелья.",
    "trophy_explanation_045": "Разгадайте все тайны Внешних подземелий.",
    "trophy_explanation_046": "Получите все трофеи.",
    "trophy_explanation_047": "Получите все достижения.",
    "trophy_explanation_048": "Получите все достижения.",
    "activity_001": "Разгадайте аномальные явления.",
    "Subcategory_Name_001": "Основной сюжет",
}

DOMAIN_TERMS = {
    "Valor": "Доблесть",
    "Philanthropy": "Альтруизм",
    "Amicability": "Дружелюбие",
    "Wisdom": "Мудрость",
}

TAMER_EXACT = {
    "Сила Риска Шарм": "Талисман рискованной силы",
    "Brave Blow": "Удар смелости",
    "Brave Perfection": "Совершенство смелости",
    "Zealous Defense": "Ревностная защита",
    "Zealous Perfection": "Совершенство рвения",
    "Daring Wall": "Стена отваги",
    "Daring Perfection": "Совершенство отваги",
    "Adoring Life Charm": "Талисман жизни обожания",
    "Adoring Perfection": "Совершенство обожания",
    "Devoted Treatment": "Преданное лечение",
    "Devoted Perfection": "Совершенство преданности",
    "Tolerant Heart Charm": "Талисман терпимого сердца",
    "Tolerant Perfection": "Совершенство терпимости",
    "Overprotective Perfection": "Совершенство сверхопеки",
    "Overprotective Healing": "Сверхопека: лечение",
    "Compassionate Tool Technique": "Техника заботливого инструмента",
    "Compassionate Perfection": "Совершенство сострадания",
    "Friendly Impulse": "Дружелюбный импульс",
    "Friendly Perfection": "Совершенство дружелюбия",
    "Opportunistic Perfection": "Совершенство находчивости",
    "Opportunistic Rest": "Находчивый отдых",
    "Sociable Tool Reinforcement": "Усиление инструментов общительности",
    "Sociable Perfection": "Совершенство общительности",
    "Astute Blow": "Проницательный удар",
    "Astute Perfection": "Совершенство проницательности",
    "Enlightened Perfection": "Совершенство просветления",
    "Enlightened Enlightenment": "Просветлённое озарение",
    "Sly Perfection": "Совершенство хитрости",
    "Sly Fundraising": "Хитрый сбор средств",
    "Lesson in Rearing": "Урок воспитания",
    "Применение КП: Стратег": "Применение ОА: стратег",
    "Младенец Education": "Обучение стадии «Малыш I»",
    "Ребёнок Education": "Обучение стадии «Ребёнок»",
    "Навык стадии «Взрослый»": "Обучение стадии «Взрослый»",
    "Навык стадии «Совершенный»": "Обучение стадии «Совершенный»",
    "Bond of Strength": "Связь силы",
    "Bond of Support": "Связь поддержки",
    "Bond of Recovery": "Связь восстановления",
}

PREFIX_RE = re.compile(r"^(\{(?:next|end)\})")

changes: list[str] = []


def read_rows(path: Path) -> list[list[str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.reader(f))


def write_rows(path: Path, rows: list[list[str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        csv.writer(f, lineterminator="\r\n").writerows(rows)


def text_column(relative: str, row: list[str]) -> int | None:
    if relative.startswith("message/"):
        return 2 if len(row) > 2 else None
    return 1 if len(row) > 1 else None


def apply_targeted_rows() -> int:
    by_file: dict[str, dict[str, str]] = {}
    for (relative, row_id), value in TARGETED_ROWS.items():
        by_file.setdefault(relative, {})[row_id] = value

    count = 0
    for root in CSV_ROOTS:
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
                old = row[index]
                row[index] = value
                touched = True
                count += 1
                changes.append(f"{root.name}/{relative}:{row[0]}: {old!r} -> {value!r}")
            if touched:
                write_rows(path, rows)
    return count


def apply_short_responses() -> int:
    count = 0
    for root in CSV_ROOTS:
        message_root = root / "message"
        if not message_root.exists():
            continue
        for path in sorted(message_root.rglob("*.csv")):
            relative = path.relative_to(root).as_posix()
            rows = read_rows(path)
            touched = False
            for row in rows[1:]:
                if len(row) <= 2:
                    continue
                old = row[2]
                prefix_match = PREFIX_RE.match(old)
                prefix = prefix_match.group(1) if prefix_match else ""
                body = old[len(prefix) :].strip()
                if body not in SHORT_RESPONSES:
                    continue
                new = f"{prefix}{SHORT_RESPONSES[body]}"
                if old == new:
                    continue
                row[2] = new
                touched = True
                count += 1
                changes.append(f"{root.name}/{relative}:{row[0]}: {old!r} -> {new!r}")
            if touched:
                write_rows(path, rows)
    return count


def apply_text_replacements() -> int:
    count = 0
    for root in CSV_ROOTS:
        for path in sorted(root.rglob("*.csv")):
            relative = path.relative_to(root).as_posix()
            rows = read_rows(path)
            touched = False
            for row in rows[1:]:
                index = text_column(relative, row)
                if index is None:
                    continue
                old = row[index]
                new = old
                for source, target in TEXT_REPLACEMENTS:
                    new = new.replace(source, target)
                if old == new:
                    continue
                row[index] = new
                touched = True
                count += 1
                changes.append(f"{root.name}/{relative}:{row[0]}: {old!r} -> {new!r}")
            if touched:
                write_rows(path, rows)
    return count


def has_cyrillic(text: str) -> bool:
    return bool(re.search(r"[А-Яа-яЁё]", text))


def has_suspicious_latin(text: str) -> bool:
    stripped = re.sub(r"\{[^}]*\}|image\([^)]*\)|ui_[A-Za-z0-9_]+", " ", text)
    for word in re.findall(r"[A-Za-z]{3,}", stripped):
        if word.upper() in {"HP", "SP", "ATK", "DEF", "INT", "SPD", "CRT", "DLC", "DNA", "EXP", "USB"}:
            continue
        if word in {"Digimon", "PlayStation", "Store", "ADAMAS"}:
            continue
        return True
    return False


def sync_app_from_patch() -> int:
    if not APP_ROOT.exists() or not PATCH_ROOT.exists():
        return 0

    count = 0
    for patch_path in sorted(PATCH_ROOT.rglob("*.csv")):
        relative = patch_path.relative_to(PATCH_ROOT).as_posix()
        app_path = APP_ROOT / relative
        if not app_path.exists():
            continue

        patch_rows = read_rows(patch_path)
        app_rows = read_rows(app_path)
        patch_by_id = {row[0]: row for row in patch_rows[1:] if row}
        touched = False

        for row in app_rows[1:]:
            if not row:
                continue
            patch_row = patch_by_id.get(row[0])
            if not patch_row:
                continue
            index = text_column(relative, row)
            if index is None or len(patch_row) <= index:
                continue
            app_text = row[index]
            patch_text = patch_row[index]
            if app_text == patch_text or not has_cyrillic(patch_text):
                continue
            if has_suspicious_latin(app_text) or not has_cyrillic(app_text):
                row[index] = patch_text
                touched = True
                count += 1
                if count <= 300:
                    changes.append(f"sync app_text01/{relative}:{row[0]}")

        if touched:
            write_rows(app_path, app_rows)
    if count > 300:
        changes.append(f"sync app_text01: {count} total rows")
    return count


def sync_app_skill_ruby_from_patch_skill_name() -> int:
    source = PATCH_ROOT / "text/skill_name.mbe/000_Sheet1.csv"
    target = APP_ROOT / "text/skill_ruby.mbe/000_Sheet1.csv"
    if not source.exists() or not target.exists():
        return 0

    source_rows = read_rows(source)
    target_rows = read_rows(target)
    source_by_id = {row[0]: row[1] for row in source_rows[1:] if len(row) > 1 and has_cyrillic(row[1])}
    count = 0
    for row in target_rows[1:]:
        if len(row) <= 1:
            continue
        replacement = source_by_id.get(row[0])
        if not replacement or row[1] == replacement:
            continue
        if has_suspicious_latin(row[1]) or not has_cyrillic(row[1]):
            old = row[1]
            row[1] = replacement
            count += 1
            if count <= 80:
                changes.append(f"skill_ruby sync:{row[0]}: {old!r} -> {replacement!r}")
    if count:
        write_rows(target, target_rows)
    if count > 80:
        changes.append(f"skill_ruby sync: {count} total rows")
    return count


def translate_tamer_skill_name(value: str) -> str:
    if not value:
        return value
    if value in TAMER_EXACT:
        return TAMER_EXACT[value]

    match = re.fullmatch(r"Body Boost Lv\. ([123]): (.+)", value)
    if match:
        return f"Усиление тела ур. {match.group(1)}: {match.group(2)}"

    match = re.fullmatch(r"Body Boost: (.+)", value)
    if match:
        return f"Усиление тела: {match.group(1)}"

    match = re.fullmatch(r"Cross Art: (.+)", value)
    if match:
        cross_art = {
            "Field": "Поле",
            "Burst": "Всплеск",
            "Reverse": "Реверс",
            "Strike": "Удар",
            "Aura": "Аура",
            "High Field": "Высшее поле",
            "Break": "Прорыв",
            "Heal": "Лечение",
            "Revive": "Возрождение",
        }.get(match.group(1), match.group(1))
        return f"Кросс-арт: {cross_art}"

    for english, russian in DOMAIN_TERMS.items():
        replacements = {
            f"Bonds of {english}": f"Связи: {russian}",
            f"Study of {english}": f"Изучение: {russian}",
            f"Peerless Perception: {english}": f"Исключительное чутьё: {russian}",
            f"Awakening Sagacity: {english}": f"Пробуждение мудрости: {russian}",
            f"Sagacious Study: {english}": f"Мудрое обучение: {russian}",
            f"Crash Course in {english}": f"Быстрый курс: {russian}",
            f"Extra Strikes Tech: {english}": f"Техника доп. атак: {russian}",
            f"эволюция of {english}": f"Эволюция: {russian}",
            f"Farm Adaptation: {english}": f"Адаптация фермы: {russian}",
            f"Combat Doctrine: {english}": f"Боевая доктрина: {russian}",
        }
        if value in replacements:
            return replacements[value]

    return value


def apply_tamer_skill_names() -> int:
    count = 0
    for root in CSV_ROOTS:
        path = root / "text/tamer_skill_name.mbe/000_Sheet1.csv"
        if not path.exists():
            continue
        rows = read_rows(path)
        touched = False
        for row in rows[1:]:
            if len(row) <= 1:
                continue
            old = row[1]
            new = translate_tamer_skill_name(old)
            if old == new:
                continue
            row[1] = new
            touched = True
            count += 1
            changes.append(f"{root.name}/text/tamer_skill_name:{row[0]}: {old!r} -> {new!r}")
        if touched:
            write_rows(path, rows)
    return count


def apply_trophy_text() -> int:
    count = 0
    for root in CSV_ROOTS:
        path = root / "text/trophy.mbe/000_Sheet1.csv"
        if not path.exists():
            continue
        rows = read_rows(path)
        touched = False
        for row in rows[1:]:
            if len(row) <= 1:
                continue
            replacement = TROPHY_TEXT.get(row[0])
            if replacement is None or row[1] == replacement:
                continue
            old = row[1]
            row[1] = replacement
            touched = True
            count += 1
            changes.append(f"{root.name}/text/trophy:{row[0]}: {old!r} -> {replacement!r}")
        if touched:
            write_rows(path, rows)
    return count


def main() -> None:
    targeted = apply_targeted_rows()
    short = apply_short_responses()
    fragments = apply_text_replacements()
    synced = sync_app_from_patch()
    skill_ruby = sync_app_skill_ruby_from_patch_skill_name()
    tamer_names = apply_tamer_skill_names()
    trophies = apply_trophy_text()

    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    LOG_PATH.write_text("\n".join(changes) + ("\n" if changes else ""), encoding="utf-8")
    print(
        "Applied translation quality pass v0.25: "
        f"targeted={targeted}, short_responses={short}, fragments={fragments}, "
        f"app_sync={synced}, skill_ruby={skill_ruby}, tamer_names={tamer_names}, trophies={trophies}. "
        f"Log: {LOG_PATH.relative_to(ROOT)}"
    )


if __name__ == "__main__":
    main()

from __future__ import annotations

import csv
import re
from collections import Counter
from pathlib import Path


ROOT = Path("csv/patch_text01")


def has_cyrillic(value: str) -> bool:
    return any(0x0400 <= ord(ch) <= 0x04FF for ch in value)


PHRASES: list[tuple[str, str]] = [
    ("Received{fc9 {d1}} {fc13{d0}Anomaly Points}.", "Получено: {fc9 {d1}} {fc13{d0} очков аномалии}."),
    (
        "No Дигимон that fit the criteria for Auto-Select available.\r\n\r\n"
        "{fc9Note: Only Дигимон at Lv. 1 with no cumulative bonuses will be selected.}",
        "Нет Дигимонов, подходящих под условия авто-выбора.\r\n\r\n"
        "{fc9Примечание: будут выбраны только Дигимоны ур. 1 без накопленных бонусов.}",
    ),
    (
        "No Дигимон that fit the criteria for Auto-Select available.\n\n"
        "{fc9Note: Only Дигимон at Lv. 1 with no cumulative bonuses will be selected.}",
        "Нет Дигимонов, подходящих под условия авто-выбора.\n\n"
        "{fc9Примечание: будут выбраны только Дигимоны ур. 1 без накопленных бонусов.}",
    ),
    (
        "{pf(Add-ons/Add-ons/Downloadable content/Downloadable content)} present in the save data could not be found.\r\n"
        "Please download or purchase the following content again.\r\n\r\n{fc9{d0}}\r\n\r\n"
        "*If the download is in progress, please wait for it to be completed.",
        "{pf(Add-ons/Add-ons/Downloadable content/Downloadable content)} из данных сохранения не найден.\r\n"
        "Скачайте или приобретите следующий контент повторно.\r\n\r\n{fc9{d0}}\r\n\r\n"
        "*Если загрузка уже идет, дождитесь ее завершения.",
    ),
    (
        "{pf(Add-ons/Add-ons/Downloadable content/Downloadable content)} present in the save data could not be found.\n"
        "Please download or purchase the following content again.\n\n{fc9{d0}}\n\n"
        "*If the download is in progress, please wait for it to be completed.",
        "{pf(Add-ons/Add-ons/Downloadable content/Downloadable content)} из данных сохранения не найден.\n"
        "Скачайте или приобретите следующий контент повторно.\n\n{fc9{d0}}\n\n"
        "*Если загрузка уже идет, дождитесь ее завершения.",
    ),
    (
        "{pf(Add-ons/Add-ons/Downloadable content/Downloadable content)} present in the save data could not be found.\r\n\r\n"
        "Returning to the title screen.",
        "{pf(Add-ons/Add-ons/Downloadable content/Downloadable content)} из данных сохранения не найден.\r\n\r\n"
        "Возврат к титульному экрану.",
    ),
    (
        "{pf(Add-ons/Add-ons/Downloadable content/Downloadable content)} present in the save data could not be found.\n\n"
        "Returning to the title screen.",
        "{pf(Add-ons/Add-ons/Downloadable content/Downloadable content)} из данных сохранения не найден.\n\n"
        "Возврат к титульному экрану.",
    ),
    (
        "{fc9Additional Дигимон & Episode Pack 1} is now available.\r\n\r\n"
        "To play this new content, access the {is28}{image(ui_icon_minimap_lobby)} Door of Truth\r\n"
        "in the In-Between Theater.",
        "{fc9Дополнительный набор дигимонов и эпизодов 1} теперь доступен.\r\n\r\n"
        "Чтобы сыграть в новый контент, войдите через {is28}{image(ui_icon_minimap_lobby)} Дверь истины\r\n"
        "в Театре Между Мирами.",
    ),
    (
        "{fc9Additional Дигимон & Episode Pack 2} is now available.\r\n\r\n"
        "To play this new content, access the {is28}{image(ui_icon_minimap_lobby)} Door of Truth\r\n"
        "in the In-Between Theater.",
        "{fc9Дополнительный набор дигимонов и эпизодов 2} теперь доступен.\r\n\r\n"
        "Чтобы сыграть в новый контент, войдите через {is28}{image(ui_icon_minimap_lobby)} Дверь истины\r\n"
        "в Театре Между Мирами.",
    ),
    (
        "{fc9Additional Дигимон & Episode Pack 3} is now available.\r\n\r\n"
        "To play this new content, access the {is28}{image(ui_icon_minimap_lobby)} Door of Truth\r\n"
        "in the In-Between Theater.",
        "{fc9Дополнительный набор дигимонов и эпизодов 3} теперь доступен.\r\n\r\n"
        "Чтобы сыграть в новый контент, войдите через {is28}{image(ui_icon_minimap_lobby)} Дверь истины\r\n"
        "в Театре Между Мирами.",
    ),
    (
        "{fc9Digifarm Item \"\"Golden Moai\"\"} is now available.\r\n\r\n"
        "You can obtain this item by navigating to\r\n"
        "Item > Item Packs on your Digivice.",
        "{fc9Предмет Дигифермы \"\"Золотой моаи\"\"} теперь доступен.\r\n\r\n"
        "Получить его можно через меню\r\n"
        "Предметы > Наборы предметов на вашем Дигивайсе.",
    ),
    (
        "{fc9Special Agumon that can Digivolve into Agumon (Bond of Bravery) &\r\n"
        "Special Gabumon that can Digivolve into Gabumon (Bond of Friendship)}\r\n"
        "are now available.\r\n\r\n"
        "You can obtain these Дигимон by navigating to\r\n"
        "Item > Item Packs on your Digivice.",
        "{fc9Особый Агумон, способный дигиволюционировать в Агумона (Узы храбрости), и\r\n"
        "особый Габумон, способный дигиволюционировать в Габумона (Узы дружбы)}\r\n"
        "теперь доступны.\r\n\r\n"
        "Получить этих Дигимонов можно через меню\r\n"
        "Предметы > Наборы предметов на вашем Дигивайсе.",
    ),
    (
        "{fc9Costume \"\"Public Safety Suit\"\" & Special Supply Set} are now available.\r\n\r\n"
        "You can change into this costume by navigating to\r\n"
        "Agent > Costumes on your Digivice.\r\n\r\n"
        "You can obtain these items by navigating to\r\n"
        "Item > Item Packs on your Digivice.",
        "{fc9Костюм \"\"Форма общественной безопасности\"\" и специальный набор припасов} теперь доступны.\r\n\r\n"
        "Переодеться в этот костюм можно через меню\r\n"
        "Агент > Костюмы на вашем Дигивайсе.\r\n\r\n"
        "Получить эти предметы можно через меню\r\n"
        "Предметы > Наборы предметов на вашем Дигивайсе.",
    ),
    (
        "{fc9Cyber Sleuth BGM Pack} is now available.\r\n\r\n"
        "You can change to this music by navigating to\r\n"
        "System > Music Settings on your Digivice.",
        "{fc9Набор фоновой музыки Cyber Sleuth} теперь доступен.\r\n\r\n"
        "Изменить музыку можно через меню\r\n"
        "Система > Настройки музыки на вашем Дигивайсе.",
    ),
    (
        "{fc9Дигимон Anime Song Pack} is now available.\r\n\r\n"
        "You can change to this music by navigating to\r\n"
        "System > Music Settings on your Digivice.",
        "{fc9Набор песен аниме Digimon} теперь доступен.\r\n\r\n"
        "Изменить музыку можно через меню\r\n"
        "Система > Настройки музыки на вашем Дигивайсе.",
    ),
    (
        "{fc9Outer Dungeons \"\"The Halls of EXP, Gold, & Materials\"\"} \r\n"
        "are now available.\r\n\r\n"
        "To play this new content, talk to Mirei in the In-Between Theater.",
        "{fc9Внешние подземелья \"\"Залы опыта, золота и материалов\"\"} \r\n"
        "теперь доступны.\r\n\r\n"
        "Чтобы сыграть в новый контент, поговорите с Мирэй в Театре Между Мирами.",
    ),
    (
        "{fc9Costume Set \"\"Cyber Sleuth\"\"} is now available.\r\n\r\n"
        "You can change into these costumes by navigating to\r\n"
        "Agent > Costumes on your Digivice.",
        "{fc9Набор костюмов \"\"Cyber Sleuth\"\"} теперь доступен.\r\n\r\n"
        "Переодеться в эти костюмы можно через меню\r\n"
        "Агент > Костюмы на вашем Дигивайсе.",
    ),
    (
        "{fc9Costume Set \"\"Swimwear\"\"} is now available.\r\n\r\n"
        "You can change into these costumes by navigating to\r\n"
        "Agent > Costumes on your Digivice.",
        "{fc9Набор костюмов \"\"Купальники\"\"} теперь доступен.\r\n\r\n"
        "Переодеться в эти костюмы можно через меню\r\n"
        "Агент > Костюмы на вашем Дигивайсе.",
    ),
    (
        "{fc9Costume Set \"\"Chosen Children\"\"} is now available.\r\n\r\n"
        "You can change into these costumes by navigating to\r\n"
        "Agent > Costumes on your Digivice.",
        "{fc9Набор костюмов \"\"Избранные дети\"\"} теперь доступен.\r\n\r\n"
        "Переодеться в эти костюмы можно через меню\r\n"
        "Агент > Костюмы на вашем Дигивайсе.",
    ),
    (
        "{fc9Costume Set \"\"Дигимон Costumes\"\"} is now available.\r\n\r\n"
        "You can change into these costumes by navigating to\r\n"
        "Agent > Costumes on your Digivice.",
        "{fc9Набор костюмов \"\"Костюмы Дигимонов\"\"} теперь доступен.\r\n\r\n"
        "Переодеться в эти костюмы можно через меню\r\n"
        "Агент > Костюмы на вашем Дигивайсе.",
    ),
    (
        "{fc9Agumon (Black), Gabumon (Black)}, \r\n"
        "{fc9Costume \"\"Uniform of a Certain School\"\"} and\r\n"
        "{fc9Adventure Item Set} are now available.\r\n\r\n"
        "You can change into this costume by navigating to\r\n"
        "Agent > Costumes on your Digivice.\r\n\r\n"
        "You can obtain these items by navigating to\r\n"
        "Item > Item Packs on your Digivice.",
        "{fc9Агумон (черный), Габумон (черный)}, \r\n"
        "{fc9костюм \"\"Форма определенной школы\"\"} и\r\n"
        "{fc9набор предметов для приключений} теперь доступны.\r\n\r\n"
        "Переодеться в этот костюм можно через меню\r\n"
        "Агент > Костюмы на вашем Дигивайсе.\r\n\r\n"
        "Получить эти предметы можно через меню\r\n"
        "Предметы > Наборы предметов на вашем Дигивайсе.",
    ),
    (
        "This mode lets you experience an adventure in Central Town, \r\n"
        "located in the middle of the Digital World of Iliad, as well as \r\n"
        "collect, raise and battle Digimon and explore the Digital World.\r\n\r\n"
        "{fc9This mode has no save function and the data cannot be imported into the retail version.}",
        "Этот режим позволяет пережить приключение в Центральном городе, \r\n"
        "расположенном в центре Цифрового мира Илиады, а также \r\n"
        "собирать и растить Дигимонов, сражаться с ними и исследовать Цифровой мир.\r\n\r\n"
        "{fc9В этом режиме нет функции сохранения, а данные нельзя импортировать в полную версию.}",
    ),
    ("Sayori the Cutie Magician", "«Милая волшебница Саёри»"),
    ("Digifarm", "Дигиферма"),
    ("команду tag из", "команду"),
    ('"ide " или "air" моей семьи и друзей', '"гордость" или "дух" моей семьи и друзей'),
    ("ever попадём", "когда-нибудь попадём"),
    ("only в бизнесе", "только в бизнесе"),
    ("pretty уверен", "почти уверен"),
    ("really хотел", "очень хотел"),
    ("Ты must быть", "Ты, должно быть,"),
    ("Если only мы", "Если только мы"),
    ("Geh geh geh", "Гех-гех-гех"),
    ("La la laaa", "Ля-ля-ляя"),
    ("Omni inForce", "Омни-инФорс"),
    ('"Vim and vigor"', '"Бодрость и энергия"'),
    ("В My spot есть все", "В моем заведении есть все"),
    ("за пределами mere здравого смысла", "за пределами простого здравого смысла"),
    ("Так что,\r\nbasically,", "Так что,\r\nпо сути,"),
    ("Так что,\nbasically,", "Так что,\nпо сути,"),
    (", basically, символ", ", по сути, символ"),
    ("действительно confusing", "действительно сбивать с толку"),
    ("остановим fighting", "остановим сражения"),
    ("Зону\r\nnext.", "Зону\r\nдальше."),
    ("Зону\nnext.", "Зону\nдальше."),
    ("grand-вход", "грандиозный выход"),
    ("formidable forces врага", "грозными силами врага"),
    ("machinations Хрономона", "замыслу Хрономона"),
    ("сути the Twentiest", "сути звания «Двадцатого»"),
    ("king of sea", "морском короле"),
    ("future me", "будущей версии себя"),
    ("super sus", "очень подозрительно"),
    ("сочные tips", "сочные наводки"),
    ("называем это \"digi\"", "называем это \"диги\""),
    ("обычно лежали бы dormant", "обычно оставались бы спящими"),
    ("лежали бы dormant", "оставались бы спящими"),
    ("лежавшие dormant", "дремавшие"),
    ("afterimages", "остаточными образами"),
    ("greatest скоростью", "величайшей скоростью"),
    ("highly-", "очень "),
    ("ever-", "вечно-"),
    ("near-", "почти "),
    ("further-", "дальнейше-"),
    ("combat-", "боевой "),
    ("grand-", "грандиозный "),
    ("rapid-fire", "скоростной"),
    ("close-range", "ближнего боя"),
    ("old-fashioned", "старомодный"),
    ("all-out", "полной силы"),
    ("blade-arms", "рук-лезвий"),
    ("highest-ranking", "высшего ранга"),
    ("jet-black", "угольно-черный"),
]


WORDS: dict[str, str] = {
    "extremely": "чрезвычайно",
    "highly": "очень",
    "dramatically": "резко",
    "available": "доступен",
    "now": "теперь",
    "immense": "огромный",
    "pursuit": "погоня",
    "terrifying": "ужасающий",
    "considerable": "значительный",
    "fearsome": "грозный",
    "intense": "интенсивный",
    "formidable": "грозный",
    "countless": "бесчисленные",
    "said": "говорят",
    "yet": "еще",
    "great": "огромный",
    "fully": "полностью",
    "practically": "практически",
    "this": "этот",
    "can": "может",
    "navigating": "перемещаясь",
    "your": "ваш",
    "presumed": "предполагаемый",
    "apparently": "по-видимому",
    "tremendous": "огромный",
    "vast": "обширный",
    "truly": "по-настоящему",
    "fierce": "свирепый",
    "beyond": "за пределами",
    "though": "хотя",
    "appearance": "внешность",
    "reduced": "сниженный",
    "boasts": "может похвастаться",
    "mere": "простой",
    "resulting": "возникший",
    "properly": "как следует",
    "proof": "доказательство",
    "exceptional": "исключительный",
    "presence": "облик",
    "even": "даже",
    "beautiful": "прекрасный",
    "area": "область",
    "very": "очень",
    "bigger": "больше",
    "further": "дальнейший",
    "high": "высокий",
    "directly": "напрямую",
    "eventually": "в итоге",
    "ultimate": "предельный",
    "once": "однажды",
    "mental": "ментальный",
    "attack": "атака",
    "involves": "включает",
    "weapon": "оружие",
    "form": "форма",
    "into": "в",
    "play": "игра",
    "new": "новый",
    "content": "контент",
    "access": "доступ",
    "these": "эти",
    "change": "изменить",
    "platinumnumemon": "ПлатинумНюмемон",
    "only": "только",
    "geh": "гех",
    "laaa": "ляяя",
    "basically": "по сути",
    "forces": "силы",
    "isten": "слушайте",
    "future": "будущая версия",
    "near": "почти",
    "glamor": "очарование",
    "tough": "прочных",
    "primordial": "первозданный",
    "immensely": "невероятно",
    "extreme": "крайний",
    "utmost": "предельный",
    "almost": "почти",
    "shreds": "клочья",
    "absolute": "абсолютный",
    "tend": "склонны",
    "consumed": "поглощенный",
    "rivaling": "соперничающий",
    "well": "хорошо",
    "escape": "сбежать",
    "brandishes": "размахивает",
    "hardly": "едва",
    "firearm": "огнестрельное оружие",
    "occasionally": "иногда",
    "genesis": "зарождение",
    "entirely": "полностью",
    "obliterate": "уничтожить",
    "similar": "похожий",
    "perfectly": "идеально",
    "unimaginable": "невообразимый",
    "alike": "одинаково",
    "shatter": "разрушить",
    "disposition": "нрав",
    "few": "немногие",
    "being": "существо",
    "supreme": "верховный",
    "several": "несколько",
    "capabilities": "способности",
    "steeped": "пропитанный",
    "destroy": "уничтожить",
    "alone": "один",
    "never": "никогда",
    "incomparable": "несравненный",
    "slightly": "слегка",
    "completely": "полностью",
    "live": "живой",
    "composition": "состав",
    "martial": "боевой",
    "range": "дальность",
    "repeated": "повторяющийся",
    "nearby": "рядом",
    "none": "никакой",
    "consume": "поглощать",
    "obtain": "получить",
    "resistance": "сопротивление",
    "hiandromon": "ХайАндромон",
    "ide": "гордость",
    "air": "дух",
    "ever": "когда-либо",
    "pretty": "довольно",
    "really": "очень",
    "must": "должно быть",
    "vigor": "энергия",
    "spot": "место",
    "confusing": "запутанным",
    "fighting": "сражения",
    "machinations": "замыслы",
    "king": "король",
    "sea": "моря",
    "ere": "сюда",
    "digi": "диги",
    "super": "очень",
    "sus": "подозрительно",
    "tips": "наводки",
    "loosely": "примерно",
    "while": "пока",
    "wallop": "удар",
    "explosive": "взрывной",
    "uniquely": "уникально",
    "accomplished": "искусный",
    "ambush": "засада",
    "encasing": "покрывающая",
    "naturally": "от природы",
    "rugged": "крепкий",
    "considerably": "значительно",
    "responsible": "ответственен",
    "fleeing": "убегающий",
    "apparent": "очевидный",
    "little": "маленький",
    "enormous": "огромный",
    "array": "множество",
    "dates": "берет начало",
    "back": "назад",
    "thoroughly": "полностью",
    "lovely": "милый",
    "resilient": "стойкий",
    "giant": "гигантский",
    "disintegrating": "распадающийся",
    "dozens": "десятки",
    "grasp": "схватить",
    "equivalent": "эквивалент",
    "awesome": "впечатляющий",
    "focus": "сосредоточить",
    "glorious": "славный",
    "surging": "бурлящий",
    "whenever": "когда бы ни",
    "credible": "надежный",
    "fail": "провалиться",
    "cultivates": "развивает",
    "miraculously": "чудесным образом",
    "bitter": "горький",
    "continuously": "непрерывно",
    "guard": "охрана",
    "elicits": "вызывает",
    "seldom": "редко",
    "upward": "вверх",
    "incorporates": "включает",
    "finally": "наконец",
    "adverse": "неблагоприятный",
    "charging": "заряжаясь",
    "harsh": "суровый",
    "horrifying": "ужасающий",
    "seems": "кажется",
    "seen": "видимый",
    "resplendent": "сияющий",
    "pursued": "преследуемый",
    "intellect": "интеллект",
    "its": "его",
    "disposal": "распоряжение",
    "bulk": "масса",
    "farthest": "самый дальний",
    "endlessly": "бесконечно",
    "particular": "особенный",
    "whatsoever": "вообще",
    "glitter": "блеск",
    "evidently": "очевидно",
    "supremely": "чрезвычайно",
    "severe": "суровый",
    "nonexistent": "несуществующий",
    "come": "приходить",
    "brute": "грубая",
    "public": "общественный",
    "primitive": "примитивный",
    "unexpectedly": "неожиданно",
    "surprise": "сюрприз",
    "intelligent": "разумный",
    "chronicling": "описывающий",
    "outside": "снаружи",
    "rumored": "по слухам",
    "subsequently": "впоследствии",
    "extended": "расширенный",
    "inconsolable": "безутешный",
    "fundamentally": "в корне",
    "far": "далеко",
    "comparatively": "сравнительно",
    "suited": "подходящий",
    "sizable": "значительный",
    "fuzzy": "пушистый",
    "actually": "на самом деле",
    "farther": "дальше",
    "best": "лучший",
    "level": "уровень",
    "raw": "сырая",
    "merely": "лишь",
    "surprisingly": "удивительно",
    "ushered": "привел",
    "subsequent": "последующий",
    "alignment": "выравнивание",
    "frighteningly": "пугающе",
    "wreaks": "сеет",
    "significantly": "значительно",
    "decay": "разложение",
    "flee": "бежать",
    "extraordinary": "исключительный",
    "incredibly": "невероятно",
    "collapse": "обрушение",
    "mesmerizes": "завораживает",
    "altogether": "совсем",
    "epitome": "воплощение",
    "crush": "сокрушить",
    "channel": "направить",
    "incredible": "невероятный",
    "sheer": "чистая",
    "singlehearted": "целеустремленный",
    "fixated": "зацикленный",
    "scrap": "лом",
    "defeat": "победить",
    "various": "различные",
    "gigantic": "гигантский",
    "weak": "слабый",
    "sizzling": "пылающий",
    "rarely": "редко",
    "many": "многие",
    "akin": "сродни",
    "pulverize": "размолоть",
    "certainty": "уверенность",
    "identifiable": "распознаваемый",
    "wipe": "стереть",
    "out": "прочь",
    "perfect": "идеальный",
    "should": "должен",
    "resetting": "сбрасывая",
    "advanced": "продвинутый",
    "manner": "манера",
    "absolutely": "абсолютно",
    "locked": "заперт",
    "swift": "быстрый",
    "pipe": "ствол",
    "foxes": "лисы",
    "pursue": "преследовать",
    "reappear": "появиться снова",
    "believed": "считается",
    "believes": "считает",
    "ended": "закончил",
    "disavowed": "отрекся",
    "deft": "ловкий",
    "supremacy": "превосходство",
    "straight": "прямой",
    "shines": "сияет",
    "generally": "обычно",
    "nothing": "ничего",
    "radiant": "сияющий",
    "instantly": "мгновенно",
    "excellent": "отличный",
    "risk": "риск",
    "limb": "конечность",
    "lately": "в последнее время",
    "rather": "скорее",
    "aims": "стремится",
    "kinds": "виды",
    "worse": "хуже",
    "contraptions": "приспособления",
    "ammo": "боезапас",
    "ammunition": "боеприпасы",
    "incoming": "входящий",
    "strife": "раздор",
    "gun": "пушка",
    "barrel": "ствол",
    "tight": "плотный",
    "security": "безопасность",
    "infiltrate": "проникнуть",
    "gunport": "амбразура",
    "amalgamation": "слияние",
    "mientras": "пока",
    "data": "данные",
    "repeatedly": "неоднократно",
    "thereby": "тем самым",
    "destruction": "разрушение",
    "revels": "упивается",
    "carnage": "бойня",
    "slaughter": "резня",
    "combat": "бой",
    "discipline": "дисциплина",
    "artist": "мастер",
    "arts": "искусства",
    "harness": "использовать",
    "flight": "полет",
    "unit": "отряд",
    "locking": "фиксируя",
    "violently": "яростно",
    "fires": "стреляет",
    "brittle": "хрупкий",
    "injustice": "несправедливость",
    "savage": "свирепый",
    "fervor": "пыл",
    "firepower": "огневая мощь",
    "fervent": "пылкий",
    "close": "близко",
    "long": "долго",
    "transform": "преобразовать",
    "twisted": "искаженный",
    "sharp": "острый",
    "committed": "преданный",
    "holds": "держит",
    "beam": "луч",
    "damage": "урон",
    "brands": "клеймит",
    "powerful": "мощный",
    "defensive": "защитный",
    "barrier": "барьер",
    "channeling": "направляя",
    "spinning": "вращающийся",
    "slash": "рассечение",
    "finish": "завершить",
    "compelling": "убедительный",
    "slashing": "рубящий",
    "concepts": "понятия",
    "loyal": "верный",
    "concept": "понятие",
    "any": "любой",
    "means": "средства",
    "necessary": "необходимые",
    "leads": "ведет",
    "lasting": "долговременный",
    "through": "через",
    "strength": "сила",
    "ruthless": "безжалостный",
    "compassion": "сострадание",
    "movement": "движение",
    "shockwave": "ударная волна",
    "wishes": "желает",
    "obsessed": "одержим",
    "treats": "считает",
    "else": "еще",
    "astounding": "поразительный",
    "wildly": "дико",
    "coming": "грядущий",
    "inharmonious": "несогласованное",
    "pairing": "сочетание",
    "predicament": "положение",
    "accomplishes": "достигает",
    "enabling": "позволяя",
    "lending": "придавая",
    "crushing": "сокрушительный",
    "overconfident": "самоуверенный",
    "sibling": "собрат",
    "comparable": "сравнимый",
    "shaped": "сформированный",
    "hearty": "сердечный",
    "grand": "грандиозный",
    "excels": "превосходен",
    "multiple": "множественные",
    "designed": "предназначенный",
    "immediately": "немедленно",
    "composed": "состоящий",
    "regenerates": "восстанавливается",
    "commands": "командует",
    "disintegrate": "расщеплять",
    "equipping": "экипируя",
    "releases": "выпускает",
    "vicious": "злобный",
    "devour": "пожирать",
    "solely": "исключительно",
    "relentlessly": "безжалостно",
    "forced": "вынужденный",
    "overpowered": "подавляющий",
    "transforming": "превращая",
    "billowing": "клубящийся",
    "select": "выбрать",
    "assigned": "назначенный",
    "perfectionist": "перфекционист",
    "efficiently": "эффективно",
    "mutual": "взаимный",
    "remarkable": "выдающийся",
    "features": "особенности",
    "thrusting": "пронзая",
    "combined": "объединенный",
    "proceed": "продолжить",
    "that": "что",
    "fit": "соответствуют",
    "criteria": "критериям",
    "for": "для",
    "are": "являются",
    "music": "музыка",
    "costumes": "костюмы",
    "costume": "костюм",
    "items": "предметы",
    "mode": "режим",
    "lets": "позволяет",
    "you": "вам",
    "experience": "испытать",
    "adventure": "приключение",
    "located": "расположен",
    "middle": "середина",
    "collect": "собирать",
    "raise": "выращивать",
    "battle": "сражаться",
    "explore": "исследовать",
    "ramen": "рамен",
    "categorized": "классифицированы",
}


def replace_word(text: str, old: str, new: str) -> tuple[str, int]:
    pattern = re.compile(rf"(?<![A-Za-z]){re.escape(old)}(?![A-Za-z])")
    return pattern.subn(new, text)


def fix_cell(cell: str, counts: Counter[str]) -> str:
    if not has_cyrillic(cell):
        value = cell
        for old, new in PHRASES:
            if old in value:
                n = value.count(old)
                value = value.replace(old, new)
                counts[old] += n
        return value
    value = cell
    for old, new in PHRASES:
        if old in value:
            n = value.count(old)
            value = value.replace(old, new)
            counts[old] += n

    protected: list[str] = []

    def protect(match: re.Match[str]) -> str:
        protected.append(match.group(0))
        return f"__TAG{len(protected) - 1}__"

    value = re.sub(r"\{[^}]*\}", protect, value)
    for old, new in WORDS.items():
        value, n = replace_word(value, old, new)
        if n:
            counts[old] += n
    for index, original in enumerate(protected):
        value = value.replace(f"__TAG{index}__", original)
    value = re.sub(r"[ \t]{2,}", " ", value)
    return value


def main() -> None:
    counts: Counter[str] = Counter()
    changed_files: list[str] = []
    for path in sorted(ROOT.rglob("*.csv")):
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.reader(handle))
        dirty = False
        for row in rows:
            for index, cell in enumerate(row):
                fixed = fix_cell(cell, counts)
                if fixed != cell:
                    row[index] = fixed
                    dirty = True
        if dirty:
            with path.open("w", encoding="utf-8", newline="") as handle:
                csv.writer(handle, lineterminator="\r\n").writerows(rows)
            changed_files.append(str(path))

    Path("logs").mkdir(exist_ok=True)
    with Path("logs/fix_remaining_translation.log").open("w", encoding="utf-8") as handle:
        handle.write(f"changed_files\t{len(changed_files)}\n")
        for file in changed_files:
            handle.write(f"file\t{file}\n")
        handle.write("counts\n")
        for key, count in counts.most_common():
            handle.write(f"{key}\t{count}\n")

    print(f"changed_files {len(changed_files)}")
    print(f"replacement_count {sum(counts.values())}")


if __name__ == "__main__":
    main()

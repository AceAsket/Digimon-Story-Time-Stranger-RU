from __future__ import annotations

import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CSV_ROOTS = [ROOT / "csv" / "patch_text01", ROOT / "csv" / "app_text01"]
LOG_PATH = ROOT / "logs" / "apply_undub_translation_pass_v020.log"
DIRS_PATH = ROOT / "logs" / "apply_undub_translation_pass_v020_dirs.json"


changes: list[str] = []
changed_dirs: set[str] = set()


NAME_REPLACEMENTS = {
    "Агумон (узы храбрости)": "Агумон (Узы храбрости)",
    "Антиламон": "Андиромон",
    "Арукенимон": "Арахнемон",
    "Армадилломон": "Армадимон",
    "МегаКабутеримон": "АтлаКабутеримон",
    "Маломиотизмон": "БелиалВамдемон",
    "ХаосГаллантмон": "ХаосДюкмон",
    "Курисаримон": "Хризалимон",
    "Краниамон": "Краниуммон",
    "Циклонемон": "Цикломон",
    "Диаборомон": "Диабломон",
    "ДоруГреймон": "ДОРУгремон",
    "Эбемон": "ЭБЭмон",
    "Флэймдрамон": "Фладрамон",
    "Гайомон": "Гайоумон",
    "Гаргомон": "Гальгомон",
    "ГраундЛокомон": "ГрандЛокомон",
    "ГрейтГриззлимон": "ГрейтГриззмон",
    "ГеркулесКабутеримон": "ГераклКабутеримон",
    "Фениксмон": "Хоуоумон",
    "Хиогамон": "Хёгамон",
    "Черимон": "Дзюреймон",
    "ШеллНумемон": "КарацукиНумемон",
    "Лиллимон": "Лилимон",
    "Лотосмон": "Лотусмон",
    "Мерукимон": "Меркуримон",
    "Моджьямон": "Моджамон",
    "Датамон": "Наномон",
    "АйсЛеомон": "Панджамон",
    "ПилеВолканомон": "ПайлВолкамон",
    "ПлатинаСукамон": "ПлатинумСкамон",
    "Сукамон": "Скамон",
    "СкулМаммонмон": "СкаллМаммон",
    "МудФригимон": "Цучидарумон",
    "УльтимаБрачиомон": "УльтимейтБрахимон",
    "ВеномМиотисмон": "ВеномВамдемон",
    "Волканомон": "Волкамон",
    "Визардмон": "Визармон",
}


CHAR_NAME_OVERRIDES = {
    "char_AGUMON_KIZUNA": "Агумон (Узы храбрости)",
    "char_ANTYLAMON": "Андиромон",
    "char_ARCHNEMON": "Арахнемон",
    "char_ARMADILLOMON": "Армадимон",
    "char_ATLURKABUTERIMON": "АтлаКабутеримон",
    "char_BEELZEMON_BM": "Вельзевумон: Бласт-режим",
    "char_BEELZEMON_BM_BIG": "Вельзевумон: Бласт-режим",
    "char_BELIALVAMDEMON": "БелиалВамдемон",
    "char_CALAMARAMON": "Каламарамон",
    "char_CHAOSDUKEMON": "ХаосДюкмон",
    "char_KURISARIMON": "Хризалимон",
    "char_CRANIAMON": "Краниуммон",
    "char_CRANIAMON_BIG": "Краниуммон",
    "char_CYCLONEMON": "Цикломон",
    "char_CYCLONEMON_BIG": "Цикломон",
    "char_DIABOROMON": "Диабломон",
    "char_DORUGREYMON": "ДОРУгремон",
    "char_DUKEMON_CM": "Дюкмон: Багровый режим",
    "char_EBEMON": "ЭБЭмон",
    "char_FLAMEDRAMON": "Фладрамон",
    "char_GAIOMON": "Гайоумон",
    "char_GARGOMON": "Гальгомон",
    "char_GROUNDLOCOMON": "ГрандЛокомон",
    "char_GREATGRYZMON": "ГрейтГриззмон",
    "char_HERCULESKABUTERIMON": "ГераклКабутеримон",
    "char_HERCULESKABUTERIMON_BIG": "ГераклКабутеримон",
    "char_HOUOUMON": "Хоуоумон",
    "char_HYOUGAMON": "Хёгамон",
    "char_HYOUGAMON_BOSS": "Хёгамон",
    "char_JESMON": "Джесмон",
    "char_JESMON_BIG": "Джесмон",
    "char_JYUREIMON": "Дзюреймон",
    "char_JYUREIMON_BIG": "Дзюреймон",
    "char_KARATUKINUMEMON": "КарацукиНумемон",
    "char_LILLYMON": "Лилимон",
    "char_LOTOSMON": "Лотусмон",
    "char_MERCURYMON": "Меркуримон",
    "char_MERCURYMON_BIG": "Меркуримон",
    "char_MOJYAMON": "Моджамон",
    "char_NANOMON": "Наномон",
    "char_PANJYAMON": "Панджамон",
    "char_PILEVOLCAMON": "ПайлВолкамон",
    "char_PLATINUM_SCUMON": "ПлатинумСкамон",
    "char_SUKAMON": "Скамон",
    "char_SHAWUJINMON": "Шауджинмон",
    "char_SKULLMAMMON": "СкаллМаммон",
    "char_TUCHIDARUMON": "Цучидарумон",
    "char_ULTIMATEBRAKIMON": "УльтимейтБрахимон",
    "char_ULTIMATEBRAKIMON_BIG": "УльтимейтБрахимон",
    "char_VENOMMYOTISMON": "ВеномВамдемон",
    "char_VENOMMYOTISMON_BIG": "ВеномВамдемон",
    "char_VOLCAMON": "Волкамон",
    "char_WIZARDMON": "Визармон",
}


TERM_REPLACEMENTS = [
    ("DNA De-Digivolution", "джогресс-деволюция"),
    ("DNA Digivolution", "джогресс-эволюция"),
    ("De-Digivolution", "деволюция"),
    ("Digivolutions", "эволюции"),
    ("Digivolution", "эволюция"),
    ("Digivolved", "эволюционировал"),
    ("Digivolve", "эволюционировать"),
    ("Digi-Eggs", "Дигименталы"),
    ("Digi-Egg", "Дигиментал"),
    ("Digimentals", "Дигименталы"),
    ("Digimental", "Дигиментал"),
    ("King Drasil", "Иггдрасиль"),
    ("DigiAttack", "Дигиатака"),
    ("DigiAttacks", "Дигиатаки"),
    ("DigiRide", "ДигиРайд"),
    ("DigiRides", "ДигиРайды"),
    ("DigiRiding", "ДигиРайд"),
    ("DigiFarm", "Дигиферма"),
    ("Digifarm", "Дигиферма"),
    ("DigiMeat", "ДигиМясо"),
    ("Digimeat", "ДигиМясо"),
    ("DigiLine", "ДигиЛиния"),
    ("Digiline", "ДигиЛиния"),
    ("DigiBank", "ДигиБанк"),
    ("Digibank", "ДигиБанк"),
    ("DigiFuse", "ДигиКросс"),
    ("Digifuse", "ДигиКросс"),
    ("Digi-Jewel", "ДигиСамоцвет"),
    ("DigiEgg", "Диги-яйцо"),
    ("In-Training II", "Малыш"),
    ("In-Training I", "Младенец"),
    ("In-Training", "Младенец"),
    ("Rookie", "Ребёнок"),
    ("Champion Team", "Команда чемпионов"),
    ("Champion", "Взрослый"),
    ("Ultimate Collection", "Сильнейшая коллекция"),
    ("Ultimate Digimon", "сильнейший дигимон"),
    ("Mega +", "Супер-Абсолютный"),
    ("Mega+", "Супер-Абсолютный"),
    ("Ultimate", "Совершенный"),
    ("Mega", "Абсолютный"),
    ("Mature Education", "Навык стадии «Взрослый»"),
    ("Complete Education", "Навык стадии «Совершенный»"),
    ("Paradise Colosseum", "Высотный колизей"),
    ("PCGT", "HRCGT"),
    ("Three Celestials", "Три Архангела"),
    ("Omni Blade", "Омега-клинок"),
    ("Omni inForce", "Омега inForce"),
    ("Jindai Technology", "Камисиро Текнолоджи"),
    ("Sorayodo", "Куёдо"),
    ("Digimon Data Squad", "Digimon Savers"),
    ("Digimon Fusion", "Digimon Xros Wars"),
    ("Chrondigizoid", "хромдигизоид"),
    ("Chrondigizoit", "хромдигизоит"),
    ("Chrome Digizoid Metal", "металл хромдигизоид"),
    ("Crystallization", "пикселизация"),
    ("Crystallize", "пикселизация"),
    ("Gamma Device", "Гамма-терминал"),
    ("Alpha Device", "Альфа-терминал"),
    ("Beta Device", "Бета-терминал"),
    ("Final Battle Challenger", "Добровольцы финальной битвы"),
    ("The Helper from Shambala", "Помощники из Шамбалы"),
    ("Mighty Mad Man", "Землетрясение, гром, пожар и отец"),
    ("Ka-medical", "Kamedical"),
    ("Genius Labs", "Genius Lab"),
]


ATTACK_TRANSLATIONS = {
    "Иггдрасиль 7D6 Special Skill 1": "Особый навык Иггдрасиля 7D6 1",
    "Yggdrasil 7D6 Special Skill 1": "Особый навык Иггдрасиля 7D6 1",
    "Совершенный Seibaken": "Совершенный Сэйбакен",
    "Меканоримон is targeting the civilians!": "Меканоримон целится в гражданских!",
    "Дианамон gained more actions!": "Дианамон получила дополнительные действия!",
    "ДигиКросс Skill": "Навык ДигиКросса",
    "Хрономон is staggering!": "Хрономон пошатнулся!",
    "Pursuit": "Преследование",
    "Infinity Dream": "Бесконечный сон",
    "Flying Kick": "Летящий удар ногой",
    "Funny Smile": "Забавная улыбка",
    "Chaos Flare": "Вспышка хаоса",
    "Lampranthus": "Лампрантус",
    "Data Drain": "Поглощение данных",
    "Soul Absorption": "Поглощение души",
    "Prison Fist": "Тюремный кулак",
    "Dot Matrix": "Точечная матрица",
    "Exile Spear": "Копьё изгнания",
    "God Matrix": "Божественная матрица",
    "Dystopia Lances": "Копья Дистопии",
    "Ama no Habakiri": "Ама-но Хабакири",
    "Quo Vadis": "Кво Вадис",
    "Pernicious Waltz": "Гибельный вальс",
    "Quarzione": "Кварционе",
    "Spitfire Blast": "Взрыв Спитфайра",
    "Dark Terra Force": "Тёмная сила Терры",
    "Black Tornado": "Чёрный торнадо",
    "Ice Wolf Claw": "Коготь ледяного волка",
    "Garuru Tomahawk": "Гаруру-томагавк",
    "Famis": "Фамис",
    "Gewalt Schwärmer": "Гевальт Швермер",
    "Der Blitz": "Дер Блиц",
    "Omeka Kick": "Омека-кик",
    "Fire Fist of Shiva": "Кулак Асуры",
    "Grau Lärm": "Грау Лерм",
    "Judgment Arrow": "Стрела правосудия",
    "Matador Dash": "Рывок матадора",
    "Freeze Wave": "Ледяная волна",
    "Thermal Mane": "Термальная грива",
    "Ear Lancer": "Ушное копьё",
    "Down Tornado": "Нисходящий торнадо",
    "Mad Balloon Bomb": "Бомба безумного шара",
    "Nose Blaster": "Носовой бластер",
    "Wool Grenade": "Шерстяная граната",
    "Sonic Ear": "Звуковое ухо",
    "Trident Arm": "Рука-трезубец",
    "Omega Burst": "Омега-взрыв",
    "Gaia Tornado": "Торнадо Геи",
    "Sharp Claymore": "Острый клеймор",
    "Absolute Zero": "Абсолютный ноль",
    "Pendragon's Glory": "Слава Пендрагона",
    "Dragonic Impact": "Драконий удар",
    "All Delete": "Полное удаление",
    "Supreme Cannon": "Высшая пушка",
    "Zeig Saber": "Зиг-сабля",
    "Shield of the Just": "Щит праведника",
    "King Drasil 7D6 Special Skill 1": "Особый навык Иггдрасиля 7D6 1",
    "Vee Лазер": "Ви-лазер",
    "Bubble Blow": "Пузырьковый выдох",
    "Взрыв V-Nova": "Взрыв V-Новы",
    "Mjölnir Thunder": "Гром Мьёльнира",
    "The Ray of Victory": "Луч победы",
    "Victory Sword": "Меч победы",
    "Megadeath": "Мегасмерть",
    "Gigadeath": "Гигасмерть",
    "Positron Laser": "Позитронный лазер",
    "Copy-paste": "Копировать и вставить",
    "Shining Gold Solar Storm": "Сияющая золотая солнечная буря",
    "Plasma Shot": "Плазменный выстрел",
    "Pahorus": "Пахорус",
    "Form Taranis": "Форма Таранис",
    "Flame Hellscythe": "Пламенная коса ада",
    "Demonic Crystal": "Кристалл демона",
    "Fearsome Blade": "Жуткий клинок",
    "Graceful Cannon": "Изящная пушка",
    "Absorbent Bang": "Поглощающий взрыв",
    "Endless Trance": "Бесконечный транс",
    "Zeppelin Explosion": "Взрыв цеппелина",
    "Weltflügel": "Вельтфлюгель",
    "Ultimate Seibaken": "Совершенный Сэйбакен",
    "Imprisonment": "Заточение",
    "Terabyte Disaster": "Терабайтная катастрофа",
    "Distortion Line": "Линия искажения",
    "Death Cloud": "Облако смерти",
    "Dead Scream": "Мёртвый крик",
    "Black Requiem": "Чёрный реквием",
    "Critical Bite": "Критический укус",
    "Thunder of the King": "Гром короля",
    "Bloody Finish": "Кровавый финиш",
    "Depth Charge Sky": "Небесный глубинный заряд",
    "Absolute Territory": "Абсолютная территория",
    "Twin Petal": "Двойной лепесток",
    "Kanshaku Dust": "Кансаку Даст",
    "Yobori Claw Drill": "Когтевой бур Ёбори",
    "Golden Rush": "Золотой натиск",
    "Senbon Dokkan": "Сэнбон Доккан",
    "Acid Bubbles": "Кислотные пузырьки",
    "Hop Attack": "Прыжковая атака",
    "Amethyst Mandala": "Мандала Алмазного мира",
    "Taizoukai Mandala": "Мандала мира чрева",
    "Petra Fire": "Окаменяющий огонь",
    "Chicken Red Eyes": "Красные глаза труса",
    "Final Excalibur": "Последний Экскалибур",
    "Captain Cannon": "Капитанская пушка",
    "Northern Cross Bomber": "Бомбардировка Северного Креста",
    "Nightmare Shock": "Шок кошмара",
    "Zweihänder": "Цвайхендер",
    "Zwei Sieger": "Цвай Зигер",
    "Plasma Stake": "Плазменный кол",
    "Elec Guard": "Электрозащита",
    "Beast Cyclone": "Звериный циклон",
    "Fury: Ice Moon Fang": "Ярость: клык ледяной луны",
    "Supreme Sword": "Высший меч",
    "Transcendent Cannon": "Трансцендентная пушка",
    "Transcendent Sword": "Трансцендентный меч",
    "Zwei Glänze": "Цвай Гленце",
    "Thron Messer": "Трон Мессер",
    "Double Typhoon": "Двойной тайфун",
    "Bit Fire": "Битовый огонь",
    "Little Horn": "Малый рог",
    "Freeze Fang": "Ледяной клык",
    "Full Moon Kick": "Удар полной луны",
    "Eroberung": "Эроберунг",
    "Weltgeist": "Вельтгайст",
    "Pepper Breath": "Малышевое пламя",
    "Aguichant Lèvres": "Агишан Левр",
    "Charité": "Шарите",
    "Divine Pierce": "Божественный пронзающий удар",
    "Protect Wave": "Защитная волна",
    "Divine Pierce (Awake)": "Божественный пронзающий удар (пробуждение)",
    "Protect Wave (Awake)": "Защитная волна (пробуждение)",
    "Mickey Bullet": "Пуля Микки",
    "Bless Fire": "Благословенный огонь",
    "Mickey Bullet (Awake)": "Пуля Микки (пробуждение)",
    "Bless Fire (Awake)": "Благословенный огонь (пробуждение)",
    "Chronos Crop": "Жатва Хроноса",
    "Future Denied": "Отвергнутое будущее",
    "Reversing the Cycle of Time": "Обратный ход времени",
    "Blade of the Dragon King": "Клинок короля драконов",
    "Soul Digitalization": "Оцифровка души",
    "Spiral Masquerade": "Спиральный маскарад",
    "Fist of Athena": "Кулак Афины",
    "Extinction Wave": "Аусстербен",
    "Black Aura Blast": "Эрнсте Велле",
    "Lightning Joust": "Молниеносный турнирный удар",
    "Spirit Boost": "Усиление духа",
    "Intimidate": "Запугивание",
    "Hahahahaha!": "Ха-ха-ха-ха-ха!",
    "Seven's Fantasia": "Фантазия Семи",
    "Wolkenapalm II": "Волькенапальм II",
    "Wolkenapalm III": "Волькенапальм III",
    "Вспыхнувшее Пламя III": "Вспышка пламени III",
    "Падение магмы III": "Магмопад III",
    "Вспышка зажигания III": "Воспламеняющая вспышка III",
    "Давление воды III": "Водяное давление III",
    "Гидро - Вода III": "Гидровода III",
    "Океанская волна III": "Океанская волна III",
    "Приливный поток III": "Приливный поток III",
    "Серповидный Лист III": "Серповидный лист III",
    "Удар шипом III": "Удар шипами III",
    "Рунический Лес III": "Рунический лес III",
    "Игольчатый завод III": "Игольчатое растение III",
    "Край сосульки III": "Ледяная кромка III",
    "Замороженная Пуля III": "Ледяная пуля III",
    "Смертельная Метель III": "Смертельная метель III",
    "Алмазная Пыль III": "Алмазная пыль III",
    "Перерыв в работе наномашины III": "Сбой наномашин III",
    "Ударная плазма III": "Ударная плазма III",
    "Падение Грома III": "Громопад III",
    "Молниеносный Коготь III": "Молниеносный коготь III",
    "Кометный Молот III": "Кометный молот III",
    "Гея Бластер III": "Бластер Геи III",
    "Потрясающее Землетрясение III": "Сокрушительное землетрясение III",
    "Каменный Скол III": "Каменный рассекатель III",
    "Коготь Ветра III": "Коготь ветра III",
    "Звуковой Выстрел III": "Звуковой выстрел III",
    "Штормовой ветер III": "Штормовой ветер III",
    "Буря III": "Буря III",
    "Раздавливающее Лезвие III": "Сокрушительный клинок III",
    "Двигатель Металлический III": "Металлический ускоритель III",
    "Цельнометаллическая свая III": "Цельнометаллический свайный удар III",
    "Железный Разрез III": "Железный кулак III",
    "Святой Кулак III": "Святой кулак III",
    "Святой Свет III": "Святой свет III",
    "Взрыв Блеска III": "Сияющий взрыв III",
    "Лестница Ангела III": "Ангельская лестница III",
    "Теневой Клык III": "Теневой клык III",
    "Кошмар III": "Кошмар III",
    "Адская Дробилка III": "Адский сокрушитель III",
    "Душевный Страх III": "Страх души III",
    "Тяжелый Удар III": "Тяжёлый удар III",
    "Мощность Энергия III": "Силовая энергия III",
    "Пустой Луч III": "Луч пустоты III",
    "Врата Безумия III": "Врата безумия III",
    "Medical Spray DX": "Медицинский спрей DX",
    "Mekanorimon is targeting the civilians!": "Меканоримон целится в гражданских!",
    "The civilians are afraid.": "Гражданские напуганы.",
    "Intercept System 103! Full burst!": "Система перехвата 103! Полный залп!",
    "Good Night Moon": "Луна спокойной ночи",
    "Arrow of Artemis": "Стрела Артемиды",
    "\"Sweet dreams...\"": "«Сладких снов...»",
    "\"I grant you eternal rest.\"": "«Я дарую тебе вечный покой.»",
    "Dianamon gained more actions!": "Дианамон получила дополнительные действия!",
    "Special Right Arm Skill": "Особый навык правой руки",
    "Right arm charge feature halted!": "Заряд правой руки остановлен!",
    "Right arm shorted out!": "Правая рука закорочена!",
    "Right arm is shorted out.": "Правая рука закорочена.",
    "Right arm self-restored!": "Правая рука самовосстановилась!",
    "Special Left Arm Skill": "Особый навык левой руки",
    "Left arm charge feature halted!": "Заряд левой руки остановлен!",
    "Left arm shorted out!": "Левая рука закорочена!",
    "Left arm is shorted out.": "Левая рука закорочена.",
    "Left arm self-restored!": "Левая рука самовосстановилась!",
    "Digifuse Skill": "Навык ДигиКросса",
    "Attack": "Атака",
    "Flash Barrage": "Шквальный обстрел",
    "Raremon's sludge coating is gone!": "Шламовое покрытие Раремона исчезло!",
    "Let's heal those wounds.": "Давай залечим эти раны.",
    "Chronomon is staggering!": "Хрономон пошатнулся!",
}


DIALOGUE_TRANSLATIONS = {
    'When I analyzed them, I discovered they seem to have... evolved. Or "Digivolved," as it were. Apparently, now their name is "Koromon."': 'Анализ показал, что они, похоже... «эволюционировали». Теперь их зовут «Коромон».',
    "Oh, no! My ivy is tangled around the tree.": "О нет! Плющ обвился вокруг дерева.",
    "I can't use my vines with it like that. I've got to do something.": "Из-за этого я не могу пользоваться лианами. Нужно что-то сделать.",
    "They may not look like it, but they're friends! Please, you've got to help them!": "Даже в таком виде они всё ещё мои друзья! Пожалуйста, помоги им!",
    "Run into them to knock them off of Locomon!": "Если коснёшься их, тебя сбросит с Локомона!",
    "Got it. I'll take care of these scumbags.": "Понял. Я с ними разберусь.",
    "[I want to know more about the Digi-Egg.]": "[Поговорить о Дигименталах.]",
    "[Go back to the real world.]": "[Покинуть подземелье.]",
    "Return to the real world?": "Вернуться в предыдущий мир?",
    "If Dr. Yuki, were alive...": "Если бы доктор Юки был жив...",
    'I see why they call ya "Comedimon"!': 'Теперь понятно, почему тебя зовут «Комедимон»!',
    "What a Digi-Monster... No way in hell I'm fightin' that thing!": "Вот это чудовище... Ни за что не стану с ним драться!",
    "Not a drop of red in sight... I-It's back to normal?!": "Красный туман ещё не появился... В-всё вернулось в норму?!",
    "Who are you...?": "Вы...?",
    "What are these...?": "Что это...?",
    'This dynamic duo hates oolong tea! It\'s cuteness to the max, the "Terrier Twins"!': "Максимальная милота! Они не терпят банальности! Близняшки-показушницы, экстремальные когяру!",
    "I'm lowkey starving like a minute ago! Like, let's go grab an EbiBurger after this?": "Я буквально умираю с голоду! Может, потом перекусим в Эбису?",
    "Don't you dare think that you won, here...": "Не вздумай считать, что победил здесь...",
    "It's a little late to ask you this now, but what did you come here for in the first place.": "Поздновато спрашивать, но зачем ты вообще сюда пришёл?",
    "Oh! Hey! You, there! Aren't ya that big rookie from way back when?!": "О! Эй, ты! Разве ты не тот самый знаменитый новичок из тех времён?!",
    "Can't make an omelet without breaking a few Digitamamon, though, right? That's what this plan is all about.": "Отчаянные времена требуют отчаянных мер. В этом и суть плана.",
    "Callismon's body... they couldn't undo the changes...": "Тело Каллисмона... не вернулось в норму...",
    "True. But I think we avoided the worst outcome. As long you're alive, you can always try again...": "Верно. Но худшего исхода мы избежали. Пока его брат жив, всё ещё можно начать сначала...",
    "Despite my results on the IQ test, I can't accept the thought of Yuya as the successor.": "Да, я проиграл тест IQ. Но всё равно не могу смириться с тем, что преемником станет Юя.",
    "I despise them, both Yuya and Simmons.": "Я не могу простить ни Юю, ни Симмонса.",
    "May you roam the world forever as a walking corpse, thanks to the help of this chronolixir.": "Броди по миру вечным живым мертвецом, поддерживаемый этим зельем времени.",
    "Chronomon's curse... his grudge... His bitter resentment at being sealed away...": "Проклятие Хрономона... его злоба...",
    "abonormalities": "аномалии",
    "Not only was Vulcanusmon used as a test subject, but in a true display of horror, his body was assimilated into the weapon.": "Вулканусмона не только использовали как подопытного: часть его тела чудовищным образом встроили в оружие.",
    "It'd snuff this fire right out! Let's go snag one!": "Ледяное семя сразу потушит этот огонь! Пойдём раздобудем одно!",
    "Darn! This isn't where I parked my Digi Beetle!": "Чёрт! Мы не туда попали!",
    'That being was Aegiomon, or the "dark shadow."': "Тем существом была «тёмная тень».",
    "But is that really what you want?": "Но... ты правда уверен?",
    "I am GraceNovamon!": "ГрейсНовамон!",
    "Okay... I'm sorry... but... ...thank you!": "Понятно... Прости... и... ...спасибо!",
    "Hmm... Could it be... we pulled out that whole, entire moment...?": "Понятно... Неужели мы вытащили тот самый момент целиком...?",
    "Uh... Oh, I remember! She was dressed in a costume just like your friend's, there.": "А... Точно, вспомнил! На ней был наряд, похожий на тот, что несёт этот человек!",
    "Like my friend's? That should make things easier... Put this on and walk over there.": "Так... Вот этот, значит? Отлично. Надень его и походи по округе.",
    "If someone walked around the park wearing this...": "Если я пройдусь по парку в этом...",
    "Thanks! We'll try walking around the park in the Chosen Children outfit, then.": "Спасибо за сведения! Тогда попробуем пройтись по парку в костюме Избранных детей.",
    "Let's try walking around the park in the Chosen Children outfit.": "Пройдись по парку в костюме Избранных детей.",
    "Hmm... I wonder if they're capable of taking on Mercurymon?": "Хм. Значит... мы сможем скрестить клинки с Меркуримоном?",
    "Yes, the more we have searching, the better! We can definitely use your help!": "Да, чем больше людей ищут, тем лучше! Твоя помощь нам точно пригодится!",
    "This one was displayed right in front. So, without further ado, let the screening begin!": "Этот экземпляр стоял на самом видном месте. Итак, без лишних слов, начинаем показ!",
    "Sayori the Cutie Magician": "Милая волшебница Саёри",
    "Genius Labs": "Genius Lab",
    "When I finally came to, it was eight years later... or so it seemed.": "Когда он наконец очнулся, прошло восемь лет... или ему так показалось.",
    "It must be hard living in a time different from your own. We've got to get you home.": "Наверное, тяжело жить не в своём времени. Нужно вернуть его домой.",
    "You can't always tell, though. Now, head to the rendezvous point with Agumon and the others.": "Но наверняка не скажешь. А теперь отправляйся к месту встречи с Агумоном и Габумоном.",
    "Humans, together let us defeat GranKuwagamon": "Человек, давай вместе одолеем ГранКувагамона",
    "It is a pleasure to find humans who are so quick to understand. Down with GranKuwagamon!": "Приятно встретить человека, который так быстро всё понимает. Долой ГранКувагамона!",
    "Stop talking already and just leave it to the rest of us!": "Хватит болтать!",
    "Kamemon's medical team": "Команда Kamedical",
    "And Nani the who are you?": "А ты ещё что за Нанимон?!",
    "Eh, Whatever!": "Эх, неважно!",
    "Anybody else probably would've ended up ending me. But because it was you, I managed to hang in there for a while.": "Кто-нибудь послабее, наверное, погиб бы, но ты оказался достаточно силён, чтобы выстоять.",
    "Ah, welcome. You...": "А, добро пожаловать. Ты, должно быть...",
    "...Are who exactly?": "...Ты меня не знаешь?",
}


TOKEN_REPLACEMENTS = {
    "Mekanorimon": "Меканоримон",
    "Dianamon": "Дианамон",
    "Chronomon": "Хрономон",
    "GraceNovamon": "ГрейсНовамон",
    "GranKuwagamon": "ГранКувагамон",
    "Mercurymon": "Меркуримон",
    "Callismon": "Каллисмон",
    "Aegiomon": "Эгиомон",
    "Locomon": "Локомон",
    "Koromon": "Коромон",
    "Palmon": "Палмон",
    "Agumon": "Агумон",
    "Gabumon": "Габумон",
}


LATIN_ALLOWED_RE = re.compile(
    r"^(?:[A-Z]{1,4}|DX|7D6|HRCGT|Kamedical|Genius Lab|Digimon(?: [A-Za-z]+)*|Xros|inForce)$"
)


def read_rows(path: Path) -> list[list[str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.reader(f))


def write_rows(path: Path, rows: list[list[str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        csv.writer(f, lineterminator="\n").writerows(rows)


def mark_changed(path: Path, detail: str) -> None:
    rel = path.relative_to(ROOT).as_posix()
    changes.append(f"{rel}: {detail}")
    changed_dirs.add(str(path.parent.relative_to(ROOT)).replace("/", "\\"))


def should_skip_value(value: str) -> bool:
    return value.startswith("char_")


def replace_many(
    text: str,
    replacements: dict[str, str] | list[tuple[str, str]],
    *,
    whole_word_ascii: bool = False,
) -> str:
    items = replacements.items() if isinstance(replacements, dict) else replacements
    for old, new in items:
        if whole_word_ascii and re.search(r"[A-Za-z]", old):
            pattern = re.compile(rf"(?<![A-Za-z_]){re.escape(old)}(?![A-Za-z_])")
            text = pattern.sub(new, text)
        else:
            text = text.replace(old, new)
    return text


def normalize_case(text: str) -> str:
    # Keep technical tags intact, but clean common Russian capitalization artifacts.
    replacements = [
        ("Кросс-арт: Высшее поле", "Кросс-арт: Высшее поле"),
        ("Дополнительные Удары", "Дополнительные удары"),
        ("Элементальный Потрошитель", "Элементальный потрошитель"),
        ("Элементальный Занавес", "Элементальный занавес"),
        ("Разрушение от Упадка", "Разрушение упадком"),
        ("Связывание Ядом", "Связывание ядом"),
        ("Панический страх Связывает", "Связывание паникой"),
        ("Паралич Связывает", "Связывание параличом"),
        ("Привязка ко сну", "Связывание сном"),
        ("Очень Смелый", "Сверхсмелость"),
    ]
    return replace_many(text, replacements)


def apply_global_replacements() -> None:
    replacements = []
    replacements.extend(sorted(NAME_REPLACEMENTS.items(), key=lambda item: len(item[0]), reverse=True))
    replacements.extend(TERM_REPLACEMENTS)
    replacements.extend(sorted(TOKEN_REPLACEMENTS.items(), key=lambda item: len(item[0]), reverse=True))
    for root in CSV_ROOTS:
        if not root.exists():
            continue
        for path in sorted(root.rglob("*.csv")):
            rows = read_rows(path)
            updated = False
            for row in rows:
                for idx in range(1, len(row)):
                    if should_skip_value(row[idx]):
                        continue
                    old = row[idx]
                    new = replace_many(old, replacements, whole_word_ascii=True)
                    new = normalize_case(new)
                    if new != old:
                        row[idx] = new
                        updated = True
            if updated:
                write_rows(path, rows)
                mark_changed(path, "global replacements")


def set_values(path: Path, values: dict[str, str], column: int = 1) -> None:
    rows = read_rows(path)
    updated = False
    for row in rows:
        if len(row) <= column:
            continue
        key = row[0]
        if key in values and row[column] != values[key]:
            old = row[column]
            row[column] = values[key]
            updated = True
            mark_changed(path, f"{key}: {old!r} -> {values[key]!r}")
    if updated:
        write_rows(path, rows)


def apply_name_overrides() -> None:
    for root in CSV_ROOTS:
        path = root / "text" / "char_name.mbe" / "000_Sheet1.csv"
        if path.exists():
            set_values(path, CHAR_NAME_OVERRIDES, column=1)


def read_key_values(path: Path, column: int = 1) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values
    for row in read_rows(path):
        if len(row) > column and row[0] != "string2 0":
            values[row[0]] = row[column]
    return values


def apply_jogress_skill_names() -> None:
    jogress_path = ROOT / "csv" / "app_text01" / "text" / "jogress_skill_name.mbe" / "000_Sheet1.csv"
    skill_path = ROOT / "csv" / "patch_text01" / "text" / "skill_name.mbe" / "000_Sheet1.csv"
    skill_names = read_key_values(skill_path)
    rows = read_rows(jogress_path)
    updated = False
    latin_re = re.compile(r"[A-Za-z]{3,}")
    roman_re = re.compile(r"\b[IVXLCDM]+\b")
    for row in rows:
        if len(row) < 2 or row[0] == "string2 0":
            continue
        old = row[1]
        new = old
        skill_value = skill_names.get(row[0])
        if skill_value and not latin_re.search(roman_re.sub("", skill_value)):
            new = skill_value
        new = ATTACK_TRANSLATIONS.get(new, new)
        new = normalize_case(new)
        if new != old:
            row[1] = new
            updated = True
            mark_changed(jogress_path, f"{row[0]}: {old!r} -> {new!r}")
    if updated:
        write_rows(jogress_path, rows)


def build_text_index(app_root: Path, target_root: Path) -> dict[str, list[tuple[Path, str, int]]]:
    index: dict[str, list[tuple[Path, str, int]]] = {}
    if not app_root.exists():
        return index
    for path in sorted(app_root.rglob("*.csv")):
        rel = path.relative_to(app_root)
        target_path = target_root / rel
        for row in read_rows(path):
            for idx in range(1, len(row)):
                index.setdefault(row[idx], []).append((target_path, row[0], idx))
    return index


def choose_target_path(app_path: Path) -> Path:
    rel = app_path.relative_to(ROOT / "csv" / "app_text01")
    patch_path = ROOT / "csv" / "patch_text01" / rel
    return patch_path if patch_path.exists() else app_path


def set_row_value(path: Path, key: str, column: int, value: str) -> bool:
    rows = read_rows(path)
    updated = False
    for row in rows:
        if len(row) > column and row[0] == key:
            if row[column] != value:
                old = row[column]
                row[column] = value
                updated = True
                mark_changed(path, f"{key}: {old!r} -> {value!r}")
            break
    if updated:
        write_rows(path, rows)
    return updated


def apply_dialogue_rows() -> None:
    app_root = ROOT / "csv" / "app_text01"
    index = build_text_index(app_root, app_root)
    original_app_root = ROOT / "verify" / "current_payload_v0_1_9" / "csv" / "app_text01.dx11"
    for text, matches in build_text_index(original_app_root, app_root).items():
        index.setdefault(text, []).extend(matches)

    for source, ru_text in DIALOGUE_TRANSLATIONS.items():
        matches = index.get(source, [])
        if not matches:
            # Some rows may already have been rewritten by term replacements.
            continue
        for app_path, key, col in matches:
            if not app_path.exists():
                continue
            target = choose_target_path(app_path)
            set_row_value(target, key, col, ru_text)


def apply_attack_phrase_replacements() -> None:
    # Also replace attack names in profiles/chats where they are mentioned as text.
    replacements = sorted(ATTACK_TRANSLATIONS.items(), key=lambda item: len(item[0]), reverse=True)
    for root in CSV_ROOTS:
        for path in sorted(root.rglob("*.csv")):
            rows = read_rows(path)
            updated = False
            for row in rows:
                for idx in range(1, len(row)):
                    if should_skip_value(row[idx]):
                        continue
                    old = row[idx]
                    new = replace_many(old, replacements, whole_word_ascii=True)
                    if new != old:
                        row[idx] = new
                        updated = True
            if updated:
                write_rows(path, rows)
                mark_changed(path, "attack phrase replacements")


def main() -> None:
    apply_global_replacements()
    apply_name_overrides()
    apply_jogress_skill_names()
    apply_attack_phrase_replacements()
    apply_dialogue_rows()

    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    LOG_PATH.write_text("\n".join(changes) + ("\n" if changes else ""), encoding="utf-8")
    DIRS_PATH.write_text(
        json.dumps(sorted(changed_dirs), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"changed entries: {len(changes)}")
    print(f"changed dirs: {len(changed_dirs)}")
    print(f"log: {LOG_PATH}")
    print(f"dirs: {DIRS_PATH}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Normalize source-confirmed Digimon skill and attack names.

The pass follows the English row attached to each table, not just its numeric
ID.  This matters for DLC 02, where two source tables assign Kanshaku Dust and
Yobori Claw Drill to opposite IDs.  It also makes the pass safe to rerun.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = ROOT / "verify/game_build_23514637/text_original"


@dataclass(frozen=True)
class Table:
    label: str
    target: Path
    source: Path


TABLES = [
    Table(
        "base_skill",
        ROOT / "csv/patch_text01/text/skill_name.mbe/000_Sheet1.csv",
        SOURCE_ROOT / "patch_text01/csv/text/skill_name.mbe/000_Sheet1.csv",
    ),
    Table(
        "base_jogress",
        ROOT / "csv/patch_text01/text/jogress_skill_name.mbe/000_Sheet1.csv",
        SOURCE_ROOT / "app_text01/csv/text/jogress_skill_name.mbe/000_Sheet1.csv",
    ),
    Table(
        "base_ruby",
        ROOT / "csv/patch_text01/text/skill_ruby.mbe/000_Sheet1.csv",
        SOURCE_ROOT / "app_text01/csv/text/skill_ruby.mbe/000_Sheet1.csv",
    ),
]
for dlc in ("01", "02", "03"):
    for kind in ("skill", "jogress_skill"):
        filename = f"{kind}_name_dlc{dlc}.mbe/000_Sheet1.csv"
        TABLES.append(
            Table(
                f"dlc{dlc}_{kind}",
                ROOT / f"csv/addcont_{dlc}_text01/text/{filename}",
                SOURCE_ROOT / f"addcont_{dlc}_text01/csv/text/{filename}",
            )
        )


# The English game deliberately presents these as three tiers of one attack.
# Russian wording and capitalization must therefore stay identical apart from
# the Roman numeral.
SERIES_BASES = {
    "Angel Ladder": "Ангельская лестница",
    "Aqua Pressure": "Водяное давление",
    "Awesome Quake": "Сокрушительное землетрясение",
    "Burst Flame": "Вспышка пламени",
    "Comet Hammer": "Кометный молот",
    "Crescent Leaf": "Серповидный лист",
    "Crush Blade": "Сокрушительный клинок",
    "Diamond Dust": "Алмазная пыль",
    "Frozen Bullet": "Ледяная пуля",
    "Full Metal Pile": "Цельнометаллический свайный удар",
    "Gaia Blaster": "Бластер Геи",
    "Gale Storm": "Штормовой ветер",
    "Heavy Strike": "Тяжёлый удар",
    "Hell Crusher": "Адский сокрушитель",
    "Holy Light": "Святой свет",
    "Hydro Water": "Гидропоток",
    "Icicle Edge": "Ледяная кромка",
    "Ignition Flare": "Пламенный всполох",
    "Iron Slash": "Железный разрез",
    "Lethal Blizzard": "Смертельная метель",
    "Lightning Claw": "Молниеносный коготь",
    "Lunatic Gate": "Врата безумия",
    "Magma Fall": "Магмопад",
    "Nanomachine Break": "Сбой наномашин",
    "Needle Plant": "Игольчатое растение",
    "Nightmare": "Кошмар",
    "Ocean Wave": "Океанская волна",
    "Power Energy": "Силовая энергия",
    "Rune Forest": "Рунический лес",
    "Saint Knuckle": "Святой кулак",
    "Shadow Fang": "Теневой клык",
    "Shine Burst": "Сияющий взрыв",
    "Shock Plasma": "Ударная плазма",
    "Sonic Shot": "Звуковой выстрел",
    "Soul Fear": "Страх души",
    "Stone Cleave": "Каменный раскол",
    "Tempest": "Буря",
    "Thorn Strike": "Удар шипами",
    "Thruster Metal": "Металлический ускоритель",
    "Thunder Fall": "Громопад",
    "Tidal Stream": "Приливный поток",
    "Void Ray": "Луч пустоты",
    "Wind Claw": "Коготь ветра",
    "Wolkenapalm": "Облачный напалм",
}

# Two English skill_ruby rows contain stock spelling/name mistakes.  They use
# the same IDs as the correctly named main table and must follow that family.
SERIES_ALIASES = {
    "Iron Fist": "Iron Slash",
    "Thron Strike": "Thorn Strike",
}


# Exact English names shared by the base game and DLC should have one Russian
# equivalent.  The DLC 02 pair is resolved by English name because its IDs are
# swapped between skill_name and jogress_skill_name in the original assets.
EXACT_NAMES = {
    "Fearsome Blade": "Грозный клинок",
    "Graceful Cannon": "Изящная пушка",
    "Kanshaku Dust": "Пыль Кансяку",
    "Shield of the Just": "Щит праведника",
    "Shining Gold Solar Storm": "Сияющая золотая солнечная буря",
    "Sub-Zero Ice Punch": "Ледяной удар абсолютного нуля",
    "Supreme Cannon": "Высшая пушка",
    "Transcendent Sword": "Трансцендентный меч",
    "Victory Sword": "Меч победы",
    "Yobori Claw Drill": "Когтевой бур Ёбори",
}


# Manually reviewed literal/machine translations.  These are intentionally
# keyed by the English source so duplicate skill and jogress rows stay equal.
# Foreign proper names which are merely unusual are left untouched.
HUMANIZED_NAMES = {
    "A BlackKingNumemon has appeared!": "Появился БлэкКингНумемон!",
    "A PlatinumNumemon has appeared!": "Появился ПлатинаНумемон!",
    "Accel Arm": "Ускоряющая рука",
    "Adhesive Bubble Blow": "Клейкие пузыри",
    "Air Bubbles": "Воздушные пузыри",
    "Ambush Crunch": "Укус из засады",
    "Animal Nail": "Звериный коготь",
    "Appropriate Works": "Оружие на все случаи",
    "Atomic Inferno": "Атомное инферно",
    "Attack Bind": "Ослабление атаки",
    "Attack Break": "Массовое ослабление атаки",
    "Attack Charge": "Усиление атаки",
    "Attack Field": "Массовое усиление атаки",
    "Aurora Blaster": "Бластер «Аврора»",
    "Baby Breath": "Детское дыхание",
    "Bifrost": "Биврёст",
    "Bite": "Укус",
    "Biting Crush": "Сокрушительный укус",
    "Blitz Arm": "Блиц-рука",
    "Bloody Finish": "Кровавый финал",
    "Black Rain": "Чёрный дождь",
    "Blight Break": "Пробой скверны",
    "Blinded": "Ослепление",
    "Boost Charge": "Усиливающий заряд",
    "Boost Cheer": "Усиливающее подбадривание",
    "Boost Link": "Усиливающая связь",
    "Bowling Storm": "Боулинг-шторм",
    "Brachio Bubble": "Брахио-пузырь",
    "Branch Drain": "Высасывающая ветвь",
    "Brave Metal": "Храбрый металл",
    "Bramble Bite": "Терновый укус",
    "Bunny Blades": "Кроличьи клинки",
    "Catastrophe Cannon": "Пушка-катастрофа",
    "Chaos Degradation": "Деградация хаоса",
    "Cheer of Energy": "Энергетическая поддержка",
    "Cheer of Regeneration": "Поддержка регенерации",
    "Chrono Devolution": "Хроно-деволюция",
    "Circlet Defense": "Защита обручем",
    "Confusion unto Despair": "Смятение до отчаяния",
    "Cool Edge": "Холодная кромка",
    "Corona Blaze Sword": "Пламенный меч короны",
    "Critical Arm": "Критическая рука",
    "Critical Bind": "Ослабление критического удара",
    "Critical Break": "Массовое ослабление критического удара",
    "Critical Charge": "Усиление критического удара",
    "Critical Field": "Массовое усиление критического удара",
    "Cross Blade": "Крестовый клинок",
    "Damaged by skill recoil!": "Урон от отдачи навыка!",
    "Dark Explosion": "Тёмный взрыв",
    "Dark Prominence": "Тёмный протуберанец",
    "Darkside Quake": "Землетрясение тёмной стороны",
    "Daredevil Break": "Пробой сорвиголовы",
    "Dead Angle Horn": "Рог мёртвой зоны",
    "Dead or Alive": "Живой или мёртвый",
    "Demi Darts": "Малые дротики",
    "Depth Charge Sky": "Небесная глубинная бомба",
    "Destruction Crush": "Разрушительный удар",
    "Destroyed Rush": "Разрушительный натиск",
    "Dimension Scissor": "Пространственные ножницы",
    "Disaster Blaster": "Бластер катастрофы",
    "Dispel": "Рассеивание",
    "Dios Thunder": "Гром Диоса",
    "DJ Shooter": "Диджей-шутер",
    "Double Backhand": "Двойной удар тыльной стороной",
    "Downward Cleave": "Нисходящий разрез",
    "Dumdum Uppercut": "Апперкот «Дам-дам»",
    "EDEN's Javelin": "Копьё ЭДЕНа",
    "Exhaust Flame": "Выхлопное пламя",
    "Extra Brave": "Дополнительная отвага",
    "Final Crest": "Последний герб",
    "Final Mirage Burst": "Последний миражный взрыв",
    "Final Shining Burst": "Последний сияющий взрыв",
    "Flame Dive": "Пламенное пикирование",
    "Flame Inferno": "Пламенное инферно",
    "Flashy Boss Punch": "Эффектный удар босса",
    "Fly Bullet": "Летящая пуля",
    "Fox Tail Inferno": "Инферно лисьего хвоста",
    "Full Moon Blaster": "Бластер полной луны",
    "Full Moon Meteor Impact": "Метеоритный удар полной луны",
    "Future Denied": "Будущего не будет",
    "Gear Stinger": "Шестерёнчатое жало",
    "GeoGrey Sword": "Меч Гео Грея",
    "Giga Blaster": "Гига-бластер",
    "Giga Death": "Гигасмерть",
    "Giga Destroyer": "Гига-разрушитель",
    "Gigastick Lance": "Копьё «Гигастик»",
    "Glare Eye": "Слепящий взгляд",
    "Good Night Moon": "Спокойной ночи, Луна",
    "Guard Bind": "Ослабление защиты",
    "Guard Break": "Массовое ослабление защиты",
    "Guard Charge": "Усиление защиты",
    "Guard Field": "Массовое усиление защиты",
    "Happy Bullet Showering": "Счастливый ливень пуль",
    "Hard Rock Soul": "Хард-рок-душа",
    "Harden": "Закалка",
    "Hearts Attack": "Атака сердец",
    "Heavy Metal Fire": "Огонь тяжёлого металла",
    "Heal": "Исцеление",
    "Horn Buster": "Роговой сокрушитель",
    "Hyper Heat": "Сверхжар",
    "Hyper Infinity Cannon": "Гиперпушка бесконечности",
    "Hyper Smell": "Сверхвонь",
    "Infinity Arrow": "Стрела бесконечности",
    "Inferno Divide": "Рассечение инферно",
    "Island Freefall": "Свободное падение острова",
    "Justice Kick": "Пинок правосудия",
    "Judgment of the Blade": "Суд клинка",
    "Keraunos Divide": "Рассечение Керавном",
    "Knuckle Beater": "Костоломный кулак",
    "Kouyoujou: Hydro Descent": "Коёдзё: гидроспуск",
    "Legendary Dragon Blade": "Клинок легендарного дракона",
    "Lila Shower": "Сиреневый ливень",
    "Lightning Joust": "Молниеносный выпад",
    "Lightning Pile": "Громовая свая",
    "Lion Slash": "Львиный разрез",
    "Little Iron Beads": "Малые железные шарики",
    "Magic Bind": "Ослабление магии",
    "Magic Break": "Массовое ослабление магии",
    "Magic Charge": "Усиление магии",
    "Magic Field": "Массовое усиление магии",
    "Machine Gun Punch": "Пулемётный удар",
    "Machinegun Destroyer": "Пулемётный разрушитель",
    "Maul Attack": "Удар булавой",
    "Meditator": "Медитация",
    "Mega Burst": "Мегавзрыв",
    "Mega Death": "Мегасмерть",
    "Mega Flame": "Мегапламя",
    "Mental Break": "Массовое ослабление духа",
    "Mental Charge": "Усиление духа",
    "Mental Field": "Массовое усиление духа",
    "Miracle Bomb": "Чудо-бомба",
    "Misery Bullet Rain": "Дождь пуль отчаяния",
    "Mystic Break": "Мистический пробой",
    "Nail Bone": "Костяной коготь",
    "Nail Scratch": "Царапина когтем",
    "Necromist": "Некротуман",
    "Normalize": "Нормализация",
    "Ocean Love": "Любовь океана",
    "Omni Blade": "Омни-клинок",
    "Oxygen Homing": "Самонаводящийся кислород",
    "Pandemonium Lost": "Утраченный пандемониум",
    "Party of the Heavens": "Небесная вечеринка",
    "Phosphorus Fire Attack": "Атака фосфорным огнём",
    "Pinpoint Weapon Works": "Оружие точно в цель",
    "Pit Bomb": "Яма-бомба",
    "Plasmadness": "Плазмобезумие",
    "Poop Dunk": "Какашечный данк",
    "Powered Ignition": "Форсированное зажигание",
    "Pretty Attack": "Милая атака",
    "Pummel": "Град ударов",
    "Pummel Peck": "Дробящий клевок",
    "Pummel Whack": "Молотящий удар",
    "Punish Judge": "Карающий суд",
    "Pyro Punch": "Огненный удар",
    "Rejection of All Order": "Отрицание всякого порядка",
    "Regeneration Charge": "Заряд регенерации",
    "Restore": "Восстановление",
    "Restoring...": "Восстановление...",
    "Revive": "Возрождение",
    "Rolling Tackle": "Катящийся таран",
    "Rodeo Bullet": "Пуля родео",
    "Rock Soul": "Рок-душа",
    "Ruthless Charge": "Безжалостный натиск",
    "Safety Guard": "Защитный барьер",
    "Scissors Execution": "Казнь ножницами",
    "Scrapless Claw": "Сокрушающий коготь",
    "Serpent Cure": "Змеиное исцеление",
    "Seven's Fantasia": "Фантазия семи",
    "Shine of Bee": "Пчелиное сияние",
    "Sludge": "Ил",
    "Smile Fang": "Улыбающийся клык",
    "Sorrow Blue": "Синяя печаль",
    "Soul Digitalization": "Оцифровка души",
    "Soul-Piercing Snaketail": "Пронзающий душу змеиный хвост",
    "Speed Bind": "Ослабление скорости",
    "Speed Break": "Массовое ослабление скорости",
    "Speed Charge": "Усиление скорости",
    "Speed Field": "Массовое усиление скорости",
    "Spider Shooter": "Паучий стрелок",
    "Spirit Bind": "Ослабление духа",
    "Spiritual Enchantment": "Духовные чары",
    "Sticker Blade": "Клинок-наклейка",
    "Strike Fishing": "Ударная рыбалка",
    "Strike Roll": "Ударный перекат",
    "Summon": "Призыв",
    "Tenryu Slash": "Разрез Тэнрю",
    "Shoryu Slash": "Разрез Сёрю",
    "Koryu Slash": "Разрез Корю",
    "Terra Force": "Сила Терры",
    "The Key": "Ключ",
    "Their power is building...": "Их сила нарастает...",
    "Their power surges!": "Их сила резко возрастает!",
    "Twenty Dive": "Двадцатейший рывок",
    "Triangler": "Трианглер",
    "Tri-Horn Attack": "Трёхрогая атака",
    "Trident Revolver": "Револьвер «Трезубец»",
    "Trinity Arm": "Рука Троицы",
    "Triple Forces": "Тройная сила",
    "Turbo Stinger": "Турбожало",
    "Ultimate Blast": "Высший взрыв",
    "Ultimate Ouryuken": "Высший Оурюкен",
    "Ultimate Quake": "Высшее землетрясение",
    "Ultimate Seibaken": "Высший Сэйбакен",
    "Unidentified Flying Kiss": "Неопознанный летающий поцелуй",
    "Venom Infusion": "Ядовитое вливание",
    "Veemon Headbutt": "Удар головой Ви-мона",
    "Vortex Penetration": "Пронзающий вихрь",
    "Vulcan Crusher": "Сокрушитель Вулкана",
    "Wheel Grinder": "Колёсная дробилка",
    "Wide Plasment": "Всеохватная плазма",
    "Will-O'-Wisp Slash": "Разрез блуждающего огонька",
    "Wind Cutter Sword": "Меч ветрового резака",
    "Winning Knuckle": "Победный кулак",
    "Witchmon Begins to Meditate": "Витчмон начинает медитировать",
    "Zealous Defense": "Ревностная защита",
}


# A handful of aggregate jogress rows come from optional content for which the
# installed game has no extracted English table.  Their identity is still
# unambiguous because they duplicate reviewed base-game attacks or contain an
# obvious typo.
SOURCELESS_ID_NAMES = {
    ("base_jogress", "22001"): "Омега-кик",
    ("base_jogress", "24203"): "Гигасмерть",
    ("base_jogress", "29051"): "Молниеносный выпад",
    ("base_jogress", "29681"): "Фантазия семи",
    ("base_jogress", "40003"): "Механоримон целится в гражданских!",
    ("base_jogress", "47331"): "Спокойной ночи, Луна",
}


PROFILE_PATH = (
    ROOT
    / "csv/addcont_02_text01/text/digimon_profile_dlc02.mbe/000_Sheet1.csv"
)
PROFILE_REPLACEMENTS = {
    "digimon_0448_profile": (
        "Серый меч Омегамона преобразился в катану «Grey Tou»,\n"
        "которой он одним неохотным взмахом обезглавливает\n"
        "цель. Особый приём «Гаруру-пушка» также изменился:\n"
        "теперь это «Garuru Hou», лазер абсолютного нуля.",
        "«Трансцендентный меч» Омегамона преобразился в катану\n"
        "«Грозный клинок», которой Милосердный режим одним\n"
        "неохотным взмахом обезглавливает цель. «Высшая пушка»\n"
        "превратилась в «Изящную пушку», стреляющую лазером\n"
        "абсолютного нуля.",
    ),
    "digimon_0487_profile": (
        "Особые приёмы — «Kanshaku Dust», отражающий\n"
        "луч из Кансякудамы в животе от падающих камней для\n"
        "широкой атаки, и «Когтевой бур Ёбори», пронзающий врага\n"
        "буром на левой руке, способным дробить даже хромдигизоид.",
        "Особые приёмы — «Пыль Кансяку»: луч из Кансякудамы\n"
        "в животе отражается от падающих камней и поражает\n"
        "большую площадь; и «Когтевой бур Ёбори», которым\n"
        "дигимон пронзает врага буром на левой руке, способным\n"
        "раздробить даже хромдигизоид.",
    ),
}


def read_rows(path: Path) -> list[list[str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.reader(handle))


def source_map(table: Table) -> dict[str, str]:
    source = {row[0]: row[1] for row in read_rows(table.source)[1:] if len(row) >= 2}
    if table.label == "base_jogress":
        # The translated aggregate jogress table also contains DLC rows which
        # are absent from the stock app table.  Link those rows to their own
        # DLC jogress sources before treating them as source-less.
        for spec in TABLES:
            if not spec.label.startswith("dlc") or not spec.label.endswith("jogress_skill"):
                continue
            for row in read_rows(spec.source)[1:]:
                if len(row) >= 2:
                    source.setdefault(row[0], row[1])
    return source


def write_rows(path: Path, rows: list[list[str]]) -> None:
    raw = path.read_bytes()
    encoding = "utf-8-sig" if raw.startswith(b"\xef\xbb\xbf") else "utf-8"
    newline = "\r\n" if b"\r\n" in raw else "\n"
    with path.open("w", encoding=encoding, newline="") as handle:
        csv.writer(handle, lineterminator=newline).writerows(rows)


def desired_name(english: str) -> str | None:
    exact = EXACT_NAMES.get(english)
    if exact is not None:
        return exact
    humanized = HUMANIZED_NAMES.get(english)
    if humanized is not None:
        return humanized
    for numeral in ("I", "II", "III"):
        suffix = f" {numeral}"
        if english.endswith(suffix):
            english_base = english[: -len(suffix)]
            english_base = SERIES_ALIASES.get(english_base, english_base)
            base = SERIES_BASES.get(english_base)
            if base is not None:
                return f"{base} {numeral}"
    return None


def update_tables() -> tuple[int, int, int]:
    changed = current = matched = 0
    for table in TABLES:
        source = source_map(table)
        rows = read_rows(table.target)
        file_changed = False
        for row in rows[1:]:
            if len(row) < 2:
                continue
            english = source.get(row[0])
            wanted = (
                desired_name(english)
                if english is not None
                else SOURCELESS_ID_NAMES.get((table.label, row[0]))
            )
            if wanted is None:
                continue
            matched += 1
            if row[1] == wanted:
                current += 1
            else:
                row[1] = wanted
                changed += 1
                file_changed = True
        if file_changed:
            write_rows(table.target, rows)
    return matched, changed, current


def update_profiles() -> tuple[int, int]:
    rows = read_rows(PROFILE_PATH)
    by_id = {row[0]: row for row in rows[1:] if len(row) >= 2}
    changed = current = 0
    for row_id, (old, new) in PROFILE_REPLACEMENTS.items():
        row = by_id.get(row_id)
        if row is None:
            raise ValueError(f"missing profile row {row_id}")
        if new in row[1]:
            current += 1
        elif old in row[1]:
            row[1] = row[1].replace(old, new)
            changed += 1
        else:
            raise ValueError(f"unexpected profile text for {row_id}")
    if changed:
        write_rows(PROFILE_PATH, rows)
    return changed, current


def main() -> None:
    matched, changed, current = update_tables()
    profile_changed, profile_current = update_profiles()
    print(f"Source-confirmed attack rows: {matched}")
    print(f"Attack names changed: {changed}")
    print(f"Attack names already current: {current}")
    print(f"Profiles changed: {profile_changed}")
    print(f"Profiles already current: {profile_current}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Apply the final manually reviewed profile move-name mappings."""

from __future__ import annotations

import csv
import re
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CSV_ROOT = ROOT / "csv"
MANIFEST = ROOT / "exports/profile_move_replacements_manual_tail_v108.csv"
PROFILE_FILE = "text/digimon_profile.mbe/000_Sheet1.csv"
FIELDS = [
    "package", "file", "row_id", "source_move", "old", "new",
    "mode", "expected_count", "note",
]


def entry(row_id: str, source_move: str, old: str, new: str, mode: str = "bare", note: str = ""):
    return ("patch_text01", PROFILE_FILE, row_id, source_move, old, new, mode, note)


REVIEWED = [
    entry("digimon_0779_profile", "Aguichant Lèvres", "Соблазнительные Губы", "Агишан Левр", "quote"),
    entry("digimon_0104_profile", "Ama no Habakiri", "Ама но Хабакири", "Ама-но Хабакири", "quote"),
    entry("digimon_0149_profile", "Ame no Murakumo", "Амэ но Муракумо", "Амэ - но - Муракумо", "quote"),
    entry("digimon_0669_profile", "Atomic Inferno", "Атомный Инферно", "Атомное инферно"),
    entry("digimon_0616_profile", "Bind Red Trigger", "Связывающий Красный Курок", "Привязать Красный Триггер"),
    entry("digimon_0106_profile", "Black Rain", "Блэк Рейн", "Чёрный дождь", "quote"),
    entry("digimon_0416_profile", "Blade of the Dragon King", "Блейд оф зе Драгон Кинг", "Клинок короля драконов", "quote"),
    entry("digimon_0614_profile", "Blade of the True", "Клинок Истины", "Клинок Истинного"),
    entry("digimon_0479_profile", "Bowling Storm", "Боулинг Шторм", "Боулинг-шторм"),
    entry("digimon_0019_profile", "Brave Metal", "Брэйв Метал", "Храбрый металл", "quote"),
    entry("digimon_0604_profile", "Calydon Arcus", "Калидонский Лук", "Калидон Аркус"),
    entry("digimon_0632_profile", "Catastrophe Cannon", "Пушка Катастрофы", "Пушка-катастрофа"),
    entry("digimon_0490_profile", "Cool Edge", "Крутой Край", "Холодная кромка"),
    entry("digimon_0626_profile", "Crazy Giggle", "Безумный Хихикс", "Сумасшедшее Хихиканье"),
    entry(
        "digimon_0465_profile", "Daredevil Break", "Во время Лиходейского Прорыва",
        "Во время приёма «Пробой сорвиголовы»", "raw", "preserve case agreement",
    ),
    entry("digimon_0630_profile", "Data Crusher", "Сокрушитель Данных", "Дробилка данных"),
    entry("digimon_0492_profile", "Deep Forest", "Глухой Лес", "Дремучий Лес"),
    entry("digimon_0704_profile", "Destruction Crush", "Сокрушительное Раздавливание", "Разрушительный удар"),
    entry("digimon_0617_profile", "Destruction Trigger", "Курок Разрушения", "Триггер разрушения"),
    entry("digimon_0573_profile", "Downward Cleave", "Нисходящий Рассекающий Удар", "Нисходящий разрез"),
    entry("digimon_0574_profile", "Dual Swallow Reversal", "Двойной Ласточкин Разворот", "Двойной Разворот Ласточки"),
    entry(
        "digimon_0687_profile", "Fifth Rush", "используя Пятую Атаку",
        "используя приём «Пятый Порыв»", "raw", "preserve syntax",
    ),
    entry("digimon_0683_profile", "Flame Cannon", "Пламенная Пушка", "Огненная Пушка"),
    entry("digimon_0049_profile", "Flashy Boss Punch", "Флэши Босс Панч", "Эффектный удар босса", "quote"),
    entry("digimon_0129_profile", "Forbidden Trident", "Форбидден Трайдент", "Запрещенный Трезубец", "quote"),
    entry("digimon_0515_profile", "Fox Tail", "Лисьий Хвост", "Лисий Хвост"),
    entry("digimon_0395_profile", "Fox Tail Inferno", "Фокс Тейл Инферно", "Инферно лисьего хвоста", "quote"),
    entry("digimon_0489_profile", "Gaia Brave", "Гайя Храбрец", "Гея Храбрая"),
    entry("digimon_0306_profile", "Giga Blaster", "Гига Бластер", "Гига-бластер", "quote"),
    entry("digimon_0629_profile", "Glare Eye", "Ослепляющий Глаз", "Слепящий взгляд"),
    entry("digimon_0614_profile", "Golden Ripper", "Золотой Разрыватель", "Золотой Потрошитель"),
    entry("digimon_0170_profile", "Graceful Lance", "Грейсфул Ланс", "Изящное Копье", "quote"),
    entry("digimon_0616_profile", "Happy Bullet Showering", "Ливень Счастливых Пуль", "Счастливый ливень пуль"),
    entry(
        "digimon_0683_profile", "Hard Rock Soul", "С Твердой Каменной Душой",
        "С помощью приёма «Хард-рок-душа»", "raw", "preserve case agreement",
    ),
    entry("digimon_0735_profile", "Heaven's Judgment", "Суд Небес", "Небесный суд", "quote"),
    entry("digimon_0774_profile", "Heaven's Judgment", "Суд Небес", "Небесный суд", "quote"),
    entry("digimon_0621_profile", "Hyper Cannon", "Гипер Пушка", "Гиперпушка"),
    entry("digimon_0422_profile", "Hyper Infinity Cannon", "Бесконечная Пушка", "Гиперпушка бесконечности", "quote"),
    entry("digimon_0702_profile", "Kunai Wing", "Крыло Куная", "Крыло Кунаи"),
    entry("digimon_0186_profile", "Lightning Shower", "Лайтнинг Шауэр", "Ливень с Молнией", "quote"),
    entry("digimon_0778_profile", "Lightning Thrust", "Удар Молнии", "Молниеносный Удар", "quote"),
    entry("digimon_0582_profile", "Lullaby Bubble", "Колыбельная Пузырь", "Колыбельный Пузырь"),
    entry("digimon_0678_profile", "Machinegun Destroyer", "Разрушитель Пулемета", "Пулемётный разрушитель"),
    entry("digimon_0912_profile", "Marionette Abomination", "Марионеточная мерзость", "Мерзость Марионетки", "quote"),
    entry("digimon_0466_profile", "Metal Drop", "Металлическая Капля", "Падение металла"),
    entry("digimon_0609_profile", "Mini Scissor Claw", "Мини Коготь-Ножницы", "Мини-Ножничный Коготь"),
    entry("digimon_0617_profile", "Misery Bullet Rain", "Ливень Пуль Страдания", "Дождь пуль отчаяния"),
    entry("digimon_0567_profile", "Poison Bubbles", "Ядовитые Пузыри", "Ядовитые Пузырьки"),
    entry("digimon_0610_profile", "Pummel Peck", "Долбежка Клювом", "Дробящий клевок"),
    entry("digimon_0117_profile", "Purge Shine", "Пёдж Шайн", "Очищающий Блеск", "quote"),
    entry(
        "digimon_0117_profile", "Purge Shine", "Пёдж Шайна", "Очищающего Блеска",
        "raw", "inflected repeated reference",
    ),
    entry("digimon_0677_profile", "Pyro Dragons", "Пиро Драконы", "Поджигательные Драконы"),
    entry("digimon_0676_profile", "Pyro Punch", "Пиро Удар", "Огненный удар"),
    entry(
        "digimon_0688_profile", "Quake! Blast! Fire! Father!", "Тряси! Взрывай! Огонь! Отец!",
        "Землетрясение! Взрыв! Огонь! Отец!",
    ),
    entry("digimon_0603_profile", "Rage of Wyvern", "Гнев Виверна", "Ярость Виверны"),
    entry("digimon_0611_profile", "Rain of Pollen", "Ливень Пыльцы", "Дождь из пыльцы"),
    entry("digimon_0489_profile", "Red Reamer", "Красное Сверло", "Красный риммер"),
    entry("digimon_0492_profile", "Rodeo Bullet", "Родео Пуля", "Пуля родео"),
    entry("digimon_0421_profile", "Sefirot Crystal", "Сефирот Кристалл", "Кристалл Сфирот", "quote"),
    entry("digimon_0126_profile", "Shield of the Just", "Шилд оф зе Джаст", "Щит праведника", "quote"),
    entry(
        "digimon_0382_profile", "Shining Gold Solar Storm", "Шайнинг Голд Солар Сторм",
        "Сияющая золотая солнечная буря", "quote",
    ),
    entry("digimon_0598_profile", "Slamming Tusk", "Сокрушающий Клык", "Бьющий Бивень"),
    entry("digimon_0173_profile", "Sol Blaster", "Сол Бластер", "Солнечный Бластер", "quote"),
    entry("digimon_0584_profile", "Soul Chopper", "Рассекатель Душ", "Измельчитель Душ"),
    entry("digimon_0564_profile", "Sparkling Thunder", "Искрящаяся Гроза", "Сверкающий Гром"),
    entry("digimon_0484_profile", "Spike Buster", "Шип Бастер", "Спайк Бастер"),
    entry("digimon_0594_profile", "Spiral Edge", "Спиральное Лезвие", "Спиральный край"),
    entry("digimon_0703_profile", "Spiral Masquerade", "Спиральная Маскарад", "Спиральный Маскарад"),
    entry("digimon_0491_profile", "Spirited Claws", "Воодушевленные Когти", "Энергичные Когти"),
    entry("digimon_0605_profile", "Stinger Surprise", "Хвост Смерти", "Жало - Сюрприз"),
    entry("digimon_0606_profile", "Strike Fishing", "Ударный Лов", "Ударная рыбалка"),
    entry(
        "digimon_0390_profile", "Strike of the Seven Stars", "Страйк оф зе Севен Старз",
        "Удар семи звезд", "quote",
    ),
    entry("digimon_0575_profile", "Sunburst Dance", "Танец Вспышки Солнца", "Танец Солнечных Лучей"),
    entry("digimon_0622_profile", "Super Slap", "Супер Пощечина", "Супер-Пощечина"),
    entry("digimon_0688_profile", "Table Flip", "Опрокидывание Стола", "Переворачивание стола"),
    entry("digimon_0701_profile", "Terrier Tornado", "Торнадо Терьера", "Терьер Торнадо"),
    entry("digimon_0790_profile", "Terrier Tornado", "Терьер-Торнадо", "Терьер Торнадо", "quote"),
    entry("digimon_0596_profile", "Trick or Treat", "Уловка или Угощение", "Трюк или угощение"),
    entry("digimon_0588_profile", "Tusk Strikes", "Удары Клыками", "Удары Бивня"),
    entry("digimon_0600_profile", "Venom Infusion", "Вливание Яда", "Ядовитое вливание"),
    entry("digimon_0171_profile", "Welcome Demise", "Велком Демайз", "Желанная Кончина", "quote"),
    entry("digimon_0463_profile", "Zeppelin Explosion", "Цеппелин Взрыв", "Взрыв Цеппелина"),
]


def flexible_pattern(value: str, quoted: bool) -> re.Pattern[str]:
    pieces = [re.escape(piece) for piece in value.split()]
    body = r"\s+".join(pieces)
    if quoted:
        return re.compile(r"«" + body + r"»")
    return re.compile(r"(?<!\w)" + body + r"(?!\w)")


def replacement_text(new: str, mode: str) -> str:
    if mode in {"quote", "bare"}:
        return f"«{new}»"
    return new


def read_rows(path: Path) -> list[list[str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.reader(handle))


def build_manifest() -> list[dict[str, str]]:
    if len(REVIEWED) != 82:
        raise SystemExit(f"Reviewed manual-tail baseline changed: expected 82 entries, got {len(REVIEWED)}")
    cache: dict[tuple[str, str], dict[str, str]] = {}
    manifest: list[dict[str, str]] = []
    for package, relative, row_id, source_move, old, new, mode, note in REVIEWED:
        key = (package, relative)
        if key not in cache:
            cache[key] = {
                row[0]: row[1] for row in read_rows(CSV_ROOT / package / relative) if len(row) >= 2
            }
        current = cache[key].get(row_id)
        if current is None:
            raise SystemExit(f"Missing profile row: {package}:{relative}:{row_id}")
        pattern = flexible_pattern(old, mode == "quote")
        count = len(pattern.findall(current))
        if count < 1:
            raise SystemExit(f"Reviewed fragment missing: {row_id}:{source_move}:{old!r}")
        manifest.append(
            {
                "package": package,
                "file": relative,
                "row_id": row_id,
                "source_move": source_move,
                "old": old,
                "new": new,
                "mode": mode,
                "expected_count": str(count),
                "note": note or "manual source-context review",
            }
        )
    with MANIFEST.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(manifest)
    return manifest


def read_manifest() -> list[dict[str, str]]:
    if not MANIFEST.exists():
        return build_manifest()
    with MANIFEST.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def main() -> None:
    manifest = read_manifest()
    grouped: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in manifest:
        grouped[(row["package"], row["file"])].append(row)

    changed = 0
    already_current = 0
    for (package, relative), updates in sorted(grouped.items()):
        path = CSV_ROOT / package / relative
        rows = read_rows(path)
        by_id = {row[0]: row for row in rows if len(row) >= 2}
        file_changed = False
        for update in updates:
            row = by_id.get(update["row_id"])
            if row is None:
                raise SystemExit(f"Missing profile row: {package}:{relative}:{update['row_id']}")
            old_pattern = flexible_pattern(update["old"], update["mode"] == "quote")
            new_text = replacement_text(update["new"], update["mode"])
            new_pattern = flexible_pattern(new_text, False)
            expected = int(update["expected_count"])
            old_count = len(old_pattern.findall(row[1]))
            if old_count == expected:
                row[1] = old_pattern.sub(lambda _: new_text, row[1])
                changed += expected
                file_changed = True
            elif old_count == 0 and len(new_pattern.findall(row[1])) >= expected:
                already_current += expected
            else:
                raise SystemExit(
                    f"Ambiguous manual-tail replacement {update['row_id']}:{update['source_move']}: "
                    f"{update['old']!r} count={old_count}, expected={expected}"
                )
        if file_changed:
            with path.open("w", encoding="utf-8-sig", newline="") as handle:
                csv.writer(handle, lineterminator="\n").writerows(rows)

    print(f"Manual-tail mappings: {len(manifest)}")
    print(f"Changed occurrences: {changed}")
    print(f"Already current occurrences: {already_current}")
    print(f"Manifest: {MANIFEST.relative_to(ROOT)}")


if __name__ == "__main__":
    main()

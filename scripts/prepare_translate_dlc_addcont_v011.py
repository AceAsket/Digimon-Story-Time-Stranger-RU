from __future__ import annotations

import csv
import json
import re
import shutil
import sys
import time
from pathlib import Path

from deep_translator import GoogleTranslator

ROOT = Path(__file__).resolve().parents[1]
UNDUB_CSV_ROOT = ROOT / "verify" / "undub_v1_5_4" / "csv"
DLC_ROOTS = [
    "addcont_01_text01",
    "addcont_02_text01",
    "addcont_03_text01",
    "addcont_05_text01",
    "addcont_07_text01",
    "addcont_12_text01",
    "addcont_17_text01",
]
TARGET_CSV_ROOT = ROOT / "csv"
CACHE_PATH = ROOT / "exports" / "dlc_translation_cache_v011.json"
LOG_PATH = ROOT / "logs" / "prepare_translate_dlc_addcont_v011.log"

sys.path.insert(0, str(ROOT / "scripts"))
import apply_undub_translation_pass_v020 as base  # noqa: E402


TECH_RE = re.compile(
    r"^(?:|string \d+|empty \d+|char_[A-Za-z0-9_:\-&]+|[A-Za-z0-9_]+_\d+(?:_\d+)*(?:_[A-Za-z0-9_]+)?|\d+)$"
)
LATIN_RE = re.compile(r"[A-Za-z]{3,}")


MANUAL_TRANSLATIONS = {
    "Akashic Backdoor": "Акашический бэкдор",
    "Space-Time Pathway": "Путь сквозь пространство-время",
    "Exit Ampule": "Выходная ампула",
    "{fc9Exit Ampule}": "{fc9Выходная ампула}",
    "Talent Awakening Booster EX: 01": "Бустер пробуждения таланта EX: 01",
    "Talent Awakening Booster EX: 02": "Бустер пробуждения таланта EX: 02",
    "Talent Awakening Booster EX: 03": "Бустер пробуждения таланта EX: 03",
    "Backdoor Key 1": "Ключ бэкдора 1",
    "Backdoor Key 2": "Ключ бэкдора 2",
    "Kyoko's Goggles (Spare)": "Очки Кёко (запасные)",
    "Hiroko's Memory Card": "Карта памяти Хироко",
    "Simmons's Update Patch": "Патч обновления Симмонса",
    "Golden Moai": "Золотой моаи",
    "Collector's USB Stick": "USB-накопитель коллекционера",
    "Strategist's USB Stick": "USB-накопитель стратега",
    "Millionaire's USB Stick": "USB-накопитель миллионера",
    "Stylish Toilet": "Стильный туалет",
    "Cyber Sleuth Outfit": "Костюм Cyber Sleuth",
    "Misono Inori": "Мисоно Инори",
    "Sagisaka Hiroko": "Сагисака Хироко",
    "Shiroki Asuna": "Сироки Асуна",
    "Dr. Simmons": "доктор Симмонс",
    "Alternate Dimension": "Иное измерение",
    "GAKU-RAN": "GAKU-RAN",
    "Anti-ParadoX": "Anti-ParadoX",
    "Goddramon": "Годдрамон",
    "MirageGaogamon": "МиражГаогамон",
    "Parallelmon": "Параллельмон",
    "BlitzGreymon": "БлицГреймон",
    "CresGarurumon": "КресГарурумон",
    "Omegamon Alter-S": "Омегамон Alter-S",
    "Omegamon Zwart Defeat": "Омегамон Зварт Defeat",
    "Omegamon Alter-B": "Омегамон Alter-B",
    "BlitzGreymon & CresGarurumon": "БлицГреймон и КресГарурумон",
    "Kuremi Kyoko": "Курэми Кёко",
    "Kuremi Kodai": "Курэми Кодай",
    "Girl Who Wandered In": "Забредшая сюда девушка",
    "BanchoLeomon": "БанчоЛеомон",
    "Omegamon": "Омегамон",
    "Omegamon MM": "Омегамон MM",
    "BanchoStingmon": "БанчоСтингмон",
    "BanchoLilimon": "БанчоЛилимон",
    "BanchoGolemon": "БанчоГолемон",
    "BanchoMamemon": "БанчоМамемон",
    "Omegamon (X Antibody)": "Омегамон (X-антитело)",
    "Dukemon (X Antibody)": "Дюкмон (X-антитело)",
    "UlforceV-dramon (X Antibody)": "УльфорсV-драмон (X-антитело)",
    "Magnamon (X Antibody)": "Магнамон (X-антитело)",
    "JESmon (X Antibody)": "Джесмон (X-антитело)",
    "DORUmon": "ДОРУмон",
    "Alphamon": "Альфамон",
    "Agumon (Black)": "Агумон (чёрный)",
    "BlackWarGreymon": "БлэкВарГреймон",
    "MetalGarurumon (Black)": "МеталГарурумон (чёрный)",
    "MetalGreymon (Blue)": "МеталГреймон (синий)",
    "Greymon (Blue)": "Греймон (синий)",
    "Gabumon (Black)": "Габумон (чёрный)",
    "Garurumon (Black)": "Гарурумон (чёрный)",
    "WereGarurumon (Black)": "ВерГарурумон (чёрный)",
    "Omegamon Zwart": "Омегамон Зварт",
    "Absorbent Bang": "Поглощающий взрыв",
    "Endless Trance": "Бесконечный транс",
    "Plasma Stake": "Плазменный кол",
    "Elec Guard": "Электрозащита",
    "Great Beast-Wolf Rotation": "Вращение великого зверя-волка",
    "Fury: Ice Moon Fang": "Ярость: клык ледяной луны",
    "Garuru Sword": "Гаруру-меч",
    "Grey Cannon": "Грей-пушка",
    "Grey Sword": "Грей-меч",
    "Garuru Cannon": "Гаруру-пушка",
    "I Give You My Guidance!": "Я укажу тебе путь!",
    "Amazing Enemy!": "Невероятный враг!",
    "Let's Be Fully Prepared!": "Подготовимся как следует!",
    "Let's Take Action!": "Пора действовать!",
    "Digimon from Another Dimension!": "Дигимоны из другого измерения!",
    "Allow me to perform your last rites!": "Позволь провести твой последний обряд!",
    "For an enemy, they're amazing!": "Для врага они впечатляют!",
    "Let's be fully prepared!": "Подготовимся как следует!",
    "Let's take action!": "Пора действовать!",
    "{d0} mustered their strength!": "{d0} собрался с силами!",
    "Digimon from another dimension have been summoned!": "Призваны дигимоны из другого измерения!",
    "Grey Tou": "Грей-то",
    "Garuru Hou": "Гаруру-хо",
    "Bloody Finish": "Кровавый финиш",
    "Explosive Thunderstorm": "Взрывная гроза",
    "Absolute Territory": "Абсолютная территория",
    "Twin Petal": "Двойной лепесток",
    "Kanshaku Dust": "Кансяку Даст",
    "Yobori Claw Drill": "Бур-коготь Ёбори",
    "Golden Rush": "Золотой натиск",
    "Senbon Dokkan": "Сэнбон Доккан",
    "Locked on.": "Цель захвачена.",
    "Obliterating the target.": "Уничтожаю цель.",
    "Eliminating the target.": "Ликвидирую цель.",
    "All Delete": "Полное удаление",
    "Sieg Saber": "Зиг-забер",
    "Final Elysion": "Финальный Элизион",
    "Shining V Force": "Сияющая V-сила",
    "Ulforce Saber": "Ульфорс-забер",
    "Shining Gold Solar Storm": "Сияющая золотая солнечная буря",
    "Plasma Shoot": "Плазменный выстрел",
    "Known Bug": "Известный баг",
    "Schwertflügel": "Швертфлюгель",
    "Ultimate Seibaken": "Совершенный Сэйбакен",
    "Spitfire": "Спитфайр",
    "Dark Gaia Force": "Тёмная сила Геи",
    "Black Tornado": "Чёрный торнадо",
    "Grace Cross Freezer": "Грейс-кросс фризер",
    "Garuru Tomahawk": "Гаруру-томагавк",
    "Trident Arm": "Трезубец-рука",
    "Bit Fire": "Малое пламя",
    "Little Horn": "Малый рог",
    "Freeze Fang": "Ледяной клык",
    "Full Moon Kick": "Удар полной луны",
    "A farm item.\r\nUse this to customize your DigiFarm to your liking.": "Предмет для Дигифермы.\r\nИспользуйте его, чтобы оформить Дигиферму по своему вкусу.",
    "A farm item.\r\nUse this to customize your Digifarm to your liking.": "Предмет для Дигифермы.\r\nИспользуйте его, чтобы оформить Дигиферму по своему вкусу.",
    "Boosts item drop rate by 10% when equipped by a battle or\r\nreserve member.": "Повышает шанс выпадения предметов на 10%, если предмет экипирован у боевого или запасного участника.",
    "Boosts EXP gained by 100% when equipped by a battle or\r\nreserve member.": "Увеличивает получаемый EXP на 100%, если предмет экипирован у боевого или запасного участника.",
    "Boosts money obtained by 100% when equipped by a battle or\r\nreserve member.": "Увеличивает получаемые деньги на 100%, если предмет экипирован у боевого или запасного участника.",
    "Costume.\r\nAn outfit taking inspiration from Digimon Story: Cyber Sleuth.": "Костюм.\r\nНаряд, вдохновлённый Digimon Story: Cyber Sleuth.",
}

POST_REPLACEMENTS = [
    ("Черный ход Акаши", "Акашический бэкдор"),
    ("черный ход Акаши", "Акашический бэкдор"),
    ("черного хода Акаши", "Акашического бэкдора"),
    ("черному ходу Акаши", "Акашическому бэкдору"),
    ("Акашический Бэкдор", "Акашический бэкдор"),
    ("Акашийский бэкдор", "Акашический бэкдор"),
    ("Бэкдор Акаши", "Акашический бэкдор"),
    ("черный кристалл", "чёрный кристалл"),
    ("черная форма", "чёрная форма"),
    ("Внепространственное пространство", "Межпространственное пространство"),
    ("внепространственное пространство", "межпространственное пространство"),
    ("ДигиФарм", "Дигиферма"),
    ("Дигиферму", "Дигиферму"),
    ("DigiFarm", "Дигиферма"),
    ("Digifarm", "Дигиферма"),
    ("ДигиМир", "Цифровой мир"),
    ("Digital World", "Цифровой мир"),
    ("Digital Worlds", "Цифровые миры"),
    ("Диджимон", "Дигимон"),
    ("дигимон", "дигимон"),
    ("Дигимоны", "Дигимоны"),
    ("Параллелемон", "Параллельмон"),
    ("Параллелмон", "Параллельмон"),
    ("Омегамон", "Омегамон"),
    ("Cyber Sleuth", "Cyber Sleuth"),
    ("USB-накопитель", "USB-накопитель"),
    ("EXP", "EXP"),
    ("присоединился к вечеринке", "присоединился к группе"),
    ("присоединилась к вечеринке", "присоединилась к группе"),
    ("присоединились к вечеринке", "присоединились к группе"),
    ("резервный член", "запасной участник"),
    ("резервным членом", "запасным участником"),
    ("Давай скинем как-нибудь.", "Давай как-нибудь сразимся."),
]


def read_rows(path: Path) -> list[list[str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.reader(f))


def write_rows(path: Path, rows: list[list[str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        csv.writer(f, lineterminator="\n").writerows(rows)


def normalize_sources() -> None:
    for name in DLC_ROOTS:
        src_root = UNDUB_CSV_ROOT / f"{name}.dx11"
        dst_root = TARGET_CSV_ROOT / name
        if dst_root.exists():
            shutil.rmtree(dst_root)
        for csv_path in sorted(src_root.rglob("000_Sheet1.csv")):
            rel_parts = list(csv_path.relative_to(src_root).parts)
            # Unpack-mbe created message/foo.mbe/foo.mbe/000_Sheet1.csv.
            if len(rel_parts) >= 4 and rel_parts[-2] == rel_parts[-3]:
                rel_parts.pop(-2)
            dst_path = dst_root.joinpath(*rel_parts)
            write_rows(dst_path, read_rows(csv_path))


def load_cache() -> dict[str, str]:
    if CACHE_PATH.exists():
        return json.loads(CACHE_PATH.read_text(encoding="utf-8"))
    return {}


def save_cache(cache: dict[str, str]) -> None:
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    CACHE_PATH.write_text(json.dumps(cache, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def is_translatable(value: str) -> bool:
    value = value.strip()
    if not value:
        return False
    if value.startswith("char_"):
        return False
    if not LATIN_RE.search(value):
        return False
    if TECH_RE.fullmatch(value):
        return False
    return True


def protect_text(text: str) -> str:
    return text.replace("\r\r\n", "\n").replace("\r\n", "\n").replace("\r", "\n")


def restore_text(text: str) -> str:
    return text.replace("\n", "\r\n")


def clean_translation(text: str) -> str:
    if text.startswith("char_"):
        return text
    text = base.replace_many(text, base.TERM_REPLACEMENTS, whole_word_ascii=True)
    text = base.replace_many(text, base.TOKEN_REPLACEMENTS, whole_word_ascii=True)
    text = base.replace_many(text, base.ATTACK_TRANSLATIONS, whole_word_ascii=True)
    for old, new in sorted(MANUAL_TRANSLATIONS.items(), key=lambda item: len(item[0]), reverse=True):
        if old and LATIN_RE.search(old):
            text = text.replace(old, new)
    for old, new in POST_REPLACEMENTS:
        text = text.replace(old, new)
    text = base.normalize_case(text)
    return text


def translate_values(values: list[str], cache: dict[str, str]) -> None:
    translator = GoogleTranslator(source="en", target="ru")
    missing = [v for v in values if v not in cache and v not in MANUAL_TRANSLATIONS]
    total = len(missing)
    done = 0
    batch_size = 30
    for start in range(0, total, batch_size):
        batch = missing[start : start + batch_size]
        prepared = [protect_text(v) for v in batch]
        try:
            translated = translator.translate_batch(prepared)
            if len(translated) != len(batch):
                raise RuntimeError(f"batch returned {len(translated)} items for {len(batch)} inputs")
            for src, dst in zip(batch, translated):
                cache[src] = clean_translation(restore_text(dst))
        except Exception:
            for src, prepared_src in zip(batch, prepared):
                for attempt in range(3):
                    try:
                        cache[src] = clean_translation(restore_text(translator.translate(prepared_src)))
                        break
                    except Exception:
                        if attempt == 2:
                            cache[src] = clean_translation(src)
                        time.sleep(1.5)
        done += len(batch)
        if done % 150 == 0 or done == total:
            print(f"translated {done}/{total}")
            save_cache(cache)
        time.sleep(0.2)


def apply_known_table_values(rows: list[list[str]], file_name: str, char_names: dict[str, str], skill_names: dict[str, str]) -> None:
    for row in rows:
        if len(row) < 2 or row[0] == "string2 0":
            continue
        key = row[0]
        if file_name.startswith("char_name") and key in char_names:
            row[1] = char_names[key]
        if ("skill_name" in file_name or "jogress_skill_name" in file_name) and key in skill_names and skill_names[key]:
            row[1] = skill_names[key]
        if row[1] in MANUAL_TRANSLATIONS:
            row[1] = MANUAL_TRANSLATIONS[row[1]]


def load_key_values(path: Path) -> dict[str, str]:
    values = {}
    if not path.exists():
        return values
    for row in read_rows(path):
        if len(row) > 1 and row[0] != "string2 0":
            values[row[0]] = row[1]
    return values


def build_project_maps() -> tuple[dict[str, str], dict[str, str]]:
    char_names = {}
    skill_names = {}
    for root in [ROOT / "csv" / "app_text01", ROOT / "csv" / "patch_text01"]:
        char_names.update(load_key_values(root / "text" / "char_name.mbe" / "000_Sheet1.csv"))
        skill_names.update(load_key_values(root / "text" / "skill_name.mbe" / "000_Sheet1.csv"))
        skill_names.update(load_key_values(root / "text" / "jogress_skill_name.mbe" / "000_Sheet1.csv"))
    char_names.update(base.CHAR_NAME_OVERRIDES)
    char_names.update({k: v for k, v in MANUAL_TRANSLATIONS.items() if k.startswith("char_")})
    return char_names, skill_names


def collect_values() -> list[str]:
    values: set[str] = set()
    for name in DLC_ROOTS:
        for path in (TARGET_CSV_ROOT / name).rglob("*.csv"):
            for row in read_rows(path):
                for idx in range(1, len(row)):
                    if is_translatable(row[idx]):
                        values.add(row[idx])
    return sorted(values, key=lambda item: (len(item), item))


def apply_translations(cache: dict[str, str]) -> list[str]:
    changed_files: list[str] = []
    char_names, skill_names = build_project_maps()
    for name in DLC_ROOTS:
        for path in sorted((TARGET_CSV_ROOT / name).rglob("*.csv")):
            rows = read_rows(path)
            before = [row[:] for row in rows]
            file_name = path.parent.name
            apply_known_table_values(rows, file_name, char_names, skill_names)
            for row in rows:
                for idx in range(1, len(row)):
                    old = row[idx]
                    if old in MANUAL_TRANSLATIONS:
                        row[idx] = MANUAL_TRANSLATIONS[old]
                    elif is_translatable(old):
                        row[idx] = cache.get(old, old)
                    row[idx] = clean_translation(row[idx])
            if rows != before:
                write_rows(path, rows)
                changed_files.append(str(path.relative_to(ROOT)))
    return changed_files


def audit_remaining_latin() -> dict[str, int]:
    result: dict[str, int] = {}
    allowed = re.compile(
        r"\b(?:HP|SP|EXP|YEN|ATK|DEF|INT|SPI|SPD|CRT|EX|DX|USB|DLC|X|MM|GAKU-RAN|Anti-ParadoX|Cyber Sleuth|Alter-S|Alter-B|Zwart|Defeat|inForce)\b"
    )
    for name in DLC_ROOTS:
        count = 0
        for path in (TARGET_CSV_ROOT / name).rglob("*.csv"):
            for row in read_rows(path):
                for cell in row[1:]:
                    scrubbed = allowed.sub("", cell)
                    if LATIN_RE.search(scrubbed) and not TECH_RE.fullmatch(cell.strip()):
                        count += 1
        result[name] = count
    return result


def main() -> None:
    normalize_sources()
    cache = load_cache()
    for src, dst in MANUAL_TRANSLATIONS.items():
        cache[src] = dst
    values = collect_values()
    translate_values(values, cache)
    changed = apply_translations(cache)
    remaining = audit_remaining_latin()
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    LOG_PATH.write_text(
        "\n".join(
            [
                f"values={len(values)}",
                f"cache={len(cache)}",
                f"changed_files={len(changed)}",
                "remaining_latin=" + json.dumps(remaining, ensure_ascii=False, sort_keys=True),
                "",
                *changed,
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    save_cache(cache)
    print(LOG_PATH)
    print(json.dumps(remaining, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()

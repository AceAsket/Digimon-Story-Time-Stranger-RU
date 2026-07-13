#!/usr/bin/env python3
"""Fix reported quest-overview and Digifarm-item layout overflows."""

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CSV_ROOT = ROOT / "csv"


# package, relative CSV, row id, column, guarded old text, replacement
EXACT_UPDATES: list[tuple[str, str, str, int, str, str]] = [
    (
        "patch_text01",
        "text/quest_outline.mbe/000_Sheet1.csv",
        "970",
        1,
        "Появилось Внешнее подземелье с щедрыми наградами опыта!\n"
        "Сражайтесь с противниками, соответствующими вашим силам,\n"
        "чтобы растить более мощных дигимонов.Вы можете приходить\n"
        "и уходить в любое время, так что сражайтесь сколько захотите!",
        "Открыто Внешнее подземелье!\n"
        "Сражайтесь с противниками себе по силам,\n"
        "получайте опыт и развивайте дигимонов.\n"
        "Вход свободный — сражайтесь сколько захотите!",
    ),
    (
        "patch_text01",
        "text/quest_outline.mbe/000_Sheet1.csv",
        "971",
        1,
        "Появилось Внешнее подземелье с большими наградами в ЙЕНАХ!\n"
        "Сражайтесь в соответствии со своими силами и растите ещё более\n"
        "мощных дигимонов! Можете приходить и уходить когда хотите —\n"
        "сражайтесь сколько душе угодно!",
        "Открыто Внешнее подземелье!\n"
        "Сражайтесь с противниками себе по силам,\n"
        "зарабатывайте иены и развивайте дигимонов.\n"
        "Вход свободный — сражайтесь сколько захотите!",
    ),
    (
        "patch_text01",
        "text/quest_outline.mbe/000_Sheet1.csv",
        "972",
        1,
        "Появилось Внешнее подземелье с богатыми материалами!\n"
        "Сражайтесь с противниками по своим силам и растите ещё\n"
        "более мощных дигимонов. Заходите и уходите когда угодно —\n"
        "сражайтесь в своё удовольствие!",
        "Открыто Внешнее подземелье!\n"
        "Сражайтесь с противниками себе по силам,\n"
        "собирайте материалы и развивайте дигимонов.\n"
        "Вход свободный — сражайтесь сколько захотите!",
    ),
    (
        "patch_text01",
        "text/quest_outline.mbe/000_Sheet1.csv",
        "980",
        1,
        "Сможете ли вы победить участников с 43 по 56 из моей\n"
        "окончательной коллекции? Вам лучше не недооценивать\n"
        "их! Не имеет значения, какой маршрут вы выберете,\n"
        "Просто сразите любых троих из них, и вы победите!",
        "Сможете победить участников № 43–56\n"
        "из моей Ультимативной коллекции?\n"
        "Не недооценивайте их! Выберите любой путь\n"
        "и одолейте любых троих, чтобы победить!",
    ),
    (
        "patch_text01",
        "text/quest_outline.mbe/000_Sheet1.csv",
        "981",
        1,
        "Сможете ли вы победить участников под номерами с 29 по 42\n"
        "из моей окончательной коллекции? Эти ребята не пони с\n"
        "одним трюком. Не имеет значения, какой маршрут вы выберете,\n"
        "просто сразите любых трех из них, и вы Победите!",
        "Сможете победить участников № 29–42\n"
        "из моей Ультимативной коллекции?\n"
        "У каждого не один козырь. Выберите любой путь\n"
        "и одолейте любых троих, чтобы победить!",
    ),
    (
        "patch_text01",
        "text/quest_outline.mbe/000_Sheet1.csv",
        "982",
        1,
        "Сможете ли вы победить участников с 15 по 28 из моей\n"
        "окончательной коллекции? Я предупреждаю вас! Их сила\n"
        "необычайна. Не имеет значения, какой маршрут вы выберете,\n"
        "просто сразите любых трех из них, и вы Победите!",
        "Сможете победить участников № 15–28\n"
        "из моей Ультимативной коллекции?\n"
        "Их сила огромна! Выберите любой путь\n"
        "и одолейте любых троих, чтобы победить!",
    ),
    (
        "patch_text01",
        "text/quest_outline.mbe/000_Sheet1.csv",
        "983",
        1,
        "Сможете ли вы победить участников с 1 по 14 из моей\n"
        "Окончательной коллекции? Бьюсь об заклад, вы не сможете\n"
        "противостоять их силе. Не имеет значения, какой маршрут\n"
        "вы выберете, просто сразите любых трех из них, и вы победите!",
        "Сможете победить участников № 1–14\n"
        "из моей Ультимативной коллекции?\n"
        "Вам с ними не совладать! Выберите любой путь\n"
        "и одолейте любых троих, чтобы победить!",
    ),
]

EXACT_UPDATES.extend(
    [
        (
            "patch_text01", "text/quest_outline.mbe/000_Sheet1.csv", "920", 1,
            "Тут полно скользких дигимонов! Постарайтесь не испачкаться\n"
            "в их слизи и какашках! Продержитесь до конца — и победа ваша!",
            "Здесь полно скользких дигимонов! Постарайтесь\n"
            "не испачкаться в их слизи и какашках.\n"
            "Продержитесь до конца — и победа ваша!",
        ),
        (
            "patch_text01", "text/quest_outline.mbe/000_Sheet1.csv", "921", 1,
            "Они такие крутые и свирепые! Я собрал всех своих любимых\n"
            "дигимонов! Продержитесь до конца — и победа ваша!",
            "Какие они крутые и свирепые! Я собрал здесь\n"
            "всех своих любимых дигимонов.\n"
            "Продержитесь до конца — и победа ваша!",
        ),
        (
            "patch_text01", "text/quest_outline.mbe/000_Sheet1.csv", "922", 1,
            "Океан полон тайн! Здесь совсем другая экосистема, чем на суше!\n"
            "Продержитесь до конца — и победа ваша!",
            "Океан полон тайн! Его экосистема совсем\n"
            "не похожа на сухопутную.\n"
            "Продержитесь до конца — и победа ваша!",
        ),
        (
            "patch_text01", "text/quest_outline.mbe/000_Sheet1.csv", "923", 1,
            "Берегитесь палящего пламени, которое сжигает всё, чего касается!\n"
            "Одно прикосновение мгновенно обратит вас в пепел.\n"
            "Продержитесь до конца, уклоняясь от него, — и победа ваша!",
            "Берегитесь палящего пламени: оно сжигает\n"
            "всё на своём пути! Одно касание —\n"
            "и вы обратитесь в пепел. Уклоняйтесь\n"
            "до конца — и победа ваша!",
        ),
        (
            "patch_text01", "text/quest_outline.mbe/000_Sheet1.csv", "930", 1,
            "Сможешь ли ты угнаться за Лаламоном, которого я\n"
            "Настраивал? Если ты сможешь достичь цели быстрее,\n"
            "Чем Лаламон, ты победишь!",
            "Сможете угнаться за улучшенной Лаламон?\n"
            "Доберитесь до цели раньше неё —\n"
            "и победа ваша!",
        ),
        (
            "patch_text01", "text/quest_outline.mbe/000_Sheet1.csv", "931", 1,
            "Сможете ли вы угнаться за Витчмон, который был\n"
            "настроен мной? Если вы сможете достичь цели быстрее,\n"
            "чем Витчмон, вы выиграете!",
            "Сможете угнаться за улучшенной Витчмон?\n"
            "Доберитесь до цели раньше неё —\n"
            "и победа ваша!",
        ),
        (
            "patch_text01", "text/quest_outline.mbe/000_Sheet1.csv", "932", 1,
            "Сможешь ли ты угнаться за Вингдрамоном, которого я\n"
            "настраивал? Если ты сможешь достичь цели быстрее\n"
            "Вингдрамона, ты победишь!",
            "Сможете угнаться за улучшенным Вингдрамоном?\n"
            "Доберитесь до цели раньше него —\n"
            "и победа ваша!",
        ),
        (
            "patch_text01", "text/quest_outline.mbe/000_Sheet1.csv", "933", 1,
            "Сможешь ли ты угнаться за Магнагарурумоном, которого\n"
            "я настраивал? Если ты сможешь достичь цели быстрее\n"
            "Магнагарурумона, ты победишь!",
            "Сможете угнаться за улучшенным\n"
            "Магна Гарурумоном? Доберитесь до цели\n"
            "раньше него — и победа ваша!",
        ),
        (
            "patch_text01", "text/quest_outline.mbe/000_Sheet1.csv", "945", 1,
            "Тема игры - самураи и ниндзя! Вы должны победить\n"
            "босса в дальнем конце за отведенное время! Вот\n"
            "Подсказка о боссе: это мастер камайтачи!",
            "Тема — самураи и ниндзя! Доберитесь\n"
            "до дальнего конца и победите босса\n"
            "за отведённое время. Подсказка:\n"
            "босс — мастер камайтачи!",
        ),
        (
            "patch_text01", "text/quest_outline.mbe/000_Sheet1.csv", "946", 1,
            "Тема - арктический рай! Вы должны победить босса в\n"
            "дальнем конце за отведенное время! Вот подсказка о\n"
            "Боссе: у него острые мифриловые рога.",
            "Тема — арктический рай! Доберитесь\n"
            "до дальнего конца и победите босса\n"
            "за отведённое время. Подсказка:\n"
            "у него острые рога из мифрила.",
        ),
        (
            "patch_text01", "text/quest_outline.mbe/000_Sheet1.csv", "947", 1,
            "Тема — диноленд! Вы должны победить босса в дальнем\n"
            "конце за отведенное время! Вот подсказка о боссе: его\n"
            "Сильные челюсти прогрызут даже самую прочную броню.",
            "Тема — мир динозавров! Доберитесь\n"
            "до дальнего конца и победите босса\n"
            "за отведённое время. Подсказка: его челюсти\n"
            "прогрызают даже самую прочную броню.",
        ),
        (
            "patch_text01", "text/quest_outline.mbe/000_Sheet1.csv", "948", 1,
            "Тема - мания насекомых! Вы должны победить босса в\n"
            "дальнем конце за отведенное время! Вот подсказка о\n"
            "Боссе: это Монарх насекомых, живущих в темном лесу.",
            "Тема — царство насекомых! Доберитесь\n"
            "до дальнего конца и победите босса\n"
            "за отведённое время. Подсказка:\n"
            "босс — монарх насекомых из тёмного леса.",
        ),
        (
            "patch_text01", "text/quest_outline.mbe/000_Sheet1.csv", "950", 1,
            "Защитите лучшее гигантское ДигиМясо от дигимонов!\n"
            "Летающих дигимонов легко не заметить, так что будьте осторожны!\n"
            "Победите всех врагов — и вы выиграете!",
            "Защитите гигантское ДигиМясо от дигимонов!\n"
            "Летающих дигимонов легко не заметить,\n"
            "так что будьте осторожны. Победите всех\n"
            "врагов — и победа ваша!",
        ),
        (
            "patch_text01", "text/quest_outline.mbe/000_Sheet1.csv", "951", 1,
            "Защитите лучшее гигантское ДигиМясо от дигимонов!\n"
            "Остерегайтесь вспыльчивых дигимонов: они будут атаковать вас.\n"
            "Победите всех врагов — и вы выиграете!",
            "Защитите гигантское ДигиМясо от дигимонов!\n"
            "Берегитесь вспыльчивых дигимонов:\n"
            "они будут нападать на вас. Победите всех\n"
            "врагов — и победа ваша!",
        ),
        (
            "patch_text01", "text/quest_outline.mbe/000_Sheet1.csv", "952", 1,
            "Защитите лучшее гигантское ДигиМясо от дигимонов!\n"
            "Особое внимание обратите на СкаллМаммона: он медлительный,\n"
            "но очень выносливый. Победите всех врагов — и вы выиграете!",
            "Защитите гигантское ДигиМясо от дигимонов!\n"
            "Берегитесь СкаллМаммона: он медлителен,\n"
            "но очень вынослив. Победите всех врагов —\n"
            "и победа ваша!",
        ),
        (
            "patch_text01", "text/quest_outline.mbe/000_Sheet1.csv", "953", 1,
            "Защитите лучшее гигантское ДигиМясо от дигимонов!\n"
            "Остерегайтесь резких рывков летающих дигимонов.\n"
            "Победите всех врагов — и вы выиграете!",
            "Защитите гигантское ДигиМясо от дигимонов!\n"
            "Берегитесь резких рывков летающих\n"
            "дигимонов. Победите всех врагов —\n"
            "и победа ваша!",
        ),
    ]
)


FARM_OLD = (
    "Предмет для Дигифермы.\n"
    "Используйте его, чтобы оформить Дигиферму по своему вкусу."
)
FARM_NEW = (
    "Предмет для Дигифермы.\n"
    "Разместите его по своему вкусу."
)

MAIN_FARM_IDS = [
    *map(str, range(20001, 20016)),
    *map(str, range(20100, 20117)),
    "20300",
    "20301",
    "20500",
    *map(str, range(20502, 20529)),
    *map(str, range(20532, 20550)),
    *map(str, range(20605, 20623)),
    *map(str, range(22001, 22006)),
]

FARM_GROUPS: list[tuple[str, str, list[str]]] = [
    (
        "patch_text01",
        "text/item_explanation.mbe/000_Sheet1.csv",
        MAIN_FARM_IDS,
    ),
    (
        "addcont_05_text01",
        "text/item_explanation_dlc05.mbe/000_Sheet1.csv",
        ["23002"],
    ),
    (
        "addcont_07_text01",
        "text/item_explanation_dlc07.mbe/000_Sheet1.csv",
        ["23001"],
    ),
]


def read_document(path: Path) -> tuple[list[list[str]], str, bool]:
    raw = path.read_bytes()
    encoding = "utf-8-sig" if raw.startswith(b"\xef\xbb\xbf") else "utf-8"
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.reader(handle))
    physical = raw.removeprefix(b"\xef\xbb\xbf").splitlines()
    quote_all_after_header = len(physical) > 1 and physical[1].startswith(b'"')
    return rows, encoding, quote_all_after_header


def write_document(
    path: Path,
    rows: list[list[str]],
    encoding: str,
    quote_all_after_header: bool,
) -> None:
    with path.open("w", encoding=encoding, newline="") as handle:
        if quote_all_after_header:
            csv.writer(handle, lineterminator="\n").writerow(rows[0])
            csv.writer(handle, lineterminator="\n", quoting=csv.QUOTE_ALL).writerows(rows[1:])
        else:
            csv.writer(handle, lineterminator="\n").writerows(rows)


def main() -> None:
    if len(MAIN_FARM_IDS) != 103 or len(set(MAIN_FARM_IDS)) != 103:
        raise SystemExit("Invalid main Digifarm fixture list")

    documents: dict[tuple[str, str], list[list[str]]] = {}
    formats: dict[tuple[str, str], tuple[str, bool]] = {}
    dirty: set[tuple[str, str]] = set()

    def get_document(package: str, relative: str) -> list[list[str]]:
        marker = (package, relative)
        if marker not in documents:
            path = CSV_ROOT / package / relative
            rows, encoding, quote_all = read_document(path)
            documents[marker] = rows
            formats[marker] = (encoding, quote_all)
        return documents[marker]

    exact_changed = exact_current = 0
    for package, relative, row_id, column, old, new in EXACT_UPDATES:
        rows = get_document(package, relative)
        matches = [row for row in rows if row and row[0] == row_id]
        if len(matches) != 1 or len(matches[0]) <= column:
            raise SystemExit(f"Missing or ambiguous row {package}:{relative}:{row_id}")
        row = matches[0]
        if row[column] == new:
            exact_current += 1
        elif row[column] == old:
            row[column] = new
            exact_changed += 1
            dirty.add((package, relative))
        else:
            raise SystemExit(
                f"Unexpected text {package}:{relative}:{row_id}: {row[column]!r}"
            )

    farm_changed = farm_current = 0
    farm_targets: set[tuple[str, str, str]] = set()
    for package, relative, row_ids in FARM_GROUPS:
        rows = get_document(package, relative)
        for row_id in row_ids:
            target = (package, relative, row_id)
            if target in farm_targets:
                raise SystemExit(f"Duplicate Digifarm target: {target}")
            farm_targets.add(target)
            matches = [row for row in rows if row and row[0] == row_id]
            if len(matches) != 1 or len(matches[0]) <= 1:
                raise SystemExit(f"Missing or ambiguous Digifarm row {target}")
            row = matches[0]
            if row[1] == FARM_NEW:
                farm_current += 1
            elif row[1] == FARM_OLD:
                row[1] = FARM_NEW
                farm_changed += 1
                dirty.add((package, relative))
            else:
                raise SystemExit(f"Unexpected Digifarm text {target}: {row[1]!r}")

    if len(farm_targets) != 105:
        raise SystemExit(f"Expected 105 Digifarm targets, found {len(farm_targets)}")

    for marker in sorted(dirty):
        package, relative = marker
        encoding, quote_all = formats[marker]
        write_document(
            CSV_ROOT / package / relative,
            documents[marker],
            encoding,
            quote_all,
        )

    print(f"Quest overview targets: {len(EXACT_UPDATES)}")
    print(f"Quest overview changed: {exact_changed}")
    print(f"Quest overview already current: {exact_current}")
    print(f"Digifarm targets: {len(farm_targets)}")
    print(f"Digifarm changed: {farm_changed}")
    print(f"Digifarm already current: {farm_current}")
    print(f"Files written: {len(dirty)}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Fix source-confirmed Digimon gender inconsistencies.

The pass is row-addressed and fail-closed.  It covers recurring story
characters whose gender is explicit in the English script (Lady/her/Lord/his)
or unambiguous from their own surrounding Russian dialogue.  Generic species
are not assigned one global gender because separate NPCs can share a speaker
ID in unrelated scenes.
"""

from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CSV_ROOT = ROOT / "csv"
DATASET = ROOT / "exports/dynamic_gender_confirmed_variants_v066.csv"


UPDATES: dict[tuple[str, str, str], tuple[str, str]] = {
    ("patch_text01", "message/battle.mbe/000_Sheet1.csv", "1190130002"): (
        "Даже если это подделка... Я уверен, что это все равно будет\nтрудный бой!",
        "Даже если это подделка... Я уверена, что бой всё равно будет\nтрудным!",
    ),
    ("patch_text01", "message/d06.mbe/000_Sheet1.csv", "f_d0603_0030_0040"): (
        "Фух, я думал, мне конец! Ах, лорд Титамон...",
        "Фух, я думала, мне конец! Ах, лорд Титамон...",
    ),
    ("patch_text01", "message/d09.mbe/000_Sheet1.csv", "f_d0907_0010_0030"): (
        "Теперь я Церемонный медиум, Бахусмон. Спасибо, что присматривал\n"
        "за мной все те годы, когда я был всего лишь молодым деревцем.",
        "Теперь я Сересмон Медиум, Бахусмон. Спасибо, что присматривал\n"
        "за мной все те годы, когда я была ещё молодым деревцем.",
    ),
    (
        "patch_text01",
        "message/digimon_chat.mbe/000_Sheet1.csv",
        "mari_001_1_reaction_char_MARINEANGEMON",
    ): (
        "Смелости... Я уверен, что мне ее не хватает. Но я чувствую, что\n"
        "могу ее обрести, оставаясь рядом с тобой!",
        "Смелости... Уверена, именно её мне и не хватает. Но рядом\n"
        "с тобой я чувствую, что смогу её обрести!",
    ),
    (
        "patch_text01",
        "message/digimon_chat.mbe/000_Sheet1.csv",
        "lala_001_4_reaction_char_LALAMON",
    ): (
        "Хохо. Даже не близко. Но если ты так сильно этого хочешь, я был\n"
        "бы рад нежно напеть тебе.",
        "Хо-хо. Совсем мимо. Но раз ты так просишь,\n"
        "я буду рада тихонько тебе напеть.",
    ),
    (
        "patch_text01",
        "message/digimon_chat.mbe/000_Sheet1.csv",
        "roto_001_4_reaction_char_LOTOSMON",
    ): (
        "Я рад. Продолжай смотреть на меня, и я исполню все твои\n"
        "счастливые мечты.",
        "Я рада. Продолжай любоваться мной — и я исполню\n"
        "все твои счастливые мечты.",
    ),
    ("patch_text01", "message/h06.mbe/000_Sheet1.csv", "f_h0601_0010_0050"): (
        "Здесь нет такого понятия, как здравый смысл... Но что-то не так!\n"
        "Я уверен, вы это чувствуете... Не упустите это.",
        "Здесь нет такого понятия, как здравый смысл... Но что-то не так!\n"
        "Я уверена, вы это чувствуете... Не упустите это.",
    ),
    ("patch_text01", "message/m170.mbe/000_Sheet1.csv", "m170_065_150"): (
        "Тебе не обязательно быть таким. Я просто сделал то, что считал\nправильным.",
        "Тебе не обязательно быть таким. Я просто сделала то,\nчто считала правильным.",
    ),
    ("patch_text01", "message/s020_173.mbe/000_Sheet1.csv", "s020_173_010"): (
        "Я хотел стать звездой во всем цифровом мире, поэтому покинул\n"
        "море, чтобы работать здесь.",
        "Я хотела стать звездой всего Цифрового мира,\n"
        "поэтому покинула море и приехала работать сюда.",
    ),
    ("patch_text01", "message/s020_173.mbe/000_Sheet1.csv", "s020_173_220"): (
        "Не смей мне этого говорить! Я хотел, чтобы ты достал мне морской\n"
        "воды из океанских глубин!",
        "Не смей так говорить! Я хотела, чтобы ты принёс мне\n"
        "морскую воду из океанских глубин!",
    ),
    ("patch_text01", "message/s020_173.mbe/000_Sheet1.csv", "s020_173_350"): (
        "Ни единого шанса! Это все равно что сдаться только потому, что\n"
        "все пошло не так, как я хотел!",
        "Ни за что! Сдаться лишь потому, что всё пошло наперекосяк?",
    ),
    ("patch_text01", "message/s020_173.mbe/000_Sheet1.csv", "s020_173_390"): (
        "Я был так уверен, что ветры, завывающие далеко за морем, унесут\n"
        "мое одиночество прочь...",
        "Я была уверена, что ветры далёких морей унесут\n"
        "моё одиночество прочь...",
    ),
    ("patch_text01", "message/s020_173.mbe/000_Sheet1.csv", "s020_173_420"): (
        "Возможно, это было бы лучше всего. Вместо того, чтобы страдать\n"
        "из-за своей гордости, я должен отправиться туда, где я мечтаю быть.",
        "Возможно, так будет лучше. Чем страдать из-за гордости,\n"
        "я должна отправиться туда, где мечтаю быть.",
    ),
    ("patch_text01", "message/s020_173.mbe/000_Sheet1.csv", "s020_173_480"): (
        "О! Так это от тебя морская вода.\nБлагодаря тебе я решил вернуться домой.",
        "О! Так это от тебя морская вода.\nБлагодаря тебе я решила вернуться домой.",
    ),
    ("patch_text01", "message/s200_148.mbe/000_Sheet1.csv", "s200_148_390"): (
        "Да... ты прав! Может, люди не так страшны, как я думал?",
        "Да... ты прав! Может, люди не так страшны, как я думала?",
    ),
    ("patch_text01", "message/s030_031.mbe/000_Sheet1.csv", "s030_031_100"): (
        "Я так и думал! Это замечательно!",
        "Я так и думала! Это замечательно!",
    ),
    ("patch_text01", "message/d07.mbe/000_Sheet1.csv", "f_d0701_0010_0070"): (
        "Давай, глурп. Я готова к этому! Сделай мне настоящий, сладкий\n"
        "стон! Такой, от которого у меня скривится лицо, глурп!",
        "Давай, глурп. Я готов! Выдай самую приторную банальность,\n"
        "от которой лицо само скривится, глурп!",
    ),
    ("patch_text01", "message/s110_108.mbe/000_Sheet1.csv", "s110_108_800"): (
        "Я чувствую, что мой нынешний размер подходит мне лучше всего. Я\n"
        "сделаю все, что смогу, теперь, когда я вернулась к нормальной жизни.",
        "Мне кажется, мой обычный размер подходит лучше всего.\n"
        "Теперь, когда я вернулся в норму, я сделаю всё, что смогу.",
    ),
    ("patch_text01", "message/d09.mbe/000_Sheet1.csv", "f_d0903_0200_0010"): (
        "Сиренмон был бы недоволен, если бы увидел, что ты спишь здесь,\n"
        "лорд Бахусмон! Тебе следовало бы... *ворчать, ворчать*",
        "Сиренмон была бы недовольна, если бы увидела, что ты спишь здесь,\n"
        "лорд Бахусмон! Тебе следовало бы... *ворчит, ворчит*",
    ),
    ("addcont_01_text01", "message/d120.mbe/000_Sheet1.csv", "d120_110_090"): (
        "Как я уже сказал, он «раньше был моим отцом».",
        "Как я уже сказала, он «раньше был моим отцом».",
    ),
}


DATASET_UPDATE = {
    "package": "patch_text01",
    "file": "message/s200_148.mbe/000_Sheet1.csv",
    "base_id": "s200_148_390",
    "old_male": "Да... ты прав! Может, люди не так страшны, как я думал?",
    "old_female": "Да... ты права! Может, люди не так страшны, как я думал?",
    "new_male": "Да... ты прав! Может, люди не так страшны, как я думала?",
    "new_female": "Да... ты права! Может, люди не так страшны, как я думала?",
}


def read_rows(path: Path) -> list[list[str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.reader(handle))


def write_rows(path: Path, rows: list[list[str]]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        csv.writer(handle, lineterminator="\n").writerows(rows)


def apply_messages() -> tuple[int, int]:
    grouped: dict[tuple[str, str], list[tuple[str, str, str]]] = defaultdict(list)
    for (package, relative, row_id), (old, new) in UPDATES.items():
        grouped[(package, relative)].append((row_id, old, new))
    changed = current = 0
    for (package, relative), updates in sorted(grouped.items()):
        path = CSV_ROOT / package / relative
        rows = read_rows(path)
        by_id = {row[0]: row for row in rows if row}
        file_changed = False
        for row_id, old, new in updates:
            row = by_id.get(row_id)
            if row is None or len(row) < 3:
                raise ValueError(f"missing row {package}/{relative}:{row_id}")
            if row[2] == new:
                current += 1
                continue
            if row[2] != old:
                raise ValueError(
                    f"unexpected text {package}/{relative}:{row_id}\n"
                    f"expected={old!r}\nactual={row[2]!r}"
                )
            row[2] = new
            changed += 1
            file_changed = True
        if file_changed:
            write_rows(path, rows)
    return changed, current


def apply_dataset() -> tuple[int, int]:
    with DATASET.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    with DATASET.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        fieldnames = reader.fieldnames
    if not fieldnames:
        raise ValueError("dynamic gender dataset has no header")
    match = next(
        (
            row
            for row in rows
            if row["package"] == DATASET_UPDATE["package"]
            and row["file"] == DATASET_UPDATE["file"]
            and row["base_id"] == DATASET_UPDATE["base_id"]
        ),
        None,
    )
    if match is None:
        raise ValueError("dynamic Palmon row is missing")
    current_pair = (
        match["male_protagonist_text"],
        match["female_protagonist_text"],
    )
    new_pair = (DATASET_UPDATE["new_male"], DATASET_UPDATE["new_female"])
    if current_pair == new_pair:
        return 0, 1
    old_pair = (DATASET_UPDATE["old_male"], DATASET_UPDATE["old_female"])
    if current_pair != old_pair:
        raise ValueError(f"unexpected dynamic Palmon texts: {current_pair!r}")
    match["male_protagonist_text"], match["female_protagonist_text"] = new_pair
    with DATASET.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    return 1, 0


def main() -> None:
    changed, current = apply_messages()
    dataset_changed, dataset_current = apply_dataset()
    longest = max(len(line) for _, new in UPDATES.values() for line in new.splitlines())
    print(f"Message targets: {len(UPDATES)}")
    print(f"Message changed: {changed}")
    print(f"Message already current: {current}")
    print(f"Dataset changed: {dataset_changed}")
    print(f"Dataset already current: {dataset_current}")
    print(f"Longest replacement line: {longest}")


if __name__ == "__main__":
    main()

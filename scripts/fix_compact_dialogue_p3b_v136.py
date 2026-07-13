#!/usr/bin/env python3
"""Apply the manually reviewed second block of compact-dialogue P3 fixes."""

from __future__ import annotations

from pathlib import Path

from fix_reported_sidequests_v120 import digest, read_document, write_document


ROOT = Path(__file__).resolve().parents[1]
CSV_ROOT = ROOT / "csv"

UPDATES: list[tuple[str, str, str, int, str, str]] = [
    ("patch_text01", "message/arena01.mbe/000_Sheet1.csv", "arena01_f001_012_030", 2,
     "3b83bbf9404d5f41dae2b0d0e155ee29040daf10f1ef283702be5e260f7e5504",
     "Что на этот раз случилось с Суперстармоном?.. Постойте!\n"
     "Теперь у нас истинный царь — блистательный Фараомон!"),
    ("patch_text01", "message/d03.mbe/000_Sheet1.csv", "f_d0302_0020_0020", 2,
     "d593b7ed1ecdc546748cf733332642d744004794647f4c6658153befef45262d",
     "Фех, ну и дела. Не сомневайтесь: мы каждый раз\n"
     "даём этим прохвостам отпор. И всё же...!"),
    ("patch_text01", "message/d13.mbe/000_Sheet1.csv", "f_d1301_0360_0010", 2,
     "81c7976a7fe5e84c6b8954b28294bf5a525dcf17bfa417413cc81b044cf0b516",
     "Там держат Вулканусмона, но сначала мне нужно\n"
     "перезаписать ID этой ключ-карты. Иначе дверь не открыть."),
    ("patch_text01", "message/m120.mbe/000_Sheet1.csv", "m120_100_050", 2,
     "de95bd74026749687d872550a52cfe8c59a310475b53e1bb85702853f101e74f",
     "Пока это лишь рабочая теория, но мы считаем, что большинство\n"
     "аномалий вызвано дигимонами..."),
    ("patch_text01", "message/m210.mbe/000_Sheet1.csv", "m210_050_030", 2,
     "0295aaaebcea6440a5f0c9076e0964bc73c3ac48e121bf2219d468f43208fd03",
     "То самое возмущение породило аномалию,\n"
     "стеревшую из реальности твоего приёмного отца, доктора Юки."),
    ("patch_text01", "message/m330.mbe/000_Sheet1.csv", "m330_010_166", 2,
     "4ad2dfe35e0d8ca2af2e03106ddd144327ffad53ead16aefacbc4575bdec0549",
     "Прошу вас прикрыть нас с тыла, пока мы заняты другим делом!\n"
     "За подробностями обратитесь к доктору Симмонс."),
    ("patch_text01", "message/t03.mbe/000_Sheet1.csv", "f_t0302_0130_0010", 2,
     "3781e81295b207af3e73f923115946ae93b2204e057ffa3842c5fd477c251b31",
     "Учёная из службы общественной безопасности, значит?\n"
     "Если она видный специалист, о ней должны быть открытые сведения."),
    ("addcont_03_text01", "message/d330.mbe/000_Sheet1.csv", "d330_050_040", 2,
     "e91dd50fb731f9cce2eef17c67d7107c9b3613b159ffed721b190b9c188bf894",
     "Ваши «принципы» в лучшем случае взяты с потолка!\n"
     "Неужели вы не видите, насколько всё это порочно?"),
    ("patch_text01", "message/m390.mbe/000_Sheet1.csv", "m390_020_090", 2,
     "825d254df290e59e932e81fe17a384df0012f7fc3fa016cd50faf2a79b16a8b8",
     "Будь я умнее... разработала бы лекарство\n"
     "от человеческой глупости..."),
    ("patch_text01", "message/arena01.mbe/000_Sheet1.csv", "arena01_m310_010_040", 2,
     "cc3a5773bf21ac01fa2c312c60acc1f7d17ebbde75d6f4d45bc2f4d68f4ac739",
     "Не повезло вам: в первые соперники достались именно мы!\n"
     "Постарайтесь не отставать!"),
    ("patch_text01", "message/d12.mbe/000_Sheet1.csv", "f_d1205_0240_0030", 2,
     "179b865ef3a123140c2f24ff10fc5350996ca987f87db5ae405e9fab6c0f7b32",
     "Но, как я слышал, в последнее время они страшно враждуют\n"
     "и из-за этого забыли о долге правителей."),
    ("patch_text01", "message/m350.mbe/000_Sheet1.csv", "m350_020_150", 2,
     "863cbb8f12c55a8f1dd7fb82b9dae15dfd9d0caa1bbbaf40b42b110f1603c581",
     "Ты здесь без остальных... Что-то случилось?\n"
     "Хочешь поговорить со мной?"),
    ("patch_text01", "message/s080_059.mbe/000_Sheet1.csv", "s080_059_370", 2,
     "4ea4a23bbf81095504906665f23bea18d489e9d3431daf5f7059918181b4be1b",
     "Наверняка туда можно добраться,\n"
     "но нужного снаряжения у меня пока нет."),
    ("patch_text01", "message/s910_169.mbe/000_Sheet1.csv", "s910_169_770", 2,
     "81bd1f5cb008b3499d70737930646066a76130cbbcaa282429f9950f4f0ee44d",
     "Ке-хе-хе. Твой голос дрожит. Я-то знаю: тебе страшно."),
    ("patch_text01", "message/s910_171.mbe/000_Sheet1.csv", "s910_171_1230", 2,
     "830b3d0757e4711d00ff5ef0277ddcff31ee28fd8d1dfb2ed94bf2e3146de5c5",
     "Дай ему время. Нелегко человеку принять столько всего сразу."),
    ("patch_text01", "message/t01.mbe/000_Sheet1.csv", "f_t0108_0110_0030", 2,
     "57d244495b2fee5e618d620172747fd6976eecd84951f57e0b36aed9b90fd2d7",
     "Единственная проблема — энергоснабжение.\n"
     "Из-за спешки с подготовкой возникли перебои."),
]


def main() -> None:
    documents: dict[tuple[str, str], list[list[str]]] = {}
    formats: dict[tuple[str, str], tuple[str, bool]] = {}
    dirty: set[tuple[str, str]] = set()
    changed = current = 0
    for package, relative, row_id, column, expected_hash, replacement in UPDATES:
        marker = (package, relative)
        path = CSV_ROOT / package / relative
        if marker not in documents:
            rows, encoding, quote_all = read_document(path)
            documents[marker] = rows
            formats[marker] = (encoding, quote_all)
        matches = [row for row in documents[marker] if row and row[0] == row_id]
        if len(matches) != 1 or len(matches[0]) <= column:
            raise SystemExit(f"Missing or ambiguous row {package}:{relative}:{row_id}")
        row = matches[0]
        if row[column] == replacement:
            current += 1
        elif digest(row[column]) == expected_hash:
            row[column] = replacement
            changed += 1
            dirty.add(marker)
        else:
            raise SystemExit(f"Unexpected text {package}:{relative}:{row_id}: {row[column]!r}")
    for marker in sorted(dirty):
        package, relative = marker
        encoding, quote_all = formats[marker]
        write_document(CSV_ROOT / package / relative, documents[marker], encoding, quote_all)
    print(f"Targets: {len(UPDATES)}")
    print(f"Changed: {changed}")
    print(f"Already current: {current}")
    print(f"Files written: {len(dirty)}")


if __name__ == "__main__":
    main()

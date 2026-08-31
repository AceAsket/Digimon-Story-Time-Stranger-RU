from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATASET = ROOT / "exports" / "dynamic_gender_confirmed_variants_v066.csv"

FIELDS = (
    "package",
    "file",
    "base_id",
    "role",
    "male_protagonist_text",
    "female_protagonist_text",
    "confidence",
    "basis",
)


# These rows became deliberately gender-neutral during the final prose pass.
# Keeping them in the runtime registry would restore the older wording the next
# time the M/F rows are generated.
REMOVE_IDS = {
    "m050_010_072",
    "m050_010_120",
    "m060_150_100",
    "m070_100_010",
    "m080_020_070",
    "m080_040_030",
    "m090_010_010",
    "m090_010_050",
    "m090_030_040",
    "m100_060_020",
    "m120_040_010",
    "m120_060_100",
    "m210_030_132",
    "m340_020_160",
    "m360_070_100",
    "m420_030_020",
    "m420_030_030",
    "m420_030_050",
    "m420_070_030",
    "m420_080_070",
    "m420_100_080",
    "m420_100_090",
}


# Retained variants whose surrounding prose was polished after the original
# reviewed dataset was created.  Values remain protagonist-oriented.
UPDATE_TEXTS = {
    "f_d0404_0130_0010": (
        "Ты! Ты был в Центральном городе!.. Эй, тебе не кажется, что вон\n"
        "тот дигимон такой клёвый?",
        "Ты! Ты была в Центральном городе!.. Эй, тебе не кажется, что вон\n"
        "тот дигимон такой клёвый?",
    ),
    "f_d0604_0350_0010": (
        "Гех-гех-гех... Ты это видел? Я задал этим ангельским дигимонам\n"
        "хорошую трепку!",
        "Гех-гех-гех... Ты это видела? Я задал этим ангельским дигимонам\n"
        "хорошую трепку!",
    ),
    "m210_030_120": (
        "Ч-что случилось? Тебе явно больно... Ты не пострадал?",
        "Ч-что случилось? Тебе явно больно... Ты не пострадала?",
    ),
    "m210_033_020": (
        "Тебе явно больно... Ты не пострадал?",
        "Тебе явно больно... Ты не пострадала?",
    ),
    "m260_080_310": (
        "Ты уверен, что это хорошая идея? Если мы не пойдём, вместо нас,\n"
        "вероятно, придётся идти Венусмон.",
        "Ты уверена, что это хорошая идея? Если мы не пойдём, вместо нас,\n"
        "вероятно, придётся идти Венусмон.",
    ),
    "s020_019_320": (
        "Ну что? Ты готов спасти этого пойманного в ловушку дигимона? Мне\n"
        "нужно, чтобы ты показал мне дорогу.",
        "Ну что? Ты готова спасти этого пойманного в ловушку дигимона? Мне\n"
        "нужно, чтобы ты показала мне дорогу.",
    ),
    "s070_056_320": (
        "А, ты вернулся. Ну что? Ты нашёл для меня достойного дигимона?",
        "А, ты вернулась. Ну что? Ты нашла для меня достойного дигимона?",
    ),
}


ADDITIONS = (
    {
        "package": "patch_text01",
        "file": "message/m140.mbe/000_Sheet1.csv",
        "base_id": "m140_100_060",
        "role": "operator",
        "male_protagonist_text": (
            "Я почти уверена, что это связано с Адом Синдзюку: он тоже был\n"
            "вызван конфликтом между дигимонами."
        ),
        "female_protagonist_text": (
            "Я почти уверен, что это связано с Адом Синдзюку: он тоже был\n"
            "вызван конфликтом между дигимонами."
        ),
        "confidence": "1.00",
        "basis": "operator_self_opposite_to_player",
    },
    {
        "package": "patch_text01",
        "file": "message/m390.mbe/000_Sheet1.csv",
        "base_id": "m390_010_010",
        "role": "player_address",
        "male_protagonist_text": "Хм? Сегодня ты один? Где остальные двое?",
        "female_protagonist_text": "Хм? Сегодня ты одна? Где остальные двое?",
        "confidence": "1.00",
        "basis": "scene_context_player_address",
    },
    {
        "package": "patch_text01",
        "file": "message/m390.mbe/000_Sheet1.csv",
        "base_id": "m390_060_030",
        "role": "player_address",
        "male_protagonist_text": "Ты ведь видел всё это много раз, правда, {player}?",
        "female_protagonist_text": "Ты ведь видела всё это много раз, правда, {player}?",
        "confidence": "1.00",
        "basis": "explicit_player_name",
    },
)


def read_dataset() -> list[dict[str, str]]:
    with DATASET.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != FIELDS:
            raise ValueError(f"unexpected dataset columns: {reader.fieldnames}")
        return list(reader)


def write_dataset(rows: list[dict[str, str]]) -> None:
    with DATASET.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    rows = read_dataset()
    original_count = len(rows)
    by_id = {row["base_id"]: row for row in rows}

    missing_remove = sorted(REMOVE_IDS - by_id.keys())
    missing_update = sorted(UPDATE_TEXTS.keys() - by_id.keys())
    duplicate_add = sorted(row["base_id"] for row in ADDITIONS if row["base_id"] in by_id)
    if missing_remove or missing_update or duplicate_add:
        raise ValueError(
            f"dataset precondition failed: missing_remove={missing_remove}, "
            f"missing_update={missing_update}, duplicate_add={duplicate_add}"
        )

    rows = [row for row in rows if row["base_id"] not in REMOVE_IDS]
    for row in rows:
        texts = UPDATE_TEXTS.get(row["base_id"])
        if texts:
            row["male_protagonist_text"], row["female_protagonist_text"] = texts
    rows.extend(dict(row) for row in ADDITIONS)
    rows.sort(key=lambda row: (row["package"], row["file"], row["base_id"]))

    if len({(row["package"], row["file"], row["base_id"]) for row in rows}) != len(rows):
        raise ValueError("duplicate dynamic-gender dataset key after update")
    write_dataset(rows)

    print(f"dataset rows: {original_count} -> {len(rows)}")
    print(f"neutral variants removed: {len(REMOVE_IDS)}")
    print(f"polished variants updated: {len(UPDATE_TEXTS)}")
    print(f"missed variants added: {len(ADDITIONS)}")


if __name__ == "__main__":
    main()

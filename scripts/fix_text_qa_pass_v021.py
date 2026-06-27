from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CSV_ROOTS = [
    ROOT / "csv" / "app_text01",
    ROOT / "csv" / "patch_text01",
]


TARGETED_ROWS: dict[tuple[str, str], str] = {
    ("message/battle.mbe/000_Sheet1.csv", "1200020186"): (
        "Прямо в сердце!"
    ),
    ("message/digimon_chat.mbe/000_Sheet1.csv", "agu_001_0_char_AGUMON"): (
        "Хочу стать обаятельным маскотом! Как мне всем понравиться?"
    ),
    ("message/digimon_chat.mbe/000_Sheet1.csv", "agu_001_1_replay"): (
        "Сделай что-нибудь смелое!"
    ),
    ("message/digimon_chat.mbe/000_Sheet1.csv", "agu_001_1_reaction_char_AGUMON"): (
        "Всем нравятся зрелища, да? Может, прыгну с тарзанкой\n"
        "или устрою испытание на смелость!"
    ),
    ("message/digimon_chat.mbe/000_Sheet1.csv", "agu_001_2_replay"): (
        "Покажи, что умеешь думать."
    ),
    ("message/digimon_chat.mbe/000_Sheet1.csv", "agu_001_2_reaction_char_AGUMON"): (
        "Людям нравятся умники-викторинщики, да! Ладно, пора\n"
        "засесть за учебники и стать знатоком!"
    ),
    ("message/digimon_chat.mbe/000_Sheet1.csv", "agu_001_3_replay"): (
        "Я расскажу о тебе всем."
    ),
    ("message/digimon_chat.mbe/000_Sheet1.csv", "agu_001_3_reaction_char_AGUMON"): (
        "Ты правда расскажешь обо мне? Вот это по-дружески!\n"
        "Рассчитываю на тебя!"
    ),
    ("message/digimon_chat.mbe/000_Sheet1.csv", "agu_001_4_replay"): (
        "Тебя любят таким, какой ты есть."
    ),
    ("message/digimon_chat.mbe/000_Sheet1.csv", "agu_001_4_reaction_char_AGUMON"): (
        "Мне хорошо таким, какой я есть...? Знаешь, похоже,\n"
        "ты дело говоришь. Ура, я так рад!"
    ),
    ("message/m030.mbe/000_Sheet1.csv", "m030_080_010"): (
        "Хм... Похоже, у нас снова неприятности."
    ),
    ("message/m040.mbe/000_Sheet1.csv", "m040_050_080"): (
        "Говорят, здесь творятся странные вещи. Если сниму их на видео,\n"
        "ролик может разлететься по сети..."
    ),
    ("message/m040.mbe/000_Sheet1.csv", "m040_050_130"): (
        "Давайте исследовать эти явления вместе!\n"
        "Помогите ОккультТокио ТВ набрать просмотры!"
    ),
    ("message/m040.mbe/000_Sheet1.csv", "m040_050_220"): (
        "Значит... всё было прямо как во время того инцидента..."
    ),
    ("message/t03.mbe/000_Sheet1.csv", "f_t0303_0130_0080"): (
        "Ладно, идёмте искать моего непослушного ребёнка!"
    ),
    ("text/char_name.mbe/000_Sheet1.csv", "char_HIROKO_nickname"): (
        "Начинающий стример"
    ),
    ("text/item_name.mbe/000_Sheet1.csv", "28"): (
        "Второе дыхание"
    ),
    ("text/item_ruby.mbe/000_Sheet1.csv", "28"): (
        "Второе дыхание"
    ),
    ("text/skill_name.mbe/000_Sheet1.csv", "30034"): (
        "Пламенный всполох I"
    ),
    ("text/skill_name.mbe/000_Sheet1.csv", "30035"): (
        "Пламенный всполох II"
    ),
    ("text/skill_name.mbe/000_Sheet1.csv", "30036"): (
        "Пламенный всполох III"
    ),
    ("text/skill_ruby.mbe/000_Sheet1.csv", "30034"): (
        "Пламенный всполох I"
    ),
    ("text/skill_ruby.mbe/000_Sheet1.csv", "30035"): (
        "Пламенный всполох II"
    ),
    ("text/skill_ruby.mbe/000_Sheet1.csv", "30036"): (
        "Пламенный всполох III"
    ),
    ("text/jogress_skill_name.mbe/000_Sheet1.csv", "30034"): (
        "Пламенный всполох I"
    ),
    ("text/jogress_skill_name.mbe/000_Sheet1.csv", "30035"): (
        "Пламенный всполох II"
    ),
    ("text/jogress_skill_name.mbe/000_Sheet1.csv", "30036"): (
        "Пламенный всполох III"
    ),
    ("text/common_message.mbe/000_Sheet1.csv", "130"): (
        "Гости"
    ),
    ("text/common_message.mbe/000_Sheet1.csv", "132"): (
        "Боевой состав"
    ),
    ("text/common_message.mbe/000_Sheet1.csv", "133"): (
        "Гость"
    ),
    ("text/common_message.mbe/000_Sheet1.csv", "139"): (
        "Резерв"
    ),
    ("text/common_message.mbe/000_Sheet1.csv", "153"): (
        "Боевой состав"
    ),
    ("text/common_message.mbe/000_Sheet1.csv", "154"): (
        "Резерв"
    ),
    ("text/common_message.mbe/000_Sheet1.csv", "601"): (
        "Бой"
    ),
    ("text/common_message.mbe/000_Sheet1.csv", "602"): (
        "Резерв"
    ),
    ("text/common_message.mbe/000_Sheet1.csv", "120101"): (
        "Боевые дигимоны"
    ),
    ("text/common_message.mbe/000_Sheet1.csv", "120102"): (
        "Резервные дигимоны"
    ),
    ("text/common_message.mbe/000_Sheet1.csv", "150102"): (
        "Резерв"
    ),
    ("text/common_message.mbe/000_Sheet1.csv", "ui_battle_target_0010"): (
        "{is24}{sub1} Сменить на резерв"
    ),
    ("text/common_message.mbe/000_Sheet1.csv", "ui_item_list_0030"): (
        "Бой/резерв/гости"
    ),
    ("text/help_message.mbe/000_Sheet1.csv", "1100"): (
        "Просмотр характеристик дигимонов и настройка боевого состава."
    ),
    ("text/tutorial_title.mbe/000_Sheet1.csv", "tutorial_title_Change_01"): (
        "Боевой состав и резерв"
    ),
    ("text/tutorial_title.mbe/000_Sheet1.csv", "tutorial_title_PartyAegiomon_01"): (
        "Эгиомон: четвёртый боец"
    ),
    ("text/tutorial_explanation.mbe/000_Sheet1.csv", "tutorial_exp_Change_01_001"): (
        "Дигимоны в отряде делятся на три категории:\n\n"
        "{fc9Боевой состав}: выходят в бой с самого начала\n"
        "{fc9Резерв}: могут заменить бойцов во время сражения\n"
        "{fc9Гости}: временно присоединившиеся дигимоны, которые\n"
        "сражаются самостоятельно\n\n"
        "{fc9Меняйте боевой состав и резерв с учётом слабостей врага.}"
    ),
    ("text/key_help_text.mbe/000_Sheet1.csv", "key_help_0007"): (
        "Подробная информация"
    ),
    ("text/common_message.mbe/000_Sheet1.csv", "19027"): (
        "Открыть Дигивайс/Информация/Пропустить ролик"
    ),
    ("text/common_message_dx11.mbe/000_Sheet1.csv", "1019021"): (
        "Открыть Дигивайс/Информация/Пропустить ролик"
    ),
    ("text/skill_name.mbe/000_Sheet1.csv", "20501"): (
        "Малое пламя"
    ),
    ("text/skill_ruby.mbe/000_Sheet1.csv", "20501"): (
        "Малое пламя"
    ),
    ("text/jogress_skill_name.mbe/000_Sheet1.csv", "20501"): (
        "Малое пламя"
    ),
    ("text/jogress_skill_name.mbe/000_Sheet1.csv", "27611"): (
        "Малое пламя"
    ),
    ("text/jogress_skill_name.mbe/000_Sheet1.csv", "27621"): (
        "Малое пламя"
    ),
    ("text/jogress_skill_name.mbe/000_Sheet1.csv", "27631"): (
        "Малое пламя"
    ),
    ("text/jogress_skill_name.mbe/000_Sheet1.csv", "27641"): (
        "Малое пламя"
    ),
    ("text/jogress_skill_name.mbe/000_Sheet1.csv", "27651"): (
        "Малое пламя"
    ),
    ("text/digitter_message.mbe/000_Sheet1.csv", "hazama_99_080_2"): (
        "Их теперь называют «Агумон». Ещё они научились\n"
        "особому приёму под названием «Малое пламя»."
    ),
    ("text/digitter_message.mbe/000_Sheet1.csv", "hazama_99_060_1"): (
        "День 6 после прибытия. Коромон снова эволюционировал."
    ),
    ("text/digitter_message.mbe/000_Sheet1.csv", "hazama_99_060_2"): (
        "Теперь его зовут «Агумон». Ещё он освоил особый приём\n"
        "«Малое пламя»."
    ),
    ("text/digitter_message.mbe/000_Sheet1.csv", "hazama_99_060_3"): (
        "Пожалуй, пора дать ему сразиться с другими дигимонами.\n"
        "Но, как обычно, я не могу перестать умиляться, когда\n"
        "он набивает щёки ДигиМясом."
    ),
    ("text/tutorial_explanation.mbe/000_Sheet1.csv", "tutorial_exp_Analysis_01_001"): (
        "{fc9Режим анализа позволяет изучать врагов во время боя.}\n\n"
        "Вы можете посмотреть тип, стихию, слабости и устойчивости\n"
        "цели, а также проверить подробные сведения кнопкой {sub2}."
    ),
    ("text/tutorial_explanation.mbe/000_Sheet1.csv", "tutorial_exp_Personality_01_001"): (
        "Личность влияет на развитие дигимона и на то, какие\n"
        "характеристики чаще повышаются.\n\n"
        "Доблесть: легче растёт {fc9АТК}, физический атакующий тип.\n"
        "Дружелюбие: легче растёт {fc9ЗАЩ}, тип поддержки.\n"
        "Человеколюбие: легче растёт {fc9ДУХ}, лечащий тип.\n"
        "Мудрость: легче растёт {fc9ИНТ}, магический атакующий тип.\n\n"
        "{fc9Чтобы проверить личность, откройте статус дигимона и нажмите\n"
        "{sub2} для подробной информации.}"
    ),
    ("text/digimon_profile.mbe/000_Sheet1.csv", "digimon_0314_profile"): (
        "Плотоядный дигимон-растение с длинными лозами\n"
        "и огромной пастью. Этот злобный хищник\n"
        "источает сладкий аромат, приманивая мелких\n"
        "дигимонов, а затем опутывает их своими\n"
        "длинными лозами, похожими на щупальца.\n"
        "Однако Веджимону недостаёт боевой силы, и\n"
        "против крупных дигимонов он почти бессилен.\n"
        "Вырастая, он расцветает и приносит плоды."
    ),
}


def read_rows(path: Path) -> list[list[str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.reader(f))


def write_rows(path: Path, rows: list[list[str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, lineterminator="\n")
        writer.writerows(rows)


def text_column(relative: str, row: list[str]) -> int:
    if relative.startswith("message/") and len(row) > 2:
        return 2
    return 1


def apply_targeted_rows() -> list[str]:
    changed: list[str] = []
    by_file: dict[str, dict[str, str]] = {}
    for (relative, key), value in TARGETED_ROWS.items():
        by_file.setdefault(relative, {})[key] = value

    for root in CSV_ROOTS:
        if not root.exists():
            continue
        for relative, replacements in by_file.items():
            path = root / relative
            if not path.exists():
                continue
            rows = read_rows(path)
            touched = False
            for row in rows:
                if len(row) < 2:
                    continue
                value = replacements.get(row[0])
                if value is None:
                    continue
                index = text_column(relative, row)
                if len(row) <= index or row[index] == value:
                    continue
                row[index] = value
                touched = True
                changed.append(f"{root.name}/{relative}:{row[0]}")
            if touched:
                write_rows(path, rows)
    return changed


def main() -> None:
    changed = apply_targeted_rows()
    print(f"targeted_rows={len(changed)}")
    for item in changed:
        print(f"  {item}")


if __name__ == "__main__":
    main()

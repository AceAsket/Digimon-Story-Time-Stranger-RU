from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CSV_ROOT = ROOT / "csv"


def update_rows(rel_path: str, values: dict[str, str]) -> int:
    path = CSV_ROOT / rel_path
    with path.open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.reader(f))

    changed = 0
    for row in rows:
        if len(row) < 2:
            continue
        value = values.get(row[0])
        if value is not None and row[1] != value:
            row[1] = value
            changed += 1

    if changed:
        quoting = csv.QUOTE_ALL if "key_help_text.mbe" in rel_path else csv.QUOTE_MINIMAL
        with path.open("w", encoding="utf-8", newline="") as f:
            csv.writer(f, lineterminator="\n", quoting=quoting).writerows(rows)
    return changed


COMMON_VALUES = {
    "10501": "Перевернуть страницу",
    "10850": "Настройки игры",
    "10851": "Язык и звук",
    "10852": "Графика",
    "10853": "Настройка кнопок (клавиатура и мышь)",
    "10854": "Настройка кнопок",
    "10860": "Изменить",
    "10865": "Настройка яркости",
    "10866": "Настройте {fc10яркость}, сравнив левое и правое изображения.",
    "11308": "Узы филантропии",
    "11309": "Узы доблести",
    "11310": "Узы мудрости",
    "11311": "Узы дружелюбия",
    "11312": "Узы верности",
    "19004": "Отображение мини-карты",
    "19005": "Вращение мини-карты",
    "19006": "Показывать обучение",
    "19021": "Громкость роликов",
    "19022": "Устройство вывода",
    "19026": "Управление в меню",
    "19027": "Открыть Дигивайс/Переключить информацию/Пропустить ролик",
    "19028": "Быстрый доступ (подтвердить)",
    "19029": "Езда/Побег из боя",
    "19030": "Анализ/Переключение вкладок",
    "19031": "Дигиатака/Кросс-арт/Переключение вкладок",
    "19032": "Переключить карту/Закрыть Дигивайс",
    "19035": "Нормальная",
    "19036": "Сложная",
    "19038": "Показать только 1",
    "19039": "Показать всё",
    "19055": "Бразильский португальский",
    "19057": "Китайский (традиционный)",
    "19058": "Китайский (упрощённый)",
    "19061": "Объёмный",
    "19062": "Латиноамериканский испанский",
    "19063": "Открыть системное меню/Переключить сортировку",
    "19065": "Внешний вид главного героя",
    "19068": "Имя главного героя",
    "19069": "Лицензионное соглашение",
    "19070": "Политика конфиденциальности",
    "19071": "Соглашение об использовании данных ({d0})",
    "19073": "Просмотреть/изменить",
    "19076": "Автоматические диалоги",
    "19077": "Автобой",
    "19078": "Авторские права",
    "ui_difficulty_name_01": "Сюжет",
    "ui_difficulty_name_02": "Сбалансированная",
    "ui_difficulty_name_03": "Сложная",
    "ui_difficulty_name_04": "Мега",
    "ui_difficulty_name_05": "Мега+",
    "ui_difficulty_explanation_04": (
        "Для игроков, желающих полностью погрузиться в сложные бои.\n"
        "Вражеские дигимоны будут сильнее и станут появляться в большем числе.\n"
        "Понадобятся хорошая тренировка и продуманный состав отряда.\n\n"
        "{fc15Примечание: сложность игры можно изменить позже.}"
    ),
    "ui_digifarm_digimon_0021": "Быстрое завершение тренировки",
    "ui_digifarm_digimon_0022": "Выйти из тренировки",
    "ui_digifarm_digimon_0040": "Текущий личный навык",
    "ui_digifarm_digimon_0050": "Новый личный навык",
    "ui_digifarm_digimon_0055": "Для {fc9{d0}} доступен новый личный навык.\nЗаменить текущий личный навык?",
    "ui_digifarm_digimon_0060": "Тренировочные предметы",
    "ui_digifarm_digimon_0070": "Требуемое время",
    "ui_digifarm_digimon_0090": "Нет доступных тренировочных предметов.",
    "ui_digifarm_digimon_0100": "{fc10Т}ренировка завершена!",
    "ui_digifarm_digimon_0130": "Ваш дигимон собрал предметы.",
    "ui_digifarm_digimon_0140": "Задайте положение, направление и радиус действия дигимона.",
    "ui_digifarm_digimon_0150": "Взаимодействовать с дигимоном на ферме",
    "ui_digifarm_digimon_0160": "Режим редактирования",
    "ui_digifarm_digimon_0170": "Выберите, куда отправить дигимона.",
    "ui_digifarm_digimon_0180": "Выберите, куда отправить предмет.",
    "ui_digifarm_island_02": "Травяной остров",
    "ui_digifarm_island_03": "Пустынный остров",
    "ui_digifarm_island_04": "Остров руин",
    "ui_digifarm_island_05": "Заводской остров",
    "ui_digifarm_island_06": "Морозный остров",
    "ui_title_demo_0110": "Выбрать главного героя",
}

INFO_VALUES = {
    "info_message_playername_option": "Введите имя главного героя.\n\n<{fc9{d0} Юки}>",
}

YES_NO_VALUES = {
    "yesno_language_0010": (
        "Чтобы изменить язык текста, игра сохранит прогресс и вернётся на титульный экран.\n"
        "Продолжить?\n\n"
        "{fc9Имена главного героя и дигимонов останутся на прежнем языке. Кроме того, из-за смены шрифта имена главного героя и дигимонов могут отображаться некорректно. (Их можно изменить позже.)}"
    ),
    "yesno_language_0020": (
        "Чтобы изменить язык текста, игра сохранит прогресс и вернётся на титульный экран.\n"
        "Продолжить?\n\n"
        "{fc9Имена главного героя и дигимонов останутся на прежнем языке. (Их можно изменить позже.)}"
    ),
}

CHAR_VALUES = {
    "char_HERO": "Главный герой",
    "char_HEROINES_FATHER": "Отец Инори",
}

KEY_HELP_VALUES = {
    "key_help_0046": " {image({d0})}",
    "key_help_0081": " Быстрое завершение",
}


def main() -> None:
    updates = {
        "app_text01/text/common_message.mbe/000_Sheet1.csv": COMMON_VALUES,
        "patch_text01/text/common_message.mbe/000_Sheet1.csv": COMMON_VALUES,
        "app_text01/text/info_message.mbe/000_Sheet1.csv": INFO_VALUES,
        "patch_text01/text/info_message.mbe/000_Sheet1.csv": INFO_VALUES,
        "app_text01/text/yes_no_message.mbe/000_Sheet1.csv": YES_NO_VALUES,
        "patch_text01/text/yes_no_message.mbe/000_Sheet1.csv": YES_NO_VALUES,
        "app_text01/text/char_name.mbe/000_Sheet1.csv": CHAR_VALUES,
        "patch_text01/text/char_name.mbe/000_Sheet1.csv": CHAR_VALUES,
        "app_text01/text/key_help_text.mbe/000_Sheet1.csv": KEY_HELP_VALUES,
        "patch_text01/text/key_help_text.mbe/000_Sheet1.csv": KEY_HELP_VALUES,
    }
    total = 0
    for rel_path, values in updates.items():
        changed = update_rows(rel_path, values)
        total += changed
        print(f"{rel_path}: {changed} row(s)")
    print(f"total: {total} row(s)")


if __name__ == "__main__":
    main()

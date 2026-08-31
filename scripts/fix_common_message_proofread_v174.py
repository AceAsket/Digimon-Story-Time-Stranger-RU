#!/usr/bin/env python3
"""Apply the first guarded proofreading pass to common UI messages."""

from __future__ import annotations

import csv
import io
import subprocess
from pathlib import Path

from fix_t01_npc_context_v169 import (
    csv_format,
    read_document,
    unique_row,
    write_document,
)


ROOT = Path(__file__).resolve().parents[1]
CSV_ROOT = ROOT / "csv"
BASELINE_REF = "v0.1.51"
RELATIVE = "text/common_message.mbe/000_Sheet1.csv"

# package, relative CSV, row id, text column, replacement
UPDATES: list[tuple[str, str, str, int, str]] = []


def add(row_id: str, replacement: str) -> None:
    UPDATES.append(("patch_text01", RELATIVE, row_id, 1, replacement))


# Basic labels and synthesis screens.
add("103", "В группе")
add("110", "Очки агента")
add("119", "Вкл.")
add("120", "Выкл.")
add("135", "Ранг агента")
add("410", "Кол-во для создания")
add("413", "Предметы после разборки")
add("730", "Навыки агента")
add("731", "Информация агента")
add("741", "Полевой справочник")
add("752", "Настройки")
add("771", "Усиление синтезом")
add("802", "Усиление синтезом")
add("1001", "Игровое время")
add("1100", "Полная карта")
add("1261", "В списке есть {d0} со связью 100%")
add("1267", "Выберите дигимона для джогресс-эволюции.")
add(
    "1268",
    "Указанный ниже дигимон будет помещён в бокс после джогресс-деволюции:",
)
add("1269", "Ранг агента {d0} и выше")
add("1284", "Базовая личность цели совпадает с текущей")
add("1312", "Дополнительный")
add("1314", "Рекомендуемый ур.")
add("1315", "Следующая цель")
add("1316", "Очки аномалий")
add("1319", "Квест {fc10з}авершён")
add("1400", "Сортировка")
add("1409", "ЗАЩ")
add("1413", "Получено ОПТ")
add("1414", "Прогресс сканирования")
add("1704", "Специальные навыки")
add("3209", "Повышение уровня")
add("9019", "Сопротивление атрибутам")
add("9020", "Сопротивление стихиям")
add("10008", "Автовыбор")
add("10012", "ОПТ до следующего ур.")
add("10013", "Получено ОПТ")
add("10018", "(Макс. ур. {n0})")
add("10029", "Характеристики")
add("10030", "Усилено!")
add("10046", "Прогресс сканирования: {d0}")
add("10049", "Характеристики")
add("10053", "Особые условия")
add("10075", "Только ур. 1")
add("10080", "Нет дигимона")
add("10092", "Мощность (по возрастанию)")
add("10093", "Мощность (по убыванию)")
add("10200", "Среда фермы")
add("10202", "Команды")
add("10300", "Получить предмет")
add(
    "10402",
    "{fc1Режим можно свободно менять в обе стороны.\n\n"
    "Примечание: уровень, личность, талант и связь не меняются.}",
)
add(
    "10404",
    "{fc1Получите} {fc9{d0}} {fc1, чтобы разблокировать смену режима.\n"
    "Режим можно свободно менять в обе стороны.\n\n"
    "Примечание: уровень, личность, талант и связь не изменятся.}",
)
add("10500", "История диалогов")
add("10502", "Воспроизвести")
add("11300", "Изучено")
add("11306", "Доступно ТП")
add("11502", "№ в полевом справочнике")
add("11503", "Профиль")
add("11504", "Характеристики")
add("11507", "Базовая личность")
add("12100", "Повторить")
add("12101", "Начать с последнего сохранения")
add("12102", "Вернуться в главное меню")
add("13003", "{d0} доступно")
add("13004", "{d0} недоступно")
add("13014", "Смена режима")
add("13015", "Исходный дигимон")
add("13018", "Нет данных")


# Settings, top-level menus, and short system actions.
add("19012", "Автопереход реплик")
add("19003", "Дигимон-компаньон")
add("19023", "Голоса дигимонов")
add("19027", "Открыть Дигивайс/Переключить информацию/Пропустить ролик")
add("19030", "Анализ/Сменить вкладку")
add("19031", "Дигиатака/Кросс-арт/Сменить вкладку")
add("19033", "Вкл.")
add("19034", "Выкл.")
add("19063", "Открыть системное меню/Сменить сортировку")
add("19076", "Автопереход реплик")
add("20100", "Личность")
add("20102", "Справедливый")
add("20103", "Рьяный")
add("21002", "В боксе нет дигимонов.")
add("21003", "Нет доступных для выбора дигимонов.")
add("21005", "Противников не найдено.")
add("100000", "{fc10Н}астройка")
add("100002", "{fc10Э}волюция")
add("100010", "{fc10Н}астройки")
add("100012", "{fc10П}олевой справочник")
add("100013", "{fc10Н}авыки агента")
add("100200", "{fc10М}атериальный мир")
add("100201", "{fc10Ц}ифровой мир: Илиада")
add("100301", "{fc10И}стория диалогов")
add("100400", "{fc10Н}а Дигиферму")
add("110000", "Список снаряжения")
add("110001", "Список костюмов")
add("120200", "Расходные предметы")
add("120302", "Поддержка в поле")
add("120304", "Навыки фермы")
add("120305", "Навыки ухода")
add("120401", "Побочные миссии")
add("130000", "Текущий костюм")
add("130001", "{image(ui_digivice_costume_vdr)} Виртуальная раздевалка")
add("140001", "8 лет назад")
add("140002", "Наши дни")
add("150103", "Сменить дигимона?")
add("150122", "Специальные навыки")
add("171002", "Прогресс сканирования:")
add("171004", "Награда получена:")
add("180000", "История диалогов")
add("180007", "{is30}{image(ui_digivice_digiline_reply)} Ответить")
add("180008", "Ответить")
add("190013", "Переместить дигимона")
add("190014", "Разместить остров")
add("190015", "Разместить предмет")
add("190017", "Удалить предмет")


# Contextual UI actions and card-game screens.
add("ui_reinforcement_0102", "Исходный дигимон")
add("ui_reinforcement_0106", "Только ур. 1")
add("ui_reinforcement_0107", "Нет накопительного бонуса")
add("ui_conversion_0100", "Список дигимонов")
add("ui_shop_0112", "Требуется предметов")
add("ui_shop_0114", "Полученные предметы")
add("ui_shop_0120", "{d0} {d1} × {n0}")
add("ui_worldmap_0100", "Запретная зона")
add("ui_hazamagate_0010", "Вернуться в реальный мир (продолжить сюжет)")
add("ui_battle_0050", "Предметы")
add("ui_digifarm_digicare_0010", "Погладить")
add("ui_digifarm_digimon_0010", "Погладить")
add("ui_digimoncard_battle_0070", "Выберите карты!")
add("ui_digimoncard_battle_0120", "Вы проиграли…")
add(
    "ui_digimoncard_battle_0150",
    "Призванная дополнительная карта будет добавлена в руку.",
)
add(
    "ui_digimoncard_battle_0151",
    "Призванная дополнительная карта будет добавлена в руку.\n"
    "({fc9Эта карта ещё не получена.})",
)
add(
    "ui_digimoncard_battle_0170",
    "Побед в раундах: {n0} — {fc9Получено карт: {n1}}\n"
    "Выберите карты.\n{n2}\n{n1}",
)
add("ui_digimoncard_deck_0020", "Избранное")
add("ui_digimoncard_deck_0040", "Получить призывом дополнительной карты")
add("ui_digimoncard_deck_0060", "—Требуемый дигимон—")
add("ui_digimoncard_deck_0080", "Полученные карты")
add("ui_digimoncard_deck_0090", "{d0} × {n0}")
add("ui_gameover_0041", "Вернуться в лобби")
add("ui_gameover_0050", "Загрузить")
add("ui_hazama_d_0040", "Условия провала")
add("ui_arena_0010", "Список претендентов")
add("ui_battle_item_0010", "В этом ходу предметы больше недоступны.")
add(
    "ui_battle_item_0020",
    "{fc2Примечание: использовать нельзя — ни один дигимон не нуждается в лечении.}",
)
add(
    "ui_battle_jogress_01",
    "Провести джогресс-эволюцию этих дигимонов и активировать их навык слияния?",
)
add("ui_battle_target_0010", "{is24}{sub1} Переключиться на резерв")
add("ui_title_0070", "Настройки")
add("ui_title_0080", "Выход из игры")
add("ui_launch_0020", "Предупреждение")


# Personality labels.  The same concepts occur in two neighboring UI groups.
for row_id in (
    "ui_kizunaskill_0030",
    "ui_kizunaskill_0031",
    "ui_kizunaskill_0032",
    "ui_kizunaskill_0033",
):
    replacements = {
        "ui_kizunaskill_0030": "Кол-во {is32}{image(ui_icon_personal01_00)} дигимонов типа «Доблесть»: {n0} {fc15/ {n1}}",
        "ui_kizunaskill_0031": "Кол-во {is32}{image(ui_icon_personal01_01)} дигимонов типа «Филантропия»: {n0} {fc15/ {n1}}",
        "ui_kizunaskill_0032": "Кол-во {is32}{image(ui_icon_personal01_02)} дигимонов типа «Дружелюбие»: {n0} {fc15/ {n1}}",
        "ui_kizunaskill_0033": "Кол-во {is32}{image(ui_icon_personal01_03)} дигимонов типа «Мудрость»: {n0} {fc15/ {n1}}",
    }
    add(row_id, replacements[row_id])

PERSONALITY_LABELS = {
    "ui_kizunaskill_0040": ("ui_icon_personal01_00", "Рвение"),
    "ui_kizunaskill_0041": ("ui_icon_personal01_00", "Храбрость"),
    "ui_kizunaskill_0042": ("ui_icon_personal01_00", "Безрассудство"),
    "ui_kizunaskill_0043": ("ui_icon_personal01_00", "Отвага"),
    "ui_kizunaskill_0044": ("ui_icon_personal01_01", "Обожание"),
    "ui_kizunaskill_0045": ("ui_icon_personal01_01", "Преданность"),
    "ui_kizunaskill_0046": ("ui_icon_personal01_01", "Терпимость"),
    "ui_kizunaskill_0047": ("ui_icon_personal01_01", "Опека"),
    "ui_kizunaskill_0048": ("ui_icon_personal01_02", "Оппортунизм"),
    "ui_kizunaskill_0049": ("ui_icon_personal01_02", "Дружелюбие"),
    "ui_kizunaskill_0050": ("ui_icon_personal01_02", "Общительность"),
    "ui_kizunaskill_0051": ("ui_icon_personal01_02", "Сострадание"),
    "ui_kizunaskill_0052": ("ui_icon_personal01_03", "Просветлённость"),
    "ui_kizunaskill_0053": ("ui_icon_personal01_03", "Хитрость"),
    "ui_kizunaskill_0054": ("ui_icon_personal01_03", "Проницательность"),
    "ui_kizunaskill_0055": ("ui_icon_personal01_03", "Стратег"),
}
for row_id, (icon, label) in PERSONALITY_LABELS.items():
    add(row_id, f"{{is26}}{{image({icon})}} {label}")

DIGIMON_CHAT_PERSONALITIES = {
    "ui_digimonchat_personality_001": ("ui_icon_personal01_00", "Храбрость"),
    "ui_digimonchat_personality_002": ("ui_icon_personal01_00", "Рвение"),
    "ui_digimonchat_personality_003": ("ui_icon_personal01_00", "Отвага"),
    "ui_digimonchat_personality_004": ("ui_icon_personal01_00", "Безрассудство"),
    "ui_digimonchat_personality_101": ("ui_icon_personal01_01", "Обожание"),
    "ui_digimonchat_personality_102": ("ui_icon_personal01_01", "Преданность"),
    "ui_digimonchat_personality_103": ("ui_icon_personal01_01", "Терпимость"),
    "ui_digimonchat_personality_104": ("ui_icon_personal01_01", "Опека"),
    "ui_digimonchat_personality_201": ("ui_icon_personal01_02", "Сострадание"),
    "ui_digimonchat_personality_202": ("ui_icon_personal01_02", "Общительность"),
    "ui_digimonchat_personality_203": ("ui_icon_personal01_02", "Дружелюбие"),
    "ui_digimonchat_personality_204": ("ui_icon_personal01_02", "Оппортунизм"),
    "ui_digimonchat_personality_301": ("ui_icon_personal01_03", "Проницательность"),
    "ui_digimonchat_personality_302": ("ui_icon_personal01_03", "Стратег"),
    "ui_digimonchat_personality_303": ("ui_icon_personal01_03", "Просветлённость"),
    "ui_digimonchat_personality_304": ("ui_icon_personal01_03", "Хитрость"),
}
for row_id, (icon, label) in DIGIMON_CHAT_PERSONALITIES.items():
    add(row_id, f"{{is28}}{{image({icon})}} {label}")


# Difficulty, music, icon legends, and consistent game terminology.
add(
    "ui_difficulty_explanation_01",
    "Для игроков, предпочитающих проходить сюжет без сложностей.\n"
    "Рекомендуется тем, кто хочет быстро завершать бои, чтобы узнать, что произойдёт дальше.\n"
    "Позволяет {fc9повторять битвы в режиме неуязвимости при поражении}.\n\n"
    "{fc15Примечание: сложность игры можно изменить позже.}",
)
add(
    "ui_difficulty_explanation_02",
    "Для игроков, желающих гармоничного сочетания сюжета и боёв.\n"
    "Это наиболее сбалансированный игровой режим.\n"
    "Игроки могут {fc9повторять битвы на пониженной сложности после двух поражений}.\n\n"
    "{fc15Примечание: сложность игры можно изменить позже.}",
)
add("ui_systemmenu_0010", "Вернуться в игру")
add("ui_systemmenu_0020", "Настройки музыки")
add("ui_bgm_0020", "Обычный бой")
add("ui_bgm_0021", "Битва с боссом")
add("ui_bgm_0050", "Карточная битва")
add("icon_info_category_01", "Совместимость атрибутов")
add("icon_info_category_02", "Описание значка: дигимон")
add("icon_info_category_03", "Описание значка: бой (аномалия/изменение состояния)")
add("icon_info_category_04", "Описание значка: бой (усиление/ослабление)")
add("icon_info_category_05", "Описание значка: навыки агента")
add("icon_info_category_06", "Описание значка: карта")
add("icon_info_category_07", "Описание значка: перемещение по карте")
add("icon_info_description_02_05", "Атрибут (Переменный)")
add("icon_info_description_02_07", "Атрибут (без атрибута)")
add("icon_info_description_02_08", "Элемент (Нейтральный)")
add("icon_info_description_02_09", "Элемент (Огонь)")
add("icon_info_description_02_10", "Элемент (Вода)")
add("icon_info_description_02_11", "Элемент (Растение)")
add("icon_info_description_02_12", "Элемент (Лёд)")
add("icon_info_description_02_13", "Элемент (Электричество)")
add("icon_info_description_02_14", "Элемент (Сталь)")
add("icon_info_description_02_15", "Элемент (Ветер)")
add("icon_info_description_02_16", "Элемент (Земля)")
add("icon_info_description_02_17", "Элемент (Свет)")
add("icon_info_description_02_18", "Элемент (Тьма)")
add("icon_info_description_02_19", "Навык восстановления")
add("icon_info_description_02_20", "Навык усиления")
add("icon_info_description_02_21", "Навык ослабления")
add("icon_info_description_03_01", "Отравление: потеря ОЗ в конце хода")
add("icon_info_description_03_03", "Смятение: атака случайных целей")
add("icon_info_description_03_04", "Паралич: шанс пропустить действие")
add("icon_info_description_03_05", "Сон: обездвиживание и уязвимость")
add("icon_info_description_03_06", "Кристаллизация: навыки недоступны")
add("icon_info_description_03_07", "Реверс: слабости и устойчивости меняются местами")
add("icon_info_description_03_08", "Травма: восстановление ОЗ невозможно")
add("icon_info_description_03_09", "Болезнь: восстановление ОС невозможно")
add("icon_info_description_03_12", "Контратака: ответный удар при получении урона")
add("icon_info_description_03_13", "Отражение: атаки противника отражаются")
add("icon_info_description_03_14", "Иммунитет к аномалиям состояния")
add("icon_info_description_03_17", "Защита: получаемый урон снижен")
add("icon_info_description_03_18", "Смена урона: наносимый урон изменён")
add("icon_info_description_03_19", "Заряд: сила атаки повышена")
add("icon_info_description_03_20", "Провокация: привлекает атаки противников")
add("icon_info_description_04_09", "Макс. ОЗ ↑/↓")
add("icon_info_description_04_10", "Макс. ОС ↑/↓")
add("icon_info_description_04_11", "Стойкость к нейтральному ↑/↓")
add("icon_info_description_04_12", "Стойкость к огню ↑/↓")
add("icon_info_description_04_13", "Стойкость к воде ↑/↓")
add("icon_info_description_04_14", "Стойкость к растениям ↑/↓")
add("icon_info_description_04_15", "Стойкость ко льду ↑/↓")
add("icon_info_description_04_16", "Стойкость к электричеству ↑/↓")
add("icon_info_description_04_17", "Стойкость к стали ↑/↓")
add("icon_info_description_04_18", "Стойкость к ветру ↑/↓")
add("icon_info_description_04_19", "Стойкость к земле ↑/↓")
add("icon_info_description_04_20", "Стойкость к свету ↑/↓")
add("icon_info_description_04_21", "Стойкость к тьме ↑/↓")
add("icon_info_description_05_01", "Кросс-арт")
add("icon_info_description_05_02", "Личность (Доблесть)")
add("icon_info_description_05_03", "Личность (Филантропия)")
add("icon_info_description_05_04", "Личность (Дружелюбие)")
add("icon_info_description_05_05", "Личность (Мудрость)")
add("icon_info_description_05_06", "Усиление характеристик")
add("icon_info_description_05_14", "Увеличение получаемого ОПТ")
add("icon_info_description_05_16", "Усиление кросс-арта")
add("icon_info_description_05_24", "Изучен эффект кросс-арта (атака)")
add("icon_info_description_05_25", "Изучен эффект кросс-арта (лечение)")
add("icon_info_description_05_26", "Изучен эффект кросс-арта (усиление/ослабление)")
add("icon_info_description_06_03", "Враждебные дигимоны")
add("icon_info_description_06_05", "Поговорить")
add("icon_info_description_06_07", "Сундук с сокровищами")
add("icon_info_description_06_08", "Основная миссия")
add("icon_info_description_06_09", "Побочная миссия")
add("icon_info_description_06_10", "Свободная миссия")
add("icon_info_description_06_12", "Лавка предметов")
add("icon_info_description_06_13", "Лавка дисков навыков")
add("icon_info_description_06_14", "Лавка снаряжения")
add("icon_info_description_06_15", "Лавка товаров для фермы")
add("icon_info_description_06_16", "Магазин костюмов")
add("icon_info_description_06_17", "Мастерская")
add("icon_info_description_06_18", "Карточная битва")
add("icon_info_description_06_19", "Карточная битва (победа)")
add("icon_info_description_07_01", "Такси")
add("icon_info_description_07_04", "Смена зон")
add("icon_info_description_07_10", "Театр между мирами")
add("icon_info_description_07_12", "Внешнее подземелье (пройдено)")
add("icon_info_description_07_17", "Поезд")
add("ui_evolution_condition_010", "Базовая личность дигимона: {d0}")
add("ui_mission_recommendedlv", "Рекомендуемый ур.: {fc9 {d0}}")
add("ui_mission_recommendedlv_none", "Рекомендуемый ур.: -")
add("ui_reinforcement_nextlv", "До следующего ур.: {fc1 {d0}}")
add("ui_analyse_damage_010", "Легенда устойчивостей")
add("ui_sort_0090", "Атрибут (Переменный)")
add("ui_sort_0130", "Прогресс сканирования")
add("ui_sort_0190", "Избранное")
add("ui_title_demo_0030", "Пэрротмон — битва с боссом")


def read_baseline() -> tuple[list[list[str]], str]:
    object_name = f"{BASELINE_REF}:csv/patch_text01/{RELATIVE}"
    result = subprocess.run(
        ["git", "show", object_name],
        cwd=ROOT,
        capture_output=True,
        check=False,
    )
    if result.returncode:
        detail = result.stderr.decode("utf-8", errors="replace").strip()
        raise SystemExit(f"Cannot read baseline {object_name}: {detail}")
    rows = list(csv.reader(io.StringIO(result.stdout.decode("utf-8-sig"), newline="")))
    return rows, csv_format(result.stdout)


def main() -> None:
    markers = [(package, relative, row_id, column) for package, relative, row_id, column, _ in UPDATES]
    if len(markers) != len(set(markers)):
        raise SystemExit("Duplicate guarded target in UPDATES")

    path = CSV_ROOT / "patch_text01" / RELATIVE
    rows, encoding, _ = read_document(path)
    baseline_rows, mode = read_baseline()
    changed = current = 0

    for package, relative, row_id, column, replacement in UPDATES:
        label = f"{package}:{relative}"
        row = unique_row(rows, row_id, column, label)
        baseline_row = unique_row(
            baseline_rows,
            row_id,
            column,
            f"{BASELINE_REF}:{label}",
        )
        if row[column] == replacement:
            current += 1
        elif row[column] == baseline_row[column]:
            row[column] = replacement
            changed += 1
        else:
            raise SystemExit(
                f"Unexpected text {label}:{row_id}:\n"
                f"baseline={baseline_row[column]!r}\n"
                f"current={row[column]!r}\n"
                f"replacement={replacement!r}"
            )

    if changed:
        write_document(path, rows, encoding, mode)

    print(f"Baseline: {BASELINE_REF}")
    print(f"Guarded targets: {len(UPDATES)}")
    print(f"Changed: {changed}")
    print(f"Already current: {current}")


if __name__ == "__main__":
    main()

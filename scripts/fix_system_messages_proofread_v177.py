#!/usr/bin/env python3
"""Apply guarded proofreading fixes to system and confirmation messages."""

from __future__ import annotations

import csv
import io
import subprocess
from pathlib import Path

from fix_t01_npc_context_v169 import (
    read_document,
    unique_row,
    write_document,
)


ROOT = Path(__file__).resolve().parents[1]
CSV_ROOT = ROOT / "csv"
BASELINE_REF = "v0.1.51"
UPDATES: list[tuple[str, str, str, int, str]] = []
MIGRATION_VALUES = {
    ("patch_text01", "text/common_message.mbe/000_Sheet1.csv", "771", 1): "Загрузка улучшений",
    ("patch_text01", "text/common_message.mbe/000_Sheet1.csv", "802", 1): "Загрузка улучшений",
    ("patch_text01", "text/info_message.mbe/000_Sheet1.csv", "1109020030", 1):
        "{player} передаёт принцу Мамемону 20 ед. обычной древесины!",
    ("patch_text01", "text/info_message.mbe/000_Sheet1.csv", "1110020030", 1):
        "{player} передаёт принцу Мамемону 20 прочных стальных пластин!",
    ("patch_text01", "text/info_message.mbe/000_Sheet1.csv", "info_message_dlc_disable", 1):
        "Контент из данных сохранения не найден.\n"
        "Скачайте или приобретите следующий контент повторно.\n\n"
        "{fc9{d0}}\n\n"
        "*Если загрузка уже идёт, дождитесь её завершения.",
    ("patch_text01", "text/info_message.mbe/000_Sheet1.csv", "info_message_dlc_disable_01", 1):
        "Контент из данных сохранения не найден.\n\nВозврат на главный экран.",
}


def add(
    relative: str,
    row_id: str,
    replacement: str,
    *,
    package: str = "patch_text01",
) -> None:
    UPDATES.append((package, relative, row_id, 1, replacement))


COMMON = "text/common_message.mbe/000_Sheet1.csv"
BATTLE = "text/battle_info_message.mbe/000_Sheet1.csv"
INFO = "text/info_message.mbe/000_Sheet1.csv"
YES_NO = "text/yes_no_message.mbe/000_Sheet1.csv"


# Menu terminology shared with the tutorial names.
add(COMMON, "771", "Усиление синтезом")
add(COMMON, "802", "Усиление синтезом")
add(COMMON, "120306", "Бонус тренировки")


# Short battle notifications.
add(BATTLE, "100016", "Союзник")
add(BATTLE, "18", "{d0} нокаутирован!")
add(BATTLE, "20", "Превращение в {d0}!")
add(BATTLE, "22", "{d0}: поколение понижено на 1 ступень!")
add(BATTLE, "100022", "{d0}: поколение понижено на 1 ступень!")
add(BATTLE, "23", "Усиления и ослабления характеристик {d0} поменялись местами!")


# Core information and error messages.
add(INFO, "1008", "Загрузка…")
add(INFO, "1011", "Файл повреждён.")
add(INFO, "1050", "Введённое вами имя содержит неподходящие слова.")
add(INFO, "1218", "Нет доступных отсканированных дигимонов.")
add(INFO, "1219", "Нет дигимонов, на которых можно ездить.")
add(INFO, "1222", "Нельзя выполнить деволюцию: бокс заполнен.")
add(INFO, "1800", "Тип личности изменён на «{d0}».")
add(INFO, "1901", "Это не даст никакого эффекта.")
add(INFO, "1904", "Связь с {d0} повысилась до {fc9{n0}}.")
add(INFO, "1905", "{d0}: тип личности изменён на {fc9{d1}}.")
add(INFO, "1906", "{d0}: накопленный показатель «{d1}» увеличен.")
add(INFO, "1907", "Предел уровня {d0} повышен.")
add(INFO, "1913", "Но больше ничего не унести — предмет придётся оставить.")
add(INFO, "1919", "Больше нельзя нести {fc9{d0}}.")
add(INFO, "1922", "{d0}: предел роста")
add(INFO, "2300", "Не останется ни одного дигимона, способного сражаться.")
add(INFO, "2400", "Теперь можно отправиться в {d0}.")
add(
    INFO,
    "2704",
    "Случайное восстановление не выполнено.\n\n"
    "{fc9 -В отряде нет дигимонов с навыками восстановления ОЗ.}\n"
    "{fc9 -В инвентаре нет предметов восстановления.}",
)
add(
    INFO,
    "2705",
    "Случайное восстановление не выполнено.\n\n"
    "{fc9 -Недостаточно ОС для навыков восстановления ОЗ.}\n"
    "{fc9 -В инвентаре нет предметов восстановления.}",
)
add(
    INFO,
    "2706",
    "Случайное восстановление не выполнено.\n\n"
    "{fc9 -В отряде нет дигимонов с навыками восстановления ОЗ.}",
)
add(
    INFO,
    "2707",
    "Случайное восстановление не выполнено.\n\n"
    "{fc9 -В инвентаре нет предметов восстановления.}",
)
add(INFO, "2800", "Набор карт собран!\n{fa1}{d0}")
for unused_id in (
    "2900",
    "2901",
    "2902",
    "2903",
    "2911",
    "2912",
    "2914",
    "2915",
    "2916",
    "2923",
):
    add(INFO, unused_id, "Не используется")
add(INFO, "2905", "Не удаётся подключиться.")
add(INFO, "2913", "Соединение отменено.")
add(INFO, "2917", "Этот сервис пока недоступен.")
add(INFO, "3000", "Началась тренировка дигимонов: {d0}.")
add(INFO, "3001", "Началось создание предметов. Дигимонов: {d0}.")
add(INFO, "3002", "Началось расследование. Дигимонов: {d0}.")
add(INFO, "3003", "Уже есть 99 ед. {d0}. Больше получить нельзя.")
add(INFO, "3009", "Нечего забирать с фермы.")
add(INFO, "3100", "Сейчас нельзя сохраниться.")
add(INFO, "5051", "ОЗ и ОС отряда полностью восстановлены!")
add(INFO, "7006", "Получены памятные драгоценности.")
add(INFO, "7037", "{fc9Украденная деталь x 1} возвращена. Примечание: не используется.")
add(INFO, "7055", "Получено: {fc9Материал костюма}.")
add(INFO, "8000", "Уплачено {fc9{n0} ЙЕН}.")
add(
    INFO,
    "10007",
    "Это сообщение заблокировано.\n"
    "{fc9Условие разблокировки: добраться до цели, ни разу не столкнувшись\n"
    "с врагом или препятствием.}",
)
add(INFO, "10020", "Сообщение разблокировано. Воспроизведение…")
add(INFO, "10350100", "Теперь можно использовать особый навык {fc9Оглушающий Удар}.")
add(INFO, "1101040040", "{player} брызгает цветочным экстрактом на голову Танемон!")
add(INFO, "1103010100", "Получена карточка с печатью!")
add(INFO, "1103060020", "{player} передаёт карточку с печатью Маммимону!")
add(INFO, "1108030040", "{player} изо всех сил бьёт по стене!")
add(INFO, "1109020030", "Передано принцу Мамемону: обычная древесина x20!")
add(INFO, "1110020030", "Передано принцу Мамемону: прочная стальная пластина x20!")
add(INFO, "1124090170", "Возвращено 100 000 иен!")
add(INFO, "info_message_reinforcement_02", "Получен диск навыка.")
add(INFO, "info_message_digifarm_0050", "Во время тренировки нельзя кормить дигимонов.")
add(INFO, "info_message_lockmenu_02", "Чтобы разблокировать усиление синтезом, продвиньтесь дальше по сюжету.")
add(INFO, "info_message_personality_skill", "{fc9{d0}} освоил новый личный навык!")


TRAINING_ROWS = {
    "01": ["{d0} {n0} → {fc7 {n1}}"],
    "02": ["{d0} {n0} → {fc7 {n1}}", "{d1} {n2} → {fc7 {n3}}"],
    "03": ["{d0} {n0} → {fc7 {n1}}", "{d1} {n2} → {fc7 {n3}}", "{d2} {n4} → {fc7 {n5}}"],
    "04": ["{d0} {n0} → {fc7 {n1}}", "{d1} {n2} → {fc7 {n3}}", "{d2} {n4} → {fc7 {n5}}", "{d3} {n6} → {fc7 {n7}}"],
    "05": ["{d0} {n0} → {fc7 {n1}}", "{d1} {n2} → {fc7 {n3}}", "{d2} {n4} → {fc7 {n5}}", "{d3} {n6} → {fc7 {n7}}", "{d4} {n8} → {fc7 {n9}}"],
    "06": ["{d0} {n0} → {fc7 {n1}}", "{d1} {n2} → {fc7 {n3}}", "{d2} {n4} → {fc7 {n5}}", "{d3} {n6} → {fc7 {n7}}", "{d4} {n8} → {fc7 {n9}}", "{d5} {n10} → {fc7 {n11}}"],
    "07": ["{d0} {n0} → {fc7 {n1}}", "{d1} {n2} → {fc7 {n3}}", "{d2} {n4} → {fc7 {n5}}", "{d3} {n6} → {fc7 {n7}}", "{d4} {n8} → {fc7 {n9}}", "{d5} {n10} → {fc7 {n11}}", "{d6} {n12} → {fc7 {n13}}"],
}
for suffix, stat_lines in TRAINING_ROWS.items():
    add(
        INFO,
        f"info_message_training_{suffix}",
        "[Результаты тренировки]\n"
        + "\n".join(stat_lines)
        + "\n\nТип личности изменён: {d7} → {d8}!",
    )

for suffix, stat_lines in TRAINING_ROWS.items():
    shifted_suffix = str(int(suffix) + 10).zfill(2)
    add(
        INFO,
        f"info_message_training_{shifted_suffix}",
        "[Результаты тренировки]\n"
        + "\n".join(stat_lines)
        + "\n\nТип личности сместился к {d9}.",
    )
add(INFO, "info_message_training_18", "[Результаты тренировки]\n{d0} {n0} → {fc7 {n1}}")

add(
    INFO,
    "info_message_dlc_disable",
    "{pf(Дополнения из данных сохранения не найдены./"
    "Дополнения из данных сохранения не найдены./"
    "Загружаемый контент из данных сохранения не найден./"
    "Загружаемый контент из данных сохранения не найден.)}\n"
    "Скачайте или приобретите следующий контент повторно.\n\n"
    "{fc9{d0}}\n\n"
    "*Если загрузка уже идёт, дождитесь её завершения.",
)
add(
    INFO,
    "info_message_dlc_disable_01",
    "{pf(Дополнения из данных сохранения не найдены./"
    "Дополнения из данных сохранения не найдены./"
    "Загружаемый контент из данных сохранения не найден./"
    "Загружаемый контент из данных сохранения не найден.)}\n\n"
    "Возврат на главный экран.",
)
for suffix in ("01", "02", "03"):
    add(
        INFO,
        f"info_message_dlc_{suffix}",
        {
            "01": "{fc9Дополнительный набор дигимонов и эпизодов 1: Альтернативное измерение}",
            "02": "{fc9Дополнительный набор дигимонов и эпизодов 2: Гакуран}",
            "03": "{fc9Дополнительный набор дигимонов и эпизодов 3: Anti-ParadoX}",
        }[suffix]
        + " теперь доступен.\n\n"
        "Чтобы сыграть в новый контент, войдите через "
        "{is28}{image(ui_icon_minimap_lobby)} Дверь истины\n"
        "в Промежуточном театре.",
    )
add(
    INFO,
    "info_message_dlc_10",
    "{fc9Внешние подземелья «Залы опыта, золота и материалов»}\n"
    "теперь доступны.\n\n"
    "Чтобы сыграть в новый контент, поговорите с Мирэй в Промежуточном театре.",
)
add(
    INFO,
    "20010",
    "Если продолжить, выполнение всех текущих побочных миссий будет приостановлено.\n\n"
    "Сначала завершите все активные побочные миссии.\n"
    "Примечание: {fc9подробности миссий можно посмотреть в Дигивайсе > Миссии}.",
)
add(
    INFO,
    "20020",
    "Если отправиться во Дворец Хранителя, выполнение всех текущих побочных миссий\n"
    "будет приостановлено.\n\n"
    "Сначала завершите все активные побочные миссии.\n"
    "Примечание: {fc9подробности миссий можно посмотреть в Дигивайсе > Миссии}.",
)


# Confirmation dialogs.
add(YES_NO, "1204", "Изменить режим {d0}?")
add(
    YES_NO,
    "1206",
    "Конвертировать {fc9{d0}}?\n\n"
    "{fc15Подсказка: чем ближе уровень сканирования к 200%,\n"
    "тем выше будут макс. ОЗ и талант этого дигимона.}",
)
add(YES_NO, "yesno_quest_0010", "{fc9 {d0} }\n\nПосмотреть сведения о миссии?")
add(
    YES_NO,
    "yesno_hazamagate_0020",
    "Переместиться к входу в Промежуточный театр,\n"
    "ближайшему к цели текущей миссии?",
)
add(YES_NO, "yesno_digimoncard_battle_0020", "Подтвердить выбор?")
add(
    YES_NO,
    "yesno_digimoncard_battle_0030",
    "Можно выбрать ещё карт: {fc9 {n0}}.\nПодтвердить выбор?",
)
add(
    YES_NO,
    "yesno_gameover_0010",
    "Понизить сложность до {fc9{d0}} и повторить бой?\n\n"
    "{fc8*Повтор с полным восстановлением ОЗ и ОС.\n"
    "*Сложность останется пониженной после завершения боя.\n"
    "Предыдущий уровень сложности можно вернуть в настройках.}",
)
add(
    YES_NO,
    "yesno_gameover_0020",
    "Повторить бой в режиме неуязвимости?\n\n"
    "{fc9*Враги не будут наносить урон, а ОС не будут расходоваться.\n"
    "*Повтор с полным восстановлением ОЗ и ОС.\n"
    "*Режим неуязвимости действует только для этого боя.}",
)
add(YES_NO, "yesno_digifarm_0050", "Этот дигимон всё ещё тренируется.\nОтменить тренировку?")
add(YES_NO, "yesno_systemmenu_0010", "Выйти из игры?\n\n{fc2Примечание: все несохранённые данные будут утеряны.}")
add(
    YES_NO,
    "yesno_unequip_0010",
    "Снять все диски навыков и снаряжение\n"
    "с дигимонов в боксе и на ферме?\n\n"
    "{fc9Примечание: с защищённых дигимонов\n"
    "диски навыков и снаряжение не снимаются.}",
)
add(
    YES_NO,
    "yesno_language_0030",
    "Чтобы изменить язык интерфейса, настройки будут\n"
    "сохранены, а игра перезапустится.\n\nПродолжить?",
)
add(YES_NO, "yesno_giveup_0010", "Отказаться от этого боя?")


def read_baseline(package: str, relative: str) -> list[list[str]]:
    object_name = f"{BASELINE_REF}:csv/{package}/{relative}"
    result = subprocess.run(
        ["git", "show", object_name],
        cwd=ROOT,
        capture_output=True,
        check=False,
    )
    if result.returncode:
        detail = result.stderr.decode("utf-8", errors="replace").strip()
        raise SystemExit(f"Cannot read baseline {object_name}: {detail}")
    return list(csv.reader(io.StringIO(result.stdout.decode("utf-8-sig"), newline="")))


def main() -> None:
    markers = [(package, relative, row_id, column) for package, relative, row_id, column, _ in UPDATES]
    if len(markers) != len(set(markers)):
        raise SystemExit("Duplicate guarded target in UPDATES")

    documents: dict[tuple[str, str], list[list[str]]] = {}
    baselines: dict[tuple[str, str], list[list[str]]] = {}
    formats: dict[tuple[str, str], tuple[str, str]] = {}
    dirty: set[tuple[str, str]] = set()
    changed = current = 0

    for package, relative, row_id, column, replacement in UPDATES:
        marker = (package, relative)
        if marker not in documents:
            path = CSV_ROOT / package / relative
            rows, encoding, mode = read_document(path)
            documents[marker] = rows
            baselines[marker] = read_baseline(package, relative)
            formats[marker] = (encoding, mode)

        label = f"{package}:{relative}"
        row = unique_row(documents[marker], row_id, column, label)
        baseline_row = unique_row(baselines[marker], row_id, column, f"{BASELINE_REF}:{label}")
        if row[column] == replacement:
            current += 1
        elif row[column] == baseline_row[column] or row[column] == MIGRATION_VALUES.get(
            (package, relative, row_id, column)
        ):
            row[column] = replacement
            changed += 1
            dirty.add(marker)
        else:
            raise SystemExit(
                f"Unexpected text {label}:{row_id}:\n"
                f"baseline={baseline_row[column]!r}\n"
                f"current={row[column]!r}\n"
                f"replacement={replacement!r}"
            )

    for marker in sorted(dirty):
        package, relative = marker
        encoding, mode = formats[marker]
        write_document(CSV_ROOT / package / relative, documents[marker], encoding, mode)

    print(f"Baseline: {BASELINE_REF}")
    print(f"Guarded targets: {len(UPDATES)}")
    print(f"Changed: {changed}")
    print(f"Already current: {current}")
    print(f"Files written: {len(dirty)}")


if __name__ == "__main__":
    main()

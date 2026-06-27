from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CSV_ROOT = ROOT / "csv"
LOG_PATH = ROOT / "logs" / "fix_translation_polish_v028.log"

ROOTS = [
    CSV_ROOT / "patch_text01",
    CSV_ROOT / "app_text01",
]


def read_rows(path: Path) -> list[list[str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.reader(f))


def write_rows(path: Path, rows: list[list[str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        csv.writer(f, lineterminator="\r\n").writerows(rows)


def text_index(path: Path, row: list[str]) -> int | None:
    if "message" in path.parts:
        return 2 if len(row) > 2 else None
    return 1 if len(row) > 1 else None


def replace_id(path: Path, key: str, text: str, log: list[str]) -> bool:
    rows = read_rows(path)
    rel = path.relative_to(path.parents[3]).as_posix()
    changed = False
    for row in rows[1:]:
        if row and row[0] == key:
            idx = text_index(path, row)
            if idx is not None and row[idx] != text:
                old = row[idx]
                row[idx] = text
                changed = True
                log.append(f"{rel}:{key}: {old!r} -> {text!r}")
    if changed:
        write_rows(path, rows)
    return changed


def upsert_text_row(path: Path, key: str, text: str, after_key: str, log: list[str]) -> None:
    rows = read_rows(path)
    for row in rows[1:]:
        if row and row[0] == key:
            if len(row) > 1 and row[1] != text:
                old = row[1]
                row[1] = text
                log.append(f"{path.relative_to(ROOT).as_posix()}:{key}: {old!r} -> {text!r}")
                write_rows(path, rows)
            return

    insert_at = len(rows)
    template_len = len(rows[-1]) if rows else 2
    for i, row in enumerate(rows):
        if row and row[0] == after_key:
            insert_at = i + 1
            template_len = len(row)
            break

    new_row = [key, text] + [""] * max(0, template_len - 2)
    rows.insert(insert_at, new_row)
    write_rows(path, rows)
    log.append(f"{path.relative_to(ROOT).as_posix()}:{key}: inserted {text!r}")


TARGETS: dict[tuple[str, str], str] = {
    ("message/m050.mbe/000_Sheet1.csv", "m050_010_130"):
        "Что ж, давай начнём с осмотра дома. Спускайся вниз,\nкогда будешь готов, хорошо?",
    ("message/m050.mbe/000_Sheet1.csv", "m050_010_250"):
        "Понимаю, плохих новостей уже хватило... но ситуация\nздесь критическая.",
    ("message/m050.mbe/000_Sheet1.csv", "m050_010_280"):
        "Присылай мне всё, что узнаешь. Рассчитываю на тебя,\nагент {player}.",
    ("message/m050.mbe/000_Sheet1.csv", "m050_020_030"):
        "Здесь кухня. Пользуйся, когда захочешь.\nТы умеешь готовить?",
    ("message/m050.mbe/000_Sheet1.csv", "m050_020_050"):
        "...Подожди. Не слишком ли много всего сразу?",
    ("message/m050.mbe/000_Sheet1.csv", "m050_020_070"):
        "Чтобы попасть в его офис, выйди через\nпарадную дверь и спустись на один этаж ниже.",
    ("message/m050.mbe/000_Sheet1.csv", "m050_030_010"):
        "Как спалось?",
    ("message/m050.mbe/000_Sheet1.csv", "m050_030_021"):
        "Спасибо за помощь.{next}",
    ("message/m050.mbe/000_Sheet1.csv", "m050_030_100"):
        "Я знаком с термином \"фазово-электронные формы жизни\", но\nпохоже, ты знаешь о них гораздо больше, чем я.",
    ("message/t04.mbe/000_Sheet1.csv", "f_t0401_0070_0010"):
        "Почему блюда по временной акции всегда так хочется съесть\nпрямо сейчас?",
    ("message/t04.mbe/000_Sheet1.csv", "f_t0403_0070_0010"):
        "Похоже, это постер к аниме. Наверное, оно довольно популярное,\nраз его повесили в гостиной.",
    ("message/field_text.mbe/000_Sheet1.csv", "g_shop008_0030_0010"):
        "Сейчас всё соберу для тебя...",
    ("message/t01.mbe/000_Sheet1.csv", "f_t0108_0010_0040"):
        "Не буду врать: я правда во всё это верю! Особенно если учесть,\nчто всё явно пытаются скрыть...",
    ("message/t01.mbe/000_Sheet1.csv", "f_t0108_0010_0060"):
        "Координаты получены без проблем. Пожалуйста,\nдвигайся к следующей точке.",
    ("message/s200_147.mbe/000_Sheet1.csv", "s200_147_240"):
        "Спасибо! Тогда мы попробуем прогуляться по парку\nв наряде Избранных детей.",
    ("message/s200_147.mbe/000_Sheet1.csv", "s200_147_255"):
        "Давай прогуляемся по парку в наряде Избранных детей.",
    ("text/digitter_message.mbe/000_Sheet1.csv", "field_06_190_40"):
        "Прямо впереди обнаружен огромный Дигимон! Он, должно быть,\nдовольно сильный. Держись!",
    ("text/digitter_message.mbe/000_Sheet1.csv", "field_06_190_10"):
        "Иди в переднюю часть вагона! Спаси Локомона!",
    ("text/digitter_message.mbe/000_Sheet1.csv", "field_06_190_20"):
        "Обнаружены многочисленные сигналы Титанов. Вступай с ними\nв бой, чтобы сбросить их с Локомона!",
    ("text/digitter_message.mbe/000_Sheet1.csv", "field_06_190_21"):
        "Используй Дигиатаки, чтобы быстро побеждать врагов\nи двигаться дальше!",
    ("text/digitter_message.mbe/000_Sheet1.csv", "field_06_190_30"):
        "Впереди обнаружено множество дигимонов! Действуй осторожно!",
    ("text/digitter_message.mbe/000_Sheet1.csv", "field_06_190_50"):
        "Используй Дигиатаки, чтобы победить врага! Спаси Локомона!",
    ("text/digitter_message.mbe/000_Sheet1.csv", "timejump_010_010"):
        "Возврат к Абсолютной временной шкале: Реальный мир.",
    ("text/digitter_message.mbe/000_Sheet1.csv", "timejump_020_010"):
        "Возврат к Абсолютной временной шкале: Синдзюку\n(8 лет назад).",
    ("text/digitter_message.mbe/000_Sheet1.csv", "timejump_030_010"):
        "Возврат к Абсолютной временной шкале: Цифровой мир\n(8 лет назад).",
    ("text/digitter_message.mbe/000_Sheet1.csv", "timejump_040_010"):
        "Возврат к Абсолютной временной шкале: Синдзюку\n(настоящее время).",
    ("text/digitter_message.mbe/000_Sheet1.csv", "timejump_050_010"):
        "Возврат к Абсолютной временной шкале: Цифровой мир\n(настоящее время).",
    ("text/digitter_message.mbe/000_Sheet1.csv", "timejump_060_010"):
        "Возврат к Абсолютной временной шкале: Деревня Восстания\n(настоящее время).",
    ("text/common_message.mbe/000_Sheet1.csv", "755"):
        "Исследование",
    ("text/common_message.mbe/000_Sheet1.csv", "ui_shop_0012"):
        "Имеется",
    ("text/common_message.mbe/000_Sheet1.csv", "ui_shop_0113"):
        "Имеется/Нужно",
}


ITEM_NAMES = {
    "820": "Рекламная футболка с аниме",
    "821": "Футболка сотрудника игрового магазина",
    "822": "Винтажная футболка с классическим фильмом",
    "823": "Футболка бургерной",
    "824": "Костюм Cyber Sleuth",
    "825": "Наряд Избранных детей",
    "826": "Купальник",
    "833": "Футболка The Idolmaster (Харука Амами)",
}

ITEM_RUBY = {
    "820": "Рекламная футболка с аниме",
    "821": "Футболка сотрудника игрового магазина",
    "822": "Винтажная футболка с классическим фильмом",
    "823": "Футболка бургерной",
    "824": "Костюм Cyber Sleuth",
    "825": "Наряд Избранных детей",
    "826": "Купальник",
    "833": "Футболка The Idolmaster (Харука Амами)",
}

ITEM_EXPLANATIONS = {
    "45": "Укрепляет связь с дигимоном на 3%.",
    "46": "Укрепляет связь с дигимоном на 5%.",
    "47": "Укрепляет связь с дигимоном на 1%.",
    "105": "Еда для дигимона. Дай её дигимону на Дигиферме, чтобы постепенно укреплять связь с ним.",
    "106": "Еда для дигимона. Дай её дигимону на Дигиферме, чтобы постепенно укреплять связь с ним.",
    "107": "Еда для дигимона. Дай её дигимону на Дигиферме, чтобы постепенно укреплять связь с ним.",
    "108": "Еда для дигимона. Дай её дигимону на Дигиферме, чтобы постепенно укреплять связь с ним.",
    "109": "Еда для дигимона. Дай её дигимону на Дигиферме, чтобы постепенно укреплять связь с ним.",
    "110": "Еда для дигимона. Дай её дигимону на Дигиферме, чтобы постепенно укреплять связь с ним.",
    "203": "Еда для дигимона. Дай её дигимону на Дигиферме, чтобы постепенно укреплять связь с ним.",
    "210": "Еда для дигимона. Дай её дигимону на Дигиферме, чтобы постепенно укреплять связь с ним.",
    "211": "Еда для дигимона. Дай её дигимону на Дигиферме, чтобы постепенно укреплять связь с ним.",
    "213": "Еда для дигимона. Дай её дигимону на Дигиферме, чтобы постепенно укреплять связь с ним.",
    "222": "Еда для дигимона. Дай её дигимону на Дигиферме, чтобы постепенно укреплять связь с ним.",
    "223": "Еда для дигимона. Дай её дигимону на Дигиферме, чтобы постепенно укреплять связь с ним.",
    "824": "Костюм. Наряд, вдохновлённый Digimon Story: Cyber Sleuth.",
    "825": "Костюм. Наряд, вдохновлённый Digimon Adventure.",
}

WORLDMAP_GROUPS = {
    "1": "Хигаси-Синдзюку",
    "2": "Акихабара",
    "3": "Ниси-Синдзюку",
    "4": "Синдзюку: восточный торговый район",
    "101": "Космическая область",
    "102": "Центральный город",
    "103": "Область Бездны",
    "104": "Зубчатый лес",
    "105": "Факториальная область",
    "106": "Дворец Хранителя",
    "107": "Тёмное Поле",
    "108": "Обратная сторона дворца",
    "109": "Акашические записи",
    "110": "Забытые рельсы",
    "111": "Подземный водный путь Синдзюку",
    "112": "Деревня Восстания",
    "113": "Подземная база спецназа",
    "999": "Промежуточный театр",
}

UI_INFORMAL_REPLACEMENTS = [
    ("Ваш Ранг Агента", "Твой ранг агента"),
    ("Вашего Дигивайса", "Твоего Дигивайса"),
    ("вашего Дигивайса", "твоего Дигивайса"),
    ("вашем Полевом Руководстве", "твоём Полевом руководстве"),
    ("вашем Дигивайсе", "твоём Дигивайсе"),
    ("вашего Дигимона-партнёра", "твоего Дигимона-партнёра"),
    ("вашего Дигимона", "твоего Дигимона"),
    ("ваш Дигимон-партнёр", "твой Дигимон-партнёр"),
    ("Ваш Дигивайс", "Твой Дигивайс"),
    ("ваш Дигивайс", "твой Дигивайс"),
    ("вашу скорость", "твою скорость"),
    ("вашей миссии", "твоей миссии"),
    ("вашей руке", "твоей руке"),
    ("вашу Связь", "твою Связь"),
    ("вашу максимальную вместимость", "твою максимальную вместимость"),
    ("ваш прогресс", "твой прогресс"),
    ("ваш Бокс", "твой Бокс"),
    ("ваш вклад", "твой вклад"),
    ("человека вашего уровня", "человека твоего уровня"),
    ("вашей группы", "твоей группы"),
    ("вашей стороне", "твоей стороне"),
    ("для вас", "для тебя"),
    ("Для вас", "Для тебя"),
    ("у вас", "у тебя"),
    ("У вас", "У тебя"),
    ("вам не даст", "тебе не даст"),
    ("ожидающих вас", "ожидающих тебя"),
    ("позволит вам", "позволит тебе"),
    ("позволяет вам", "позволяет тебе"),
    ("поможет вам", "поможет тебе"),
    ("Вам просто нужно", "Тебе просто нужно"),
    ("вам просто нужно", "тебе просто нужно"),
    ("вам понадобится", "тебе понадобится"),
    ("вернёт вас", "вернёт тебя"),
    ("ваша основная миссия", "твоя основная миссия"),
    ("ваши настройки", "настройки"),
    ("ваших данных", "твоих данных"),
    ("если вы продолжите", "если продолжить"),
    ("Хотите продолжить?", "Продолжить?"),
    ("Ваш следующий бой завершён!", "Следующий бой завершён!"),
    ("Ваш следующий бой завершён,", "Следующий бой завершён,"),
    ("Ваш следующий бой завершён.", "Следующий бой завершён."),
    ("Вам противостоит", "Тебе противостоит"),
    ("Ваши оппоненты", "Твои оппоненты"),
    ("Вас перенесёт", "Тебя перенесёт"),
    ("Вы также можете", "Ты также можешь"),
    ("Вы можете", "Ты можешь"),
    ("Вы получите", "Ты получишь"),
    ("Вы хотите сохранить?", "Сохранить?"),
    ("Вы хотите продолжить?", "Продолжить?"),
]

UI_INFORMAL_FILES = [
    "text/tutorial_explanation.mbe/000_Sheet1.csv",
    "text/yes_no_message.mbe/000_Sheet1.csv",
    "text/digitter_message.mbe/000_Sheet1.csv",
]


def apply_direct_targets(log: list[str]) -> None:
    for root in ROOTS:
        for (relative, key), text in TARGETS.items():
            path = root / relative
            if path.exists():
                replace_id(path, key, text, log)


def apply_item_updates(log: list[str]) -> None:
    for root in ROOTS:
        item_name = root / "text" / "item_name.mbe" / "000_Sheet1.csv"
        item_ruby = root / "text" / "item_ruby.mbe" / "000_Sheet1.csv"
        item_explanation = root / "text" / "item_explanation.mbe" / "000_Sheet1.csv"

        if item_name.exists():
            for key, text in ITEM_NAMES.items():
                upsert_text_row(item_name, key, text, "823" if key == "824" else key, log)

        if item_ruby.exists():
            for key, text in ITEM_RUBY.items():
                upsert_text_row(item_ruby, key, text, "823" if key == "824" else key, log)

        if item_explanation.exists():
            for key, text in ITEM_EXPLANATIONS.items():
                upsert_text_row(item_explanation, key, text, "823" if key == "824" else key, log)


def apply_worldmap_groups(log: list[str]) -> None:
    app_path = CSV_ROOT / "app_text01" / "text" / "worldmap_group_name.mbe" / "000_Sheet1.csv"
    patch_path = CSV_ROOT / "patch_text01" / "text" / "worldmap_group_name.mbe" / "000_Sheet1.csv"
    if not app_path.exists():
        return

    if not patch_path.exists():
        patch_path.parent.mkdir(parents=True, exist_ok=True)
        write_rows(patch_path, read_rows(app_path))
        log.append(f"{patch_path.relative_to(ROOT).as_posix()}: synced from app_text01")

    for path in [app_path, patch_path]:
        for key, text in WORLDMAP_GROUPS.items():
            replace_id(path, key, text, log)


def apply_ui_informal_tone(log: list[str]) -> None:
    for root in ROOTS:
        for relative in UI_INFORMAL_FILES:
            path = root / relative
            if not path.exists():
                continue
            rows = read_rows(path)
            changed = False
            for row in rows[1:]:
                idx = text_index(path, row)
                if idx is None:
                    continue
                old = row[idx]
                new = old
                for src, dst in UI_INFORMAL_REPLACEMENTS:
                    new = new.replace(src, dst)
                if new != old:
                    row[idx] = new
                    changed = True
                    log.append(f"{path.relative_to(ROOT).as_posix()}:{row[0]}: tone")
            if changed:
                write_rows(path, rows)


def main() -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    log: list[str] = []

    apply_direct_targets(log)
    apply_item_updates(log)
    apply_worldmap_groups(log)
    apply_ui_informal_tone(log)

    LOG_PATH.write_text("\n".join(log) + ("\n" if log else ""), encoding="utf-8")
    print(f"Applied {len(log)} changes. Log: {LOG_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()

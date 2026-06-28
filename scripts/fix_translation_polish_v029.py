from __future__ import annotations

import csv
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CSV_ROOT = ROOT / "csv"
LOG_PATH = ROOT / "logs" / "fix_translation_polish_v029.log"

ROOTS = [
    CSV_ROOT / "patch_text01",
    CSV_ROOT / "app_text01",
]


def read_rows(path: Path) -> list[list[str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.reader(f))


def write_rows(path: Path, rows: list[list[str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        if path.parent.name == "minimap_marker_help_text.mbe" and rows:
            csv.writer(f, lineterminator="\r\n").writerow(rows[0])
            csv.writer(f, lineterminator="\r\n", quoting=csv.QUOTE_ALL).writerows(rows[1:])
            return
        csv.writer(f, lineterminator="\r\n").writerows(rows)


def package_name(root: Path) -> str:
    return root.name


def text_index(relative: str, row: list[str]) -> int | None:
    if relative.startswith("message/"):
        return 2 if len(row) > 2 else None
    return 1 if len(row) > 1 else None


def replace_id(path: Path, relative: str, key: str, text: str, log: list[str]) -> bool:
    if not path.exists():
        return False

    rows = read_rows(path)
    changed = False
    for row in rows[1:]:
        if not row or row[0] != key:
            continue

        idx = text_index(relative, row)
        if idx is None or row[idx] == text:
            continue

        old = row[idx]
        row[idx] = text
        changed = True
        log.append(f"{path.relative_to(ROOT).as_posix()}:{key}: {old!r} -> {text!r}")

    if changed:
        write_rows(path, rows)
    return changed


def replace_substring(
    path: Path,
    relative: str,
    key: str,
    old: str,
    new: str,
    log: list[str],
) -> bool:
    if not path.exists():
        return False

    rows = read_rows(path)
    changed = False
    for row in rows[1:]:
        if not row or row[0] != key:
            continue

        idx = text_index(relative, row)
        if idx is None or old not in row[idx]:
            continue

        row[idx] = row[idx].replace(old, new)
        changed = True
        log.append(f"{path.relative_to(ROOT).as_posix()}:{key}: replaced {old!r}")

    if changed:
        write_rows(path, rows)
    return changed


def ensure_patch_copy(relative: str, log: list[str]) -> None:
    app_path = CSV_ROOT / "app_text01" / relative
    patch_path = CSV_ROOT / "patch_text01" / relative
    if patch_path.exists() or not app_path.exists():
        return

    patch_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(app_path, patch_path)
    log.append(f"{patch_path.relative_to(ROOT).as_posix()}: synced from app_text01")


TARGETS: dict[tuple[str, str], str] = {
    ("message/rumor_npc.mbe/000_Sheet1.csv", "r_t0104_0010_0040"):
        "Моя очередь уже подошла? Я умираю с голоду...",
    ("message/t01.mbe/000_Sheet1.csv", "f_t0108_0020_0030"):
        "Если уж говорить о странностях, ты слышал о странной двери в\nпереулке Кабуки-тё?",
    ("message/m050.mbe/000_Sheet1.csv", "m050_030_270"):
        "Но, полагаю, этого следовало ожидать. Наш анализ показывает, что ты\nкаким-то образом был отправлен назад во времени на восемь лет.",
    ("message/m050.mbe/000_Sheet1.csv", "m050_030_280"):
        "Я объединил информацию, которую получал от твоего цифрового\nустройства, с данными о местоположении восьмилетней давности...",
    ("message/m050.mbe/000_Sheet1.csv", "m050_030_290"):
        "...и создал импровизированную систему данных о местоположении.\nЯ бы сказал, она довольно точная.",
    ("message/m050.mbe/000_Sheet1.csv", "m050_040_010"):
        "Кстати, убедись, что ты скрываешь свою личность\nот этого частного детектива.",
    ("message/m060.mbe/000_Sheet1.csv", "m060_020_150"):
        "Я знала, да?! Я знала, что ты тоже так думаешь!",
    ("message/m060.mbe/000_Sheet1.csv", "m060_020_020"):
        "Т-ты говорила то же самое в прошлый раз, и посмотри, что\nслучилось!",
    ("message/m060.mbe/000_Sheet1.csv", "m060_020_190"):
        "Я же говорю, нам пора обратно. Ну же!\nПодземный мир зовёт нас!",
    ("message/m060.mbe/000_Sheet1.csv", "m060_020_240"):
        "Помнишь, что я говорил тебе, агент {player}?",
    ("message/m060.mbe/000_Sheet1.csv", "m060_020_260"):
        "Знаешь, как я смог это сделать? Благодаря видео,\nкоторые восемь лет назад загрузили обычные люди.",
    ("message/m060.mbe/000_Sheet1.csv", "m060_020_280"):
        "Нам пригодится любая крупица информации.\nЯ бы сказал, пойти с ними — не самая плохая идея...",
    ("message/m060.mbe/000_Sheet1.csv", "m060_050_050"):
        "Что такое? Что-то бросилось в глаза?",
    ("message/m060.mbe/000_Sheet1.csv", "m060_070_030"):
        "\"Хотите увидеть, что будет дальше? Тогда ставьте лайк,\nподписывайтесь и включайте уведомления!\"",
    ("message/m070.mbe/000_Sheet1.csv", "m070_020_080"):
        "...В общем, постарайся быть с ней тактичнее.",
    ("message/m070.mbe/000_Sheet1.csv", "m070_030_020"):
        "Слышал, в последнее время у тебя было много дел, Куреми.",
    ("message/m070.mbe/000_Sheet1.csv", "m070_070_030"):
        "Беспокоишься о бюджете, капитан? Бюрократ до мозга костей, не\nтак ли.",
    ("message/m070.mbe/000_Sheet1.csv", "m070_100_010"):
        "Агент {player}, я заново оценил текущую ситуацию.",
    ("text/digitter_message.mbe/000_Sheet1.csv", "main_070_020_012"):
        "Мы примем любую зацепку, которая поможет предотвратить\nбудущую катастрофу, какой бы незначительной она ни казалась.",
    ("text/digitter_message.mbe/000_Sheet1.csv", "digifarm_training_01"):
        "Обучение {fc9{d0}} завершено. Если хочешь продолжить\nтренировки, дай знать.",
    ("message/m140.mbe/000_Sheet1.csv", "m140_020_040"):
        "Агент {player}. Я бы сказал, сейчас хорошее время собрать\nпобольше информации.",
    ("message/m210.mbe/000_Sheet1.csv", "m210_050_040"):
        "Что касается причины... Я бы сказал, что это, скорее всего, яростный\nконфликт между фазово-электронными формами жизни — дигимонами.",
    ("text/char_name.mbe/000_Sheet1.csv", "char_FEMALE_STUDENT"):
        "Студентка",
    ("text/char_name.mbe/000_Sheet1.csv", "char_MYSTERIOUS_DIGIMON"):
        "Загадочный дигимон",
    ("text/char_name.mbe/000_Sheet1.csv", "char_CLIENT_WOMAN"):
        "Заказчица",
    ("text/char_name.mbe/000_Sheet1.csv", "char_CLIENT_WOMAN_FRIEND"):
        "Подруга заказчицы",
    ("text/common_message.mbe/000_Sheet1.csv", "1300"):
        "Заказчик",
    ("text/common_message.mbe/000_Sheet1.csv", "1313"):
        "{fc12Заказчик} {image(ui_digivice_quest_point)} {d0}",
    ("text/common_message.mbe/000_Sheet1.csv", "11108"):
        "Кол-во",
    ("text/common_message.mbe/000_Sheet1.csv", "190018"):
        "Переместить",
    ("text/common_message.mbe/000_Sheet1.csv", "151"):
        "Выполнено",
    ("text/common_message.mbe/000_Sheet1.csv", "ui_hazama_d_0010"):
        "{fc9З}ачищено",
    ("text/common_message.mbe/000_Sheet1.csv", "ui_hazama_d_0070"):
        "Зачищено!",
    ("text/common_message.mbe/000_Sheet1.csv", "ui_title_0090"):
        "Пройдено",
    ("text/common_message.mbe/000_Sheet1.csv", "ui_digifarm_digimon_0021"):
        "Завершить сразу",
    ("text/field_name.mbe/000_Sheet1.csv", "10109"):
        "Синдзюку: переулок",
    ("text/field_name.mbe/000_Sheet1.csv", "10139"):
        "Синдзюку: переулок",
    ("text/field_name.mbe/000_Sheet1.csv", "10203"):
        "Акихабара: переулок",
    ("text/field_name.mbe/000_Sheet1.csv", "10301"):
        "Здание правительства Токио: снаружи",
    ("text/item_name.mbe/000_Sheet1.csv", "47"):
        "Дружба C",
    ("text/item_name.mbe/000_Sheet1.csv", "105"):
        "Приготовленное мясо",
    ("text/item_ruby.mbe/000_Sheet1.csv", "47"):
        "Дружба C",
    ("text/item_ruby.mbe/000_Sheet1.csv", "105"):
        "Приготовленное мясо",
    ("text/worldmap_place_name.mbe/000_Sheet1.csv", "109"):
        "Синдзюку: переулок",
    ("text/worldmap_place_name.mbe/000_Sheet1.csv", "203"):
        "Акихабара: переулок",
    ("text/worldmap_place_name.mbe/000_Sheet1.csv", "301"):
        "Здание правительства Токио: снаружи",
    ("text/minimap_marker_help_text.mbe/000_Sheet1.csv", "minimap_marker_name_0175"):
        "Внешнее подземелье (Зачищено)",
}


SKILL_NAME_TARGETS = {
    "21832": "Манящее эхо",
    "30011": "Напалм I",
    "30012": "Напалм II",
    "30013": "Напалм III",
    "30021": "Вспышка пламени I",
    "30022": "Вспышка пламени II",
    "30023": "Вспышка пламени III",
}


EXACT_REPLACEMENTS = {
    "Студент мужского пола": "Студент",
    "Детектив-фрилансер": "Частный детектив",
    "детектив-фрилансер": "частный детектив",
    "Детектив фрилансер": "Частный детектив",
    "детектив фрилансер": "частный детектив",
}


def apply_direct_targets(log: list[str]) -> None:
    for root in ROOTS:
        if not root.exists():
            continue
        for (relative, key), text in TARGETS.items():
            replace_id(root / relative, relative, key, text, log)


def apply_skill_names(log: list[str]) -> None:
    for relative in [
        "text/skill_name.mbe/000_Sheet1.csv",
        "text/skill_ruby.mbe/000_Sheet1.csv",
        "text/jogress_skill_name.mbe/000_Sheet1.csv",
    ]:
        ensure_patch_copy(relative, log)
        for root in ROOTS:
            path = root / relative
            for key, text in SKILL_NAME_TARGETS.items():
                replace_id(path, relative, key, text, log)


def apply_exact_replacements(log: list[str]) -> None:
    for root in ROOTS:
        if not root.exists():
            continue
        for path in sorted(root.rglob("*.csv")):
            relative = path.relative_to(root).as_posix()
            rows = read_rows(path)
            changed = False
            for row in rows[1:]:
                idx = text_index(relative, row)
                if idx is None:
                    continue
                old_text = row[idx]
                new_text = old_text
                for old, new in EXACT_REPLACEMENTS.items():
                    new_text = new_text.replace(old, new)
                if new_text != old_text:
                    row[idx] = new_text
                    changed = True
                    log.append(f"{path.relative_to(ROOT).as_posix()}:{row[0]}: exact replacement")
            if changed:
                write_rows(path, rows)


def main() -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    log: list[str] = []

    apply_direct_targets(log)
    apply_skill_names(log)
    apply_exact_replacements(log)

    LOG_PATH.write_text("\n".join(log) + ("\n" if log else ""), encoding="utf-8")
    print(f"Applied {len(log)} changes. Log: {LOG_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()

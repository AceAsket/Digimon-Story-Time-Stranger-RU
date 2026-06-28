from __future__ import annotations

import csv
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CSV_ROOT = ROOT / "csv"
APP_ROOT = CSV_ROOT / "app_text01"
PATCH_ROOT = CSV_ROOT / "patch_text01"
LOG_PATH = ROOT / "logs" / "fix_app_only_short_dialogues_v030.log"


def read_rows(path: Path) -> list[list[str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.reader(f))


def write_rows(path: Path, rows: list[list[str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        csv.writer(f, lineterminator="\r\n").writerows(rows)


def ensure_patch_copy(relative: str, log: list[str]) -> None:
    app_path = APP_ROOT / relative
    patch_path = PATCH_ROOT / relative
    if patch_path.exists() or not app_path.exists():
        return
    patch_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(app_path, patch_path)
    log.append(f"{patch_path.relative_to(ROOT).as_posix()}: synced from app_text01")


TRANSLATIONS: dict[tuple[str, str], str] = {
    ("message/m370.mbe/000_Sheet1.csv", "m370_020_010"):
        "Коронамон и Лунамон...?",
    ("message/m370.mbe/000_Sheet1.csv", "m370_020_020"):
        "А, значит, раньше их так звали. Теперь это\nАполломон и Дианамон.",
    ("message/m370.mbe/000_Sheet1.csv", "m370_020_030"):
        "Дианамон совсем рядом, но...",
    ("message/m370.mbe/000_Sheet1.csv", "m370_020_040"):
        "...добраться до неё будет непросто. Эти двое\nдавно в ссоре.",
    ("message/m370.mbe/000_Sheet1.csv", "m370_020_050"):
        "Они не пропускают посланников друг друга и\nзаперлись каждый у себя.",
    ("message/m370.mbe/000_Sheet1.csv", "m370_020_060"):
        "Если вы всё равно хотите идти, я вас не остановлю...",
    ("message/m370.mbe/000_Sheet1.csv", "m370_020_070"):
        "Но я бы посоветовал сначала поговорить с Аполломоном.\nОн хотя бы ещё готов слушать...",
    ("message/m370.mbe/000_Sheet1.csv", "m370_100_010"):
        "...А это ещё кто?",
    ("message/m370.mbe/000_Sheet1.csv", "m370_100_020"):
        "Я уже знаю, что вы хотите сказать.",
    ("message/m370.mbe/000_Sheet1.csv", "m370_100_030"):
        "Хотите, чтобы я помирился с Дианамон, верно?",
    ("message/m370.mbe/000_Sheet1.csv", "m370_100_050"):
        "Дианамон сама всё испортила. Посторонние,\nуходите немедленно.",
    ("message/m370.mbe/000_Sheet1.csv", "m370_100_070"):
        "Я ведь велел вам уйти! Или вас подпалить,\nчтобы вы наконец убрались?!",
    ("message/m370.mbe/000_Sheet1.csv", "m370_110_010"):
        "В-вы... и правда сильны...",
    ("message/m370.mbe/000_Sheet1.csv", "m370_110_030"):
        "Постойте! Неужели вы... Вы что—?!",
    ("message/m370.mbe/000_Sheet1.csv", "m370_110_040"):
        "Вы меня помните?",
    ("message/m370.mbe/000_Sheet1.csv", "m370_110_050"):
        "Вы тоже слышали слухи о Дианамон?",
    ("message/m370.mbe/000_Sheet1.csv", "m370_110_060"):
        "Понятно... Я не хотел в это верить, но, похоже,\nпридётся...",
    ("message/m370.mbe/000_Sheet1.csv", "m370_110_070"):
        "Раз уж до этого дошло, я сам разберусь с Дианамон.\nТаков долг семьи...!",
    ("message/m380.mbe/000_Sheet1.csv", "m380_010_010"):
        "Минерва должна быть внутри, а вместе с ней и знание,\nкоторое вы ищете.",
    ("message/m380.mbe/000_Sheet1.csv", "m380_010_020"):
        "Давно я так не загорался... Ну же,\nидём вперёд.",
    ("message/m380.mbe/000_Sheet1.csv", "m380_020_010"):
        "Минерва!",
    ("message/m380.mbe/000_Sheet1.csv", "m380_020_030"):
        "Корона...мон?",
    ("message/m380.mbe/000_Sheet1.csv", "m380_020_040"):
        "Почему ты в тюрьме?! Что здесь произошло?!",
    ("message/m380.mbe/000_Sheet1.csv", "m380_020_050"):
        "Видишь ли—",
    ("message/m380.mbe/000_Sheet1.csv", "m380_020_060"):
        "Стой. Что?!",
    ("message/m380.mbe/000_Sheet1.csv", "m380_020_070"):
        "Этот человек с тобой...!",
    ("message/m380.mbe/000_Sheet1.csv", "m380_020_080"):
        "Давно не виделись.",
    ("message/m380.mbe/000_Sheet1.csv", "m380_020_081"):
        "Вижу, ты меня помнишь.",
    ("message/m380.mbe/000_Sheet1.csv", "m380_020_082"):
        "Ты совсем не изменилась.",
    ("message/m380.mbe/000_Sheet1.csv", "m380_020_090"):
        "Сколько же времени прошло?",
    ("message/m380.mbe/000_Sheet1.csv", "m380_020_100"):
        "Мы сейчас же тебя вытащим—",
    ("message/m380.mbe/000_Sheet1.csv", "m380_020_110"):
        "Эту камеру так просто не сломать. Поверь, я пробовала.",
    ("message/m380.mbe/000_Sheet1.csv", "m380_020_120"):
        "Куда важнее другое... Мне нужно, чтобы вы передали\nсообщение Меркуримону.",
    ("message/m380.mbe/000_Sheet1.csv", "m380_020_130"):
        "Тот, кто запер меня здесь... это была Юномон.",
    ("message/m380.mbe/000_Sheet1.csv", "m380_020_140"):
        "...Что?",
    ("message/m380.mbe/000_Sheet1.csv", "m380_020_150"):
        "И это ещё не всё.",
    ("message/m380.mbe/000_Sheet1.csv", "m380_020_160"):
        "Во время инцидента, произошедшего в Синдзюку\nвосемь лет назад...",
    ("message/m380.mbe/000_Sheet1.csv", "m380_020_170"):
        "...люди захватили нескольких дигимонов, включая\nнескольких Титанов.",
    ("message/m380.mbe/000_Sheet1.csv", "m380_020_180"):
        "По слухам... над ними проводили ужасные эксперименты.",
    ("message/m380.mbe/000_Sheet1.csv", "m380_020_190"):
        "Когда Титаны об этом узнали, они пришли в ярость.\nОни даже собирались вторгнуться в мир людей.",
    ("message/m380.mbe/000_Sheet1.csv", "m380_020_200"):
        "Похоже, именно поэтому они планировали открыть\nврата храма.",
    ("message/m380.mbe/000_Sheet1.csv", "m380_020_210"):
        "Я попыталась доложить об этом Юномон, но стоило\nмне заговорить... Юномон вдруг стала совсем другой...",
    ("message/m380.mbe/000_Sheet1.csv", "m380_020_220"):
        "Поторопитесь и передайте мои слова. Вытащить меня\nотсюда успеете потом.",
}


def apply_translations(log: list[str]) -> None:
    by_file: dict[str, dict[str, str]] = {}
    for (relative, key), text in TRANSLATIONS.items():
        by_file.setdefault(relative, {})[key] = text

    for relative, replacements in by_file.items():
        ensure_patch_copy(relative, log)
        for root in [PATCH_ROOT, APP_ROOT]:
            path = root / relative
            if not path.exists():
                continue
            rows = read_rows(path)
            changed = False
            for row in rows[1:]:
                if len(row) < 3:
                    continue
                text = replacements.get(row[0])
                if text is None or row[2] == text:
                    continue
                old = row[2]
                row[2] = text
                changed = True
                log.append(f"{path.relative_to(ROOT).as_posix()}:{row[0]}: {old!r} -> {text!r}")
            if changed:
                write_rows(path, rows)


def main() -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    log: list[str] = []
    apply_translations(log)
    LOG_PATH.write_text("\n".join(log) + ("\n" if log else ""), encoding="utf-8")
    print(f"Applied {len(log)} changes. Log: {LOG_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()

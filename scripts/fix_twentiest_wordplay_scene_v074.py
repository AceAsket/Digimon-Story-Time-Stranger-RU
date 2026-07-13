#!/usr/bin/env python3
"""Relocalize the complete Twentiest fashion-wordplay scene.

The English term combines ``twenty`` with a superlative ending.  The previous
Russian text used four incompatible literal renderings and lost both the joke
and the scene's progression.  ``двадцатейший / Двадцатейшесть`` deliberately
sound coined, support the adapted "двадцати шести" reply, and remain stable
through all three Digimon forms in the quest.
"""

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = (
    ROOT
    / "csv"
    / "patch_text01"
    / "message"
    / "s010_159.mbe"
    / "000_Sheet1.csv"
)


UPDATES: dict[str, str] = {
    "s010_159_010": (
        "Эй! Давно не виделись. Вопрос ни с того ни с сего, но...\n"
        "что значит быть «двадцатейшим»?"
    ),
    "s010_159_020": "{next}Вопрос не из лёгких.",
    "s010_159_021": "{next}Никто не знает.",
    "s010_159_022": "{next}Дожить до двадцати шести.",
    "s010_159_030": (
        "Вот и я о том! А ведь ещё недавно мне казалось,\n"
        "что я во всём разобрался..."
    ),
    "s010_159_040": (
        "Может, все стремятся к Двадцатейшести именно потому,\n"
        "что никто не знает, что это."
    ),
    "s010_159_050": (
        "Ха-ха... Пытаешься подбодрить меня шуткой?\n"
        "Всё равно спасибо."
    ),
    "s010_159_060": (
        "Я больше не понимаю, что сейчас «в тренде».\n"
        "Будто сбился с пути к Двадцатейшести."
    ),
    "s010_159_070": (
        "Нет ничего хуже обыденности. Ты только ПОСМОТРИ\n"
        "на свой наряд!"
    ),
    "s010_159_080": "{next}Разве быть обычным так плохо?",
    "s010_159_081": "{next}Что не так с моим нарядом?",
    "s010_159_082": "{next}Может, добавить яркости?",
    "s010_159_090": (
        "Ужасно! Когда ты как все, тебя не замечают.\n"
        "Двадцатейший обязан выделяться!"
    ),
    "s010_159_100": (
        "Если бы я знал КАК, не метался бы! Твоя одежда должна\n"
        "быть рваной, оплавленной... какой угодно необычной!"
    ),
    "s010_159_110": (
        "Добавить яркости... Точно! Импровизация и творческое\n"
        "самовыражение — это так по-двадцатейшему!"
    ),
    "s010_159_120": (
        "О! Кажется, разговор с тобой приблизил меня к самой сути\n"
        "Двадцатейшести. Спасибо!"
    ),
    "s010_159_130": (
        "Слушай... В следующий раз покажешь мне\n"
        "ещё какой-нибудь модный образ?"
    ),
    "s010_159_140": (
        "Футболка с дигимоном — идеальный способ вывести меня\n"
        "из творческого тупика. Спасибо!"
    ),
    "s010_159_150": (
        "Хочу увидеть образ, над которым ты как следует потрудишься.\n"
        "Ничего обычного."
    ),
    "s010_159_160": "О! Это ты! А этот наряд... просто двадцатейший!",
    "s010_159_170": "{next}Правда?",
    "s010_159_171": "{next}Значит, наряд помог?",
    "s010_159_172": "{next}Наконец-то понял?",
    "s010_159_180": (
        "Да! Изюминка, которая выводит обычную моду за рамки...\n"
        "Вот она — Двадцатейшесть!"
    ),
    "s010_159_190": (
        "Именно! Теперь вдохновение осеняет меня\n"
        "тридцать раз в секунду!"
    ),
    "s010_159_200": (
        "Ха-ха... Да, наконец-то! Позволь хоть раз назвать тебя\n"
        "Мастером Двадцатейшести!"
    ),
    "s010_159_210": (
        "Твой стиль — как обычное острое карри\n"
        "с капелькой мёда!"
    ),
    "s010_159_220": (
        "Я слишком старался. Чем сильнее хочешь стать двадцатейшим,\n"
        "тем дальше оказываешься от Двадцатейшести."
    ),
    "s010_159_230": (
        "С яркостью нельзя перебарщивать! Пусть она будет\n"
        "лишь акцентом в простом образе."
    ),
    "s010_159_240": "{next}Ты быстро учишься.",
    "s010_159_241": "{next}К Двадцатейшести лёгких путей нет.",
    "s010_159_242": "{next}Как готовить без изысканных ингредиентов?",
    "s010_159_250": (
        "Понятно. Значит, я наконец-то поднялся\n"
        "с тобой на одну высоту..."
    ),
    "s010_159_260": (
        "Верно. Путь извилист: порой теряется,\n"
        "порой расходится на несколько дорог."
    ),
    "s010_159_270": (
        "Что? Сравниваешь Двадцатейшесть с кулинарией? Чушь!\n"
        "Ещё скажи, что это как карри!"
    ),
    "s010_159_280": (
        "Истина Двадцатейшести заставляет меня эволюционировать!\n"
        "К новым вершинам моды!"
    ),
    "s010_159_290": "А-а-а-а!",
    "s010_159_300": (
        "Эта форма доказывает, что я стал ближе к Двадцатейшести!\n"
        "И всё благодаря тебе!"
    ),
    "s010_159_310": (
        "Лучше всего быть обычным. Похоже,\n"
        "раньше я это недооценивал."
    ),
    "s010_159_320": (
        "Слышал, в Промышленной зоне есть арена. Хочу испытать себя\n"
        "в модном поединке!"
    ),
    "s010_159_330": (
        "Я выбрал обычный путь, трудился как обычно и победил...\n"
        "Но всё оказалось таким... обычным!"
    ),
    "s010_159_340": (
        "Неужели это всё, что даёт обыденность? Неужели...\n"
        "это мой предел?"
    ),
    "s010_159_350": "Возможно, теперь нужно свернуть с обычного пути...",
    "s010_159_355": (
        "Не позволю всему так закончиться! Я... буду выделяться!\n"
        "Поднимусь над обыденностью!"
    ),
    "s010_159_360": (
        "Этот проклятый клинок необычайно остёр. Он вернул меня\n"
        "на путь Двадцатейшести."
    ),
    "s010_159_370": "{next}Сразу видно — сил у тебя прибавилось.",
    "s010_159_371": "{next}Опять Двадцатейшесть?",
    "s010_159_372": "{next}Проклятое оружие тоже может быть мощным.",
    "s010_159_380": (
        "Хех... Тоже так думаешь? Согласен. Не терпится\n"
        "испытать обретённую силу!"
    ),
    "s010_159_390": (
        "Да... Для дигимона всё начинается и заканчивается\n"
        "Двадцатейшестью. Такова природа вещей."
    ),
    "s010_159_400": (
        "Почему проклятие обязательно должно быть злом? Клянусь честью\n"
        "Двадцатейшего: я овладею этим оружием!"
    ),
    "s010_159_410": (
        "Испытаю новую силу в Райском колизее.\n"
        "Буду ждать твоего вызова!"
    ),
}


if len(UPDATES) != 52:
    raise ValueError(f"expected all 52 scene rows, got {len(UPDATES)}")


def serialization(path: Path) -> tuple[str, str, bool]:
    raw = path.read_bytes()
    bom = raw.startswith(b"\xef\xbb\xbf")
    body = raw.removeprefix(b"\xef\xbb\xbf")
    newline = "\r\n" if b"\r\n" in body else "\n"
    lines = body.splitlines()
    quote_all = len(lines) > 1 and lines[1].lstrip().startswith(b'"')
    return ("utf-8-sig" if bom else "utf-8"), newline, quote_all


def write_rows(path: Path, rows: list[list[str]]) -> None:
    encoding, newline, quote_all = serialization(path)
    with path.open("w", encoding=encoding, newline="") as handle:
        writer = csv.writer(
            handle,
            lineterminator=newline,
            quoting=csv.QUOTE_ALL if quote_all else csv.QUOTE_MINIMAL,
        )
        if quote_all:
            csv.writer(handle, lineterminator=newline).writerow(rows[0])
            writer.writerows(rows[1:])
        else:
            writer.writerows(rows)


def apply_updates() -> tuple[int, int]:
    with CSV_PATH.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.reader(handle))

    counts = {row_id: 0 for row_id in UPDATES}
    changed = current = 0
    for row in rows[1:]:
        if not row or row[0] not in UPDATES:
            continue
        counts[row[0]] += 1
        if len(row) <= 2:
            raise RuntimeError(f"Missing text column: {CSV_PATH}:{row[0]}")
        if row[2] == UPDATES[row[0]]:
            current += 1
        else:
            changed += 1

    missing = [row_id for row_id, count in counts.items() if count == 0]
    duplicates = {row_id: count for row_id, count in counts.items() if count > 1}
    if missing or duplicates:
        raise RuntimeError(
            f"Target cardinality failure: missing={missing}, counts={duplicates}"
        )

    if changed:
        for row in rows[1:]:
            if row and row[0] in UPDATES:
                row[2] = UPDATES[row[0]]
        write_rows(CSV_PATH, rows)
    return changed, current


def main() -> None:
    changed, current = apply_updates()
    print(f"Targets: {len(UPDATES)}")
    print(f"Changed: {changed}")
    print(f"Already current: {current}")


if __name__ == "__main__":
    main()

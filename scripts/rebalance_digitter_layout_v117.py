#!/usr/bin/env python3
"""Rebalance Digitter lines that exceed the width seen in game."""

from __future__ import annotations

import csv
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "csv/patch_text01/text/digitter_message.mbe/000_Sheet1.csv"
TAG_RE = re.compile(r"\{[^}]+\}")
TRIGGER_WIDTH = 60
TARGET_WIDTH = 56

MANUAL = {
    "main_180_010_011": (
        "Бьюсь об заклад, ты помнишь таинственное исчезновение твоего\n"
        "собственного приёмного отца. Существует отчётливая возможность,\n"
        "что доктор Юки оказался там, в том мире.",
        "Ты наверняка помнишь загадочное исчезновение своего\n"
        "приёмного отца. Возможно, доктор Юки попал в тот мир.",
    ),
    "main_260_050_012": (
        "Но если аномалии на самом деле связаны с Дигимонами, ассоциация\n"
        "начинает размываться. Если бы мы только могли понять принципы,\n"
        "стоящие за всем этим, мы могли бы взорвать всё это дело.",
        "Но если аномалии действительно связаны с дигимонами,\n"
        "всё становится запутаннее. Разберёмся в принципах\n"
        "этой связи — и сможем раскрыть всю правду.",
    ),
    "main_400_000_020": (
        'Они утверждают, что оно предназначено для "контроля", но на\n'
        "самом деле это просто машина для убийств. Отключи ограничитель,\n"
        "и оно, по-видимому, уничтожит каждую биоподпись в окрестностях.",
        "Они называют это средством «контроля», но на деле это\n"
        "машина для убийств. Сними ограничитель — и она уничтожит\n"
        "все биосигнатуры поблизости.",
    ),
    "sub_seekhiroko_090_010": (
        "Мне приснился сон о том, как я спускаюсь под оживленный город. Я\n"
        "продолжал спускаться всё ниже и ниже через все эти повороты и\n"
        "изгибы... Типа, обойдусь без этой влажности, хотя! Фух!",
        "Мне снилось, будто я спускаюсь под шумный город — всё\n"
        "ниже и ниже, по бесконечным извилистым ходам... А там\n"
        "такая сырость! Бр-р!",
    ),
    "sub_seekhiroko_130_010": (
        "Я побывал в этой сверкающей комнате во сне. Там было то, что,\n"
        "как мне кажется, было стулом, очень высоким, с действительно\n"
        "большим лицом на нём. Извини. Я знаю, это трудно представить!",
        "Во сне я оказался в сверкающем зале. Там высоко стоял\n"
        "какой-то трон с огромным лицом. Прости, знаю, звучит\n"
        "невразумительно!",
    ),
    "hazama_99_100_4": (
        "Тем не менее, раздражает невозможность оценить характеристики\n"
        "противника, не сразившись с ним сначала. Если бы только был\n"
        "какой-то способ узнать его статистику заранее...",
        "Жаль, что силу противника нельзя оценить до боя.\n"
        "Вот бы узнавать его характеристики заранее...",
    ),
}


def visible_length(text: str) -> int:
    return len(TAG_RE.sub("", text))


def wrap_words(text: str) -> list[str]:
    lines: list[str] = []
    current = ""
    for word in text.replace("\n", " ").split():
        candidate = word if not current else f"{current} {word}"
        if current and visible_length(candidate) > TARGET_WIDTH:
            lines.append(current)
            current = word
        else:
            current = candidate
    if current:
        lines.append(current)
    return lines


def reflow(text: str) -> str:
    original_lines = text.splitlines() or [""]
    decision_lines = [line.strip() for line in original_lines if "{decision}" in line]
    if decision_lines and original_lines[-len(decision_lines) :] != decision_lines:
        raise SystemExit(f"Decision line is not at the end: {text!r}")
    body_lines = [
        line.strip()
        for line in original_lines
        if line.strip() and "{decision}" not in line
    ]
    result = wrap_words(" ".join(body_lines)) + decision_lines
    allowed_lines = 4 if decision_lines else 3
    if len(result) > allowed_lines:
        raise SystemExit(f"Reflow needs {len(result)} lines: {text!r}")
    if max((visible_length(line) for line in result), default=0) > TARGET_WIDTH:
        raise SystemExit(f"Reflow still exceeds target width: {text!r}")
    return "\n".join(result)


def main() -> None:
    with PATH.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.reader(handle))
    by_id = {row[0]: row for row in rows if len(row) >= 2}

    manual_changed = 0
    manual_current = 0
    for row_id, (old, new) in MANUAL.items():
        row = by_id.get(row_id)
        if row is None:
            raise SystemExit(f"Missing Digitter row: {row_id}")
        if row[1] == new:
            manual_current += 1
        elif row[1] == old:
            row[1] = new
            manual_changed += 1
        else:
            raise SystemExit(f"Unexpected Digitter text for {row_id}: {row[1]!r}")

    reflowed = 0
    for row in rows[1:]:
        if len(row) < 2:
            continue
        lines = row[1].splitlines() or [""]
        if max((visible_length(line) for line in lines), default=0) <= TRIGGER_WIDTH:
            continue
        row[1] = reflow(row[1])
        reflowed += 1

    if reflowed not in (0, 194):
        raise SystemExit(f"Unexpected number of reflowed rows: {reflowed}")
    if manual_changed or reflowed:
        with PATH.open("w", encoding="utf-8", newline="") as handle:
            csv.writer(handle, lineterminator="\n").writerows(rows)

    remaining = [
        row[0]
        for row in rows[1:]
        if len(row) >= 2
        and max((visible_length(line) for line in row[1].splitlines()), default=0)
        > TRIGGER_WIDTH
    ]
    if remaining:
        raise SystemExit(f"Overlong Digitter rows remain: {remaining[:10]}")

    print(f"Manual changes: {manual_changed}")
    print(f"Manual already current: {manual_current}")
    print(f"Reflowed rows: {reflowed}")
    print(f"Remaining over {TRIGGER_WIDTH}: {len(remaining)}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Fix source-confirmed item/skill semantics and terminology inconsistencies."""

from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CSV_ROOT = ROOT / "csv/patch_text01/text"


UPDATES: dict[tuple[str, str], tuple[str, str]] = {
    ("skill_auto_explanation.mbe/000_Sheet1.csv", "29"): (
        "{d0}% крит.",
        "{d0}% шанс крита.",
    ),
    ("tamer_skill_explanation.mbe/000_Sheet1.csv", "5"): (
        "Повышает получаемый в бою опыт для сражающихся и запасных\n"
        "дигимонов с чертами Смелый, Ревностный, Отважный и\n"
        "Безрассудный на {d0}% за каждый ранг Агента.",
        "Повышает получаемый в бою ОПТ для сражающихся и запасных\n"
        "дигимонов с чертами Смелый, Ревностный, Отважный и\n"
        "Безрассудный на {d0}% за каждый ранг Агента.",
    ),
    ("tamer_skill_explanation.mbe/000_Sheet1.csv", "42"): (
        "Повышает получаемый в бою опыт для сражающихся и запасных\n"
        "дигимонов с чертами Смелый, Ревностный, Отважный и\n"
        "Безрассудный на {d0}% за каждый ранг Агента.",
        "Повышает получаемый в бою ОПТ для сражающихся и запасных\n"
        "дигимонов с чертами Смелый, Ревностный, Отважный и\n"
        "Безрассудный на {d0}% за каждый ранг Агента.",
    ),
    ("tamer_skill_explanation.mbe/000_Sheet1.csv", "13"): (
        "Повышает SP дигимонов с чертами Смелый, Ревностный,\n"
        "Отважный и Безрассудный на {d1}%.",
        "Повышает ОС дигимонов с чертами Смелый, Ревностный,\n"
        "Отважный и Безрассудный на {d1}%.",
    ),
    ("skill_name.mbe/000_Sheet1.csv", "34061"): (
        "Волшебное Отражение",
        "Магическое отражение",
    ),
    ("skill_ruby.mbe/000_Sheet1.csv", "34061"): (
        "Волшебное Отражение",
        "Магическое отражение",
    ),
    ("jogress_skill_name.mbe/000_Sheet1.csv", "34061"): (
        "Волшебное Отражение",
        "Магическое отражение",
    ),
    ("skill_explanation.mbe/000_Sheet1.csv", "11023"): (
        "[Цель: Все союзники] Повышение на 50% до АТК / ЗАЩ / ИНТ / ДУХ / СКР на 2 хода.",
        "[Цель: все союзники]\nНа 2 хода повышает АТК, ЗАЩ, ИНТ, ДУХ и СКР на 50%.",
    ),
    ("skill_explanation.mbe/000_Sheet1.csv", "11024"): (
        "[Цель: все враги] Наносит незначительный урон. Всегда попадает. Снижение на 25% до АТК / ЗАЩ / ИНТ / ДУХ на 4 хода.",
        "[Цель: все враги]\nНаносит небольшой урон и всегда попадает.\n"
        "На 4 хода снижает АТК, ЗАЩ, ИНТ и ДУХ на 25%.",
    ),
    ("skill_explanation.mbe/000_Sheet1.csv", "11025"): (
        "[Цель: Все союзники] 50% повышение уровня АТК / ЗАЩ / ИНТ / ДУХ / СКР на 3 хода. Сводит к нулю физический / магический урон на 1 ход.",
        "[Цель: все союзники]\nНа 3 хода повышает АТК, ЗАЩ, ИНТ, ДУХ и СКР на 50%.\n"
        "На 1 ход полностью блокирует физический и магический урон.",
    ),
    ("skill_explanation.mbe/000_Sheet1.csv", "34041"): (
        "[Цель: 1 враг] Удаляет статусные усиления.",
        "[Цель: 1 враг]\nСнимает усиления характеристик.",
    ),
    ("skill_explanation.mbe/000_Sheet1.csv", "31041"): (
        "[Цель: 1 союзник] Удаляет аномалии состояния.",
        "[Цель: 1 союзник]\nСнимает негативные состояния.",
    ),
    ("skill_explanation.mbe/000_Sheet1.csv", "22322"): (
        "[Цель: все враги] 100% вероятность снижения ДУХ на 30% и МЕТ на 10% на 3 хода.",
        "[Цель: все враги]\nНа 3 хода со 100% вероятностью снижает ДУХ на 30%,\nа МЕТ — на 10%.",
    ),
    ("skill_explanation.mbe/000_Sheet1.csv", "80040"): (
        "[Цель: 1 союзник] Увеличивает МЕТ / УКЛ / КРТ на 20% на 3 хода.",
        "[Цель: 1 союзник]\nНа 3 хода повышает МЕТ, УКЛ и КРТ на 20%.",
    ),
    ("skill_explanation.mbe/000_Sheet1.csv", "23751"): (
        "[Цель: 1 враг] Наносит 5% урона HP. 100% вероятность снижения уровня защиты на 15% на 3 хода.",
        "[Цель: 1 враг]\nНаносит урон в размере 5% ОЗ.\n"
        "На 3 хода со 100% вероятностью снижает ЗАЩ и ДУХ на 15%.",
    ),
    ("skill_explanation.mbe/000_Sheet1.csv", "21131"): (
        "[Цель: все враги] Наносит 2% урона HP за 3 попадания. 100% вероятность снижения ДУХ на 15% за 3 хода.",
        "[Цель: все враги]\nНаносит 3 удара по 2% ОЗ.\n"
        "На 3 хода со 100% вероятностью снижает ДУХ на 15%.",
    ),
    ("skill_explanation.mbe/000_Sheet1.csv", "20701"): (
        "[Цель: 1 враг] Наносит 5% урона HP. 100% вероятность снижения ДУХ на 25% на 3 хода.",
        "[Цель: 1 враг]\nНаносит урон в размере 5% ОЗ.\n"
        "На 3 хода со 100% вероятностью снижает ДУХ на 25%.",
    ),
    ("skill_explanation.mbe/000_Sheet1.csv", "20691"): (
        "[Цель: все враги] Наносит 2% урона HP за 3 попадания. 100% шанс снижения на 10% до ИНТ / ДУХ на 3 хода.",
        "[Цель: все враги]\nНаносит 3 удара по 2% ОЗ.\n"
        "На 3 хода со 100% вероятностью снижает ИНТ и ДУХ на 10%.",
    ),
    ("skill_explanation.mbe/000_Sheet1.csv", "21721"): (
        "[Цель: 1 враг] Наносит фиксированный урон мощностью 10 х 3 попадания. 100% вероятность снижения на 30% до АТК / ИНТ на 3 хода. Удаляет статусные усиления.",
        "[Цель: 1 враг]\nНаносит 3 удара фиксированного урона силой 10.\n"
        "На 3 хода со 100% вероятностью снижает АТК и ИНТ на 30%.\n"
        "Снимает усиления характеристик.",
    ),
}


def main() -> None:
    by_file: dict[str, list[tuple[str, str, str]]] = defaultdict(list)
    for (relative, row_id), (old, new) in UPDATES.items():
        by_file[relative].append((row_id, old, new))

    changed = 0
    current = 0
    for relative, updates in sorted(by_file.items()):
        path = CSV_ROOT / relative
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.reader(handle))
        row_by_id = {row[0]: row for row in rows if row}
        file_changed = False
        for row_id, old, new in updates:
            row = row_by_id.get(row_id)
            if row is None or len(row) < 2:
                raise SystemExit(f"Missing or malformed row {row_id!r} in {path}")
            if row[1] == new:
                current += 1
            elif row[1] == old:
                row[1] = new
                changed += 1
                file_changed = True
            else:
                raise SystemExit(
                    f"Unexpected text for {relative}:{row_id}:\n"
                    f"expected: {old!r}\nactual:   {row[1]!r}"
                )
        if file_changed:
            with path.open("w", encoding="utf-8-sig", newline="") as handle:
                csv.writer(handle, lineterminator="\n").writerows(rows)

    longest = max(len(line) for _, new in UPDATES.values() for line in new.splitlines())
    print(f"Targets: {len(UPDATES)}")
    print(f"Changed: {changed}")
    print(f"Already current: {current}")
    print(f"Longest replacement line: {longest}")


if __name__ == "__main__":
    main()

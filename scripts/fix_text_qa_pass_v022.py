from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CSV_ROOTS = [
    ROOT / "csv" / "app_text01",
    ROOT / "csv" / "patch_text01",
]


TARGETED_ROWS: dict[tuple[str, str], str] = {
    ("message/m040.mbe/000_Sheet1.csv", "m040_130_100"): (
        "То есть... ты никуда не уйдёшь, пока я не получу\n"
        "ответы на все эти вопросы..."
    ),
    ("message/m040.mbe/000_Sheet1.csv", "m040_130_110"): (
        "Если тебя это устраивает, можешь какое-то время\n"
        "пожить у нас."
    ),
    ("message/m040.mbe/000_Sheet1.csv", "m040_130_140"): (
        "Н-нет, просто обычно ты бы никогда\n"
        "такого не позволил..."
    ),
    ("message/m040.mbe/000_Sheet1.csv", "m040_130_150"): (
        'Ты же вечно заводишь: "Ты хоть знаешь, сколько ей лет?"\n'
        'и "Держись подальше от моей дочери!"...'
    ),
    ("message/m040.mbe/000_Sheet1.csv", "m040_130_160"): (
        "О-ох, ну, это..."
    ),
    ("message/m040.mbe/000_Sheet1.csv", "m040_130_170"): (
        "...Я должен заботиться о тебе как можно лучше.\n"
        "Ради твоей матери..."
    ),
    ("message/m040.mbe/000_Sheet1.csv", "m040_130_180"): (
        "Иначе, когда я встречусь с ней на том свете,\n"
        "она мне этого не простит."
    ),
    ("message/m040.mbe/000_Sheet1.csv", "m040_130_190"): (
        "Послушай. Со мной всё будет хорошо..."
    ),
    ("message/m040.mbe/000_Sheet1.csv", "m040_130_200"): (
        "Я пытаюсь сказать... что тебе давно пора..."
    ),
    ("message/m040.mbe/000_Sheet1.csv", "m040_130_210"): (
        "Пора жить своей жизнью, папа..."
    ),
    ("message/m040.mbe/000_Sheet1.csv", "m040_130_220"): (
        "...Разговор окончен. Пока просто идём домой."
    ),
    ("message/m040.mbe/000_Sheet1.csv", "m040_130_230"): (
        "И не думай, что я забыл про обещанную лекцию."
    ),
    ("message/m050.mbe/000_Sheet1.csv", "m050_010_140"): (
        "...Наконец-то, наконец-то связь восстановлена!\n"
        "Привет, агент {игрок}!"
    ),
    ("message/m050.mbe/000_Sheet1.csv", "m050_010_150"): (
        "Мне удалось разобрать фрагменты аудио из твоего канала связи.\n"
        "Даже не знаю, с чего начать."
    ),
    ("message/m050.mbe/000_Sheet1.csv", "m050_010_160"): (
        "...Итак, с твоей позиции здание правительства Токио\n"
        "выглядит совершенно невредимым?"
    ),
    ("message/m050.mbe/000_Sheet1.csv", "m050_010_170"): (
        "А картинка Синдзюку, которую вижу я...\n"
        "это настоящий ад. Словами не передать."
    ),
    ("message/m050.mbe/000_Sheet1.csv", "m050_010_180"): (
        "Я также подтвердил: по координатам,\n"
        "отмеченным как твоё «текущее» местоположение, тебя нет."
    ),
    ("message/m050.mbe/000_Sheet1.csv", "m050_010_190"): (
        "Сопоставив все данные, аналитический отдел\n"
        "пришёл к выводу, что..."
    ),
    ("message/m050.mbe/000_Sheet1.csv", "m050_010_200"): (
        "..тебя перенесло во времени в прошлое."
    ),
    ("message/m050.mbe/000_Sheet1.csv", "m050_010_210"): (
        "Это беспрецедентная аномалия. Как мы вообще\n"
        "можем сейчас разговаривать?!"
    ),
    ("message/m050.mbe/000_Sheet1.csv", "m050_010_220"): (
        "Остаётся только надеяться, что связь не оборвётся."
    ),
    ("message/m350.mbe/000_Sheet1.csv", "m350_010_030"): (
        "Похоже, тебя снова перенесло во времени... но на этот раз\n"
        "что-то не так... Эгимона нет рядом."
    ),
    ("message/m350.mbe/000_Sheet1.csv", "m350_010_060"): (
        "За их безопасность я волнуюсь... но куда важнее то,\n"
        "что перенос во времени произошёл без Эгимона."
    ),
    ("message/m350.mbe/000_Sheet1.csv", "m350_010_070"): (
        "Именно: перенос во времени произошёл\n"
        "без присутствия Эгимона."
    ),
    ("message/m350.mbe/000_Sheet1.csv", "m350_010_090"): (
        "Если вспомнить, первое путешествие во времени\n"
        "тоже прошло без сопровождения."
    ),
    ("message/m350.mbe/000_Sheet1.csv", "m350_020_010"): (
        "То, что Меркуримон жив, — надёжное доказательство\n"
        "переноса во времени."
    ),
    ("message/m350.mbe/000_Sheet1.csv", "m350_020_030"): (
        "Нужно повторить попытку — и не допустить Ада Синдзюку."
    ),
}


def read_rows(path: Path) -> list[list[str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.reader(f))


def write_rows(path: Path, rows: list[list[str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, lineterminator="\n")
        writer.writerows(rows)


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
                if len(row) < 3:
                    continue
                value = replacements.get(row[0])
                if value is None or row[2] == value:
                    continue
                row[2] = value
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

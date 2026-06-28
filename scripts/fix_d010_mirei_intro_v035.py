from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CSV_ROOT = ROOT / "csv"
RELATIVE = "patch_text01/message/d010.mbe/000_Sheet1.csv"
LOG_PATH = ROOT / "logs" / "fix_d010_mirei_intro_v035.log"


ROWS = [
    ["string2 0", "string 1", "string 2", "string 3"],
    ["d010_010_010", "char_MIREI", "Я ждала тебя.", ""],
    [
        "d010_010_020",
        "char_MIREI",
        "Я обнаружила довольно странное пространство.\nАномальный мир, отрезанный от нормального пространства-времени.",
        "",
    ],
    [
        "d010_010_030",
        "char_MIREI",
        "Этот театр тоже необычное измерение между временем\nи пространством... но администраторы держат его под контролем.",
        "",
    ],
    [
        "d010_010_040",
        "char_MIREI",
        "Если оставить всё как есть, это может повлиять на весь мир.\nПоэтому я хочу, чтобы ты исследовал эту аномалию.",
        "",
    ],
    [
        "d010_010_050",
        "char_MIREI",
        "Нельзя допустить, чтобы другие люди вмешивались\nв аномальное пространство-время: последствия могут быть серьёзными...",
        "",
    ],
    [
        "d010_010_060",
        "char_MIREI",
        "...поэтому я попросила именно тебя. Если готов взяться за это задание,\nвоспользуйся здешним лифтом.",
        "",
    ],
    [
        "d010_010_070",
        "char_MIREI",
        "Я обнаружила ещё одно аномальное пространство.\nПохоже, появился новый Акашический бэкдор.",
        "",
    ],
    ["d010_010_080", "char_MIREI", "Я хочу, чтобы ты снова всё проверил.", ""],
    [
        "d010_010_090",
        "char_MIREI",
        "Если готов взяться за это задание,\nвоспользуйся здешним лифтом.",
        "",
    ],
]


def main() -> None:
    path = CSV_ROOT / RELATIVE
    path.parent.mkdir(parents=True, exist_ok=True)

    old = path.read_text(encoding="utf-8-sig") if path.exists() else ""
    with path.open("w", encoding="utf-8", newline="") as f:
        csv.writer(f, lineterminator="\r\n").writerows(ROWS)

    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    status = "updated" if old else "created"
    LOG_PATH.write_text(f"{RELATIVE}: {status}\n", encoding="utf-8")
    print(f"{status.capitalize()} {RELATIVE}. Log: {LOG_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()

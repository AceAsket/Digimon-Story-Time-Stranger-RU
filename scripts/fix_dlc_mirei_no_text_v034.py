from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CSV_ROOT = ROOT / "csv"
LOG_PATH = ROOT / "logs" / "fix_dlc_mirei_no_text_v034.log"


TARGETS: dict[tuple[str, str], str] = {
    ("patch_text01/message/dlc000.mbe/000_Sheet1.csv", "dlc000_100_010"):
        "...Просыпайся.",
    ("patch_text01/message/dlc000.mbe/000_Sheet1.csv", "dlc000_100_020"):
        "Когда будешь готов, начни расследование заново.\nЯ верю в тебя.",
    ("patch_text01/message/dlc000.mbe/000_Sheet1.csv", "dlc000_100_030"):
        "...",
    ("patch_text01/message/dlc000.mbe/000_Sheet1.csv", "dlc000_100_040"):
        "...",
    ("app_text01/message/dlc000.mbe/000_Sheet1.csv", "dlc000_100_010"):
        "...Просыпайся.",
    ("app_text01/message/dlc000.mbe/000_Sheet1.csv", "dlc000_100_020"):
        "Когда будешь готов, начни расследование заново.\nЯ верю в тебя.",
    ("app_text01/message/dlc000.mbe/000_Sheet1.csv", "dlc000_100_030"):
        "...",
    ("app_text01/message/dlc000.mbe/000_Sheet1.csv", "dlc000_100_040"):
        "...",
    ("addcont_01_text01/message/dlcep001_field.mbe/000_Sheet1.csv", "dlc001_0000_0010"):
        "...Просыпайся.",
    ("addcont_01_text01/message/dlcep001_field.mbe/000_Sheet1.csv", "dlc001_0000_0030"):
        "...",
    ("addcont_01_text01/message/dlcep001_field.mbe/000_Sheet1.csv", "dlc001_0000_0040"):
        "...",
    ("addcont_02_text01/message/dlcep002_field.mbe/000_Sheet1.csv", "dlc002_0000_0010"):
        "...Просыпайся.",
    ("addcont_03_text01/message/dlcep003_field.mbe/000_Sheet1.csv", "dlc003_0000_0010"):
        "...Просыпайся.",
    ("addcont_03_text01/message/dlcep003_field.mbe/000_Sheet1.csv", "dlc003_0000_0030"):
        "...",
    ("addcont_03_text01/message/dlcep003_field.mbe/000_Sheet1.csv", "dlc003_0000_0040"):
        "...",
}


def read_rows(path: Path) -> list[list[str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.reader(f))


def write_rows(path: Path, rows: list[list[str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        csv.writer(f, lineterminator="\r\n").writerows(rows)


def apply_target(relative: str, key: str, text: str, log: list[str]) -> None:
    path = CSV_ROOT / relative
    if not path.exists():
        log.append(f"{relative}:{key}: missing file")
        return

    rows = read_rows(path)
    changed = False
    found = False
    for row in rows[1:]:
        if len(row) < 3 or row[0] != key:
            continue
        found = True
        if row[2] == text:
            continue
        old = row[2]
        row[2] = text
        changed = True
        log.append(f"{relative}:{key}: {old!r} -> {text!r}")

    if not found:
        log.append(f"{relative}:{key}: missing row")
    if changed:
        write_rows(path, rows)


def main() -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    log: list[str] = []
    for (relative, key), text in TARGETS.items():
        apply_target(relative, key, text, log)
    LOG_PATH.write_text("\n".join(log) + ("\n" if log else ""), encoding="utf-8")
    print(f"Applied {len(log)} changes. Log: {LOG_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()

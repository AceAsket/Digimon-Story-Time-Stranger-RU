#!/usr/bin/env python3
"""Fix source-checked Digitter lines reported as overflowing in the log."""

from __future__ import annotations

import csv
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "csv/patch_text01/text/digitter_message.mbe/000_Sheet1.csv"
MAX_VISIBLE_LINE = 65
TAG_RE = re.compile(r"\{[^}]+\}")


UPDATES: dict[str, tuple[str, str]] = {
    "main_020_070_030": (
        "При прогрессивном усилении в конечном итоге упреждающая атака\n"
        "твоей Дигиатаки {r2} иногда будет достаточной, чтобы закончить\n"
        "битву до её начала.",
        "Постепенно усиливая Дигиатаку {r2}, ты сможешь порой завершать\n"
        "бой упреждающим ударом — ещё до его начала.",
    ),
    "main_020_070_031": (
        "Это поможет тебе выполнять миссии более эффективно, так что\n"
        "надеюсь, ты будешь этим пользоваться.",
        "Так ты сможешь быстрее выполнять задания.\n"
        "Надеюсь, это преимущество тебе пригодится.",
    ),
}


def visible_length(line: str) -> int:
    return len(TAG_RE.sub("", line))


def main() -> None:
    with PATH.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.reader(handle))

    row_by_key = {row[0]: row for row in rows if row}
    changed = 0
    current = 0
    for key, (old, new) in UPDATES.items():
        row = row_by_key.get(key)
        if row is None or len(row) < 2:
            raise SystemExit(f"Missing or malformed row {key!r} in {PATH}")
        if row[1] == new:
            current += 1
        elif row[1] == old:
            row[1] = new
            changed += 1
        else:
            raise SystemExit(
                f"Unexpected text for {key!r}:\nexpected: {old!r}\nactual:   {row[1]!r}"
            )

        for line in new.splitlines():
            length = visible_length(line)
            if length > MAX_VISIBLE_LINE:
                raise SystemExit(f"Line for {key!r} is too long ({length}): {line!r}")

    if changed:
        with PATH.open("w", encoding="utf-8-sig", newline="") as handle:
            csv.writer(handle, lineterminator="\n").writerows(rows)

    longest = max(visible_length(line) for _, new in UPDATES.values() for line in new.splitlines())
    print(f"Targets: {len(UPDATES)}")
    print(f"Changed: {changed}")
    print(f"Already current: {current}")
    print(f"Longest visible replacement line: {longest}")


if __name__ == "__main__":
    main()

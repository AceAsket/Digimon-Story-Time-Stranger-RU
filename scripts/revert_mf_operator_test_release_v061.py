from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CSV_ROOT = ROOT / "csv"
LOG_PATH = ROOT / "logs" / "revert_mf_operator_test_release_v061.log"

NAME_RESTORE = {
    "char_PLAYER_M": "{player}",
    "char_PLAYER_F": "{player}",
    "char_OPERATOR_M": "Оператор",
    "char_OPERATOR_F": "Оператор",
    "char_OPERATOR": "Оператор",
}


def read_rows(path: Path) -> list[list[str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.reader(f))


def write_rows(path: Path, rows: list[list[str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        csv.writer(f, lineterminator="\n").writerows(rows)


def alias_base(row_id: str) -> tuple[str, str] | None:
    if row_id.endswith("_M"):
        return row_id[:-2], "M"
    if row_id.endswith("_F"):
        return row_id[:-2], "F"
    return None


def update_char_names(root_name: str) -> list[str]:
    path = CSV_ROOT / root_name / "text" / "char_name.mbe" / "000_Sheet1.csv"
    if not path.exists():
        return []

    rows = read_rows(path)
    changed: list[str] = []
    for row in rows[1:]:
        if len(row) < 2:
            continue
        restored = NAME_RESTORE.get(row[0])
        if restored is not None and row[1] != restored:
            row[1] = restored
            changed.append(f"{root_name}/text/char_name:{row[0]}")

    if changed:
        write_rows(path, rows)
    return changed


def is_test_alias_row(row: list[str]) -> tuple[str, str] | None:
    if len(row) < 4:
        return None
    parsed = alias_base(row[0])
    if parsed is None:
        return None
    base, suffix = parsed
    if suffix == "M" and row[1] == "char_OPERATOR_F" and row[3] == row[0]:
        return base, suffix
    if suffix == "F" and row[1] == "char_OPERATOR_M" and row[3] == row[0]:
        return base, suffix
    return None


def revert_operator_split(root_name: str) -> list[str]:
    message_root = CSV_ROOT / root_name / "message"
    if not message_root.exists():
        return []

    changed: list[str] = []
    for path in sorted(message_root.rglob("000_Sheet1.csv")):
        rows = read_rows(path)
        if not rows:
            continue

        alias_pairs: dict[str, dict[str, str]] = {}
        kept_rows: list[list[str]] = [rows[0]]
        removed_count = 0

        for row in rows[1:]:
            parsed = is_test_alias_row(row)
            if parsed is None:
                kept_rows.append(row)
                continue

            base, suffix = parsed
            alias_pairs.setdefault(base, {})[suffix] = row[0]
            removed_count += 1

        if not removed_count:
            continue

        file_changed = True
        for row in kept_rows[1:]:
            if len(row) < 4:
                continue
            pair = alias_pairs.get(row[0])
            if not pair or "M" not in pair or "F" not in pair:
                continue
            restored_voice = f"{pair['M']} {pair['F']}"
            if row[1] != "char_OPERATOR_M" or row[3] != restored_voice:
                row[1] = "char_OPERATOR_M"
                row[3] = restored_voice

        write_rows(path, kept_rows)
        changed.append(
            f"{root_name}/{path.relative_to(CSV_ROOT / root_name).as_posix()}: removed {removed_count}"
        )

    return changed


def main() -> None:
    changed: list[str] = []
    for root_name in ("app_text01", "patch_text01"):
        changed.extend(update_char_names(root_name))
        changed.extend(revert_operator_split(root_name))

    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    LOG_PATH.write_text("Updated files:\n" + "\n".join(changed) + "\n", encoding="utf-8")
    print(f"Updated files: {len(changed)}")
    for item in changed:
        print(item)


if __name__ == "__main__":
    main()

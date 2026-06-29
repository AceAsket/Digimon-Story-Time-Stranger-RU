from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CSV_ROOT = ROOT / "csv"
LOG_PATH = ROOT / "logs" / "apply_mf_operator_test_release_v060.log"


OPERATOR_BASE = "OP BASE"
OPERATOR_M = "OP M"
OPERATOR_F = "OP F"
PLAYER_M = "{player} PM"
PLAYER_F = "{player} PF"


def read_rows(path: Path) -> list[list[str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.reader(f))


def write_rows(path: Path, rows: list[list[str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        csv.writer(f, lineterminator="\n").writerows(rows)


def alias_pair(tags: str) -> tuple[str, str] | None:
    tokens = tags.split()
    m_tokens = [token for token in tokens if token.endswith("_M")]
    f_tokens = [token for token in tokens if token.endswith("_F")]
    if len(m_tokens) == 1 and len(f_tokens) == 1:
        return m_tokens[0], f_tokens[0]
    return None


def update_char_names(root_name: str) -> list[str]:
    path = CSV_ROOT / root_name / "text" / "char_name.mbe" / "000_Sheet1.csv"
    if not path.exists():
        return []

    rows = read_rows(path)
    updates = {
        "char_PLAYER_M": PLAYER_M,
        "char_PLAYER_F": PLAYER_F,
        "char_OPERATOR_M": OPERATOR_M,
        "char_OPERATOR_F": OPERATOR_F,
        "char_OPERATOR": OPERATOR_BASE,
    }

    changed: list[str] = []
    for row in rows[1:]:
        if len(row) < 2:
            continue
        new_value = updates.get(row[0])
        if new_value is None or row[1] == new_value:
            continue
        row[1] = new_value
        changed.append(f"{root_name}/text/char_name:{row[0]}")

    if changed:
        write_rows(path, rows)
    return changed


def apply_operator_split(root_name: str) -> list[str]:
    message_root = CSV_ROOT / root_name / "message"
    if not message_root.exists():
        return []

    changed: list[str] = []
    for path in sorted(message_root.rglob("000_Sheet1.csv")):
        rows = read_rows(path)
        if not rows:
            continue

        existing_ids = {row[0] for row in rows[1:] if row}
        out_rows = [rows[0]]
        file_changed = False

        for row in rows[1:]:
            if len(row) < 4:
                out_rows.append(row)
                continue

            pair = alias_pair(row[3])
            is_operator_pair = row[1] in {"char_OPERATOR_M", "char_OPERATOR"} and pair is not None
            if not is_operator_pair:
                out_rows.append(row)
                continue

            alias_m, alias_f = pair
            base_row = list(row)
            if base_row[1] != "char_OPERATOR" or base_row[3] != "":
                base_row[1] = "char_OPERATOR"
                base_row[3] = ""
                file_changed = True

            out_rows.append(base_row)

            m_row = [alias_m, "char_OPERATOR_F", row[2], alias_m]
            f_row = [alias_f, "char_OPERATOR_M", row[2], alias_f]

            if alias_m not in existing_ids:
                out_rows.append(m_row)
                existing_ids.add(alias_m)
                file_changed = True
                changed.append(f"{root_name}/{path.relative_to(CSV_ROOT / root_name).as_posix()}:{row[0]}->{alias_m}")
            if alias_f not in existing_ids:
                out_rows.append(f_row)
                existing_ids.add(alias_f)
                file_changed = True
                changed.append(f"{root_name}/{path.relative_to(CSV_ROOT / root_name).as_posix()}:{row[0]}->{alias_f}")

        if file_changed:
            write_rows(path, out_rows)

    return changed


def main() -> None:
    changed: list[str] = []
    for root_name in ("app_text01", "patch_text01"):
        changed.extend(update_char_names(root_name))
        changed.extend(apply_operator_split(root_name))

    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    LOG_PATH.write_text("Updated rows:\n" + "\n".join(changed) + "\n", encoding="utf-8")
    print(f"Updated rows: {len(changed)}")
    for item in changed:
        print(item)


if __name__ == "__main__":
    main()

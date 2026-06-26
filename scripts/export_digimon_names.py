from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PATCH_NAMES = ROOT / "csv" / "patch_text01" / "text" / "char_name.mbe" / "000_Sheet1.csv"
APP_NAMES = ROOT / "csv" / "app_text01" / "text" / "char_name.mbe" / "000_Sheet1.csv"
OUT_DIR = ROOT / "exports"


NON_DIGIMON_BATTLE_ROWS = {
    "char_POWER_LOADER",
    "char_PUBLICSAFETY_BATTLE",
}


def read_names(path: Path) -> list[tuple[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.reader(f))
    result: list[tuple[str, str]] = []
    for row in rows[1:]:
        if len(row) >= 2:
            result.append((row[0].strip(), row[1].strip()))
    return result


def main() -> None:
    patch_rows = read_names(PATCH_NAMES)
    app_rows = dict(read_names(APP_NAMES))

    digimon_rows: list[tuple[int, str, str, str]] = []
    for index, (row_id, ru_name) in enumerate(patch_rows, start=1):
        if row_id == "char_PLAYER_M":
            break
        if row_id in NON_DIGIMON_BATTLE_ROWS:
            continue
        digimon_rows.append((len(digimon_rows) + 1, row_id, app_rows.get(row_id, ""), ru_name))

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    csv_path = OUT_DIR / "digimon_names.csv"
    with csv_path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["#", "id", "english_name", "russian_name"])
        writer.writerows(digimon_rows)

    tsv_path = OUT_DIR / "digimon_names.tsv"
    with tsv_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, delimiter="\t", lineterminator="\n")
        writer.writerow(["#", "id", "english_name", "russian_name"])
        writer.writerows(digimon_rows)

    unique_ru_path = OUT_DIR / "digimon_names_ru_unique.txt"
    seen: set[str] = set()
    unique_ru: list[str] = []
    for _, _, _, ru_name in digimon_rows:
        if ru_name and ru_name not in seen:
            seen.add(ru_name)
            unique_ru.append(ru_name)
    unique_ru_path.write_text("\n".join(unique_ru) + "\n", encoding="utf-8")

    print(f"rows={len(digimon_rows)} unique_ru={len(unique_ru)}")
    print(csv_path)
    print(tsv_path)
    print(unique_ru_path)


if __name__ == "__main__":
    main()

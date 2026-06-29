from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CSV_ROOT = ROOT / "csv"
LOG_PATH = ROOT / "logs" / "repair_mojibake_tail_pass_v059.log"


def unpack_text(text: str) -> str:
    bs = bytearray()
    for ch in text:
        try:
            bs.extend(ch.encode("cp1251"))
        except UnicodeEncodeError:
            code = ord(ch)
            if code < 256:
                bs.append(code)
            else:
                return text
    try:
        return bs.decode("utf-8")
    except UnicodeDecodeError:
        return text


def cyrillic_score(text: str) -> int:
    return sum(1 for ch in text if "\u0400" <= ch <= "\u04ff")


def mojibake_score(text: str) -> int:
    suspicious = {
        "\u0402",
        "\u0403",
        "\u0405",
        "\u0406",
        "\u0408",
        "\u0409",
        "\u040a",
        "\u040b",
        "\u040e",
        "\u0452",
        "\u0453",
        "\u0455",
        "\u0456",
        "\u0458",
        "\u0459",
        "\u045a",
        "\u045b",
        "\u045e",
        "\u00a0",
        "\u00a1",
        "\u00a2",
        "\u00a3",
        "\u00a4",
        "\u00a5",
        "\u00a6",
        "\u00a7",
        "\u00a8",
        "\u00a9",
        "\u00ab",
        "\u00ac",
        "\u00ad",
        "\u00ae",
        "\u00af",
        "\u00b0",
        "\u00b1",
        "\u00b2",
        "\u00b3",
        "\u00b4",
        "\u00b5",
        "\u00b6",
        "\u00b7",
        "\u00b8",
        "\u00b9",
        "\u00bb",
        "\u00bc",
        "\u00bd",
        "\u00be",
        "\u00bf",
        "\u201a",
        "\u201e",
        "\u2020",
        "\u2021",
        "\u20ac",
    }
    return sum(1 for ch in text if ch in suspicious)


def should_repair(old: str, new: str) -> bool:
    if old == new:
        return False
    if cyrillic_score(new) < 3:
        return False
    return mojibake_score(new) < mojibake_score(old)


def repair_csv(path: Path) -> list[str]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        rows = list(csv.reader(f))

    changed: list[str] = []
    for row_index, row in enumerate(rows[1:], start=2):
        row_id = row[0] if row else f"line{row_index}"
        for col_index, value in enumerate(row):
            repaired = unpack_text(value)
            if not should_repair(value, repaired):
                continue
            row[col_index] = repaired
            changed.append(f"{path.relative_to(ROOT).as_posix()}:{row_id}:col{col_index}")

    if changed:
        with path.open("w", encoding="utf-8", newline="") as f:
            csv.writer(f, lineterminator="\n").writerows(rows)

    return changed


def main() -> None:
    changed: list[str] = []
    for root_name in ("app_text01", "patch_text01"):
        root = CSV_ROOT / root_name
        for path in sorted(root.rglob("000_Sheet1.csv")):
            changed.extend(repair_csv(path))

    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    LOG_PATH.write_text("Updated fields:\n" + "\n".join(changed) + "\n", encoding="utf-8")
    print(f"Updated fields: {len(changed)}")
    for item in changed:
        print(item)


if __name__ == "__main__":
    main()

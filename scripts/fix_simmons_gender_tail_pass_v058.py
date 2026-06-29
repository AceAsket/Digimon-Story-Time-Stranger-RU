from __future__ import annotations

import csv
import io
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CSV_ROOT = ROOT / "csv"
LOG_PATH = ROOT / "logs" / "fix_simmons_gender_tail_pass_v058.log"


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


def pack_text(text: str) -> str:
    chars: list[str] = []
    for byte in text.encode("utf-8"):
        try:
            chars.append(bytes([byte]).decode("cp1251"))
        except UnicodeDecodeError:
            chars.append(chr(byte))
    return "".join(chars)


def csv_field(value: str) -> str:
    out = io.StringIO()
    csv.writer(out, lineterminator="").writerow([value])
    return out.getvalue()


UPDATES = {
    "message/m390.mbe/000_Sheet1.csv": {
        "m390_100_080": "Что? Ты уже на месте? Быстро же ты добираешься.\nДругого я и не ожидала от агента.",
    },
    "message/m420.mbe/000_Sheet1.csv": {
        "m420_010_070": "О чём ты говоришь? Если это какая-то шутка, то я её не поняла.",
        "m420_010_130": "Эта серия так много для меня значит. Именно из-за неё я вообще\nстала учёной.",
    },
}


def apply_updates(root_name: str) -> list[str]:
    changed: list[str] = []
    for relative_path, row_updates in UPDATES.items():
        path = CSV_ROOT / root_name / relative_path
        if not path.exists():
            continue
        raw = path.read_bytes()
        has_bom = raw.startswith(b"\xef\xbb\xbf")
        text = raw[3:].decode("utf-8") if has_bom else raw.decode("utf-8")
        original_text = text
        reader = csv.DictReader(io.StringIO(text))
        for row in reader:
            row_id = unpack_text(row.get("string2 0", ""))
            new_value = row_updates.get(row_id)
            if new_value is None:
                continue
            old_value = row["string 2"]
            if unpack_text(old_value) == new_value:
                continue
            text = text.replace(csv_field(old_value), csv_field(pack_text(new_value)), 1)
            changed.append(f"{root_name}/{relative_path}:{row_id}")
        if text != original_text:
            output = text.encode("utf-8")
            if has_bom:
                output = b"\xef\xbb\xbf" + output
            path.write_bytes(output)
    return changed


def main() -> None:
    changed: list[str] = []
    for root_name in ("app_text01", "patch_text01"):
        changed.extend(apply_updates(root_name))
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    LOG_PATH.write_text("Updated rows:\n" + "\n".join(changed) + "\n", encoding="utf-8")
    print(f"Updated rows: {len(changed)}")
    for item in changed:
        print(item)


if __name__ == "__main__":
    main()

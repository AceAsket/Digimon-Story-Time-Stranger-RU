from __future__ import annotations

import csv
import io
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CSV_ROOT = ROOT / "csv"
LOG_PATH = ROOT / "logs" / "fix_gender_tail_pass_v054.log"


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
    "message/s070_057.mbe/000_Sheet1.csv": {
        "s070_057_070": [("что должен\r\nвстретиться", "что должна\r\nвстретиться")],
    },
    "message/s910_169.mbe/000_Sheet1.csv": {
        "s910_169_530": [("со\r\nмной все будет", "со\r\nмной всё будет")],
        "s910_169_560": [("Я должен\r\nвернуться", "Я должна\r\nвернуться")],
    },
}


def apply_updates(root_name: str) -> int:
    changed = 0
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
            replacements = row_updates.get(row_id)
            if not replacements:
                continue
            old_value = row["string 2"]
            decoded = unpack_text(old_value)
            updated = decoded
            for old, new in replacements:
                updated = updated.replace(old, new, 1)
            if updated == decoded:
                continue
            text = text.replace(csv_field(old_value), csv_field(pack_text(updated)), 1)
            changed += 1
        if text != original_text:
            output = text.encode("utf-8")
            if has_bom:
                output = b"\xef\xbb\xbf" + output
            path.write_bytes(output)
    return changed


def main() -> None:
    total = sum(apply_updates(root_name) for root_name in ("app_text01", "patch_text01"))
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    LOG_PATH.write_text(f"Updated rows: {total}\n", encoding="utf-8")
    print(f"Updated rows: {total}")


if __name__ == "__main__":
    main()

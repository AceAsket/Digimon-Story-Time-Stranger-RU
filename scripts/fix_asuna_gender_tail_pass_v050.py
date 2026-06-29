from __future__ import annotations

import csv
import io
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CSV_ROOT = ROOT / "csv"
LOG_PATH = ROOT / "logs" / "fix_asuna_gender_tail_pass_v050.log"


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


def apply_updates(root_name: str) -> int:
    path = CSV_ROOT / root_name / "message/d11.mbe/000_Sheet1.csv"
    if not path.exists():
        return 0
    raw = path.read_bytes()
    has_bom = raw.startswith(b"\xef\xbb\xbf")
    text = raw[3:].decode("utf-8") if has_bom else raw.decode("utf-8")
    original_text = text
    changed = 0

    reader = csv.DictReader(io.StringIO(text))
    for row in reader:
        row_id = unpack_text(row.get("string2 0", ""))
        if row_id not in {"f_d1101_0150_0022", "f_d1101_0150_0030"}:
            continue
        old_value = row["string 2"]
        decoded = unpack_text(old_value)
        updated = decoded.replace("я немного растерялся", "я немного растерялась", 1)
        updated = updated.replace("но хотел поблагодарить", "но хотела поблагодарить", 1)
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

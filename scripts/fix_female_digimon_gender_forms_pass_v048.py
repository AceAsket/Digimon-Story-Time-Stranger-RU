from __future__ import annotations

import csv
import io
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CSV_ROOT = ROOT / "csv"
LOG_PATH = ROOT / "logs" / "fix_female_digimon_gender_forms_pass_v048.log"


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


UPDATES: dict[str, dict[str, list[tuple[str, str]]]] = {
    "message/d06.mbe/000_Sheet1.csv": {
        "f_d0604_0100_0070": [("Понял!", "Поняла!")],
        "f_d0604_0300_0040": [
            ("Я был замаскирован", "Я была замаскирована"),
            ("все слышал", "все слышала"),
        ],
    },
    "message/d09.mbe/000_Sheet1.csv": {
        "f_d0906_0060_0170": [("Я рад это слышать", "Я рада это слышать")],
        "f_d0907_0040_0010": [
            ("Я был обманут", "Я была обманута"),
            ("Я\r\nбыл частью", "Я\r\nбыла частью"),
        ],
    },
    "message/d12.mbe/000_Sheet1.csv": {
        "f_d1204_0120_0030": [("Я изо всех сил пытался", "Я изо всех сил пыталась")],
    },
    "message/digimon_chat.mbe/000_Sheet1.csv": {
        "belsta_001_2_reaction_char_BEELSTARMON": [("Я никогда об этом не думал", "Я никогда об этом не думала")],
        "lilis_001_2_reaction_char_LILITHMON": [("Я не уверен", "Я не уверена")],
    },
    "message/m160.mbe/000_Sheet1.csv": {
        "m160_040_010": [("Рад встрече", "Рада встрече")],
    },
    "message/s070_167.mbe/000_Sheet1.csv": {
        "s070_167_240": [
            ("Я знал", "Я знала"),
            ("что был прав", "что была права"),
        ],
        "s070_167_490": [("Я не уверен", "Я не уверена")],
    },
    "message/s110_108.mbe/000_Sheet1.csv": {
        "s110_108_450": [("Я хотел бы посмотреть", "Я хотела бы посмотреть")],
        "s110_108_720": [
            ("Я согласен с вами", "Я согласна с вами"),
            ("чем я думал", "чем я думала"),
        ],
        "s110_108_840": [("Я уверен, что", "Я уверена, что")],
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
                if old not in updated:
                    print(f"missing fragment: {root_name}/{relative_path}:{row_id}: {old!r}")
                    continue
                updated = updated.replace(old, new, 1)
            if updated == decoded:
                continue

            new_value = pack_text(updated)
            old_field = csv_field(old_value)
            new_field = csv_field(new_value)
            if old_field not in text:
                print(f"missing field: {root_name}/{relative_path}:{row_id}")
                continue
            text = text.replace(old_field, new_field, 1)
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

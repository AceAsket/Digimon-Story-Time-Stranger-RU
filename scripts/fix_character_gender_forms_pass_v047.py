from __future__ import annotations

import csv
import io
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CSV_ROOT = ROOT / "csv"
LOG_PATH = ROOT / "logs" / "fix_character_gender_forms_pass_v047.log"


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
    "message/d11.mbe/000_Sheet1.csv": {
        "f_d1101_0150_0050": [("Я заметил,", "Я заметила,")],
    },
    "message/d12.mbe/000_Sheet1.csv": {
        "f_d1206_0040_0140": [("Я все время смотрел", "Я все время смотрела")],
    },
    "message/m040.mbe/000_Sheet1.csv": {
        "m040_100_060": [("Я нашел его", "Я нашла его")],
    },
    "message/m100.mbe/000_Sheet1.csv": {
        "m100_090_060": [("Я не смогла", "Я не смог")],
    },
    "message/m130.mbe/000_Sheet1.csv": {
        "m130_100_190": [("Я хотела бы", "Я хотел бы")],
    },
    "message/m170.mbe/000_Sheet1.csv": {
        "m170_020_020": [("Я бы не стал слишком беспокоиться", "Я бы не стала слишком беспокоиться")],
    },
    "message/s110_103.mbe/000_Sheet1.csv": {
        "s110_103_120": [
            ("Ни за что. Я бы смог сказать", "Да ладно. Я бы заметила"),
        ],
        "s110_103_450": [("Я все видел!", "Я все видела!")],
    },
    "message/s200_149.mbe/000_Sheet1.csv": {
        "s200_149_180": [("Я не хотел этого говорить", "Я не хотела этого говорить")],
        "s200_149_1020": [
            ("Я так и думал", "Я так и думала"),
            ("я думал о", "я думала о"),
        ],
    },
    "message/s910_169.mbe/000_Sheet1.csv": {
        "s910_169_088": [("Я бы хотел помочь", "Я бы хотела помочь")],
        "s910_169_870": [("Я понял, что просто", "Я поняла, что просто")],
        "s910_169_950": [("Я уверен, что", "Я уверена, что")],
        "s910_169_1090": [
            ("Я нашел это", "Я нашла это"),
            ("когда был в ловушке", "когда была в ловушке"),
            ("Уверен, ты", "Уверена, ты"),
        ],
    },
    "message/t03.mbe/000_Sheet1.csv": {
        "f_t0301_0010_0020": [("Понял. Мы", "Поняла. Мы")],
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
            row_id = row.get("string2 0", "")
            replacements = row_updates.get(unpack_text(row_id))
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

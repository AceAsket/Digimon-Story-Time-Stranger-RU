from __future__ import annotations

import csv
import io
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CSV_ROOT = ROOT / "csv"
LOG_PATH = ROOT / "logs" / "fix_broad_gender_forms_pass_v053.log"


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
    "message/battle.mbe/000_Sheet1.csv": {
        "2010157001": [("чем я думал", "чем я думала")],
    },
    "message/d02.mbe/000_Sheet1.csv": {
        "f_d0213_0040_0010": [("Я слышал", "Я слышала")],
        "f_d0213_0040_0020": [
            ("Я надеялся", "Я надеялась"),
            ("быть полезным", "быть полезной"),
        ],
    },
    "message/d03.mbe/000_Sheet1.csv": {
        "f_d0302_0240_0050": [
            ("я должен", "я должна"),
            ("во все это", "во всё это"),
        ],
    },
    "message/d06.mbe/000_Sheet1.csv": {
        "f_d0604_0160_0010": [("Я слышал", "Я слышала")],
        "f_d0604_0300_0070": [("Я также слышал", "Я также слышала")],
        "f_d0604_0410_0010": [("Я слышал", "Я слышала")],
    },
    "message/d09.mbe/000_Sheet1.csv": {
        "f_d0900_0020_0020": [
            ("Я подготовил", "Я подготовила"),
            ("я не уверен", "я не уверена"),
        ],
        "f_d0907_0040_0020": [
            ("должен ли я", "должна ли я"),
            ("испытал", "испытала"),
        ],
        "f_d0907_0060_0020": [("я уверен", "я уверена")],
    },
    "message/d12.mbe/000_Sheet1.csv": {
        "f_d1204_0120_0040": [("Если бы я получил", "Если бы я получила")],
        "f_d1204_0120_0100": [
            ("Я слышал", "Я слышала"),
            ("еще раз", "ещё раз"),
        ],
        "f_d1204_0660_0020": [("я слышал", "я слышала")],
        "f_d1204_0740_0020": [("я был Блэкгатомоном", "я была Блэкгатомоном")],
        "f_d1204_0750_0020": [("я был Блэкгатомоном", "я была Блэкгатомоном")],
    },
    "message/digimon_chat.mbe/000_Sheet1.csv": {
        "angew_001_1_reaction_char_ANGEWOMON": [("я должен помогать", "я должна помогать")],
        "belsta_001_1_reaction_char_BEELSTARMON": [("Я должен бороться", "Я должна бороться")],
    },
    "message/m050.mbe/000_Sheet1.csv": {
        "m050_040_070": [("Я не должна был", "Я не должен был")],
    },
    "message/m100.mbe/000_Sheet1.csv": {
        "m100_030_200": [("что я нашла здесь", "что я нашел здесь")],
        "m100_030_220": [("я готова", "я готов")],
        "m100_090_005": [("Я слышала", "Я слышал")],
        "m100_090_040": [("я должна", "я должен")],
    },
    "message/m170.mbe/000_Sheet1.csv": {
        "m170_020_180": [("я что-то сказал", "я что-то сказала")],
        "m170_110_050": [("Я просто подумал", "Я просто подумала")],
    },
    "message/m235.mbe/000_Sheet1.csv": {
        "m235_040_110": [("я уверена", "я уверен")],
    },
    "message/m390.mbe/000_Sheet1.csv": {
        "m390_050_040": [("я бы сказал", "я бы сказала")],
    },
    "message/m420.mbe/000_Sheet1.csv": {
        "m420_010_070": [("я её не поняла", "я её не понял")],
    },
    "message/rumor_npc.mbe/000_Sheet1.csv": {
        "r_t0403_0010_0070": [("Я никогда такого не слышал", "Я никогда такого не слышала")],
    },
    "message/s010_003.mbe/000_Sheet1.csv": {
        "s010_003_060": [
            ("я и думал", "я и думала"),
            ("начнем", "начнём"),
        ],
        "s010_003_370": [("Я должен заснять", "Я должна заснять")],
        "s010_003_610": [
            ("как я думал", "как я думала"),
            ("я ошибался", "я ошибалась"),
        ],
    },
    "message/s010_156.mbe/000_Sheet1.csv": {
        "s010_156_030": [
            ("я связался", "я связалась"),
            ("я был так\nнапуган", "я была так\nнапугана"),
        ],
        "s010_156_280": [("я уже видел", "я уже видела")],
        "s010_156_350": [
            ("Я совсем забыл", "Я совсем забыла"),
            ("я видел это", "я видела это"),
        ],
        "s010_156_920": [("я уверен", "я уверена")],
    },
    "message/s010_180.mbe/000_Sheet1.csv": {
        "s010_180_150": [("я был полон решимости", "я была полна решимости")],
        "s010_180_470": [
            ("я никогда не видел", "я никогда не видела"),
            ("кто-то еще", "кто-то ещё"),
        ],
        "s010_180_510": [("я должен выразить", "я должна выразить")],
    },
    "message/s020_013.mbe/000_Sheet1.csv": {
        "s020_013_390": [("я должен подумать", "я должна подумать")],
    },
    "message/s040_160.mbe/000_Sheet1.csv": {
        "s040_160_140": [("Я слышал", "Я слышала")],
    },
    "message/s070_057.mbe/000_Sheet1.csv": {
        "s070_057_070": [("что должен\nвстретиться", "что должна\nвстретиться")],
        "s070_057_130": [
            ("Я проиграл!", "Я проиграла!"),
            ("Я должен стать", "Я должна стать"),
            ("быть готов к", "быть готова к"),
        ],
        "s070_057_140": [("Я должен запереть", "Я должна запереть")],
        "s070_057_180": [("я был так уверен", "я была так уверена")],
    },
    "message/s070_167.mbe/000_Sheet1.csv": {
        "s070_167_350": [("я бы не смог", "я бы не смогла")],
    },
    "message/s110_103.mbe/000_Sheet1.csv": {
        "s110_103_030": [("я только что получил", "я только что получила")],
        "s110_103_100": [("я тоже так думал", "я тоже так думала")],
    },
    "message/s200_147.mbe/000_Sheet1.csv": {
        "s200_147_060": [("я бы хотел услышать", "я бы хотела услышать")],
        "s200_147_500": [("Как я уже сказал", "Как я уже сказала")],
        "s200_147_590": [("я так рад", "я так рада")],
    },
    "message/s200_149.mbe/000_Sheet1.csv": {
        "s200_149_010": [("как я рад", "как я рада")],
        "s200_149_140": [
            ("я только что получил", "я только что получила"),
            ("еще одно", "ещё одно"),
        ],
        "s200_149_500": [
            ("как все зашло", "как всё зашло"),
            ("я почти уверен", "я почти уверена"),
        ],
    },
    "message/s910_169.mbe/000_Sheet1.csv": {
        "s910_169_320": [("я не смогла", "я не смог")],
        "s910_169_530": [
            ("Я должен прочитать", "Я должна прочитать"),
            ("со\nмной все будет", "со\nмной всё будет"),
        ],
        "s910_169_560": [("Я должен вернуться", "Я должна вернуться")],
        "s910_169_570": [
            ("Я должен дочитать еще", "Я должна дочитать ещё"),
        ],
        "s910_169_810": [
            ("ударился головой", "ударилась головой"),
            ("когда падал", "когда падала"),
        ],
        "s910_169_850": [("Я подумал", "Я подумала")],
        "s910_169_890": [
            ("я решил прочитать", "я решила прочитать"),
            ("книгу сам", "книгу сама"),
            ("я был уверен", "я была уверена"),
        ],
        "s910_169_910": [("Я не ожидал", "Я не ожидала")],
    },
    "message/s910_170.mbe/000_Sheet1.csv": {
        "s910_170_010": [("я хотел\nтебя познакомить", "я хотела\nтебя познакомить")],
        "s910_170_220": [("я смог подключиться", "я смогла подключиться")],
        "s910_170_430": [("я не уверен", "я не уверена")],
        "s910_170_530": [("я видел в\nфильмах", "я видела в\nфильмах")],
        "s910_170_1090": [("я должен быть честен", "я должна быть честна")],
    },
    "message/s910_171.mbe/000_Sheet1.csv": {
        "s910_171_080": [("я ничем не смог", "я ничем не смогла")],
    },
    "message/t01.mbe/000_Sheet1.csv": {
        "f_t0108_0110_0020": [
            ("должна сказать", "должен сказать"),
            ("я никогда не думала", "я никогда не думал"),
        ],
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

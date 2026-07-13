#!/usr/bin/env python3
"""Fix confirmed entity-name mismatches from scene audit rows 24-45."""

from __future__ import annotations

from pathlib import Path

from fix_reported_sidequests_v120 import digest, read_document, write_document


ROOT = Path(__file__).resolve().parents[1]
CSV_ROOT = ROOT / "csv"

# package, relative CSV, row id, text column, expected SHA-256, replacement
UPDATES: list[tuple[str, str, str, int, str, str]] = [
    (
        "patch_text01", "message/m310.mbe/000_Sheet1.csv", "m310_020_180", 2,
        "4b916a5c7a24ac0fb20b64e047c0dac5857ac553abe68ca07eff178c09f7f084",
        "Давай попробуем найти Маленького Медвежонка в Деревне Восстания.",
    ),
    (
        "patch_text01", "message/m310.mbe/000_Sheet1.csv", "m310_030_020", 2,
        "441d7e3a804180c0d28a74546ad0fb8735d8de22b2b3074ea0ca2768060787be",
        "Ты Бермон, верно?",
    ),
    (
        "patch_text01", "message/m310.mbe/000_Sheet1.csv", "m310_030_021", 2,
        "0f1a7e6cc5a71c603d1c29a2e60800afcdff69a10efc96f6adec510441d59107",
        "...Маленький Медвежонок из Центрального города — это ведь ты?{next}",
    ),
    (
        "patch_text01", "message/m310.mbe/000_Sheet1.csv", "m310_040_080", 2,
        "a3a220fde8c759239324ef681346ffeba2929828a85c655cfbed633b242f8a4a",
        "ГрапЛеомон сражался... с Каллисмоном?",
    ),
    (
        "patch_text01", "message/m410.mbe/000_Sheet1.csv", "m410_001_090", 2,
        "5602740cb4e688a4fcda2775b320cabe6759548c63c969ca52abf7dd542fb591",
        "Пампмон...!",
    ),
    (
        "patch_text01", "message/m430.mbe/000_Sheet1.csv", "m430_020_050", 2,
        "602ced902c926cea0a1c59c3b953225e2a3389dcf96063039da2fa2995710dfd",
        "Я Грейс Новамон!",
    ),
    (
        "patch_text01", "message/rumor_npc.mbe/000_Sheet1.csv", "r_d0302_0010_0070", 2,
        "9ebc9a1b31af6e0590a58f3af148f97f4449d43bee8bbdcc14d485917cad1117",
        "Маринангемон!",
    ),
    (
        "patch_text01", "message/rumor_npc.mbe/000_Sheet1.csv", "r_d0404_0020_0090", 2,
        "4ac6f060f3522689bb575daf36462a66acbd8b3249596617d38c5e90d8bed7c4",
        "И Роузмон тоже!",
    ),
    (
        "patch_text01", "message/s010_156.mbe/000_Sheet1.csv", "s010_156_661", 2,
        "200c0a6b77f1c20df88c58722300093b4e267cefb64e01640e746c4627a72cdc",
        "{next}Дюкмон.",
    ),
    (
        "patch_text01", "message/s010_156.mbe/000_Sheet1.csv", "s010_156_711", 2,
        "2499863425846921d522c87f7440b69fed4aa78cd5450c3a85e3134dde5e3f22",
        "{next}Лорд Найтмон.",
    ),
    (
        "patch_text01", "message/s010_156.mbe/000_Sheet1.csv", "s010_156_712", 2,
        "ed53ad45310fb94a98f33106a6b137e0f8adcec247010e7cf72b6ec52af9413d",
        "{next}Алфорс Ви-драмон.",
    ),
    (
        "patch_text01", "message/s010_156.mbe/000_Sheet1.csv", "s010_156_760", 2,
        "9a893757c6b5da7f9b01e40a0d8b7c563ca9e3a22021e1db334751edb355dff2",
        "{next}Краниуммон.",
    ),
    (
        "patch_text01", "message/s010_156.mbe/000_Sheet1.csv", "s010_156_761", 2,
        "22a987859a63c75b741c69d2a8605514e18536165786011b739695350fab0a91",
        "{next}Слейпмон.",
    ),
    (
        "patch_text01", "message/s010_156.mbe/000_Sheet1.csv", "s010_156_762", 2,
        "a8a8302adbba19c7587d4759fa5dd6a5b4843b6d7c5c7635df0b082f057746e5",
        "{next}Дуфтмон.",
    ),
    (
        "patch_text01", "message/s010_156.mbe/000_Sheet1.csv", "s010_156_810", 2,
        "3bba9fd98c3b18d66ac33746dadd6c71aa87f48b222d2d89d71204e8cb5b129a",
        "{next}Эксамон.",
    ),
    (
        "patch_text01", "message/s010_156.mbe/000_Sheet1.csv", "s010_156_811", 2,
        "be3945535ed0bfa51e9e01a871a5dd157b3301e81bf6035b13e5a41b3b9cd84f",
        "{next}Гэнкумон.",
    ),
    (
        "patch_text01", "message/s070_055.mbe/000_Sheet1.csv", "s070_055_301", 2,
        "e771591c697e149d28149c8b4a8a268e42dc012e29b0da352d08e6266640830c",
        "{next}Асуна Широки?",
    ),
    (
        "patch_text01", "message/s080_059.mbe/000_Sheet1.csv", "s080_059_091", 2,
        "3e8e1f0ed2876d5c2074701f345133f5df93a9294a27d334582f36325de5c6c0",
        "{next}Космическая область?",
    ),
    (
        "patch_text01", "message/s080_059.mbe/000_Sheet1.csv", "s080_059_380", 2,
        "34e3aad8109264fbed786c73db0f0be434d5578141c530bcc16dff5cec2fa3b2",
        "Для Жаркого Космоса нужен кулер, а для Холодного Космоса —\n"
        "обогреватель.",
    ),
    (
        "patch_text01", "message/s080_059.mbe/000_Sheet1.csv", "s080_059_391", 2,
        "4aec8187938708cbd1155cb84d167e0e9763b8fc83344129cef3984b6945f785",
        "Жаркий Космос?",
    ),
    (
        "patch_text01", "message/s080_059.mbe/000_Sheet1.csv", "s080_059_392", 2,
        "4b5274e2a1dde7809fe1a8d1dda9d3672532a1c6329a03e8d0e24f5a69bbc538",
        "Холодный Космос?",
    ),
    (
        "patch_text01", "message/s110_102.mbe/000_Sheet1.csv", "s110_102_600", 2,
        "72b5bbd841b6f8f3074155dcf70d7b9e01da52ddb61ae8643de41d26b115bcdd",
        "Я только что отдал синий хрондигизойтовый металл\n"
        "Алфорс Ви-драмону.",
    ),
    (
        "patch_text01", "message/s110_102.mbe/000_Sheet1.csv", "s110_102_610", 2,
        "a35ac6a0ea5f06f1f13b93aeac949a63d50b667d8dbc054422a272d6221616f0",
        "Я счастлив! ДжамбоГамемон полезен!",
    ),
    (
        "patch_text01", "message/s110_111.mbe/000_Sheet1.csv", "s110_111_331", 2,
        "006b95bd15c6c781a92f342f82eff40de7a5e32d873cc58ef68c8b7a5649c229",
        "{next}Король Драсил?",
    ),
    (
        "patch_text01", "message/t01.mbe/000_Sheet1.csv", "f_t0121_050_0030", 2,
        "c40900f83927285eb99a1209763b18c8a6d047c5ddc01a9675d88b90bbb1b22e",
        "Хм? Маленький Медвежонок?",
    ),
]


def main() -> None:
    documents: dict[tuple[str, str], list[list[str]]] = {}
    formats: dict[tuple[str, str], tuple[str, bool]] = {}
    dirty: set[tuple[str, str]] = set()
    changed = current = 0
    for package, relative, row_id, column, expected_hash, replacement in UPDATES:
        marker = (package, relative)
        path = CSV_ROOT / package / relative
        if marker not in documents:
            rows, encoding, quote_all = read_document(path)
            documents[marker] = rows
            formats[marker] = (encoding, quote_all)
        matches = [row for row in documents[marker] if row and row[0] == row_id]
        if len(matches) != 1 or len(matches[0]) <= column:
            raise SystemExit(f"Missing or ambiguous row {package}:{relative}:{row_id}")
        row = matches[0]
        if row[column] == replacement:
            current += 1
        elif digest(row[column]) == expected_hash:
            row[column] = replacement
            changed += 1
            dirty.add(marker)
        else:
            raise SystemExit(f"Unexpected text {package}:{relative}:{row_id}: {row[column]!r}")
    for marker in sorted(dirty):
        package, relative = marker
        encoding, quote_all = formats[marker]
        write_document(CSV_ROOT / package / relative, documents[marker], encoding, quote_all)
    print(f"Targets: {len(UPDATES)}")
    print(f"Changed: {changed}")
    print(f"Already current: {current}")
    print(f"Files written: {len(dirty)}")


if __name__ == "__main__":
    main()

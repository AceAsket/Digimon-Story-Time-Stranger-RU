#!/usr/bin/env python3
"""Unify Heat Cosmic and Chill Cosmic names across UI and dialogue tables."""

from __future__ import annotations

from pathlib import Path

from fix_reported_sidequests_v120 import digest, read_document, write_document


ROOT = Path(__file__).resolve().parents[1]
CSV_ROOT = ROOT / "csv"

UPDATES: list[tuple[str, str, str, int, str, str]] = [
    ("patch_text01", "text/bgm_name.mbe/000_Sheet1.csv", "922", 1,
     "75b274246267380f37a357a135290a4726101b4f5a9573b7415d8e07bba666d1", "Жаркий Космос"),
    ("patch_text01", "text/bgm_name.mbe/000_Sheet1.csv", "923", 1,
     "f59ca684951f532825ce92498a0d22acd1b400c2f9b66ae351af1b96c19332ca", "Холодный Космос"),
    ("patch_text01", "text/char_name.mbe/000_Sheet1.csv", "char_HEAT_COSMIC", 1,
     "75b274246267380f37a357a135290a4726101b4f5a9573b7415d8e07bba666d1", "Жаркий Космос"),
    ("patch_text01", "text/char_name.mbe/000_Sheet1.csv", "char_CHILL_COSMIC", 1,
     "f59ca684951f532825ce92498a0d22acd1b400c2f9b66ae351af1b96c19332ca", "Холодный Космос"),
]

AREA_NAMES = {
    "02": ("2613c26a64a908a47d93232004ad6ae88b8abc63bb21e680b9b520d226f3b862", "Жаркий Космос: зона красного пламени"),
    "03": ("51f6a44aad75a9453e72ff228194e3c063ffe981baf9893a3eebf0b19b533a8e", "Жаркий Космос: зона жёлтого пламени"),
    "04": ("c9e2a672263de80e400bfad1d9156c60f7fb8bc5fb8a985fb2a66cf633df2258", "Жаркий Космос: зона белого пламени"),
    "05": ("e158e17f5d2dacf1046211c6e59516246ac5c80415866d2e3c4c9deac8b8e2f7", "Жаркий Космос: тронный зал"),
    "06": ("583028281cafcf5f1bf3a504a8a5b9d9adcd36fdb1d650954088a46d3077727f", "Холодный Космос: зона новолуния"),
    "07": ("73cc4c6954a05131df6533fd1813506cc9f5a90354a00db732195c721bd9f906", "Холодный Космос: зона полумесяца"),
    "08": ("793bec0d351fd0257adf8f81dbe03514a7312b2efa1fbeebc5f44e56a57c7103", "Холодный Космос: зона полулуния"),
    "09": ("62ef3e32d1e8720935dc412155c5760ada7a2722b6cdd87c4bf3bbd512084f6d", "Холодный Космос: тронный зал"),
}

for suffix, (expected_hash, replacement) in AREA_NAMES.items():
    UPDATES.append((
        "patch_text01", "text/field_name.mbe/000_Sheet1.csv", f"201{suffix}", 1,
        expected_hash, replacement,
    ))
    world_hash = expected_hash
    if suffix == "08":
        # The world-map row incorrectly duplicated the crescent-moon label.
        world_hash = "73cc4c6954a05131df6533fd1813506cc9f5a90354a00db732195c721bd9f906"
    UPDATES.append((
        "patch_text01", "text/worldmap_place_name.mbe/000_Sheet1.csv", f"101{suffix}", 1,
        world_hash, replacement,
    ))


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

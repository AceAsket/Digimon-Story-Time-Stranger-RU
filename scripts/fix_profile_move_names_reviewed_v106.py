#!/usr/bin/env python3
"""Apply the manually reviewed low-confidence profile move-name matches."""

from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CSV_ROOT = ROOT / "csv"
SUGGESTIONS = ROOT / "exports/profile_move_replacement_suggestions_v097.csv"
MANIFEST = ROOT / "exports/profile_move_replacements_reviewed_v106.csv"
FIELDS = [
    "package", "file", "row_id", "source_move", "old", "new",
    "quoted", "expected_count", "note",
]

REVIEWED_SUGGESTION_KEYS = {
    ("patch_text01", "digimon_0148_profile", "Celestial Arrow"),
    ("patch_text01", "digimon_0383_profile", "Rust Breath"),
    ("patch_text01", "digimon_0218_profile", "Blue Flare Breath"),
    ("patch_text01", "digimon_0209_profile", "Green Flare Breath"),
    ("patch_text01", "digimon_0021_profile", "Tidal Wave"),
    ("patch_text01", "digimon_0137_profile", "Flame Dive"),
    ("patch_text01", "digimon_0170_profile", "Needle Hive"),
    ("patch_text01", "digimon_0361_profile", "Puppy Howl"),
    ("patch_text01", "digimon_0363_profile", "Fire Breath"),
    ("patch_text01", "digimon_0371_profile", "Icicle Rod"),
    ("patch_text01", "digimon_0725_profile", "Ultimate Blast"),
    ("patch_text01", "digimon_0012_profile", "Fox Fire"),
    ("patch_text01", "digimon_0082_profile", "Heat Wave"),
    ("patch_text01", "digimon_0739_profile", "Extinction Wave"),
    ("patch_text01", "digimon_0017_profile", "Darkside Quake"),
    ("patch_text01", "digimon_0128_profile", "Bee Cyclone"),
    ("patch_text01", "digimon_0208_profile", "Baby Breath"),
    ("patch_text01", "digimon_0348_profile", "Poison Ivy"),
    ("addcont_01_text01", "digimon_0691_profile", "Transcendent Cannon"),
    ("patch_text01", "digimon_0078_profile", "Exhaust Flame"),
    ("patch_text01", "digimon_0775_profile", "Chaos Flare"),
    ("patch_text01", "digimon_0402_profile", "Eradication Gears"),
    ("patch_text01", "digimon_0102_profile", "Gauntlet Claw"),
    ("patch_text01", "digimon_0168_profile", "Punish Judge"),
    ("patch_text01", "digimon_0451_profile", "Brain Rupture"),
    ("patch_text01", "digimon_0737_profile", "Trinity Arm"),
    ("patch_text01", "digimon_0601_profile", "Baluluna Gale"),
    ("patch_text01", "digimon_0758_profile", "Iceball Bomb"),
    ("patch_text01", "digimon_0706_profile", "Feather Slash"),
    ("patch_text01", "digimon_0742_profile", "Serpent Ruin"),
    ("patch_text01", "digimon_0607_profile", "Fungus Crusher"),
    ("patch_text01", "digimon_0767_profile", "Reversal of the Dead"),
    ("patch_text01", "digimon_0727_profile", "Nitro Stinger"),
    ("patch_text01", "digimon_0731_profile", "Bunny Blades"),
    ("addcont_01_text01", "digimon_0691_profile", "Supreme Sword"),
    ("patch_text01", "digimon_0725_profile", "Ultimate Quake"),
    ("patch_text01", "digimon_0754_profile", "Taizoukai Mandala"),
    ("patch_text01", "digimon_0775_profile", "Death Slinger"),
    ("patch_text01", "digimon_0770_profile", "Striver Cannon"),
    ("patch_text01", "digimon_0772_profile", "Dark Prominence"),
    ("patch_text01", "digimon_0729_profile", "Hyper Smell"),
    ("patch_text01", "digimon_0735_profile", "Lightning Spear"),
    ("patch_text01", "digimon_0774_profile", "Lightning Spear"),
    ("addcont_02_text01", "digimon_0485_profile", "Depth Charge Sky"),
}

EXTRA_REPLACEMENTS = [
    ("patch_text01", "text/digimon_profile.mbe/000_Sheet1.csv", "digimon_0740_profile",
     "Spiral Raven Claw", "Коготь Ворона-Спирали", "Спиральный Коготь Ворона", True,
     "corrected automatic alignment"),
    ("patch_text01", "text/digimon_profile.mbe/000_Sheet1.csv", "digimon_0745_profile",
     "Mach Stinger V", "Махающее Жало V", "Стингер Маха V", True,
     "corrected automatic alignment"),
    ("patch_text01", "text/digimon_profile.mbe/000_Sheet1.csv", "digimon_0181_profile",
     "Madness Merry-Go-Round DX", "Маднесс\nМерри-Го-Раунд DX", "Безумная карусель DX", True,
     "corrected automatic alignment"),
    ("patch_text01", "text/digimon_profile.mbe/000_Sheet1.csv", "digimon_0225_profile",
     "Vorpal Blade", "Ворпал\nБлейд", "Клинок Ворпала", True,
     "corrected automatic alignment"),
    ("patch_text01", "text/digimon_profile.mbe/000_Sheet1.csv", "digimon_0315_profile",
     "Strike of the Seven Stars", "Страйк оф зе Севен\nСтарз", "Удар семи звезд", True,
     "corrected automatic alignment"),
    ("patch_text01", "text/digimon_profile.mbe/000_Sheet1.csv", "digimon_0315_profile",
     "Testament", "Тестамент", "Завещание", True,
     "corrected automatic alignment"),
    ("patch_text01", "text/digimon_profile.mbe/000_Sheet1.csv", "digimon_0075_profile",
     "Vortex Penetration", "Вортекс\nПенетрайшн", "Пронзающий вихрь", True,
     "unambiguous quoted move"),
    ("patch_text01", "text/digimon_profile.mbe/000_Sheet1.csv", "digimon_0075_profile",
     "Wave of Depth", "Вейв оф\nДефс", "Волна глубины", True,
     "unambiguous quoted move"),
    ("addcont_03_text01", "text/digimon_profile_dlc03.mbe/000_Sheet1.csv", "digimon_0358_profile",
     "Lightning Joust", "Молниеносный\nтурнирный удар", "Молниеносный выпад", True,
     "DLC move-name consistency"),
    ("addcont_03_text01", "text/digimon_profile_dlc03.mbe/000_Sheet1.csv", "digimon_0358_profile",
     "Shield of the Just", "Финальный Элизион", "Щит праведника", True,
     "DLC move-name consistency"),
    ("addcont_03_text01", "text/digimon_profile_dlc03.mbe/000_Sheet1.csv", "digimon_0418_profile",
     "Victory Sword", "Ульфорс-саблю", "Меч победы", True,
     "DLC move-name consistency"),
    ("addcont_03_text01", "text/digimon_profile_dlc03.mbe/000_Sheet1.csv", "digimon_0418_profile",
     "Tensegrity Shield", "Tense-Great Shield", "Тенсегрити-щит", True,
     "localized English-only equipment name"),
    ("addcont_03_text01", "text/digimon_profile_dlc03.mbe/000_Sheet1.csv", "digimon_0418_profile",
     "The Ray of Victory", "Сияющая V-сила", "Луч победы", True,
     "DLC move-name consistency"),
    ("addcont_03_text01", "text/digimon_profile_dlc03.mbe/000_Sheet1.csv", "digimon_0468_profile",
     "Ultimate Seibaken", "Совершенный боевой клинок\nСэйбакен", "«Высший Сэйбакен»", False,
     "DLC move-name consistency"),
]


def read_rows(path: Path) -> list[list[str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.reader(handle))


def token(old: str, quoted: bool) -> str:
    return f"«{old}»" if quoted else old


def build_manifest() -> list[dict[str, str]]:
    with SUGGESTIONS.open("r", encoding="utf-8-sig", newline="") as handle:
        suggestions = list(csv.DictReader(handle))
    selected = {
        (row["package"], row["row_id"], row["source_move"]): row
        for row in suggestions
        if (row["package"], row["row_id"], row["source_move"]) in REVIEWED_SUGGESTION_KEYS
    }
    missing = REVIEWED_SUGGESTION_KEYS - set(selected)
    if missing:
        raise SystemExit(f"Reviewed suggestions missing: {sorted(missing)}")

    raw: list[tuple[str, str, str, str, str, str, bool, str]] = []
    for key in sorted(REVIEWED_SUGGESTION_KEYS):
        row = selected[key]
        raw.append(
            (
                row["package"], row["file"], row["row_id"], row["source_move"],
                row["current_fragment"], row["approved_ru"], True,
                "reviewed quoted-name match",
            )
        )
    raw.extend(EXTRA_REPLACEMENTS)

    cache: dict[tuple[str, str], dict[str, str]] = {}
    manifest: list[dict[str, str]] = []
    for package, relative, row_id, source_move, old, new, quoted, note in raw:
        key = (package, relative)
        if key not in cache:
            rows = read_rows(CSV_ROOT / package / relative)
            cache[key] = {row[0]: row[1] for row in rows if len(row) >= 2}
        current = cache[key].get(row_id)
        if current is None:
            raise SystemExit(f"Missing profile row: {package}:{relative}:{row_id}")
        old_token = token(old, quoted)
        count = current.count(old_token)
        if count < 1:
            raise SystemExit(
                f"Reviewed fragment not found: {package}:{relative}:{row_id}:{old_token!r}"
            )
        manifest.append(
            {
                "package": package,
                "file": relative,
                "row_id": row_id,
                "source_move": source_move,
                "old": old,
                "new": new,
                "quoted": "yes" if quoted else "no",
                "expected_count": str(count),
                "note": note,
            }
        )

    with MANIFEST.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(manifest)
    return manifest


def read_manifest() -> list[dict[str, str]]:
    if not MANIFEST.exists():
        return build_manifest()
    with MANIFEST.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def main() -> None:
    manifest = read_manifest()
    grouped: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in manifest:
        grouped[(row["package"], row["file"])].append(row)

    changed = 0
    already_current = 0
    for (package, relative), updates in sorted(grouped.items()):
        path = CSV_ROOT / package / relative
        rows = read_rows(path)
        by_id = {row[0]: row for row in rows if len(row) >= 2}
        file_changed = False
        for update in updates:
            row = by_id.get(update["row_id"])
            if row is None:
                raise SystemExit(f"Missing profile row: {package}:{relative}:{update['row_id']}")
            quoted = update["quoted"] == "yes"
            old_token = token(update["old"], quoted)
            new_token = token(update["new"], quoted)
            expected = int(update["expected_count"])
            old_count = row[1].count(old_token)
            if old_count == expected:
                row[1] = row[1].replace(old_token, new_token)
                changed += expected
                file_changed = True
            elif old_count == 0 and row[1].count(new_token) >= expected:
                already_current += expected
            else:
                raise SystemExit(
                    f"Ambiguous reviewed replacement {package}:{relative}:{update['row_id']}: "
                    f"{old_token!r} count={old_count}, expected={expected}"
                )
        if file_changed:
            with path.open("w", encoding="utf-8-sig", newline="") as handle:
                csv.writer(handle, lineterminator="\n").writerows(rows)

    print(f"Reviewed replacements: {len(manifest)}")
    print(f"Changed occurrences: {changed}")
    print(f"Already current occurrences: {already_current}")
    print(f"Manifest: {MANIFEST.relative_to(ROOT)}")


if __name__ == "__main__":
    main()

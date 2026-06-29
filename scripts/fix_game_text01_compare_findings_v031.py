from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CSV_ROOT = ROOT / "csv"
ORIGINAL_ROOT = ROOT / "analysis" / "game_text01_compare_v030" / "original_csv"

PATCH_MESSAGE_FILES = [
    "s030_183",
    "s040_032",
    "s040_033",
    "s070_055",
    "s110_100",
]

JOGRESS_ROWS = ["23943", "23944", "23945", "28050", "29268", "70010"]

VOICE_LANGUAGE_ROWS = {
    "19049": "Японский",
    "19050": "\u00A0",
}

YESNO_PATCH_ROWS = {
    "yesno_language_0040": (
        "Чтобы изменить язык отображения игры,\n"
        "вы вернётесь на титульный экран.\n"
        "Продолжить?\n\n"
        "{fc9Имена главного героя и дигимонов останутся на прежнем языке. "
        "Кроме того, из-за смены шрифта имена главного героя и дигимонов "
        "могут отображаться некорректно. (Их можно изменить позже.)}"
    ),
    "yesno_language_0050": (
        "Чтобы изменить язык отображения игры,\n"
        "вы вернётесь на титульный экран.\n"
        "Продолжить?\n\n"
        "{fc9Имена главного героя и дигимонов останутся на прежнем языке. "
        "(Их можно изменить позже.)}"
    ),
}

GRAPHICTEXT_ROWS = {
    "ui_textext_digivice_0010": "Боевой состав",
    "ui_textext_digivice_0020": "Резерв",
    "ui_textext_digivice_0030": "Дигимоны",
    "ui_textext_digivice_0040": "Предметы",
    "ui_textext_digivice_0050": "Агент",
    "ui_textext_digivice_0060": "Система",
    "ui_textext_digivice_0070": "Дигилайн",
    "ui_textext_digivice_0080": "Миссии",
    "ui_textext_battle_0010": "Защита",
    "ui_textext_battle_0020": "Навыки",
    "ui_textext_battle_0030": "Замена",
    "ui_textext_battle_0040": "Предметы",
    "ui_textext_battle_0050": "Кросс-арты",
    "ui_textext_battle_0070": "Эволюция",
    "ui_textext_battle_0100": "СОПР.",
    "ui_textext_battle_0110": "БЛОК",
    "ui_textext_battle_0120": "МИМО",
    "ui_textext_battle_0130": "ХОРОШО!",
    "ui_textext_battle_0140": "ОТЛИЧНО!!",
    "ui_textext_battle_0150": "ПРЕВОСХОДНО!!!",
    "ui_textext_battle_0160": "ПРОРЫВ",
    "ui_textext_battle_0170": "КО",
}

TEXT_ROW_FIXES = {
    ("app_text01", "text/skill_auto_explanation.mbe/000_Sheet1.csv"): {
        "95": "{fc9Смена режима:}",
    },
    ("patch_text01", "text/skill_auto_explanation.mbe/000_Sheet1.csv"): {
        "95": "{fc9Вызывает смену режима.}",
    },
    ("app_text01", "text/trophy.mbe/000_Sheet1.csv"): {
        "trophy_explanation_027": "Получите оценку ПРЕВОСХОДНО!!! при атаке по слабому месту врага.",
    },
    ("app_text01", "message/s095_077.mbe/000_Sheet1.csv"): {
        "s095_077_320": "{next}Нет.",
    },
    ("patch_text01", "message/s095_077.mbe/000_Sheet1.csv"): {
        "s095_077_320": "{next}Нет.",
    },
    ("app_text01", "text/belong.mbe/000_Sheet1.csv"): {
        "0": "Нет",
    },
    ("app_text01", "text/common_message.mbe/000_Sheet1.csv"): {
        "411": "№ для разбора",
        "1422": "№",
        "ui_sort_0180": "№",
    },
    ("patch_text01", "text/common_message.mbe/000_Sheet1.csv"): {
        "411": "№ для разбора",
    },
}

MESSAGE_SPEAKER_FIXES = {
    ("app_text01", "message/s095_077.mbe/000_Sheet1.csv"): {
        "s095_077_320": "char_PLAYER_M",
    },
    ("patch_text01", "message/s095_077.mbe/000_Sheet1.csv"): {
        "s095_077_320": "char_PLAYER_M",
    },
}

TEXT_SUBSTRING_FIXES = {
    ("app_text01", "text/tutorial_explanation.mbe/000_Sheet1.csv"): {
        "При undergoing эволюции или деволюции,": "При эволюции или деволюции,",
    },
    ("patch_text01", "text/tutorial_explanation.mbe/000_Sheet1.csv"): {
        "При undergoing эволюции или деволюции,": "При эволюции или деволюции,",
    },
}


def read_rows(path: Path) -> list[list[str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.reader(f))


def write_rows(path: Path, rows: list[list[str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        csv.writer(f, lineterminator="\n").writerows(rows)


def rows_by_id(rows: list[list[str]]) -> dict[str, list[str]]:
    return {row[0]: row for row in rows[1:] if row}


def value_column(rel_path: str, row: list[str]) -> int | None:
    if rel_path.startswith("message/"):
        return 2 if len(row) > 2 else None
    if rel_path.startswith("text/"):
        return 1 if len(row) > 1 else None
    return None


def sync_patch_message_file(name: str) -> str:
    app_path = CSV_ROOT / "app_text01" / "message" / f"{name}.mbe" / "000_Sheet1.csv"
    source_patch_path = ORIGINAL_ROOT / "patch_text01" / "message" / f"{name}.mbe" / "000_Sheet1.csv"
    out_path = CSV_ROOT / "patch_text01" / "message" / f"{name}.mbe" / "000_Sheet1.csv"

    app_rows = read_rows(app_path)
    source_rows = read_rows(source_patch_path)
    app_by_id = rows_by_id(app_rows)

    out_rows = [source_rows[0]]
    missing: list[str] = []
    for row in source_rows[1:]:
        if not row:
            out_rows.append(row)
            continue
        translated = app_by_id.get(row[0])
        if translated is None or len(translated) < 3:
            missing.append(row[0])
            out_rows.append(row)
            continue
        new_row = list(row)
        new_row[2] = translated[2]
        out_rows.append(new_row)

    if missing:
        raise RuntimeError(f"{name}: missing translated rows in app_text01: {', '.join(missing[:10])}")

    write_rows(out_path, out_rows)
    return f"{out_path.relative_to(ROOT)} ({len(out_rows) - 1} rows)"


def add_jogress_rows_from_skill_name(package: str) -> str:
    jogress_path = CSV_ROOT / package / "text" / "jogress_skill_name.mbe" / "000_Sheet1.csv"
    skill_path = CSV_ROOT / package / "text" / "skill_name.mbe" / "000_Sheet1.csv"

    jogress_rows = read_rows(jogress_path)
    skill_rows = read_rows(skill_path)
    existing = {row[0] for row in jogress_rows[1:] if row}
    skill_by_id = rows_by_id(skill_rows)

    rows_to_add: list[list[str]] = []
    for row_id in JOGRESS_ROWS:
        if row_id in existing:
            continue
        source = skill_by_id.get(row_id)
        if source is None or len(source) < 2:
            raise RuntimeError(f"{package}: missing source skill_name row {row_id}")
        rows_to_add.append([row_id, source[1]])

    if not rows_to_add:
        return f"{jogress_path.relative_to(ROOT)} (already complete)"

    combined = jogress_rows[1:] + rows_to_add
    combined.sort(key=lambda row: int(row[0]) if row and row[0].isdigit() else 10**12)
    write_rows(jogress_path, [jogress_rows[0], *combined])
    return f"{jogress_path.relative_to(ROOT)} (+{len(rows_to_add)} rows)"


def add_patch_yesno_rows() -> str:
    path = CSV_ROOT / "patch_text01" / "text" / "yes_no_message.mbe" / "000_Sheet1.csv"
    rows = read_rows(path)
    existing = {row[0] for row in rows[1:] if row}

    to_add = [[row_id, text] for row_id, text in YESNO_PATCH_ROWS.items() if row_id not in existing]
    if not to_add:
        return f"{path.relative_to(ROOT)} (already complete)"

    insert_at = len(rows)
    for index, row in enumerate(rows):
        if row and row[0] == "yesno_language_0030":
            insert_at = index + 1
            break
    rows[insert_at:insert_at] = to_add
    write_rows(path, rows)
    return f"{path.relative_to(ROOT)} (+{len(to_add)} rows)"


def fix_voice_language_labels(package: str) -> str:
    path = CSV_ROOT / package / "text" / "common_message.mbe" / "000_Sheet1.csv"
    rows = read_rows(path)
    changed: list[str] = []
    for row in rows[1:]:
        if len(row) < 2:
            continue
        expected = VOICE_LANGUAGE_ROWS.get(row[0])
        if expected is not None and row[1] != expected:
            row[1] = expected
            changed.append(row[0])

    if changed:
        write_rows(path, rows)
        return f"{path.relative_to(ROOT)} ({', '.join(changed)})"
    return f"{path.relative_to(ROOT)} (already correct)"


def fix_graphictext_labels(package: str) -> str:
    path = CSV_ROOT / package / "text" / "graphictext.mbe" / "000_Sheet1.csv"
    rows = read_rows(path)
    changed: list[str] = []
    for row in rows[1:]:
        if len(row) < 2:
            continue
        expected = GRAPHICTEXT_ROWS.get(row[0])
        if expected is not None and row[1] != expected:
            row[1] = expected
            changed.append(row[0])

    if changed:
        write_rows(path, rows)
        return f"{path.relative_to(ROOT)} ({len(changed)} labels)"
    return f"{path.relative_to(ROOT)} (already correct)"


def fix_text_rows(package: str, rel_path: str, replacements: dict[str, str]) -> str:
    path = CSV_ROOT / package / rel_path
    rows = read_rows(path)
    changed: list[str] = []
    for row in rows[1:]:
        col = value_column(rel_path, row)
        if col is None:
            continue
        expected = replacements.get(row[0])
        if expected is not None and row[col] != expected:
            row[col] = expected
            changed.append(row[0])

    if changed:
        write_rows(path, rows)
        return f"{path.relative_to(ROOT)} ({', '.join(changed)})"
    return f"{path.relative_to(ROOT)} (already correct)"


def fix_text_substrings(package: str, rel_path: str, replacements: dict[str, str]) -> str:
    path = CSV_ROOT / package / rel_path
    rows = read_rows(path)
    changed: list[str] = []
    for row in rows[1:]:
        col = value_column(rel_path, row)
        if col is None:
            continue
        updated = row[col]
        for old, new in replacements.items():
            updated = updated.replace(old, new)
        if updated != row[col]:
            row[col] = updated
            changed.append(row[0])

    if changed:
        write_rows(path, rows)
        return f"{path.relative_to(ROOT)} ({', '.join(changed)})"
    return f"{path.relative_to(ROOT)} (already correct)"


def fix_message_speakers(package: str, rel_path: str, replacements: dict[str, str]) -> str:
    path = CSV_ROOT / package / rel_path
    rows = read_rows(path)
    changed: list[str] = []
    for row in rows[1:]:
        if len(row) < 2:
            continue
        expected = replacements.get(row[0])
        if expected is not None and row[1] != expected:
            row[1] = expected
            changed.append(row[0])

    if changed:
        write_rows(path, rows)
        return f"{path.relative_to(ROOT)} speakers ({', '.join(changed)})"
    return f"{path.relative_to(ROOT)} speakers (already correct)"


def main() -> None:
    changed: list[str] = []
    for name in PATCH_MESSAGE_FILES:
        changed.append(sync_patch_message_file(name))
    changed.append(add_jogress_rows_from_skill_name("app_text01"))
    changed.append(add_patch_yesno_rows())
    changed.append(fix_voice_language_labels("app_text01"))
    changed.append(fix_voice_language_labels("patch_text01"))
    changed.append(fix_graphictext_labels("app_text01"))
    for (package, rel_path), replacements in MESSAGE_SPEAKER_FIXES.items():
        changed.append(fix_message_speakers(package, rel_path, replacements))
    for (package, rel_path), replacements in TEXT_ROW_FIXES.items():
        changed.append(fix_text_rows(package, rel_path, replacements))
    for (package, rel_path), replacements in TEXT_SUBSTRING_FIXES.items():
        changed.append(fix_text_substrings(package, rel_path, replacements))

    print("Updated:")
    for item in changed:
        print(f"- {item}")


if __name__ == "__main__":
    main()

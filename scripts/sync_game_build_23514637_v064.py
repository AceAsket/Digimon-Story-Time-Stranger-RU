from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CSV_ROOT = ROOT / "csv" / "patch_text01"
LOG_PATH = ROOT / "logs" / "sync_game_build_23514637_v064.log"


# Steam build 23514637 added 27 patch_text01 records on 2026-07-09.
# Store complete rows so the sync is deterministic and also repairs a partially
# imported row.  The character-name row already existed but used a literal,
# misleading translation, so it is normalized in the same build sync.
ROWS: dict[tuple[str, str], list[str]] = {
    ("message/digimon_chat.mbe/000_Sheet1.csv", "jyos_001_0_char_ASSISTANT_TERRIERMON"): [
        "jyos_001_0_char_ASSISTANT_TERRIERMON",
        "char_ASSISTANT_TERRIERMON",
        "Как человек, что ты думаешь о дигимонах?\nДля исследования мне важно твоё мнение!",
        "",
    ],
    ("message/digimon_chat.mbe/000_Sheet1.csv", "jyos_001_1_replay"): [
        "jyos_001_1_replay",
        "char_PLAYER_M",
        "Без них мне не выполнить свою миссию.",
        "",
    ],
    ("message/digimon_chat.mbe/000_Sheet1.csv", "jyos_001_1_reaction_char_ASSISTANT_TERRIERMON"): [
        "jyos_001_1_reaction_char_ASSISTANT_TERRIERMON",
        "char_ASSISTANT_TERRIERMON",
        "Ого! Восхищаюсь твоей смелостью — не каждый решится\nна такую тяжёлую миссию! Я тоже выложусь по полной!",
        "",
    ],
    ("message/digimon_chat.mbe/000_Sheet1.csv", "jyos_001_2_replay"): [
        "jyos_001_2_replay",
        "char_PLAYER_M",
        "Они — аномалия, окутанная тайной.",
        "",
    ],
    ("message/digimon_chat.mbe/000_Sheet1.csv", "jyos_001_2_reaction_char_ASSISTANT_TERRIERMON"): [
        "jyos_001_2_reaction_char_ASSISTANT_TERRIERMON",
        "char_ASSISTANT_TERRIERMON",
        "Правда? Да, загадок вокруг дигимонов ещё много!\nДавай разгадывать их вместе!",
        "",
    ],
    ("message/digimon_chat.mbe/000_Sheet1.csv", "jyos_001_3_replay"): [
        "jyos_001_3_replay",
        "char_PLAYER_M",
        "Это верные союзники, сражающиеся рядом со мной.",
        "",
    ],
    ("message/digimon_chat.mbe/000_Sheet1.csv", "jyos_001_3_reaction_char_ASSISTANT_TERRIERMON"): [
        "jyos_001_3_reaction_char_ASSISTANT_TERRIERMON",
        "char_ASSISTANT_TERRIERMON",
        "Точно! Ещё не раз попрошу тебя о помощи!",
        "",
    ],
    ("message/digimon_chat.mbe/000_Sheet1.csv", "jyos_001_4_replay"): [
        "jyos_001_4_replay",
        "char_PLAYER_M",
        "Я их очень люблю.",
        "",
    ],
    ("message/digimon_chat.mbe/000_Sheet1.csv", "jyos_001_4_reaction_char_ASSISTANT_TERRIERMON"): [
        "jyos_001_4_reaction_char_ASSISTANT_TERRIERMON",
        "char_ASSISTANT_TERRIERMON",
        "Вот именно! Ладно... Один раз можешь\nпогладить меня по ушам.",
        "",
    ],
    ("text/belong.mbe/000_Sheet1.csv", "790"): ["790", "Зверь"],
    ("text/char_name.mbe/000_Sheet1.csv", "char_ASSISTANT_TERRIERMON"): [
        "char_ASSISTANT_TERRIERMON",
        "Терьермон-ассистент",
        "",
    ],
    ("text/common_message.mbe/000_Sheet1.csv", "19079"): ["19079", "Режим графики"],
    ("text/common_message.mbe/000_Sheet1.csv", "19080"): ["19080", "Качество"],
    ("text/common_message.mbe/000_Sheet1.csv", "19081"): [
        "19081",
        "Этот режим отдаёт приоритет {fc9качеству графики}.\n"
        "Игра поддерживает {fc9разрешение 4K} и изображение HDR.\n"
        "Примечание: дисплей должен поддерживать 4K и HDR.\n"
        "Примечание: режим можно изменить позже.",
    ],
    ("text/common_message.mbe/000_Sheet1.csv", "19082"): ["19082", "Производительность"],
    ("text/common_message.mbe/000_Sheet1.csv", "19083"): [
        "19083",
        "Этот режим отдаёт приоритет {fc9частоте кадров}.\n"
        "Игра работает с частотой до {fc960 кадров/с}.\n"
        "Примечание: режим можно изменить позже.",
    ],
    ("text/common_message_dx11.mbe/000_Sheet1.csv", "1901016"): ["1901016", "HDR"],
    ("text/digimon_profile.mbe/000_Sheet1.csv", "digimon_0790_profile"): [
        "digimon_0790_profile",
        "Прилежный Терьермон, помощник Эксперта Агумона.\n"
        "Терьермон-ассистент больше всего любит изучать разных\n"
        "дигимонов, их экологию и делиться знаниями с другими.\n"
        "Помимо фирменного приёма «Терьер-Торнадо», он применяет\n"
        "«Дай-Бэджи-Гу»: увеличивает значок на груди и запускает\n"
        "его во врагов.",
    ],
    ("text/key_help_text.mbe/000_Sheet1.csv", "key_help_0134"): ["key_help_0134", "Фоторежим"],
    ("text/key_help_text.mbe/000_Sheet1.csv", "key_help_0135"): ["key_help_0135", "Отдалить"],
    ("text/key_help_text.mbe/000_Sheet1.csv", "key_help_0136"): ["key_help_0136", "Приблизить"],
    ("text/key_help_text.mbe/000_Sheet1.csv", "key_help_0137"): [
        "key_help_0137",
        "Показать/скрыть персонажа",
    ],
    ("text/key_help_text.mbe/000_Sheet1.csv", "key_help_0138"): [
        "key_help_0138",
        "Показать/скрыть интерфейс",
    ],
    ("text/key_help_text.mbe/000_Sheet1.csv", "key_help_0139"): [
        "key_help_0139",
        "Показать эволюции",
    ],
    ("text/skill_explanation.mbe/000_Sheet1.csv", "27901"): [
        "27901",
        "[Цель: 1 враг]\n"
        "Наносит физическую атаку {is28}{image(ui_icon_skill_000)} Нейтрального типа силой 30.\n"
        "С вероятностью 100% снижает случайную характеристику на 60% на 1 ход.",
    ],
    ("text/skill_name.mbe/000_Sheet1.csv", "27901"): ["27901", "Дай-Бэджи-Гу"],
    ("text/yes_no_message.mbe/000_Sheet1.csv", "yesno_graphics_0010"): [
        "yesno_graphics_0010",
        "Чтобы изменить режим графики, игра сохранит прогресс\n"
        "и вернётся на титульный экран.\nПродолжить?",
    ],
    ("text/yes_no_message.mbe/000_Sheet1.csv", "yesno_graphics_0020"): [
        "yesno_graphics_0020",
        "Чтобы изменить режим графики, игра сохранит настройки\n"
        "и перезапустится.\nПродолжить?",
    ],
}


def read_rows(path: Path) -> list[list[str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.reader(handle))


def write_rows(path: Path, rows: list[list[str]]) -> None:
    # Preserve the convention used by the source CSV.  A few tables (notably
    # belong.mbe) quote every field, while most tables use QUOTE_MINIMAL; using
    # the wrong convention turns a one-row sync into a whole-file diff.
    first_data = next((row for row in rows[1:] if row), [])
    quote_all = bool(first_data and path.read_text(encoding="utf-8-sig").splitlines()[1].startswith('"'))
    with path.open("w", encoding="utf-8", newline="") as handle:
        csv.writer(
            handle,
            lineterminator="\n",
            quoting=csv.QUOTE_ALL if quote_all else csv.QUOTE_MINIMAL,
        ).writerows(rows)


def main() -> None:
    by_file: dict[str, dict[str, list[str]]] = defaultdict(dict)
    for (relative_file, row_id), row in ROWS.items():
        if not row or row[0] != row_id:
            raise RuntimeError(f"Invalid target row: {relative_file}:{row_id}")
        by_file[relative_file][row_id] = row

    added: list[str] = []
    updated: list[str] = []
    unchanged: list[str] = []
    for relative_file, targets in sorted(by_file.items()):
        path = CSV_ROOT / relative_file
        if not path.exists():
            raise FileNotFoundError(path)
        rows = read_rows(path)
        if not rows:
            raise RuntimeError(f"Empty CSV: {path}")
        expected_columns = len(rows[0])
        if any(len(target) != expected_columns for target in targets.values()):
            raise RuntimeError(f"Column mismatch in targets for {relative_file}")

        found: set[str] = set()
        changed = False
        for index, current in enumerate(rows[1:], 1):
            if not current or current[0] not in targets:
                continue
            row_id = current[0]
            if row_id in found:
                raise RuntimeError(f"Duplicate row ID in {relative_file}: {row_id}")
            found.add(row_id)
            marker = f"patch_text01/{relative_file}:{row_id}"
            target = targets[row_id]
            if current == target:
                unchanged.append(marker)
            else:
                rows[index] = target
                updated.append(marker)
                changed = True

        for row_id in sorted(set(targets) - found):
            rows.append(targets[row_id])
            added.append(f"patch_text01/{relative_file}:{row_id}")
            changed = True

        if changed:
            write_rows(path, rows)

    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    LOG_PATH.write_text(
        "Added rows:\n"
        + "\n".join(added)
        + "\n\nUpdated rows:\n"
        + "\n".join(updated)
        + "\n\nAlready current:\n"
        + "\n".join(unchanged)
        + "\n",
        encoding="utf-8",
    )
    print(f"Added rows: {len(added)}")
    print(f"Updated rows: {len(updated)}")
    print(f"Already current: {len(unchanged)}")
    print(f"Total targets: {len(ROWS)}")


if __name__ == "__main__":
    main()

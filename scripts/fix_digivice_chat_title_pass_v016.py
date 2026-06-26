from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
APP_ROOT = ROOT / "csv" / "app_text01"
PATCH_ROOT = ROOT / "csv" / "patch_text01"
LOG_PATH = ROOT / "logs" / "fix_digivice_chat_title_pass_v016.log"

ROOTS = (APP_ROOT, PATCH_ROOT)

changes: list[str] = []


def set_csv_values(root: Path, rel_path: str, values: dict[str, str], column: int) -> None:
    path = root / rel_path
    if not path.exists():
        changes.append(f"missing {path.relative_to(ROOT).as_posix()}")
        return

    with path.open("r", encoding="utf-8-sig", newline="") as f:
        rows = list(csv.reader(f))

    found: set[str] = set()
    updated = 0
    for row in rows:
        if not row or len(row) <= column:
            continue
        key = row[0]
        if key not in values:
            continue
        found.add(key)
        new_value = values[key]
        if row[column] != new_value:
            old_value = row[column]
            row[column] = new_value
            updated += 1
            changes.append(
                f"{path.relative_to(ROOT).as_posix()}: {key}: {old_value!r} -> {new_value!r}"
            )

    missing = sorted(set(values) - found)
    if missing:
        changes.append(f"{path.relative_to(ROOT).as_posix()}: missing keys {missing}")

    if updated:
        with path.open("w", encoding="utf-8", newline="") as f:
            quoting = csv.QUOTE_ALL if rel_path == "text/main_quest_title.mbe/000_Sheet1.csv" else csv.QUOTE_MINIMAL
            csv.writer(f, lineterminator="\n", quoting=quoting).writerows(rows)


CHAT_SUFFIXES = (
    "child_courage",
    "male_courage",
    "female_courage",
    "old_courage",
    "child_love",
    "male_love",
    "female_love",
    "old_love",
    "child_friendship",
    "male_friendship",
    "female_friendship",
    "old_friendship",
    "child_knowledge",
    "male_knowledge",
    "female_knowledge",
    "old_knowledge",
)


def add_common(values: dict[str, str], key_prefix: str, text: str) -> None:
    for suffix in CHAT_SUFFIXES:
        values[f"{key_prefix}_{suffix}"] = text


def build_chat_values() -> dict[str, str]:
    values: dict[str, str] = {
        "koro_001_0_char_KOROMON": "Я тоже хочу в бой! Прямо сейчас!",
        "koro_001_1_replay": "Хочу скорее отправить тебя в бой.",
        "koro_001_1_reaction_char_KOROMON": (
            "Сначала мне нужно эволюционировать в более сильную форму, да? "
            "Я выложусь на полную, так что поддержи меня!"
        ),
        "koro_001_2_replay": "Сначала тебе стоит посмотреть пару боёв.",
        "koro_001_2_reaction_char_KOROMON": (
            "Я уже кучу боёв посмотрел! Да я почти эксперт."
        ),
        "koro_001_3_replay": "Теперь с этим проще.",
        "koro_001_3_reaction_char_KOROMON": (
            "Ладно. Раз ты так говоришь! Ты правда добрый, знаешь?"
        ),
        "koro_001_4_replay": "Пока не хочу, чтобы ты ввязывался в драки.",
        "koro_001_4_reaction_char_KOROMON": (
            "Ну ладно. Тогда пока оставлю эту идею. Ты меня и правда хорошо знаешь."
        ),
        "tsuno_001_1_reaction_char_TUNOMON": (
            "Ха, значит, я и правда крут, раз смог тебя напугать. "
            "Сейчас напугаю ещё сильнее!"
        ),
        "tsuno_001_2_replay": "Выглядит немного... сомнительно.",
        "tsuno_001_2_reaction_char_TUNOMON": (
            "Сомнительно? Что значит «сомнительно»? Ну же, скажи!"
        ),
        "tsuno_001_3_replay": "Твой рог выглядит очень сильным.",
        "tsuno_001_3_reaction_char_TUNOMON": (
            "Что, правда?! У меня аж голова кругом! Честно!"
        ),
        "tsuno_001_4_reaction_char_TUNOMON": (
            "Спасибо! Мне надо поскорее эволюционировать и стать ещё круче."
        ),
        "kure_001_0_char_CRANIAMON": (
            "Я хотел бы попробовать человеческую еду. Что посоветуешь?"
        ),
        "kure_001_1_replay": "Адски острый рамен!",
        "kure_001_1_reaction_char_CRANIAMON": (
            "Одно название уже требует смелости. Что скрывается за этим вкусом? "
            "Я должен узнать!"
        ),
        "kure_001_2_replay": "Рыбное ассорти с ДГК! Омега-3 хоть отбавляй!",
        "kure_001_2_reaction_char_CRANIAMON": (
            "Блюдо, питающее и желудок, и мозг? Поразительно эффективно!"
        ),
        "kure_001_3_replay": "Устроим вечеринку с хот-потом!",
        "kure_001_3_reaction_char_CRANIAMON": (
            "Еда вкуснее, когда делишь её с другими! Для меня честь разделить её с тобой!"
        ),
        "kure_001_4_replay": "Приготовлю тебе домашний ужин.",
        "kure_001_4_reaction_char_CRANIAMON": (
            "Домашняя еда? Для меня? Хо-хо! Думаю, она будет вкуснее любого ресторана."
        ),
        "common017_1_replay": "И у меня так же. Смелость - это сила!",
        "common017_2_replay": "По-моему, это больше похоже на безрассудство...",
        "common018_1_replay": "Совершенно верно!",
        "common018_2_replay": "Нет, важны и другие вещи.",
        "common050_1_replay": "Конечно. Смелость - это сила идти вперёд!",
        "common050_2_replay": "Есть вещи важнее смелости.",
        "common058_1_replay": "Я ценю дружбу.",
        "common058_2_replay": "Сила превыше всего.",
        "common059_1_replay": "Надеюсь, мы и дальше будем друзьями!",
        "common062_1_replay": "Это неправда. Любовь всё ещё имеет значение.",
        "common062_2_replay": "Да. Времена меняются.",
        "common063_1_replay": "Тогда, пожалуй, пора отдохнуть.",
        "common063_2_replay": "Давай. Ещё чуть-чуть.",
    }

    add_common(values, "common017_1_reaction", "С ней можно выйти за пределы обычных возможностей.")
    add_common(values, "common017_2_reaction", "О-о, правда? Тогда мне стоит быть осторожнее...")
    add_common(values, "common018_0", "Если есть смелость, можно преодолеть что угодно!")
    add_common(values, "common018_1_reaction", "Я так и знал! Будем храбрыми до конца!")
    add_common(values, "common018_2_reaction", "Ха... Правда? Уф, сложно...")
    add_common(
        values,
        "common050_1_reaction",
        "Приятно слышать. Я тоже считаю, что смелость важнее всего.",
    )
    add_common(
        values,
        "common050_2_reaction",
        "Ты прав. Смелость - ещё не всё. Пожалуй, мне стоит пересмотреть свои взгляды.",
    )
    add_common(
        values,
        "common058_1_reaction",
        "Здорово, что мы думаем одинаково. Давай и дальше дорожить нашей дружбой.",
    )
    add_common(
        values,
        "common058_2_reaction",
        "Ты так стремишься к силе... Возможно, мне стоит брать с тебя пример.",
    )
    add_common(values, "common059_0", "Дружить с кем-то другого возраста не так уж плохо.")
    add_common(
        values,
        "common062_0",
        "Когда-то любовь наполняла этот мир. Возможно, теперь такие чувства уже не ценят.",
    )
    add_common(
        values,
        "common062_1_reaction",
        "Значит, любовь живёт в любую эпоху? Благодарю. Мне стало легче.",
    )
    add_common(
        values,
        "common062_2_reaction",
        "Вот как? Время принадлежит молодым... И всё же немного грустно.",
    )
    add_common(values, "common063_0", "*Пыхтит* *хрипит* ...Я просто... немного без сил.")
    add_common(values, "common063_1_reaction", "Ладно... Спасибо. Твоя доброта бесценна.")
    add_common(
        values,
        "common063_2_reaction",
        "*Пыхтит* *хрипит* ...Так со старшими не обращаются...",
    )
    return values


def main() -> None:
    title_values = {"30": "Картина после конца"}

    d14_values = {
        "f_d1402_0030_0010": (
            "У меня есть для вас отчёт, агент. Для вашего Дигивайса доступно\r\n"
            "последнее обновление."
        ),
        "f_d1403_0020_0020": (
            "Он мгновенно сканирует ваше окружение и отмечает всё\r\n"
            "подозрительное. Дигимоны в вашем Дигивайсе помогают в этом."
        ),
    }

    m050_values = {
        "m050_060_020": (
            "Я анализирую данные, поступающие из вашего Дигивайса. Похоже,\n"
            "вернуться к исходной временной шкале будет непросто."
        ),
    }

    field_text_values = {
        "g_tutorial_1001_0040": (
            "Вы можете узнать больше о личности каждого Дигимона в разделе\n"
            "«Дигимоны» > «Настройки» вашего Дигивайса."
        ),
    }

    chat_values = build_chat_values()

    for root in ROOTS:
        set_csv_values(root, "text/main_quest_title.mbe/000_Sheet1.csv", title_values, 1)
        set_csv_values(root, "message/d14.mbe/000_Sheet1.csv", d14_values, 2)
        set_csv_values(root, "message/m050.mbe/000_Sheet1.csv", m050_values, 2)
        set_csv_values(root, "message/field_text.mbe/000_Sheet1.csv", field_text_values, 2)
        set_csv_values(root, "message/digimon_chat.mbe/000_Sheet1.csv", chat_values, 2)

    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    LOG_PATH.write_text("\n".join(changes) + ("\n" if changes else ""), encoding="utf-8")
    print(f"{len(changes)} changes logged to {LOG_PATH.relative_to(ROOT).as_posix()}")


if __name__ == "__main__":
    main()

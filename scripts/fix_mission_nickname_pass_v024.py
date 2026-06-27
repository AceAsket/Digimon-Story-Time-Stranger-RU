from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CSV_ROOT = ROOT / "csv"
LOG_PATH = ROOT / "logs" / "fix_mission_nickname_pass_v024.log"

CSV_ROOTS = [
    path
    for path in sorted(CSV_ROOT.iterdir())
    if path.is_dir() and ((path / "message").exists() or (path / "text").exists())
]


MAIN_QUEST_TITLES = {
    "60": "Резонирующие мысли",
    "70": "Гений или псих?",
    "100": "Промежуточное звено",
    "140": "Тучи сгущаются",
    "160": "Аудиенция у оракула",
    "180": "Крик Древа мира",
    "200": "Начало конца",
    "220": "Откровение в белом свете",
    "235": "8 лет",
    "240": "Клянусь жизнью",
    "270": "Особая точка",
    "280": "Обещание на шарфе",
    "290": "Слишком поздно",
    "300": "Вражда титанов",
    "320": "Райский колизей",
    "350": "Желание Бога скорости",
    "360": "Трон подземелья",
    "390": "От глупости нет лекарства",
    "400": "Война огня и льда",
    "410": "Безумный оракул",
    "420": "Круговорот времени",
    "430": "Часики тикают",
}


QUEST_TITLES = {
    "2": "Безграничное воображение",
    "3": "Тайное бегство",
    "12": "Лечение перемоткой времени",
    "16": "Старый Шеллмон из подземного мира",
    "18": "Цвет, о котором говорит вода",
    "19": "Прислушайся к голосу",
    "24": "Тайна скрытой медовой базы",
    "30": "Скрытая медовая база наносит ответный удар",
    "32": "Могучие братья Бермоны",
    "33": "Послание из-за пределов времени",
    "38": "Просьба кузнеца",
    "39": "Партнёр ремесленника",
    "41": "Отложенное возвращение",
    "50": "Рёв мастера",
    "55": "Что такое любовь?",
    "57": "Мой триумф",
    "60": "Нетерпение и решимость",
    "63": "Карточная игра «Храм яйца»",
    "71": "Найди посланника",
    "73": "Защитите дигимона-малыша в прологе: подземелье",
    "74": "Защитите дигимона-малыша в прологе: правительственное здание",
    "78": "Назад в небеса",
    "89": "Забывчивые помощники",
    "91": "Пропавший друг",
    "93": "Схватка с бессмертным конём",
    "94": "Секретами надо делиться",
    "100": "Рост Ви-мона",
    "105": "Прекрасный рыцарский корпус",
    "106": "Искусное владение мечом",
    "108": "Жизнь на уровне частиц",
    "109": "Беды посредника",
    "112": "Рамен яро-кей и чувство вины",
    "116": "Моя первая карточная битва",
    "147": "Косплеер под прицелом",
    "150": "Подходящий пляжный наряд",
    "155": "Невероятная легенда",
    "157": "Спасение дигимона: отправление",
    "158": "Спасение дигимона: пробуждение",
    "160": "Как подбодрить воина",
    "168": "Сбор батареек",
    "170": "Воплощение великих амбиций",
    "171": "Наблюдение за подземным миром",
    "176": "Претендент на финальную битву",
    "178": "Подарок от хозяев",
    "179": "Заперт в туалете",
    "183": "Упрямый туман",
    "200": "Мечты или реальность?",
    "201": "Все взгляды устремлены на меня!",
    "202": "Молчаливая зависть",
    "216": "Встречи за пределами пространства-времени",
    "500": "Истина нового мира",
    "930": "Скорость - это победа 1",
    "931": "Скорость - это победа 2",
    "932": "Скорость - это победа 3",
    "933": "Скорость - это победа 4",
    "961": "Финальная битва: Агумон (узы храбрости)",
    "962": "Финальная битва: Габумон (узы дружбы)",
    "963": "Финальная битва: Империалдрамон DM",
}


QUEST_CLIENTS = {
    "27": "Вакхмон",
    "28": "Вакхмон",
    "29": "Вакхмон",
}


CHAR_NAMES = {
    "char_PUBLICSAFETY_BATTLE": "Сотрудник общественной безопасности",
    "char_DIGNIFIED_VOICE": "Величавый голос",
    "char_HOMEROS_SLEEPY_GIRL": "Сонная девушка",
    "char_YGGDRASILL_SELFISH_GIRL": "Надменная девушка",
    "char_TOUHO_CALM_BOY": "Спокойный мальчик",
    "char_MAYBE_LEADER": "Мужчина (похоже, лидер)",
    "char_MYSTERIOUS_GIRL": "Таинственная девушка",
    "char_PROTECTED_GIRL": "Девушка под охраной",
    "char_STRONG_VOICE": "Властный голос",
    "char_STRONG_VOICE_DIGIMON": "Дигимон с властным голосом",
    "char_DIGIMON_CALLED_MY_SISTER": "Дигимон по прозвищу «Сестрёнка»",
    "char_GREENGROCER": "Продавец овощей",
    "char_STRAY_DIGIMON": "Дикий дигимон",
    "char_STRAY_DIGIMONS": "Стая диких дигимонов",
    "char_PASSERBY_WOMAN": "Прохожая",
    "char_PASSERBY_MAN": "Прохожий",
    "char_HIGH_SCHOOL_BOY": "Старшеклассник",
    "char_CHEERFUL_VOICE": "Знакомый бодрый голос",
    "char_GREEN_BIG_DIGIMON": "Огромный зелёный дигимон",
    "char_CHILDHOOD_DIGIMON": "Дигимон-малыш",
    "char_DIGIMON_WITH_A_BONE-LIKE_SWORD": "Дигимон с костяным мечом",
    "char_STATION_MASTER_DIGIMON": "Дигимон-начальник станции",
    "char_BEAUTIFUL_VOICE": "Прекрасный голос",
    "char_BEAUTIFUL_DIGIMON": "Прекрасный дигимон",
    "char_DIGIMONS": "Несколько дигимонов",
    "char_MINION_DIGIMON": "Дигимон-подручный",
    "char_VOICES_HEARD_FROM_INSIDE_THE_GATE": "Голос из-за ворот",
    "char_SMALL_TITAN": "Маленький титан",
    "char_DIGIMON_LIKE_A_BEAR_CUB": "Дигимон, похожий на медвежонка",
    "char_SMALL_DIGIMON": "Маленький дигимон",
    "char_BEAUTIFUL_SINGING_VOICE": "Красивый певучий голос",
    "char_BEAUTIFUL_SINGING_VOICE_DIGIMON": "Дигимон с красивым певучим голосом",
    "char_DIGIMON_LIKE_A_LEADER": "Дигимон, похожий на лидера",
    "char_MAD_SINGING_VOICE": "Забавный певучий голос",
    "char_RED_CLOAK_DIGIMON": "Дигимон в красном плаще",
    "char_AEGIOMON_VOICE_OF_THE_HEART": "Эгиомон (внутренний голос)",
    "char_MYSTERIOUS_VOICE": "Таинственный голос",
    "char_VOICE_FULL_OF_RESENTMENT": "Озлобленный голос (тёмный Эгиомон)",
    "char_WIDE_SHOW_COMMENTATOR": "Комментатор ток-шоу",
    "char_WIDE_SHOW_MC": "Ведущий ток-шоу",
    "char_GIANT_BIRD_DIGIMON": "Гигантский птицеподобный дигимон",
    "char_WOMAN_OF_PUBLIC_SECURITY": "Сотрудница общественной безопасности",
    "char_MAN_OF_PUBLIC_SECURITY": "Сотрудник общественной безопасности",
    "char_BEARMON_BRO": "Братья Бермоны",
    "char_MAN_WHO_LIKES_TO_GOSSIP": "Сплетник",
    "char_VOICE_MIXED_WITH_NOISE": "Приглушённый голос",
    "char_DIGIMON_RING ANNOUNCER": "Дигимон-ведущий",
    "char_AUDIBLE_VOICE": "Раздражающий голос",
    "char_ENCHANTING_VOICE": "Манящий голос",
    "char_PALE_MAN": "Бледный мужчина",
    "char_PALE_MAN?": "Бледный мужчина?",
    "char_GOSSIP_GIRL": "Сплетница",
    "char_GIRL_REALLY_NOT_INTERESTED": "Девушка, изображающая интерес",
    "char_TIRED_MAN": "Измученный мужчина",
    "char_STATION_WORKER_DIGIMON": "Дигимон-работник станции",
    "char_RUINS_MANIA": "Исследователь руин",
    "char_SEXY_WOMEN": "Соблазнительная женщина",
    "char_TIRED_OFFICE_WORKER": "Уставший офисный работник",
    "char_GIRL_WHO_LIKES_RUMORS": "Любительница слухов",
    "char_GIRL_NOT_REALLY_INTERESTED_2": "Равнодушная девушка",
    "char_DESPERATE_MEN": "Отчаявшийся мужчина",
    "char_WOMAN_LIKE_MOTHER": "Женщина, похожая на мать",
    "char_WOMAN_LIKE_SHRINE_MAIDEN": "Женщина, похожая на жрицу",
    "char_TRUE_CARD_KING": "Настоящий карточный король",
    "char_WORKING_MAN": "Рабочий",
    "char_BROTHER_WHO_CAME_TO_LUNCH": "Мужчина, пришедший на обед",
    "char_PLAIN_MAN": "Прямолинейный мужчина",
    "char_MAN_IN_WAIT": "Брошенный мужчина",
    "char_KIND_HEARTED_MAN": "Добросердечный мужчина",
    "char_TIRED_OLD_MAN": "Усталый мужчина",
    "char_STANDING_MAN": "Мужчина без дела",
    "char_MYSTERIOUS_MAN": "Загадочный мужчина",
    "char_MAN_LOOKS_KIND": "Мужчина с добрым лицом",
    "char_ANNOYED_WOMAN": "Раздражённая женщина",
    "char_RELAXED_MAN": "Расслабленный мужчина",
    "char_DISTRESSED_WOMAN": "Расстроенная женщина",
    "char_YOUNG_MAN_STANDING": "Бездельничающий юноша",
    "char_YOUNG_MAN": "Молодой мужчина",
    "char_YOUNG_WOMAN": "Молодая женщина",
    "char_CHILDHOOD_DIGIMON_BE_KIDNAPPED": "Похищенный дигимон-малыш",
    "char_INORI_nickname": "Девушка под охраной",
    "char_AEGIOMON_nickname": "Заблудившийся дигимон",
    "char_MINERVAMON_nickname": "Воительница, прибывшая в Синдзюку",
    "char_SUMERAGI_nickname": "Следователь по аномалиям",
    "char_TOUDO_nickname": "Следователь по аномалиям",
    "char_KUREMI_nickname": "Главный следователь по аномалиям",
    "char_MONIKA_SIMMONS_nickname": "Учёная из общественной безопасности",
    "char_JUNOMON_nickname": "Божественный оракул",
    "char_ARENA_001": "В поисках Нанимона",
    "char_ARENA_002": "Короли огромных жуков",
    "char_ARENA_005": "Надёжные правдорубы",
    "char_ARENA_006": "Цирк в красном: без ошибок",
    "char_ARENA_007": "Роял-флеш",
    "char_ARENA_008": "Тайный медовый корпус: королевские коммандос",
    "char_ARENA_009": "Империалдрамон: Режим Паладина",
    "char_ARENA_011": "Эй, парень! Пришёл подраться?!",
    "char_ARENA_012": "Цари Фараомона",
    "char_ARENA_015": "Опекуны хранителя",
    "char_ARENA_016": "Близнецы-терьеры и их учительница",
    "char_ARENA_017": "Могучий безумец",
    "char_ARENA_018": "Марсмон, бог дигибитв",
    "char_ARENA_019": "Трио мастера и ученика",
    "char_ARENA_021": "Красавица-солистка",
    "char_ARENA_022": "Истинный двадцатый",
    "char_ARENA_023": "Золотые незваные гости",
    "char_MIREI_nickname": "Управляющая театром из Промежуточного звена",
    "char_BACCHUSMON_nickname": "Пьяный лесной вожак",
    "char_VULCANUSMON_nickname": "Дигимон-кузнец с божественным оружием",
    "char_VENUSMON_nickname": "Странствующий дигимон-врач",
    "char_APOLLOMON_nickname": "Дигимон-божество солнца и огня",
    "char_DIANAMON_nickname": "Дигимон-божество луны и льда",
    "char_MARSMON_nickname": "Человек-леопард, следующий за братом",
    "char_JUPITERMON_nickname": "Посредник времени и пространства",
    "char_TITAMON_nickname": "Лидер титанов",
    "char_CENTRAL_TOWN_nickname": "Цифровой мир: Илиада - Центральный город",
    "char_FACTORYAL_AREA_nickname": "Цифровой мир: Илиада - Промышленная зона",
    "char_GEAR_FOREST_nickname": "Зелёная земля, где пустило корни Древо мира",
    "char_ABYSS_AREA_nickname": "Синее море дигимонов",
    "char_GUARDIAN_PALACE_nickname": "Храм божественного оракула Юномон",
    "char_REBELLION_VILLAGE_nickname": "Убежище дигимонов",
    "char_GEAR_FOREST_VILLAGE_nickname": "Лесная деревня, где праздник никогда не заканчивается",
    "char_HIGH_RISE_COLOSSEUM_nickname": "Турнирная арена, где правит сила",
    "char_HEAT_COSMIC_nickname": "Выжженная земля, где царит солнце",
    "char_CHILL_COSMIC_nickname": "Замёрзшая земля, где царит луна",
    "char_AKASHIC_RECORDS_nickname": "Пространство, управляющее законами времени",
    "char_TIME_LOOPHOLE_THEATER_nickname": "Таинственное пространство, где люди исчезают",
}


DLC_QUEST_TITLES = {
    "text/quest_title_dlc02.mbe/000_Sheet1.csv": {"520": "Гакуран"},
}


TARGETED_ROWS = {
    "text/common_message.mbe/000_Sheet1.csv": {
        "dlc_name_02": "Дополнительный набор дигимонов и эпизодов 2: Гакуран",
    },
    "text/info_message.mbe/000_Sheet1.csv": {
        "info_message_dlc_02": "{fc9Дополнительный набор дигимонов и эпизодов 2: Гакуран} теперь доступен.\n\nЧтобы сыграть в новый контент, войдите через {is28}{image(ui_icon_minimap_lobby)} Дверь Истины\nв Театре Между Мирами.",
    },
    "text/quest_step.mbe/000_Sheet1.csv": {
        "176010": "Поговорите с Рапидмоном и Фараомоном.",
        "176020": "Сразитесь с Рапидмоном и Фараомоном.",
    },
    "text/info_message_dlc02.mbe/000_Sheet1.csv": {
        "9002007": "Даже после завершения «Гакуран» вы можете поговорить\nс дворецким в лифтовом зале и снова принять вызов.\n\nНаграды за прохождение также можно получить повторно.",
    },
}


TEXT_REPLACEMENTS = {
    "Шелмона": "Шеллмона",
    "Шелмону": "Шеллмону",
    "Шелмоном": "Шеллмоном",
    "Шелмоне": "Шеллмоне",
    "Шелмон": "Шеллмон",
    "Дайвермона": "Дивермона",
    "Дайвермону": "Дивермону",
    "Дайвермоном": "Дивермоном",
    "Дайвермоне": "Дивермоне",
    "Дайвермон": "Дивермон",
    "Бирмона": "Бермона",
    "Бирмону": "Бермону",
    "Бирмоном": "Бермоном",
    "Бирмоне": "Бермоне",
    "Бирмоны": "Бермоны",
    "Бирмонов": "Бермонов",
    "Бирмон": "Бермон",
    "Фараонамона": "Фараомона",
    "Фараономмоном": "Фараомоном",
    "Фараонмон": "Фараомон",
    "фараона!": "Фараомона!",
}


changes: list[str] = []


def set_csv_values(root: Path, rel_path: str, values: dict[str, str], column: int = 1) -> None:
    path = root / rel_path
    if not path.exists():
        return

    with path.open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.reader(f))

    found: set[str] = set()
    updated = 0
    for row in rows:
        if len(row) <= column:
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
            changes.append(f"{path.relative_to(ROOT).as_posix()}: {key}: {old_value!r} -> {new_value!r}")

    missing = sorted(set(values) - found)
    if missing:
        changes.append(f"{path.relative_to(ROOT).as_posix()}: missing keys {missing}")

    if updated:
        with path.open("w", encoding="utf-8", newline="") as f:
            csv.writer(f, lineterminator="\r\n").writerows(rows)


def replace_text_fragments_in_root(root: Path) -> None:
    for path in sorted(root.rglob("*.csv")):
        with path.open("r", encoding="utf-8", newline="") as f:
            rows = list(csv.reader(f))

        updated = 0
        for row in rows:
            for index in range(1, len(row)):
                old_value = row[index]
                new_value = old_value
                for old, new in TEXT_REPLACEMENTS.items():
                    new_value = new_value.replace(old, new)
                if old_value != new_value:
                    row[index] = new_value
                    updated += 1
                    if updated <= 30:
                        changes.append(
                            f"{path.relative_to(ROOT).as_posix()}: {row[0]}: {old_value!r} -> {new_value!r}"
                        )

        if updated:
            if updated > 30:
                changes.append(f"{path.relative_to(ROOT).as_posix()}: {updated} text fragment replacements")
            with path.open("w", encoding="utf-8", newline="") as f:
                csv.writer(f, lineterminator="\r\n").writerows(rows)


def main() -> None:
    for root in CSV_ROOTS:
        set_csv_values(root, "text/main_quest_title.mbe/000_Sheet1.csv", MAIN_QUEST_TITLES)
        set_csv_values(root, "text/quest_title.mbe/000_Sheet1.csv", QUEST_TITLES)
        set_csv_values(root, "text/quest_client.mbe/000_Sheet1.csv", QUEST_CLIENTS)
        set_csv_values(root, "text/char_name.mbe/000_Sheet1.csv", CHAR_NAMES)
        for rel_path, values in DLC_QUEST_TITLES.items():
            set_csv_values(root, rel_path, values)
        for rel_path, values in TARGETED_ROWS.items():
            set_csv_values(root, rel_path, values)

    for root_name in ("app_text01", "patch_text01"):
        replace_text_fragments_in_root(CSV_ROOT / root_name)

    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    LOG_PATH.write_text("\n".join(changes) + ("\n" if changes else ""), encoding="utf-8")
    print(f"Applied {len(changes)} mission/title/nickname edits. Log: {LOG_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()

from __future__ import annotations

import csv
import io
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CSV_ROOT = ROOT / "csv"
LOG_PATH = ROOT / "logs" / "fix_machine_calque_pass_v060.log"


# Targeted pass for English calques such as "in the past", "not that",
# "not like", and "or something" where the current Russian sounds machine-made.
REPLACEMENTS: dict[str, dict[str, str]] = {
    "message/d01.mbe/000_Sheet1.csv": {
        "f_d0103_0090_0010": "О-о, лифту конец... Вряд ли мы снова\nзаставим его работать...",
    },
    "message/d02.mbe/000_Sheet1.csv": {
        "f_d0202_0550_0020": "Ну надо же! Великий Страж собственной персоной!\nВот это была драка!",
        "f_d0202_0630_0030": "Хотя вам, конечно, никогда не сравниться с моими\nгероическими подвигами! Хахаха!",
        "f_d0203_0010_0223": "Эй, я тут не только из-за еды торчу!",
        "f_d0203_0010_0300": "О, кстати... Ты здорово сражался против\nтех титанов!",
    },
    "message/d03.mbe/000_Sheet1.csv": {
        "f_d0302_0270_0010": "Хм? Вы, ребята, явно не местные.\nДостопримечательности осматриваете?",
        "f_d0302_0240_0070": "Ну, я не думаю, что ты лжёшь... но...",
    },
    "message/d05.mbe/000_Sheet1.csv": {
        "f_d0501_0140_0010": "Мы сейчас в затруднительном положении. Лифт позади нас\nотключён, им нельзя пользоваться.",
        "f_d0502_0220_0050": "...Я запомню, как ты пытался меня там бросить.",
        "f_d0506_0070_0020": "Хотя над остальными тоже смеяться не стоит...\nДумаю, с ними тоже нельзя сдерживаться.",
        "f_d0513_0030_0020": "Впрочем, этого и следовало ожидать. Ты ведь не мог\nпроиграть так рано!",
        "f_d0513_0050_0010": "Эй, похоже, у тебя всё хорошо! Я, конечно,\nне переживал, что у тебя не выйдет.",
    },
    "message/d06.mbe/000_Sheet1.csv": {
        "f_d0603_0050_0030": "Забудь об этом, ладно? Что это?\nПохоже на какой-то переключатель!",
        "f_d0604_0090_0061": "А, это вы. Не сказать, что я по вам скучала.",
        "f_d0604_0240_0010": "Ладно, дело сделано. Это всё благодаря твоим усилиям.",
    },
    "message/d09.mbe/000_Sheet1.csv": {
        "f_d0901_0020_0060": "Лорд Плутомон сказал, что этих ребят вроде как\nискусственно «создали»!",
        "f_d0901_0120_0030": "Значит, решено... другого транспорта у вас всё равно нет...\nПросто уточняю: вам же НАДО идти, глурп?",
        "f_d0902_0080_0020": "Мы всегда были вместе, так что и конец встретим вместе!\n...Хотя умирать я, конечно, не собираюсь!",
        "f_d0903_0010_0190": "Эй! Я не сдерживаюсь и не притворяюсь! Я\nправда сейчас не могу их сломать.",
        "f_d0903_0020_0020": "Но дальше, похоже, не пройти... Что нам делать?",
        "f_d0903_0045_0280": "Да, мы во многом не сходимся во взглядах, но\nя не желала тебе смерти.",
    },
    "message/d11.mbe/000_Sheet1.csv": {
        "f_d1101_0040_0010": "Эй, эта машина, похоже, подключена к затвору.\nЕсли бы мы как-нибудь смогли её запустить...",
    },
    "message/d12.mbe/000_Sheet1.csv": {
        "f_d1204_0220_0010": "Эх... Хочу снова устроить шоу, как тогда в городе.",
    },
    "message/d14.mbe/000_Sheet1.csv": {
        "f_d1405_0020_0010": "Этим путём нам, похоже, не вернуться.",
    },
    "message/digimon_chat.mbe/000_Sheet1.csv": {
        "nep_001_1_reaction_char_NEPTUNEMON": "Чувства, конечно, важны, но нужны и действия.\nВпрочем, тебе это и так понятно.",
        "fuga_001_4_reaction_char_FUGAMON": "И как ты собираешься защищаться? Хотя ладно.\nЕсли что, я всё равно помогу.",
        "presi_001_4_reaction_char_PLESIOMON": "Хм. Если таково ваше желание, пусть будет так.\nЯ такую цель не осуждаю.",
        "viki_001_1_reaction_char_VIKEMON": "Тьфу! Привыкнешь к этой жаре, а потом замёрзнешь,\nкак только похолодает!",
        "asta_001_3_reaction_char_ASTAMON": "Думаю, нож сгодился бы для игры с тобой.\nНо я бы тебя, конечно, не пырнул.",
        "migao_001_3_reaction_char_MIRAGEGAOGAMON": "Его всё же можно разглядеть. Даже моё остаточное\nизображение достойно внимания.",
    },
    "message/field_text.mbe/000_Sheet1.csv": {
        "g_shop096_0020_0010": "Где мы встретимся в следующий раз — в прошлом или\nв будущем? Помни, тебе всегда здесь рады.",
        "g_shop099_0020_0010": "Где мы встретимся в следующий раз — в прошлом или\nв будущем? Помни, тебе всегда здесь рады.",
    },
    "message/m080.mbe/000_Sheet1.csv": {
        "m080_060_012": "Нас что, духи унесли?{next}",
        "m080_110_070": "Но раньше люди считали эти огни богами.",
    },
    "message/m090.mbe/000_Sheet1.csv": {
        "m090_030_020": "Я вовсе не извиняться пришёл!",
    },
    "message/m110.mbe/000_Sheet1.csv": {
        "m110_050_190": "Похоже, это случилось не недавно...",
        "m110_070_050": "Хотя шансов у тебя всё равно нет!",
    },
    "message/m150.mbe/000_Sheet1.csv": {
        "m150_110_010": "Похоже, она не откроется. Может, Кокувамон поможет?",
    },
    "message/m160.mbe/000_Sheet1.csv": {
        "m160_060_110": "Прежде конфликты дигимонов уже вредили миру людей.",
    },
    "message/m170.mbe/000_Sheet1.csv": {
        "m170_130_130": "Ты что, головой ударился? Как ты смеешь\nмне приказывать?!",
    },
    "message/m190.mbe/000_Sheet1.csv": {
        "m190_021_090": "Ого... Его явно не просто отбросило.\nНа мой взгляд, он почти цел.",
    },
    "message/m235.mbe/000_Sheet1.csv": {
        "m235_020_060": "Справедливый вопрос. В такой одежде вы бы меня\nи не узнали.",
        "m235_020_080": "Мы с вами уже несколько раз говорили.",
    },
    "message/m260.mbe/000_Sheet1.csv": {
        "m260_060_010": "Похоже, титанов здесь нет. Наверняка это всё\nблагодаря стараниям Шеллмон.",
    },
    "message/m420.mbe/000_Sheet1.csv": {
        "m420_120_200": "Я не могу вечно жить прошлым. Я должен выбрать\nбудущее.",
    },
    "message/rumor_npc.mbe/000_Sheet1.csv": {
        "r_d0906_0050_0020": "Как держишься? Я не волнуюсь, просто спрашиваю!",
    },
    "message/s020_019.mbe/000_Sheet1.csv": {
        "s020_019_690": "Я-я ещё не всё проверил!",
    },
    "message/s030_030.mbe/000_Sheet1.csv": {
        "s030_030_010": "Квок! Помнишь меня? Я тот Мучомон, которому ты помогал с\nФанбимон восемь лет назад.",
    },
    "message/s050_043.mbe/000_Sheet1.csv": {
        "s050_043_220": "Что с тобой?! Ты бредишь?\nУспокойся и хорошенько всё обдумай.",
        "s050_043_840": "Привет. Давно не виделись. Помнишь меня? Раньше я был\nСолармоном под началом мастера Беармона.",
    },
    "message/s070_056.mbe/000_Sheet1.csv": {
        "s070_056_360": "Что с тобой такое? Головой ударился?",
        "s070_056_361": "Что с тобой такое? Головой ударился?",
    },
    "message/s080_060.mbe/000_Sheet1.csv": {
        "s080_060_220": "Хм. Думаю, это не то место.",
    },
    "message/s110_093.mbe/000_Sheet1.csv": {
        "s110_093_070": "И что мне с этого?! Крылья от этого всё равно\nне вырастут!",
    },
    "message/s110_101.mbe/000_Sheet1.csv": {
        "s110_101_750": "Возможно, но этой битвы нам всё равно\nне избежать!",
    },
    "message/s200_147.mbe/000_Sheet1.csv": {
        "s200_147_410": "Я сразу это понял! От меня такое не скроешь!",
        "s200_147_630": "Что это вообще было...? Мне приснился кошмар...?",
    },
    "message/s910_170.mbe/000_Sheet1.csv": {
        "s910_170_540": "...это полностью ломает будущее. Кажется, это называется\nвременным парадоксом.",
        "s910_170_870": "Будто я стану частным детективом. Звучит весело.\nЯ в деле!",
        "s910_170_1380": "В этом нет необходимости. Любопытство ведь\nне порок, правда?",
        "s910_170_1740": "{next}Похоже, он вдохновил свою молодую версию.",
    },
    "message/t03.mbe/000_Sheet1.csv": {
        "f_t0303_0100_0010": "Похоже, этих детей здесь нет...",
        "f_t0303_0120_0010": "Эта дверь, похоже, ещё долго не откроется...",
    },
    "message/t04.mbe/000_Sheet1.csv": {
        "f_t0401_0100_0010": "Роллеты уже давно опущены. Вряд ли их скоро поднимут.",
        "f_t0403_0170_0070": "Э-Этот человек... просто в косплее!",
    },
    "text/digimon_profile.mbe/000_Sheet1.csv": {
        "digimon_0410_profile": (
            "Дигимон-пикси, управляющий магией.\n"
            "Пиксимон умеет читать слова на продвинутом\n"
            "языке программирования из другого измерения\n"
            "и творить чудеса, почти как магию.\n"
            "Этот загадочный дигимон может появиться\n"
            "когда угодно, где угодно и в любом\n"
            "пространстве. Несмотря на малый размер,\n"
            "он владеет особым навыком, позволяющим\n"
            "запечатывать способности врагов и\n"
            "сокрушать их одним мощным ударом.\n"
            "Пиксимон любит розыгрыши и с удовольствием\n"
            "устраивает хаос в компьютерах своим любимым\n"
            "копьём «Фэри Тейл», которым всегда вооружён,\n"
            "хотя злого умысла у него нет. Его особый приём\n"
            "«Пит Бомб» сжимает компьютерный вирус и\n"
            "создаёт сверхмощный взрыв. Несмотря на\n"
            "внешность, атаки Пиксимона пугающе сильны."
        ),
    },
    "text/digitter_message.mbe/000_Sheet1.csv": {
        "main_120_090_011": "Как и ты, другие люди, видимо, тоже случайно попадали\nв тот мир. Одно это объяснило бы несколько аномалий...!",
        "main_210_020_132": "В древности люди, увидев такое, могли придумывать\nбожеств или существ из фольклора.",
        "main_390_010_020": "Как им удалось захватить и контролировать всех этих Дигимонов?\nОни ведь не беззащитны...",
    },
}


def text_column_for(relative_path: str) -> int:
    return 1 if relative_path.startswith("text/") else 2


def detect_csv_style(raw: bytes) -> tuple[str, bool, bool]:
    body = raw[3:] if raw.startswith(b"\xef\xbb\xbf") else raw
    line_terminator = "\r\n" if b"\r\n" in body else "\n"
    text = body.decode("utf-8")
    physical_lines = [line for line in text.splitlines() if line]
    quote_all_data = len(physical_lines) > 1 and physical_lines[1].startswith('"')
    has_bom = raw.startswith(b"\xef\xbb\xbf")
    return line_terminator, quote_all_data, has_bom


def serialize_rows(rows: list[list[str]], line_terminator: str, quote_all_data: bool) -> str:
    buffer = io.StringIO(newline="")
    if quote_all_data and rows:
        header_writer = csv.writer(buffer, lineterminator=line_terminator)
        header_writer.writerow(rows[0])
        data_writer = csv.writer(buffer, lineterminator=line_terminator, quoting=csv.QUOTE_ALL)
        data_writer.writerows(rows[1:])
    else:
        writer = csv.writer(buffer, lineterminator=line_terminator)
        writer.writerows(rows)
    return buffer.getvalue()


def apply_root(root_name: str) -> list[str]:
    changed: list[str] = []
    missing: list[str] = []
    for relative_path, row_updates in REPLACEMENTS.items():
        path = CSV_ROOT / root_name / relative_path
        if not path.exists():
            continue
        raw = path.read_bytes()
        line_terminator, quote_all_data, has_bom = detect_csv_style(raw)

        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.reader(handle))

        column = text_column_for(relative_path)
        pending = dict(row_updates)
        file_changed = False
        for row in rows:
            if not row or row[0] not in pending:
                continue
            if len(row) <= column:
                missing.append(f"{root_name}/{relative_path}:{row[0]}: no text column")
                continue
            new_text = pending.pop(row[0])
            if row[column] != new_text:
                row[column] = new_text
                file_changed = True
                changed.append(f"{root_name}/{relative_path}:{row[0]}")

        for row_id in sorted(pending):
            missing.append(f"{root_name}/{relative_path}:{row_id}")

        if file_changed:
            output = serialize_rows(rows, line_terminator, quote_all_data).encode("utf-8")
            if has_bom:
                output = b"\xef\xbb\xbf" + output
            path.write_bytes(output)

    if missing:
        raise RuntimeError("Missing rows:\n" + "\n".join(missing))
    return changed


def main() -> None:
    changed = []
    for root_name in ("app_text01", "patch_text01"):
        changed.extend(apply_root(root_name))

    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    LOG_PATH.write_text("\n".join(changed) + f"\nUpdated rows: {len(changed)}\n", encoding="utf-8")
    print(f"Updated rows: {len(changed)}")


if __name__ == "__main__":
    main()

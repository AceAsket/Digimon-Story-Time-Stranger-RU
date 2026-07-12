#!/usr/bin/env python3
"""Apply source-checked fixes for newly reported story and side-quest scenes."""

from __future__ import annotations

import csv
import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CSV_ROOT = ROOT / "csv"
P = "patch_text01"

# package, relative CSV, row id, column, expected current SHA-256, replacement
UPDATES: list[tuple[str, str, str, int, str, str]] = []


def add(relative: str, row_id: str, expected_hash: str, replacement: str, column: int = 2) -> None:
    UPDATES.append((P, relative, row_id, column, expected_hash, replacement))


# Aegiomon addresses the female Oracle/Junomon; remove the literal "indulge" calque.
add("message/m160.mbe/000_Sheet1.csv", "m160_060_050",
    "9bb12f6da63909f9ea68b36ad81e69654c222d0c9719d6abe558cc30442b203e",
    "В-Вся эта история про «Хрономона» и «Великого Стража»...\n"
    "Как бы ты ни объясняла, я всё равно ничего не понимаю...")
add("message/m160.mbe/000_Sheet1.csv", "m160_060_210",
    "44e6d0753298d8d80daca04b9ff3844f346cedafd300d2a96bdf775c78d991d3",
    "Ты исполнишь мою просьбу, Эгиомон?")
add("message/m160.mbe/000_Sheet1.csv", "m160_060_220",
    "4c4753fdd1e6c5a053558093b71e3beef23985ad52f47f9fa6aeac992addd6b5",
    "Д-да... Думаю, смогу.")

# Operator report.
add("message/m170.mbe/000_Sheet1.csv", "m170_010_050",
    "2214289b6af83ee30c5912f56339f398bbd40b4bb522e73ef35c03785b6544ae",
    "АДАМАС отслеживает ряд нераскрытых дел... Мы полагаем,\n"
    "что за большинством из них могут стоять дигимоны.")

# Quest objectives: canonical item/name terminology and one consistent imperative.
QUEST_STEPS = {
    "78020": ("dc904ed67330d7a721eda5648c861b8e35ea16ac477ad635a96fa71906dfbbe3", "Добудь большой запас металла."),
    "78030": ("e82b02fc68b165ff8088776b60a0a6cdf4308ad0fc1d0c7a67cc9ccd185e4daf", "Отдай Андромону большой запас металла."),
    "78040": ("e1a99f256a03091541e96bdc753da8aa9ac7dbc0acf968d89a21bd4774273179", "Поговори с отремонтированным Блимпмоном."),
    "152010": ("b5453d568133c41609bafff13c60deac0d58e1587903e10f9de761804fee5af5", "Поговори с Пегасмоном."),
    "152020": ("cb07cfbd4315cd3d51724737f07659938651b0bf32422123dbdb1bd8c9ee4a2c", "Передай Дигиментал искренности Пегасмону."),
    "152030": ("fe439c1ab8f7f212dffb3405dc6080ec8c2459b2c8457324253ab570c714bf47", "Передай Дигиментал света Пегасмону."),
    "152040": ("af8171f9befa9129511416078007fb59a411f4271d3cfc8129e16f116e585b06", "Передай Дигиментал дружбы Пегасмону."),
    "152050": ("40485cbf36c247cc7e0e2b161c058a800adb3d2dfde34e66004c2e94be7ea9f3", "Передай Дигиментал судьбы Пегасмону."),
    "152060": ("2420067e496b06e2d077f52701bc94614f4bbfa355060a0b5876a514bc6cddea", "Передай Дигиментал мужества Пегасмону."),
    "152070": ("b5453d568133c41609bafff13c60deac0d58e1587903e10f9de761804fee5af5", "Поговори с Пегасмоном."),
}
for row_id, (expected_hash, replacement) in QUEST_STEPS.items():
    add("text/quest_step.mbe/000_Sheet1.csv", row_id, expected_hash, replacement, column=1)

# Guardromon/LoaderLiomon metal-production menu.
GUARDROMON = {
    "s095_077_480": ("9d05123a4658b35592783258b06b910b7a2d898ed7dce779ffd13f4b319a87c3", "Теперь я буду не только добывать металл, но и доставлять его\nобратно."),
    "s095_077_490": ("25a6a68a5c05f53e36a55b116e21c57123b4af5cbf52a831d09be44c7ab85be8", "Лоадер Лиомон вернулся, и теперь мы снова можем производить\nразные металлы. Заходи, если что-нибудь понадобится."),
    "s095_077_500": ("bd477fa81deec72885e2fab0d0b6b459b218592de3733df574003103b148e875", "Благодаря тебе производство идёт без перебоев.\nЧем я могу помочь?"),
    "s095_077_520": ("810fd2267141b1c06b4663897e2b0bb2f4b643d5bceabaec500a96030a6689cc", "Для починки молота нужен... хрондигизойтовый металл, верно?"),
    "s095_077_530": ("f18601a11f09cb3950830c6ec67b9846b5f213b14b991978db5b022070b4252e", "Возьми. Это ценный материал, поэтому могу поделиться лишь\nнебольшой порцией."),
    "s095_077_540": ("79ffd9245662267a81e25f7523ec37aa08f478010cf303e389c8c0afd6bd4fe7", "Понятно. Для ремонта нужен большой запас металла, верно?"),
    "s095_077_550": ("46c46d287ea10c144638e467a4a762a65a08e246a4ff22781276992581d9d269", "Держи. Металла много, так что попроси кого-нибудь из дигимонов\nпомочь его донести."),
    "s095_077_560": ("bcc5c0412013903f225ac06f6cd690076b1c9f92dfee1c14efbaf0a03aab4642", "До встречи. Обращайся, если ещё понадобится помощь."),
    "s095_077_570": ("815a429674a75df52ea5523c5ee162fc7fda603a4bbb00a2b103f55da1eb21bd", "Тебе ещё что-нибудь нужно? Производство идёт без перебоев,\nтак что я могу помочь."),
    "s095_077_580": ("18d8a3e2de7d95fea2c61c7ae6d41678fa89acf13c88409dc08f0983e7633072", "Все материалы у меня под рукой. Обращайся, если что-нибудь\nпонадобится."),
}
for row_id, (expected_hash, replacement) in GUARDROMON.items():
    add("message/s095_077.mbe/000_Sheet1.csv", row_id, expected_hash, replacement)

GUARD_MENU_TEXT = "Благодаря тебе производство идёт без перебоев.\nЧем я могу помочь?"
add("message/s110_101.mbe/000_Sheet1.csv", "s110_101_420",
    "bd477fa81deec72885e2fab0d0b6b459b218592de3733df574003103b148e875", GUARD_MENU_TEXT)
add("message/s110_102.mbe/000_Sheet1.csv", "s110_102_620",
    "bd477fa81deec72885e2fab0d0b6b459b218592de3733df574003103b148e875", GUARD_MENU_TEXT)

# Zudomon: preserve the English hammering wordplay and remove material calques.
ZUDOMON = {
    "s050_039_220": ("84204462b6d90c5a335c67cc1ac86e3afa94a20705eedf4d07e40df04c9dcfb1", "Как только добуду хрондигизойтовый металл, с остальным справлюсь\nсам. Удачи в поисках!"),
    "s050_039_230": ("a02dbc12c9e98f114a6836cc3c7e15274762402e1a15303ff1cb9ad9dfd6953c", "Ого, это хрондигизойтовый металл?! Давай сюда — теперь я смогу\nпочинить молот!"),
    "s050_039_240": ("94f5d6346b2609d1be5676d2aae255e4c72dfd69b4b577c90b708c428adbc043", "Этот молот — мой товарищ и в работе, и в бою. Без него я словно\nбез рук."),
    "s050_039_250": ("926ebca394851f4ea005afe547ee2b94f5860a8b81d5db917c5542781d964baa", "Выходит, я обязан тебе жизнью. Держи — это самое малое, чем я\nмогу тебя отблагодарить."),
    "s050_039_260": ("9d5c9cc842d5772d9e382dfef3e95dc106e6997812478a38e74ad6bd35c6ca1e", "Теперь я снова могу взяться за молот! Скоро накую много всякого,\nтак что заглядывай!"),
    "s050_039_270": ("c23bea6ed4c2c125e3ca4c8556cb2213e3e13e0e81b60c40719751d295b5c4b8", "Вот бы когда-нибудь побывать в реакторе! Было бы здорово\nпоработать вместе с Вулканусмоном!"),
}
for row_id, (expected_hash, replacement) in ZUDOMON.items():
    add("message/s050_039.mbe/000_Sheet1.csv", row_id, expected_hash, replacement)

# Blimpmon is contextually male in this localization and travels by flying.
BLIMPMON = {
    "s095_078_010": ("11b380efe3e47621d568760003b4137b25a36e7ff7b9c51aedd22ee45e0bd406", "Ой... Кажется, я что-то сломал. Я едва могу двигаться."),
    "s095_078_060": ("2d8e4d75efcc3b093004add84593561bff8d24e9c45f602ac5b656d4f9cb3557", "НЕПОСРЕДСТВЕННОЙ УГРОЗЫ ЕГО ЖИЗНИ НЕТ,\nНО ПОВРЕЖДЕНИЯ ОБШИРНЫ."),
    "s095_078_070": ("f1752b438a3f7770a819962ddc2cace2e5474799f6d908b9cbc122cad01bfb77", "ДЛЯ РЕМОНТА НУЖНО МНОГО МЕТАЛЛА\nИЗ НЕДАВНО ОТКРЫВШИХСЯ ШАХТ."),
    "s095_078_090": ("a6e3c60bfe620cb1ccb0c36bc5c04610bea270a9e2e2101211f935c54e5e330e", "РЕМОНТ ЗАВЕРШЁН. БЛИМПМОН ВОССТАНОВЛЕН\nДО ПРЕЖНЕГО СОСТОЯНИЯ."),
    "s095_078_100": ("29667d47a3f33a340dc02aa20c11f0beac0f8c8de6393e07ba6306825a25303e", "А ТЕПЕРЬ Я, ПОЖАЛУЙ, ПОЙДУ."),
    "s095_078_110": ("300c47aadea70d75bcd1682d249505939d87b702637674b3adbc8ea128ca384b", "Эй! Посмотри на меня! Круто, да? Я снова готов летать по небу!"),
    "s095_078_120": ("d6a6a63916e280a07007a8d0b3cdaa4c7b4f227c7d9d48892cf7aae97d61fc17", "Так это ты помог мне починиться? Спасибо! Вот награда за помощь!"),
    "s095_078_130": ("f4995f3d7d94bfedf61451d677b3d1ccc6218b8229ad4e5949a6757662575f89", "Ну что, куда летим? Я могу отвезти тебя куда угодно!\nА пока возвращаюсь в Центральный город!"),
}
for row_id, (expected_hash, replacement) in BLIMPMON.items():
    add("message/s095_078.mbe/000_Sheet1.csv", row_id, expected_hash, replacement)

add("message/digimon_chat.mbe/000_Sheet1.csv", "blimp_001_0_char_BLIMPMON",
    "e73f3590a6faa1de4a4bd4daa839b42c5439215cfff6e0bd3ffa9b4ab7202b9b",
    "Куда хочешь отправиться? Если я смогу туда долететь,\nобязательно тебя отвезу!")
add("message/d02.mbe/000_Sheet1.csv", "f_d0201_0290_0030",
    "81cf44869e4ba5f003f878b426bbd8e64f52f6a71678018b696da2599968a4dc",
    "Ладно! Тогда полетели!")

# Pegasusmon quest: Digi-Egg is localized as Digimental throughout the UI.
PEGASMON = {
    "s050_152_140": ("949555347194f7093f485e38be414a56a8defa96662c358897e8fa3f7f4b895b", "Для броневой эволюции им нужны Дигименталы.\nДля начала — Дигиментал искренности."),
    "s050_152_150": ("853d8e80e88604232d58952393053edd53e94e31b5a67402438305bb8b01c75c", "{next}Вообще-то у меня есть Дигиментал искренности."),
    "s050_152_180": ("903c8add3b1b1a0c88f9f77fdd8901a6a87955b6960d583b5865b693672cc870", "Вот бы у меня был Дигиментал...!"),
    "s050_152_190": ("45cce95d6442567a7e034db38a8f4e0cd4bdd3e14a82dbecb87347e62d75e481", "Прости, что заставил ждать, друг! Я принёс тебе Дигиментал!"),
    "s050_152_250": ("adfd835f6854b2e06a83921a062aea5885836ba4831aadb155d6bc38546e2249", "Я знаю и других дигимонов, которые тоже хотят пройти\nброневую эволюцию."),
    "s050_152_260": ("311234d0eb5bf265e53a6b93189ab6cddb2ab82c8e8795e11585aa5543b60e60", "Им нужны Дигименталы света, дружбы и мужества.\nДай знать, если найдёшь хотя бы один."),
    "s050_152_280": ("8d50da8cd5818367db30c8320b360ba1705038d9af9f09945375c02d9258f5f1", "Привет! У тебя есть Дигиментал для моих союзников?"),
    "s050_152_300": ("b79bc374e5973ea29c1cbc75a26f9cf9d81d95dae1fd242c565b73f37871d07d", "Какой Дигиментал ты мне передашь?"),
    "s050_152_310": ("e3358049f50778264a6146eef70bcdacb6fc9d1127014c6777f3dc30328bc379", "Моим союзникам нужны Дигименталы света, дружбы\nи мужества. Если найдёшь один из них, принеси мне."),
    "s050_152_340": ("4acd3a6cc2155ba76842d6af8e2968144b173ea1250dca31ceb27a12acb15e34", "О, это Дигиментал! Спасибо! Я чувствую, как меня озаряет свет!"),
    "s050_152_370": ("18828b93401be394fe919ca7b850ada0cb68b218e301aa9491375182dd6c676e", "О, это Дигиментал! Спасибо! Теперь я выложусь на полную!"),
    "s050_152_390": ("a15a2ec36c76ccf1cee5e1a60118fbba34d6fb410924eb5713c6ecbaa7134b62", "Прости за задержку! Вот твой Дигиментал!"),
    "s050_152_400": ("dee61cb0c53032eeb1e007009bc5b188b1805438ee3545ad3fd6e4dda337c0fb", "Я чувствую, как во мне пылает неугасимое пламя мужества!"),
    "s050_152_410": ("4783f789c0454427665502171f0bcb0863509e7be5c1b44861d419c979cb640f", "Отлично, эволюция удалась! А теперь вместе покажем всё,\nна что способны!"),
    "s050_152_420": ("4bc7cfb1148dd70626828b2b851372b288fc9859b8d75428d8b91120021c5a38", "Спасибо за Дигиментал! Благодаря тебе\nя помог ещё одному союзнику."),
    "s050_152_430": ("e17db04e0790b81b6c105ac45a6bc8f339dc4030bdd32c13eb5d9d6d281b7473", "Все мои союзники прошли броневую эволюцию!\nПрими этот знак моей благодарности!"),
}
for row_id, (expected_hash, replacement) in PEGASMON.items():
    add("message/s050_152.mbe/000_Sheet1.csv", row_id, expected_hash, replacement)

for row_id, expected_hash, replacement in [
    ("s050_152_1001", "974856d754b955ddc039491cbb30275f42e8ce97eab8672aeaca82d023d39d77", "{next}Дигиментал света."),
    ("s050_152_1010", "e0de456788a660f1b3ea3d6a076158a883a28ae889bcfb53f583842f2cccca6f", "{next}Дигиментал дружбы."),
    ("s050_152_1100", "95171981549e83a5c53224ebc629e7f540874c4d0db14866bd01bf66fce056ab", "{next}Дигиментал мужества."),
    ("s050_152_2011", "974856d754b955ddc039491cbb30275f42e8ce97eab8672aeaca82d023d39d77", "{next}Дигиментал света."),
    ("s050_152_2012", "e0de456788a660f1b3ea3d6a076158a883a28ae889bcfb53f583842f2cccca6f", "{next}Дигиментал дружбы."),
    ("s050_152_2101", "974856d754b955ddc039491cbb30275f42e8ce97eab8672aeaca82d023d39d77", "{next}Дигиментал света."),
    ("s050_152_2102", "95171981549e83a5c53224ebc629e7f540874c4d0db14866bd01bf66fce056ab", "{next}Дигиментал мужества."),
    ("s050_152_2110", "e0de456788a660f1b3ea3d6a076158a883a28ae889bcfb53f583842f2cccca6f", "{next}Дигиментал дружбы."),
    ("s050_152_2111", "95171981549e83a5c53224ebc629e7f540874c4d0db14866bd01bf66fce056ab", "{next}Дигиментал мужества."),
    ("s050_152_3111", "974856d754b955ddc039491cbb30275f42e8ce97eab8672aeaca82d023d39d77", "{next}Дигиментал света."),
    ("s050_152_3112", "e0de456788a660f1b3ea3d6a076158a883a28ae889bcfb53f583842f2cccca6f", "{next}Дигиментал дружбы."),
    ("s050_152_3113", "95171981549e83a5c53224ebc629e7f540874c4d0db14866bd01bf66fce056ab", "{next}Дигиментал мужества."),
]:
    add("message/s050_152.mbe/000_Sheet1.csv", row_id, expected_hash, replacement)

# Other Digi-Egg terminology in the same game UI.
add("message/d02.mbe/000_Sheet1.csv", "f_d0202_0760_0012",
    "4f08a08fc576f5ef08be3ab2cdd05c696e606a90ae3e34ef2b55cbb10fcbd268",
    "[Передать Дигиментал.]")
add("message/d02.mbe/000_Sheet1.csv", "f_d0202_0770_0012",
    "2388af768c072f78ffb37fb5d54d066d644eb8190bb3dd488d0fe3ee7a0820b1",
    "Я хочу узнать больше о Дигиментале.")
add("message/s110_101.mbe/000_Sheet1.csv", "s110_101_400",
    "6d18a06f27d546484c11f80a16811a245dc2625f32219606f334acfcc376ef16",
    "Итак... Я слышал, что в этом мире Дигименталы могут обрабатывать\n"
    "только в Факториальной области.")

# Coromon response menu and the immediately connected calques.
CORONAMON = {
    "s080_059_040": ("3c5d4bbdf505a6c50aecd741d04130cdd1dbdb055d63d6bfde4a23582383c079", "{next}У тебя всё получится!"),
    "s080_059_041": ("4a3a4b9284f567a2a28e9346bec13eb6640e335cf8e23621a5b539e8a284c9f7", "{next}И в чём же ты его превзойдёшь?"),
    "s080_059_042": ("5b328e23f65b36756aa9b1c34c302f075c9acbf6182a107b3860f2b7a50cc970", "{next}Ты-то сам летать умеешь?"),
    "s080_059_060": ("bb5e26b102a796f6aa8c6199ffa2629af44d6c0c2d24e1b519b05776b82f1ad3", "Я докажу, что могу тренироваться усерднее Блимпмона!\nНу, то есть..."),
    "s080_059_070": ("2cb1134f1f17bb65693ea1decb29d0afcab4ac961bdc9dd04664dff602bdb89b", "Не это я имел в виду! Я скорее о том, что... ну, понимаешь..."),
    "s080_059_080": ("cbc2f145f4c9cdaa62ab180b50dc5690dc4437878fb8a434fc2676859e427e70", "Теперь я могу отправиться в Космическую область! Тренировки\nв легендарном месте сделают меня ещё сильнее!"),
    "s080_059_090": ("008e5cb6c01e7a2e9b89e3a4f2ed3e9442aa3a8d726e389da9e15ca81e0fa32f", "{next}Хочешь стать ещё сильнее?"),
    "s080_059_092": ("54469df602c5156b323f752875225bb1d2bc673c8711a518d23ebba3172f3f6b", "{next}Ты и сейчас хорош."),
    "s080_059_100": ("9a186a183447ba4d42e357627fdb174842d76c89f2c31680a812cc5bcda4d2bf", "Да! То, что я от вас отстал, — просто случайность!"),
}
for row_id, (expected_hash, replacement) in CORONAMON.items():
    add("message/s080_059.mbe/000_Sheet1.csv", row_id, expected_hash, replacement)


def digest(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def read_document(path: Path) -> tuple[list[list[str]], str, bool]:
    raw = path.read_bytes()
    encoding = "utf-8-sig" if raw.startswith(b"\xef\xbb\xbf") else "utf-8"
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.reader(handle))
    physical = raw.removeprefix(b"\xef\xbb\xbf").splitlines()
    quote_all_after_header = len(physical) > 1 and physical[1].startswith(b'"')
    return rows, encoding, quote_all_after_header


def write_document(path: Path, rows: list[list[str]], encoding: str, quote_all: bool) -> None:
    with path.open("w", encoding=encoding, newline="") as handle:
        if quote_all:
            csv.writer(handle, lineterminator="\n").writerow(rows[0])
            csv.writer(handle, lineterminator="\n", quoting=csv.QUOTE_ALL).writerows(rows[1:])
        else:
            csv.writer(handle, lineterminator="\n").writerows(rows)


def main() -> None:
    if len(UPDATES) != len({(p, r, k, c) for p, r, k, c, _, _ in UPDATES}):
        raise SystemExit("Duplicate update target")

    documents: dict[tuple[str, str], list[list[str]]] = {}
    formats: dict[tuple[str, str], tuple[str, bool]] = {}
    dirty: set[tuple[str, str]] = set()
    changed = current = 0

    for package, relative, row_id, column, expected_hash, replacement in UPDATES:
        marker = (package, relative)
        if marker not in documents:
            rows, encoding, quote_all = read_document(CSV_ROOT / package / relative)
            documents[marker] = rows
            formats[marker] = (encoding, quote_all)
        matches = [row for row in documents[marker] if row and row[0] == row_id]
        if len(matches) != 1 or len(matches[0]) <= column:
            raise SystemExit(f"Missing or ambiguous target {package}:{relative}:{row_id}")
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

    print(f"Guarded targets: {len(UPDATES)}")
    print(f"Changed: {changed}")
    print(f"Already current: {current}")
    print(f"Files written: {len(dirty)}")


if __name__ == "__main__":
    main()

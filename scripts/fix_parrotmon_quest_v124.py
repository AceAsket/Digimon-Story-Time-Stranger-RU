#!/usr/bin/env python3
"""Polish the Solarmon/Parrotmon-plume quest and unify its terminology."""

from __future__ import annotations

import csv
from pathlib import Path

from fix_reported_sidequests_v120 import digest, read_document, write_document


ROOT = Path(__file__).resolve().parents[1]
CSV_ROOT = ROOT / "csv"
DATASET = ROOT / "exports" / "dynamic_gender_confirmed_variants_v066.csv"
NEUTRALIZED_IDS = {"s050_042_0270", "s050_042_0280"}

# package, relative CSV, row id, text column, expected SHA-256, replacement
UPDATES: list[tuple[str, str, str, int, str, str]] = [
    ("patch_text01", "message/s050_042.mbe/000_Sheet1.csv", "s050_042_0030", 2,
     "85f0265fae62a64f06a34125656805c41e5f9ac658ee0c7809e96ec8280fe17e",
     "Я не Хагурумон! Только не надо\nменя с ним путать!"),
    ("patch_text01", "message/s050_042.mbe/000_Sheet1.csv", "s050_042_0040", 2,
     "0e67795abd1a36b7f3d33dfcd3649d917eb137db843afc6c6fc3005115184cdc",
     "Я не перекрашенный Хагурумон!\nПрисмотрись — я совсем другой!"),
    ("patch_text01", "message/s050_042.mbe/000_Sheet1.csv", "s050_042_0045", 2,
     "f6fef739412231426d14a4a45f6c407d11b4fbd94c458e8fb6c4eeb76592fcd9",
     "*вздыхает* В таком виде нельзя показываться мастеру.\nЧто же делать?.."),
    ("patch_text01", "message/s050_042.mbe/000_Sheet1.csv", "s050_042_0050", 2,
     "09768c7011cd7a4ddeaef8bfd127a640aca7d43d61d27d3d3e197be91aec343b",
     "Как грубо! Я вообще-то Солармон,\nдоверенный помощник мастера Беармона!"),
    ("patch_text01", "message/s050_042.mbe/000_Sheet1.csv", "s050_042_0060", 2,
     "d9c812df02c0f0082adf450ca12fe745ed8e7eb4040c10ec93f283b5b1f75e0d",
     "...Но я ещё не оправдал ожиданий мастера.\nУ меня ничего не получается!"),
    ("patch_text01", "message/s050_042.mbe/000_Sheet1.csv", "s050_042_0070", 2,
     "e837ab0898e242efd04a84464162a957242020a448171dcdc18cd57594195b02",
     "...Постой. Нельзя же торчать здесь вечно.\nМне нужно в Центральную башню!"),
    ("patch_text01", "message/s050_042.mbe/000_Sheet1.csv", "s050_042_0080", 2,
     "fbb09e9f8815c5d67cb3f4fda16dc0f9bda699445fa9f2b867c0edd0ab95b373",
     "И вы тоже сюда пришли? Тише! Не так громко."),
    ("patch_text01", "message/s050_042.mbe/000_Sheet1.csv", "s050_042_0091", 2,
     "a70237f381cf48bdfee28c24be620d21012e3e1eab1db402a3ddba291203d99f",
     "{next}Ты нашёл перо Пэрротмона?"),
    ("patch_text01", "message/s050_042.mbe/000_Sheet1.csv", "s050_042_0100", 2,
     "41f31b7ce20a3e343a681e89895ec4c497e58bd685c3dad045f882d88a3d29d4",
     "Я-я не прячусь! Любое дело\nнужно начинать с наблюдения."),
    ("patch_text01", "message/s050_042.mbe/000_Sheet1.csv", "s050_042_0110", 2,
     "20c887f31d2ff35999c7dc637b51e0e900c0ed8a7bd7022fb5fec7fa7af12f31",
     "П-подумаешь... Для меня это пустяк!\nСкоро найду."),
    ("patch_text01", "message/s050_042.mbe/000_Sheet1.csv", "s050_042_0120", 2,
     "2e6c6ad1a45309694cf23011cb7d8eb37c9b5fa1f95ab52867b6d9d5f2cfbe7e",
     "Э-э... Ты о чём? Я вовсе не боюсь!"),
    ("patch_text01", "message/s050_042.mbe/000_Sheet1.csv", "s050_042_0130", 2,
     "0b3e92e92cd9066c2891d9e466f6b3086f741ebc621186dd702fce7b65059718",
     "Я пришёл за пером Пэрротмона\nпо приказу мастера Беармона."),
    ("patch_text01", "message/s050_042.mbe/000_Sheet1.csv", "s050_042_0140", 2,
     "7521b4df682a6ba8da33759019d455ea2d0680256d439a4bf4a00e11a4097034",
     "Видишь, сколько вокруг блестящих штуковин?\nСреди них наверняка есть перо Пэрротмона."),
    ("patch_text01", "message/s050_042.mbe/000_Sheet1.csv", "s050_042_0150", 2,
     "3514c23ab3cd305c70744500e7edb3ad23ac89f5deffcc11f87bd40c9b7ce183",
     "Но, как назло, явились Титаны.\nПоможешь найти перо?"),
    ("patch_text01", "message/s050_042.mbe/000_Sheet1.csv", "s050_042_0180", 2,
     "1a4e076492c1fa1f767e894476826fc0f2f7071cf870474bf004267d2f447f64",
     "Нет, не все. Среди них полно всякого другого хлама."),
    ("patch_text01", "message/s050_042.mbe/000_Sheet1.csv", "s050_042_0185", 2,
     "9dac69bd0181081abcbe5c1dc7f887d2d5644b7c093d602787380d3ae32dee61",
     "Ничего не поделаешь. Возвращайся,\nкогда закончишь свои дела!"),
    ("patch_text01", "message/s050_042.mbe/000_Sheet1.csv", "s050_042_0190", 2,
     "00c0ad81037247dbe96fa0c2537fd5c24a9997cabcf99e96e99e9cd36cf329c8",
     "Ладно, перо ищешь ты. Берегись Титанов,\nа я постою на страже."),
    ("patch_text01", "message/s050_042.mbe/000_Sheet1.csv", "s050_042_0200", 2,
     "5969c928f8e989506ba8d983d45378639a3464120ef96fbfc33caf1b888b2297",
     "Ч-что? Я не боюсь! Я останусь здесь!\nСтоять на страже — тоже важная работа!"),
    ("patch_text01", "message/s050_042.mbe/000_Sheet1.csv", "s050_042_0210", 2,
     "7f33adb3096bc8c9f20cde61326e64ce8016dafef909e51bfca71f944f23a615",
     "Ну же, меньше разговоров, больше дела.\nОбязательно найди перо!"),
    ("patch_text01", "message/s050_042.mbe/000_Sheet1.csv", "s050_042_0220", 2,
     "717cd095aaff38ec3d07ed701e9fda9eb1a61e92c2175e03d7f10c0ce6ab946d",
     "Это перо Пэрротмона... Нет, всего лишь обёртка\nот конфеты в форме пера. В мусор!"),
    ("patch_text01", "message/s050_042.mbe/000_Sheet1.csv", "s050_042_0230", 2,
     "459b7d80617aa724f45438c19251f849cc242fe7a2f49c814e8b96ed5be24662",
     "Это перо Пэрротмона... Нет, всего лишь\nпохожая на него перьевая ручка!"),
    ("patch_text01", "message/s050_042.mbe/000_Sheet1.csv", "s050_042_0240", 2,
     "f0a034f95edea32cfa5f79c3bc1f16442745064e23ca25416a6a7111882c7e0f",
     "Это перо Пэрротмона... Нет, всего лишь\nпохожее перо другого дигимона!"),
    ("patch_text01", "message/s050_042.mbe/000_Sheet1.csv", "s050_042_0250", 2,
     "76d576338021f92fac7358803443d3d13ea6ab465c1a92b6b5561ed27cf1b06d",
     "Это перо Пэрротмона... Нет, просто помёт!\nПоблизости что, туалета не было?"),
    ("patch_text01", "message/s050_042.mbe/000_Sheet1.csv", "s050_042_0260", 2,
     "9b6fbc8b867100dde95e1ab56cd216af384aea98f8bf163423d58841a9de4daf",
     "На земле что-то лежит."),
    ("patch_text01", "message/s050_042.mbe/000_Sheet1.csv", "s050_042_0270", 2,
     "066f257c6e53f6a58bf660120f144897fefc3f215dc720657d753e3853ce7e06",
     "Перо Пэрротмона у тебя?! Отлично, давай сюда."),
    ("patch_text01", "message/s050_042.mbe/000_Sheet1.csv", "s050_042_0275", 2,
     "01625ca50f7db472cb14f2a3df9f9a0f052666ceeba3ffcb4b34a9c5520b6706",
     "А взамен отдам тебе одну из своих находок.\nВыгодная сделка, правда?"),
    ("patch_text01", "message/s050_042.mbe/000_Sheet1.csv", "s050_042_0280", 2,
     "3dba247ed146b98ec23524e966ff7c468b3e6d6d9e43cc972d70bd9feb806c68",
     "Ну что, хорошо, что мы объединились?\nОсновную работу сделал я, но твою помощь тоже не забуду."),
    ("patch_text01", "message/s050_042.mbe/000_Sheet1.csv", "s050_042_0290", 2,
     "ce56d23a6a2395188f23de3207718eb78e4d499c05f14ac7d886144c4ef0cf94",
     "Ладно, пойду доложу мастеру. До встречи!"),
    ("patch_text01", "message/s050_042.mbe/000_Sheet1.csv", "s050_042_0300", 2,
     "90d95826849e3663a15482580c82d023b4b7c7bc32d3b0abad649d65364f3522",
     "Хе-хе-хе! Мы добыли перо Пэрротмона\nи вдобавок обрели бесстрашного последователя."),
    ("patch_text01", "message/s050_042.mbe/000_Sheet1.csv", "s050_042_0310", 2,
     "f1e69c67d31828a817de449b80fa60ad5554e26e795f3b50a6404ac7159e15c4",
     "Ну что, братец, дела идут в гору!"),
    ("patch_text01", "message/s050_042.mbe/000_Sheet1.csv", "s050_042_0320", 2,
     "7eb31c175a633ed4174885f39190348db144744352a02f28c5ed85fac88860c2",
     "Точно! Пора продолжить охоту за украшениями\nПлатинаНумемона в канализации!"),
    ("patch_text01", "message/s050_042.mbe/000_Sheet1.csv", "s050_042_0340", 2,
     "50bb1f4da5c01b0a12449d3c913610fd43c3fb84dd9878b4c922d79ee12e4e16",
     "Ветер на нашей стороне! Вперёд!"),
    ("patch_text01", "message/s050_042.mbe/000_Sheet1.csv", "s050_042_0350", 2,
     "ae4ade8c490b42ed89876cdd741abf6d7a1514346491646a55e9c3f16de611c4",
     "Я последую за тобой хоть на край Илиады, мастер!"),
    ("patch_text01", "message/s050_042.mbe/000_Sheet1.csv", "s050_042_0360", 2,
     "07edeb20a1af3872ee78e0d35fe4e9964970b9e6db72dc44bac816b4d1bcc77f",
     "...Только без шуток, ладно?"),
    ("patch_text01", "message/s050_042.mbe/000_Sheet1.csv", "s050_042_0370", 2,
     "d94ede53b587abc41fe1543bb2d508eb6b6d64e2bc29705a0dd8c9746c536755",
     "Ну что, с делами покончено? Тогда ищем перо!"),
    ("patch_text01", "message/s050_042.mbe/000_Sheet1.csv", "s050_042_0390", 2,
     "19243d61178ef0a6fbe0df31e294eae61ff26707e2e4c268c85b6318f39730cf",
     "Понятно. Так не терпится заручиться моей помощью?\nЧто ж, выбора у меня нет!"),
    ("patch_text01", "message/s050_042.mbe/000_Sheet1.csv", "s050_042_0400", 2,
     "f855e45e82b3a2d41599e23e6f22e2461e7b13101685c3d19343a4a789904792",
     "Откуда столько дел? Возвращайся,\nкогда освободишься, только скорее!"),
    ("patch_text01", "text/item_explanation.mbe/000_Sheet1.csv", "765", 1,
     "a4e1f49d480b632f46fcb9afbd90d5af9d99f8a97ccd989c8ccb6eae97426b2a",
     "Перо, выпавшее у Пэрротмона.\nПотрёпанный вид напоминает о суровых битвах."),
    ("patch_text01", "text/quest_step.mbe/000_Sheet1.csv", "42020", 1,
     "47c63888db65b7a70cf5a650e7e0daf98f856470eabb6de28f4d2bc7ff157b64",
     "Поговори с Солармоном на вершине башни."),
    ("patch_text01", "text/quest_step.mbe/000_Sheet1.csv", "42030", 1,
     "b62f38f9973f4ca9c9baaaae92ac4c40d2fe106fcb0f74fd886b9bca90399355",
     "Найди перо Пэрротмона."),
    ("patch_text01", "text/quest_step.mbe/000_Sheet1.csv", "42040", 1,
     "f9fa3bdd8406633b48b6a6695e35830a142849dc0fb75a44dd4d1676cea79af8",
     "Отдай перо Солармону."),
    ("patch_text01", "text/quest_outline.mbe/000_Sheet1.csv", "42", 1,
     "8728d3819a2f3fcf5b5087a7870e952772edb1516d1b4ace1b79a1e84ab0cf00",
     "Титаны мешают мне добыть перо Пэрротмона!\nМожет, стоит съездить в центр города\nи пересмотреть план."),
    ("patch_text01", "message/d02.mbe/000_Sheet1.csv", "f_d0208_0050_0060", 2,
     "85132c044441d8f674fbbdd2a92a49772ee4f5b01d21e9b521c1daf766465b68",
     "Ах да... По приказу мастера\nя пытался добыть перо Пэрротмона..."),
    ("patch_text01", "message/s050_043.mbe/000_Sheet1.csv", "s050_043_030", 2,
     "8707f25c2cd65a9fe3a332a770fc87f01db3d81c82364ee1445463cf9b656d0c",
     "Это тот, кто принёс мне перо Пэрротмона.\nВпечатляет, правда?"),
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

    dataset_rows, dataset_encoding, dataset_quote_all = read_document(DATASET)
    header = dataset_rows[0]
    base_index = header.index("base_id")
    found = [row for row in dataset_rows[1:] if row[base_index] in NEUTRALIZED_IDS]
    found_ids = {row[base_index] for row in found}
    if found and (found_ids != NEUTRALIZED_IDS or len(found) != len(NEUTRALIZED_IDS)):
        raise SystemExit(f"Unexpected dynamic-gender rows: {sorted(found_ids)}")
    if found:
        dataset_rows = [
            header,
            *(row for row in dataset_rows[1:] if row[base_index] not in NEUTRALIZED_IDS),
        ]
        write_document(DATASET, dataset_rows, dataset_encoding, dataset_quote_all)

    print(f"Targets: {len(UPDATES)}")
    print(f"Changed: {changed}")
    print(f"Already current: {current}")
    print(f"Files written: {len(dirty)}")
    print(f"Neutralized runtime rows removed: {len(found)}")


if __name__ == "__main__":
    main()

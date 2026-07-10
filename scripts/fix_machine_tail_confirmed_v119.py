#!/usr/bin/env python3
"""Apply source-checked P1/P2 machine-translation tail fixes."""

from __future__ import annotations

import csv
import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CSV_ROOT = ROOT / "csv"

# This extracted table intentionally keeps every data field quoted while the
# header stays minimally quoted. Preserve that style so a one-row edit does
# not turn into a whole-file formatting diff.
QUOTE_ALL_AFTER_HEADER = {
    ("patch_text01", "message/m200.mbe/000_Sheet1.csv"),
}

# package, relative CSV, row id, text column, expected SHA-256 (or accepted
# SHA-256 values for a reviewed follow-up), replacement
UPDATES = [
    ("patch_text01", "text/buff_message.mbe/000_Sheet1.csv", "23", 1,
     "d5501f41cc75cf6c69cad2ab1901ee223351779c1b2324f28d087ce1767ccbcd",
     "{d0}: {is28}{image(ui_icon_btlStatus_014)} {fc9ОЗ} теперь восстанавливаются каждый ход!"),
    ("patch_text01", "text/buff_message.mbe/000_Sheet1.csv", "24", 1,
     "48b5bbb40a7b6d0420a9532cecbae5674c3114875f84debecfa73af211ab5c38",
     "{d0}: {is28}{image(ui_icon_btlStatus_015)} {fc9ОС} теперь восстанавливаются каждый ход!"),
    ("patch_text01", "text/buff_message.mbe/000_Sheet1.csv", "100023", 1,
     "d5501f41cc75cf6c69cad2ab1901ee223351779c1b2324f28d087ce1767ccbcd",
     "{d0}: {is28}{image(ui_icon_btlStatus_014)} {fc9ОЗ} теперь восстанавливаются каждый ход!"),
    ("patch_text01", "text/buff_message.mbe/000_Sheet1.csv", "100024", 1,
     "48b5bbb40a7b6d0420a9532cecbae5674c3114875f84debecfa73af211ab5c38",
     "{d0}: {is28}{image(ui_icon_btlStatus_015)} {fc9ОС} теперь восстанавливаются каждый ход!"),
    ("patch_text01", "message/d14.mbe/000_Sheet1.csv", "f_d1401_0050_0020", 2,
     "6f334c5b8fd7cef357a4819d4c4503791fc535456a33c1a6cf925ef393efc94d",
     "Не хочу больше смотреть на эту драку. Посмотрим,\nкуда можно подняться на лифте."),
    ("patch_text01", "message/d09.mbe/000_Sheet1.csv", "f_d0906_0130_0010", 2,
     "9f37a9da221e8970dcb919d1fcea4913bddf9f88a8ed3e90b930f42ed4561fde",
     "А теперь отправляйтесь к тем воротам."),
    ("patch_text01", "message/s110_093.mbe/000_Sheet1.csv", "s110_093_412", 2,
     "bb7e7914bf0473c50551e40a3c410a48f367096e082980774b417501977d90f0",
     "Тебе есть чем гордиться. Энбаррмон удостаивает такой чести\nлишь тех, кого считает достойными."),
    ("patch_text01", "message/s110_093.mbe/000_Sheet1.csv", "s110_093_414", 2,
     "76a478b1431fd263533792f5a0c6d9a9095c3b1948168a90e57b7e7516924539",
     "Это доказательство твоей силы. Смело садись на скакуна."),
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "common022_1_replay", 2,
     "dd4baddc256fc3db9a8b6b3ede8511699e3250c0f40bb767f1d1eea755b38e7f", "Точно."),
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "exbui_001_1_reaction_char_XV-MON", 2,
     "d4d50d2a4d18cc66e9c108f543ca36c3a5d17747585fa56a9f06368924256c7a",
     "Разве что по сравнению с тем, каким я был до эволюции.\nНо мне ещё есть куда расти!"),
    ("patch_text01", "message/s010_180.mbe/000_Sheet1.csv", "s010_180_180", 2,
     "dd4baddc256fc3db9a8b6b3ede8511699e3250c0f40bb767f1d1eea755b38e7f", "Да."),
    ("patch_text01", "text/digimon_profile.mbe/000_Sheet1.csv", "digimon_0699_profile", 1,
     "7dc39b507df53cea032b795835e833878f2882df3a963114a3326162e5c4adc1",
     "Дюрамон — Ультимативный Дигимон, уже увидевший\n"
     "свою конечную цель и сделавший первый шаг к ней. Он не\n"
     "знает, что ждёт его впереди, но рассечёт своими клинками\n"
     "любое препятствие: их закалили бесчисленные тренировки.\n"
     "В форме оружия огромный меч за его спиной обретает\n"
     "несравненную мощь. Особый приём Дюрамона — «Ослепление»:\n"
     "луч из груди наносит колоссальный урон и оставляет на цели\n"
     "клеймо с числом 20."),
    ("patch_text01", "text/digimon_profile.mbe/000_Sheet1.csv", "digimon_0234_profile", 1,
     ("1c5a2e65afd9564ec8f6a48b1950df6b96a0945bf529dd78aab6ede33bbfde77",
      "ec82bc105c0020a21b55c8b517650e7382cc6b1bc129fac69700310fb6db059a"),
     "Беармон — зверь-дигимон, похожий на маленького медведя\n"
     "и носящий фирменную кепку козырьком назад. Иногда он робок,\n"
     "но легко ладит с другими дигимонами, необычайно отважен\n"
     "и вынослив. Вступив в бой, Беармон не сдаётся,\n"
     "сколько бы ударов ни пропустил, поэтому на него всегда можно\n"
     "положиться. Его кулаки настолько сильны, что их приходится\n"
     "обматывать кожаными ремнями, иначе он сам пострадает от\n"
     "собственных ударов. Особым приёмом «Медвежий Кулак» Беармон\n"
     "бросается на противника и со всей силы бьёт его в грудь."),
    ("patch_text01", "message/d05.mbe/000_Sheet1.csv", "f_d0552_0010_0010", 2,
     ("101bf3b8b08b0e0c67f1f4be8e6ccd1afc8c128909b0b3d77897d50afc1857e6",
      "591ccda9d4fb736fb0e0b795084bbfe81dc8bb4ea69ecb10fdc45450a759fc94"),
     "Никакой реакции, но от него веет угрозой —\nсловно он вот-вот зашевелится."),
    ("patch_text01", "message/d07.mbe/000_Sheet1.csv", "f_d0702_0070_0010", 2,
     "9818839fa9f5598d4aecca565b989c31824cb86f60c70ac8f0df8ee320116ca5", "...Слишком поздно. Он уже мёртв."),
    ("patch_text01", "message/m140.mbe/000_Sheet1.csv", "m140_070_090", 2,
     "a01c4bcb08d3f22190b13c4e65db5c2ebf893eb754ff4da6a494ef5ba2dc5d57", "Никто не отвечает. Что происходит?!"),
    ("patch_text01", "message/battle.mbe/000_Sheet1.csv", "1200020109", 2,
     "7dcc604395a350487d717fb88b57914d1f7055138e015f8ba868f2f89ea257e8", "Так вот как всё закончится... Какой позор!"),
    ("patch_text01", "message/d02.mbe/000_Sheet1.csv", "f_d0201_0620_0030", 2,
     "11fcbc9c0aed14e10e4a23121d52d6c21bdd7f7d5194dc467d3e4e3d33285a61",
     "Может, теперь всё не так уж плохо — раньше здесь\nтворилось настоящее безумие?"),
    ("patch_text01", "message/m080.mbe/000_Sheet1.csv", "m080_110_001", 2,
     ("66b769098881782866d7c0a4355074f5967ff995a09d443ebc4ffaec4151f272",
      "4ac79d685c5c06400ed6f1ff8c353c4c44f388997f3b564e953bf8bbc284d06f"),
     "*тяжело дышит*"),
    ("patch_text01", "message/m170.mbe/000_Sheet1.csv", "m170_210_201", 2,
     "0b0924fbae11bde99e396e254194a40ce3638a6bce459077bf3a29cb7030c6ab", "Если пострадали люди, тогда... {next}"),
    ("patch_text01", "message/rumor_npc.mbe/000_Sheet1.csv", "r_d0407_0020_0050", 2,
     "481f4741d0131e0615bcf8a346995f595c459b1a2e81005e53a08e06e2bc838e", "Так-так..."),
    ("patch_text01", "text/info_message.mbe/000_Sheet1.csv", "1108030050", 1,
     "5d3755a6d8ca919f8b2f265030586822116a5dd40bb5a53d16e2647146a20058", "...Похоже, это не помогло."),
    ("addcont_02_text01", "message/d220.mbe/000_Sheet1.csv", "d220_080_130", 2,
     "c25d3ca2180f5606aabc0302832c6e51394a9c075d32c2c6493a873f84efc5c9",
     "Как ты и сказал, пора говорить кулаками.\nНо эта беседа тебе не понравится."),
    ("addcont_03_text01", "message/d340.mbe/000_Sheet1.csv", "d340_022_100", 2,
     ("30342a74fb7e523f794c6a3c00b0ad5b1931873470a6369cbe434c85f6256b20",
      "d604f9a5afb9017214e7802207c5e8113b57a0c9f4bb56fc64b755af389a1ae9"),
     "Как думаешь, почему мы сопровождали тебя всё это время?\n"
     "Твои слова и поступки доказали, что ты ничем от нас не отличаешься."),
    ("addcont_03_text01", "message/d340.mbe/000_Sheet1.csv", "d340_023_020", 2,
     "15c8aac1e7aa9796e04b115ee467411c74bd986d61fb561326d12d64d273d968",
     "Я слышал все ваши голоса.\nВаши разрозненные сердца... слились воедино."),
    ("patch_text01", "message/m070.mbe/000_Sheet1.csv", "m070_030_120", 2,
     "ade06d291a22b18829cfdaadc4adc6b9c0a5c2a289aa8b8393628bf3aec86f0f",
     "Если кто и должен быть благодарен, так это вы, ребята. Разве не так?"),
    ("patch_text01", "message/m180.mbe/000_Sheet1.csv", "m180_040_150", 2,
     "582fd6775982c0ad581402273f6cbb229aef5bc49fb853d62f7b5e9c2e5a4c80",
     "Вы и представить не можете, какой я была до встречи с вами..."),
    ("patch_text01", "message/m180.mbe/000_Sheet1.csv", "m180_060_250", 2,
     "9d2fbadc99ad8e01cfb7e04b9312c9425140ed3214ca1cc1aa789f901b77761c",
     "Мне нужна ваша помощь. Вы пойдёте со мной к Мировому Древу?"),
    ("patch_text01", "message/m410.mbe/000_Sheet1.csv", "m400_050_070", 2,
     "69dd093b56540ef9f1f74e5f19700cb87403857c49039c3bfc4c29477df232e4",
     "Но вы двое не зазнавайтесь... Я пока не собираюсь от вас отставать!"),
    ("patch_text01", "text/digitter_message.mbe/000_Sheet1.csv", "hazama_00_030_7", 1,
     "bbb394e9619cbbd32bdfcfd2ff371cea6b739639a11baf3557a9535c8cd2ac82",
     "Пройди одну игру — и я подарю тебе кое-что особенное,\nчто припас заранее."),
    ("patch_text01", "message/d04.mbe/000_Sheet1.csv", "f_d0407_0020_0030", 2,
     "a05823565d05a67c0ecad994dabb1dc52dff34805530f942f0c64eda7bfd89b6",
     "Сайренмон? Понятно... Тогда святилище я вверяю тебе.\nА вы можете пройти в лес."),
    ("patch_text01", "message/d06.mbe/000_Sheet1.csv", "f_d0608_0010_0030", 2,
     "bef469766ec31ea6e348e9b73b38e9cb70734dd4528c3497b76f221afd858bc3",
     "Тогда я полагаюсь на тебя, Эгиомон.\nИ на вас тоже, дети человеческие..."),
    ("patch_text01", "message/d12.mbe/000_Sheet1.csv", "f_d1205_0020_0020", 2,
     "b719e456419eb41d3b9ddba39798550c675d99da7b998d03df372a6ffb4ca405", "А, вот и вы! Рад, что все целы!"),
    ("patch_text01", "message/m100.mbe/000_Sheet1.csv", "m100_060_060", 2,
     ("48f11ea093ae17739d0cf1a1599edb8fef5f8320d17308bf0615192756ed39b5",
      "e18035e456b20cef428222490f99f615b2b2ff25b50909550dd36b55110c553b"),
     "Люди нам не соперники! Не нравится — попробуйте что-нибудь сделать!"),
    ("patch_text01", "message/m160.mbe/000_Sheet1.csv", "m160_060_240", 2,
     "10bfc992ee982b6736c29501b4abadf7460386e5960169d88f962df77a4ad5f2",
     "Я полагаюсь на тебя, Великий Хранитель Эгиомон.\nИ на вас, дети человеческие..."),
    ("patch_text01", "message/d09.mbe/000_Sheet1.csv", "f_d0903_0045_0050", 2,
     "92f1b40d57021be8d0f7f46e038317d969587bc6ac7255f294862f76d5e61d81",
     "Теперь осталось отнести плод лорду Бахусмону—"),
    ("patch_text01", "message/d09.mbe/000_Sheet1.csv", "f_d0904_0250_0070", 2,
     "2363b6d93f743a21f0e8050eda251b130c2b3324b520e1ca9f2f8c8754e81a5e",
     "Хватит болтать! Оставь остальное нам!"),
    ("patch_text01", "message/m120.mbe/000_Sheet1.csv", "m120_100_210", 2,
     ("5e313d4505b8b8bd76167e4f22c37306ca940c05fad52555c7b91127b086479e",
      "452b4f21480ecb51cc63288309f2477fc7b7686196ad3fd9707e765b175d6836"),
     "Кто дружит со слабаком, тот и сам слабак! Слабак!"),
    ("patch_text01", "text/digitter_message.mbe/000_Sheet1.csv", "hazama_99_010_1", 1,
     "a80d4199ec884d8e737d8712e6cf821488cc384e0ccf34518ce27f975931b7df",
     "День 1 после прибытия.\nЯ встретил существ, которых называют «дигимонами»."),
    ("patch_text01", "text/digimon_profile.mbe/000_Sheet1.csv", "digimon_0001_profile", 1,
     "cb511f2d51885600280bbe0b6f4438fea6d87fc22e07cd5876129f4a8a1170ad",
     "Кукольный дигимон, спрятавшийся внутри плюшевого\n"
     "Тиранномона. Почему этот загадочный дигимон выбрал\n"
     "именно такую игрушку, неизвестно: вероятно, она просто\n"
     "оказалась ближе всего. Как бы то ни было, плюшевый\n"
     "Тиранномон обладает всей атакующей и защитной силой\n"
     "Мондзаэмона, поэтому обычным дигимонам с ним не\n"
     "сравниться. Однако, как и Мондзаэмон, без кукловода\n"
     "он остаётся лишь украшением. Его особый приём —\n"
     "«Милая атака», исходящая от очаровательного тела."),
    ("patch_text01", "text/digimon_profile.mbe/000_Sheet1.csv", "digimon_0045_profile", 1,
     "f04ef39c78a97ae3e6f4db63f6733141d4bf2f808516e4eb458d27948d63e488",
     "Божественный дигимон, считающийся воплощением системы,\n"
     "управляющей временем. Течение времени в Цифровом мире\n"
     "непостоянно: столкновения могучих дигимонов и\n"
     "катаклизмы способны вызывать пространственно-временные\n"
     "искажения. В таких случаях появляется Хрономон, чтобы\n"
     "восстановить ход времени. После исправления искажения\n"
     "исчезает даже сам факт его появления, поэтому никто\n"
     "никогда не видел этого дигимона. О его существовании\n"
     "говорят лишь редкие легенды. Особые приёмы Хрономона —\n"
     "«Священная Вспышка», святое пламя, стирающее из бытия\n"
     "злонамеренно искажающих пространство-время, и\n"
     "«Урожай Хроноса»: неблокируемый удар крыльями-клинками,\n"
     "вырезающий врага из самой ткани времени и пространства."),
    ("patch_text01", "text/digimon_profile.mbe/000_Sheet1.csv", "digimon_0046_profile", 1,
     "47a940bc89ca20414bc15e6d194b46ed79e61e2d8149a702b3748a8dfd4df504",
     "Хрономон: Режим разрушения — форма, которую Хрономон\n"
     "принимает, утратив контроль. Этот легендарный монстр\n"
     "отрёкся от обязанности хранить порядок\n"
     "пространства-времени и восстал против самой системы,\n"
     "управляющей временем. Когда Хрономон исправлял\n"
     "искажение, всё зло Цифрового мира одновременно хлынуло\n"
     "в него и заставило обезуметь, словно от заражения\n"
     "вирусом. Используя изначальную власть над временем,\n"
     "он взламывает запечатлённые в Цифровом мире воспоминания\n"
     "и загружает в себя множество навыков для неистовых атак.\n"
     "Даже в этом состоянии Хрономон сохраняет «Священную\n"
     "Вспышку», сжигающую врагов без остатка.\n"
     "«Хроно-деволюция» превращает временные данные Цифрового\n"
     "мира в энергию, которая мгновенно старит коснувшегося\n"
     "её и обращает его данные в пыль."),
    ("patch_text01", "text/digimon_profile.mbe/000_Sheet1.csv", "digimon_0183_profile", 1,
     "5d73429c39d925b89b96d6dcc602b360de6f37b29cd05899da74eee1847dc005",
     "Божественный дигимон с человеческим торсом и телом\n"
     "горного козла ниже пояса. Эгиомон обычно выступает\n"
     "в одной музыкальной труппе с Сайренмон и любит играть\n"
     "на свирели «Сиринкс», висящей у него на поясе.\n"
     "Он миролюбив и не любит сражаться, но таит неведомую\n"
     "силу и проявляет исключительное боевое мастерство,\n"
     "защищая тех, кто ему дорог. Мелодией «Манящее эхо»\n"
     "Эгиомон завладевает вниманием слушателя, лишает его\n"
     "чувства собственного «я» и заставляет видеть только\n"
     "музыканта. Пока цель зачарована, другие дигимоны могут\n"
     "спастись или броситься за ней в погоню. Особым приёмом\n"
     "«Оглушающий Удар» Эгиомон бьёт противника и выпускает\n"
     "через руки электричество своего тела, парализуя нервы\n"
     "врага и обездвиживая его."),
    ("patch_text01", "text/digimon_profile.mbe/000_Sheet1.csv", "digimon_0627_profile", 1,
     "9d0deb5c11e0db308b0442694325bfd5877f8eb2cce82df741af784b1ad02403",
     "Ультимативный дигимон, похожий на длинноногого паука.\n"
     "В обычной форме Инфермон вытягивает голову и конечности,\n"
     "но может втянуть их в тело и свернуться в кокон. Защита\n"
     "кокона способна отразить любую атаку, однако двигаться\n"
     "в нём можно лишь по прямой. Инфермон без труда обходит\n"
     "самую надёжную защиту и проникает в любую сеть. Если он\n"
     "вырвется в Сеть, мир погрузится в хаос. Особым приёмом\n"
     "«Паучий стрелок» Инфермон выпускает из отверстия во рту\n"
     "энергетическую бомбу чудовищной разрушительной силы."),
    ("patch_text01", "text/digimon_profile.mbe/000_Sheet1.csv", "digimon_0701_profile", 1,
     "ad11584126c058d8596fefcf49ac15ddffc53fc00c57d00308fdd2acadcc3f04",
     "Загадочный дигимон с огромным рогом на голове. По строению\n"
     "Терьермона можно отнести к зверям-дигимонам, но его\n"
     "последующая форма всё ещё неизвестна. Говорят, иногда он\n"
     "рождается вместе с близнецом. Милый вид и спокойный нрав\n"
     "Терьермона не выдают в нём представителя боевого вида,\n"
     "однако в сражении он оказывается куда сильнее, чем можно\n"
     "подумать. Фирменным приёмом «Терьер Торнадо» он вращает\n"
     "ушами, словно пропеллером, и создаёт небольшой смерч."),
    ("addcont_02_text01", "message/d230.mbe/000_Sheet1.csv", "d230_020_140", 2,
     "fb98dc9d1db40e899b31e6fdc8f7d9438e492bc4b8605c31da71002af9079275",
     "Внезапно я почувствовал, что кто-то ещё теряет силы, как и я.\n"
     "Я тоже ощутил в кристаллах чьё-то присутствие."),
    ("patch_text01", "message/d05.mbe/000_Sheet1.csv", "f_d0501_0050_0230", 2,
     "baebc0339b435a976bcff1e06d3545af9893302f97c25d2c5344fc6e6e166677",
     "До реактора на самом нижнем уровне, где находится лорд\n"
     "Вулканусмон, можно добраться, только если мы оба будем рядом."),
    ("patch_text01", "message/d06.mbe/000_Sheet1.csv", "f_d0604_0060_0020", 2,
     "f135dced65f662589bf3f1cfeb81e3688a7f6ee2ee5d23079cd38d02ee795b19",
     "Здесь чувствуется невообразимое зло. Пока лучше не приближаться."),
    ("patch_text01", "message/d13.mbe/000_Sheet1.csv", "f_d1301_0030_0020", 2,
     "1c4cce4d591bfa978caf328bbd5ae594916864fce96bbbd5b459d2c916d2f662",
     "...Дигимон? А персонала нигде не видно."),
    ("patch_text01", "message/d13.mbe/000_Sheet1.csv", "f_d1301_0180_0010", 2,
     "6e12368ad03a1874767d5eeac5ca6d89e55d56b041bb2ec8fab8828fa76d8085",
     "Тут записка: «О хранении важных документов»."),
    ("patch_text01", "message/d13.mbe/000_Sheet1.csv", "f_d1301_0440_0020", 2,
     "7f05c1cb9e7531876dd99200caadc0dfcb6331dd049b1012d068569a0b30629a",
     "«Люди принимают стихийные бедствия за гнев Божий,\n"
     "но в мифах за ними можно разглядеть дигимонов»."),
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv",
     "lasty_001_4_reaction_char_RUSTTYRANOMON", 2,
     "890c9217e95b016fabf4e7d8e44c193bee84b2837d8dbbf76f33312aebbc88da",
     "Тот, кого хочешь защитить, делает тебя сильнее?\n"
     "Тогда отныне я буду защищать тебя."),
    ("patch_text01", "message/m200.mbe/000_Sheet1.csv", "m200_030_110", 2,
     "64513f3b313d75b649a314d052ba0552aa25ee34ed2fdeb4b22f6d4a540940d4",
     "Все районы в радиусе пяти километров от правительственного здания,\n"
     "включая этот, временно перекроют электромагнитной сетью."),
    ("patch_text01", "message/m235.mbe/000_Sheet1.csv", "m235_010_050", 2,
     "d399c135faeab389b168d466cb6e5dd0f4531c3d00b9845673615d5a26fcfc66",
     "...Дигимон обнаружен. Идите с нами.\nВас поместят в Район Дигимон."),
    ("patch_text01", "message/m350.mbe/000_Sheet1.csv", "m350_010_030", 2,
     "58cf4f68e92b697acedb51c118613a3930ea11c33051065770c83cf557743f43",
     "Похоже, тебя снова перенесло во времени... Но на этот раз\n"
     "что-то не так: Эгиомона нет рядом."),
    ("patch_text01", "message/m350.mbe/000_Sheet1.csv", "m350_010_040", 2,
     "565bd436ab5a354a6378f681ef10569d15eac8cf932aed67266f3997bc73e5a7",
     "Инори тоже нигде нет. Несомненно, её поглотило\n"
     "пространственно-временное возмущение, а Эгиомон последовал за ней."),
    ("patch_text01", "message/m350.mbe/000_Sheet1.csv", "m350_010_050", 2,
     "1203ea0f8e7f58852d77f07f56b9ca184a19851f5b87ac45d062059f1ae69b0c",
     "Вероятно, её поглотило пространственно-временное возмущение.\n"
     "Похоже, Эгиомон отправился следом."),
    ("patch_text01", "message/m350.mbe/000_Sheet1.csv", "m350_010_060", 2,
     "9444d625334d2c5829a5440430f65951b9c2f928430441b3aa163eff1a2cbe42",
     "Я беспокоюсь за них... Но куда важнее то, что путешествие\n"
     "во времени произошло без Эгиомона."),
    ("patch_text01", "message/m350.mbe/000_Sheet1.csv", "m350_010_070", 2,
     "99128a6968b210c8fae7e894d6b720713b2c3c039f3e1c35da70158c572c5371",
     "Именно: тебя перенесло во времени без Эгиомона."),
    ("patch_text01", "message/m350.mbe/000_Sheet1.csv", "m350_140_010", 2,
     "7c5ef07d55a008dc27ea25491e806bf7cd51c51d299bdd3af1522689abec34df",
     "Акашическое Видение активируется даже без Эгиомона."),
    ("patch_text01", "message/m360.mbe/000_Sheet1.csv", "m360_080_011", 2,
     "3de36c79522eb219bac2559431216c10421d8ba2ab2d22a47466da825c17aa0d",
     "Хрономон обладал властью над временем и безраздельно правил Илиадой."),
    ("patch_text01", "message/s110_108.mbe/000_Sheet1.csv", "s110_108_370", 2,
     "1f8c844e92266c28e53a3fb93dfe9a8038d3256af403dfef64e1c4ae85040dc2",
     "Я прямо здесь! Ростом я мал, зато меня невозможно не заметить!"),
    ("patch_text01", "text/digitter_message.mbe/000_Sheet1.csv", "sub_030_029_1", 1,
     "18365b9fcbf00c2675fac6abf5a67474d9e3ca9b2d104167c643f8c36f0f7884",
     "С музыкальной группой вечеринка станет веселее.\n"
     "Мне нужна твоя помощь. Я буду ждать тебя в Деревне\n"
     "Зубчатого Леса.\nПросмотреть детали миссии {decision}"),
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv",
     "zplu_001_3_reaction_char_UNDEADPLUTOMON", 2,
     "1d07d249e39f3f7668f64967558001278586b4199bc687a372eda50647323f23",
     "Дразнишь меня? Так ты и друзей лишишься.\nНо сейчас — тренировка."),
    ("patch_text01", "message/s910_170.mbe/000_Sheet1.csv", "s910_170_1780", 2,
     "c5fdf0fa0a32e11d06ab6fc0aac0e8adf38baf8da9f44eb923c9e0b93ccae3b9",
     "Возможно, он знал, что добьётся успеха, если покажет себе\n"
     "из прошлого, кем станет."),
    ("patch_text01", "message/s020_018.mbe/000_Sheet1.csv", "s020_018_1010", 2,
     "a7f5b752af554737802795ebdcfa3ccc168588103892c5b79121816e54ed35b0",
     "А? Не так. Кажется, было: «Синий цвет — вода чиста;\n"
     "фиолетовый — беда»."),
    ("patch_text01", "text/digitter_message.mbe/000_Sheet1.csv", "hazama_99_200_1", 1,
     "5846ade4477abbe840e56c3e086dc6c979ca6e8ecdb49fd681aa2f07e1b0237e",
     "Я слышал, в Цифровом мире есть группа дигимонов,\n"
     "известная как «Семь Великих Повелителей Демонов»..."),
    ("patch_text01", "message/m320.mbe/000_Sheet1.csv", "m320_040_030", 2,
     "d6fe166cf75e4cbe61db8a50c03d5ea08de20665cef9d08c36b96c6acde1dea3",
     "Послушай Эгиомона. Я не выношу, когда семья сражается."),
    ("patch_text01", "message/m310.mbe/000_Sheet1.csv", "m310_010_150", 2,
     "ad28f01c63980ba4bc49cb24b04fd22600a417ed258eb28826a54f680ace8808",
     "Ведь всё ещё есть шанс, что сила Эгиомона сможет предотвратить\n"
     "Ад Синдзюку."),
    ("patch_text01", "message/s050_043.mbe/000_Sheet1.csv", "s050_043_100", 2,
     "b16ca3990725be55043cdfc4d661fdb826d4ff7751df6aaf8512c2d1f5dbe55a",
     "Похоже, сейчас ты чувствуешь себя совсем никчёмным, да?\n"
     "Ладно, я введу тебя в курс дела."),
    ("patch_text01", "message/s050_043.mbe/000_Sheet1.csv", "s050_043_900", 2,
     "b16ca3990725be55043cdfc4d661fdb826d4ff7751df6aaf8512c2d1f5dbe55a",
     "Похоже, сейчас ты чувствуешь себя совсем никчёмным, да?\n"
     "Ладно, я введу тебя в курс дела."),
    ("patch_text01", "message/d02.mbe/000_Sheet1.csv", "f_d0201_800_0010", 2,
     "e5908fe450b5fcf5b7431abe6242919fee750f63a1e2caa5914c78d921dedfed",
     "Локомона... нет. Значит, пока мы закрыты."),
    ("patch_text01", "message/d02.mbe/000_Sheet1.csv", "f_d0201_1230_0010", 2,
     "bd97f2620cfc6a49faea104f71042337ed9bb13636892d561a1720dd8f157bd2",
     "Сейчас мы убираем эту улицу, так что тебе придётся подождать."),
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv",
     "gao_001_2_reaction_char_GAOMON", 2,
     "4fb58af04ab0e12a9ba0afa870bc3391aa543e12ee90353dfefa2b5dc7093fdd",
     "Надо было догадаться. Мне стоит лучше следить за здоровьем —\n"
     "как и тебе!"),
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv",
     "lena_001_4_reaction_char_RENAMON", 2,
     "f58dc0db96be530c22819180139a1592300909ed67701b527364fd822fc3fc22",
     "Понятно. С каким бы сильным дигимоном мне ни пришлось сразиться,\n"
     "надеюсь, ты меня поддержишь."),
    ("patch_text01", "message/s040_160.mbe/000_Sheet1.csv", "s040_160_380", 2,
     "056f2e58d2488fbc687286845688fb7c0b784290926769605be285a0d4a7dbf7",
     "Фух, больше ни кусочка! Я ведь съел всё, что вы советовали!"),
    ("patch_text01", "message/m340.mbe/000_Sheet1.csv", "m350_080_010", 2,
     "54e17acf3a048845874b518983640dd775b23e6fd55ea088b034ec4b34a71c97",
     "Меркуримон и его союзники бежали и в итоге нашли путь в мир людей."),
    ("patch_text01", "message/d09.mbe/000_Sheet1.csv", "f_d0905_0010_0100", 2,
     "845df8c1fa3d40fced21b7c36eef2fefa24790ae48d597d92218f31bf636cb75",
     "К сожалению, прямо перед завершением моста ценные\n"
     "специальные аккумуляторы..."),
    ("patch_text01", "message/d09.mbe/000_Sheet1.csv", "f_d0905_0010_0110", 2,
     "ac501a042fa5e2e97dae2b9402df007f452cdb9061c6cc30fdf00ecf48c8ba2e",
     "...украл какой-то Цумемон!"),
    ("patch_text01", "message/d09.mbe/000_Sheet1.csv", "f_d0905_0010_0120", 2,
     "ce4a59e25962a9a2b420c74103de8a850b64fabae9f127a0be1a4d55e53fed33",
     "А их так много! Мы понятия не имеем, кто из них утащил наши\n"
     "аккумуляторы!"),
    ("patch_text01", "message/d09.mbe/000_Sheet1.csv", "f_d0905_0010_0130", 2,
     "e70db15cf841de9e5501bf22a0c11dfa6d7322f907add61f101a9125c8cf7436",
     "Этого не может быть! Запасных аккумуляторов у нас нет!"),
    ("patch_text01", "message/m360.mbe/000_Sheet1.csv", "m360_110_031", 2,
     "d4fec804db7abf9659e5b04c2cf2f4464427931e7db9c74dc927b92368082426",
     "—погрузив Илиаду в хаос и в итоге направив мир к гибели."),
]


def digest(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def main() -> None:
    documents: dict[tuple[str, str], list[list[str]]] = {}
    encodings: dict[tuple[str, str], str] = {}
    dirty: set[tuple[str, str]] = set()
    changed = 0
    current = 0

    for package, relative, row_id, column, expected_hash, replacement in UPDATES:
        marker = (package, relative)
        path = CSV_ROOT / package / relative
        if marker not in documents:
            raw = path.read_bytes()
            encodings[marker] = "utf-8-sig" if raw.startswith(b"\xef\xbb\xbf") else "utf-8"
            with path.open("r", encoding="utf-8-sig", newline="") as handle:
                documents[marker] = list(csv.reader(handle))
            physical_lines = raw.removeprefix(b"\xef\xbb\xbf").splitlines()
            if (
                marker in QUOTE_ALL_AFTER_HEADER
                and len(physical_lines) > 1
                and not physical_lines[1].startswith(b'"')
            ):
                dirty.add(marker)
        rows = documents[marker]
        matches = [row for row in rows if row and row[0] == row_id]
        if len(matches) != 1 or len(matches[0]) <= column:
            raise SystemExit(f"Missing or ambiguous row {package}:{relative}:{row_id}")
        row = matches[0]
        if row[column] == replacement:
            current += 1
        elif digest(row[column]) in (
            (expected_hash,) if isinstance(expected_hash, str) else expected_hash
        ):
            row[column] = replacement
            changed += 1
            dirty.add(marker)
        else:
            raise SystemExit(
                f"Unexpected text {package}:{relative}:{row_id}: {row[column]!r}"
            )

    for package, relative in sorted(dirty):
        path = CSV_ROOT / package / relative
        with path.open("w", encoding=encodings[(package, relative)], newline="") as handle:
            rows = documents[(package, relative)]
            if (package, relative) in QUOTE_ALL_AFTER_HEADER:
                csv.writer(handle, lineterminator="\n").writerow(rows[0])
                csv.writer(
                    handle, lineterminator="\n", quoting=csv.QUOTE_ALL
                ).writerows(rows[1:])
            else:
                csv.writer(handle, lineterminator="\n").writerows(rows)

    print(f"Targets: {len(UPDATES)}")
    print(f"Changed: {changed}")
    print(f"Already current: {current}")
    print(f"Files written: {len(dirty)}")


if __name__ == "__main__":
    main()

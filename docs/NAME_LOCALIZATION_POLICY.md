# Политика локализации имен дигимонов

Полного официального русскоязычного глоссария для всех дигимонов из `Digimon Story Time Stranger` найти не удалось. Поэтому проект ведет имена по прозрачной иерархии источников:

1. Официальные игровые строки и официальный Digimon Encyclopedia от Bandai используются как канон для идентичности дигимона и английского/международного имени.
2. Русская Digimon Wiki/Fandom используется как широкий русскоязычный справочник для кириллических вариантов имен. Это не официальный глоссарий, поэтому такие строки помечаются как `ru_digimon_fandom` и обычно получают уверенность `medium`.
3. Если русская страница не найдена, текущий перевод сохраняется и помечается для ручной проверки.
4. Для служебных форм в скобках берется найденное базовое имя, а локальный суффикс формы сохраняется: например, `Аполломон (огненная сфера)`.

Аудитные таблицы:

- `exports/digimon_name_wiki_compare.csv` - полное сравнение текущих имен с русской Digimon Wiki/Fandom.
- `exports/digimon_name_wiki_mismatches.csv` - все несовпадения и строки без найденного источника.
- `exports/digimon_name_wiki_unmatched.csv` - строки, для которых не найдена русская страница.
- `exports/digimon_name_recommendations.csv` - применяемые рекомендации с источником, ссылкой и уровнем уверенности.
- `exports/digimon_name_changes_applied.csv` - фактически примененные замены.

Ключевые источники:

- Official Digimon Encyclopedia: https://digimon.net/reference_en/
- Digimon Card Game language standardization rules: https://world.digimoncard.com/rule/lang-standardization-rules/
- Русская Digimon Wiki/Fandom, список дигимонов: https://digimon.fandom.com/ru/wiki/Список_дигимонов

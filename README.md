# Digimon Story Time Stranger RU

Русский перевод для **Digimon Story Time Stranger**.

## Что внутри

- `csv` - редактируемые CSV-исходники `patch_text01` и DLC-пакетов `addcont_*`.
- `scripts` - вспомогательные скрипты экспорта, сверки и редакторских проходов.
- `docs` - заметки по политике перевода и источникам.
- `exports` - отчёты по именам дигимонов и сверке с русской Digimon Wiki/Fandom.
- `exports/excel` - версии отчётов для Excel: `.xlsx` и CSV с `sep=;`.
- `installer` - установщик, оформление и payload с готовыми `.mvgl` файлами.
- `dist` - собранные релизы: ZIP-инсталлятор и standalone EXE.

## Установка

Для обычной установки скачайте standalone-файл из `dist` и запустите его:

```powershell
DSTS_RU_Installer_v*.exe
```

Установщик позволит выбрать путь к папке игры, найдёт обязательные
`app_text01.dx11.mvgl` и `patch_text01.dx11.mvgl`, а также обновит присутствующие
DLC-архивы `addcont_*`. Перед заменой каждого файла он сохранит резервную копию
в `_dsts_ru_backups`.

ZIP-архив в `dist` оставлен как запасной вариант: его нужно распаковать целиком,
а затем запустить `DSTS-RU-Installer.exe` рядом с папкой `payload`.

> **Важно:** «История диалогов» хранит в сохранении текст уже показанных реплик.
> Установка или обновление перевода не меняет старые записи; новые и повторно
> показанные реплики отображаются в актуальной редакции.

## Восстановление бэкапа

Запустите:

```powershell
DSTS_RU_Installer_v*.exe
```

В окне установщика выберите папку игры и нажмите `Восстановить бэкап`.

## Сборка инсталлятора

Чтобы пересобрать payload из CSV, ZIP, standalone EXE и контрольные суммы:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/build_release.ps1
```

Перед упаковкой скрипт запускает строгую проверку подтверждённых исправлений,
а после упаковки сверяет содержимое всех MVGL с CSV и Lua-хуком. Нужен
Python 3.9+; путь можно передать через `-PythonExe` или переменную
`DSTS_PYTHON`. Быстрый запуск только исходных проверок: `-PreflightOnly`.

Готовые файлы появятся в `dist`.

После создания и отправки тега релиз публикуется командой:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/publish_release.ps1
```

Скрипт закрепляет единый заголовок `DSTS RU vX.Y.Z`, проверяет наличие трёх релизных файлов и не позволяет случайно перезаписать существующий GitHub Release.

Полезные отдельные команды:

```powershell
# CSV -> installer/payload/*.mvgl
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/mvgl_text_workflow.ps1 -Mode pack

# installer/payload/*.mvgl -> csv/<package>
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/mvgl_text_workflow.ps1 -Mode unpack -Package patch_text01 -Force
```

## Контроль целостности

SHA-256 суммы опубликованных файлов лежат в `CHECKSUMS.sha256`.

## История версий

См. [CHANGELOG.md](CHANGELOG.md).

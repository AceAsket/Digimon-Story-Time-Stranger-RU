# Digimon Story Time Stranger RU

Русский перевод для **Digimon Story Time Stranger**.

## Что внутри

- `csv/patch_text01` - редактируемые CSV-исходники перевода.
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

Установщик позволит выбрать путь к папке игры, найдёт `app_text01.dx11.mvgl` и
`patch_text01.dx11.mvgl`, сделает резервную копию оригиналов в
`_dsts_ru_backups`, а затем заменит их файлами перевода.

ZIP-архив в `dist` оставлен как запасной вариант: его нужно распаковать целиком,
а затем запустить `DSTS-RU-Installer.exe` рядом с папкой `payload`.

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

Готовые файлы появятся в `dist`.

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

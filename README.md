# Digimon Story Time Stranger RU

Русский перевод для **Digimon Story Time Stranger**.

Автор перевода и репозитория: **AceAsket**.

## Что внутри

- `csv/patch_text01` - редактируемые CSV-исходники перевода.
- `scripts` - вспомогательные скрипты экспорта, сверки и редакторских проходов.
- `docs` - заметки по политике перевода и источникам.
- `exports` - отчёты по именам дигимонов и сверке с русской Digimon Wiki/Fandom.
- `installer` - установщик и payload с готовыми `.mvgl` файлами.
- `dist` - собранный ZIP-инсталлятор.

## Установка

Скачайте архив из `dist`, распакуйте его в любую папку и запустите:

```powershell
DSTS-RU-Installer.exe
```

Установщик позволит выбрать путь к папке игры, найдёт `app_text01.dx11.mvgl` и
`patch_text01.dx11.mvgl`, сделает резервную копию оригиналов в
`_dsts_ru_backups`, а затем заменит их файлами перевода.

## Восстановление бэкапа

Запустите:

```powershell
DSTS-RU-Installer.exe
```

В окне установщика выберите папку игры и нажмите `Восстановить бэкап`.

## Сборка инсталлятора

После обновления файлов в `installer/payload` выполните:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File installer/build_installer.ps1
```

Готовый архив появится в `dist`.

## Контроль целостности

SHA-256 суммы опубликованных файлов лежат в `CHECKSUMS.sha256`.

## История версий

См. [CHANGELOG.md](CHANGELOG.md).

param(
    [string]$GameDir,
    [switch]$RestoreLatest,
    [switch]$NoPause
)

$ErrorActionPreference = "Stop"

$ModName = "Digimon Story Time Stranger RU"
$PayloadDir = Join-Path $PSScriptRoot "payload"
$RequiredGameDataPayloadFiles = @(
    "app_text01.dx11.mvgl",
    "patch_text01.dx11.mvgl"
)
$RequiredRootPayloadFiles = @(
    "dinput8.dll"
)
$GameExecutableNames = @(
    "Digimon Story Time Stranger.exe",
    "Digimon Story Time Stranger Demo.exe"
)
$RequiredPayloadFiles = $RequiredGameDataPayloadFiles + $RequiredRootPayloadFiles
$OptionalPayloadFiles = @(
    "addcont_01_text01.dx11.mvgl",
    "addcont_02_text01.dx11.mvgl",
    "addcont_03_text01.dx11.mvgl",
    "addcont_05_text01.dx11.mvgl",
    "addcont_07_text01.dx11.mvgl",
    "addcont_12_text01.dx11.mvgl",
    "addcont_17_text01.dx11.mvgl"
)
$GameDataPayloadFiles = $RequiredGameDataPayloadFiles + $OptionalPayloadFiles
$NativeInputMarkerFileName = "_dsts_ru_input_fix.txt"
$CreatedFilesListName = "_dsts_ru_created_files.txt"
$InstalledVersionFileName = "_dsts_ru_translation_version.txt"

function Write-Info([string]$Message) {
    Write-Host "[DSTS-RU] $Message"
}

function Resolve-FullPath([string]$Path) {
    return [System.IO.Path]::GetFullPath($Path)
}

function Get-RelativePathCompat([string]$BasePath, [string]$ChildPath) {
    $base = Resolve-FullPath $BasePath
    $child = Resolve-FullPath $ChildPath
    if (-not $base.EndsWith([System.IO.Path]::DirectorySeparatorChar)) {
        $base += [System.IO.Path]::DirectorySeparatorChar
    }
    if ($child.StartsWith($base, [System.StringComparison]::OrdinalIgnoreCase)) {
        return $child.Substring($base.Length)
    }
    return [System.IO.Path]::GetFileName($child)
}

function Find-SteamLibraries {
    $libraries = New-Object System.Collections.Generic.List[string]
    $steamPaths = @(
        "HKCU:\Software\Valve\Steam",
        "HKLM:\Software\WOW6432Node\Valve\Steam",
        "HKLM:\Software\Valve\Steam"
    )

    foreach ($regPath in $steamPaths) {
        try {
            $steamPath = (Get-ItemProperty -Path $regPath -ErrorAction Stop).SteamPath
            if ($steamPath -and (Test-Path -LiteralPath $steamPath)) {
                $libraries.Add((Join-Path $steamPath "steamapps\common"))
                $libraryFile = Join-Path $steamPath "steamapps\libraryfolders.vdf"
                if (Test-Path -LiteralPath $libraryFile) {
                    $content = Get-Content -LiteralPath $libraryFile -Raw
                    $matches = [regex]::Matches($content, '"path"\s+"([^"]+)"')
                    foreach ($match in $matches) {
                        $path = $match.Groups[1].Value.Replace("\\", "\")
                        $common = Join-Path $path "steamapps\common"
                        if (Test-Path -LiteralPath $common) {
                            $libraries.Add($common)
                        }
                    }
                }
            }
        } catch {
            # Missing registry keys are normal on non-Steam installs.
        }
    }

    return $libraries | Select-Object -Unique
}

function Find-GameDir {
    $candidates = New-Object System.Collections.Generic.List[string]
    foreach ($library in Find-SteamLibraries) {
        $candidates.Add((Join-Path $library "Digimon Story Time Stranger"))
        $candidates.Add((Join-Path $library "Digimon Story Time Stranger Demo"))
    }

    foreach ($candidate in $candidates) {
        if (Test-Path -LiteralPath $candidate) {
            return (Resolve-FullPath $candidate)
        }
    }

    return $null
}

function Read-GameDir {
    param([string]$InitialGameDir)

    if ($InitialGameDir -and (Test-Path -LiteralPath $InitialGameDir)) {
        return (Resolve-FullPath $InitialGameDir)
    }

    $auto = Find-GameDir
    if ($auto) {
        Write-Info "Найдена папка игры: $auto"
        $answer = Read-Host "Использовать этот путь? [Y/n]"
        if ([string]::IsNullOrWhiteSpace($answer) -or $answer -match "^[YyДд]") {
            return $auto
        }
    }

    do {
        $manual = Read-Host "Укажите папку игры"
        if ($manual -and (Test-Path -LiteralPath $manual)) {
            return (Resolve-FullPath $manual)
        }
        Write-Host "Папка не найдена. Попробуйте ещё раз."
    } while ($true)
}

function Find-TargetFile {
    param(
        [string]$Root,
        [string]$FileName,
        [switch]$Optional
    )

    $matches = Get-ChildItem -LiteralPath $Root -Recurse -File -Filter $FileName -ErrorAction SilentlyContinue |
        Where-Object {
            $_.FullName -notmatch "\\_dsts_ru_backups\\" -and
            $_.FullName -notmatch "\\payload\\"
        } |
        Sort-Object FullName
    if ($matches.Count -eq 0) {
        if ($Optional) {
            return $null
        }
        throw "Не найден файл $FileName внутри $Root. Укажите корневую папку игры, где уже есть этот файл."
    }
    if ($matches.Count -gt 1) {
        Write-Info "Найдено несколько файлов $FileName, используется первый:"
        foreach ($match in $matches) {
            Write-Host "  $($match.FullName)"
        }
    }
    return $matches[0].FullName
}

function Get-Sha256([string]$Path) {
    return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
}

function Test-NativeInputPayloadConflict([string]$Root) {
    $file = $RequiredRootPayloadFiles[0]
    $target = Join-Path $Root $file
    if (-not (Test-Path -LiteralPath $target)) {
        return
    }

    $payload = Join-Path $PayloadDir $file
    $targetHash = Get-Sha256 $target
    $payloadHash = Get-Sha256 $payload
    if ($targetHash -eq $payloadHash) {
        return
    }

    $marker = Join-Path $Root $NativeInputMarkerFileName
    $recordedHash = ""
    if (Test-Path -LiteralPath $marker) {
        foreach ($line in Get-Content -LiteralPath $marker -Encoding UTF8) {
            if ($line -match '^sha256=(.+)$') {
                $recordedHash = $Matches[1].Trim().ToLowerInvariant()
                break
            }
        }
    }
    if ($recordedHash -and $recordedHash -eq $targetHash) {
        return
    }

    throw "В папке игры уже есть сторонний dinput8.dll. Установщик не будет его перезаписывать. Удалите конфликтующий мод вручную или восстановите его штатным способом, затем повторите установку."
}

function Test-GameRoot([string]$Root) {
    $found = $false
    foreach ($file in $GameExecutableNames) {
        if (Test-Path -LiteralPath (Join-Path $Root $file) -PathType Leaf) {
            $found = $true
            break
        }
    }
    if (-not $found) {
        throw "В выбранной папке нет исполняемого файла Digimon Story Time Stranger. Выберите корневую папку игры, а не gamedata и не родительский каталог."
    }
}

function Install-Mod {
    param([string]$Root)

    if (-not (Test-Path -LiteralPath $PayloadDir)) {
        throw "Не найдена папка payload рядом с установщиком: $PayloadDir"
    }

    foreach ($file in $RequiredPayloadFiles) {
        $payloadFile = Join-Path $PayloadDir $file
        if (-not (Test-Path -LiteralPath $payloadFile)) {
            throw "Не найден файл payload: $payloadFile"
        }
    }
    foreach ($file in $OptionalPayloadFiles) {
        $payloadFile = Join-Path $PayloadDir $file
        if (-not (Test-Path -LiteralPath $payloadFile)) {
            Write-Info "Опциональный payload отсутствует, пропуск: $file"
        }
    }

    Test-GameRoot -Root $Root
    Test-NativeInputPayloadConflict -Root $Root

    $timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
    $backupRoot = Join-Path $Root "_dsts_ru_backups"
    $backupDir = Join-Path $backupRoot $timestamp
    New-Item -ItemType Directory -Force -Path $backupDir | Out-Null

    $manifest = [ordered]@{
        mod = $ModName
        created_at = (Get-Date).ToString("o")
        game_dir = $Root
        files = @()
        created_files = @()
    }

    foreach ($file in $GameDataPayloadFiles) {
        $payloadFile = Join-Path $PayloadDir $file
        $optional = $OptionalPayloadFiles -contains $file
        if ($optional -and -not (Test-Path -LiteralPath $payloadFile)) {
            continue
        }

        $target = Find-TargetFile -Root $Root -FileName $file -Optional:$optional
        if (-not $target) {
            Write-Info "Опциональный файл не найден в игре, пропуск: $file"
            continue
        }
        $relative = Get-RelativePathCompat -BasePath $Root -ChildPath $target
        $backupFile = Join-Path $backupDir $relative
        New-Item -ItemType Directory -Force -Path (Split-Path -Parent $backupFile) | Out-Null

        Write-Info "Бэкап: $relative"
        Copy-Item -LiteralPath $target -Destination $backupFile -Force

        Write-Info "Установка: $relative"
        Copy-Item -LiteralPath $payloadFile -Destination $target -Force

        $manifest.files += [ordered]@{
            relative_path = $relative
            backup_path = $backupFile
        }
    }

    foreach ($file in $RequiredRootPayloadFiles) {
        $payloadFile = Join-Path $PayloadDir $file
        $target = Join-Path $Root $file
        $relative = Get-RelativePathCompat -BasePath $Root -ChildPath $target
        if (Test-Path -LiteralPath $target) {
            $backupFile = Join-Path $backupDir $relative
            New-Item -ItemType Directory -Force -Path (Split-Path -Parent $backupFile) | Out-Null
            Write-Info "Бэкап: $relative"
            Copy-Item -LiteralPath $target -Destination $backupFile -Force
            $manifest.files += [ordered]@{
                relative_path = $relative
                backup_path = $backupFile
            }
        }
        else {
            $manifest.created_files += $relative
        }
        Write-Info "Установка: $relative"
        Copy-Item -LiteralPath $payloadFile -Destination $target -Force
    }

    $version = ""
    foreach ($versionFile in @(
        (Join-Path $PSScriptRoot "VERSION"),
        (Join-Path $PSScriptRoot "..\VERSION")
    )) {
        if (Test-Path -LiteralPath $versionFile) {
            $version = (Get-Content -LiteralPath $versionFile -Raw -Encoding UTF8).Trim()
            if ($version) { break }
        }
    }
    if (-not $version) {
        $version = "unknown"
    }
    $nativeMarker = Join-Path $Root $NativeInputMarkerFileName
    $nativeMarkerRelative = Get-RelativePathCompat -BasePath $Root -ChildPath $nativeMarker
    if (Test-Path -LiteralPath $nativeMarker) {
        $backupFile = Join-Path $backupDir $nativeMarkerRelative
        Copy-Item -LiteralPath $nativeMarker -Destination $backupFile -Force
        $manifest.files += [ordered]@{
            relative_path = $nativeMarkerRelative
            backup_path = $backupFile
        }
    }
    else {
        $manifest.created_files += $nativeMarkerRelative
    }
    $nativeHash = Get-Sha256 (Join-Path $PayloadDir $RequiredRootPayloadFiles[0])
    [IO.File]::WriteAllText(
        $nativeMarker,
        "version=$version`r`nsha256=$nativeHash`r`n",
        [Text.UTF8Encoding]::new($false)
    )

    if ($manifest.created_files.Count -gt 0) {
        [IO.File]::WriteAllLines(
            (Join-Path $backupDir $CreatedFilesListName),
            [string[]]$manifest.created_files,
            [Text.UTF8Encoding]::new($false)
        )
    }

    $manifestPath = Join-Path $backupDir "manifest.json"
    $manifest | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $manifestPath -Encoding UTF8

    [IO.File]::WriteAllText(
        (Join-Path $Root $InstalledVersionFileName),
        $version + [Environment]::NewLine,
        [Text.UTF8Encoding]::new($false)
    )

    Write-Info "Версия перевода: $version"
    Write-Info "Исправление ввода кириллического имени установлено."
    Write-Info "Важно: «История диалогов» хранит в сохранении текст уже показанных реплик. Установка или обновление перевода не меняет старые записи; новые и повторно показанные реплики отображаются в актуальной редакции."
    Write-Info "Готово. Бэкап сохранён: $backupDir"
}

function Restore-Backup {
    param([string]$Root)

    $backupRoot = Join-Path $Root "_dsts_ru_backups"
    if (-not (Test-Path -LiteralPath $backupRoot)) {
        throw "Папка бэкапов не найдена: $backupRoot"
    }

    $latest = Get-ChildItem -LiteralPath $backupRoot -Directory | Sort-Object Name -Descending | Select-Object -First 1
    if (-not $latest) {
        throw "Бэкапы не найдены в $backupRoot"
    }

    $manifestPath = Join-Path $latest.FullName "manifest.json"
    if (-not (Test-Path -LiteralPath $manifestPath)) {
        throw "manifest.json не найден в $($latest.FullName)"
    }

    $manifest = Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json
    foreach ($entry in $manifest.files) {
        $target = Join-Path $Root $entry.relative_path
        $backup = $entry.backup_path
        if (-not (Test-Path -LiteralPath $backup)) {
            $backup = Join-Path $latest.FullName $entry.relative_path
        }
        if (-not (Test-Path -LiteralPath $backup)) {
            throw "Файл бэкапа не найден: $backup"
        }

        Write-Info "Восстановление: $($entry.relative_path)"
        Copy-Item -LiteralPath $backup -Destination $target -Force
    }

    $created = @()
    if ($manifest.created_files) {
        $created += @($manifest.created_files)
    }
    $createdList = Join-Path $latest.FullName $CreatedFilesListName
    if (Test-Path -LiteralPath $createdList) {
        $created += @(Get-Content -LiteralPath $createdList -Encoding UTF8)
    }
    foreach ($relative in ($created | Where-Object { $_ } | Select-Object -Unique)) {
        $target = Join-Path $Root $relative
        $fullRoot = (Resolve-FullPath $Root).TrimEnd('\', '/') + [IO.Path]::DirectorySeparatorChar
        $fullTarget = Resolve-FullPath $target
        if (-not $fullTarget.StartsWith($fullRoot, [StringComparison]::OrdinalIgnoreCase)) {
            throw "Небезопасный путь в списке восстановления: $relative"
        }
        if (Test-Path -LiteralPath $fullTarget) {
            Write-Info "Удаление добавленного файла: $relative"
            Remove-Item -LiteralPath $fullTarget -Force
        }
    }

    $installedVersion = Join-Path $Root $InstalledVersionFileName
    if (Test-Path -LiteralPath $installedVersion) {
        Remove-Item -LiteralPath $installedVersion -Force
    }

    Write-Info "Восстановлен бэкап: $($latest.FullName)"
}

try {
    $resolvedGameDir = Read-GameDir -InitialGameDir $GameDir
    if ($RestoreLatest) {
        Restore-Backup -Root $resolvedGameDir
    } else {
        Install-Mod -Root $resolvedGameDir
    }
} catch {
    Write-Host ""
    Write-Host "Ошибка: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
} finally {
    if (-not $NoPause) {
        Write-Host ""
        Write-Host "Нажмите Enter для выхода..."
        [void][System.Console]::ReadLine()
    }
}

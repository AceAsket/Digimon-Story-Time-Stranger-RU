param(
    [string]$GameDir,
    [switch]$RestoreLatest,
    [switch]$NoPause
)

$ErrorActionPreference = "Stop"

$ModName = "Digimon Story Time Stranger RU"
$PayloadDir = Join-Path $PSScriptRoot "payload"
$PayloadFiles = @(
    "app_text01.dx11.mvgl",
    "patch_text01.dx11.mvgl"
)

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
        [string]$FileName
    )

    $matches = Get-ChildItem -LiteralPath $Root -Recurse -File -Filter $FileName -ErrorAction SilentlyContinue |
        Where-Object {
            $_.FullName -notmatch "\\_dsts_ru_backups\\" -and
            $_.FullName -notmatch "\\payload\\"
        } |
        Sort-Object FullName
    if ($matches.Count -eq 0) {
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

function Install-Mod {
    param([string]$Root)

    if (-not (Test-Path -LiteralPath $PayloadDir)) {
        throw "Не найдена папка payload рядом с установщиком: $PayloadDir"
    }

    foreach ($file in $PayloadFiles) {
        $payloadFile = Join-Path $PayloadDir $file
        if (-not (Test-Path -LiteralPath $payloadFile)) {
            throw "Не найден файл payload: $payloadFile"
        }
    }

    $timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
    $backupRoot = Join-Path $Root "_dsts_ru_backups"
    $backupDir = Join-Path $backupRoot $timestamp
    New-Item -ItemType Directory -Force -Path $backupDir | Out-Null

    $manifest = [ordered]@{
        mod = $ModName
        created_at = (Get-Date).ToString("o")
        game_dir = $Root
        files = @()
    }

    foreach ($file in $PayloadFiles) {
        $target = Find-TargetFile -Root $Root -FileName $file
        $relative = Get-RelativePathCompat -BasePath $Root -ChildPath $target
        $backupFile = Join-Path $backupDir $relative
        New-Item -ItemType Directory -Force -Path (Split-Path -Parent $backupFile) | Out-Null

        Write-Info "Бэкап: $relative"
        Copy-Item -LiteralPath $target -Destination $backupFile -Force

        Write-Info "Установка: $relative"
        Copy-Item -LiteralPath (Join-Path $PayloadDir $file) -Destination $target -Force

        $manifest.files += [ordered]@{
            relative_path = $relative
            backup_path = $backupFile
        }
    }

    $manifestPath = Join-Path $backupDir "manifest.json"
    $manifest | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $manifestPath -Encoding UTF8

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

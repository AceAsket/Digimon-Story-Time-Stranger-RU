param(
    [ValidateSet("pack", "unpack")]
    [string]$Mode = "pack",

    [string[]]$Package = @(),

    [string]$CsvRoot = (Join-Path $PSScriptRoot "..\csv"),
    [string]$PayloadRoot = (Join-Path $PSScriptRoot "..\installer\payload"),
    [string]$WorkRoot = (Join-Path $PSScriptRoot "..\verify\mvgl_text_workflow"),

    [switch]$Force,
    [switch]$KeepWork
)

$ErrorActionPreference = "Stop"

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$CsvRoot = [System.IO.Path]::GetFullPath($CsvRoot)
$PayloadRoot = [System.IO.Path]::GetFullPath($PayloadRoot)
$WorkRoot = [System.IO.Path]::GetFullPath($WorkRoot)

function Assert-UnderPath([string]$Child, [string]$Parent) {
    $parentFull = [System.IO.Path]::GetFullPath($Parent).TrimEnd('\', '/') + [System.IO.Path]::DirectorySeparatorChar
    $childFull = [System.IO.Path]::GetFullPath($Child)
    if (-not $childFull.StartsWith($parentFull, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "Refusing to operate outside expected directory. Path: $childFull Parent: $parentFull"
    }
}

function Remove-DirectorySafe([string]$Path, [string]$AllowedParent) {
    if (-not (Test-Path -LiteralPath $Path)) {
        return
    }
    $resolved = (Resolve-Path -LiteralPath $Path).Path
    Assert-UnderPath -Child $resolved -Parent $AllowedParent
    Remove-Item -LiteralPath $resolved -Recurse -Force
}

function Invoke-MvglTool([string[]]$Arguments) {
    & $script:MvglTool @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "MVGLToolsCLI failed: $($Arguments -join ' ')"
    }
}

function Resolve-MvglTool {
    if ($env:MVGLTOOLS_CLI -and (Test-Path -LiteralPath $env:MVGLTOOLS_CLI)) {
        return (Resolve-Path -LiteralPath $env:MVGLTOOLS_CLI).Path
    }

    $fixedCandidate = Join-Path $RepoRoot ".tools\MVGLTools-v2.2.0-fixed\MVGLToolsCLI.exe"
    if (Test-Path -LiteralPath $fixedCandidate) {
        return (Resolve-Path -LiteralPath $fixedCandidate).Path
    }

    $candidate = Join-Path $RepoRoot ".tools\MVGLTools-v2.2.0\MVGLTools-v2.2.0-win64\MVGLToolsCLI.exe"
    if (Test-Path -LiteralPath $candidate) {
        return (Resolve-Path -LiteralPath $candidate).Path
    }

    throw "MVGLToolsCLI.exe was not found. Set MVGLTOOLS_CLI or place tools under .tools\MVGLTools-v2.2.0."
}

function Get-DefaultPackages {
    Get-ChildItem -LiteralPath $PayloadRoot -File -Filter "*.dx11.mvgl" |
        Sort-Object Name |
        ForEach-Object { $_.Name -replace "\.dx11\.mvgl$", "" }
}

function Pack-Package([string]$Name) {
    $payload = Join-Path $PayloadRoot "$Name.dx11.mvgl"
    $csvPackage = Join-Path $CsvRoot $Name
    if (-not (Test-Path -LiteralPath $payload)) {
        throw "Payload not found: $payload"
    }
    if (-not (Test-Path -LiteralPath $csvPackage) -and $Name -ne "app_text01") {
        Write-Host "[skip] CSV package not found: $Name"
        return
    }

    $packageWork = Join-Path $WorkRoot $Name
    $baseDir = Join-Path $packageWork "base"
    Remove-DirectorySafe -Path $packageWork -AllowedParent $WorkRoot
    New-Item -ItemType Directory -Force -Path $packageWork | Out-Null

    Write-Host "[pack] ${Name}: unpack base MVGL"
    Invoke-MvglTool @("--game=dsts", "--mode=unpack-mvgl", "--input", $payload, "--output", $baseDir)

    foreach ($section in @("message", "text")) {
        $csvSection = Join-Path $csvPackage $section
        if (-not (Test-Path -LiteralPath $csvSection)) {
            continue
        }

        $packedSection = Join-Path $packageWork "packed_$section"
        $baseSection = Join-Path $baseDir $section
        Write-Host "[pack] ${Name}: ${section} CSV -> MBE"
        Invoke-MvglTool @("--game=dsts", "--mode=pack-mbe-dir", "--input", $csvSection, "--output", $packedSection)

        Remove-DirectorySafe -Path $baseSection -AllowedParent $baseDir
        Move-Item -LiteralPath $packedSection -Destination $baseSection
    }

    if ($Name -eq "app_text01") {
        $titleVersionRoot = Join-Path $RepoRoot "assets\title_version"
        $titleVersionAsset = Join-Path $titleVersionRoot "ui_title_copyright_01.img"
        $titleVersionMarker = Join-Path $titleVersionRoot "VERSION"
        $releaseVersion = (Get-Content -LiteralPath (Join-Path $RepoRoot "VERSION") -Raw).Trim()
        if (-not (Test-Path -LiteralPath $titleVersionAsset)) {
            throw "Title version texture not found: $titleVersionAsset"
        }
        if (-not (Test-Path -LiteralPath $titleVersionMarker)) {
            throw "Title version marker not found: $titleVersionMarker"
        }
        $assetVersion = (Get-Content -LiteralPath $titleVersionMarker -Raw).Trim()
        if ($assetVersion -ne $releaseVersion) {
            throw "Title texture version '$assetVersion' does not match release VERSION '$releaseVersion'."
        }

        $baseImage = Join-Path $baseDir "images\ui_title_copyright_01.img"
        if (-not (Test-Path -LiteralPath $baseImage)) {
            throw "Base title copyright texture not found in app_text01: $baseImage"
        }
        Copy-Item -LiteralPath $titleVersionAsset -Destination $baseImage -Force
        Write-Host "[pack] ${Name}: injected title-screen translation version $assetVersion"
    }

    if ($Name -eq "patch_text01") {
        $compiledLua = Join-Path $RepoRoot "verify\lua_gender_hook\compiled"
        $baseLua = Join-Path $baseDir "lua"
        $luaNames = @(
            "function_common.lua",
            "function_field.lua",
            "battle_10810200.lua",
            "battle_11200010.lua",
            "m360.lua",
            "m440.lua",
            "t04prcs.lua",
            "gender_message_map.lua"
        )
        foreach ($luaName in $luaNames) {
            $sourceLua = Join-Path $compiledLua $luaName
            if (-not (Test-Path -LiteralPath $sourceLua)) {
                throw "Compiled Lua hook chunk not found: $sourceLua"
            }
            Copy-Item -LiteralPath $sourceLua -Destination (Join-Path $baseLua $luaName) -Force
        }
        Write-Host "[pack] ${Name}: injected $($luaNames.Count) compiled Lua hook chunks"
    }

    # Never let a failed/hung pack truncate the currently installable payload.
    # Build beside the working tree and promote only a completed non-empty file.
    $packedArchive = Join-Path $packageWork "$Name.dx11.mvgl.new"
    Write-Host "[pack] ${Name}: pack MVGL -> $packedArchive"
    Invoke-MvglTool @("--game=dsts", "--mode=pack-mvgl", "--input", $baseDir, "--output", $packedArchive)
    if (-not (Test-Path -LiteralPath $packedArchive) -or (Get-Item -LiteralPath $packedArchive).Length -le 0) {
        throw "MVGL pack produced no usable archive: $packedArchive"
    }
    Move-Item -LiteralPath $packedArchive -Destination $payload -Force

    if (-not $KeepWork) {
        Remove-DirectorySafe -Path $packageWork -AllowedParent $WorkRoot
    }
}

function Unpack-Package([string]$Name) {
    $payload = Join-Path $PayloadRoot "$Name.dx11.mvgl"
    if (-not (Test-Path -LiteralPath $payload)) {
        throw "Payload not found: $payload"
    }

    $packageWork = Join-Path $WorkRoot $Name
    $baseDir = Join-Path $packageWork "base"
    Remove-DirectorySafe -Path $packageWork -AllowedParent $WorkRoot
    New-Item -ItemType Directory -Force -Path $packageWork | Out-Null

    Write-Host "[unpack] ${Name}: unpack base MVGL"
    Invoke-MvglTool @("--game=dsts", "--mode=unpack-mvgl", "--input", $payload, "--output", $baseDir)

    foreach ($section in @("message", "text")) {
        $baseSection = Join-Path $baseDir $section
        if (-not (Test-Path -LiteralPath $baseSection)) {
            continue
        }

        $csvSection = Join-Path (Join-Path $CsvRoot $Name) $section
        if ((Test-Path -LiteralPath $csvSection) -and -not $Force) {
            throw "CSV output already exists: $csvSection. Re-run with -Force to overwrite."
        }
        Remove-DirectorySafe -Path $csvSection -AllowedParent $CsvRoot

        Write-Host "[unpack] ${Name}: ${section} MBE -> CSV"
        Invoke-MvglTool @("--game=dsts", "--mode=unpack-mbe-dir", "--input", $baseSection, "--output", $csvSection)
    }

    if (-not $KeepWork) {
        Remove-DirectorySafe -Path $packageWork -AllowedParent $WorkRoot
    }
}

Assert-UnderPath -Child $WorkRoot -Parent $RepoRoot
if (-not (Test-Path -LiteralPath $PayloadRoot)) {
    throw "Payload root not found: $PayloadRoot"
}
if (-not (Test-Path -LiteralPath $CsvRoot)) {
    New-Item -ItemType Directory -Force -Path $CsvRoot | Out-Null
}

$script:MvglTool = Resolve-MvglTool
$packages = if ($Package.Count -gt 0) { $Package } else { @(Get-DefaultPackages) }
if ($packages.Count -eq 0) {
    throw "No packages selected."
}

New-Item -ItemType Directory -Force -Path $WorkRoot | Out-Null

foreach ($name in $packages) {
    if ($Mode -eq "pack") {
        Pack-Package -Name $name
    } else {
        Unpack-Package -Name $name
    }
}

Write-Host "Done: $Mode $($packages.Count) package(s)."

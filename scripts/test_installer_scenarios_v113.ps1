param(
    [string]$Version = (Get-Content -LiteralPath (Join-Path $PSScriptRoot "..\VERSION") -Raw).Trim()
)

$ErrorActionPreference = "Stop"
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$InstallerDir = Join-Path $RepoRoot "installer"
$PayloadDir = Join-Path $InstallerDir "payload"
$BuildScript = Join-Path $InstallerDir "build_gui_installer.ps1"
$TempRoot = Join-Path ([IO.Path]::GetTempPath()) ("dsts_ru_installer_test_" + [Guid]::NewGuid().ToString("N"))
$ExternalExe = Join-Path $TempRoot "external\DSTS-RU-Installer.exe"
$EmbeddedExe = Join-Path $TempRoot "embedded\DSTS-RU-Installer.exe"
$PayloadFiles = @(
    "app_text01.dx11.mvgl",
    "patch_text01.dx11.mvgl",
    "addcont_01_text01.dx11.mvgl",
    "addcont_02_text01.dx11.mvgl",
    "addcont_03_text01.dx11.mvgl",
    "addcont_05_text01.dx11.mvgl",
    "addcont_07_text01.dx11.mvgl",
    "addcont_12_text01.dx11.mvgl",
    "addcont_17_text01.dx11.mvgl"
)

function Assert-True([bool]$Condition, [string]$Message) {
    if (-not $Condition) {
        throw "Assertion failed: $Message"
    }
}

function Get-InternalType([Reflection.Assembly]$Assembly, [string]$Name) {
    $Type = $Assembly.GetType($Name, $false)
    if ($null -eq $Type) {
        throw "Type not found: $Name"
    }
    return $Type
}

function New-Core([Reflection.Assembly]$Assembly, [string]$BaseDir) {
    $Type = Get-InternalType $Assembly "DstsRuInstaller.InstallerCore"
    $Flags = [Reflection.BindingFlags]::Instance -bor [Reflection.BindingFlags]::Public -bor [Reflection.BindingFlags]::NonPublic
    return [Activator]::CreateInstance(
        $Type,
        $Flags,
        $null,
        [object[]]@($BaseDir),
        [Globalization.CultureInfo]::InvariantCulture
    )
}

function Invoke-Core([object]$Core, [string]$Method, [object[]]$Arguments) {
    $Flags = [Reflection.BindingFlags]::Instance -bor [Reflection.BindingFlags]::Public -bor [Reflection.BindingFlags]::NonPublic
    $Info = $Core.GetType().GetMethod($Method, $Flags)
    if ($null -eq $Info) {
        throw "Core method not found: $Method"
    }
    $Parameters = $Info.GetParameters()
    $NativeArguments = @(
        for ($Index = 0; $Index -lt $Arguments.Count; $Index++) {
            [Management.Automation.LanguagePrimitives]::ConvertTo(
                $Arguments[$Index],
                $Parameters[$Index].ParameterType,
                [Globalization.CultureInfo]::InvariantCulture
            )
        }
    )
    return $Info.Invoke($Core, [object[]]$NativeArguments)
}

function New-FakeGame([string]$Name, [string]$InstalledVersion = "") {
    $Root = Join-Path $TempRoot $Name
    $Data = Join-Path $Root "gamedata"
    New-Item -ItemType Directory -Force -Path $Data | Out-Null
    foreach ($File in $PayloadFiles) {
        [IO.File]::WriteAllText(
            (Join-Path $Data $File),
            "ORIGINAL::$Name::$File",
            [Text.UTF8Encoding]::new($false)
        )
    }
    if ($InstalledVersion) {
        [IO.File]::WriteAllText(
            (Join-Path $Root "_dsts_ru_translation_version.txt"),
            $InstalledVersion + [Environment]::NewLine,
            [Text.UTF8Encoding]::new($false)
        )
    }
    return $Root
}

function Assert-PayloadInstalled([string]$GameRoot) {
    foreach ($File in $PayloadFiles) {
        $Expected = (Get-FileHash -LiteralPath (Join-Path $PayloadDir $File) -Algorithm SHA256).Hash
        $Actual = (Get-FileHash -LiteralPath (Join-Path $GameRoot "gamedata\$File") -Algorithm SHA256).Hash
        Assert-True ($Expected -eq $Actual) "payload hash mismatch for $File"
    }
    $Marker = (Get-Content -LiteralPath (Join-Path $GameRoot "_dsts_ru_translation_version.txt") -Raw).Trim()
    Assert-True ($Marker -eq $Version) "installed version marker must be $Version, got $Marker"
}

function Assert-OriginalRestored([string]$GameRoot, [string]$Name) {
    foreach ($File in $PayloadFiles) {
        $Actual = [IO.File]::ReadAllText((Join-Path $GameRoot "gamedata\$File"), [Text.Encoding]::UTF8)
        Assert-True ($Actual -eq "ORIGINAL::$Name::$File") "restore mismatch for $File"
    }
    Assert-True (-not (Test-Path -LiteralPath (Join-Path $GameRoot "_dsts_ru_translation_version.txt"))) `
        "restore must clear installed version marker"
}

New-Item -ItemType Directory -Force -Path $TempRoot | Out-Null
try {
    & $BuildScript -Output $ExternalExe
    if ($LASTEXITCODE -ne 0) { throw "External installer build failed." }
    & $BuildScript -Output $EmbeddedExe -EmbedPayload
    if ($LASTEXITCODE -ne 0) { throw "Embedded installer build failed." }

    # Load from bytes so the temporary EXE files are not locked until process exit.
    $ExternalAssembly = [Reflection.Assembly]::Load([IO.File]::ReadAllBytes($ExternalExe))
    $EmbeddedAssembly = [Reflection.Assembly]::Load([IO.File]::ReadAllBytes($EmbeddedExe))
    $EmbeddedResources = $EmbeddedAssembly.GetManifestResourceNames() | Where-Object { $_ -like "DstsRuPayload.*" }
    Assert-True ($EmbeddedResources.Count -eq $PayloadFiles.Count) `
        "embedded installer must contain $($PayloadFiles.Count) payload resources"

    $Metadata = Get-InternalType $EmbeddedAssembly "DstsRuInstaller.InstallerMetadata"
    $MetadataFlags = [Reflection.BindingFlags]::Static -bor [Reflection.BindingFlags]::Public -bor [Reflection.BindingFlags]::NonPublic
    $EmbeddedVersion = $Metadata.GetProperty("Version", $MetadataFlags).GetValue($null, $null)
    Assert-True ($EmbeddedVersion -eq $Version) "embedded installer version must be $Version"

    $UpdateChecker = Get-InternalType $EmbeddedAssembly "DstsRuInstaller.UpdateChecker"
    $UpdateFlags = [Reflection.BindingFlags]::Static -bor [Reflection.BindingFlags]::Public -bor [Reflection.BindingFlags]::NonPublic
    $IsNewer = $UpdateChecker.GetMethod("IsNewerVersion", $UpdateFlags)
    Assert-True ([bool]$IsNewer.Invoke($null, @($Version, "0.1.40"))) "packaged version must update 0.1.40"
    Assert-True (-not [bool]$IsNewer.Invoke($null, @($Version, $Version))) "same version must not be an update"

    $Log = [Action[string]]{ param([string]$Message) }

    # Clean external-payload installation and restore.
    $CleanRoot = New-FakeGame "clean"
    $ExternalCore = New-Core $ExternalAssembly $InstallerDir
    Invoke-Core $ExternalCore "Install" @($CleanRoot, $Log) | Out-Null
    Assert-PayloadInstalled $CleanRoot
    $Backup = Get-ChildItem -LiteralPath (Join-Path $CleanRoot "_dsts_ru_backups") -Directory
    Assert-True ($Backup.Count -eq 1) "clean install must create exactly one backup"
    Assert-True (Test-Path -LiteralPath (Join-Path $Backup[0].FullName "manifest.json")) `
        "backup manifest must exist"
    Invoke-Core $ExternalCore "RestoreLatest" @($CleanRoot, $Log) | Out-Null
    Assert-OriginalRestored $CleanRoot "clean"

    # Upgrade an older installed marker using the packaged payload.
    $OldRoot = New-FakeGame "old" "0.1.40"
    Invoke-Core $ExternalCore "Install" @($OldRoot, $Log) | Out-Null
    Assert-PayloadInstalled $OldRoot
    $InstalledVersion = Invoke-Core $ExternalCore "GetInstalledVersion" @($OldRoot)
    Assert-True ($InstalledVersion -eq $Version) "old install must advance to packaged version"

    # Standalone EXE must install without any adjacent payload directory.
    $EmbeddedRoot = New-FakeGame "embedded"
    $EmbeddedCore = New-Core $EmbeddedAssembly (Split-Path -Parent $EmbeddedExe)
    $HasEmbedded = $EmbeddedCore.GetType().GetProperty("HasEmbeddedPayload", $MetadataFlags -band (-bnot [Reflection.BindingFlags]::Static))
    if ($null -eq $HasEmbedded) {
        $InstanceFlags = [Reflection.BindingFlags]::Instance -bor [Reflection.BindingFlags]::Public -bor [Reflection.BindingFlags]::NonPublic
        $HasEmbedded = $EmbeddedCore.GetType().GetProperty("HasEmbeddedPayload", $InstanceFlags)
    }
    Assert-True ([bool]$HasEmbedded.GetValue($EmbeddedCore, $null)) "standalone installer must report embedded payload"
    Invoke-Core $EmbeddedCore "Install" @($EmbeddedRoot, $Log) | Out-Null
    Assert-PayloadInstalled $EmbeddedRoot

    Write-Host "Installer scenario tests passed."
    Write-Host "Version: $Version"
    Write-Host "Scenarios: clean+restore, old-version upgrade, current-version comparison, embedded install"
    Write-Host "Embedded payload resources: $($EmbeddedResources.Count)"
}
finally {
    try {
        Remove-Item -LiteralPath $TempRoot -Recurse -Force -ErrorAction Stop
    }
    catch {
        Write-Warning "Temporary installer test directory could not be removed: $TempRoot"
    }
}

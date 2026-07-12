param(
    [string]$Output = (Join-Path $PSScriptRoot "DSTS-RU-Installer.exe"),
    [switch]$EmbedPayload
)

$ErrorActionPreference = "Stop"

$InstallerDir = $PSScriptRoot
$Source = Join-Path $InstallerDir "gui\DSTS.RU.Installer.cs"
$PayloadDir = Join-Path $InstallerDir "payload"
$AssetsDir = Join-Path $InstallerDir "assets"
$Icon = Join-Path $AssetsDir "dsts_ru_icon.ico"
$Banner = Join-Path $AssetsDir "dsts_ru_installer_banner.png"
$VersionFile = Join-Path $InstallerDir "..\VERSION"

$candidates = @(
    "$env:WINDIR\Microsoft.NET\Framework64\v4.0.30319\csc.exe",
    "$env:WINDIR\Microsoft.NET\Framework\v4.0.30319\csc.exe"
)

$csc = $candidates | Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1
if (-not $csc) {
    throw "csc.exe from .NET Framework 4.x was not found."
}
if (-not (Test-Path -LiteralPath $Icon)) {
    throw "Installer icon was not found: $Icon"
}
if (-not (Test-Path -LiteralPath $Banner)) {
    throw "Installer banner was not found: $Banner"
}
if (-not (Test-Path -LiteralPath $VersionFile)) {
    throw "Version file was not found: $VersionFile"
}

New-Item -ItemType Directory -Force -Path (Split-Path -Parent $Output) | Out-Null

$compilerArgs = @(
    "/nologo",
    "/target:winexe",
    "/platform:anycpu",
    "/optimize+",
    "/codepage:65001",
    "/reference:System.dll",
    "/reference:System.Core.dll",
    "/reference:System.Drawing.dll",
    "/reference:System.IO.Compression.dll",
    "/reference:System.IO.Compression.FileSystem.dll",
    "/reference:System.Windows.Forms.dll",
    "/win32icon:$Icon",
    "/resource:$Banner,DstsRuInstaller.banner.png",
    "/resource:$VersionFile,DstsRuInstaller.version.txt",
    "/out:$Output",
    $Source
)

if ($EmbedPayload) {
    if (-not (Test-Path -LiteralPath $PayloadDir)) {
        throw "Payload directory was not found: $PayloadDir"
    }
    foreach ($payload in Get-ChildItem -LiteralPath $PayloadDir -File | Sort-Object Name) {
        $compilerArgs += "/resource:$($payload.FullName),DstsRuPayload.$($payload.Name)"
    }
}

& $csc @compilerArgs

if ($LASTEXITCODE -ne 0) {
    throw "GUI installer build failed."
}

$mode = if ($EmbedPayload) { "standalone" } else { "external-payload" }
Write-Host "Built $Output ($mode)"

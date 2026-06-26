$ErrorActionPreference = "Stop"

$InstallerDir = $PSScriptRoot
$Source = Join-Path $InstallerDir "gui\DSTS.RU.Installer.cs"
$Output = Join-Path $InstallerDir "DSTS-RU-Installer.exe"

$candidates = @(
    "$env:WINDIR\Microsoft.NET\Framework64\v4.0.30319\csc.exe",
    "$env:WINDIR\Microsoft.NET\Framework\v4.0.30319\csc.exe"
)

$csc = $candidates | Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1
if (-not $csc) {
    throw "csc.exe from .NET Framework 4.x was not found."
}

& $csc `
    /nologo `
    /target:winexe `
    /platform:anycpu `
    /optimize+ `
    /codepage:65001 `
    /reference:System.dll `
    /reference:System.Core.dll `
    /reference:System.Drawing.dll `
    /reference:System.Windows.Forms.dll `
    /out:$Output `
    $Source

if ($LASTEXITCODE -ne 0) {
    throw "GUI installer build failed."
}

Write-Host "Built $Output"

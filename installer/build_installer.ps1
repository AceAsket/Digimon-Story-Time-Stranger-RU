param(
    [string]$Version = (Get-Content -LiteralPath (Join-Path $PSScriptRoot "..\VERSION") -Raw).Trim()
)

$ErrorActionPreference = "Stop"

$Root = Resolve-Path (Join-Path $PSScriptRoot "..")
$Dist = Join-Path $Root "dist"
$PackageName = "DSTS_RU_Installer_v$Version"
$Stage = Join-Path $Dist $PackageName
$Archive = Join-Path $Dist "$PackageName.zip"

if (Test-Path -LiteralPath $Stage) {
    Remove-Item -LiteralPath $Stage -Recurse -Force
}
if (Test-Path -LiteralPath $Archive) {
    Remove-Item -LiteralPath $Archive -Force
}

New-Item -ItemType Directory -Force -Path $Stage | Out-Null

$items = @(
    "README.md",
    "install.cmd",
    "restore-backup.cmd",
    "Install-DSTS-RU.ps1",
    "payload"
)

foreach ($item in $items) {
    $source = Join-Path $PSScriptRoot $item
    $destination = Join-Path $Stage $item
    Copy-Item -LiteralPath $source -Destination $destination -Recurse -Force
}

Compress-Archive -Path (Join-Path $Stage "*") -DestinationPath $Archive -CompressionLevel Optimal
Remove-Item -LiteralPath $Stage -Recurse -Force

Write-Host "Built $Archive"

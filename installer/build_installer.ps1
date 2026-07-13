param(
    [string]$Version = (Get-Content -LiteralPath (Join-Path $PSScriptRoot "..\VERSION") -Raw).Trim()
)

$ErrorActionPreference = "Stop"

$Root = Resolve-Path (Join-Path $PSScriptRoot "..")
$Dist = Join-Path $Root "dist"
$PackageName = "DSTS_RU_Installer_v$Version"
$PayloadPackageName = "DSTS_RU_Update_v$Version"
$Stage = Join-Path $Dist $PackageName
$PayloadStage = Join-Path $Dist $PayloadPackageName
$Archive = Join-Path $Dist "$PackageName.zip"
$Standalone = Join-Path $Dist "$PackageName.exe"
$PayloadArchive = Join-Path $Dist "$PayloadPackageName.zip"

powershell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $PSScriptRoot "build_gui_installer.ps1")

if (Test-Path -LiteralPath $Stage) {
    Remove-Item -LiteralPath $Stage -Recurse -Force
}
if (Test-Path -LiteralPath $Archive) {
    Remove-Item -LiteralPath $Archive -Force
}
if (Test-Path -LiteralPath $Standalone) {
    Remove-Item -LiteralPath $Standalone -Force
}
if (Test-Path -LiteralPath $PayloadStage) {
    Remove-Item -LiteralPath $PayloadStage -Recurse -Force
}
if (Test-Path -LiteralPath $PayloadArchive) {
    Remove-Item -LiteralPath $PayloadArchive -Force
}

powershell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $PSScriptRoot "build_gui_installer.ps1") -Output $Standalone -EmbedPayload

New-Item -ItemType Directory -Force -Path $Stage | Out-Null

$items = @(
    "README.md",
    "DSTS-RU-Installer.exe",
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

Copy-Item -LiteralPath (Join-Path $Root "VERSION") -Destination (Join-Path $Stage "VERSION") -Force

Compress-Archive -Path (Join-Path $Stage "*") -DestinationPath $Archive -CompressionLevel Optimal
Remove-Item -LiteralPath $Stage -Recurse -Force

New-Item -ItemType Directory -Force -Path (Join-Path $PayloadStage "payload") | Out-Null
Copy-Item -Path (Join-Path $PSScriptRoot "payload\*") -Destination (Join-Path $PayloadStage "payload") -Recurse -Force
Copy-Item -LiteralPath (Join-Path $PSScriptRoot "..\VERSION") -Destination (Join-Path $PayloadStage "VERSION") -Force
Compress-Archive -Path (Join-Path $PayloadStage "*") -DestinationPath $PayloadArchive -CompressionLevel Optimal
Remove-Item -LiteralPath $PayloadStage -Recurse -Force

Write-Host "Built $Archive"
Write-Host "Built $Standalone"
Write-Host "Built $PayloadArchive"

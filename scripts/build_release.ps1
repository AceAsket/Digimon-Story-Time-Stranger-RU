param(
    [string]$Version = (Get-Content -LiteralPath (Join-Path $PSScriptRoot "..\VERSION") -Raw).Trim(),
    [string[]]$Package = @(),
    [switch]$SkipPayloadPack
)

$ErrorActionPreference = "Stop"

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path

if (-not $SkipPayloadPack) {
    $workflowArgs = @{
        Mode = "pack"
    }
    if ($Package.Count -gt 0) {
        $workflowArgs.Package = $Package
    }
    & (Join-Path $PSScriptRoot "mvgl_text_workflow.ps1") @workflowArgs
    if ($LASTEXITCODE -ne 0) {
        throw "Payload pack failed."
    }
}

powershell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $RepoRoot "installer\build_installer.ps1") -Version $Version
if ($LASTEXITCODE -ne 0) {
    throw "Installer build failed."
}

powershell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $PSScriptRoot "update_checksums.ps1")
if ($LASTEXITCODE -ne 0) {
    throw "Checksum update failed."
}

Write-Host "Release build complete for version $Version."

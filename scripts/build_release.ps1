param(
    [string]$Version = (Get-Content -LiteralPath (Join-Path $PSScriptRoot "..\VERSION") -Raw).Trim(),
    [string[]]$Package = @(),
    [switch]$SkipPayloadPack
)

$ErrorActionPreference = "Stop"

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path

$MojibakePattern = [regex]'\u0420[\u0080-\u00ff\u0400-\u040f\u201a\u201e\u201c\u201d\u2020\u2021\u20ac]'
$MojibakeCount = 0
$MojibakeSamples = @()
$CsvRoot = Join-Path $RepoRoot "csv"
foreach ($File in Get-ChildItem -LiteralPath $CsvRoot -Recurse -Filter "000_Sheet1.csv") {
    $LineNumber = 0
    foreach ($Line in Get-Content -LiteralPath $File.FullName -Encoding UTF8) {
        $LineNumber++
        if (-not $MojibakePattern.IsMatch($Line)) {
            continue
        }
        $MojibakeCount++
        if ($MojibakeSamples.Count -lt 20) {
            $Relative = $File.FullName.Substring($RepoRoot.Length + 1)
            $MojibakeSamples += ("{0}:{1}: {2}" -f $Relative, $LineNumber, $Line)
        }
    }
}

if ($MojibakeCount -gt 0) {
    Write-Host "Mojibake preflight failed. Found $MojibakeCount suspicious line(s):"
    $MojibakeSamples | ForEach-Object { Write-Host $_ }
    throw "Fix mojibake fragments before building a release."
}

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

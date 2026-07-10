param(
    [string]$Version = (Get-Content -LiteralPath (Join-Path $PSScriptRoot "..\VERSION") -Raw).Trim(),
    [string]$NotesFile = "",
    [switch]$Prerelease,
    [switch]$ValidateOnly
)

$ErrorActionPreference = "Stop"

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$Version = $Version.Trim().TrimStart('v', 'V')
if ($Version -notmatch '^\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?$') {
    throw "Invalid release version: $Version"
}

$Tag = "v$Version"
$Title = "DSTS RU $Tag"
if ([string]::IsNullOrWhiteSpace($NotesFile)) {
    $NotesFile = Join-Path $RepoRoot "docs\RELEASE_NOTES_v$Version.md"
}
$NotesFile = [System.IO.Path]::GetFullPath($NotesFile)

$Assets = @(
    (Join-Path $RepoRoot "dist\DSTS_RU_Installer_v$Version.exe"),
    (Join-Path $RepoRoot "dist\DSTS_RU_Installer_v$Version.zip"),
    (Join-Path $RepoRoot "dist\DSTS_RU_Payload_v$Version.zip")
)

if (-not (Test-Path -LiteralPath $NotesFile -PathType Leaf)) {
    throw "Release notes were not found: $NotesFile"
}
foreach ($Asset in $Assets) {
    if (-not (Test-Path -LiteralPath $Asset -PathType Leaf)) {
        throw "Release asset was not found: $Asset"
    }
}

& gh auth status | Out-Null
if ($LASTEXITCODE -ne 0) {
    throw "GitHub CLI is not authenticated."
}

& git rev-parse --verify --quiet "refs/tags/$Tag" | Out-Null
if ($LASTEXITCODE -ne 0) {
    throw "Create and push tag $Tag before publishing the release."
}

$ExistingJson = & gh release view $Tag --json tagName,name,isDraft,isPrerelease 2>$null
$ReleaseExists = $LASTEXITCODE -eq 0
if ($ReleaseExists -and $ValidateOnly) {
    $Existing = $ExistingJson | ConvertFrom-Json
    if ($Existing.tagName -ne $Tag -or $Existing.name -ne $Title -or $Existing.isDraft) {
        throw "Existing release metadata does not match the required format."
    }
    Write-Host "Validated existing release $Title and $($Assets.Count) local assets."
    return
}
if ($ReleaseExists) {
    throw "GitHub Release $Tag already exists."
}

if ($ValidateOnly) {
    Write-Host "Validated unpublished release $Title and $($Assets.Count) local assets."
    return
}

$Arguments = @("release", "create", $Tag)
$Arguments += $Assets
$Arguments += @("--title", $Title, "--notes-file", $NotesFile)
if ($Prerelease) {
    $Arguments += "--prerelease"
}

& gh @Arguments
if ($LASTEXITCODE -ne 0) {
    throw "Failed to publish GitHub Release $Tag."
}

$Published = & gh release view $Tag --json tagName,name,isDraft,isPrerelease | ConvertFrom-Json
if ($Published.tagName -ne $Tag -or $Published.name -ne $Title -or $Published.isDraft) {
    throw "Published release metadata does not match the required format."
}

Write-Host "Published $Title with $($Assets.Count) assets."

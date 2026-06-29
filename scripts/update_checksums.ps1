param(
    [string]$Output = (Join-Path $PSScriptRoot "..\CHECKSUMS.sha256")
)

$ErrorActionPreference = "Stop"

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$Output = [System.IO.Path]::GetFullPath($Output)

function Get-RelativePath([string]$Base, [string]$Child) {
    $baseFull = [System.IO.Path]::GetFullPath($Base).TrimEnd('\', '/') + [System.IO.Path]::DirectorySeparatorChar
    $childFull = [System.IO.Path]::GetFullPath($Child)
    if ($childFull.StartsWith($baseFull, [System.StringComparison]::OrdinalIgnoreCase)) {
        return $childFull.Substring($baseFull.Length).Replace('\', '/')
    }
    return [System.IO.Path]::GetFileName($Child)
}

function Get-VersionSortKey([System.IO.FileInfo]$File) {
    if ($File.Name -match "_v(\d+)\.(\d+)\.(\d+)\.(zip|exe)$") {
        return "{0:D4}.{1:D4}.{2:D4}.{3}" -f [int]$Matches[1], [int]$Matches[2], [int]$Matches[3], $Matches[4]
    }
    return $File.Name
}

$files = New-Object System.Collections.Generic.List[System.IO.FileInfo]

$gui = Join-Path $RepoRoot "installer\DSTS-RU-Installer.exe"
if (Test-Path -LiteralPath $gui) {
    $files.Add((Get-Item -LiteralPath $gui))
}

$payloadRoot = Join-Path $RepoRoot "installer\payload"
if (Test-Path -LiteralPath $payloadRoot) {
    Get-ChildItem -LiteralPath $payloadRoot -File -Filter "*.dx11.mvgl" |
        Sort-Object Name |
        ForEach-Object { $files.Add($_) }
}

$distRoot = Join-Path $RepoRoot "dist"
if (Test-Path -LiteralPath $distRoot) {
    Get-ChildItem -LiteralPath $distRoot -File |
        Where-Object {
            $_.Name -match "^DSTS_RU_Installer_v\d+\.\d+\.\d+\.(zip|exe)$" -or
            $_.Name -match "^DSTS_RU_Payload_v\d+\.\d+\.\d+\.zip$"
        } |
        Sort-Object @{ Expression = { Get-VersionSortKey $_ } }, Name |
        ForEach-Object { $files.Add($_) }
}

$lines = foreach ($file in $files) {
    $hash = (Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
    "$hash  $(Get-RelativePath -Base $RepoRoot -Child $file.FullName)"
}

[System.IO.File]::WriteAllText($Output, (($lines -join "`n") + "`n"), [System.Text.Encoding]::ASCII)
Write-Host "Wrote $($files.Count) checksums to $Output"

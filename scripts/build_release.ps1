param(
    [string]$Version = (Get-Content -LiteralPath (Join-Path $PSScriptRoot "..\VERSION") -Raw).Trim(),
    [string[]]$Package = @(),
    [switch]$SkipPayloadPack,
    [switch]$PreflightOnly,
    [string]$PythonExe = $env:DSTS_PYTHON
)

$ErrorActionPreference = "Stop"

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path

function Resolve-PythonRunner([string]$Requested) {
    $candidates = @()
    if ($Requested) {
        $candidates += $Requested
    }
    else {
        $candidates += @("python3.exe", "python.exe", "python3", "python")
    }

    foreach ($candidate in $candidates) {
        $resolved = $null
        if (Test-Path -LiteralPath $candidate) {
            $resolved = (Resolve-Path -LiteralPath $candidate).Path
        }
        else {
            $command = Get-Command $candidate -CommandType Application -ErrorAction SilentlyContinue | Select-Object -First 1
            if ($command) {
                $resolved = $command.Source
            }
        }
        if (-not $resolved) {
            continue
        }
        if (-not $Requested -and $resolved -like "*\Microsoft\WindowsApps\*") {
            continue
        }

        & $resolved -c "import sys; assert sys.version_info >= (3, 9)" *> $null
        if ($LASTEXITCODE -eq 0) {
            return @($resolved)
        }
    }

    if (-not $Requested) {
        $launcher = Get-Command "py.exe" -CommandType Application -ErrorAction SilentlyContinue | Select-Object -First 1
        if ($launcher) {
            & $launcher.Source -3 -c "import sys; assert sys.version_info >= (3, 9)" *> $null
            if ($LASTEXITCODE -eq 0) {
                return @($launcher.Source, "-3")
            }
        }
    }

    throw "Python 3.9+ was not found. Pass -PythonExe or set DSTS_PYTHON before building a release."
}

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

$PythonRunner = @(Resolve-PythonRunner -Requested $PythonExe)
$ResolvedPython = $PythonRunner[0]
$PythonPrefix = @($PythonRunner | Select-Object -Skip 1)
$RegressionAudit = Join-Path $PSScriptRoot "audit_reported_regressions_v165.py"
& $ResolvedPython @PythonPrefix $RegressionAudit
$RegressionAuditExit = $LASTEXITCODE
if ($RegressionAuditExit -ne 0) {
    throw "Release regression audit failed (exit $RegressionAuditExit); payload was not modified."
}

if ($PreflightOnly) {
    Write-Host "Release source preflight complete; no payload or installer files were modified."
    exit 0
}

$NativeInputDir = Join-Path $RepoRoot "native\name_input_fix"
powershell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $NativeInputDir "build.ps1")
if ($LASTEXITCODE -ne 0) {
    throw "Cyrillic name-input hook build failed."
}
powershell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $NativeInputDir "test.ps1")
if ($LASTEXITCODE -ne 0) {
    throw "Cyrillic name-input hook verification failed."
}

if (-not $SkipPayloadPack) {
    $workflowArgs = @{
        Mode = "pack"
        PythonExe = $ResolvedPython
        PythonPrefix = $PythonPrefix
    }
    if ($Package.Count -gt 0) {
        $workflowArgs.Package = $Package
    }
    & (Join-Path $PSScriptRoot "mvgl_text_workflow.ps1") @workflowArgs
    if ($LASTEXITCODE -ne 0) {
        throw "Payload pack failed."
    }

    $PayloadVerifier = Join-Path $PSScriptRoot "verify_release_payload_v114.py"
    & $ResolvedPython @PythonPrefix $PayloadVerifier
    $PayloadVerifierExit = $LASTEXITCODE
    if ($PayloadVerifierExit -ne 0) {
        throw "Packed payload verification failed (exit $PayloadVerifierExit); installer was not built."
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

param(
    [string]$Output = (Join-Path $PSScriptRoot "..\..\installer\payload\dinput8.dll")
)

$ErrorActionPreference = "Stop"

$Root = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$Compiler = Join-Path $Root ".tools\llvm-mingw-20260616-ucrt-x86_64\bin\clang.exe"
$Source = Join-Path $PSScriptRoot "dinput8_proxy.c"
$Output = [IO.Path]::GetFullPath($Output)

if (-not (Test-Path -LiteralPath $Compiler)) {
    throw "Компилятор не найден: $Compiler"
}

New-Item -ItemType Directory -Force -Path (Split-Path -Parent $Output) | Out-Null

& $Compiler `
    --target=x86_64-w64-windows-gnu `
    -std=c11 `
    -Os `
    -Wall `
    -Wextra `
    -Werror `
    -shared `
    -s `
    "-Wl,--no-insert-timestamp" `
    -o $Output `
    $Source `
    (Join-Path $PSScriptRoot "dinput8.def") `
    -luser32

if ($LASTEXITCODE -ne 0) {
    throw "Сборка dinput8.dll завершилась с кодом $LASTEXITCODE"
}

Write-Host "Built $Output"

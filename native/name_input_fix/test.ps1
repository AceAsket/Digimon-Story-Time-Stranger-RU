param(
    [string]$Dll = (Join-Path $PSScriptRoot "..\..\installer\payload\dinput8.dll")
)

$ErrorActionPreference = "Stop"

$Root = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$Compiler = Join-Path $Root ".tools\llvm-mingw-20260616-ucrt-x86_64\bin\clang.exe"
$ReadObj = Join-Path $Root ".tools\llvm-mingw-20260616-ucrt-x86_64\bin\llvm-readobj.exe"
$TestExe = Join-Path $env:TEMP ("dsts_ru_input_hook_test_" + [Guid]::NewGuid().ToString("N") + ".exe")
$FallbackDll = Join-Path $env:TEMP ("dsts_ru_input_hook_fallback_" + [Guid]::NewGuid().ToString("N") + ".dll")
$Dll = [IO.Path]::GetFullPath($Dll)

if (-not (Test-Path -LiteralPath $Dll)) {
    throw "DLL не найдена: $Dll"
}

try {
    & $Compiler `
        --target=x86_64-w64-windows-gnu `
        -std=c11 `
        -Os `
        -Wall `
        -Wextra `
        -Werror `
        -o $TestExe `
        (Join-Path $PSScriptRoot "test_hook.c") `
        -luser32 `
        -ldxguid `
        -lole32
    if ($LASTEXITCODE -ne 0) {
        throw "Сборка теста завершилась с кодом $LASTEXITCODE"
    }

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
        -DDSTS_RU_DISABLE_DLLMAIN_WORKER `
        -o $FallbackDll `
        (Join-Path $PSScriptRoot "dinput8_proxy.c") `
        (Join-Path $PSScriptRoot "dinput8.def") `
        -luser32
    if ($LASTEXITCODE -ne 0) {
        throw "Сборка DirectInput-fallback DLL завершилась с кодом $LASTEXITCODE"
    }

    $Cases = @(
        @{ Dll = $Dll; ClassName = "Digimon Story Time Stranger"; Startup = "dllmain" },
        @{ Dll = $Dll; ClassName = "Digimon Story Time Stranger Demo"; Startup = "dllmain" },
        @{ Dll = $FallbackDll; ClassName = "GameMain"; Startup = "directinput" }
    )
    foreach ($Case in $Cases) {
        & $TestExe $Case.Dll $Case.ClassName $Case.Startup
        if ($LASTEXITCODE -ne 0) {
            throw "Тест dinput8.dll ($($Case.ClassName), $($Case.Startup)) завершился с кодом $LASTEXITCODE"
        }
    }

    $Headers = & $ReadObj --file-headers --coff-imports --coff-exports $Dll
    if ($LASTEXITCODE -ne 0) {
        throw "Не удалось проверить PE-заголовки dinput8.dll"
    }
    $Text = $Headers -join "`n"
    foreach ($Export in @("DirectInput8Create", "DstsRuInstallInputHook", "DstsRuInputFixVersion")) {
        if ($Text -notmatch [regex]::Escape($Export)) {
            throw "В dinput8.dll отсутствует экспорт $Export"
        }
    }
    if ($Text -notmatch "Machine: IMAGE_FILE_MACHINE_AMD64") {
        throw "dinput8.dll собрана не для x64"
    }
    Write-Host "PE verification passed: x64 and required exports present."
}
finally {
    Remove-Item -LiteralPath $TestExe -Force -ErrorAction SilentlyContinue
    Remove-Item -LiteralPath $FallbackDll -Force -ErrorAction SilentlyContinue
}

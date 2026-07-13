#define WIN32_LEAN_AND_MEAN
#define COBJMACROS
#include <windows.h>
#include <dinput.h>


typedef HRESULT(WINAPI *DirectInput8CreateFn)(
    HINSTANCE,
    DWORD,
    REFIID,
    LPVOID *,
    LPUNKNOWN
);

static HMODULE g_system_dinput8;
static DirectInput8CreateFn g_direct_input8_create;
static SRWLOCK g_hook_lock = SRWLOCK_INIT;
static volatile LONG g_hook_worker_started;
static HWND g_game_window;
static WNDPROC g_original_wndproc;


static LRESULT CALLBACK DstsRuWindowProc(
    HWND window,
    UINT message,
    WPARAM wparam,
    LPARAM lparam
) {
    WNDPROC original_wndproc;

    if (message == WM_CHAR && wparam >= 0x80 && wparam <= 0xFF) {
        const UINT code_page = GetACP();
        const unsigned char input_byte = (unsigned char)wparam;

        /*
         * The game registers an ANSI window class, so WM_CHAR contains one
         * byte in the active ANSI code page.  Its own handler mistakenly
         * treats that byte as UTF-16 before converting it to UTF-8.  Decode
         * the single-byte Cyrillic character first and pass the real UTF-16
         * code point to the original handler.
         *
         * Do not alter DBCS lead bytes: they require state across messages
         * and are outside the Russian localization fix.
         */
        if (!IsDBCSLeadByteEx(code_page, input_byte)) {
            const char input = (char)input_byte;
            WCHAR decoded = 0;
            if (MultiByteToWideChar(
                    code_page,
                    MB_PRECOMPOSED,
                    &input,
                    1,
                    &decoded,
                    1
                ) == 1) {
                wparam = (WPARAM)decoded;
            }
        }
    }

    original_wndproc = g_original_wndproc;
    if (!original_wndproc) {
        return DefWindowProcA(window, message, wparam, lparam);
    }
    return CallWindowProcA(original_wndproc, window, message, wparam, lparam);
}


static BOOL IsGameWindowClass(const char *class_name) {
    return lstrcmpA(class_name, "Digimon Story Time Stranger") == 0
        || lstrcmpA(class_name, "Digimon Story Time Stranger Demo") == 0
        || lstrcmpA(class_name, "GameMain") == 0;
}


static BOOL CALLBACK FindGameWindow(HWND window, LPARAM parameter) {
    DWORD process_id = 0;
    char class_name[96];

    (void)parameter;
    GetWindowThreadProcessId(window, &process_id);
    if (process_id != GetCurrentProcessId()) {
        return TRUE;
    }
    if (GetClassNameA(window, class_name, (int)sizeof(class_name)) <= 0) {
        return TRUE;
    }
    if (IsWindowUnicode(window) || !IsGameWindowClass(class_name)) {
        return TRUE;
    }

    g_game_window = window;
    return FALSE;
}


BOOL WINAPI DstsRuInstallInputHook(void) {
    BOOL installed = FALSE;
    WNDPROC current_wndproc;
    WNDPROC previous_wndproc;

    AcquireSRWLockExclusive(&g_hook_lock);
    SetLastError(ERROR_SUCCESS);

    if (g_game_window && g_original_wndproc && IsWindow(g_game_window)) {
        /*
         * Never subclass the same live window twice.  A later overlay may
         * legitimately install its own WndProc and keep ours in its chain.
         * Hooking that overlay again would create ours -> overlay -> ours.
         */
        installed = TRUE;
        goto done;
    }

    g_game_window = NULL;
    g_original_wndproc = NULL;
    EnumWindows(FindGameWindow, 0);
    if (!g_game_window) {
        goto done;
    }

    SetLastError(ERROR_SUCCESS);
    current_wndproc = (WNDPROC)GetWindowLongPtrA(g_game_window, GWLP_WNDPROC);
    if (!current_wndproc && GetLastError() != ERROR_SUCCESS) {
        OutputDebugStringA("DSTS RU: GetWindowLongPtrA failed; Cyrillic input hook was not installed.\n");
        g_game_window = NULL;
        goto done;
    }
    g_original_wndproc = current_wndproc;

    SetLastError(ERROR_SUCCESS);
    previous_wndproc = (WNDPROC)SetWindowLongPtrA(
        g_game_window,
        GWLP_WNDPROC,
        (LONG_PTR)DstsRuWindowProc
    );
    if (!previous_wndproc && GetLastError() != ERROR_SUCCESS) {
        OutputDebugStringA("DSTS RU: SetWindowLongPtrA failed; Cyrillic input hook was not installed.\n");
        g_game_window = NULL;
        g_original_wndproc = NULL;
        goto done;
    }
    if (previous_wndproc) {
        g_original_wndproc = previous_wndproc;
    }

    OutputDebugStringA("DSTS RU: Cyrillic player-name input hook installed.\n");
    installed = TRUE;

done:
    ReleaseSRWLockExclusive(&g_hook_lock);
    return installed;
}


static DWORD WINAPI DstsRuHookWorker(LPVOID parameter) {
    DWORD attempt;

    (void)parameter;
    for (attempt = 0; attempt < 1200; ++attempt) {
        if (DstsRuInstallInputHook()) {
            InterlockedExchange(&g_hook_worker_started, 0);
            return 0;
        }
        Sleep(50);
    }

    OutputDebugStringA("DSTS RU: game window was not found before the input-hook timeout.\n");
    InterlockedExchange(&g_hook_worker_started, 0);
    return 1;
}


static void StartHookWorker(void) {
    HANDLE worker;

    if (InterlockedCompareExchange(&g_hook_worker_started, 1, 0) != 0) {
        return;
    }
    worker = CreateThread(NULL, 0, DstsRuHookWorker, NULL, 0, NULL);
    if (!worker) {
        InterlockedExchange(&g_hook_worker_started, 0);
        OutputDebugStringA("DSTS RU: input-hook worker could not be created.\n");
        return;
    }
    CloseHandle(worker);
}


DWORD WINAPI DstsRuInputFixVersion(void) {
    return 0x00010001;
}


static BOOL LoadSystemDinput8(void) {
    WCHAR path[MAX_PATH];
    UINT length;

    if (g_direct_input8_create) {
        return TRUE;
    }

    length = GetSystemDirectoryW(path, MAX_PATH);
    if (length == 0 || length >= MAX_PATH - 13) {
        return FALSE;
    }
    lstrcatW(path, L"\\dinput8.dll");
    g_system_dinput8 = LoadLibraryW(path);
    if (!g_system_dinput8) {
        return FALSE;
    }

    g_direct_input8_create = (DirectInput8CreateFn)GetProcAddress(
        g_system_dinput8,
        "DirectInput8Create"
    );
    return g_direct_input8_create != NULL;
}


HRESULT WINAPI DirectInput8Create(
    HINSTANCE instance,
    DWORD version,
    REFIID interface_id,
    LPVOID *output,
    LPUNKNOWN outer
) {
    HRESULT result;

    if (!LoadSystemDinput8()) {
        return HRESULT_FROM_WIN32(GetLastError() ? GetLastError() : ERROR_MOD_NOT_FOUND);
    }

    result = g_direct_input8_create(instance, version, interface_id, output, outer);
    if (!DstsRuInstallInputHook()) {
        StartHookWorker();
    }
    return result;
}


BOOL WINAPI DllMain(HINSTANCE instance, DWORD reason, LPVOID reserved) {
    (void)reserved;
    if (reason == DLL_PROCESS_ATTACH) {
        DisableThreadLibraryCalls(instance);
#ifndef DSTS_RU_DISABLE_DLLMAIN_WORKER
        StartHookWorker();
#endif
    }
    return TRUE;
}

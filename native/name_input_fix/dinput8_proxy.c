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
static HWND g_game_window;
static WNDPROC g_original_wndproc;


static LRESULT CALLBACK DstsRuWindowProc(
    HWND window,
    UINT message,
    WPARAM wparam,
    LPARAM lparam
) {
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

    return CallWindowProcA(g_original_wndproc, window, message, wparam, lparam);
}


static BOOL CALLBACK FindGameWindow(HWND window, LPARAM parameter) {
    DWORD process_id = 0;
    char class_name[64];

    (void)parameter;
    GetWindowThreadProcessId(window, &process_id);
    if (process_id != GetCurrentProcessId()) {
        return TRUE;
    }
    if (GetClassNameA(window, class_name, (int)sizeof(class_name)) <= 0) {
        return TRUE;
    }
    if (lstrcmpA(class_name, "GameMain") != 0) {
        return TRUE;
    }

    g_game_window = window;
    return FALSE;
}


BOOL WINAPI DstsRuInstallInputHook(void) {
    SetLastError(ERROR_SUCCESS);

    if (g_game_window && g_original_wndproc && IsWindow(g_game_window)) {
        /*
         * Never subclass the same live window twice.  A later overlay may
         * legitimately install its own WndProc and keep ours in its chain.
         * Hooking that overlay again would create ours -> overlay -> ours.
         */
        return TRUE;
    }

    g_game_window = NULL;
    g_original_wndproc = NULL;
    EnumWindows(FindGameWindow, 0);
    if (!g_game_window) {
        OutputDebugStringA("DSTS RU: GameMain window not found; Cyrillic input hook was not installed.\n");
        return FALSE;
    }

    SetLastError(ERROR_SUCCESS);
    g_original_wndproc = (WNDPROC)SetWindowLongPtrA(
        g_game_window,
        GWLP_WNDPROC,
        (LONG_PTR)DstsRuWindowProc
    );
    if (!g_original_wndproc && GetLastError() != ERROR_SUCCESS) {
        OutputDebugStringA("DSTS RU: SetWindowLongPtrA failed; Cyrillic input hook was not installed.\n");
        g_game_window = NULL;
        return FALSE;
    }

    OutputDebugStringA("DSTS RU: Cyrillic player-name input hook installed.\n");
    return TRUE;
}


DWORD WINAPI DstsRuInputFixVersion(void) {
    return 0x00010000;
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
    DstsRuInstallInputHook();
    return result;
}


BOOL WINAPI DllMain(HINSTANCE instance, DWORD reason, LPVOID reserved) {
    (void)reserved;
    if (reason == DLL_PROCESS_ATTACH) {
        DisableThreadLibraryCalls(instance);
    }
    return TRUE;
}

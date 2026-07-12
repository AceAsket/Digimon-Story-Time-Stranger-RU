#define WIN32_LEAN_AND_MEAN
#define COBJMACROS
#define DIRECTINPUT_VERSION 0x0800
#include <windows.h>
#include <dinput.h>
#include <stdio.h>


typedef BOOL(WINAPI *InstallHookFn)(void);
typedef DWORD(WINAPI *VersionFn)(void);
typedef HRESULT(WINAPI *DirectInput8CreateFn)(
    HINSTANCE,
    DWORD,
    REFIID,
    LPVOID *,
    LPUNKNOWN
);

static WPARAM g_last_char;
static WNDPROC g_overlay_original;


static LRESULT CALLBACK TestWindowProc(
    HWND window,
    UINT message,
    WPARAM wparam,
    LPARAM lparam
) {
    if (message == WM_CHAR) {
        g_last_char = wparam;
        return 0;
    }
    return DefWindowProcA(window, message, wparam, lparam);
}


static LRESULT CALLBACK OverlayWindowProc(
    HWND window,
    UINT message,
    WPARAM wparam,
    LPARAM lparam
) {
    return CallWindowProcA(g_overlay_original, window, message, wparam, lparam);
}


static int CheckCharacter(HWND window, WPARAM input, WPARAM expected) {
    g_last_char = 0;
    SendMessageA(window, WM_CHAR, input, 0);
    if (g_last_char != expected) {
        fprintf(
            stderr,
            "WM_CHAR 0x%llX -> 0x%llX, expected 0x%llX\n",
            (unsigned long long)input,
            (unsigned long long)g_last_char,
            (unsigned long long)expected
        );
        return 1;
    }
    return 0;
}


int main(int argc, char **argv) {
    WNDCLASSEXA window_class = {0};
    HMODULE proxy;
    InstallHookFn install_hook;
    VersionFn version;
    DirectInput8CreateFn direct_input8_create;
    IDirectInput8A *direct_input = NULL;
    HWND window;
    int failures = 0;

    if (argc != 2) {
        fprintf(stderr, "Usage: test_hook.exe <dinput8.dll>\n");
        return 2;
    }
    if (GetACP() != 1251) {
        fprintf(stderr, "This test requires Windows ACP 1251; current ACP is %u.\n", GetACP());
        return 2;
    }

    window_class.cbSize = sizeof(window_class);
    window_class.lpfnWndProc = TestWindowProc;
    window_class.hInstance = GetModuleHandleW(NULL);
    window_class.lpszClassName = "GameMain";
    if (!RegisterClassExA(&window_class)) {
        fprintf(stderr, "RegisterClassExA failed: %lu\n", GetLastError());
        return 2;
    }

    window = CreateWindowExA(
        0,
        "GameMain",
        "DSTS RU input hook test",
        WS_OVERLAPPED,
        0,
        0,
        320,
        200,
        NULL,
        NULL,
        window_class.hInstance,
        NULL
    );
    if (!window) {
        fprintf(stderr, "CreateWindowExA failed: %lu\n", GetLastError());
        return 2;
    }

    proxy = LoadLibraryA(argv[1]);
    if (!proxy) {
        fprintf(stderr, "LoadLibraryA failed: %lu\n", GetLastError());
        return 2;
    }
    install_hook = (InstallHookFn)GetProcAddress(proxy, "DstsRuInstallInputHook");
    version = (VersionFn)GetProcAddress(proxy, "DstsRuInputFixVersion");
    direct_input8_create = (DirectInput8CreateFn)GetProcAddress(proxy, "DirectInput8Create");
    if (!install_hook || !version || !direct_input8_create || !install_hook()) {
        fprintf(stderr, "Hook exports are missing or installation failed.\n");
        return 2;
    }
    if (version() != 0x00010000) {
        fprintf(stderr, "Unexpected input-fix version: 0x%08lX\n", version());
        return 2;
    }

    /* CP1251 bytes -> UTF-16: Юки, Алёна, Ёж. */
    failures += CheckCharacter(window, 0xDE, 0x042E);
    failures += CheckCharacter(window, 0xEA, 0x043A);
    failures += CheckCharacter(window, 0xE8, 0x0438);
    failures += CheckCharacter(window, 0xC0, 0x0410);
    failures += CheckCharacter(window, 0xEB, 0x043B);
    failures += CheckCharacter(window, 0xB8, 0x0451);
    failures += CheckCharacter(window, 0xED, 0x043D);
    failures += CheckCharacter(window, 0xE0, 0x0430);
    failures += CheckCharacter(window, 0xA8, 0x0401);
    failures += CheckCharacter(window, 0xE6, 0x0436);

    /* ASCII and editing controls must pass through untouched. */
    failures += CheckCharacter(window, 'A', 'A');
    failures += CheckCharacter(window, VK_BACK, VK_BACK);

    g_overlay_original = (WNDPROC)SetWindowLongPtrA(
        window,
        GWLP_WNDPROC,
        (LONG_PTR)OverlayWindowProc
    );
    if (!g_overlay_original) {
        fprintf(stderr, "Could not install simulated overlay WndProc.\n");
        failures++;
    }

    if (FAILED(direct_input8_create(
            GetModuleHandleW(NULL),
            DIRECTINPUT_VERSION,
            &IID_IDirectInput8A,
            (LPVOID *)&direct_input,
            NULL
        )) || !direct_input) {
        fprintf(stderr, "System DirectInput8Create forwarding failed.\n");
        failures++;
    } else {
        IDirectInput8_Release(direct_input);
    }
    if ((WNDPROC)GetWindowLongPtrA(window, GWLP_WNDPROC) != OverlayWindowProc) {
        fprintf(stderr, "Repeated hook installation replaced the overlay WndProc.\n");
        failures++;
    }
    failures += CheckCharacter(window, 0xDE, 0x042E);

    if (failures) {
        fprintf(stderr, "Input hook test failed: %d checks.\n", failures);
        return 1;
    }

    printf("Input hook test passed: CP1251 -> UTF-16, ASCII, Backspace, DirectInput forwarding, overlay chain.\n");
    return 0;
}

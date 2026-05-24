#include <windows.h>
#include <string>
#include <filesystem>
#include <iostream>

namespace fs = std::filesystem;

int main() {

    std::string url = "https://vidmoly.biz/embed-9yp0r3n1jw3o.html";
    std::string output = "video.mp4";

    std::string yt = fs::current_path().string() + "\\tools\\yt-dlp.exe";

    std::string cmd =
        "\"" + yt + "\" -f best -o \"" +
        output + "\" \"" +
        url + "\"";

    std::cout << "CMD: " << cmd << "\n";

    STARTUPINFOA si{};
    PROCESS_INFORMATION pi{};

    // IMPORTANT : CreateProcess modifie le buffer → donc copie writable
    char buffer[4096];
    strcpy_s(buffer, cmd.c_str());

    if (!CreateProcessA(
        NULL,
        buffer,
        NULL,
        NULL,
        FALSE,
        0,
        NULL,
        NULL,
        &si,
        &pi))
    {
        std::cout << "Erreur CreateProcess\n";
        return 1;
    }

    WaitForSingleObject(pi.hProcess, INFINITE);

    CloseHandle(pi.hProcess);
    CloseHandle(pi.hThread);

    std::cout << "Terminé\n";
    return 0;
}
#include "SandboxRunner.h"

#include "SecurityScanner.h"

#include <chrono>
#include <cstdio>
#include <filesystem>
#include <sstream>
#include <vector>

#ifdef _WIN32
#include <windows.h>
#endif

namespace {

std::string quote(const std::string& value) {
    return "\"" + value + "\"";
}

std::string joinFindings(const std::vector<std::string>& findings) {
    std::ostringstream output;

    for (std::size_t index = 0; index < findings.size(); ++index) {
        if (index > 0) {
            output << ", ";
        }
        output << findings[index];
    }

    return output.str();
}

}  // namespace

RunnerResult SandboxRunner::run(const RunnerTask& task) const {
    RunnerResult result;

    if (task.codeFile.empty()) {
        result.blocked = true;
        result.reason = "code_file is required";
        return result;
    }

    if (!std::filesystem::exists(task.codeFile)) {
        result.blocked = true;
        result.reason = "code_file not found: " + task.codeFile;
        return result;
    }

    SecurityScanner scanner;
    const std::vector<std::string> findings = scanner.scanFile(task.codeFile);

    if (!findings.empty()) {
        result.blocked = true;
        result.reason = "发现危险关键词: " + joinFindings(findings);
        result.returnCode = -1;
        return result;
    }

    return executePython(task);
}

RunnerResult SandboxRunner::executePython(const RunnerTask& task) const {
    RunnerResult result;
    const auto startedAt = std::chrono::steady_clock::now();

#ifdef _WIN32
    SECURITY_ATTRIBUTES securityAttributes;
    securityAttributes.nLength = sizeof(SECURITY_ATTRIBUTES);
    securityAttributes.bInheritHandle = TRUE;
    securityAttributes.lpSecurityDescriptor = nullptr;

    HANDLE readPipe = nullptr;
    HANDLE writePipe = nullptr;

    if (!CreatePipe(&readPipe, &writePipe, &securityAttributes, 0)) {
        result.stderrText = "failed to create output pipe";
        return result;
    }

    SetHandleInformation(readPipe, HANDLE_FLAG_INHERIT, 0);

    STARTUPINFOA startupInfo;
    ZeroMemory(&startupInfo, sizeof(startupInfo));
    startupInfo.cb = sizeof(startupInfo);
    startupInfo.dwFlags |= STARTF_USESTDHANDLES;
    startupInfo.hStdOutput = writePipe;
    startupInfo.hStdError = writePipe;
    startupInfo.hStdInput = GetStdHandle(STD_INPUT_HANDLE);

    PROCESS_INFORMATION processInfo;
    ZeroMemory(&processInfo, sizeof(processInfo));

    std::string command = "python " + quote(task.codeFile);
    std::string workingDir = task.workingDir.empty() ? std::filesystem::current_path().string() : task.workingDir;

    BOOL created = CreateProcessA(
        nullptr,
        command.data(),
        nullptr,
        nullptr,
        TRUE,
        CREATE_NO_WINDOW,
        nullptr,
        workingDir.c_str(),
        &startupInfo,
        &processInfo
    );

    CloseHandle(writePipe);

    if (!created) {
        CloseHandle(readPipe);
        result.stderrText = "failed to start python process";
        return result;
    }

    DWORD waitMs = task.timeoutSeconds > 0 ? static_cast<DWORD>(task.timeoutSeconds * 1000) : INFINITE;
    DWORD waitResult = WaitForSingleObject(processInfo.hProcess, waitMs);

    if (waitResult == WAIT_TIMEOUT) {
        TerminateProcess(processInfo.hProcess, 1);
        result.success = false;
        result.blocked = false;
        result.reason = "timeout";
        result.stderrText = "code execution timeout";
        result.returnCode = 1;
    } else {
        DWORD exitCode = 1;
        GetExitCodeProcess(processInfo.hProcess, &exitCode);
        result.returnCode = static_cast<int>(exitCode);
        result.success = result.returnCode == 0;
    }

    char buffer[4096];
    DWORD bytesRead = 0;
    while (ReadFile(readPipe, buffer, sizeof(buffer) - 1, &bytesRead, nullptr) && bytesRead > 0) {
        buffer[bytesRead] = '\0';
        result.stdoutText += buffer;
    }

    CloseHandle(readPipe);
    CloseHandle(processInfo.hProcess);
    CloseHandle(processInfo.hThread);
#else
    std::string command = "cd " + quote(task.workingDir.empty() ? "." : task.workingDir)
        + " && python " + quote(task.codeFile) + " 2>&1";
    FILE* pipe = popen(command.c_str(), "r");

    if (!pipe) {
        result.stderrText = "failed to start python process";
        return result;
    }

    char buffer[4096];
    while (fgets(buffer, sizeof(buffer), pipe) != nullptr) {
        result.stdoutText += buffer;
    }

    result.returnCode = pclose(pipe);
    result.success = result.returnCode == 0;
#endif

    const auto finishedAt = std::chrono::steady_clock::now();
    result.durationMs = std::chrono::duration_cast<std::chrono::milliseconds>(finishedAt - startedAt).count();

    return result;
}

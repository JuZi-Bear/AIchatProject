#include "SandboxRunner.h"

#include <filesystem>
#include <fstream>
#include <iostream>
#include <regex>
#include <sstream>
#include <string>

namespace {

std::string readFile(const std::string& path) {
    std::ifstream input(path);
    std::ostringstream buffer;
    buffer << input.rdbuf();
    return buffer.str();
}

std::string jsonStringValue(const std::string& json, const std::string& key, const std::string& defaultValue = "") {
    const std::regex pattern("\"" + key + "\"\\s*:\\s*\"([^\"]*)\"");
    std::smatch match;

    if (std::regex_search(json, match, pattern) && match.size() > 1) {
        return match[1].str();
    }

    return defaultValue;
}

int jsonIntValue(const std::string& json, const std::string& key, int defaultValue) {
    const std::regex pattern("\"" + key + "\"\\s*:\\s*(\\d+)");
    std::smatch match;

    if (std::regex_search(json, match, pattern) && match.size() > 1) {
        return std::stoi(match[1].str());
    }

    return defaultValue;
}

bool jsonBoolValue(const std::string& json, const std::string& key, bool defaultValue) {
    const std::regex pattern("\"" + key + "\"\\s*:\\s*(true|false)");
    std::smatch match;

    if (std::regex_search(json, match, pattern) && match.size() > 1) {
        return match[1].str() == "true";
    }

    return defaultValue;
}

std::string escapeJson(const std::string& value) {
    std::ostringstream output;

    for (char ch : value) {
        switch (ch) {
            case '\\':
                output << "\\\\";
                break;
            case '"':
                output << "\\\"";
                break;
            case '\n':
                output << "\\n";
                break;
            case '\r':
                output << "\\r";
                break;
            case '\t':
                output << "\\t";
                break;
            default:
                output << ch;
                break;
        }
    }

    return output.str();
}

std::string resolvePath(const std::filesystem::path& taskDir, const std::string& rawPath) {
    if (rawPath.empty()) {
        return "";
    }

    std::filesystem::path path(rawPath);
    if (path.is_relative()) {
        path = taskDir / path;
    }

    return std::filesystem::weakly_canonical(path).string();
}

void printResult(const RunnerResult& result) {
    std::cout
        << "{"
        << "\"success\":" << (result.success ? "true" : "false") << ","
        << "\"blocked\":" << (result.blocked ? "true" : "false") << ","
        << "\"reason\":\"" << escapeJson(result.reason) << "\","
        << "\"stdout\":\"" << escapeJson(result.stdoutText) << "\","
        << "\"stderr\":\"" << escapeJson(result.stderrText) << "\","
        << "\"returncode\":" << result.returnCode << ","
        << "\"duration_ms\":" << result.durationMs
        << "}"
        << std::endl;
}

RunnerResult errorResult(const std::string& message) {
    RunnerResult result;
    result.success = false;
    result.blocked = true;
    result.reason = message;
    result.returnCode = -1;
    return result;
}

}  // namespace

int main(int argc, char* argv[]) {
    if (argc < 2) {
        printResult(errorResult("usage: runner.exe task.json"));
        return 1;
    }

    std::filesystem::path taskPath(argv[1]);

    if (!std::filesystem::exists(taskPath)) {
        printResult(errorResult("task file not found"));
        return 1;
    }

    const std::string taskJson = readFile(taskPath.string());
    const std::filesystem::path taskDir = std::filesystem::absolute(taskPath).parent_path();

    RunnerTask task;
    task.codeFile = resolvePath(taskDir, jsonStringValue(taskJson, "code_file"));
    task.workingDir = resolvePath(taskDir, jsonStringValue(taskJson, "working_dir", "."));
    task.timeoutSeconds = jsonIntValue(taskJson, "timeout_seconds", 5);
    task.allowNetwork = jsonBoolValue(taskJson, "allow_network", false);

    SandboxRunner runner;
    RunnerResult result = runner.run(task);
    printResult(result);

    return result.success ? 0 : 1;
}

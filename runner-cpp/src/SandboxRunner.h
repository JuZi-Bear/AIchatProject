#pragma once

#include <string>

struct RunnerTask {
    std::string codeFile;
    std::string workingDir;
    int timeoutSeconds = 5;
    bool allowNetwork = false;
};

struct RunnerResult {
    bool success = false;
    bool blocked = false;
    std::string reason;
    std::string stdoutText;
    std::string stderrText;
    int returnCode = -1;
    long long durationMs = 0;
};

class SandboxRunner {
public:
    RunnerResult run(const RunnerTask& task) const;

private:
    RunnerResult executePython(const RunnerTask& task) const;
};

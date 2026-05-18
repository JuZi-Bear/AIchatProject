#include "SecurityScanner.h"

#include <fstream>
#include <sstream>

std::vector<std::string> SecurityScanner::dangerousKeywords() const {
    return {
        "os.remove",
        "shutil.rmtree",
        "subprocess",
        "eval(",
        "exec(",
        "socket",
        "requests",
        "urllib",
        "open(",
        "pathlib.Path.unlink",
    };
}

std::vector<std::string> SecurityScanner::scanFile(const std::string& codeFile) const {
    std::ifstream input(codeFile);
    std::vector<std::string> findings;

    if (!input.is_open()) {
        findings.push_back("code_file_not_readable");
        return findings;
    }

    std::ostringstream buffer;
    buffer << input.rdbuf();
    const std::string code = buffer.str();

    for (const std::string& keyword : dangerousKeywords()) {
        if (code.find(keyword) != std::string::npos) {
            findings.push_back(keyword);
        }
    }

    return findings;
}

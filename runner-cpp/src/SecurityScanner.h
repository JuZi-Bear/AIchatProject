#pragma once

#include <string>
#include <vector>

class SecurityScanner {
public:
    std::vector<std::string> scanFile(const std::string& codeFile) const;

private:
    std::vector<std::string> dangerousKeywords() const;
};

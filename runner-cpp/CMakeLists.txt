cmake_minimum_required(VERSION 3.16)

project(ai_agent_runner_sandbox LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

add_executable(runner
    src/main.cpp
    src/SandboxRunner.cpp
    src/SecurityScanner.cpp
)

target_include_directories(runner PRIVATE src)

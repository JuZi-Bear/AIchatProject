# runner-cpp

## 目录作用

`runner-cpp/` 是 v2.0 平台化升级轨中的 C++ Runner Sandbox 最小版本。它为后续增强代码执行安全性提供工程入口，但当前默认不替代 Python Runner。

当前版本是命令行执行器：

```powershell
runner.exe task.json
```

示例任务：

```json
{
  "code_file": "../output/generated_code.py",
  "timeout_seconds": 5,
  "working_dir": "../output",
  "allow_network": false
}
```

## 核心文件

- `CMakeLists.txt`：CMake 构建配置。
- `src/main.cpp`：命令行入口。
- `src/SandboxRunner.cpp`、`src/SandboxRunner.h`：任务读取、执行和 JSON 输出。
- `src/SecurityScanner.cpp`、`src/SecurityScanner.h`：危险关键词扫描。
- `examples/sample_task.json`：示例任务。

## 当前能力

- 读取 JSON 任务文件。
- 检查 `code_file` 是否存在。
- 扫描生成的 Python 代码危险关键词。
- 调用 `python` 执行目标文件。
- 捕获退出码和合并输出。
- 向 stdout 输出 JSON 结果。

危险关键词扫描当前会阻断：

- `os.remove`
- `shutil.rmtree`
- `subprocess`
- `eval(`
- `exec(`
- `socket`
- `requests`
- `urllib`
- `open(`
- `pathlib.Path.unlink`

## 构建

```powershell
cd runner-cpp
cmake -S . -B build
cmake --build build --config Release
```

Windows 上可执行文件通常生成在：

```text
runner-cpp/build/Release/runner.exe
```

Python 适配层还会检查：

```text
runner-cpp/build/runner.exe
runner-cpp/build/Debug/runner.exe
```

## 不能随便修改

- 不要把 C++ Runner 设置为默认执行器。
- 不要删除 Python Runner fallback。
- 不要声称当前版本提供完整安全隔离。
- 不要绕过 `SecurityScanner` 直接执行代码。

## 轨道归属

v2-platform / experimental。

## 当前开发状态

experimental。

## 当前限制

这是最小预览版，不是完整沙箱。它提供更可控的执行入口和未来集成点，但还不是强隔离边界。后续可以增加 Windows Job Object、受限 token、文件系统 allowlist、更强 timeout、内存限制、网络隔离和稳定服务协议。

# C++ Runner Sandbox

v2.0 第十五步新增 `runner-cpp/`，作为 C++ 安全执行器的最小可运行版本。它不会替换现有 Python Runner，默认配置仍然是 `runner_mode: python`，因此 v1.0 Streamlit、FastAPI、Java、Vue 和 Docker 现有链路保持兼容。

## 为什么引入 C++ Runner

- 增强工程亮点：把 AI 生成代码的执行边界从 Python 业务流程中拆出来。
- 提高可控性：后续可以在 C++ 层加入更强的进程、文件系统、网络和资源限制。
- 降低耦合：Python Agent Engine 继续负责 LangGraph 和 Agent，Runner Sandbox 只负责执行。

## 当前最小能力

当前版本是命令行程序：

```powershell
runner.exe task.json
```

任务文件示例：

```json
{
  "code_file": "../output/generated_code.py",
  "timeout_seconds": 5,
  "working_dir": "../output",
  "allow_network": false
}
```

执行流程：

1. 读取 JSON 任务文件。
2. 检查 `code_file` 是否存在。
3. 扫描危险关键词。
4. 调用 `python` 执行目标文件。
5. 输出 JSON 结果。

## 安全扫描关键词

当前会阻断以下关键词：

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

命中后不会执行代码，返回：

```json
{
  "success": false,
  "blocked": true,
  "reason": "发现危险关键词: subprocess",
  "stdout": "",
  "stderr": "",
  "returncode": -1
}
```

## 如何编译

```powershell
cd runner-cpp
cmake -S . -B build
cmake --build build --config Release
```

Windows 常见输出路径：

```text
runner-cpp/build/Release/runner.exe
```

Python 适配层也会检查：

```text
runner-cpp/build/runner.exe
runner-cpp/build/Debug/runner.exe
```

## 如何运行

```powershell
cd runner-cpp
.\build\Release\runner.exe .\examples\sample_task.json
```

成功示例：

```json
{
  "success": true,
  "blocked": false,
  "stdout": "...",
  "stderr": "",
  "returncode": 0,
  "duration_ms": 123
}
```

## 与 Python code_runner 集成

`config/settings.yaml` 新增：

```yaml
runner_mode: python
```

可选值：

- `python`：继续使用现有 Python subprocess Runner。
- `cpp`：优先调用 C++ Runner。

当设置为 `cpp` 但尚未编译 `runner.exe` 时，`utils/cpp_runner_adapter.py` 会返回 fallback 标记，`utils/code_runner.py` 会自动回退 Python Runner，并在运行结果和 `run_summary` 中写入 `runner_warning`。

## 当前限制

- 当前版本是最小可运行雏形，不是完整强隔离沙箱。
- Windows 优先，非 Windows 仅提供基础命令执行分支。
- stdout/stderr 在 Windows 当前合并捕获到 stdout。
- 危险关键词扫描是静态字符串扫描，后续需要 AST、策略配置和 allowlist。

## 后续增强方向

- Windows Job Object 限制 CPU、内存和进程树。
- Restricted Token / AppContainer 降低权限。
- 文件系统 allowlist 和临时工作目录隔离。
- 网络禁用或代理策略。
- Runner HTTP/gRPC 服务化。
- 与 Java 平台任务队列、审计和团队权限系统联动。

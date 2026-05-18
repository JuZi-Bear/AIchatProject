# 风险与解决方案

> 早期风险文档：本文保留 v1.0 风险预案和部分 v2.0 Runner 说明。当前双轨稳定性、现场兜底和平台化风险主文档请优先阅读 `docs/RISK_AND_STABILITY.md`。

## API Key 缺失

风险：未配置 `DEEPSEEK_API_KEY`、`QWEN_API_KEY` 或 `GLM_API_KEY` 时，在线模型无法调用。

解决方案：

- 使用 `.env.example` 创建 `.env`。
- Web UI 会提示缺少 API Key。
- 可以设置 `OFFLINE_MODE=true` 使用离线演示响应。

## 网络不可用

风险：比赛现场网络不稳定，导致模型 API 无法访问。

解决方案：

- 赛前准备离线模式。
- 系统在 API 调用失败时会自动使用预置演示响应。
- Docker 和本地依赖提前安装，避免现场下载依赖。

## 模型调用失败

风险：模型接口超时、额度不足、base_url 配置错误或返回格式异常。

解决方案：

- `model_manager.py` 统一管理模型配置和错误提示。
- Agent 调用失败时回退到 `offline_demo.py`。
- Web UI 显示当前模型和 API Key 状态。

## 生成代码不安全

风险：AI 生成代码可能包含删除文件、执行命令或动态执行代码。

解决方案：

- `utils/code_runner.py` 在执行前检查危险关键词。
- 禁止 `os.remove`、`shutil.rmtree`、`subprocess`、`eval`、`exec`。
- Approval Node 要求人工确认后才运行代码。
- Security Agent 在插件阶段再次检查安全风险。
- v2.0 已新增 `runner-cpp/` C++ Runner Sandbox 最小版本。默认仍使用 Python Runner；当 `runner_mode=cpp` 且 `runner.exe` 已编译时，会先由 C++ 层扫描危险关键词再执行。未编译时自动回退 Python Runner，并在 `runner_warning` 中提示。

## C++ Runner 未编译或不可用

风险：将 `runner_mode` 设置为 `cpp` 后，如果没有编译 `runner-cpp/build/runner.exe`，可能导致用户误以为已经使用 C++ Runner。

解决方案：

- `utils/cpp_runner_adapter.py` 会检测 runner 是否存在。
- runner 不存在时自动回退 Python Runner，不影响演示和原有流程。
- `run_summary.runner_warning`、Web UI 和 Vue 前端会展示回退提示。
- 编译方法见 `docs/CPP_RUNNER_SANDBOX.md`。

## 测试失败

风险：生成代码能运行，但不满足需求或边界情况处理不完整。

解决方案：

- Tester Agent 自动生成 pytest 测试。
- 失败时把测试代码、pytest 输出和 stderr 交给 Sentry Agent。
- Coder Agent 根据 Sentry 结果修复业务代码。
- 修复次数超过上限后停止并生成报告。

## Docker 启动失败

风险：Docker Desktop 未启动、端口冲突、镜像构建失败或 `.env` 未配置。

解决方案：

- 确认 Docker Desktop 处于运行状态。
- 使用 `docker compose up --build` 查看完整日志。
- 端口 8501 被占用时关闭占用进程或修改端口映射。
- 确认 `requirements.txt` 和 `.env` 存在。

## 依赖安装失败

风险：pip 网络不稳定、Python 版本不兼容或虚拟环境损坏。

解决方案：

- 优先运行 `install.bat`。
- 确认 Python 版本为 3.11。
- 删除并重建 `.venv`。
- 网络不稳定时提前在稳定网络环境安装依赖。

## Python 版本不兼容

风险：过旧 Python 版本可能不兼容 LangGraph、Streamlit 或类型语法。

解决方案：

- 推荐 Python 3.11。
- Docker 镜像固定为 `python:3.11-slim`。
- 新设备部署时先运行 `python --version` 检查版本。

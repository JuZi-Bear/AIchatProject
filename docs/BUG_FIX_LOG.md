# v1.0 Bug 修复记录

用于记录稳定性测试中发现并修复的问题。

## BUG-001

- 问题编号：BUG-001
- 问题描述：`start_demo.bat` 在依赖缺失时只检查 Python，不会明确提示先运行 `install.bat`。
- 复现步骤：
  1. 在未安装依赖的新环境运行 `start_demo.bat`。
  2. 选择 Web UI 或 CLI。
  3. 可能直接进入 Python 导入错误。
- 原因分析：启动脚本没有预检查 `streamlit`、`rich`、`langgraph`、`openai`、`dotenv`、`yaml` 等关键依赖。
- 修复方案：在 `start_demo.bat` 中增加依赖导入检查，失败时提示先运行 `install.bat`。
- 是否已修复：已修复。

## BUG-002

- 问题编号：BUG-002
- 问题描述：`install.bat` 提示 Python 3.10 或更高，但项目交付文档推荐 Python 3.11。
- 复现步骤：
  1. 打开 `install.bat`。
  2. 查看 Python 缺失提示。
- 原因分析：早期脚本提示未随 Docker 和交付文档统一到 Python 3.11。
- 修复方案：更新安装脚本提示为推荐 Python 3.11，并打印当前 Python 版本。
- 是否已修复：已修复。

## BUG-003

- 问题编号：BUG-003
- 问题描述：稳定性测试会生成 `tests/test_generated_code.py`、报告和运行历史，容易误加入 Git。
- 复现步骤：
  1. 执行 LangGraph 稳定性测试。
  2. 查看 `git status`。
  3. 发现自动生成的 pytest 文件可能显示为未跟踪文件。
- 原因分析：`.gitignore` 忽略了 `output/`，但没有忽略自动生成测试文件、报告和运行 JSON。
- 修复方案：更新 `.gitignore`，忽略 `reports/`、`runs/*.json` 和 `tests/test_generated_code.py`。
- 是否已修复：已修复。

## BUG-004

- 问题编号：BUG-004
- 问题描述：`.env.example` 和文档提供 `DEEPSEEK_MODEL`、`DEEPSEEK_BASE_URL`，但 `model_manager.py` 优先使用 `config/models.yaml`，环境变量覆盖不明显。
- 复现步骤：
  1. 设置 `DEEPSEEK_MODEL=deepseek-v4-pro`。
  2. 调用 `get_current_model_info("deepseek")`。
  3. 旧逻辑仍可能显示 `deepseek-chat`。
- 原因分析：模型配置读取后没有应用环境变量覆盖。
- 修复方案：在 `model_manager.py` 中增加 `apply_env_overrides()`，支持 `DEEPSEEK_MODEL`、`DEEPSEEK_BASE_URL`，并兼容 Qwen / GLM 的同类变量。
- 是否已修复：已修复。

## BUG-005

- 问题编号：BUG-005
- 问题描述：README 中有 `docs/DEMO_FLOW.md` 链接，但缺少单独的“比赛演示流程”章节。
- 复现步骤：
  1. 打开 README。
  2. 查找“比赛演示流程”。
- 原因分析：README 已有材料入口，但比赛现场操作顺序不够直接。
- 修复方案：新增“比赛演示流程”章节，列出 Web UI 演示步骤。
- 是否已修复：已修复。

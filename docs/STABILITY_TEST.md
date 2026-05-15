# v1.0 稳定性测试记录

本文件用于记录比赛交付前的稳定性测试项和当前检查结果。当前阶段只做 Bug 修复、提示优化和文档完善，不新增新架构功能。

## 环境测试

- [x] Python 版本是否为 3.11
  - 本机测试结果：Python 3.11.9。
- [x] 虚拟环境是否能正常激活
  - `.venv\Scripts\python.exe` 可正常执行。
- [x] requirements.txt 是否能完整安装
  - `pip`、`streamlit`、`langgraph`、`openai`、`pytest`、`coverage` 已可用。
- [x] .env 是否配置正确
  - `.env.example` 已包含 DeepSeek、Qwen、GLM 和离线模式配置项。
- [x] API Key 缺失时是否有清晰提示
  - Agent 会提示缺少对应 API Key，并建议配置 `.env` 或启用离线模式。

## CLI 测试

- [x] `python graph_demo.py` 是否能启动
  - 已验证菜单可正常显示。
- [x] 简单案例是否能成功运行
  - 离线模式和 DeepSeek 在线模式均可运行简单 hello world 案例。
- [x] 翻车修复案例是否能触发自动修复
  - 离线模式下 input 案例触发修复，`retry_count=1`，最终成功。
- [x] 综合案例是否能生成报告
  - 报告生成逻辑已通过轻量 smoke test。
- [x] 人工审批是否生效
  - `approved=False` 时 Runner 不执行，`error_log=用户拒绝执行 AI 生成代码`。

## Web UI 测试

- [x] `python -m streamlit run webui.py` 是否能启动
  - 临时端口 8502 启动并访问成功，HTTP 200。
- [x] 演示案例是否能选择
  - Web UI 可导入 `demo_cases.py`，侧边栏案例配置正常。
- [x] 插件是否能开关
  - Web UI 读取和写回 `config/agents.yaml` 的逻辑可用。
- [x] 模型是否能选择
  - DeepSeek / Qwen / GLM 配置可读取。
- [x] 运行结果是否能展示
  - `build_run_summary()` 和 `build_workflow_status()` 可正常生成展示数据。
- [x] 报告是否能查看
  - `build_report_display_data()` 可读取报告文件并生成展示数据。
- [x] 历史记录是否能查看
  - `utils/run_store.py` 的保存和读取通过 smoke test。
- [x] 演示模式/开发模式是否正常
  - 演示模式错误摘要和开发模式完整日志逻辑可用。

## Docker 测试

- [x] `docker compose up --build` 是否能启动
  - 已实际执行 `docker compose up --build -d`，镜像构建和容器启动成功。
- [x] `http://localhost:8501` 是否能访问
  - Docker Web UI 访问返回 HTTP 200。
- [x] `.env` 是否能被 Docker 读取
  - `docker-compose.yml` 使用 `env_file: .env`，并显式传入模型环境变量。
- [x] `reports/` 和 `output/` 是否能挂载保存
  - `docker-compose.yml` 已挂载 `reports/`、`output/`、`runs/`。

## 核心功能测试

- [x] Product Agent 是否输出需求拆解
  - DeepSeek 在线 smoke test 已能调用模型；离线兜底也可输出需求拆解。
- [x] Coder Agent 是否生成代码
  - 简单 hello world 案例可生成并保存代码。
- [x] Tester Agent 是否生成 pytest
  - 自动生成 `tests/test_generated_code.py`，测试通过后不纳入 Git。
- [x] Runner 是否能执行代码
  - `stdout=hello world`，returncode 为成功。
- [x] Sentry Agent 是否能分析错误
  - 翻车修复案例可触发 Sentry，并最终修复成功。
- [x] 自动修复次数是否受 `max_retry_count` 控制
  - 测试时传入 `max_retry_count=1/2` 均能写入流程。
- [x] Quality Score 是否能生成
  - 简单案例质量评分为 100。
- [x] run_summary 是否能生成
  - `build_run_summary(state)` smoke test 通过。
- [x] 插件结果是否能写入报告
  - `plugin_results_count=4`，报告生成逻辑可读取插件结果。

## DeepSeek 在线测试记录

测试时间：2026-05-16

测试配置：

- provider：DeepSeek
- model：`deepseek-v4-pro`
- base_url：`https://api.deepseek.com`
- API Key：使用临时环境变量注入，未写入代码或文档。
- OFFLINE_MODE：false

测试结果：

- API smoke test：通过。
- LangGraph 简单案例：通过。
- `success=True`
- `test_success=True`
- `retry_count=0`
- `quality_score=100`
- `plugin_results=4`
- `stdout=hello world`

## 本次稳定性结论

当前 v1.0 交付版已满足比赛现场演示的基础稳定性要求。推荐正式比赛前在目标设备上再执行一次：

```powershell
.\install.bat
python graph_demo.py
python -m streamlit run webui.py
docker compose up --build
```

## Docker 实测记录

测试时间：2026-05-16

- `docker compose config --quiet`：通过。
- `docker compose up --build -d`：通过。
- Web UI 容器访问：`http://localhost:8501` 返回 HTTP 200。
- 测试后已执行 `docker compose down` 关闭并移除容器。

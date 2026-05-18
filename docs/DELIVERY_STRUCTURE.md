# 最终提交目录结构

> 交付历史文档：本文保留 v1.0 比赛提交时的目录说明。当前完整项目目录和双轨归属请优先阅读 `docs/PROJECT_DIRECTORY_GUIDE.md`，文档总入口见 `docs/DOCUMENT_INDEX.md`。

本项目按“核心流程、智能体能力、插件扩展、工具函数、配置管理、演示入口、文档材料”组织，便于比赛提交、现场讲解和后续扩展。

## 顶层结构

```text
AIchatProject/
├── core/
├── agents/
├── plugins/
├── utils/
├── config/
├── docs/
├── reports/
├── runs/
├── output/
├── tests/
├── agents.py
├── graph.py
├── graph_demo.py
├── main.py
├── webui.py
├── demo_cases.py
├── model_manager.py
├── plugin_loader.py
├── report_generator.py
├── offline_demo.py
├── quality_evaluator.py
├── requirements.txt
├── install.bat
├── start_demo.bat
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
├── .env.example
└── README.md
```

## 核心流程

- `core/`：核心工作流模块。
- `core/state.py`：定义 LangGraph 使用的 `AgentState`。
- `core/workflow.py`：构建 LangGraph 状态机，负责 Product、Coder、Tester、Approval、Runner、Sentry、Plugins、Quality、Report 节点流转。
- `core/quality_evaluator.py`：质量评分逻辑。
- `graph.py`：兼容入口，对外继续导出 `build_graph()` 和 `run_graph_demo()`。

## Agent 能力

- `agents.py`：主要 Agent 函数入口，包含 Product Agent、Coder Agent、Tester Agent、Sentry Agent。
- `agents/`：保留给后续拆分更多 Agent 文件使用。
- `offline_demo.py`：离线模式和 API 失败时使用的预置演示响应。

## 插件系统

- `plugins/`：自定义 AI 模块目录。
- `plugins/base_plugin.py`：插件基类，规范统一返回结构。
- `plugins/doc_agent.py`：生成 README 风格说明。
- `plugins/security_agent.py`：检查危险代码关键词。
- `plugins/refactor_agent.py`：给出代码重构建议。
- `plugins/ui_agent.py`：给出 UI 设计建议。
- `plugins/plugin_template.py`：新插件开发模板。
- `plugin_loader.py`：读取 `config/agents.yaml`，按顺序执行启用插件。

## 工具函数

- `utils/`：运行、测试、错误处理、状态摘要和历史保存工具。
- `utils/code_runner.py`：保存和运行生成代码，并做安全检查。
- `utils/test_runner.py`：保存 pytest 测试并运行 pytest + coverage。
- `utils/error_utils.py`：统一错误摘要、演示模式错误格式化和可重试判断。
- `utils/summary_builder.py`：生成统一运行摘要 `run_summary`。
- `utils/ui_state_builder.py`：生成 Web UI 展示所需的工作流状态、插件展示数据和报告展示数据。
- `utils/run_store.py`：保存和读取 `runs/{run_id}.json`。
- `utils/model_comparator.py`：生成多模型对比表格和对比报告。

## 配置管理

- `config/`：项目配置目录。
- `config/settings.yaml`：默认修复次数、离线模式、人工审批和保存策略。
- `config/models.yaml`：DeepSeek、Qwen、GLM 模型配置。
- `config/agents.yaml`：插件启用/关闭配置。
- `config/config_loader.py`：YAML 配置读取工具。
- `.env.example`：环境变量模板，不包含真实 API Key。

## 演示入口

- `webui.py`：Streamlit Web UI，比赛现场推荐入口。
- `graph_demo.py`：LangGraph CLI 演示入口。
- `main.py`：早期 CLI 流程，保留兼容。
- `demo_cases.py`：演示案例文本。
- `install.bat`：Windows 一键安装依赖。
- `start_demo.bat`：Windows 一键选择 CLI 或 Web UI。

## 文档材料

- `docs/`：项目说明、答辩材料、操作手册和设计文档。
- `docs/OPERATION_GUIDE.md`：部署和操作指南。
- `docs/USER_MANUAL.md`：跨设备部署和使用手册。
- `docs/DEMO_SCRIPT.md`：演示案例和讲稿。
- `docs/DEMO_FLOW.md`：比赛现场操作流程。
- `docs/PRESENTATION_OUTLINE.md`：答辩大纲。
- `docs/DEFENSE_QA.md`：评委问答准备。
- `docs/SCORE_POINTS.md`：评分点包装。
- `docs/FINAL_CHECKLIST.md`：交付前检查清单。
- `docs/DELIVERY_STRUCTURE.md`：本文件，说明提交结构。
- `docs/INNOVATION_POINTS.md`：创新点总结。
- `docs/RISK_AND_SOLUTION.md`：风险与解决方案。
- `docs/TECH_STACK.md`：技术栈说明。
- `docs/UI_SPEC.md`：Web UI 和 Figma 设计规格。
- `docs/PLUGIN_GUIDE.md`：插件开发指南。

## 运行产物

- `reports/`：Markdown 运行报告和模型对比报告。
- `runs/`：每次运行的完整状态 JSON。
- `output/`：生成的 Python 代码和兼容报告产物。
- `tests/`：Tester Agent 自动生成的 pytest 测试文件。

## Docker 与依赖

- `Dockerfile`：基于 `python:3.11-slim` 构建 Python 镜像，可由 Compose command 启动 Streamlit 或 FastAPI。
- `docker-compose.yml`：一键启动 `mysql`、`ai-agent-api`、`backend-java`、`frontend-vue`、`streamlit-web` 多服务，并挂载 `reports/`、`runs/`、`output/`。
- `.dockerignore`：避免打包虚拟环境、缓存、Git 信息和敏感 `.env`。
- `requirements.txt`：Python 依赖清单。
- `README.md`：项目总入口说明。

# 模块边界说明

本文说明项目主要模块的职责边界。后续修改应优先在所属模块内完成，避免跨层重写。

## Python Agent Engine

职责：

- LangGraph 工作流编排。
- Agent 执行、测试、修复、评分和报告生成。
- 为 Streamlit、FastAPI 和 Java Gateway 提供核心能力。

边界：

- 不让 Vue 或 Java 直接解析 LangGraph 内部 state。
- 不随意改变 `run_summary` 和 `ui_view_model` 字段语义。
- 不把平台用户、权限、团队协作逻辑塞回 Python Agent 核心。

## Streamlit v1 Demo

职责：

- 比赛现场稳定演示。
- 展示 Agent 过程、最终结果、报告和配置入口。

边界：

- 不删除 `webui.py`、`graph_demo.py`、`start_demo.bat`。
- 不让 v2 平台重构直接阻断 v1 启动。

## FastAPI API Layer

职责：

- 暴露 Python Agent Engine HTTP API。
- 接收请求并返回 `run_summary`、`ui_view_model`、报告和历史数据。

边界：

- API 层不写复杂业务逻辑。
- API 层不直接解析或重组 LangGraph 内部细节。

## Vue Frontend

职责：

- v2 平台前端展示。
- 支持 Python Direct 和 Java Gateway 两种 API 模式。
- 展示 Dashboard、运行控制台、历史、报告、模型和插件配置。

边界：

- 不直接读取本地文件系统。
- 不直接依赖 LangGraph state。
- 不把后端配置硬编码到组件中，应通过 API client 和环境变量处理。

## Java Platform Service

职责：

- API Gateway。
- MySQL 任务记录、报告索引、平台统计、前端配置、模型和插件配置管理。

边界：

- 不替代 Python Agent Engine。
- 原有代理接口保持兼容。
- 新平台接口使用统一响应结构，不破坏旧代理响应。

## MySQL

职责：

- 保存 Java 平台层运行记录、报告索引、配置和统计基础数据。

边界：

- 大文本报告正文仍可保存在 `reports/`。
- Python Direct 模式仍可使用 `runs/` 和 `reports/` 文件。

## C++ Runner Sandbox

职责：

- 作为未来安全执行器增强点。
- 当前最小能力是扫描危险关键词并执行 Python 文件。

边界：

- 默认不替代 Python Runner。
- 未编译或不可用时必须回退 Python Runner。
- 当前不声称提供完整安全隔离。

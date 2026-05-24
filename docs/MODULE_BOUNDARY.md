# 模块边界说明

本文说明 v2-only 版本的主要模块职责边界。后续修改应优先在所属模块内完成，避免跨层重写。

## Vue Frontend

职责：

- 提供 v2 平台前端。
- 展示 Dashboard、RunConsole、History、Reports、Agents、Workflow Templates、Workflow Editor 和 Replay。
- 通过 Java Gateway 访问平台 API。
- 展示 RunEvent、SSE、CodeAgent 审计、Workflow 回放和 Figma 风编辑器。

边界：

- 不直接调用大模型。
- 不直接执行本地文件操作，文件操作必须通过 CodeAgent API。
- 不解析 LangGraph 内部 state，优先消费 `run_summary`、`ui_view_model` 和事件数据。

## Java Platform Service

职责：

- API Gateway。
- MySQL 运行记录、报告索引、平台统计、设置、模型配置、插件配置、Workflow 模板和 RunEvent。
- SSE 实时事件推送。
- 调用 Python FastAPI Agent Engine。

边界：

- 不实现 Agent 逻辑。
- 不执行 AI 生成代码。
- 原有代理接口保持兼容。

## Python Agent Engine

职责：

- FastAPI 暴露 Agent Engine API。
- LangGraph 工作流编排。
- Agent 执行、测试、修复、评分、报告生成。
- 输出 `state`、`run_summary`、`ui_view_model`、`workflow_events`。

边界：

- 不承担平台用户、权限、团队协作和 MySQL 业务管理。
- 不让 API 层直接堆复杂业务逻辑。
- 不随意改变跨层稳定契约。

## Shared Python Core

包含：

- `core/`
- `agents.py`
- `agent_registry/`
- `prompts/`
- `workflow_templates/`
- `plugins/`
- `utils/`
- `config/`

边界：

- 修改 LangGraph 主流程前必须先确认对 API、Java、Vue、Replay 和报告的影响。
- Prompt 修改优先改 `prompts/`，保留必要 fallback。
- CodeAgent 文件操作必须遵守 `config/settings.yaml` 的路径策略和审计要求。

## MySQL

职责：

- 保存 Java 平台层运行记录、事件、报告索引、配置和模板。

边界：

- 大文本报告正文仍可保存在 `reports/`。
- JSONL 审计日志仍可保存在 `output/`。
- 表结构变更需保持 JPA `ddl-auto=update` 可兼容。

## C++ Runner Sandbox

职责：

- 作为未来安全执行器增强点。
- 当前最小能力是扫描危险关键词并执行 Python 文件。

边界：

- 默认不替代 Python Runner。
- 未编译或不可用时必须回退 Python Runner。
- 当前不声称提供完整安全隔离。

## Docker Compose

职责：

- 统一启动 v2 平台链路：`mysql`、`ai-agent-api`、`backend-java`、`frontend-vue`。

边界：

- 不再维护旧 Python 页面服务。
- 不把本地生成产物写入镜像。
- 端口和服务名变更必须同步 README、Docker 指南和启动脚本。

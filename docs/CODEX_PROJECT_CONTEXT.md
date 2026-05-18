# Codex Project Context

本文给 Codex 或其他协作者提供项目上下文。修改代码前应先阅读本文、`MODULE_BOUNDARY.md` 和 `DUAL_TRACK_ARCHITECTURE.md`。

## 项目定位

AI Multi-Agent Pipeline 是一个多智能体自主开发流水线项目。它从自然语言需求出发，通过 Product Agent、Coder Agent、Tester Agent、Runner、Sentry Agent 和插件模块完成代码生成、测试、错误分析、自动修复、质量评分和报告生成。

## 当前架构状态

项目处于双轨并行阶段：

- v1-demo：Python + LangGraph + Streamlit，比赛现场稳定演示。
- v2-platform：Vue3 + TypeScript + Java Spring Boot + MySQL + FastAPI + C++ Runner Sandbox，平台化升级预览。

## 关键稳定契约

- `run_summary` 是前端、Java 和报告索引都依赖的摘要结构。
- `ui_view_model` 是 Vue 和 Streamlit 展示工作流结果的稳定数据视图。
- `agent_registry/` 是 Agent 元信息注册中心，后续可视化编排应优先读取这里的 key、stage、输入输出字段。
- `prompts/` 是 Prompt 模板目录，后续修改 Agent Prompt 时优先改 Markdown 模板。
- FastAPI 层只做 API 适配，复杂业务由 `services/run_service.py` 和共享核心承担。
- Java 层当前是 API Gateway + MySQL 平台数据视图，不替代 Python Agent Engine。
- C++ Runner 当前是可选增强，默认仍使用 Python Runner。

## 修改优先级

1. 保持 v1.0 Streamlit 演示可运行。
2. 保持 v2.0 Python Direct 和 Java Gateway 模式可运行。
3. 保持 Docker Compose 服务名和端口稳定。
4. 修改后同步更新文档。

## 修改后最低验证要求

后续任何代码修改后，至少验证：

- v1.0 Streamlit 是否仍可启动。
- v2.0 FastAPI 是否仍可启动。
- 如果修改了前端，则测试 Vue。
- 如果修改了 Java，则测试 Java + MySQL。
- 如果修改了 Docker，则测试 `docker compose`。

详细测试步骤见 `docs/DUAL_TRACK_TEST_CHECKLIST.md`，启动顺序见 `docs/STARTUP_ORDER.md`，结果记录到 `docs/TEST_RESULT_LOG.md`。

## 后续工作原则

- 优先修复 P0 / P1。
- 不主动删除代码。
- 涉及架构取舍必须询问用户。
- v1.0 演示稳定性优先。
- v2.0 平台能力逐步推进。
- 文档不一致可以直接修。
- 核心代码重构需要用户确认。
- 问题分级见 `docs/ISSUE_TRIAGE.md`，修复计划见 `docs/FIX_PLAN.md`，下一步队列见 `docs/NEXT_ACTION_QUEUE.md`。
- 后续涉及框架扩展时，必须先参考 `docs/FRAMEWORK_EXTENSION_PLAN.md`。
- 不要直接新增复杂功能，应先确认扩展方向是否在 `docs/RECOMMENDED_EXTENSION_ROADMAP.md` 中。
- 不要在 Python 代码中新增大段硬编码 Prompt；如需调 Prompt，优先修改 `prompts/` 下对应 `.md` 文件，并保留代码 fallback。
- Agent 元信息新增或调整时，优先更新 `agent_registry/default_agents.py`，不要让 Vue 或 Java 直接猜测 Agent 列表。
- 框架扩展边界见 `docs/FRAMEWORK_EXTENSION_BOUNDARY.md`；候选扩展评估见 `docs/FRAMEWORK_EXTENSION_CANDIDATES.md`。

## 当前重点入口

- v1 演示：`webui.py`、`graph_demo.py`
- v2 Python API：`api_server.py`
- v2 前端：`frontend-vue/`
- v2 Java：`backend-java/`
- 多服务启动：`docker-compose.yml`
- 文档导航：`docs/DOCUMENT_INDEX.md`

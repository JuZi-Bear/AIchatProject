# 技术框架扩展边界

本文定义 v2-only 版本后续扩展边界。

## 可以优先扩展

- `frontend-vue/`：平台工作台、Workflow Editor、Replay、Dashboard、Figma-first UI。
- `backend-java/`：平台 API、任务生命周期、配置中心、统计、RunEvent、SSE。
- `api_server.py`：轻量 API 入口扩展。
- `services/`：Python API 服务层。
- `agent_registry/`：Agent 元信息。
- `prompts/`：Prompt 模板。
- `workflow_templates/`：Workflow 模板描述。
- `figma/`：设计源规范。
- `docs/`：架构和运维说明。
- `docker-compose.yml`：v2 多服务编排。

## 需要谨慎扩展

- `core/`：LangGraph 状态和工作流。
- `agents.py`：Agent 输出结构。
- `plugins/`：插件执行协议。
- `utils/code_runner.py`：代码运行逻辑。
- `utils/simple_code_agent.py`：受控文件操作。
- `config/settings.yaml`：Runner 与 CodeAgent 策略。

## 暂时不要大改

- LangGraph 主流程。
- Agent 核心输出字段。
- 插件执行协议。
- 报告生成核心逻辑。
- `run_summary` 数据结构。
- `ui_view_model` 数据结构。
- `workflow_events` 事件结构。

## 扩展规则

- Vue 不直接解析 LangGraph 原始 state。
- Java 不替代 Python Agent Engine。
- MySQL 不替代 Python yaml 运行策略，除非已有明确迁移方案。
- C++ Runner 不默认替代 Python Runner。
- CodeAgent 不扩展成完整 Codex。
- 新能力优先走“最小接口 + 可回放事件 + 文档同步”。

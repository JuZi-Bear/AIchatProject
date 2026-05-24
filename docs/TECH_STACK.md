# 技术栈说明

当前项目是 v2-only 多服务平台演示版。

## 总体分层

```text
Vue3 + TypeScript
  -> Java Spring Boot Platform
  -> MySQL / Config / Run Records / RunEvent
  -> FastAPI Python Agent Engine
  -> LangGraph Workflow
  -> Agent Registry / Plugin System / CodeAgent
  -> Python Runner / C++ Runner Sandbox
```

## Vue3 + TypeScript

职责：

- 平台前端和演示工作台。
- Dashboard、RunConsole、History、Reports、Agents、Workflow Templates、Workflow Editor、Replay。
- 通过 Java Gateway 调用平台 API。
- 使用 Element Plus、Pinia、Axios、Vue Router。
- Workflow Editor 采用 Figma 风无限画布交互。

未来职责：

- 更强工作流编辑体验。
- 更细的事件回放、筛选和对比。
- 与 Figma 设计源持续同步。

## Java Spring Boot

职责：

- Platform API Gateway。
- 调用 Python FastAPI Agent Engine。
- MySQL 运行记录、报告索引、设置、模型配置、插件配置、Workflow 模板。
- RunEvent 事件记录和 SSE 推送。
- Replay API。

未来职责：

- 任务生命周期管理。
- 配置中心。
- 审计日志增强。
- 后续再考虑用户系统、权限和团队协作。

## MySQL

职责：

- 保存平台运行记录。
- 保存任务事件。
- 保存报告索引。
- 保存前端设置、模型配置、插件配置。
- 保存 Java/MySQL 自定义 Workflow 模板。

说明：

- 报告正文和大文本产物仍可保存在 `reports/`。
- CodeAgent JSONL 审计日志仍可保存在 `output/`。

## Python FastAPI Agent Engine

职责：

- 通过 `api_server.py` 暴露 Python Agent Engine。
- 通过 `services/run_service.py` 封装运行创建、历史、报告、模型、插件等服务。
- 返回 `state`、`run_summary`、`ui_view_model`、`workflow_events`。

边界：

- 不承担平台用户和权限。
- 不直接管理 MySQL 平台业务。

## LangGraph / Agent

职责：

- 多 Agent 工作流编排。
- Product、Coder、Tester、Runner、Sentry、Quality、Report 等节点。
- 输出工作流事件，供 Java 持久化和 Vue 回放。

相关目录：

- `core/`
- `agents.py`
- `agent_registry/`
- `prompts/`
- `workflow_templates/`
- `plugins/`

## CodeAgent

职责：

- 简化文件操作：`read_file`、`write_file`、`list_files`。
- 路径白名单、阻断路径、读取长度限制。
- JSONL 审计日志。
- 事件接入 Java RunEvent、SSE 和 Replay。

限制：

- 不是完整 Codex。
- 不自动决定修改哪些文件。
- 不做多用户权限隔离。

## Runner

默认：

- Python Runner 保持稳定。

可选：

- C++ Runner Sandbox 提供危险关键词扫描和执行器增强雏形。

限制：

- C++ Runner 当前不是完整安全沙箱。
- 不默认替代 Python Runner。

## Docker Compose

当前服务：

- `mysql`
- `ai-agent-api`
- `backend-java`
- `frontend-vue`

说明：

- 根 `Dockerfile` 默认启动 FastAPI。
- `frontend-vue/Dockerfile` 使用 Node 构建，Nginx 托管。
- `backend-java/Dockerfile` 使用 Java 17 构建和运行。

## Figma

职责：

- 维护 v2 Vue 前端的可编辑设计源。
- 保存 design tokens、页面映射和组件清单。

相关文件：

- `figma/design_tokens.json`
- `figma/frontend_ui_map.json`
- `figma/component_inventory.json`
- `docs/FIGMA_UI_WORKFLOW.md`

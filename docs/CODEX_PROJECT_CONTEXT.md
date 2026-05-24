# Codex Project Context

本文给 Codex 或其他协作者提供当前项目上下文。修改代码前应先阅读本文、`MODULE_BOUNDARY.md`、`V2_ONLY_RUNTIME_SIMPLIFICATION.md` 和 `FRAMEWORK_EXTENSION_PLAN.md`。

## 项目定位

AI Multi-Agent Pipeline 当前是 v2-only 平台化演示版。项目从自然语言需求出发，通过多 Agent 工作流、CodeAgent 文件操作、Java 平台事件记录、SSE 实时事件和 Vue 回放页面，展示“生成、运行、审计、回放”的闭环。

## 当前主链路

```text
Vue3 + TypeScript
  -> Java Spring Boot Platform API
  -> Python FastAPI Agent Engine
  -> LangGraph / Agent / CodeAgent
  -> MySQL / JSONL / reports / runs / output
  -> Java RunEvent + SSE
  -> Vue History / Replay / Dashboard
```

已删除旧 Python UI / CLI 入口文件。后续默认只维护 v2 主链路。

## 关键稳定契约

- `run_summary` 是前端、Java 和报告索引依赖的摘要结构。
- `ui_view_model` 是 Vue 展示工作流结果的稳定数据视图。
- `workflow_events` 是 Python Agent Engine 到 Java RunEvent / SSE / Replay 的事件桥。
- `agent_registry/` 是 Agent 元信息注册中心。
- `prompts/` 是 Prompt 模板目录。
- `workflow_templates/` 是内置 Workflow 模板目录。
- `figma/` 是 Vue 前端 Figma-first 设计源目录。
- FastAPI 层只做 API 适配，复杂业务由 `services/run_service.py` 和共享核心承担。
- Java 层承担 Gateway、平台记录、MySQL、SSE、Replay 和配置能力，不替代 Python Agent Engine。
- C++ Runner 当前是可选增强，默认保留 Python Runner fallback。

## 修改优先级

1. 保持 Vue -> Java -> FastAPI -> MySQL 主链路可运行。
2. 保持 `run_summary`、`ui_view_model`、`workflow_events` 字段语义稳定。
3. 保持 Docker Compose 服务名和端口稳定。
4. 修改后同步更新 README 和 docs。
5. UI 修改优先考虑 Figma-first 设计源。

## 修改后最低验证要求

- Python API：`GET http://127.0.0.1:8001/health`。
- Java Gateway：`GET http://127.0.0.1:8088/api/health`。
- Java 代理 Python：`GET http://127.0.0.1:8088/api/agent/health`。
- Vue 页面：`/`、`/agents`、`/workflows/templates`、`/workflows/editor`、`/history`、`/reports`。
- 前端构建：`cd frontend-vue && npm run build`。
- Java 构建：`cd backend-java && mvn -DskipTests package`。
- Smoke：`.\scripts\smoke_codeagent.ps1 -ApiMode java -CheckBlockedPath` 和 `.\scripts\smoke_workflow_template.ps1`。

## 后续工作原则

- 优先修复 P0 / P1。
- 文档不一致可以直接修。
- 核心代码重构需要用户确认。
- 不新增用户系统、权限系统、队列系统或动态 LangGraph 编排，除非用户明确要求。
- 后续涉及框架扩展时，先确认是否符合 `RECOMMENDED_EXTENSION_ROADMAP.md`。
- 后续涉及 `frontend-vue/` UI 创建或修改时，参考 `docs/FIGMA_UI_WORKFLOW.md`、`figma/frontend_ui_map.json` 和 `figma/component_inventory.json`。
- 如果用户提供 Figma 文件 URL，应优先同步 Figma Frame / Component，再修改 Vue 实现。

## 当前重点入口

- Vue 前端：`frontend-vue/`
- Java 平台：`backend-java/`
- Python API：`api_server.py`
- Python 服务层：`services/`
- LangGraph 核心：`core/`
- Agent / Prompt：`agents.py`、`agent_registry/`、`prompts/`
- Workflow 模板：`workflow_templates/`
- 多服务启动：`docker-compose.yml`
- v2 脚本：`scripts/`
- 文档导航：`docs/DOCUMENT_INDEX.md`

# v2-only Video Coding 录制指南

本文用于准备比赛 video coding 或项目讲解录屏。当前版本只展示 v2 平台主链路。

## 推荐录制顺序

1. 项目总览：打开 `README.md`、`docs/V2_ARCHITECTURE_PLAN.md`。
2. Docker Compose：展示 `mysql`、`ai-agent-api`、`backend-java`、`frontend-vue` 四个服务。
3. Vue Dashboard：展示运行统计、最近事件、模型、插件和报告入口。
4. Workflow Editor：展示 Figma 风无限画布、拖入节点、分支节点和 CodeAgent。
5. RunConsole：执行 CodeAgent 演示，展示 SSE 实时事件。
6. Audit / Diff：展示审计日志、阻断路径和文件前后对比。
7. Replay：回放完整事件流。
8. Java + MySQL：展示平台记录、事件、模板和报告索引。
9. FastAPI：展示 Python Agent Engine 的 `/docs` 和 Agent/Workflow API。
10. 总结：展示成果、风险兜底和下一步规划。

## 每部分讲解重点

| 部分 | 讲解重点 |
| --- | --- |
| 项目总览 | AI 多 Agent 工作流平台，v2-only 平台演示链路 |
| Docker Compose | 一次启动 Vue、Java、FastAPI、MySQL |
| Vue Dashboard | 平台总览、最近事件、报告和快捷入口 |
| Workflow Editor | 可视化编排、节点属性浮层、分支节点 |
| CodeAgent | 受控文件操作、白名单、阻断路径、审计日志 |
| SSE / RunEvent | Java 平台事件记录与实时推送 |
| Replay | 根据 MySQL 事件记录回放执行过程 |
| Java + MySQL | 平台记录、配置、模板、报告索引持久化 |
| FastAPI | Python Agent Engine API 化，屏蔽 LangGraph 内部结构 |

## 建议打开的文件

- 总览：`README.md`、`docs/DOCUMENT_INDEX.md`
- 架构：`docs/V2_ARCHITECTURE_PLAN.md`、`docs/FRAMEWORK_EXTENSION_ARCHITECTURE.md`
- Vue：`frontend-vue/src/views/WorkflowEditor.vue`
- Java：`backend-java/src/main/java/com/aichat/platform/service/RunEventService.java`
- Python：`api_server.py`、`services/run_service.py`
- CodeAgent：`utils/code_agent_tools.py`、`docs/CODE_AGENT_NODE_GUIDE.md`
- Docker：`docker-compose.yml`

## 适合现场修改的文件

- `docs/` 下的讲解文档。
- `frontend-vue/src/views/` 中轻量展示文案。
- `frontend-vue/src/components/` 中非核心展示组件。
- `config/settings.yaml` 中演示参数，例如 `runner_mode`。

## 不建议现场修改的文件

- `core/workflow.py`
- `core/state.py`
- `agents.py`
- `plugins/` 核心插件逻辑
- `report_generator.py`
- `api_server.py` 的接口结构
- Java entity/repository 结构
- Docker Compose 服务名和端口

## 推荐演示命令

```powershell
docker compose up -d --build
.\scripts\smoke_codeagent.ps1 -ApiMode java -CheckBlockedPath
.\scripts\smoke_workflow_template.ps1
.\scripts\final_v2_acceptance.ps1
```

## 录制注意事项

- 先确认 Docker 服务和本地端口正常。
- API Key 不稳定时启用 offline/demo 模式。
- 现场重点展示“拖拽 -> 执行 -> SSE -> 审计 -> Replay”的闭环。
- 不在录制中改核心工作流，避免现场引入不可控风险。

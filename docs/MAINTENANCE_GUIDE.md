# v2-only 维护指南

本文说明后续如何安全维护当前 v2 平台演示版。

## 如何判断模块归属

- Vue 前端：`frontend-vue/`
- Java 平台服务：`backend-java/`
- Python Agent Engine：`api_server.py`、`services/`、`core/`、`agents.py`
- 共享配置：`config/`
- 可选执行器：`runner-cpp/`
- 部署：`docker-compose.yml`、`Dockerfile`
- 文档：`docs/`
- 生成产物：`reports/`、`runs/`、`output/`

## 安全修改 Python Agent Engine

- 优先改 `services/`、`utils/` 或新增模块。
- 谨慎修改 `core/workflow.py`、`core/state.py`、`agents.py`。
- 不随意改变 `run_summary`、`ui_view_model`、`workflow_events` 字段。
- 修改后至少验证 Python `/health`、Java `/api/agent/health` 和一次 smoke。

## 安全修改 Vue 前端

- 优先保持 API 类型定义与接口契约一致。
- Workflow Editor 修改后必须验证拖拽、缩放、属性浮层、保存模板和生成任务。
- RunConsole 修改后必须验证 CodeAgent、SSE、审计日志和 Replay 入口。
- 修改后执行 `cd frontend-vue && npm run build`。

## 安全修改 Java 后端

- 保持代理接口兼容。
- 新增平台接口优先使用 `ApiResponse`。
- 数据库变更依赖 JPA `ddl-auto=update`，上线前应记录字段说明。
- 修改后执行 `cd backend-java && mvn -DskipTests package`。

## 安全修改 C++ Runner

- 默认不替代 Python Runner。
- 保持 `runner_mode: python` 为默认值。
- 如果启用 C++ Runner，需要验证 fallback 和安全扫描结果。

## 修改后必须测试

```powershell
cd frontend-vue
npm run build

cd ..\backend-java
mvn -DskipTests package

cd ..
docker compose up -d --build
.\scripts\smoke_codeagent.ps1 -ApiMode java -CheckBlockedPath
.\scripts\smoke_workflow_template.ps1
.\scripts\final_v2_acceptance.ps1
```

## 修改后必须更新

- `README.md`
- `docs/API_CONTRACT.md`
- `docs/V2_ARCHITECTURE_PLAN.md`
- `docs/TASKS.md`
- 相关功能文档或演示脚本

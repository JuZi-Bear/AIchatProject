# v2-only 最终交付检查清单

本文用于比赛提交或现场演示前确认 v2 主链路是否稳定。

## 核心结论

- [ ] Vue 前端可访问：`http://127.0.0.1:5174`
- [ ] Java Gateway 可访问：`http://127.0.0.1:8088/api/health`
- [ ] Python Agent Engine 可访问：`http://127.0.0.1:8001/health`
- [ ] Java 可代理 Python：`http://127.0.0.1:8088/api/agent/health`
- [ ] MySQL 可连接，Java 平台记录可写入。
- [ ] CodeAgent smoke 通过，包括安全阻断、审计日志、RunEvent 和 Replay。
- [ ] Workflow 模板 smoke 通过，包括保存、版本、实例化和删除。
- [ ] `frontend-vue` 构建通过。
- [ ] `backend-java` 打包通过。
- [ ] `docker compose up -d --build` 可启动 v2 服务。

## 环境检查

- [ ] Python 3.11 或兼容版本可用。
- [ ] Node.js 20 或兼容版本可用。
- [ ] Java 17 与 Maven 可用。
- [ ] Docker Desktop 可用。
- [ ] `.env` 已按 `.env.example` 配置，或使用离线演示模式。
- [ ] `reports/`、`runs/`、`output/` 可自动创建或已存在。

## 本地脚本

```powershell
.\scripts\start_v2_local.ps1
.\scripts\smoke_codeagent.ps1 -ApiMode java -CheckBlockedPath
.\scripts\smoke_workflow_template.ps1
.\scripts\final_v2_acceptance.ps1
```

## 手动启动

```powershell
python -m uvicorn api_server:app --reload --host 127.0.0.1 --port 8001
cd backend-java
mvn spring-boot:run
cd ..\frontend-vue
npm run dev
```

## Docker 启动

```powershell
docker compose up -d --build
```

服务地址：

- Vue: `http://localhost:5174`
- Java: `http://localhost:8088/api/health`
- FastAPI: `http://localhost:8001/docs`
- MySQL: `localhost:3307`

## 页面检查

- [ ] `/`
- [ ] `/run` 或 `/runs/new`
- [ ] `/history`
- [ ] `/reports`
- [ ] `/agents`
- [ ] `/workflows/templates`
- [ ] `/workflows/editor`
- [ ] `/models`
- [ ] `/plugins`

## 演示闭环

- [ ] Workflow Editor 可以拖入 Agent、CodeAgent、If、And、Or 节点。
- [ ] CodeAgent 可以执行允许路径内的 `read_file`、`write_file`、`list_files`。
- [ ] 违规路径会被阻断并高亮。
- [ ] JSONL 审计日志可查看。
- [ ] Java RunEvent 可查询。
- [ ] SSE 事件可实时展示。
- [ ] Replay 页面可回放事件顺序。

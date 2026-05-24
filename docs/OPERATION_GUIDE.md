# v2-only 操作指南

本文说明当前 v2-only 演示版的启动、验证和常见问题处理。

## 服务组成

| 服务 | 作用 | 默认地址 |
| --- | --- | --- |
| `frontend-vue` | Vue3 前端 | http://127.0.0.1:5174 |
| `backend-java` | Java Platform API / Gateway | http://127.0.0.1:8088/api |
| `ai-agent-api` | Python FastAPI Agent Engine | http://127.0.0.1:8001 |
| `mysql` | 平台数据持久化 | `127.0.0.1:3306` 或 `3307` |

## Docker 启动

```powershell
docker compose up --build
```

如果 MySQL 端口冲突：

```powershell
$env:MYSQL_HOST_PORT="3307"
docker compose up --build
```

后台启动：

```powershell
docker compose up -d --build
```

停止：

```powershell
docker compose down
```

清理数据卷：

```powershell
docker compose down -v
```

## 本地一键联调

```powershell
.\scripts\start_v2_local.ps1
```

停止：

```powershell
.\scripts\stop_v2_local.ps1
```

生成演示数据：

```powershell
.\scripts\seed_v2_demo_data.ps1
```

## 手动开发模式

Python：

```powershell
python -m uvicorn api_server:app --reload --host 127.0.0.1 --port 8001
```

Java：

```powershell
cd backend-java
mvn spring-boot:run
```

Vue：

```powershell
cd frontend-vue
npm install
npm run dev
```

## 页面入口

- Dashboard: `/`
- Run Console: `/runs/new`
- History: `/history`
- Reports: `/reports`
- Models: `/models`
- Plugins: `/plugins`
- Agents: `/agents`
- Workflow Templates: `/workflows/templates`
- Workflow Editor: `/workflows/editor`
- Replay: `/replay/:platformRunId`

## 常用演示流程

1. 打开 Dashboard，确认 API 模式和平台统计。
2. 打开 Agents，展示 Agent 注册中心。
3. 打开 Workflow Templates，展示模板版本、详情和实例化。
4. 打开 Workflow Editor，拖拽 CodeAgent 或分支节点。
5. 执行 CodeAgent 文件操作，查看 SSE 事件和审计日志。
6. 打开 History，查看平台运行记录。
7. 打开 Replay，逐步回放事件顺序。

## 验收命令

```powershell
.\scripts\smoke_codeagent.ps1 -ApiMode java -CheckBlockedPath
.\scripts\smoke_workflow_template.ps1
.\scripts\final_v2_acceptance.ps1
```

前端构建：

```powershell
cd frontend-vue
npm run build
```

Java 构建：

```powershell
cd backend-java
mvn -DskipTests package
```

## 常见问题

### Vue 打不开

检查容器或本地 dev server：

```powershell
docker ps
```

或重新启动：

```powershell
docker compose up -d --build frontend-vue
```

### Java 连接不上 MySQL

确认 MySQL 容器 healthy：

```powershell
docker ps
docker logs aichat-mysql --tail 80
```

如果本机 `3306` 被占用，用 `MYSQL_HOST_PORT=3307`。

### Vue 调 API 失败

检查：

- `http://127.0.0.1:8088/api/health`
- `http://127.0.0.1:8088/api/agent/health`
- `http://127.0.0.1:8001/health`

### CodeAgent 被阻断

这是预期安全策略。检查：

- `config/settings.yaml`
- `code_agent.allowed_paths`
- `code_agent.blocked_paths`
- `output/code_agent_audit.jsonl`

### Workflow Editor 生成任务不执行真实 LangGraph 分支

这是当前设计限制。模板实例化生成可回放任务视图，不直接改写 Python LangGraph 主流程。

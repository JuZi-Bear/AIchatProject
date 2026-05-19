# v2 本地一键联调

本文记录 Vue + Java + MySQL + Python API 的本地联调脚本。目标是减少比赛演示前的手动启动步骤。

## 一键启动

```powershell
.\scripts\start_v2_local.ps1
```

默认行为：

- 启动 Python FastAPI：`http://127.0.0.1:8001`
- 启动临时 MySQL：`127.0.0.1:3307`
- 启动 Java Gateway：`http://127.0.0.1:8088/api`
- 启动 Vue Java 模式：`http://127.0.0.1:5174/run`
- 自动执行一次 CodeAgent smoke test

临时 MySQL 数据目录：

```text
output/mysql-local-data
```

该目录已被 `.gitignore` 忽略，不会进入 Git。

## 使用已有 MySQL

如果要使用本机 3306 MySQL：

```powershell
.\scripts\start_v2_local.ps1 -MySqlMode existing -MySqlPort 3306 -MySqlUser root -MySqlPassword your_password
```

## Python Direct 模式

只启动 Python API 和 Vue：

```powershell
.\scripts\start_v2_local.ps1 -ApiMode python
```

## 单独执行 CodeAgent smoke

Java Gateway 模式：

```powershell
.\scripts\smoke_codeagent.ps1 -ApiMode java
```

附带阻断路径检查：

```powershell
.\scripts\smoke_codeagent.ps1 -ApiMode java -CheckBlockedPath
```

Python Direct 模式：

```powershell
.\scripts\smoke_codeagent.ps1 -ApiMode python
```

## 一键生成演示数据

启动 v2 Java Gateway 链路后，可以执行：

```powershell
.\scripts\seed_v2_demo_data.ps1
```

脚本会生成三类平台记录：

- 真实 Agent 工作流运行：走 `POST /api/runs`，用于展示普通 Agent 运行。
- CodeAgent 文件操作：走 `POST /api/code-agent/execute`，用于展示审计日志、文件操作和回放。
- Workflow 模板回放：保存 MySQL 模板并实例化为可回放任务，用于展示模板中心和 Replay。

脚本输出会包含 Dashboard、History 和 Replay 链接。若只想生成其中一类数据，可使用：

```powershell
.\scripts\seed_v2_demo_data.ps1 -SkipAgentRun
.\scripts\seed_v2_demo_data.ps1 -SkipCodeAgent
.\scripts\seed_v2_demo_data.ps1 -SkipWorkflowTemplate
```

## 停止本地联调服务

```powershell
.\scripts\stop_v2_local.ps1
```

脚本默认只停止 `start_v2_local.ps1` 记录的 PID。

如果确认要强制清理常用 v2 端口：

```powershell
.\scripts\stop_v2_local.ps1 -ForcePorts
```

## 常见问题

### Java 连接不上 MySQL

优先使用默认临时 MySQL 模式：

```powershell
.\scripts\start_v2_local.ps1 -MySqlMode temp
```

这会避开本机 3306 root 密码不确定的问题。

### Docker 未启动

本脚本不依赖 Docker。Docker 模式仍使用：

```powershell
docker compose up --build
```

### Vue 页面没有走 Java Gateway

使用脚本启动时会向 Vite 注入：

```text
VITE_API_MODE=java
VITE_JAVA_API_BASE_URL=http://127.0.0.1:8088/api
```

访问：

```text
http://127.0.0.1:5174/run
```

### CodeAgent smoke 失败

检查：

- Python API 是否健康：`http://127.0.0.1:8001/health`
- Java 是否健康：`http://127.0.0.1:8088/api/health`
- 审计日志是否生成：`output/code_agent_audit.jsonl`
- Replay 是否能访问：`http://127.0.0.1:5174/replay/{platformRunId}`

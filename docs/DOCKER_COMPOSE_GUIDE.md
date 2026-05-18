# Docker Compose 多服务启动指南

本指南说明 v2.0 多服务平台如何通过 Docker Compose 一次启动。该模式保留 Streamlit v1 演示版，同时启动 Vue、Java、MySQL 和 Python FastAPI Agent Engine。

## 多服务架构图

```text
浏览器
  ├─ http://localhost:5174  -> frontend-vue / Nginx / Vue3
  │                              ↓
  │                         backend-java / Spring Boot / :8088
  │                              ↓
  │                         ai-agent-api / FastAPI / :8001
  │                              ↓
  │                         Python Agent Engine / LangGraph
  │
  └─ http://localhost:8501  -> streamlit-web / v1 演示版

backend-java
  ↓
mysql / MySQL 8.0 / aichat_platform

Python Runner
  └─ 可选读取 runner-cpp/build/runner.exe，当前 Docker 模式只挂载 runner-cpp，不在 Compose 内编译 C++ Runner
```

## 服务说明

| 服务 | 作用 | 端口 |
| --- | --- | --- |
| `mysql` | Java 平台服务层数据库，保存运行记录、报告索引、配置和统计数据 | `3306` |
| `ai-agent-api` | Python FastAPI Agent Engine，暴露 `/health`、`/runs`、`/reports` 等接口 | `8001` |
| `backend-java` | Spring Boot 平台服务层，代理 Python API 并管理 MySQL 平台数据 | `8088` |
| `frontend-vue` | Vue3 + TypeScript 生产构建，由 Nginx 托管 | `5174` |
| `streamlit-web` | v1.0 Streamlit 演示版，保留比赛现场备用入口 | `8501` |

## 访问地址

- Vue 前端：[http://localhost:5174](http://localhost:5174)
- Java 健康检查：[http://localhost:8088/api/health](http://localhost:8088/api/health)
- FastAPI Docs：[http://localhost:8001/docs](http://localhost:8001/docs)
- Streamlit v1：[http://localhost:8501](http://localhost:8501)
- MySQL：`localhost:3306`

## 环境变量

复制示例文件：

```powershell
Copy-Item .env.docker.example .env
```

至少确认：

```text
DEEPSEEK_API_KEY=your_deepseek_api_key
MYSQL_ROOT_PASSWORD=root
MYSQL_DATABASE=aichat_platform
```

如果没有在线模型 Key，可使用：

```text
OFFLINE_MODE=true
```

## 启动

```powershell
docker compose up --build
```

后台启动：

```powershell
docker compose up -d --build
```

## 停止

```powershell
docker compose down
```

清理 MySQL 数据卷：

```powershell
docker compose down -v
```

## C++ Runner Sandbox

本阶段采用方案 A：C++ Runner 作为本地可选增强模块，不作为独立 Docker 服务。

- Compose 会把 `./runner-cpp` 挂载到 Python 容器的 `/app/runner-cpp`。
- 如果容器内存在 `/app/runner-cpp/build/runner.exe`，且 `config/settings.yaml` 设置 `runner_mode: cpp`，Python `code_runner` 会尝试调用 C++ Runner。
- 如果 runner 未编译，会自动回退 Python Runner，并在 `runner_warning` 中提示。

编译和使用说明见 `docs/CPP_RUNNER_SANDBOX.md`。

## 常见问题

### 端口占用

如果 `3306`、`5174`、`8088`、`8001` 或 `8501` 被占用，Compose 启动会失败。可以停止占用端口的本地服务，或修改 `docker-compose.yml` 左侧端口映射。

### MySQL 启动慢

`backend-java` 已等待 `mysql` healthcheck。首次初始化数据卷时 MySQL 可能需要几十秒，请查看：

```powershell
docker compose logs mysql
```

### Java 连不上 MySQL

检查：

- `mysql` 服务是否 healthy。
- `SPRING_DATASOURCE_URL` 是否使用 `mysql:3306`。
- `SPRING_DATASOURCE_PASSWORD` 是否与 `MYSQL_ROOT_PASSWORD` 一致。

### Vue 调 API 失败

生产构建默认使用 Java Gateway：

```text
VITE_API_MODE=java
VITE_JAVA_API_BASE_URL=http://localhost:8088/api
VITE_PYTHON_API_BASE_URL=http://localhost:8001
```

如果 Java 服务未启动，Dashboard 会提示 Java 平台服务未连接。

### API Key 缺失

`.env` 中缺少模型 API Key 时，在线模型调用会失败。比赛现场可设置 `OFFLINE_MODE=true` 使用离线演示兜底。

### CORS 问题

FastAPI 和 Spring Boot 已允许本地 Vue 开发/生产端口。生产部署时应收紧允许来源。

### 旧容器残留

如果之前运行过旧版 `ai_agent_pipeline` 容器，可能占用 `8501`。可先执行：

```powershell
docker compose down --remove-orphans
```

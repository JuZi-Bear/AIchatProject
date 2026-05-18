# 双轨推荐启动顺序

本文说明 v1.0 比赛演示轨、v2.0 本地开发模式和 v2.0 Docker 模式的推荐启动顺序。

## v1.0

1. 激活虚拟环境。

```powershell
cd D:\AIchatProject
.\.venv\Scripts\Activate.ps1
```

2. 启动 `graph_demo.py` 或 `webui.py`。

```powershell
python graph_demo.py
```

或：

```powershell
python -m streamlit run webui.py
```

3. 运行演示案例。

- 简单成功案例：验证基本闭环。
- 翻车修复案例：验证自动修复。
- 综合案例：验证插件、报告和质量评分。

## v2.0 本地开发

1. 启动 MySQL。

- 本地 MySQL：确认数据库 `aichat_platform` 已创建。
- Docker MySQL：也可以只启动数据库服务。

```powershell
docker compose up mysql
```

2. 启动 Python FastAPI。

```powershell
cd D:\AIchatProject
.\.venv\Scripts\Activate.ps1
python -m uvicorn api_server:app --reload --host 127.0.0.1 --port 8001
```

3. 启动 Java Spring Boot。

```powershell
cd D:\AIchatProject\backend-java
mvn spring-boot:run
```

4. 启动 Vue。

```powershell
cd D:\AIchatProject\frontend-vue
npm run dev
```

5. 访问 Dashboard。

- Vue 开发模式：`http://localhost:5173`
- Java Health：`http://localhost:8088/api/health`
- FastAPI Docs：`http://localhost:8001/docs`

## v2.0 Docker

1. 配置 `.env`。

```powershell
cd D:\AIchatProject
Copy-Item .env.docker.example .env
```

按需要填写模型 API Key，或设置：

```text
OFFLINE_MODE=true
```

2. 启动多服务。

```powershell
docker compose up --build
```

3. 访问 Vue / Java / FastAPI / Streamlit。

- Vue 前端：`http://localhost:5174`
- Java 平台服务：`http://localhost:8088/api/health`
- FastAPI Docs：`http://localhost:8001/docs`
- Streamlit v1：`http://localhost:8501`
- MySQL：`localhost:3306`

## 常见顺序问题

- Java 依赖 Python API 和 MySQL，建议先启动 MySQL 和 FastAPI。
- Vue Java Gateway 模式依赖 Java 服务，Java 未启动时 Dashboard 应显示连接失败提示。
- Vue Python Direct 模式只依赖 FastAPI。
- Docker 首次启动 MySQL 可能较慢，等待 healthcheck 完成后再访问 Java 平台接口。

# 风险与稳定性说明

本文说明为什么当前采用双轨并行，以及比赛现场如何兜底。

## 为什么保留 v1.0 作为稳定演示轨

v1.0 Streamlit 链路依赖少、路径短、已经覆盖核心演示能力。比赛现场最重要的是稳定展示多 Agent 闭环，因此必须保留 Streamlit、Python Direct、yaml 配置、Python Runner、`graph_demo.py` 和 `webui.py`。

## 为什么 v2.0 不完全替代 v1.0

v2.0 引入 Vue、Java、MySQL、Docker Compose 和 C++ Runner，能体现平台化能力，但也带来更多运行条件和外部依赖。当前阶段 v2 是升级轨，不是替换轨。只有当 v2 在稳定性和演示完整度上超过 v1，才考虑进一步收敛。

## Vue 风险点

- 前端构建依赖 Node 和 npm。
- API 模式配置错误会导致页面无法连接后端。
- Java Gateway 未启动时，Java 模式会显示连接失败。

兜底方式：切换 Python Direct 模式，或直接使用 Streamlit v1。

## Java 风险点

- 本地 Maven 或 Java 版本不一致。
- MySQL 未启动或连接配置错误。
- Java Gateway 调 Python API 失败。

兜底方式：Vue 改用 Python Direct，或直接访问 FastAPI / Streamlit。

## MySQL 风险点

- 端口 `3306` 被占用。
- 首次 Docker 初始化较慢。
- 密码或数据库名与配置不一致。

兜底方式：不依赖 Java 平台记录，使用 Python `runs/` 和 `reports/` 文件历史。

## Docker 风险点

- 端口 `5174`、`8088`、`8001`、`8501`、`3306` 被占用。
- 镜像构建网络慢。
- 本机 Docker Desktop 状态异常。

兜底方式：按本地模式分别启动 Python API、Vue、Java 或直接启动 Streamlit。

## API 不可用时怎么办

- 检查 `http://localhost:8001/docs`。
- 检查 `.env` 是否存在必要模型 Key 或 `OFFLINE_MODE=true`。
- 使用 Streamlit v1 直接调用 Python 核心。

## Java 不可用时怎么办

- Vue `.env.development` 使用 `VITE_API_MODE=python`。
- 直接访问 Python FastAPI。
- 使用 Streamlit v1 展示完整闭环。

## Docker 不可用时怎么办

使用本地启动：

```powershell
python -m streamlit run webui.py
python -m uvicorn api_server:app --reload --host 127.0.0.1 --port 8001
cd frontend-vue
npm run dev
```

如需 Java Gateway，再启动：

```powershell
cd backend-java
mvn spring-boot:run
```

## 为什么采用双轨并行而不是一次性重构

一次性重构会同时影响 UI、API、数据存储、部署和 Runner，风险集中且难以定位问题。双轨并行让稳定演示和平台升级解耦：v1 保证交付，v2 展示成长路线，出现问题时可以快速退回稳定路径。

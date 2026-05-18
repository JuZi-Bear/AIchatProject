# Video Coding 录制指南

本文用于准备比赛 video coding 或项目讲解录屏。目标是让评委看到项目从稳定演示到平台化升级的完整工程思路。

## 推荐录制顺序

1. 项目总览：打开 `README.md` 和 `docs/DUAL_TRACK_ARCHITECTURE.md`。
2. v1 Streamlit 演示：启动 `webui.py`，展示自然语言需求到报告生成。
3. FastAPI：打开 `api_server.py` 和 `/docs`，展示 Python Agent Engine API 化。
4. Vue Dashboard：打开 `frontend-vue/`，展示平台总览、运行统计、模型和插件状态。
5. Java Gateway：打开 `backend-java/`，展示代理接口、平台记录和 settings。
6. MySQL：展示 Java 持久化运行记录、报告索引和配置表的设计说明。
7. C++ Runner：打开 `runner-cpp/` 和 `docs/CPP_RUNNER_SANDBOX.md`，说明安全执行器雏形。
8. Docker Compose：打开 `docker-compose.yml` 和 `docs/DOCKER_COMPOSE_GUIDE.md`，展示多服务部署。

## 每部分建议讲解内容

| 部分 | 讲解重点 |
| --- | --- |
| 项目总览 | 多 Agent 自主开发流水线，双轨并行策略 |
| Streamlit v1 | 稳定演示、快速兜底、比赛现场可靠 |
| FastAPI | Python Agent Engine API 化，为 Vue/Java/C++ 接入做准备 |
| Vue Dashboard | 平台化总览、历史、报告、模型和插件配置 |
| Java Gateway | 平台服务层、任务记录、配置管理、MySQL 持久化 |
| MySQL | 数据从临时文件走向平台记录和统计 |
| C++ Runner | 安全执行增强点，不破坏 Python Runner |
| Docker Compose | 一次启动多服务，展示工程化部署能力 |

## 建议打开的文件

- 总览：`README.md`、`docs/DOCUMENT_INDEX.md`
- 双轨：`docs/DUAL_TRACK_ARCHITECTURE.md`
- v1：`webui.py`、`graph_demo.py`
- API：`api_server.py`、`services/run_service.py`
- Vue：`frontend-vue/src/views/Dashboard.vue`、`frontend-vue/src/api/client.ts`
- Java：`backend-java/src/main/java/com/aichat/platform/`
- Docker：`docker-compose.yml`
- C++ Runner：`runner-cpp/src/SandboxRunner.cpp`、`utils/cpp_runner_adapter.py`

## 适合现场修改的文件

- `docs/` 下的讲解文档。
- `frontend-vue/src/views/` 中轻量展示文案。
- `frontend-vue/src/components/` 中非核心展示组件。
- `config/settings.yaml` 中演示参数，例如 `runner_mode`，修改前说明风险。

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

v1 Streamlit：

```powershell
python -m streamlit run webui.py
```

FastAPI：

```powershell
python -m uvicorn api_server:app --reload --host 127.0.0.1 --port 8001
```

Vue 开发模式：

```powershell
cd frontend-vue
npm run dev
```

Java 本地模式：

```powershell
cd backend-java
mvn spring-boot:run
```

Docker Compose：

```powershell
docker compose up --build
```

C++ Runner 编译：

```powershell
cd runner-cpp
cmake -S . -B build
cmake --build build --config Release
```

## 推荐展示流程

1. Streamlit v1：展示稳定闭环。
2. FastAPI：展示 `/health`、`/runs`、`/reports`。
3. Vue Dashboard：展示平台首页、最近运行、模型和插件状态。
4. Java Gateway：展示 `/api/health` 和平台记录接口。
5. MySQL：讲解运行记录和报告索引持久化。
6. C++ Runner：展示危险关键词扫描和 fallback 设计。
7. Docker Compose：展示多服务服务名和端口。

## 录制注意事项

- 比赛现场优先用 v1 Streamlit 作为稳定入口。
- v2 平台功能用于展示工程能力，不要承诺完全替代 v1。
- 如果 API Key 不可用，使用 offline/demo 模式讲清楚兜底策略。
- 如果 Docker 端口冲突，切回本地启动模式。

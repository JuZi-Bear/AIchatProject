# 双轨并行架构说明

本文说明当前项目为什么同时保留 v1.0 比赛演示轨和 v2.0 平台化升级轨，以及后续开发时必须遵守的边界。

## 什么是双轨并行

双轨并行是指项目同时维护两条目标不同、但共享核心能力的技术路线：

- v1.0 比赛演示轨：以 Python + LangGraph + Streamlit 为主，强调稳定、可快速演示、现场可兜底。
- v2.0 平台化升级轨：以 Vue3 + TypeScript + Java Spring Boot + MySQL + FastAPI + C++ Runner Sandbox 为主，强调前后端分离、平台服务层、持久化和工程扩展。

双轨不是两套独立产品。它们共享 Agent 核心、插件系统、报告系统、运行历史和配置能力，但入口、展示层和平台职责不同。

## 为什么采用双轨策略

- 比赛现场需要稳定入口。Streamlit v1 已经能完整展示需求输入、Agent 协作、自动修复、质量评分和报告生成。
- 平台化升级需要更复杂的服务拆分。Vue、Java、MySQL、Docker Compose、C++ Runner 都会增加工程复杂度，不适合一次性替换稳定演示链路。
- 双轨可以降低重构风险。v2 能逐步接入 FastAPI、Java Gateway、MySQL 和 Docker，同时 v1 始终可作为兜底。
- Codex 协作更安全。后续修改可以先判断影响哪条轨道，避免误删或重写核心流程。

## v1.0 与 v2.0 职责区别

| 轨道 | 职责 | 核心入口 | 适用场景 |
| --- | --- | --- | --- |
| v1-demo | 比赛演示、稳定交付、快速验证 Agent 闭环 | `webui.py`、`graph_demo.py`、`start_demo.bat` | 现场演示、答辩兜底、离线演示 |
| v2-platform | 平台化服务、前后端分离、持久化、Docker 多服务部署 | `frontend-vue/`、`backend-java/`、`api_server.py`、`docker-compose.yml` | 平台预览、工程展示、后续团队协作 |

## v1.0 比赛演示轨

v1.0 轨道必须保持稳定，包含：

- Streamlit Web UI：`webui.py`
- Python Direct 运行方式：直接调用 Python Agent 核心
- yaml 配置：`config/models.yaml`、`config/agents.yaml`、`config/settings.yaml`
- Python Runner：`utils/code_runner.py`
- CLI / Demo 入口：`graph_demo.py`、`main.py`
- Windows 快速启动：`start_demo.bat`

v1.0 的目标是“能稳稳演示”，不追求平台化能力。

## v2.0 平台化升级轨

v2.0 轨道用于展示工程演进，包含：

- Vue3 + TypeScript 前端：`frontend-vue/`
- Java Spring Boot 平台服务层：`backend-java/`
- MySQL 持久化：运行记录、报告索引、配置和统计
- FastAPI API 化：`api_server.py`
- Docker Compose 多服务部署：`docker-compose.yml`
- C++ Runner Sandbox：`runner-cpp/`

v2.0 的目标是“可扩展平台雏形”，不要求完全替代 v1。

## 当前推荐运行方式

- 比赛现场优先：启动 v1.0 Streamlit。

```powershell
python -m streamlit run webui.py
```

- API 调试：启动 Python FastAPI。

```powershell
python -m uvicorn api_server:app --reload --host 127.0.0.1 --port 8001
```

- 平台演示：启动 Docker Compose 多服务。

```powershell
docker compose up --build
```

访问地址见 `docs/DOCKER_COMPOSE_GUIDE.md`。

## 当前推荐开发方式

- 修改 Agent 核心前，先确认是否会影响 v1 和 v2 两条轨道。
- 前端体验优先在 `frontend-vue/` 内迭代，不影响 Streamlit。
- 平台能力优先在 `backend-java/` 内迭代，不改变 Python API 返回结构。
- Python Agent 能力优先通过 `services/run_service.py` 和 `api_server.py` 向 v2 暴露，不让 Vue 或 Java 直接解析 LangGraph 内部 state。
- C++ Runner 仍是可选增强，默认不替代 Python Runner。

## 双轨共享部分

两条轨道共享：

- LangGraph 工作流：`core/workflow.py`
- 状态结构：`core/state.py`
- Agent 与模型相关 Python 逻辑：顶层 `agents.py`、`model_manager.py`
- 插件系统：`plugins/`、`plugin_loader.py`
- 报告系统：`report_generator.py`、`reports/`
- 运行历史：`runs/`、`utils/run_store.py`
- UI ViewModel 与摘要构建：`utils/ui_state_builder.py`、`utils/summary_builder.py`
- 配置：`config/`

## 禁止破坏的边界

后续修改禁止：

- 删除 Streamlit v1 入口。
- 删除 Python Direct 运行方式。
- 删除 FastAPI 现有接口。
- 删除 Java Gateway 代理能力。
- 删除 Docker Compose 多服务启动。
- 删除 `run_summary` 或 `ui_view_model`。
- 让 Vue 或 Java 直接依赖 LangGraph 内部 state。
- 把 API Key 写死到代码或文档示例之外。
- 默认启用未验证的 C++ Runner 替代 Python Runner。

## 后续可能收敛方向

- v2 Vue 页面完全覆盖 Streamlit 的演示能力后，可把 Streamlit 标记为 legacy demo，但不急于删除。
- Java 平台层接入用户、权限和任务队列后，可逐步成为统一入口。
- C++ Runner 完成隔离、超时、资源限制后，可作为 Python Runner 的增强执行后端。
- 报告和运行历史可逐步从文件系统迁移到数据库索引 + 文件存储的混合模式。
- 文档可继续以 `DOCUMENT_INDEX.md` 为主入口，减少 README 负担。

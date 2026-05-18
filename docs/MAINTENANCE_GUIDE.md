# 维护指南

本文说明后续如何安全维护双轨并行项目。

## 如何判断文件属于 v1.0 还是 v2.0

- v1.0 比赛演示轨：`webui.py`、`graph_demo.py`、`start_demo.bat`、Streamlit 相关展示和 Python Direct 运行链路。
- v2.0 平台化升级轨：`frontend-vue/`、`backend-java/`、`api_server.py`、`schemas/`、`services/`、`docker-compose.yml`。
- shared-core：`core/`、`plugins/`、`utils/`、`config/`、顶层 Agent/模型/报告相关 Python 文件。
- experimental：`runner-cpp/`、`figma/`。
- generated-output：`reports/`、`runs/`、`output/`。
- documentation：`docs/`、根 `README.md`。

不确定时，先查 `docs/PROJECT_DIRECTORY_GUIDE.md` 和 `docs/DUAL_TRACK_ARCHITECTURE.md`。

## 如何安全修改 Python Agent Engine

- 先确认是否影响 v1 Streamlit 和 v2 FastAPI。
- 不直接改写 LangGraph 主流程，优先小步补充工具函数或服务适配。
- 保持 `run_summary` 和 `ui_view_model` 向后兼容。
- Runner 相关修改必须保留 Python Runner fallback。
- 修改后更新 `docs/API_CONTRACT.md`、`docs/TECH_STACK.md` 或相关模块 README。

建议测试：

```powershell
python -m compileall .
python graph_demo.py
python -m uvicorn api_server:app --host 127.0.0.1 --port 8001
```

## 如何安全修改 Vue 前端

- API 路径差异只放在 `frontend-vue/src/api/`。
- 页面组件只消费类型化 API 和 ViewModel，不直接拼后端路径。
- 保持 Python Direct 和 Java Gateway 两种模式。
- 修改展示字段时兼容缺失字段和旧历史记录。

建议测试：

```powershell
cd frontend-vue
npm install
npm run build
npm run dev
```

## 如何安全修改 Java 后端

- Java 层是平台服务层和 API Gateway，不替代 Python Agent Engine。
- 原有代理接口保持原样，新平台接口使用 `ApiResponse`。
- 修改 MySQL 相关逻辑前确认是否需要 migration 或兼容旧数据。
- 不在 Java 中写死 Python API 地址、数据库密码或 API Key。

建议测试：

```powershell
cd backend-java
mvn clean package
mvn spring-boot:run
```

## 如何安全修改 C++ Runner

- 默认 `runner_mode` 保持 `python`。
- C++ Runner 不可用时必须回退 Python Runner。
- 不绕过危险关键词扫描。
- 不把当前最小版本描述为完整沙箱。

建议测试：

```powershell
cd runner-cpp
cmake -S . -B build
cmake --build build --config Release
```

然后通过 `utils/cpp_runner_adapter.py` 或 Python Runner 集成路径验证 fallback。

## 修改后必须测试哪些命令

基础检查：

```powershell
git diff --check
docker compose config --services
```

按修改范围追加：

- Python：`python -m compileall .`
- FastAPI：`python -m uvicorn api_server:app --host 127.0.0.1 --port 8001`
- Streamlit：`python -m streamlit run webui.py`
- Vue：`cd frontend-vue; npm run build`
- Java：`cd backend-java; mvn clean package`
- Docker：`docker compose up --build`

## 修改后必须更新哪些文档

- 架构边界变化：`docs/DUAL_TRACK_ARCHITECTURE.md`
- 目录变化：`docs/PROJECT_DIRECTORY_GUIDE.md`
- API 变化：`docs/API_CONTRACT.md`
- Docker 变化：`docs/DOCKER_COMPOSE_GUIDE.md`
- 技术栈变化：`docs/TECH_STACK.md`
- 风险和兜底变化：`docs/RISK_AND_STABILITY.md`
- Codex 协作规则变化：`docs/CODEX_PROJECT_CONTEXT.md`、`docs/MODULE_BOUNDARY.md`
- 用户入口变化：根 `README.md`

# 安全变更检查清单

每次修改前后都建议复制本清单到任务说明或 PR 描述中逐项确认。

## 影响范围

- [ ] 是否影响 v1.0 Streamlit 演示？
- [ ] 是否影响 v1.0 CLI 演示？
- [ ] 是否影响 v2.0 Vue 平台页面？
- [ ] 是否影响 v2.0 Java Gateway？
- [ ] 是否影响 Python FastAPI？
- [ ] 是否影响 Docker Compose？
- [ ] 是否影响 MySQL 数据？
- [ ] 是否影响 C++ Runner？

## 接口和数据

- [ ] 是否影响 API 返回结构？
- [ ] 是否影响 `run_summary`？
- [ ] 是否影响 `ui_view_model`？
- [ ] 是否影响历史运行读取？
- [ ] 是否影响报告读取或生成？
- [ ] 是否影响模型配置？
- [ ] 是否影响插件配置？

## 前端和后端

- [ ] 是否影响 Vue 页面路由？
- [ ] 是否影响 Vue Python Direct 模式？
- [ ] 是否影响 Vue Java Gateway 模式？
- [ ] 是否影响 Java 代理接口？
- [ ] 是否影响 Java 平台接口？
- [ ] 是否影响 MySQL 表结构或初始化数据？

## 运行和部署

- [ ] 是否影响 `python -m streamlit run webui.py`？
- [ ] 是否影响 `python graph_demo.py`？
- [ ] 是否影响 `python -m uvicorn api_server:app --host 127.0.0.1 --port 8001`？
- [ ] 是否影响 `npm run build`？
- [ ] 是否影响 `mvn clean package`？
- [ ] 是否影响 `docker compose up --build`？

## 文档

- [ ] 是否更新 README？
- [ ] 是否更新 `CODEX_PROJECT_CONTEXT.md`？
- [ ] 是否更新 `MODULE_BOUNDARY.md`？
- [ ] 是否更新 `DUAL_TRACK_ARCHITECTURE.md`？
- [ ] 是否更新 `API_CONTRACT.md`？
- [ ] 是否更新 `DOCKER_COMPOSE_GUIDE.md`？
- [ ] 是否更新 `TECH_STACK.md`？
- [ ] 是否更新 `TASKS.md`？

## 安全

- [ ] 是否避免提交 `.env`？
- [ ] 是否避免写死 API Key？
- [ ] 是否保留 Python Runner fallback？
- [ ] 是否避免删除 Streamlit v1？
- [ ] 是否避免删除 Python Direct？
- [ ] 是否避免删除 Java Gateway？

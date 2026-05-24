# 安全变更检查清单

## 影响范围

- [ ] 是否影响 Vue 页面？
- [ ] 是否影响 Java Gateway？
- [ ] 是否影响 FastAPI Python Agent Engine？
- [ ] 是否影响 MySQL 数据或 JPA 实体？
- [ ] 是否影响 Docker Compose？
- [ ] 是否影响 CodeAgent 文件操作？
- [ ] 是否影响 RunEvent / SSE？
- [ ] 是否影响 Workflow Replay？
- [ ] 是否影响 Workflow Templates / Editor？
- [ ] 是否影响 C++ Runner fallback？

## 契约检查

- [ ] 是否改变 `run_summary`？
- [ ] 是否改变 `ui_view_model`？
- [ ] 是否改变 `workflow_events`？
- [ ] 是否改变 Java `ApiResponse`？
- [ ] 是否改变已有 API 路径？

## 文档检查

- [ ] 是否更新 README？
- [ ] 是否更新 `CODEX_PROJECT_CONTEXT.md`？
- [ ] 是否更新 `API_CONTRACT.md`？
- [ ] 是否更新 `TASKS.md`？
- [ ] 是否更新 Figma 映射？

## 验证检查

- [ ] `npm run build`
- [ ] `mvn -DskipTests package`
- [ ] `docker compose up -d --build`
- [ ] Python health
- [ ] Java health
- [ ] Vue 页面 HTTP 200
- [ ] CodeAgent smoke
- [ ] Workflow Template smoke

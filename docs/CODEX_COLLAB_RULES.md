# Codex 协作规范

本文定义 Codex 或其他自动化协作者修改项目时必须遵守的规则。

## 修改前必须阅读

每次进入项目后，先阅读：

- `docs/CODEX_PROJECT_CONTEXT.md`
- `docs/MODULE_BOUNDARY.md`
- `docs/DUAL_TRACK_ARCHITECTURE.md`

如果修改 Docker、API、前端或 Java，还应阅读：

- `docs/API_CONTRACT.md`
- `docs/DOCKER_COMPOSE_GUIDE.md`
- `docs/TECH_STACK.md`

## Codex 禁止事项

禁止：

- 删除 Streamlit v1 演示链路。
- 删除 Python Direct 模式。
- 删除 Java Gateway 模式。
- 删除 `run_summary`。
- 删除 `ui_view_model`。
- 删除 Docker Compose 多服务启动。
- 把 API Key 写死到源码或提交文件中。
- 大规模重写 LangGraph 流程。
- 在整理阶段新增登录、权限或复杂平台业务。

## 修改规则

- 小步修改，一次只解决一个明确问题。
- 优先新增模块或适配层，不直接重写核心流程。
- 修改共享核心前，检查 v1-demo 和 v2-platform 是否都会受影响。
- API 返回结构只能兼容扩展，不能随意删除字段。
- 前端路径判断集中在 API client，不散落到页面组件。
- Java 平台层新增能力时，保留原有代理接口。
- 每次修改后同步更新相关 docs。

## 修改检查清单

提交或结束工作前检查：

- 是否影响 v1.0 Streamlit 演示？
- 是否影响 v2.0 Vue 平台页面？
- 是否影响 FastAPI 现有接口？
- 是否影响 Java Gateway 代理接口？
- 是否影响 Docker Compose 服务名、端口或 volumes？
- 是否影响 Python Direct 模式？
- 是否影响 `run_summary` 或 `ui_view_model`？
- 是否更新 README 或 docs？
- 是否避免提交 `.env`、报告、运行历史和构建产物？

## 推荐验证命令

```powershell
git diff --check
docker compose config --services
```

如果修改了前端、Java 或 Python，再按对应模块补充构建和测试。

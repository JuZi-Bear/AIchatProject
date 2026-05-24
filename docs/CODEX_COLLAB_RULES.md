# Codex 协作规则

## 修改前必读

- `docs/CODEX_PROJECT_CONTEXT.md`
- `docs/MODULE_BOUNDARY.md`
- `docs/V2_ONLY_RUNTIME_SIMPLIFICATION.md`
- `docs/FIGMA_UI_WORKFLOW.md`

## 禁止事项

- 把 API Key 写死到代码或文档。
- 破坏 `run_summary`、`ui_view_model`、`workflow_events` 契约。
- 绕过 Java Gateway 直接让 Vue 解析 LangGraph 原始 state。
- 让 CodeAgent 自动决定跨文件修改范围。
- 在未确认前引入用户系统、权限系统、队列系统或动态 LangGraph 编排。
- 删除 Docker Compose v2 主服务。

## 修改规则

- 小步修改。
- 优先新增模块或局部适配。
- 不直接重写核心流程。
- UI 修改优先同步 Figma 设计源说明。
- 每次修改后同步 README 或 docs。

## 检查清单

- 是否影响 Vue 页面？
- 是否影响 Java Gateway？
- 是否影响 FastAPI？
- 是否影响 MySQL 数据？
- 是否影响 Docker Compose？
- 是否影响 CodeAgent 审计和事件？
- 是否影响 Replay？
- 是否更新文档？
- 是否跑过必要 smoke？

# Codex UI/UX 优化工作流

本文件用于记录 Web UI 系统化优化的阶段进度。当前目标是在不改变 LangGraph 核心流程、不改变 Agent 业务逻辑的前提下，逐步改善 Streamlit Web UI，并为后续更独立的前端实现预留稳定数据结构。

## 阶段一：UI/UX 优化工作流文档

- [x] 新建 `docs/ui_workflow/`。
- [x] 新增 `UI_REDESIGN_PLAN.md`。
- [x] 新增 `UI_LAYOUT_SPEC.md`。
- [x] 新增 `UI_INTERACTION_SPEC.md`。
- [x] 新增 `UI_COMPONENTS_SPEC.md`。
- [x] 新增 `UI_ANIMATION_SPEC.md`。
- [x] 新增 `UI_ACCEPTANCE_CHECKLIST.md`。

## 阶段二：统一 UI 状态数据层

- [x] 在 `utils/ui_state_builder.py` 中实现 `build_ui_view_model(state, run_summary=None)`。
- [x] 在 `utils/ui_state_builder.py` 中实现列表结构的 `build_workflow_status(state)`。
- [x] 在 `utils/ui_state_builder.py` 中实现 `build_result_index(state, run_summary=None)`。
- [x] 保留 `build_workflow_status_map(state)` 兼容当前 Streamlit 工作流渲染。
- [x] `webui.py` 开始通过 UI ViewModel 获取摘要、插件和报告展示数据。
- [x] 原始 state 继续只在开发模式 Raw State 中展示。

## 阶段三：布局顺序优化

- [x] 根据 `UI_LAYOUT_SPEC.md` 调整主展示区顺序。
- [x] 将最终结果、质量评分和自动修复高光提升到首屏附近。
- [x] 合并重复卡片，减少空白 box。
- [x] Web UI 以 UI ViewModel 为主要展示数据源重排 Header、摘要、工作流、最终总览、详情 Tabs、结果索引和历史记录。

## 阶段四：交互与视觉引导优化

- [x] 新增 `services/run_service.py` 作为 Application Service 层。
- [x] Web UI 通过 `create_run(request)` 执行工作流，不再直接调用 LangGraph 核心入口。
- [x] 服务层统一返回 `state`、`run_summary` 和 `ui_view_model`。
- [x] 新增 `docs/API_CONTRACT.md`，记录未来 FastAPI / Vue / Java 可复用接口结构。
- [x] 新增 `render_workflow_timeline(ui_view_model)`，用统一 ViewModel 展示工作流时间轴。
- [x] Timeline 使用 `st.progress()`、`st.status()` / `st.info()` 和 CSS 状态样式增强视觉引导。
- [x] 自动修复高光时刻改为从 `ui_view_model` 读取摘要、Sentry 分析和最终测试结果。
- [x] 新增 `render_result_overview(ui_view_model)`，一屏展示成功状态、run_id、修复、测试、覆盖率、质量、安全和报告路径。
- [x] 新增 `render_result_index(ui_view_model)`，用 Tabs + expander 提供最终代码、pytest、错误、修复、插件、报告和历史入口。
- [x] 根据 `UI_INTERACTION_SPEC.md` 简化用户查找结果路径。
- [x] 抽离 `render_header`、`render_summary_cards`、`render_agent_tabs`、`render_plugin_results`、`render_report_section`、`render_history_section`。
- [x] 短字段改为 columns 横向排列，长内容默认进入 expander。
- [x] 规范卡片 padding、margin 和高度，减少重复 box 与大面积空白。
- [ ] 根据 `UI_ANIMATION_SPEC.md` 增加轻量进度条和当前 Agent 高亮。
- [ ] 强化自动修复时的视觉提示。

## UI 开发约束

- UI 优化必须优先通过 `ui_view_model` 和 `services/run_service.py` 获取数据。
- `webui.py` 只负责展示和少量 Streamlit 交互，不允许重新堆叠复杂业务判断。
- 新增页面组件时优先读取 `summary_cards`、`workflow_steps`、`agent_outputs`、`plugin_outputs`、`report` 和 `result_index`。
- 原始 `state` 只用于开发模式 Raw State、历史回放和调试。
- CLI 当前可以保持 `graph_demo.py` 原逻辑，后续可迁移到 `run_service` 以获得同样返回结构。

## 阶段五：验收与回归

- [ ] 使用 `UI_ACCEPTANCE_CHECKLIST.md` 做页面验收。
- [ ] 回归简单案例、翻车修复案例和综合案例。
- [ ] 确认 CLI、Docker、插件、报告和历史记录不受影响。

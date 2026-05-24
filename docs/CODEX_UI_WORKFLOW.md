# v2-only UI Workflow Notes

当前 UI 以 `frontend-vue/` 为唯一平台展示入口。旧 UI 优化记录已不再作为当前工作依据。

## 当前重点

- Dashboard 平台总览。
- RunConsole 运行与 CodeAgent 展示。
- Workflow Editor 无限画布与节点属性浮层。
- Replay 事件回放。
- Agents / Workflow Templates / Reports / History 管理页面。

## 修改原则

- 优先保持 Figma 风画布体验。
- 不在页面组件中解析 LangGraph 内部 state。
- 前端优先消费 `run_summary`、`ui_view_model`、`workflow_events`。
- UI 改动后执行 `frontend-vue` 构建和页面 smoke。

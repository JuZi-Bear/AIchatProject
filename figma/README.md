# Figma Design Source

本目录用于把 `frontend-vue/` 的 UI 设计源迁移到 Figma-first 工作流。

## 目标

- 让项目 UI 有一个个人可编辑的 Figma 设计源。
- 让后续 Dashboard、RunConsole、Workflow Editor、Replay、CodeAgentPanel 等页面修改先经过 Figma 设计源。
- 让 Codex 后续做 UI 修改时，优先考虑“Figma 可编辑组件 + Vue 实现同步”，而不是只改代码。

## 当前状态

- 轨道归属：`v2-platform`
- 开发状态：`active`
- 当前交付：Figma 设计源规范、设计 token、页面映射、组件清单、Figma 同步脚本。
- 仍需用户提供：个人 Figma 设计文件 URL 或可用的 Figma plan/team key。

## 核心文件

- `design_link.md`：Figma 文件链接和协作说明。
- `design_tokens.json`：颜色、字体、间距、圆角、阴影等设计 token。
- `frontend_ui_map.json`：Vue 页面到 Figma Frame 的映射。
- `component_inventory.json`：可沉淀为 Figma 组件的前端组件清单。
- `create_figma_ui_source.js`：可通过 Figma `use_figma` 工具执行的设计源生成脚本。

## 不要随意修改

- 不要删除 `design_tokens.json` 中已经映射到 Vue 的 token 名称。
- 不要随意重命名 Figma Frame 名称，避免后续无法从 Figma 回写或比对。
- 不要把 Figma 设计源变成只适合 PPT 的静态稿；它应该服务前端实现。

## 推荐工作流

1. 在 Figma 中创建或提供一个 design 文件。
2. 使用 `create_figma_ui_source.js` 初始化页面和组件。
3. 在 Figma 中编辑页面布局、组件状态和视觉细节。
4. Codex 根据 Figma 设计回写 Vue 页面或 CSS。
5. 更新 `frontend_ui_map.json` 和相关文档。

## 相关文档

- `docs/FIGMA_UI_WORKFLOW.md`
- `docs/CODEX_PROJECT_CONTEXT.md`
- `docs/CODEX_UI_WORKFLOW.md`

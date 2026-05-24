# Figma-first UI 工作流

本文说明 AI Multi-Agent Pipeline 后续前端 UI 如何与 Figma 设计源协作。

## 目标

把 `frontend-vue/` 的 UI 从“只在代码里改”升级为：

```text
Figma 可编辑设计源 → Vue3 + TypeScript 实现 → 本地/比赛演示验证
```

这样用户可以直接在个人 Figma 文件里修改页面、组件、布局和视觉状态，Codex 再按设计源同步到前端。

## 当前交付

项目已新增 `figma/` 目录：

- `figma/design_tokens.json`：设计 token。
- `figma/frontend_ui_map.json`：Vue 页面和 Figma Frame 对应关系。
- `figma/component_inventory.json`：前端组件和 Figma 组件对应关系。
- `figma/create_figma_ui_source.js`：Figma 初始化脚本。
- `figma/design_link.md`：Figma 文件链接和协作说明。

## 需要用户提供

当前已同步到用户个人 Figma design 文件：

```text
https://www.figma.com/design/6Zz9nZmWhUCRM5XK53vjv9/Untitled?node-id=0-1
```

已生成页面：

- `AI Pipeline UI Source`

已生成 12 个可编辑 Frame：

- `00 Cover / Figma Editable UI Source`
- `01 Design System / Tokens and Components`
- `Dashboard / Platform Overview`
- `RunConsole / Execute Workflow`
- `Workflow Editor / Drag CodeAgent`
- `Replay / Workflow Playback`
- `RunHistory / Detail and Events`
- `Reports / Markdown Center`
- `Agents / Registry`
- `Workflow Templates / Versioned Templates`
- `Models / Provider Config`
- `Plugins / Plugin Config`

## 页面映射规则

| Vue 路由 | Vue 文件 | Figma Frame |
|---|---|---|
| `/` | `frontend-vue/src/views/Dashboard.vue` | `Dashboard / Platform Overview` |
| `/runs/new` | `frontend-vue/src/views/RunConsole.vue` | `RunConsole / Execute Workflow` |
| `/workflows/editor` | `frontend-vue/src/views/WorkflowEditor.vue` | `Workflow Editor / Drag CodeAgent` |
| `/history` | `frontend-vue/src/views/RunHistory.vue` | `RunHistory / Detail and Events` |
| `/replay/:platformRunId` | `frontend-vue/src/views/WorkflowReplay.vue` | `Replay / Workflow Playback` |
| `/reports` | `frontend-vue/src/views/Reports.vue` | `Reports / Markdown Center` |
| `/agents` | `frontend-vue/src/views/Agents.vue` | `Agents / Registry` |
| `/workflows/templates` | `frontend-vue/src/views/WorkflowTemplates.vue` | `Workflow Templates / Versioned Templates` |
| `/models` | `frontend-vue/src/views/Models.vue` | `Models / Provider Config` |
| `/plugins` | `frontend-vue/src/views/Plugins.vue` | `Plugins / Plugin Config` |

完整映射见 `figma/frontend_ui_map.json`。

## Workflow Editor Figma 风交互基准

`/workflows/editor` 当前以 Figma 类画板为 UI 基准：

- 主体是无限感画布，支持滚轮缩放、空格拖拽或中键拖拽平移。
- Agent / CodeAgent / If / And / Or 节点入口放在左侧浮动 Palette，而不是底部常驻列表。
- 只有点击节点时才显示右侧属性浮层，点击空白、Esc 或关闭按钮隐藏。
- 连接线、节点和画布网格必须在同一个 viewport/world 坐标模型下缩放和平移，避免线条错位。
- CodeAgent 节点选中后在属性浮层中显示 CodeAgentPanel，保留执行、审计日志和 diff 预览链路。

后续 Figma 中的 `Workflow Editor / Drag CodeAgent` Frame 应按以上交互拆分为：

- `WorkflowEditor/InfiniteCanvas`
- `WorkflowEditor/FloatingPalette`
- `WorkflowEditor/AgentNode`
- `WorkflowEditor/InspectorOverlay`
- `CodeAgent/Panel`

## 组件映射规则

重要 Vue 组件必须尽量有 Figma 对应组件：

- `App.vue` → `Shell/AppShell`
- `SummaryCards.vue` → `Data/SummaryCards`
- `WorkflowTimeline.vue` → `Workflow/Timeline`
- `WorkflowCanvas.vue` → `WorkflowEditor/Canvas`
- `AgentNode.vue` → `WorkflowEditor/AgentNode`
- `CodeAgentPanel.vue` → `CodeAgent/Panel`
- `ReplayEventCard.vue` → `Replay/EventCard`
- `ReportPreview.vue` → `Reports/Preview`

完整清单见 `figma/component_inventory.json`。

## Codex 修改 UI 的规则

后续涉及 `frontend-vue/` 的 UI 修改时，Codex 应先判断：

- 是否需要同步 Figma Frame。
- 是否需要新增或修改 Figma 组件。
- 是否需要更新 `design_tokens.json`。
- 是否需要更新 `frontend_ui_map.json` 或 `component_inventory.json`。

如果用户已经给出 Figma 文件 URL，则优先：

1. 读取或更新 Figma 设计。
2. 再修改 Vue 代码。
3. 最后记录 Figma 与 Vue 的同步关系。

如果用户没有给出 Figma 文件 URL，则：

1. 先更新 `figma/` 下的设计源规范文件。
2. 在最终说明中提示用户提供 Figma URL 后可同步。

## 不建议做的事

- 不要只改 Vue UI 而完全不更新 Figma 设计源。
- 不要把 Figma 设计源做成无法编辑的截图集合。
- 不要随意更改 Frame 名称。
- 不要在 Figma 中删除 CodeAgent、Replay、Workflow Editor 的核心演示链路。
- 不要让 MySQL / Java / Python 的平台概念在 Figma 页面上消失。

## 最小同步流程

```text
用户改 Figma
↓
Codex 读取 Figma 设计上下文
↓
更新 Vue 页面 / 组件 / CSS
↓
运行 npm build 或页面检查
↓
更新 figma 映射文档
```

## 后续可升级

- 使用 Figma Variables 管理颜色和间距 token。
- 使用 Figma Component Variants 管理 Agent 节点状态。
- 为 `Element Plus` 组件建立项目专用 Figma 组件库。
- 建立 Figma to Vue 的变更检查清单。

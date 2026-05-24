# Figma 协作说明

## 当前状态

本项目已进入 Figma-first UI 工作流。后续 `frontend-vue/` 的重要 UI 修改，应优先维护一个个人可编辑的 Figma 设计源，再同步到 Vue 实现。

当前仍缺少实际 Figma 文件 URL。拿到你的 Figma 设计文件后，可使用：

```text
figma/create_figma_ui_source.js
```

通过 Figma `use_figma` 工具初始化可编辑页面、组件和设计 token。

## Figma 文件链接

请在这里记录你的个人 Figma 文件：

```text
Figma URL: https://www.figma.com/design/6Zz9nZmWhUCRM5XK53vjv9/Untitled?node-id=0-1
File Key: 6Zz9nZmWhUCRM5XK53vjv9
Owner: JvZi_Bear
Last Sync: 2026-05-23
Status: 已同步 AI Pipeline UI Source 页面，包含 12 个可编辑 Frame。
```

历史备注：

- `https://www.figma.com/site/H3g1PTceRUmawXoompH6dL/Untitled?...` 是 Figma Site 链接，不作为当前 UI 设计源。

## 设计目标

为 AI Multi-Agent Pipeline 准备一套可长期维护的 Web UI 设计源，重点覆盖：

- Dashboard 平台总览
- RunConsole 运行任务
- Workflow Editor 拖拽工作流编辑器
- CodeAgentPanel 文件操作、审计日志、diff、违规路径高亮
- RunHistory 历史记录和事件时间线
- Workflow Replay 回放
- Reports / Models / Plugins / Agents / Templates 配置和管理页面

## Figma 文件建议

建议新建一个 Figma design 文件，命名为：

```text
AI Multi-Agent Pipeline UI Source
```

推荐页面结构：

```text
AI Pipeline UI Source
  00 Cover / Figma Editable UI Source
  01 Design System / Tokens and Components
  Dashboard / Platform Overview
  RunConsole / Execute Workflow
  Workflow Editor / Drag CodeAgent
  RunHistory / Detail and Events
  Replay / Workflow Playback
  Reports / Markdown Center
  Agents / Registry
  Workflow Templates / Versioned Templates
  Models / Provider Config
  Plugins / Plugin Config
```

## 协作流程

1. 用户在 Figma 中修改页面、组件或 token。
2. Codex 根据 Figma Frame 更新 Vue 页面和 CSS。
3. 更新 `figma/frontend_ui_map.json` 的页面映射。
4. 更新 `figma/component_inventory.json` 的组件状态。
5. 涉及演示链路时，同步更新 README 和相关 docs。

## 视觉风格建议

- 整体风格：现代控制台、清晰、适合比赛现场演示。
- 主色建议：浅色平台控制台 + 深色侧边栏 + 蓝色主操作。
- Agent 色彩：
  - Product Agent：蓝色
  - Coder Agent：绿色
  - Tester Agent：黄色
  - Sentry Agent：红色
  - CodeAgent：红色 / 安全强调
- 日志区域使用等宽字体，便于展示 stdout 和 stderr。
- 关键状态使用明确图标和颜色：
  - 成功：绿色
  - 失败：红色
  - 修复中：黄色
  - 违规路径：红色高亮

## 组件建议

- AppShell：侧边栏 + 顶栏 + 内容区
- SummaryCards：运行结果摘要
- WorkflowTimeline：工作流状态
- WorkflowCanvas：拖拽画布
- AgentNode：Agent 节点
- CodeAgentPanel：文件操作、安全审计、diff
- ReplayEventCard：事件回放卡片
- ReportPreview：Markdown 报告预览

## 设计交付物

Figma 中建议交付：

- 桌面端 1440x900 页面 Frame
- 基础组件库和状态变体
- CodeAgent 安全操作高光状态
- Workflow Editor 拖拽场景
- Replay 回放场景
- 与 `frontend-vue/src` 文件对应的 Frame 命名

## 相关文档

- `figma/README.md`：Figma 设计源目录说明
- `figma/design_tokens.json`：设计 token
- `figma/frontend_ui_map.json`：Vue 页面到 Figma Frame 映射
- `figma/component_inventory.json`：组件清单
- `docs/FIGMA_UI_WORKFLOW.md`：Figma-first 工作流
- `docs/UI_SPEC.md`：页面设计规格
- `README.md`：项目运行说明

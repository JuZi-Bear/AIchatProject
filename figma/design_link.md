# Figma 协作说明

## 设计目标

为 AI Multi-Agent Pipeline 准备一套比赛演示用的 Web UI 设计稿，重点展示：

- 用户输入需求
- 多 Agent 工作流
- 代码生成、运行、报错、修复过程
- 最终报告与运行结果

本阶段只整理设计协作说明，不实现前端代码。

## Figma 文件建议

建议新建一个 Figma 文件，命名为：

```text
AI Multi-Agent Pipeline Demo UI
```

推荐页面结构：

```text
00 Cover
01 Components
02 Home
03 Agent Workflow
04 Run Logs
05 Reports
```

## 协作流程

1. 产品侧根据 `docs/UI_SPEC.md` 确认页面目标和内容。
2. 设计侧在 Figma 中建立组件和页面。
3. 开发侧根据 Figma 页面结构拆分前端组件。
4. 比赛前只保留关键演示链路，避免过度复杂。

## 视觉风格建议

- 整体风格：技术感、清晰、适合大屏演示。
- 主色建议：深色背景 + 蓝色高亮。
- Agent 色彩：
  - Product Agent：蓝色
  - Coder Agent：绿色
  - Tester Agent：黄色
  - Sentry Agent：红色
- 日志区域使用等宽字体，便于展示 stdout 和 stderr。
- 关键状态使用明确图标和颜色：
  - 成功：绿色
  - 失败：红色
  - 修复中：黄色

## 组件建议

- 顶部导航栏
- 需求输入框
- 主按钮：开始运行
- Agent 节点卡片
- 工作流连线
- 状态标签
- 日志面板
- 代码展示面板
- 报告列表卡片

## 设计交付物

Figma 中建议交付：

- 桌面端主流程页面
- 基础组件库
- Agent 节点状态变体
- 成功/失败/修复中状态样式
- 一套比赛演示用的完整页面串联

## 相关文档

- `docs/UI_SPEC.md`：页面设计规格
- `docs/DEMO_SCRIPT.md`：比赛演示脚本
- `README.md`：项目运行说明

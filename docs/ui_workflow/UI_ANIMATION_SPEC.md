# Web UI 轻量动画与动态反馈规格

## Streamlit 可实现的轻量动画方案

由于项目不引入复杂前端框架，动画只使用 Streamlit 原生能力和少量 CSS：

- `st.spinner()`：用于长耗时运行。
- `st.progress()`：用于整体流程进度。
- 动态 CSS class：用于节点高亮。
- `st.empty()` 占位容器：用于局部刷新。
- 简单文字变化：例如“运行中...”。

不使用：

- Vue / React / 独立前端工程。
- 复杂 JS 动画库。
- 数据库驱动的实时队列。

## 进度条设计

进度条表示整体流程阶段，而不是精确耗时。

建议阶段：

```text
Requirement      10%
Product Agent    20%
Coder Agent      35%
Tester Agent     50%
Approval Node    60%
Runner           70%
Sentry Repair    80%
Plugins          88%
Quality          94%
Report           100%
```

自动修复时，进度条可以回到 Coder / Tester 区间，并显示：

```text
正在进行第 N 轮自动修复
```

## Timeline 展示规则

第五步新增 `render_workflow_timeline(ui_view_model)`，作为 Web UI 主工作流展示组件。

约束：

- 只接收 `ui_view_model`。
- 不直接读取原始 `state`。
- 不直接调用 LangGraph。
- 不重新实现业务判断。

节点固定为：

```text
Requirement → Product Agent → Coder Agent → Tester Agent → Approval → Runner → Sentry Agent → Plugins → Quality → Report
```

每个节点展示：

- 节点名称。
- 中文状态。
- 简短摘要。
- 状态图标。

状态图标映射：

```text
waiting   → 等待中 ⚪
running   → 运行中 🔵
done      → 已完成 ✅
failed    → 失败 ❌
repairing → 修复中 🟡
skipped   → 已跳过 ⚪
```

Timeline 顶部使用 `st.progress()` 展示整体进度。当前执行节点通过 `st.status()` 或 `st.info()` 展示，文案格式为：

```text
当前步骤：Coder Agent · 运行中
```

自动修复时，Timeline 下方显示“自动修复高光时刻”，内容来自 `ui_view_model`：

- `summary_cards.retry_count`
- `agent_outputs.error_summary`
- `agent_outputs.sentry_result`
- `summary_cards.success`
- `summary_cards.test_success`

当 `retry_count > 0` 时展示：

- 第一次运行失败。
- Sentry Agent 发现问题。
- Coder Agent 自动修复。
- 测试最终结果。

当 `retry_count == 0` 且运行已完成时展示：

```text
本次任务一次运行成功，未触发自动修复。
```

## spinner 使用规范

适合使用 spinner 的场景：

- 调用模型。
- 运行 LangGraph。
- 执行 pytest。
- Docker 不在 Web UI 内执行，不需要 spinner。

不适合使用 spinner 的场景：

- 静态报告查看。
- 历史记录切换。
- 插件结果展开。

spinner 文案应短：

```text
Product Agent 正在拆解需求...
Coder Agent 正在生成代码...
Tester Agent 正在生成并运行 pytest...
Sentry Agent 正在分析错误...
```

## 状态节点动态变化

节点状态变化规则：

- Waiting / Skipped：灰色。
- Running：蓝色并轻微高亮。
- Done：绿色。
- Failed：红色。
- Repairing：黄色。

运行过程中只更新变化节点，避免整页闪动。

## 当前执行 Agent 高亮

当前 Agent 应同时在两个地方可见：

- 顶部状态摘要卡片：显示“当前执行 Agent”。
- 工作流节点：当前节点蓝色或黄色高亮。

高亮要求：

- 不使用夸张动画。
- 不使用闪烁。
- 使用边框、背景色和状态文案即可。

## 自动修复时的视觉提示

当 Runner 或 pytest 失败并进入自动修复：

- Runner 节点显示 Failed。
- Sentry Agent 节点显示 Repairing。
- Coder Agent 节点下一轮显示 Repairing。
- 页面显示“自动修复高光时刻”卡片。
- retry_count 大于 0 时相关节点显示黄色边框。

建议文案：

```text
已检测到错误，Sentry Agent 正在分析并触发第 N 轮修复。
```

## Streamlit 动效限制

Streamlit 页面以脚本重跑为主，不适合实现复杂连续动画。因此 v1.0 只使用轻量动态反馈：

- `st.progress()` 表示阶段推进。
- `st.status()` 或 `st.info()` 表示当前步骤。
- `st.spinner()` 表示长耗时工作流正在运行。
- CSS 颜色和边框表示节点状态。
- `st.empty()` 用于局部刷新。

不使用闪烁、轮播、拖拽、复杂 Canvas 或 JavaScript 动画，避免比赛现场部署风险。

## 后续 Vue/TS 升级方向

未来 Vue3 + TypeScript 前端可以直接复用 `ui_view_model["workflow_steps"]`，升级为真正动画时间轴：

- 节点连线动画。
- 当前 Agent 脉冲高亮。
- 自动修复回环动画。
- Runner 失败到 Sentry 的转场动画。
- Report 节点成功收束动画。

这些增强属于 v2.0 前端工程，不影响当前 Streamlit v1.0 演示版。

## 不使用复杂前端框架

本项目 v1.0 和后续 UI 优化阶段仍保持 Streamlit 技术栈：

- 不新增 Vue。
- 不新增 React。
- 不新增 Java / C++ 后端。
- 不新增数据库。
- 不拆分成复杂前后端架构。

这样可以保持比赛现场部署简单、调试直接、风险可控。

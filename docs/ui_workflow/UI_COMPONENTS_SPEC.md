# Web UI 组件规格

## UI ViewModel 数据结构

后续 Web UI 优化统一从 `utils/ui_state_builder.py` 中的 `build_ui_view_model(state, run_summary=None)` 获取展示数据，避免页面直接大量解析原始 LangGraph state。

顶层结构：

```text
header
summary_cards
workflow_steps
agent_outputs
plugin_outputs
report
result_index
raw
```

### header

用于页面顶部标题和运行上下文：

- `title`
- `subtitle`
- `run_status`
- `model_name`
- `model_provider`

### summary_cards

用于首屏状态摘要卡片：

- `success`
- `retry_count`
- `test_success`
- `coverage_percent`
- `quality_score`
- `security_status`
- `report_path`

### workflow_steps

用于 Agent 工作流节点渲染。每个节点结构：

```text
key
label
status
summary
order
```

节点 key 固定为：

```text
requirement
product
coder
tester
approval
runner
sentry
plugins
quality
report
```

节点状态固定为：

```text
waiting
running
done
failed
repairing
skipped
```

### agent_outputs

用于 Agent 输出 Tabs 和日志入口：

- `product_result`
- `code`
- `tester_result`
- `sentry_result`
- `stdout`
- `error_summary`
- `error_log`

### plugin_outputs

用于插件结果卡片：

- `plugin_results`
- `doc_result`
- `security_result`
- `refactor_result`
- `ui_result`

### report

用于报告查看卡片：

- `report_path`
- `report_markdown`
- `run_id`

### raw

仅用于开发模式：

- `state`
- `run_summary`

### 后续 Vue/TypeScript 复用

该 ViewModel 是稳定 UI 数据层。后续如果接入 Vue/TypeScript 前端或 Java 后端，可以直接让后端输出同构 JSON：

```text
GET /api/runs/{run_id}/ui-view-model
```

前端只消费 `header`、`summary_cards`、`workflow_steps`、`agent_outputs`、`plugin_outputs` 和 `report`，不直接依赖 LangGraph 原始 state 字段。

## 状态摘要卡片

用途：首屏展示最关键运行状态。

字段：

- success
- retry_count
- test_success
- coverage_percent
- quality_score
- security_status

展示要求：

- 使用 `st.columns()` 横向排列，紧凑高度。
- success 成功用绿色，失败用红色，等待用灰色。
- retry_count 大于 0 时用黄色提示。
- 不展示长文本。
- 不重复展示 report_path。
- 统一使用 `.summary-card` 样式，控制 padding 和 min-height。

## 组件渲染规范

Web UI 展示层统一拆分为以下函数：

- `render_header(ui_view_model)`
- `render_summary_cards(ui_view_model)`
- `render_workflow_timeline(ui_view_model)`
- `render_result_overview(ui_view_model)`
- `render_agent_tabs(ui_view_model)`
- `render_plugin_results(ui_view_model)`
- `render_report_section(ui_view_model)`
- `render_history_section(ui_view_model)`

规范：

- 每个函数只负责展示，不直接调用 LangGraph。
- 优先读取 `ui_view_model`，避免在页面中重复解析原始 state。
- 短字段使用 columns 横向排列。
- 长内容使用 expander 折叠。
- Raw State 只在开发模式展示。
- 不在多个区域重复展示完整 stdout、stderr、报告正文或完整代码。

## Agent 工作流节点

用途：展示多 Agent 协作过程。

节点：

- Requirement
- Product Agent
- Coder Agent
- Tester Agent
- Approval Node
- Runner
- Sentry Agent
- Plugins
- Quality
- Report

状态：

- Waiting
- Running
- Done
- Failed
- Repairing

展示要求：

- 当前节点突出显示。
- 失败节点红色。
- 修复链路黄色。
- 最终成功时 Report 节点绿色加粗。
- `render_workflow_timeline(ui_view_model)` 使用 `workflow_steps` 渲染，不直接读取 state。
- 每个节点只展示简短摘要，完整输出放入 Agent Tabs。

## Workflow Step Card

用途：作为时间轴节点，展示 Agent 当前阶段。

字段：

- 节点名称。
- 中文状态。
- 状态图标。
- 简短摘要。

样式：

- waiting / skipped：灰色。
- running：蓝色。
- done：绿色。
- failed：红色。
- repairing：黄色。
- padding 控制在 10-12px。
- 高度控制在紧凑范围，避免大面积空白。

## 高光时刻卡片

用途：突出自动修复能力。

内容：

- 第一次运行失败。
- 错误摘要。
- Sentry Agent 分析结果。
- Coder Agent 修复结果。
- 再次运行是否成功。

展示要求：

- 仅在运行后展示。
- 触发修复时使用黄色边框。
- 未触发修复时显示“一次运行成功，未触发自动修复”。

## 最终结果卡片

用途：运行完成后直接展示结论。

字段：

- 成功 / 失败
- run_id
- 修复次数
- pytest 测试结果
- 覆盖率
- 质量评分
- 安全状态
- 报告路径

展示要求：

- 成功绿色，失败红色。
- 不放长日志。
- 适合投屏一眼看懂。
- 使用 columns 横向排列。
- report_path 只在结果总览和报告入口简短展示，不重复铺满页面。

## Result Overview Card

用途：运行完成后的一屏结论区，由 `render_result_overview(ui_view_model)` 渲染。

要求：

- 展示核心指标，不展示完整日志。
- 不替代 Agent Tabs，只做结论摘要。
- 字段过长时允许文本换行，但不放大卡片高度。
- 与 Summary Card 使用一致的边距、字体和色彩风格。

## 测试结果卡片

用途：展示 pytest 测试是否通过。

字段：

- test_success
- 测试摘要
- pytest stdout 摘要
- pytest stderr 摘要

展示要求：

- 测试通过显示绿色。
- 测试失败显示红色并给出错误摘要。
- 完整测试代码放入 expander 或开发模式。

## 质量评分卡片

用途：展示最终代码质量。

字段：

- quality_score
- coverage_percent
- 安全状态
- 修复次数评分影响

展示要求：

- quality_score 使用大号数字。
- coverage 用百分比展示。
- 评分说明在开发模式中展开。

## 插件结果卡片

用途：展示自定义 AI 模块结果。

字段：

- plugin_name
- status
- summary
- detail

状态颜色：

- success：绿色
- warning：黄色
- failed：红色
- disabled：灰色

展示要求：

- 优先读取 `plugin_results`。
- 摘要先展示，详细内容折叠。
- 兼容 `doc_result`、`security_result`、`refactor_result`、`ui_result`。
- 由 `render_plugin_results(ui_view_model)` 渲染。
- 每个插件只显示一张结果卡片，避免重复 box。
- detail 必须放入 expander。

## 报告查看卡片

用途：展示和下载 Markdown 报告。

字段：

- 最新报告文件名
- 报告状态
- 报告内容预览
- 下载按钮

展示要求：

- 无报告时显示“暂无报告”。
- 报告正文默认放入 expander。
- 报告正文用 `st.markdown` 渲染。
- 代码块用 `st.code` 高亮。
- 错误摘要放入 expander。
- 由 `render_report_section(ui_view_model)` 渲染。
- report_path 不在多个大卡片中重复展示。

## Report Card

用途：报告入口和报告正文查看。

规则：

- 首屏只展示报告路径或报告状态。
- 完整 Markdown 必须折叠。
- 下载按钮可保留在报告区，但不应影响首屏布局。
- 报告区不重复展示 Agent 输出详情。

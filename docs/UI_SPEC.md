# UI 设计规格

## 设计范围

本文件用于指导 Figma 设计，不包含前端代码实现。

目标是为 AI Multi-Agent Pipeline 准备一套比赛现场演示用界面，帮助观众快速理解：

- 用户如何输入需求
- 多 Agent 如何协作
- 代码如何生成、运行、失败、修复
- 最终报告如何展示

## 全局设计建议

- 桌面优先，适合投影和大屏展示。
- 页面宽度建议按 1440px 设计。
- 背景使用深色或低饱和浅色均可，但日志和代码区域必须清晰。
- Agent 色彩保持统一：
  - Product Agent：蓝色
  - Coder Agent：绿色
  - Tester Agent：黄色
  - Sentry Agent：红色
- 日志和代码使用等宽字体。

## 页面一：首页

### 页面目标

让评委快速理解项目是什么，并引导用户开始一次自动开发演示。

### 核心组件

- 顶部导航栏
- 项目标题
- 项目简介
- 需求输入框
- 开始按钮
- 演示案例快捷选择
- 流程概览条

### 文字内容

标题：

```text
AI Multi-Agent Pipeline
```

副标题：

```text
从自然语言需求到代码生成、运行测试与自动修复的多智能体开发流水线
```

按钮：

```text
开始运行
```

案例按钮：

```text
简单成功案例
翻车修复案例
综合案例
```

流程概览：

```text
需求输入 → Product → Coder → Tester → Runner → Sentry → 自动修复
```

### 推荐布局

- 顶部为简洁导航栏，左侧显示项目名，右侧显示“演示案例”“运行日志”“报告”入口。
- 首屏中间放项目标题和副标题。
- 标题下方放一个大输入框，用于输入用户需求。
- 输入框右侧或下方放“开始运行”按钮。
- 输入区下方放三个演示案例快捷按钮。
- 页面底部展示一条横向流程概览。

### 交互说明

- 用户输入需求后点击“开始运行”，进入 Agent 工作流页。
- 点击演示案例后，输入框自动填入案例需求。
- 如果输入为空，按钮不可用或显示提示。

## 页面二：Agent 工作流页

### 页面目标

展示 Product、Coder、Tester、Sentry 节点的协作过程，让观众看到系统正在由多个 Agent 分工完成任务。

### 核心组件

- Agent 工作流图
- Agent 节点卡片
- 当前运行状态标签
- 生成代码面板
- 静态检查结果面板
- 修复次数指示器

### 文字内容

节点名称：

```text
Product Agent
Coder Agent
Tester Agent
Sentry Agent
Code Runner
```

状态文案：

```text
等待中
运行中
已完成
需要修复
修复中
运行成功
运行失败
```

页面标题：

```text
Agent 工作流
```

### 推荐布局

- 左侧为纵向或横向工作流图：
  - Product Agent
  - Coder Agent
  - Tester Agent
  - Code Runner
  - Sentry Agent
- 每个 Agent 使用不同颜色描边或状态灯。
- 右侧上方展示当前 Agent 的输出摘要。
- 右侧下方展示 Coder Agent 生成的代码。
- 底部展示修复次数，例如 `当前修复次数：1 / 3`。

### 交互说明

- 当前正在运行的 Agent 节点高亮。
- 节点完成后显示完成状态。
- 如果运行失败，Code Runner 节点变红，并显示连接到 Sentry Agent。
- Sentry 修复后，流程回到 Coder Agent。

## 页面三：运行日志页

### 页面目标

展示代码运行结果，包括 stdout、stderr、returncode 和修复次数，让自动修复过程可追踪。

### 核心组件

- 运行状态卡片
- stdout 日志面板
- stderr 日志面板
- returncode 标签
- 修复次数卡片
- 时间线列表

### 文字内容

页面标题：

```text
运行日志
```

状态：

```text
运行成功
运行失败
自动修复中
修复完成
超过最大修复次数
```

日志标题：

```text
stdout
stderr
returncode
retry_count
```

### 推荐布局

- 顶部放四个状态卡片：
  - 是否成功
  - returncode
  - 修复次数
  - 当前阶段
- 中间左右分栏：
  - 左侧 stdout
  - 右侧 stderr
- 底部放时间线，记录每轮运行和修复。

### 交互说明

- stdout 和 stderr 支持复制。
- stderr 出现内容时使用红色高亮。
- 点击某一轮修复记录，可以查看该轮错误摘要和 Sentry 建议。
- 修复成功时页面显示绿色成功状态。

## 页面四：报告页

### 页面目标

展示系统生成或整理的 Markdown 报告列表，方便赛后复盘、保存和展示结果。

### 核心组件

- 报告列表
- 报告卡片
- Markdown 预览区域
- 搜索框
- 状态筛选
- 导出按钮

### 文字内容

页面标题：

```text
报告中心
```

卡片字段：

```text
需求名称
运行状态
修复次数
生成时间
报告摘要
```

按钮：

```text
查看报告
导出 Markdown
复制结果
```

空状态：

```text
暂无报告，完成一次运行后将在这里生成结果。
```

### 推荐布局

- 左侧为报告列表，按时间倒序排列。
- 右侧为 Markdown 预览区域。
- 顶部提供搜索框和状态筛选。
- 报告卡片用状态颜色区分成功与失败。

### 交互说明

- 点击报告卡片，在右侧展示完整 Markdown 内容。
- 点击“导出 Markdown”下载或保存报告。
- 点击“复制结果”复制当前报告摘要。
- 可按状态筛选：
  - 全部
  - 成功
  - 失败
  - 自动修复成功

## Web UI 比赛展示版

当前 Streamlit Web UI 采用“左侧控制栏 + 右侧主展示区”的布局，方便比赛现场边讲解边操作。

### 左侧控制栏

页面目标：

- 集中放置所有运行控制项，避免评委观看时视线频繁跳转。
- 让演示人员可以快速切换案例、调整修复次数、启用插件并开始运行。

核心组件：

- 演示案例选择
- 自定义需求输入
- 最大修复次数设置
- 模型选择
- 在线 / 离线模式显示
- 演示模式 / 开发模式切换
- 自定义 AI 插件开关
- 运行前确认 checkbox
- 开始运行按钮
- 清空结果按钮

交互说明：

- 未勾选“我确认允许运行 AI 生成的代码”时，点击开始运行不会执行流程，并显示 warning 提示。
- 插件 checkbox 修改后自动写回 `config/agents.yaml`。
- 模型选择从 `config/models.yaml` 读取，可选择 DeepSeek、Qwen 或 GLM。
- 如果所选模型缺少 API Key，侧边栏显示 warning，并提示会使用离线演示响应。
- 清空结果按钮只清除本次页面会话中的运行结果，不删除历史报告文件。

### 模型选择区域

页面目标：

- 支持在比赛现场快速切换不同国产大模型服务。
- 展示当前模型名称、服务商和 base_url。

核心组件：

- 模型下拉框
- 当前模型名称
- 当前 base_url
- API Key 缺失 warning

可选模型：

```text
DeepSeek / deepseek-chat
Qwen / qwen-plus
GLM / glm-4-flash
```

交互说明：

- 用户选择模型后，运行时将 provider 写入 `state["model_provider"]`。
- LangGraph 节点会用该 provider 调用对应模型。
- 报告和历史记录保存 `model_provider`、`model_name` 和 `model_base_url`。

### 右侧状态摘要区

页面目标：

- 在第一屏快速说明当前系统状态。
- 让评委不用打开日志也能看到模型、运行状态、是否成功和插件数量。

核心组件：

- 当前模型
- 当前运行状态
- success
- retry_count
- enabled_plugins

推荐布局：

- 顶部横向五张状态卡片。
- 卡片使用白底、浅边框和紧凑字号，适合投影展示。

### Agent 工作流进度区

页面目标：

- 清楚展示从需求到报告的完整流水线。
- 体现 LangGraph 状态机和自动修复闭环。

节点：

```text
Requirement
Product Agent
Coder Agent
Tester Agent
Approval Node
Runner
Sentry Agent
Plugins
Quality
Report
```

状态：

```text
Waiting
Running
Done
Failed
Repairing
```

交互说明：

- 运行中节点显示蓝色。
- 完成节点显示绿色。
- 失败节点显示红色。
- 自动修复相关节点显示橙色 Repairing。
- Approval Node 在 Runner 前展示人工审批状态。
- 审批未通过时，Runner 不执行，流程直接进入 Plugins、Quality 和 Report。
- 如果 Runner 失败或 pytest 自动测试未通过，且未超过最大修复次数，流程进入 Sentry Agent，再回到 Coder Agent。
- Plugins 执行后进入 Quality Node，计算覆盖率、质量评分和评分摘要。

### 人工审批节点

页面目标：

- 在执行 AI 生成代码前加入人工确认步骤。
- 防止潜在危险代码未经确认就被自动运行。
- 让比赛评委看到系统具备 Human-in-the-loop 控制能力。

核心状态字段：

- `require_human_approval`
- `approved`
- `approval_message`

交互说明：

- Web UI 使用“我确认允许运行 AI 生成的代码”checkbox 作为审批输入。
- 勾选后，Approval Node 显示已通过，并允许 Runner 执行。
- 未勾选时，Approval Node 显示未通过，Runner 不执行。
- 未通过审批时，状态中写入：

```text
error_log = 用户拒绝执行 AI 生成代码
success = False
```

报告展示：

- 是否启用人工审批
- 是否通过审批
- 审批说明

### pytest 测试结果区域

页面目标：

- 让评委看到系统不只运行代码，还会自动生成测试并用测试结果驱动修复。
- 清晰展示 Tester Agent 生成的测试代码、测试是否通过和失败摘要。

核心组件：

- `test_success` 状态卡片
- 测试摘要卡片
- pytest 测试代码代码块
- pytest stdout 折叠面板
- pytest stderr 折叠面板
- coverage report 折叠面板

文字内容：

```text
pytest 自动测试结果
test_success：通过 / 未通过
coverage_percent：xx%
测试摘要：pytest 自动测试通过 / 错误摘要
```

推荐布局：

- 演示模式只显示 `test_success` 和测试摘要。
- 开发模式显示完整 `test_code`、`test_stdout`、`test_stderr` 和 `coverage_stdout`。
- stderr 默认在失败时展开，成功时折叠。

交互说明：

- 如果 `test_success == True` 且 Runner 也成功，流程进入插件和报告。
- 如果 `test_success == False`，Sentry Agent 接收测试代码和 pytest 日志，判断失败原因。
- Coder Agent 修复时需要修复业务代码，不能通过修改测试来规避问题。

### 质量评分区域

页面目标：

- 用量化方式说明最终代码质量，而不是只说“能运行”。
- 让比赛现场快速看到测试、覆盖率、安全和自动修复次数带来的综合评分。

核心组件：

- 大号 `quality_score` 分数卡片
- `coverage_percent` 覆盖率卡片
- pytest 通过状态
- 安全状态
- 完整评分依据
- coverage report 折叠面板

文字内容：

```text
质量评分
quality_score：xx/100
coverage_percent：xx%
test_success：通过 / 未通过
安全状态：安全检查通过 / 发现风险
```

推荐布局：

- 演示模式使用四张醒目卡片：质量总分、覆盖率、测试状态、安全状态。
- 开发模式使用指标卡 + 完整 `quality_summary` + `coverage_stdout`。

评分规则：

- pytest 通过：30 分
- 程序运行成功：20 分
- 覆盖率最高 20 分
- 安全检查通过：15 分
- 自动修复次数最高 15 分

交互说明：

- Quality Node 位于 Plugins 和 Report 之间。
- 报告和历史记录都保存 `quality_score`、`quality_summary`、`coverage_percent` 和 `coverage_stdout`。

### 模型对比 Tab

页面目标：

- 让同一需求下不同模型的表现可以横向比较。
- 为答辩 PPT 提供可复制的指标表格。

核心组件：

- 模型对比表格
- 每个模型的详情折叠面板
- 对比报告下载按钮

对比指标：

```text
模型
成功状态
失败次数
修复次数
pytest 是否通过
覆盖率
质量评分
插件摘要
```

交互说明：

- 用户在侧边栏启用“模型对比模式”后，可以选择 2-3 个模型。
- 每个模型独立执行完整 LangGraph 流程。
- 对比结果写入 `reports/report_compare_{run_id}.md`。
- 每个模型状态写入 `runs/{run_id}_model1.json`、`runs/{run_id}_model2.json`、`runs/{run_id}_model3.json`。
- 详情折叠面板展示该模型 stdout、stderr、doc_result、security_result、refactor_result 和 ui_result。

### 高亮颜色设计

Agent 工作流节点：

- Waiting：灰色，表示等待执行。
- Running：蓝色，表示当前正在运行。
- Done：绿色，表示已完成。
- Failed：红色，表示该节点失败。
- Repairing：黄色，表示正在进入自动修复。

修复次数展示：

- 每个节点卡片显示 `retry_count`。
- 当 `retry_count > 0` 时，Coder、Tester、Runner、Sentry 节点使用黄色边框，突出自动修复链路。
- 最终成功后，Report 节点使用绿色加粗样式。

模型对比表：

- 成功模型行使用绿色背景。
- 修复次数最少的模型行使用浅绿色提示。
- 覆盖率最高的单元格使用绿色文字。
- 质量评分最高的单元格使用绿色加粗。

插件结果：

- 通过 / 正常：绿色。
- 建议 / 警告：黄色。
- 风险 / 失败：红色。
- 未启用：灰色。

报告区：

- Markdown 正文直接渲染。
- 报告中的代码块用代码高亮展示。
- 错误摘要和日志放入折叠面板。
- 成功 / 失败结论使用大号彩色卡片。

### session_state 字段

Web UI 使用 `st.session_state` 保存页面状态，核心字段包括：

- `requirement`
- `selected_case`
- `result_state`
- `run_status`
- `enabled_plugins`
- `latest_report`
- `stdout`
- `stderr`
- `test_stdout`
- `test_stderr`
- `test_code`
- `test_success`
- `coverage_stdout`
- `coverage_percent`
- `quality_score`
- `quality_summary`

### 状态驱动展示层

页面展示不直接在 `webui.py` 中重复解析完整 state，而是先通过工具函数生成展示数据，再交给 Streamlit 渲染。

核心工具：

- `utils.summary_builder.build_run_summary(state)`：生成成功状态、修复次数、测试结果、覆盖率、质量评分、安全状态、启用插件、模型和报告路径等摘要。
- `utils.ui_state_builder.build_workflow_status(state)`：统一生成 Agent 工作流节点状态。
- `utils.ui_state_builder.build_plugin_display_data(state)`：统一生成插件展示数据，优先读取 `plugin_results`，兼容旧字段 `doc_result`、`security_result`、`refactor_result`、`ui_result`。
- `utils.ui_state_builder.build_report_display_data(state)`：统一生成报告文件名、报告内容、是否存在、成功状态和错误摘要。

工作流状态生成规则：

- 未运行时所有节点为 `Waiting`。
- 运行中通过 `_current_node` 标记当前节点，展示 `Running` 或 `Repairing`。
- 已完成运行通过 `requirement`、`product_result`、`code`、`test_code`、`stdout`、`error_log`、`plugin_results`、`quality_score`、`report_path` 等字段推断节点状态。
- 人工审批未通过时，Approval Node 显示 `Failed`，Runner 保持未执行状态，流程进入插件、质量评分和报告展示。

插件展示数据结构：

```text
plugin_name
status: success / warning / failed / disabled
summary
detail
```

这样做的好处：

- Web UI 只负责布局和展示，复杂状态判断集中在工具模块。
- CLI、报告生成和 Web UI 可以共享同一套摘要逻辑。
- 后续新增 Agent 节点或插件时，只需扩展状态构建函数，页面结构不需要大改。

### Agent 输出 Tabs

页面目标：

- 将复杂输出分层展示，避免一个页面堆满日志。
- 演示模式只保留关键摘要，开发模式保留完整信息。

Tabs：

- Product Agent
- Coder Agent
- Tester Agent
- Sentry Agent
- Plugins
- 模型对比
- Final State

展示规则：

- Coder Agent 的代码使用代码块展示。
- stdout 和 stderr 使用折叠面板展示。
- 演示模式只展示错误摘要。
- 开发模式展示完整 state、stdout 和 stderr。
- 演示模式隐藏完整 prompt、完整 state、过长 stderr 和冗长代码分析。
- 开发模式保留完整代码、完整插件结果和完整错误日志。

### 演示模式专项区域

页面目标：

- 让比赛现场观众快速看到“多 Agent 协作 + 自动修复 + 最终成功”。
- 不要求评委阅读完整日志，也能理解系统价值。

核心组件：

- 演示模式总览
- 自动修复高光时刻
- 比赛讲解提示
- 结果总结卡片

演示模式总览展示：

- 用户输入需求
- 当前执行 Agent
- 是否发生错误
- Sentry Agent 分析摘要
- 最终是否成功
- 修复次数
- 安全检查结果
- 报告是否生成

自动修复高光时刻展示：

```text
第一次运行失败
错误摘要
Sentry Agent 分析结果
Coder Agent 修复结果
再次运行成功
```

如果没有触发修复，显示：

```text
本次任务一次运行成功，未触发自动修复。
```

状态中文文案：

```text
Waiting   → 等待中
Running   → 运行中
Done      → 已完成
Failed    → 失败
Repairing → 修复中
```

结果总结卡片展示：

- 成功 / 失败
- 修复次数
- 生成代码文件
- 安全检查结果
- 文档生成状态
- 报告文件名

### 插件结果区

页面目标：

- 展示自定义 AI 模块的扩展能力。

字段：

- `plugin_results`
- `doc_result`
- `security_result`
- `refactor_result`
- `ui_result`

交互说明：

- 优先读取统一结构 `plugin_results`。
- 旧字段继续保留，用于兼容历史报告和历史运行记录。
- 插件启用时展示对应结果。
- 插件关闭时展示“该插件未启用”。

### 报告区域

页面目标：

- 展示最新 Markdown 报告，方便比赛现场复盘。

核心组件：

- 最新报告文件名
- 报告内容预览
- 下载 Markdown 报告按钮
- 暂无报告空状态

交互说明：

- 每次运行后自动生成 `reports/report_时间戳.md`。
- 同时更新 `reports/latest_report.md`。
- 如果没有报告，显示“暂无报告”。

## Figma 交付建议

建议在 Figma 中至少完成：

- 首页
- Agent 工作流页
- 运行日志页
- 报告页
- Agent 节点组件
- 日志面板组件
- 成功/失败/修复中状态变体

## Figma 布局关键词

在 Figma 中可以按以下关键词搜索参考：

```text
AI Dashboard
Developer Console
Agent Workflow
Automation Dashboard
Pipeline Dashboard
DevOps Dashboard
Workflow Monitoring
```

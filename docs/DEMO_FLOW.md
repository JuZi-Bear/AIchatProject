# 比赛现场演示流程

推荐演示目标：突出“多 Agent 协作 + 自动测试 + 自动修复 + 插件扩展 + 质量评分 + 报告生成”。

## 第一部分：打开 Web UI

1. 打开 PowerShell。
2. 进入项目目录：

```powershell
cd D:\AIchatProject
```

3. 启动 Web UI：

```powershell
python -m streamlit run webui.py
```

4. 浏览器访问：

```text
http://localhost:8501
```

讲解重点：这是一个 AI 自动开发控制台，左侧控制运行参数，右侧展示工作流时间轴、最终结果、快速导航和报告。

## 第二部分：选择“翻车修复案例”

在左侧“演示案例选择”中选择：

```text
翻车修复案例
```

讲解重点：该案例有意选择容易出错的需求，适合展示系统不是只生成代码，而是能发现问题并自动修复。

## 第三部分：选择模型

在“模型选择”区域选择：

```text
DeepSeek
```

如果现场配置了 Qwen 或 GLM，也可以说明系统支持多模型切换和对比。

讲解重点：系统通过 OpenAI SDK 兼容接口接入不同国产大模型，模型信息会写入报告和历史记录。

## 第四部分：启用插件

确认左侧插件全部启用：

- Doc Agent
- Security Agent
- Refactor Agent
- UI Agent

讲解重点：插件系统让主流程之外的 AI 能力可插拔，例如文档生成、安全检查、重构建议和 UI 建议。

## 第五部分：勾选人工审批

勾选：

```text
我确认允许运行 AI 生成的代码
```

讲解重点：系统在运行 AI 代码前加入 Human-in-the-loop 审批，避免危险代码自动执行。

## 第六部分：点击运行

点击：

```text
开始运行
```

讲解重点：点击后 LangGraph 会按状态机推进，每个节点只负责一个清晰任务。

## 第七部分：展示工作流进度

观察右侧 AI 工作流时间轴：

```text
Requirement → Product Agent → Coder Agent → Tester Agent → Approval → Runner → Sentry Agent → Plugins → Quality → Report
```

讲解重点：

- Product Agent 拆解需求。
- Coder Agent 生成代码。
- Tester Agent 生成 pytest 测试。
- Approval Node 进行人工审批。
- Runner 执行代码。
- Sentry Agent 处理失败。
- Plugins 执行扩展能力。
- Quality Node 量化质量。
- Report Node 生成 Markdown 报告。
- 时间轴会显示当前节点、中文状态、摘要、整体进度和自动修复高光。

## 第八部分：展示 pytest 测试失败

如果案例触发失败，打开“结果索引”中的“pytest 测试”或 Agent 输出里的“Tester”Tab。

展示内容：

- 自动生成的 pytest 测试代码。
- `test_success=False`。
- pytest stdout / stderr 摘要。

讲解重点：系统不只看程序是否能启动，还会用需求驱动测试判断代码是否正确。

## 第九部分：展示 Sentry 自动分析

查看 AI 工作流时间轴下方的“自动修复高光时刻”，或打开“Sentry”Tab。

展示内容：

- 第一次运行失败。
- 错误摘要。
- Sentry Agent 分析结果。

讲解重点：Sentry Agent 会综合 stderr、pytest 输出、测试代码和原始代码，判断是逻辑问题、边界条件问题还是运行环境问题。

## 第十部分：展示 Coder 自动修复

打开“结果索引”的“自动修复”入口，或打开“Coder”Tab。

展示内容：

- 修复后的代码。
- 工作流中的 Coder / Sentry / Runner 节点高亮。
- 修复次数 `retry_count`。

讲解重点：Coder Agent 修复的是业务代码，不是通过修改测试来规避失败。

## 第十一部分：展示测试通过

回到“结果索引”的“pytest 测试”入口。

展示内容：

- `test_success=True`。
- coverage 覆盖率。
- Runner stdout。

讲解重点：最终成功条件是 Runner 成功并且 pytest 通过。

## 第十二部分：展示质量评分和报告

展示“最终结果总览”和“结果索引”的“运行报告”入口。

展示内容：

- `quality_score`
- `coverage_percent`
- 安全检查结果
- 自动修复次数
- Markdown 报告路径
- 报告预览和下载入口

讲解重点：系统最终产出不只是代码，还包括测试结果、质量评分、插件分析和可复盘报告。

## 推荐收尾话术

```text
这个项目把 AI 写代码从一次性生成，升级成了可观察、可测试、可修复、可扩展的自动开发流水线。
它既能展示国产大模型能力，也能体现工程化、安全审批和比赛现场可演示性。
```

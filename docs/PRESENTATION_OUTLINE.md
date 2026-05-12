# 答辩演示大纲

## 1. 项目背景

AI 编程助手已经可以生成代码，但在真实开发场景中，单次生成往往不够稳定。开发者通常还需要补充需求拆解、代码检查、运行验证、错误分析和修复。

本项目尝试构建一个从自然语言需求到代码生成、测试运行、错误分析、自动修复的多智能体开发流水线。

## 2. 痛点分析

- 用户需求往往是自然语言描述，缺少结构化开发任务。
- 单个大模型直接写代码，容易漏掉边界情况。
- 代码生成后如果不运行，很难判断是否真的可用。
- 运行失败后，错误日志需要重新理解和定位。
- 传统演示只展示“生成代码”，不展示“失败后如何修复”。

## 3. 解决方案

系统将开发过程拆成多个 Agent 协作：

```text
用户需求 → Product Agent → Coder Agent → Tester Agent → Code Runner → Sentry Agent → 自动修复
```

每个 Agent 只负责一个相对清晰的任务，降低单模型一次性完成所有工作的压力。

## 4. 系统架构

核心模块：

- `agents.py`：封装 Product、Coder、Tester、Sentry 四类 Agent。
- `utils/code_runner.py`：保存并运行生成代码，捕获 stdout、stderr、returncode。
- `graph.py`：使用 LangGraph 管理状态和节点流转。
- `graph_demo.py`：命令行版 LangGraph 演示入口。
- `webui.py`：Streamlit Web UI 演示入口。
- `docs/`：PRD、任务清单、演示脚本、UI 规格和答辩材料。

## 5. 多 Agent 分工

### Product Agent

负责将用户自然语言需求拆解成：

- 功能列表
- 技术需求
- 开发步骤

### Coder Agent

负责根据产品方案生成 Python 代码，或根据错误日志修复代码。

### Tester Agent

负责对生成代码进行静态检查，关注：

- 语法问题
- 逻辑问题
- 入口函数或必要调用

### Sentry Agent

负责分析 stderr 错误日志，输出：

- 错误摘要
- 错误原因
- 修复建议

## 6. LangGraph 工作流

LangGraph 用于管理状态机和循环修复逻辑。

当前状态字段包括：

- `requirement`
- `product_result`
- `code`
- `tester_result`
- `stdout`
- `error_log`
- `sentry_result`
- `retry_count`
- `success`

工作流：

```text
START
↓
product_node
↓
coder_node
↓
tester_node
↓
runner_node
↓
条件判断：
  success == True → END
  retry_count >= 3 → END
  否则 → sentry_node → coder_node
```

## 7. 自动测试与自愈修复

系统会将 Coder Agent 生成的代码保存到：

```text
output/generated_code.py
```

然后使用 subprocess 运行代码，捕获：

- stdout
- stderr
- returncode

如果运行失败，系统会把 stderr 交给 Sentry Agent 分析，再由 Coder Agent 根据错误日志修复代码，最多自动修复 3 次。

## 8. CLI / Web UI 演示流程

### CLI 演示

```powershell
python graph_demo.py
```

可选择：

- 简单成功案例
- 翻车修复案例
- 综合案例
- 自定义输入

### Web UI 演示

```powershell
streamlit run webui.py
```

Web UI 展示：

- 需求输入
- Agent 状态卡片
- Agent Workflow 流程图
- stdout / error_log
- retry_count / success
- Markdown 报告

## 9. 创新点

- 使用国产大模型 DeepSeek 构建自动开发流水线。
- 多 Agent 分工而不是单次提示词生成。
- 自动运行生成代码，验证真实可执行性。
- 引入错误日志反馈闭环，实现自动修复。
- 使用 LangGraph 把流程升级为可维护状态机。
- CLI 与 Web UI 双演示入口，适合比赛现场展示。

## 10. 技术难点

- 如何让模型输出尽量稳定的纯 Python 代码。
- 如何处理代码块 Markdown 包裹问题。
- 如何捕获并反馈运行错误。
- 如何让 `input()` 这类交互代码在自动运行环境中可修复。
- 如何用 LangGraph 管理循环修复并限制最大次数。
- 如何在 Web UI 中展示长文本、代码和日志。

## 11. 未来扩展

- 替换 `main.py` 为 LangGraph 主流程。
- 增加真正的 pytest 测试用例生成与运行。
- 支持多文件项目生成。
- 支持前端代码生成和预览。
- 接入 Figma 设计稿，实现从需求到 UI 的更完整闭环。
- 增加报告归档和历史记录管理。
- 支持更多国产模型和本地模型。

# agents

## 目录作用

`agents/` 是 Agent 模块拆分的预留目录和说明入口。当前核心 Agent 实现仍主要位于顶层 `agents.py`，并由 `core/workflow.py` 编排。

## 核心文件

当前目录暂无核心源码文件。相关实现请先查看：

- `agents.py`：Product、Coder、Tester、Sentry 等 Agent 逻辑。
- `core/workflow.py`：LangGraph 工作流编排。
- `core/state.py`：工作流状态结构。

## 不能随便修改

- 不要在未同步工作流的情况下移动或拆分顶层 `agents.py`。
- 不要改变 Agent 输出字段而不更新 `run_summary` 和 `ui_view_model`。
- 不要让 v2 前端或 Java 直接依赖 Agent 内部结构。

## 轨道归属

shared-core。

## 当前开发状态

stable。

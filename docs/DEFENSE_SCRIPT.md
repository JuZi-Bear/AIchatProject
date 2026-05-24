# v2-only 比赛答辩讲稿

## 项目一句话介绍

这是一个 AI 多 Agent 工作流平台，可以从自然语言需求出发，完成 Agent 协作、受控文件操作、实时事件推送、审计记录和工作流回放。

## 项目解决的问题

传统 AI 代码生成演示通常只能展示“输入和输出”，很难解释中间发生了什么。本项目把执行过程事件化、持久化和可视化，让评委能看到每一步 Agent 如何参与、CodeAgent 如何受控修改文件、失败和阻断如何被记录。

## 为什么使用多 Agent

不同 Agent 负责不同职责：Product 负责需求拆解，Coder 负责代码，Tester 负责测试，Sentry 负责错误分析，Quality 负责评分，Report 负责总结。职责拆分后，流程更容易观察、调试和扩展。

## 为什么使用 LangGraph

LangGraph 适合表达有状态、多节点、可重试的 Agent 工作流。它让工作流从一次性函数调用变成可管理的执行图，为后续模板、回放和可视化编排打基础。

## 为什么使用 Vue + Java + MySQL

Vue 负责可视化工作台和编辑器，Java 负责平台 API、事件记录、SSE 推送和配置管理，MySQL 负责持久化任务、事件、模板和报告索引。Python 专注 Agent Engine，平台能力不直接侵入 LangGraph 核心。

## 为什么设计 CodeAgent

CodeAgent 是简化版代码执行模块，只做受控的 `read_file`、`write_file`、`list_files`。它有路径白名单、阻断路径、读取长度限制和 JSONL 审计日志，适合展示“可以真实改文件，但有安全边界”。

## 自动修复流程怎么工作

运行失败后，Runner 和 Tester 的输出会进入 Sentry 分析，再由 Coder 根据错误摘要修复。修复过程会写入 workflow events，Java 保存为 RunEvent，Vue 可以实时展示并回放。

## 技术栈分工

- Vue3 + TypeScript：Dashboard、RunConsole、Workflow Editor、Replay。
- Java Spring Boot：Gateway、RunEvent、SSE、MySQL 持久化。
- Python FastAPI：Agent Engine API。
- LangGraph：多 Agent 工作流。
- MySQL：任务、事件、模板、报告索引。
- C++ Runner：可选安全执行器雏形。
- Docker Compose：v2 多服务部署。

## 当前演示闭环

拖拽工作流节点 -> 执行 CodeAgent -> 文件生成或阻断 -> JSONL 审计 -> Java RunEvent -> SSE 实时展示 -> Replay 回放。

## 后续发展方向

后续可以增强 Agent 注册中心、模板版本管理、任务队列、权限、团队协作和更强的沙箱执行。但当前版本优先保证单人比赛演示闭环稳定。

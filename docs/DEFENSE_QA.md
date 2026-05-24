# v2-only Defense Q&A

## 为什么拆成 Vue、Java、Python、MySQL？

Python 适合承载 Agent Engine 和 LangGraph，Java 适合平台记录、配置、SSE 和后续企业服务，Vue 适合可视化工作台，MySQL 负责持久化。分层后，AI 工作流和平台能力不会互相绑死。

## 为什么要做 RunEvent 和 Replay？

AI 工作流如果只展示最终输出，很难说明中间过程。RunEvent 把关键节点事件保存下来，Replay 让评委看到任务从创建、执行、文件操作、安全阻断到报告生成的完整轨迹。

## CodeAgent 如何保证安全？

它不是完整自动编码助手，只支持受控的 `read_file`、`write_file`、`list_files`。路径白名单、阻断路径、读取长度限制和 JSONL 审计日志共同构成安全边界。

## 为什么保留 Python Direct？

Python Direct 是开发调试模式，可以快速定位 FastAPI Agent Engine 问题。比赛演示默认使用 Java Gateway。

## 为什么不马上做用户和权限？

当前重点是单人比赛演示闭环。用户、权限、团队协作会显著增加复杂度，应在 v2 主链路稳定后再做。

# v2-only 三分钟演示脚本

## 0:00 - 0:20 项目介绍

这是一个 AI 多 Agent 工作流平台。它不仅能运行 Agent 工作流，还能把执行过程记录成事件，通过 Java SSE 推送到 Vue，并在 Replay 中回放。

## 0:20 - 0:45 架构说明

当前主链路是 Vue -> Java Spring Boot -> FastAPI Python Agent Engine -> MySQL。Vue 负责可视化，Java 负责平台记录和实时事件，Python 负责 LangGraph Agent Engine，MySQL 保存任务、事件、模板和报告索引。

## 0:45 - 1:20 Workflow Editor

打开 Workflow Editor。这里是类似 Figma 的无限画布，可以拖入 Product、Coder、Tester、CodeAgent、If、And、Or 等节点。点击节点后才出现右侧属性浮层，避免占用画布空间。

## 1:20 - 1:55 CodeAgent 演示

拖入 CodeAgent 后执行文件操作。它只支持受控的 `read_file`、`write_file`、`list_files`，并且有路径白名单、阻断路径和读取长度限制。违规路径会被阻断并写入审计日志。

## 1:55 - 2:25 实时事件与审计

任务执行过程中，Python 生成 workflow events，Java 保存 RunEvent 并通过 SSE 推送到 Vue。页面可以看到任务创建、Python 请求、CodeAgent 操作、阻断或成功、报告索引等事件。

## 2:25 - 2:50 Replay 回放

打开 Replay 页面，可以按时间顺序回放事件。这样评委不仅看到最后结果，也能看到每一步是如何发生的。

## 2:50 - 3:00 总结

这个项目的重点是把 AI 工作流从黑盒输出升级为可观察、可审计、可回放的平台闭环。下一步可以继续扩展任务队列、权限和团队协作。

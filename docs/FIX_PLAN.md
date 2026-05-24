# v2-only Fix Plan

| 优先级 | 问题 | 所属模块 | 修复建议 | 是否需要用户确认 |
| --- | --- | --- | --- | --- |
| P1 | Docker 或本地服务无法启动 | docker/runtime | 优先修复启动脚本、端口、环境变量 | 否 |
| P1 | Vue 无法通过 Java 调用 Python | frontend/backend | 检查 Gateway、CORS、API base URL | 否 |
| P1 | CodeAgent 安全策略失效 | Python/Vue | 修复路径校验、审计日志、阻断提示 | 是 |
| P2 | 文档命令不一致 | docs | 直接同步为 v2-only 命令 | 否 |
| P2 | Replay 展示不完整 | frontend/backend | 检查 RunEvent 保存和回放 API | 否 |
| P3 | 样式细节 | frontend | 按 Figma 风格逐步优化 | 否 |

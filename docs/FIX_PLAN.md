# 修复计划

本文记录从测试清单、测试日志、代码健康检查和冗余检查中整理出的后续修复计划。本阶段不直接执行高风险修复。

| 优先级 | 问题 | 所属轨道 | 影响范围 | 修复建议 | 是否需要用户确认 |
|---|---|---|---|---|---|
| P2 | 文档体系存在启动、Docker、风险、目录结构重复说明 | docs | README、操作指南、用户手册、Docker 指南、风险文档 | 已新增 `REDUNDANCY_REVIEW.md` 并标记主文档入口 | 否 |
| P2 | `docs/ARCHITECTURE.md` 与 `DUAL_TRACK_ARCHITECTURE.md` 重叠 | docs | 架构说明 | 已在 `ARCHITECTURE.md` 顶部标记历史文档并链接双轨架构主文档 | 否 |
| P2 | `docs/DELIVERY_STRUCTURE.md` 与 `PROJECT_DIRECTORY_GUIDE.md` 目录说明重叠 | docs | 目录说明、交付说明 | 已标记为交付历史文档并指向 `PROJECT_DIRECTORY_GUIDE.md` | 否 |
| P2 | `docs/RISK_AND_SOLUTION.md` 与 `RISK_AND_STABILITY.md` 风险说明重叠 | docs | 风险说明 | 已标记为早期风险文档并指向 `RISK_AND_STABILITY.md` | 否 |
| P2 | `docs/USER_MANUAL.md` 与 `docs/OPERATION_GUIDE.md` 启动说明重复 | docs | 用户启动说明、维护启动说明 | 已明确 `USER_MANUAL.md` 面向演示用户，`OPERATION_GUIDE.md` 面向维护者 | 否 |
| P3 | `docs/PROMPTS.md` 为空文档 | docs | 提示词归档 | 由用户确认：保留为提示词归档入口，或标记为待归档空文档 | 是 |
| P3 | `tests/test_generated_code.py` 可能是生成测试文件 | shared-core | 测试文件、Git 跟踪策略 | 由用户确认是否继续跟踪；如不跟踪，只做 Git 层移出，不删除本地文件 | 是 |
| P3 | C++ Runner 当前不是完整安全沙箱 | experimental | Runner 安全能力说明 | 保持默认 Python Runner，继续在文档中标注 C++ Runner 为实验能力 | 否 |
| P3 | Docker Compose 依赖本地端口 `3306`、`8001`、`8088`、`5174`、`8501` | docker | 本地/现场启动 | 在 `TEST_RESULT_LOG.md` 中记录端口占用情况；必要时后续补充端口排查脚本 | 否 |

## 暂无测试失败项

`docs/TEST_RESULT_LOG.md` 当前尚未记录实际失败项，因此本计划没有 P0 / P1 运行故障修复项。完成手动启动测试后，应把失败项按优先级补入上表。

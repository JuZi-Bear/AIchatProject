# 测试问题归档与分级

本文基于 `docs/FINAL_CHECKLIST.md`、`docs/TEST_RESULT_LOG.md`、`docs/CODE_HEALTH_REVIEW.md` 进行问题归档和优先级判断。本阶段只整理问题，不直接删除核心代码，不大改 UI/API/数据库/LangGraph/Agent/插件/Docker Compose 服务结构。

## 问题分级标准

### P0：阻塞级

- v1.0 无法启动。
- v2.0 核心服务无法启动。
- Web UI 白屏。
- API 无法访问。
- Docker 完全无法启动。
- 演示主流程无法跑通。

### P1：高优先级

- 自动修复流程异常。
- 报告无法生成。
- Vue 无法调用 Java / Python API。
- Java 无法连接 MySQL。
- 模型配置错误。
- 插件配置失效。

### P2：中优先级

- 页面布局问题。
- 文档命令不一致。
- 历史记录显示不完整。
- 报告展示不美观。
- 部分状态提示不清晰。

### P3：低优先级

- 文案优化。
- 样式细节。
- 非核心页面的小问题。
- 后续平台化优化建议。

## 当前测试结果状态

`docs/TEST_RESULT_LOG.md` 目前所有条目仍为“未测试”，尚未记录失败项、错误日志或修复结果。因此当前没有已确认的 P0 / P1 启动阻塞问题。

等待测试结果补充后，再将失败项同步到本文和 `docs/FIX_PLAN.md`。

## 已归档问题

| 优先级 | 问题 | 来源 | 所属轨道 | 当前判断 |
| --- | --- | --- | --- | --- |
| P2 | 文档体系仍有重复说明，尤其是启动、Docker、风险和目录结构说明 | `CODE_HEALTH_REVIEW.md` | docs | 可做低风险文档合并和归档标记 |
| P2 | 架构说明分散在多个文档 | `CODE_HEALTH_REVIEW.md` | docs | 建议以 `V2_ARCHITECTURE_PLAN.md` 为主文档，其余文档只做索引或补充 |
| P2 | `docs/DELIVERY_STRUCTURE.md` 与 `PROJECT_DIRECTORY_GUIDE.md` 目录说明重叠 | `CODE_HEALTH_REVIEW.md` | docs | 建议保留交付历史口径，减少重复入口 |
| P2 | `docs/RISK_AND_SOLUTION.md` 与 `RISK_AND_STABILITY.md` 风险说明重叠 | `CODE_HEALTH_REVIEW.md` | docs | 建议后续合并风险口径 |
| P2 | `docs/USER_MANUAL.md` 与 `docs/OPERATION_GUIDE.md` 启动说明重复 | `CODE_HEALTH_REVIEW.md` | docs | 建议明确用户手册和维护手册边界 |
| P3 | `docs/PROMPTS.md` 是 0 字节空文档 | `CODE_HEALTH_REVIEW.md` | docs | 是否保留为提示词归档入口需要确认 |
| P3 | `tests/test_generated_code.py` 看起来像生成测试文件，但当前已存在于项目中 | `CODE_HEALTH_REVIEW.md` | shared-core | 是否继续跟踪需要用户确认 |
| P3 | C++ Runner 当前不是完整安全沙箱 | `CODE_HEALTH_REVIEW.md` | experimental | 已在文档中标注为实验能力，后续增强 |
| P3 | Docker Compose 依赖多个本地端口，比赛现场需要提前检查 | `CODE_HEALTH_REVIEW.md` | docker | 建议在测试记录中记录端口占用情况 |

## REDUNDANCY_REVIEW.md 状态

当前未发现 `docs/REDUNDANCY_REVIEW.md`。因此本轮没有来自该文档的冗余建议可同步。

如果后续新增该文档，应按以下规则同步：

- 文档重复类问题标记为 P2。
- 运行产物类问题标记为 P3。
- 涉及核心代码删除的问题标记为“需要用户确认”。
- 不直接删除代码。

## 当前 P0 / P1 状态

- P0：暂无已确认问题。
- P1：暂无已确认问题。

实际启动测试完成后，如果 `TEST_RESULT_LOG.md` 出现“失败”或“待修”，应优先将 v1 启动、FastAPI、Java/MySQL、Vue API、Docker 完整启动问题归入 P0 / P1。

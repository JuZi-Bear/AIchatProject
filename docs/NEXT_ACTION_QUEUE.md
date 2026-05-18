# 下一步行动队列

本文记录双轨并行架构收敛阶段的后续可执行任务。执行前应先查看 `docs/ISSUE_TRIAGE.md` 和 `docs/FIX_PLAN.md`。

## 立即修复

只放 P0 / P1。

当前暂无已确认 P0 / P1 问题。等待 `docs/TEST_RESULT_LOG.md` 补充真实启动测试结果。

## 本周优化

只放 P2。

- [x] 梳理重复启动说明：以 `README.md` 为入口，详细启动指向 `STARTUP_ORDER.md`、`OPERATION_GUIDE.md` 和 `DOCKER_COMPOSE_GUIDE.md`。
- [x] 标记 `docs/ARCHITECTURE.md` 为历史架构文档，并链接 `DUAL_TRACK_ARCHITECTURE.md`。
- [x] 标记 `docs/DELIVERY_STRUCTURE.md` 为交付历史文档，并链接 `PROJECT_DIRECTORY_GUIDE.md`。
- [x] 标记 `docs/RISK_AND_SOLUTION.md` 为历史风险文档，并链接 `RISK_AND_STABILITY.md`。
- [x] 明确 `docs/USER_MANUAL.md` 与 `docs/OPERATION_GUIDE.md` 的读者边界。

## 后续规划

只放 P3 和平台化建议。

- 继续保留 C++ Runner 为实验能力，后续再规划更强隔离、超时和资源限制。
- 在测试记录中补充端口占用、Docker 首次启动耗时、MySQL 连接状态等现场风险。
- 持续减少 README 体量，把详细内容导向 `docs/DOCUMENT_INDEX.md`。

## 需要用户确认

- `docs/PROMPTS.md` 是否保留为提示词归档入口。
- `tests/test_generated_code.py` 是否继续由 Git 跟踪，还是作为生成产物从跟踪中移出。
- 是否允许后续进一步压缩历史文档正文，仅保留跳转和必要历史信息。
- 如果真实测试发现 P0 / P1，是否优先暂停文档整理，转入修复模式。

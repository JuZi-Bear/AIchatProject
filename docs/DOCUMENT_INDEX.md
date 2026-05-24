# 文档导航

本文是 `docs/` 的总入口。当前项目已收敛为 v2-only 平台化演示版，默认文档以 Vue -> Java -> FastAPI -> MySQL 主链路为准。

## 核心架构

| 文档 | 状态 | 说明 |
| --- | --- | --- |
| `V2_ONLY_RUNTIME_SIMPLIFICATION.md` | 主文档 | v2-only 主链路、保留模块和启动口径 |
| `V2_ARCHITECTURE_PLAN.md` | 主文档 | v2 平台架构和阶段进展 |
| `PROJECT_DIRECTORY_GUIDE.md` | 主文档 | 项目目录树和目录归属 |
| `FRAMEWORK_EXTENSION_PLAN.md` | 主文档 | 技术框架扩展总规划 |
| `FRAMEWORK_EXTENSION_BOUNDARY.md` | 主文档 | 框架扩展边界 |
| `FRAMEWORK_EXTENSION_ARCHITECTURE.md` | 主文档 | 未来框架扩展示意图 |
| `ARCHITECTURE.md` | 历史文档 | 早期架构简图，仅作背景参考 |
| `DELIVERY_STRUCTURE.md` | 历史文档 | 早期交付目录说明，仅作背景参考 |

## API 与数据

| 文档 | 状态 | 说明 |
| --- | --- | --- |
| `API_CONTRACT.md` | 主文档 | Python FastAPI、Java Gateway、平台接口和前端调用示例 |
| `MYSQL_SETUP.md` | 主文档 | MySQL 本地和 Docker 配置 |
| `CPP_RUNNER_SANDBOX.md` | 主文档 | C++ Runner Sandbox 说明 |
| `PLUGIN_GUIDE.md` | 主文档 | 插件开发指南 |

## 启动、运维与验收

| 文档 | 状态 | 说明 |
| --- | --- | --- |
| `DOCKER_COMPOSE_GUIDE.md` | 主文档 | v2 Docker Compose 启动指南 |
| `STARTUP_ORDER.md` | 主文档 | v2 本地开发和 Docker 推荐启动顺序 |
| `OPERATION_GUIDE.md` | 主文档 | v2 运维和演示操作手册 |
| `LOCAL_V2_STARTUP.md` | 主文档 | v2 本地一键联调说明 |
| `FINAL_CHECKLIST.md` | 主文档 | v2 提交前检查 |
| `TEST_RESULT_LOG.md` | 主文档 | v2 验收结果记录 |
| `STABILITY_TEST.md` | 历史文档 | 早期稳定性测试记录，仅作背景参考 |
| `BUG_FIX_LOG.md` | 历史文档 | 早期修复记录，仅作背景参考 |

## Vue / Figma / UI

| 文档 | 状态 | 说明 |
| --- | --- | --- |
| `FIGMA_UI_WORKFLOW.md` | 主文档 | Figma-first 前端 UI 设计源和 Vue 同步流程 |
| `UI_SPEC.md` | 主文档 | UI 设计规格和展示契约 |
| `CODEX_UI_WORKFLOW.md` | 历史文档 | 早期 UI 优化过程记录 |

## Codex 协作

| 文档 | 状态 | 说明 |
| --- | --- | --- |
| `CODEX_PROJECT_CONTEXT.md` | 主文档 | Codex 进入项目后的上下文摘要 |
| `CODEX_COLLAB_RULES.md` | 主文档 | Codex 修改规则和检查清单 |
| `MODULE_BOUNDARY.md` | 主文档 | 模块边界和禁止跨层破坏说明 |
| `SAFE_CHANGE_CHECKLIST.md` | 主文档 | 每次修改前后的安全检查清单 |
| `MAINTENANCE_GUIDE.md` | 主文档 | v2-only 项目维护和测试指南 |
| `CODE_HEALTH_REVIEW.md` | 主文档 | 代码健康检查、风险项和建议清理项 |
| `ISSUE_TRIAGE.md` | 主文档 | 测试问题分级和归档 |
| `FIX_PLAN.md` | 主文档 | 后续修复计划 |
| `NEXT_ACTION_QUEUE.md` | 主文档 | 下一步行动队列 |
| `REDUNDANCY_REVIEW.md` | 历史文档 | 文档冗余评审记录 |

## 演示与答辩

| 文档 | 状态 | 说明 |
| --- | --- | --- |
| `V2_3_MIN_DEMO_SCRIPT.md` | 主文档 | v2 平台化三分钟现场演示脚本 |
| `V2_DEMO_RELEASE_NOTES.md` | 主文档 | v2 演示版发布说明和验收结果 |
| `DEMO_FLOW.md` | 历史文档 | 早期演示流程，仅作背景参考 |
| `DEMO_SCRIPT.md` | 历史文档 | 早期演示脚本，仅作背景参考 |
| `DEFENSE_SCRIPT.md` | 主文档 | 答辩讲稿 |
| `DEFENSE_QA.md` | 主文档 | 答辩问答 |
| `PRESENTATION_OUTLINE.md` | 主文档 | 答辩 PPT 大纲 |
| `SCORE_POINTS.md` | 主文档 | 评分点包装 |
| `INNOVATION_POINTS.md` | 主文档 | 创新点说明 |
| `VIDEO_CODING_GUIDE.md` | 主文档 | 录制顺序、讲解内容、现场修改边界和演示命令 |

## 规划与路线图

| 文档 | 状态 | 说明 |
| --- | --- | --- |
| `TASKS.md` | 主文档 | v2-only 开发任务清单 |
| `FRAMEWORK_EXTENSION_CANDIDATES.md` | 主文档 | 技术扩展候选清单和优先级评估 |
| `RECOMMENDED_EXTENSION_ROADMAP.md` | 主文档 | 推荐扩展路线 |
| `PRO.md` | 历史文档 | 早期 PRD，仅作背景参考 |
| `PROMPTS.md` | 待整理 | 提示词归档入口 |

## 当前重复项处理建议

- 启动说明以 `README.md` 为入口，详细启动以 `OPERATION_GUIDE.md` 和 `DOCKER_COMPOSE_GUIDE.md` 为准。
- API 说明以 `API_CONTRACT.md` 为准。
- 技术栈说明以 `TECH_STACK.md` 为准。
- 目录结构以 `PROJECT_DIRECTORY_GUIDE.md` 为准。
- 历史文档不作为当前启动、验收或开发入口。

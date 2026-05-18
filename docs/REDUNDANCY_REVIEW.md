# 文档冗余评审

本文记录“双轨并行架构收敛整理阶段”的 P2 文档去重评审结果。本阶段不删除文档，只标记主文档、历史文档和建议合并方向。

## 评审原则

- 不删除历史文档。
- 不改核心业务逻辑。
- README 只保留入口和最常用命令。
- 详细说明集中到主文档。
- 旧文档顶部增加提示，指向当前主文档。

## 主文档口径

| 主题 | 当前主文档 | 说明 |
| --- | --- | --- |
| 双轨架构 | `DUAL_TRACK_ARCHITECTURE.md` | v1/v2 职责、边界和收敛方向 |
| 目录结构 | `PROJECT_DIRECTORY_GUIDE.md` | 完整目录树和目录归属 |
| 文档导航 | `DOCUMENT_INDEX.md` | docs 总入口 |
| 启动顺序 | `STARTUP_ORDER.md` | v1、本地 v2、Docker v2 启动顺序 |
| Docker | `DOCKER_COMPOSE_GUIDE.md` | 多服务 Compose 说明 |
| 风险与兜底 | `RISK_AND_STABILITY.md` | 双轨稳定性和现场兜底 |
| API | `API_CONTRACT.md` | Python FastAPI 和 Java Gateway 契约 |
| 维护与安全变更 | `MAINTENANCE_GUIDE.md`、`SAFE_CHANGE_CHECKLIST.md` | 后续修改规则 |

## 冗余文档评审

| 文档 | 当前状态 | 冗余类型 | 处理方式 |
| --- | --- | --- | --- |
| `ARCHITECTURE.md` | 历史架构简图 | 与双轨架构主文档重叠 | 顶部标记历史文档，指向 `DUAL_TRACK_ARCHITECTURE.md` |
| `DELIVERY_STRUCTURE.md` | 交付目录历史说明 | 与目录指南重叠 | 顶部标记交付历史文档，指向 `PROJECT_DIRECTORY_GUIDE.md` |
| `RISK_AND_SOLUTION.md` | 早期风险说明 | 与稳定性文档重叠 | 顶部标记早期风险文档，指向 `RISK_AND_STABILITY.md` |
| `USER_MANUAL.md` | 用户手册 | 与操作指南有启动说明重复 | 标记面向演示用户和跨设备部署，不作为维护主文档 |
| `OPERATION_GUIDE.md` | 操作指南 | 与用户手册有启动说明重复 | 标记面向维护者和运维排障，详细 Docker/服务说明保留 |
| `PROMPTS.md` | 空文档 | 待归档 | 需要用户确认是否作为提示词归档入口 |

## 已完成的低风险整理

- 已给 `ARCHITECTURE.md` 增加历史提示。
- 已给 `DELIVERY_STRUCTURE.md` 增加交付历史提示。
- 已给 `RISK_AND_SOLUTION.md` 增加早期风险文档提示。
- 已给 `USER_MANUAL.md` 增加读者定位提示。
- 已给 `OPERATION_GUIDE.md` 增加维护者定位提示。

## 后续建议

- 如果用户确认，可以把 `PROMPTS.md` 改为提示词归档入口。
- 如果用户确认，可以把 `ARCHITECTURE.md` 精简为只保留跳转和历史图示。
- 不建议删除历史文档，避免比赛材料或答辩引用断链。

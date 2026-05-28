# v2-only 测试结果记录

本文记录 v2-only 平台演示链路的验收结果。

| 测试项 | 命令/页面 | 结果 | 问题 | 是否修复 |
|---|---|---|---|---|
| Python API | `http://127.0.0.1:8001/health` | 通过 | 2026-05-24 返回 `python-agent-engine` | 不适用 |
| Java Gateway | `http://127.0.0.1:8088/api/health` | 通过 | 2026-05-24 返回 `java-platform-service` | 不适用 |
| Java -> Python Proxy | `http://127.0.0.1:8088/api/agent/health` | 通过 | 2026-05-24 返回 Python health | 不适用 |
| Vue Dashboard | `http://127.0.0.1:5174/` | 通过 | HTTP 200 | 不适用 |
| Vue Agents | `http://127.0.0.1:5174/agents` | 通过 | HTTP 200 | 不适用 |
| Workflow Templates | `http://127.0.0.1:5174/workflows/templates` | 通过 | HTTP 200 | 不适用 |
| Workflow Editor | `http://127.0.0.1:5174/workflows/editor` | 通过 | HTTP 200 | 不适用 |
| History | `http://127.0.0.1:5174/history` | 通过 | HTTP 200 | 不适用 |
| Reports | `http://127.0.0.1:5174/reports` | 通过 | HTTP 200 | 不适用 |
| CodeAgent smoke | `.\scripts\smoke_codeagent.ps1 -ApiMode java -CheckBlockedPath` | 通过 | 文件写入、阻断路径、SSE、RunEvent、Replay、审计日志均通过 | 不适用 |
| Workflow Template smoke | `.\scripts\smoke_workflow_template.ps1` | 通过 | 保存、版本递增、实例化、回放、删除均通过 | 不适用 |
| Final acceptance | `.\scripts\final_v2_acceptance.ps1` | 通过 | 脚本退出码 0，完成本地启动、API、smoke、演示数据和页面检查 | 不适用 |

## 2026-05-21 v2-demo-rc1 验收记录

| 测试项 | 命令/页面 | 结果 | 问题 | 是否修复 |
|---|---|---|---|---|
| v2 最终验收脚本 | `.\scripts\final_v2_acceptance.ps1` | 通过 | 脚本退出码 0，完成本地启动、API 检查、smoke、演示数据和页面检查 | 不适用 |
| Python API | `http://127.0.0.1:8001/health` | 通过 | 返回 `python-agent-engine / v2-api-preview` | 不适用 |
| Java Gateway | `http://127.0.0.1:8088/api/health` | 通过 | 返回 `java-platform-service / v2-java-preview` | 不适用 |
| MySQL 临时实例 | `127.0.0.1:3307` | 通过 | 端口监听，Java 平台记录可查询 | 不适用 |
| Vue 关键页面 | Dashboard、RunConsole、History、Reports、Models、Plugins、Agents、Workflow Templates、Workflow Editor | 通过 | HTTP 200 | 不适用 |
| CodeAgent smoke | `.\scripts\smoke_codeagent.ps1 -ApiMode java -CheckBlockedPath` | 通过 | 文件写入、阻断 `.env`、SSE、RunEvent、Replay、审计日志均通过 | 不适用 |
| Workflow 模板 smoke | `.\scripts\smoke_workflow_template.ps1` | 通过 | 保存、版本递增、实例化、回放、删除均通过 | 不适用 |
| 演示数据生成 | `.\scripts\seed_v2_demo_data.ps1` | 通过 | 生成 Agent 运行、CodeAgent 操作、Workflow 模板回放记录 | 不适用 |

## 2026-05-24 v2-only 验收记录

| 测试项 | 命令/页面 | 结果 | 问题 | 是否修复 |
|---|---|---|---|---|
| 前端生产构建 | `cd frontend-vue && npm run build` | 通过 | 仅 Vite chunk size 常规警告 | 不适用 |
| Java 打包 | `cd backend-java && mvn -DskipTests package` | 通过 | 无 | 不适用 |
| Docker Compose | `MYSQL_HOST_PORT=3307 docker compose up -d --build` | 通过 | 本机 3306 已占用，使用 3307 映射 | 不适用 |
| Python API | `http://127.0.0.1:8001/health` | 通过 | 返回 `python-agent-engine / v2-api-preview` | 不适用 |
| Java Gateway | `http://127.0.0.1:8088/api/health` | 通过 | 返回 `java-platform-service / v2-java-preview` | 不适用 |
| Java -> Python Proxy | `http://127.0.0.1:8088/api/agent/health` | 通过 | 返回 Python health | 不适用 |
| Vue 关键页面 | `/`、`/agents`、`/workflows/templates`、`/workflows/editor`、`/history`、`/reports` | 通过 | 全部 HTTP 200 | 不适用 |
| CodeAgent smoke | `.\scripts\smoke_codeagent.ps1 -ApiMode java -CheckBlockedPath` | 通过 | 文件写入、阻断路径、SSE、RunEvent、Replay、审计日志均通过 | 不适用 |
| Workflow 模板 smoke | `.\scripts\smoke_workflow_template.ps1` | 通过 | 保存、版本递增、实例化、回放、删除均通过 | 不适用 |
| v2 最终验收脚本 | `.\scripts\final_v2_acceptance.ps1` | 通过 | 脚本退出码 0，生成演示数据并检查关键页面 | 不适用 |

## 2026-05-26 Workflow Runtime Lite 增强记录

| 测试项 | 命令/页面 | 结果 | 问题 | 是否修复 |
|---|---|---|---|---|
| 前端生产构建 | `cd frontend-vue && npm run build` | 通过 | 仅 Vite chunk size 常规警告 | 不适用 |
| Java 打包 | `cd backend-java && mvn -DskipTests package` | 通过 | 无 | 不适用 |
| Runtime Lite smoke 脚本 | `.\scripts\smoke_workflow_runtime_lite.ps1` | 待执行 | 当前本地 Python / Java 服务未启动，需启动 v2 主链路后执行 | 待确认 |

## 2026-05-27 Dynamic LangGraph Runtime v1 记录

| 测试项 | 命令/页面 | 结果 | 问题 | 是否修复 |
|---|---|---|---|---|
| Python 编译 | `python -m compileall api_server.py core/state.py dynamic_workflow` | 通过 | 无 | 不适用 |
| Python 动态暂停/恢复 smoke | `execute_dynamic_workflow` + `resume_dynamic_workflow` inline smoke | 通过 | 执行先进入 `WAITING_FOR_HUMAN`，批准后进入 `SUCCESS` 并生成动态报告 | 不适用 |
| 前端生产构建 | `cd frontend-vue && npm run build` | 通过 | 仅 Vite chunk size / VueUse pure comment 常规警告 | 不适用 |
| Java clean package | `cd backend-java && mvn -DskipTests clean package` | 通过 | 无 | 不适用 |
| Diff 格式检查 | `git diff --check` | 通过 | 仅 LF/CRLF 提示，不影响格式检查 | 不适用 |

## 2026-05-27 Workflow Skill Export 记录

| 测试项 | 命令/页面 | 结果 | 问题 | 是否修复 |
|---|---|---|---|---|
| Java clean package | `cd backend-java && mvn -DskipTests clean package` | 通过 | 新增 `WorkflowSkillExportService` 编译通过 | 不适用 |
| 前端生产构建 | `cd frontend-vue && npm run build` | 通过 | 仅 Vite chunk size / VueUse pure comment 常规警告 | 不适用 |
| Diff 格式检查 | `git diff --check` | 通过 | 仅 LF/CRLF 提示，不影响格式检查 | 不适用 |

## 2026-05-28 Skill Export 与 Dynamic Runtime 验收闭环记录

| 测试项 | 命令/页面 | 结果 | 问题 | 是否修复 |
|---|---|---|---|---|
| Skill Export smoke 脚本 | `.\scripts\smoke_skill_export.ps1 -RunExportedScript` | 通过 | 导出 `SKILL.md`、模板 JSON、`run_workflow.py`，导出脚本执行状态 `SUCCESS` | 不适用 |
| Runtime Lite / Skill Export 接入最终验收 | `.\scripts\final_v2_acceptance.ps1 -SkipDemoSeed` | 通过 | 脚本退出码 0，已纳入 Runtime Lite smoke 和 Skill Export smoke | 不适用 |
| Skill Export 演示文档 | `docs/SKILL_EXPORT_DEMO_GUIDE.md` | 通过 | 新增演示路径、自动验收命令和常见问题 | 不适用 |

## 2026-05-28 Dynamic LangGraph runtime context 记录

| 测试项 | 命令/页面 | 结果 | 问题 | 是否修复 |
|---|---|---|---|---|
| 字段级 runtime context smoke | `.\scripts\smoke_dynamic_runtime_context.ps1` | 通过 | `alpha.alpha_result -> beta.beta_input` 真实传值，Beta 输出包含接收到的上游值 | 不适用 |
| Python 编译 | `python -m compileall core/state.py dynamic_workflow` | 通过 | 无 | 不适用 |
| 前端生产构建 | `cd frontend-vue && npm run build` | 通过 | 仅 Vite chunk size / VueUse pure comment 常规警告 | 不适用 |
| Java 打包 | `cd backend-java && mvn -DskipTests package` | 通过 | 无 | 不适用 |

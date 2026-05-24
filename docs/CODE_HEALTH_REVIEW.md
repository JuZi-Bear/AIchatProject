# 代码健康检查报告

## 检查范围

- v2 入口：`api_server.py`、`frontend-vue/`、`backend-java/`、`docker-compose.yml`、`runner-cpp/`。
- 共享核心：`core/`、`agents.py`、`plugins/`、`utils/`、`config/`。
- 文档和启动脚本：`README.md`、`docs/`、`scripts/`。

## 核心入口检查

| 入口 | 状态 | 说明 |
| --- | --- | --- |
| `api_server.py` | 保留 | Python FastAPI Agent Engine |
| `frontend-vue/` | 保留 | v2 Vue 前端 |
| `backend-java/` | 保留 | Java Platform API |
| `docker-compose.yml` | 保留 | v2-only 多服务编排 |
| `runner-cpp/` | 保留 | 可选 C++ Runner Sandbox |
| `scripts/start_v2_local.ps1` | 保留 | v2 本地联调 |
| `scripts/final_v2_acceptance.ps1` | 保留 | v2 最终验收 |

## 已清理内容

- 旧 Python 页面入口已删除。
- CLI 演示入口已删除。
- Windows v1 安装和启动脚本已删除。
- v1-only 发布、冻结和验收文档已删除。
- 过时并行架构主文档已删除。
- `requirements.txt` 已移除 v1-only 依赖。
- 根 `Dockerfile` 已改为默认启动 FastAPI。

## 配置一致性

- Python API：`8001`。
- Java Gateway：`8088`。
- Vue 生产端口：`5174`。
- MySQL 容器端口：`3306`，本机可通过 `MYSQL_HOST_PORT` 覆盖。
- Docker Compose 服务：`mysql`、`ai-agent-api`、`backend-java`、`frontend-vue`。

## 风险项

- 内部工作流函数名 `run_graph_demo` 仍保留，用于 `services/run_service.py` 调用；当前不建议为了命名洁癖立即重命名。
- 部分历史文档可能仍提到早期演示背景，但不作为当前启动入口。
- Workflow Editor 当前不驱动动态 LangGraph 分支。
- CodeAgent 是简化受控文件操作，不是完整自动编码代理。

## 建议清理项

- 后续可将历史文档集中移动到 `docs/archive/`。
- 后续可把 `run_graph_demo` 重命名为更中性的 `run_workflow`，但需同步测试。
- 后续可继续精简 `docs/` 中早期比赛材料。

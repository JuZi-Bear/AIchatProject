# 双轨测试结果记录

本文用于手动记录 v1.0 / v2.0 双轨启动和回归测试结果。

| 测试项 | 轨道 | 命令/页面 | 结果 | 问题 | 是否修复 |
|---|---|---|---|---|---|
| 虚拟环境激活 | v1-demo | `.\.venv\Scripts\Activate.ps1` | 未测试 |  |  |
| requirements 安装 | v1-demo | `pip install -r requirements.txt` | 未测试 |  |  |
| CLI 演示 | v1-demo | `python graph_demo.py` | 未测试 |  |  |
| Streamlit Web UI | v1-demo | `python -m streamlit run webui.py` | 未测试 |  |  |
| Windows 启动脚本 | v1-demo | `.\start_demo.bat` | 未测试 |  |  |
| FastAPI 启动 | v2-platform | `python -m uvicorn api_server:app --reload --host 127.0.0.1 --port 8001` | 未测试 |  |  |
| Vue 开发模式 | v2-platform | `npm run dev` | 未测试 |  |  |
| Java Gateway | v2-platform | `mvn spring-boot:run` | 未测试 |  |  |
| Docker Compose | v2-platform | `docker compose up --build` | 未测试 |  |  |
| Vue Dashboard | v2-platform | `http://localhost:5173` 或 `http://localhost:5174` | 未测试 |  |  |
| FastAPI Docs | v2-platform | `http://localhost:8001/docs` | 未测试 |  |  |
| Java Health | v2-platform | `http://localhost:8088/api/health` | 未测试 |  |  |
| Streamlit Docker | v1-demo / docker | `http://localhost:8501` | 未测试 |  |  |
| C++ Runner 可选编译 | experimental | `cmake -S . -B build` | 未测试 |  |  |

## 2026-05-21 v2-demo-rc1 验收记录

| 测试项 | 轨道 | 命令/页面 | 结果 | 问题 | 是否修复 |
|---|---|---|---|---|---|
| v2 最终验收脚本 | v2-platform | `.\scripts\final_v2_acceptance.ps1` | 通过 | 脚本退出码 0，完成本地启动、API 检查、smoke、演示数据和页面检查 | 不适用 |
| Python API | v2-platform | `http://127.0.0.1:8001/health` | 通过 | 返回 `python-agent-engine / v2-api-preview` | 不适用 |
| Java Gateway | v2-platform | `http://127.0.0.1:8088/api/health` | 通过 | 返回 `java-platform-service / v2-java-preview` | 不适用 |
| MySQL 临时实例 | v2-platform | `127.0.0.1:3307` | 通过 | 端口监听，Java 平台记录可查询 | 不适用 |
| Vue Dashboard | v2-platform | `http://127.0.0.1:5174/` | 通过 | HTTP 200 | 不适用 |
| Vue RunConsole | v2-platform | `http://127.0.0.1:5174/runs/new` | 通过 | HTTP 200 | 不适用 |
| Vue History | v2-platform | `http://127.0.0.1:5174/history` | 通过 | HTTP 200 | 不适用 |
| Vue Reports | v2-platform | `http://127.0.0.1:5174/reports` | 通过 | HTTP 200 | 不适用 |
| Vue Models | v2-platform | `http://127.0.0.1:5174/models` | 通过 | HTTP 200 | 不适用 |
| Vue Plugins | v2-platform | `http://127.0.0.1:5174/plugins` | 通过 | HTTP 200 | 不适用 |
| Vue Agents | v2-platform | `http://127.0.0.1:5174/agents` | 通过 | HTTP 200 | 不适用 |
| Workflow Templates | v2-platform | `http://127.0.0.1:5174/workflows/templates` | 通过 | HTTP 200 | 不适用 |
| Workflow Editor | v2-platform | `http://127.0.0.1:5174/workflows/editor` | 通过 | HTTP 200 | 不适用 |
| CodeAgent smoke | v2-platform | `.\scripts\smoke_codeagent.ps1 -ApiMode java -CheckBlockedPath` | 通过 | 文件写入、阻断 `.env`、SSE、RunEvent、Replay、审计日志均通过 | 不适用 |
| Workflow 模板 smoke | v2-platform | `.\scripts\smoke_workflow_template.ps1` | 通过 | 保存、版本递增、实例化、回放、删除均通过 | 不适用 |
| 演示数据生成 | v2-platform | `.\scripts\seed_v2_demo_data.ps1` | 通过 | 生成 Agent 运行、CodeAgent 操作、Workflow 模板回放记录；平台记录数 44 | 不适用 |
| 真实 Agent 示例运行 | v2-platform | `POST /api/runs` via seed script | 通过 | 新 seed 示例生成 `platform_20260521_055559_0f224000` / `run_20260521_135615`；业务结果 `success=true`、`qualityScore=100` | 是 |

## 记录规则

- 结果建议填写：通过 / 失败 / 跳过 / 未测试。
- 问题栏记录错误摘要、端口、日志位置或截图说明。
- 是否修复建议填写：是 / 否 / 待确认。
- 不确定是否影响双轨时，同时标记 v1-demo 和 v2-platform。

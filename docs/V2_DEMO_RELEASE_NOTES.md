# v2-demo-rc1 发布说明

发布日期：2026-05-21

## 发布定位

`v2-demo-rc1` 是 v2.0 平台化演示候选版本。它不替代 v1.0 Streamlit 稳定演示轨，而是用于展示 Vue + Java + MySQL + FastAPI + CodeAgent + Workflow Replay 的平台化升级能力。

## 当前可演示能力

- Vue Dashboard 平台总览。
- Java Gateway 模式下的 MySQL 运行记录、事件记录和配置视图。
- Python FastAPI Agent Engine 独立服务。
- CodeAgent 受控文件操作：`read_file`、`write_file`、`list_files`。
- CodeAgent 路径白名单、阻断路径、读取长度限制和 JSONL 审计日志。
- RunEvent 持久化、SSE 实时事件、History 事件时间线。
- Workflow Replay 回放页面。
- Agent 注册中心页面。
- Workflow 模板中心与可视化 Workflow Editor。
- Workflow 模板保存到 Java + MySQL、版本递增、详情预览、删除和实例化为可回放任务。
- 一键演示数据脚本和三分钟平台演示脚本。

## 推荐启动命令

完整验收：

```powershell
cd D:\AIchatProject
.\scripts\final_v2_acceptance.ps1
```

本地联调：

```powershell
.\scripts\start_v2_local.ps1
```

生成演示数据：

```powershell
.\scripts\seed_v2_demo_data.ps1
```

停止本地联调服务：

```powershell
.\scripts\stop_v2_local.ps1
```

## 验收结果

2026-05-21 已执行：

```powershell
.\scripts\final_v2_acceptance.ps1
```

结果：通过。

确认项：

- Python API：`http://127.0.0.1:8001/health` 正常。
- Java Gateway：`http://127.0.0.1:8088/api/health` 正常。
- MySQL：临时实例 `127.0.0.1:3307` 正常监听。
- Vue：Dashboard、RunConsole、History、Reports、Models、Plugins、Agents、Workflow Templates、Workflow Editor 均 HTTP 200。
- CodeAgent smoke：文件写入、阻断 `.env`、SSE、RunEvent、Replay、JSONL 审计日志均通过。
- Workflow 模板 smoke：保存、版本递增、实例化、回放、删除均通过。
- 演示数据：成功生成 Agent 运行、CodeAgent 操作和 Workflow 模板回放三类记录。
- 真实 Agent 示例：`platform_20260521_055559_0f224000` / `run_20260521_135615`，结果 `success=true`、`qualityScore=100`。

## 已知限制

- v2.0 平台化能力仍是演示候选，不建议比赛现场临时改 LangGraph 主流程。
- Workflow 模板实例化当前生成可回放任务视图，不直接驱动动态 LangGraph 分支。
- CodeAgent 是简化执行模块，不是完整 Codex；只执行用户指定路径的受控文件操作。
- C++ Runner Sandbox 仍是可选增强，不默认替代 Python Runner。
- 用户系统、权限系统、团队协作和任务队列尚未纳入当前候选版本。
- 本地启动脚本已优先使用 `.venv\Scripts\python.exe`。如果绕过脚本手动用系统 Python 启动 FastAPI，需要确认该 Python 环境已安装 `coverage`，否则 pytest + coverage 阶段可能失败。

## 现场兜底

如果 v2 链路不可用，切回 v1.0 Streamlit：

```powershell
python -m streamlit run webui.py
```

如果 Vue 页面不可访问：

```powershell
.\scripts\start_v2_local.ps1
```

如果演示数据不足：

```powershell
.\scripts\seed_v2_demo_data.ps1
```

如果只需要快速验证 CodeAgent：

```powershell
.\scripts\smoke_codeagent.ps1 -ApiMode java -CheckBlockedPath
```

## 不建议现场操作

- 不现场修改 `.env` API Key。
- 不现场修改数据库表结构。
- 不现场改 Java JPA 实体字段。
- 不现场改 Vue 路由或构建配置。
- 不现场把 Workflow 模板接入真实 LangGraph 动态编排。
- 不现场删除 Streamlit v1 演示轨。

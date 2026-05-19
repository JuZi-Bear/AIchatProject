# AI Multi-Agent Pipeline

AI Multi-Agent Pipeline 是一个基于多智能体协作的自主开发流水线。项目可以从自然语言需求出发，完成需求拆解、代码生成、测试验证、错误分析、自动修复、质量评分和 Markdown 报告生成。

当前项目采用“双轨并行”策略：

- v1.0 比赛演示轨：Python + LangGraph + Streamlit，优先稳定演示。
- v2.0 平台化升级轨：Vue3 + TypeScript + Java Spring Boot + MySQL + FastAPI + C++ Runner Sandbox，优先工程扩展。

详细说明见 `docs/DUAL_TRACK_ARCHITECTURE.md`。

## 核心能力

- 多 Agent 协作：Product、Coder、Tester、Runner、Sentry 和插件 Agent 分工协作。
- 自动修复闭环：测试失败后由 Sentry 分析错误，Coder 自动修复，再次验证。
- 插件扩展：Doc Agent、Security Agent、Refactor Agent、UI Agent。
- 质量评分：汇总测试、覆盖率、安全、修复次数和报告结果。
- 报告生成：输出 Markdown 报告，并支持历史记录查看。
- 平台事件记录：Java + MySQL 记录任务创建、状态变化、Python 请求/响应、成功失败和报告索引事件。
- 实时事件流：Java Gateway 模式下通过 SSE 向 Vue 推送平台事件日志。
- 细粒度 Agent 事件：Python Agent Engine 输出 `workflow_events`，记录 Product、Coder、Tester、Runner、Sentry、Quality 和 Report 等节点事件。
- 工作流回放：Vue 可基于 Java + MySQL 事件记录逐步回放一次历史运行。
- Agent 注册中心：Python 统一管理 Agent 元信息，Vue 可查看注册表。
- Prompt 模板管理：主要 Agent Prompt 已迁移到 `prompts/` Markdown 模板。
- Workflow 模板管理：Python 提供 `workflow_templates/`，Vue 可查看模板、Agent 顺序、阶段顺序并生成轻量模板任务视图。
- 可视化工作流编辑器：Vue 支持从 Agent Palette 拖拽节点、调整执行顺序、编辑节点输入输出和生成模板任务视图。
- 简化 CodeAgent：支持在 Workflow Editor 中触发 `read_file`、`write_file`、`list_files` 项目文件操作，并生成可 SSE 推送和回放的事件。
- 双轨展示：Streamlit 稳定演示 + Vue 平台化预览。
- 多服务部署：Docker Compose 启动 Vue、Java、MySQL、FastAPI 和 Streamlit。

## 双轨架构说明

| 轨道 | 技术栈 | 目标 | 入口 |
| --- | --- | --- | --- |
| v1-demo | Python、LangGraph、Streamlit、yaml、Python Runner | 比赛现场稳定演示 | `webui.py`、`graph_demo.py`、`start_demo.bat` |
| v2-platform | Vue3、TypeScript、FastAPI、Spring Boot、MySQL、Docker Compose、C++ Runner | 平台化升级预览 | `frontend-vue/`、`backend-java/`、`api_server.py`、`docker-compose.yml` |

当前推荐：比赛现场优先使用 v1 Streamlit；平台能力展示使用 v2 Docker Compose 或 Java Gateway 模式。

## 技术框架扩展方向

当前 v2.0 不只是功能升级，而是平台化框架升级。项目后续优先扩展技术框架，而不是继续堆单点功能。

已完成的框架能力：

- Python Agent Engine 与 FastAPI API 层。
- Streamlit v1 稳定演示入口。
- Vue3 + TypeScript 平台前端骨架。
- Java Spring Boot Gateway + MySQL 平台数据视图。
- Java 平台任务事件记录与 Vue 事件时间线。
- SSE 实时事件流预留接口。
- Python Agent Engine 细粒度事件上报。
- Java + MySQL + Vue 工作流回放。
- Agent 注册中心与 Prompt 模板管理。
- Workflow 模板管理和 Vue 模板选择页面。
- Vue 可视化工作流拖拽编辑器最小版本。
- 简化 CodeAgent 文件操作节点。
- C++ Runner Sandbox 最小版本。
- Docker Compose 多服务部署。

规划中的框架能力：

- Java 任务生命周期管理。
- Java 配置中心增强。
- Vue 接入平台配置和工作台能力。
- Python Workflow 模板管理向可视化编排继续扩展。
- WebSocket 实时日志升级与工作流回放增强。
- 更强 Runner 隔离和 Docker Sandbox 预留。

当前推荐扩展路线见 `docs/RECOMMENDED_EXTENSION_ROADMAP.md`，完整规划见 `docs/FRAMEWORK_EXTENSION_PLAN.md`。

## 技术栈

- Python 3.11：Agent Engine、LangGraph 工作流、Streamlit、FastAPI。
- workflow_events：Python 工作流细粒度事件，用于 Java 持久化、SSE 推送和 Vue 时间线展示。
- agent_registry / prompts：Python Agent 元信息注册和 Prompt 模板管理。
- workflow_templates：Python Workflow 模板管理，保存可复用流程和 Markdown 描述。
- Vue3 + TypeScript + Vite：v2 平台前端。
- Element Plus、Pinia、Axios、Vue Router：前端 UI、状态和 API 调用。
- Java 17 + Spring Boot 3 + Maven：平台服务层和 API Gateway。
- MySQL 8.0：平台运行记录、报告索引、配置和统计数据。
- C++17 + CMake：C++ Runner Sandbox 最小版本。
- Docker Compose：多服务编排。

更多技术细节见 `docs/TECH_STACK.md`。

## 快速启动

### v1.0 比赛演示模式

安装依赖：

```powershell
pip install -r requirements.txt
```

启动 Streamlit：

```powershell
python -m streamlit run webui.py
```

或使用 Windows 脚本：

```powershell
start_demo.bat
```

CLI 演示：

```powershell
python graph_demo.py
```

### v2.0 Python API 模式

启动 FastAPI Agent Engine：

```powershell
python -m uvicorn api_server:app --reload --host 127.0.0.1 --port 8001
```

访问：

- FastAPI Docs: http://localhost:8001/docs
- Health: http://localhost:8001/health

### v2.0 Vue 开发模式

```powershell
cd frontend-vue
npm install
npm run dev
```

默认开发配置见 `frontend-vue/.env.development`。Vue 支持两种 API 模式：

- `VITE_API_MODE=python`：直连 Python FastAPI。
- `VITE_API_MODE=java`：通过 Java Gateway 调用。

### v2.0 Java Gateway 模式

先启动 Python FastAPI，再启动 Java：

```powershell
cd backend-java
mvn spring-boot:run
```

访问：

- Java Health: http://127.0.0.1:8088/api/health
- Java Agent Health: http://127.0.0.1:8088/api/agent/health

MySQL 配置见 `docs/MYSQL_SETUP.md`。

Java Gateway 模式下，平台层会为每次运行记录任务事件。History 页面可查看单次运行事件时间线，Dashboard 可查看最近平台事件；RunConsole 和 History 可通过 SSE 订阅实时事件流。这只是实时日志和运行回放的基础，不会改变 Python LangGraph 执行流程。

### v2.0 本地一键联调

推荐用脚本启动 Java Gateway 演示链路：

```powershell
.\scripts\start_v2_local.ps1
```

默认会启动 Python API、临时 MySQL `3307`、Java Gateway、Vue Java 模式，并执行一次 CodeAgent smoke test。

停止：

```powershell
.\scripts\stop_v2_local.ps1
```

单独验证 CodeAgent：

```powershell
.\scripts\smoke_codeagent.ps1 -ApiMode java -CheckBlockedPath
```

单独验证 Workflow Editor 自定义模板保存到 Java + MySQL：

```powershell
.\scripts\smoke_workflow_template.ps1
```

详细说明见 `docs/LOCAL_V2_STARTUP.md`。

### Workflow 模板管理

Vue 可访问 `/workflows/templates` 查看当前内置模板：

- 简单演示流程
- 完整多 Agent 流程
- 自动修复重点流程

模板页面会展示 Agent 执行顺序、阶段顺序和 Markdown 描述，并可生成轻量模板任务视图。当前模板实例化不直接执行 LangGraph，后续可升级为可视化工作流编辑和任务快速生成。

Vue 还提供 `/workflows/editor` 可视化工作流拖拽编辑器：

- 左侧 Agent Palette 从 Agent 注册中心读取节点。
- 中间 Canvas 支持拖入节点、拖动位置、顺序连线和删除节点。
- 右侧属性面板支持编辑输入字段、输出字段、阶段、启用状态和描述。
- 工具栏支持新建、撤销、重做、加载模板、本地保存模板、导出 JSON 和生成任务视图。

当前编辑器在 Python Direct 模式下保存到浏览器 localStorage；在 Java Gateway 模式下可额外保存到 MySQL，接口为 `POST /api/platform/workflows/templates`。MySQL 模板支持详情预览、覆盖保存版本递增、删除，以及一键生成可回放任务视图。Dashboard 和 History 会将这类记录标记为“模板回放”，与真实 Agent 运行、CodeAgent 文件操作区分开。生成任务时仍不会直接改写 LangGraph 主流程。

### 简化 CodeAgent 文件操作

Workflow Editor 中选中 `CodeAgent` 节点后，可以触发三类受控文件操作：

```text
read_file("src/moduleA.py")
write_file("src/moduleB.py", content)
list_files("src/")
```

每次操作都会返回摘要：

```json
{
  "success": true,
  "filePath": "src/moduleA.py",
  "message": "已读取/修改/生成内容"
}
```

并生成 `AGENT_STARTED`、`AGENT_FINISHED` 或 `AGENT_FAILED` 事件。Java Gateway 模式下，这些事件会写入 MySQL `run_event` 并通过 SSE 推送给 Vue；Python Direct 模式下，前端直接展示 API 返回事件。该模块不是完整 Codex，不会自动决定修改哪些文件，只执行用户指定路径的受控操作。

CodeAgent 的访问范围由 `config/settings.yaml` 中的 `code_agent.allowed_paths` 和 `code_agent.blocked_paths` 控制；审计日志默认写入 `output/code_agent_audit.jsonl`。

RunConsole 也提供 CodeAgent 操作面板，便于比赛现场快速演示“拖拽/触发 -> 文件生成或修改 -> SSE 事件 -> 审计日志 -> 回放”的闭环。Java Gateway 模式下，每次 CodeAgent 操作会登记为平台运行记录，可在 History 和 Workflow Replay 中查看事件顺序。完整说明见 `docs/CODE_AGENT_NODE_GUIDE.md`。

## Docker Compose 启动

复制环境变量示例：

```powershell
Copy-Item .env.docker.example .env
```

启动多服务：

```powershell
docker compose up --build
```

访问地址：

- Vue 前端: http://localhost:5174
- Java 平台服务: http://localhost:8088/api/health
- FastAPI Docs: http://localhost:8001/docs
- Streamlit v1: http://localhost:8501
- MySQL: localhost:3306

停止：

```powershell
docker compose down
```

完整说明见 `docs/DOCKER_COMPOSE_GUIDE.md`。

## 双轨启动测试

修改代码或文档后，按影响范围验证 v1.0 和 v2.0 两条轨道：

- `docs/DUAL_TRACK_TEST_CHECKLIST.md`：v1.0 / v2.0 启动测试清单。
- `docs/TEST_RESULT_LOG.md`：手动测试结果记录表。
- `docs/STARTUP_ORDER.md`：v1.0、v2.0 本地开发和 Docker 模式推荐启动顺序。

## 项目结构

```text
AIchatProject/
├─ frontend-vue/      v2 Vue3 + TypeScript 前端
├─ backend-java/      v2 Java Spring Boot 平台服务层
├─ runner-cpp/        C++ Runner Sandbox 预研模块
├─ workflow_templates/ Workflow 模板和 Markdown 描述
├─ core/              LangGraph 状态和工作流
├─ plugins/           插件系统
├─ utils/             Runner、摘要、历史和 UI ViewModel 工具
├─ config/            yaml 配置
├─ reports/           生成报告
├─ runs/              运行历史
├─ output/            生成代码和临时输出
├─ docs/              项目文档
├─ api_server.py      Python FastAPI Agent Engine
├─ webui.py           Streamlit v1 演示入口
├─ graph_demo.py      CLI 演示入口
└─ docker-compose.yml 多服务编排
```

完整目录说明见 `docs/PROJECT_DIRECTORY_GUIDE.md`。

## 文档导航

优先阅读：

- `docs/DOCUMENT_INDEX.md`：文档总导航。
- `docs/DUAL_TRACK_ARCHITECTURE.md`：双轨并行架构。
- `docs/API_CONTRACT.md`：API 契约。
- `docs/DOCKER_COMPOSE_GUIDE.md`：多服务 Docker 启动。
- `docs/LOCAL_V2_STARTUP.md`：v2 本地一键联调脚本。
- `docs/VIDEO_CODING_GUIDE.md`：录制和现场讲解。
- `docs/DEFENSE_SCRIPT.md`：答辩讲稿。
- `docs/RISK_AND_STABILITY.md`：风险和兜底。
- `docs/CODEX_COLLAB_RULES.md`：Codex 协作规范。
- `docs/CODE_HEALTH_REVIEW.md`：代码健康检查。
- `docs/ISSUE_TRIAGE.md`：测试问题分级和归档。
- `docs/FIX_PLAN.md`：修复计划。
- `docs/NEXT_ACTION_QUEUE.md`：下一步行动队列。
- `docs/REDUNDANCY_REVIEW.md`：文档冗余评审。
- `docs/FRAMEWORK_EXTENSION_PLAN.md`：技术框架扩展总规划。
- `docs/FRAMEWORK_EXTENSION_BOUNDARY.md`：框架扩展边界。
- `docs/FRAMEWORK_EXTENSION_CANDIDATES.md`：候选扩展评估。
- `docs/RECOMMENDED_EXTENSION_ROADMAP.md`：推荐扩展路线。
- `docs/FRAMEWORK_EXTENSION_ARCHITECTURE.md`：未来架构示意图。
- `docs/CODE_AGENT_NODE_GUIDE.md`：CodeAgent 节点集成和演示闭环。
- `docs/MAINTENANCE_GUIDE.md`：维护指南。
- `docs/SAFE_CHANGE_CHECKLIST.md`：安全变更检查清单。
- `docs/DUAL_TRACK_TEST_CHECKLIST.md`：双轨启动测试清单。
- `docs/STARTUP_ORDER.md`：推荐启动顺序。
- `docs/TEST_RESULT_LOG.md`：测试结果记录。

## Video Coding 指南入口

录制建议顺序：

1. 项目总览和双轨架构。
2. Streamlit v1 稳定演示。
3. FastAPI Agent Engine。
4. Vue Dashboard。
5. Java Gateway 和 MySQL。
6. C++ Runner Sandbox。
7. Docker Compose 多服务部署。

详细脚本见 `docs/VIDEO_CODING_GUIDE.md`。

## 后续规划

- 保持 v1 Streamlit 作为稳定演示轨。
- 继续增强 v2 Vue 平台前端体验。
- 让 Java 平台层逐步承担任务管理、配置中心和团队协作能力。
- 增强 C++ Runner 的隔离、超时和资源限制。
- 在 v2 稳定后再评估是否收敛 Streamlit 为 legacy demo。

路线图见 `docs/V2_ARCHITECTURE_PLAN.md` 和 `docs/TASKS.md`。

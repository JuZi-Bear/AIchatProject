# v2.0 多技术栈架构预留规划

本文用于规划项目从 v1.0 比赛演示版升级到 v2.0 多技术栈平台版的路线。当前阶段已新增 Python Agent Engine API 服务层、独立 Vue3 + TypeScript 前端、Java Spring Boot API Gateway 和 C++ Runner Sandbox 雏形，不影响 v1.0 Streamlit 演示稳定性。

当前 v2.0 不只是功能升级，而是平台化框架升级：通过 Vue、Java、MySQL、FastAPI、C++ Runner 和 Docker Compose 把项目从单机演示扩展为可继续演进的平台骨架。框架扩展总规划见 `docs/FRAMEWORK_EXTENSION_PLAN.md`，推荐路线见 `docs/RECOMMENDED_EXTENSION_ROADMAP.md`。

## v1.0 当前架构

v1.0 目标是稳定完成比赛演示，强调“可运行、可展示、可复盘”。

- Python：项目主语言，承载 Agent、工作流、测试、运行、报告和 Web UI。
- LangGraph：多 Agent 状态机，负责 Product、Coder、Tester、Approval、Runner、Sentry、Plugins、Quality、Report 等节点编排。
- Streamlit：v1.0 Web UI 演示前端，负责案例选择、运行控制、工作流可视化、报告和历史记录展示。
- Docker：固定 Python 运行环境，降低跨设备部署风险。
- 插件系统：通过 `plugins/` 和 `config/agents.yaml` 支持 Doc、Security、Refactor、UI 等自定义 AI 模块。
- run_summary：统一运行摘要，供 CLI、Web UI、报告和模型对比复用。
- ui_view_model：统一 UI 数据层，让页面优先读取展示结构而不是反复解析原始 state。
- run_service：Application Service 层，封装创建运行、读取历史、查询报告、模型和插件，为 API 层提供统一调用入口。
- FastAPI：v2.0 第一阶段新增 `api_server.py`，将 Python Agent Engine 暴露为 HTTP API。
- frontend-vue：v2.0 第二阶段新增独立 Vue3 + TypeScript 前端骨架，用于后续替代 Streamlit。

当前架构可以概括为：

```text
Streamlit Web UI / CLI / FastAPI API / frontend-vue
  ↓
services/run_service.py
  ↓
Python Agent Engine
  ↓
LangGraph Workflow
  ↓
Runner / pytest / coverage / plugins / report
  ↓
run_summary + ui_view_model + runs + reports
```

## v2.0 目标架构

v2.0 目标是从比赛演示工具升级为可扩展平台，支持前后端分离、多服务部署和更强安全执行。

- Vue3 + TypeScript 前端：正式 Dashboard，负责交互、时间轴动画、模型对比、报告和历史记录。
- Java Spring Boot 平台服务层：负责用户、权限、任务、审计、运行记录、组织管理和企业系统集成。
- Python Agent Engine：继续负责多 Agent、LangGraph、模型调用、测试修复和报告生成。
- C++ Runner Sandbox：作为后续安全执行增强，隔离运行 AI 生成代码。
- Docker Compose 多服务编排：同时启动前端、Java API、Python Agent Engine、Runner Sandbox 等服务。

## 服务拆分设计

### frontend-vue

职责：

- Vue3 + TypeScript 实现正式前端。
- 消费 `ui_view_model` 渲染 Dashboard。
- 展示 Agent 工作流时间轴、结果总览、模型对比、插件结果、报告和历史。
- 通过 `VITE_API_MODE` 在 Python Direct 和 Java Gateway 两种 API 调用模式间切换。
- Java Gateway 模式下优先读取 Java/MySQL 持久化数据，包括平台运行记录、前端配置、模型配置和插件配置；Python Direct 模式继续读取 Python API 和 localStorage。
- 未来可加入更流畅的时间轴动画和交互式报告查看。

边界：

- 不直接调用大模型。
- 不直接运行代码。
- 不解析 LangGraph 原始 state。

### backend-java

职责：

- Java Spring Boot 作为平台服务层。
- 提供用户、权限、任务管理、运行审计、组织空间、API 鉴权等能力。
- 调用 Python Agent Engine 提交 AI 工作流任务。
- 存储运行记录索引和业务侧元数据。

边界：

- 不实现 Agent 逻辑。
- 不直接执行 AI 生成代码。
- 不替代 Python LangGraph 工作流。

### agent-engine-python

职责：

- 保留当前 Python LangGraph 核心。
- 提供 FastAPI HTTP API，通过 `api_server.py` 包装 `services/run_service.py`。
- 负责 Product、Coder、Tester、Sentry、Plugins、Quality、Report。
- 输出 `state`、`run_summary` 和 `ui_view_model`。

边界：

- 不承担用户系统和企业权限。
- 不实现正式前端页面。

### runner-sandbox-cpp

职责：

- 后续提供更强隔离的代码运行环境。
- 可对 AI 生成代码进行资源限制、超时控制、文件系统隔离和危险调用拦截。
- 与 Python Agent Engine 通过进程或 API 通信。

边界：

- 不调用大模型。
- 不生成代码。
- 只关注安全执行。

## 数据流

```text
用户需求
  ↓
Vue 前端
  ↓
Java API
  ↓
Python Agent Engine
  ↓
LangGraph
  ↓
Runner Sandbox
  ↓
run_summary / ui_view_model
  ↓
前端展示
```

更细的数据关系：

```text
Vue3 + TS
  当前预览阶段可直接调用 Python Agent Engine API
  后续平台化阶段调用 Java API：POST /runs

Java Spring Boot
  做鉴权、任务登记、审计
  转发到 Python Agent Engine

Python Agent Engine
  FastAPI 接收请求
  调用 services/run_service.create_run(request)
  执行 LangGraph 工作流
  生成 state / run_summary / ui_view_model

C++ Runner Sandbox
  接收待运行代码
  返回 stdout / stderr / returncode / 安全状态

Vue3 + TS
  直接消费 ui_view_model 渲染页面
```

## 接口契约

接口契约以 `docs/API_CONTRACT.md` 为准。

核心接口包括：

- `POST /runs`
- `GET /runs/{run_id}`
- `GET /runs`
- `GET /models`
- `GET /plugins`
- `GET /reports`
- `GET /reports/{report_name}`

v2.0 前端和 Java 后端都应围绕以下结构设计：

```json
{
  "run_id": "run_20260516_124408",
  "run_summary": {},
  "ui_view_model": {}
}
```

其中：

- `run_id`：本次运行唯一标识。
- `run_summary`：列表、卡片、报告和模型对比的核心摘要。
- `ui_view_model`：前端展示优先消费的数据结构。
- `state`：仅在 `GET /runs/{run_id}` 历史详情和调试场景返回。

## 第一阶段进度

v2.0 第一阶段已新增 Python Agent Engine API：

- 新增 `api_server.py`，通过 FastAPI 暴露健康检查、模型、插件、运行、历史和报告接口。
- 新增 `schemas/`，用 Pydantic 定义 `RunRequest`、`RunResponse`、`RunSummaryResponse` 和 `UIWorkflowStep`。
- API 层只调用 `services/run_service.py`，不直接解析 LangGraph 内部 state。
- Vue3 + TypeScript、Java Spring Boot、C++ Runner Sandbox 后续都通过 API 接入 Python Agent Engine，不直接耦合 LangGraph 内部逻辑。
- v1.0 Streamlit Web UI、`graph_demo.py`、`main.py`、`start_demo.bat`、Docker 启动方式继续保留。

## 第二阶段进度

v2.0 第二阶段已新增 Vue3 + TypeScript 前端骨架：

- 新增 `frontend-vue/` 独立项目，不影响 v1.0 Streamlit Web UI。
- 使用 Vue3、TypeScript、Vite、Vue Router、Pinia、Axios 和 Element Plus。
- 已建立 Dashboard、RunConsole、RunHistory、Reports、Models、Plugins 页面路由。
- 已建立 `src/api/` 封装 `GET /health`、`GET /models`、`GET /plugins`、`GET /runs`、`GET /reports` 和 `POST /runs`。
- `RunConsole` 已提供需求输入、模型选择、插件选择、最大修复次数、人工审批、演示模式、离线模式和开始运行按钮。
- 已新增 `WorkflowTimeline`、`SummaryCards`、`ResultOverview`、`AgentOutputTabs`、`PluginResultPanel` 和 `ReportPreview`。
- Vue 前端已基于 `run_summary` 和 `ui_view_model` 展示工作流可视化、结果总览、Agent 输出详情、插件结果和报告入口。
- `RunHistory` 已支持历史运行列表、成功/失败筛选、模型筛选、需求关键字搜索、按创建时间倒序、点击加载 `GET /runs/{run_id}` 详情。
- 历史详情复用 `SummaryCards`、`WorkflowTimeline`、`ResultOverview`、`AgentOutputTabs` 和 `ReportPreview`，优先消费 `ui_view_model`。
- `Reports` 已支持报告列表、报告名搜索、run_id 解析、点击加载 `GET /reports/{report_name}`、Markdown 文本查看和复制报告内容。
- `Models` 已支持模型列表、provider/启用状态筛选、模型搜索、API Key 状态提示和前端默认模型选择。
- `Plugins` 已支持插件卡片、启用/关闭开关、插件说明、最近结果占位和运行时启用状态管理。
- 新增 `stores/settings.ts`，将默认模型、启用插件、演示模式、最大修复次数、人工审批和离线模式保存到浏览器 localStorage。
- `RunConsole` 已联动前端设置，默认读取 `selectedModelProvider` 和 `enabledPlugins`，运行时仍可临时修改并传给 `POST /runs`。
- `Dashboard` 已升级为 AI 多智能体开发平台总览控制台，展示 API 连接状态、前端默认模型、启用插件数量、运行统计、最近运行、最近报告、模型状态、插件状态和快捷操作。
- Dashboard 通过 `GET /health`、`GET /runs`、`GET /reports`、`GET /models`、`GET /plugins` 分模块加载数据；单个接口失败只影响对应模块，不导致页面白屏。
- `RunConsole` 已支持比赛演示模式，新增演示案例选择、一键开始演示、DemoHero、DemoWorkflowStage、RepairHighlight、DemoResultSummary 和 DemoNarrationPanel。
- 演示模式重点突出 Agent 工作流过程、自动修复高光时刻、最终质量评分、插件参与情况和 Markdown 报告结果；后端未流式返回时采用运行完成后的阶段回放展示。
- Vue 前端已支持生产构建，新增 `frontend-vue/.env.production`、`frontend-vue/Dockerfile` 和 `frontend-vue/nginx.conf`。
- FastAPI Agent Engine 已支持作为独立 Docker Compose 服务 `ai-agent-api` 启动，端口为 `8001`。
- Docker Compose 已支持多服务启动：Streamlit v1 演示版、FastAPI Python Agent Engine API、Vue3 + Nginx 前端、Java Spring Boot 平台服务层。
- `backend-java` 已作为 v2.0 第九阶段最小骨架加入，当前只做 API Gateway / Proxy，不接数据库、不做登录权限、不保存状态。
- Java 层当前代理 `GET /health`、`GET /models`、`GET /plugins`、`POST /runs`、`GET /runs`、`GET /runs/{run_id}`、`GET /reports` 和 `GET /reports/{report_name}`，后续可扩展用户系统、权限控制、任务队列、配置中心、数据库存储和团队协作。
- v2.0 第十阶段已让 Vue 支持 Python Direct 和 Java Gateway 两种 API 调用模式：过渡期推荐 Python Direct 便于调试，平台化扩展推荐 Java Gateway 承接任务管理、权限和配置中心能力。
- v2.0 第十一步已让 Java 平台服务层增加任务记录和配置管理雏形：`POST /api/runs` 会保存 `RunRecord`，新增 `/api/platform/runs` 查询平台记录，新增 `/api/settings` 保存前端设置。
- v2.0 第十二步已接入 MySQL 持久化：Java 平台运行记录、前端配置、模型配置和插件配置通过 JPA 保存到 MySQL；Python Agent Engine 仍负责 AI 工作流，`reports/` 与 `runs/` 文件仍保留用于大文本产物存储。
- v2.0 第十三步已让 Vue 接入 Java + MySQL 数据视图：`VITE_API_MODE=java` 时，History 优先读取 `/api/platform/runs`，Settings 同步 `/api/settings`，Models 和 Plugins 读取 Java/MySQL 配置；`VITE_API_MODE=python` 时保持 Python Direct 与 localStorage 逻辑。
- v2.0 第十四步已增强 Java + MySQL 任务记录详情和报告索引管理：`RunRecordEntity` 保存运行摘要、UI ViewModel、插件结果摘要、错误摘要、模型信息和审批字段；新增 `ReportIndexEntity`、`/api/platform/reports`、`/api/platform/stats`，Vue Reports 和 Dashboard 已接入平台报告索引与统计视图。
- v2.0 第十五步已新增 C++ Runner Sandbox 最小可运行版本：`runner-cpp/` 支持任务 JSON、危险关键词扫描、调用 Python 执行目标文件和 JSON 结果输出；Python `code_runner` 通过 `runner_mode=cpp` 可选接入，未编译 runner 时自动回退 Python Runner。
- v2.0 第十六步已完成多服务 Docker Compose 总集成：`mysql`、`ai-agent-api`、`backend-java`、`frontend-vue`、`streamlit-web` 可通过 `docker compose up --build` 一起启动，C++ Runner 作为挂载目录和本地可选增强模块保留。
- 技术框架扩展落地第二步已新增 Java 平台任务事件记录：`RunEventEntity` 保存任务创建、状态变化、Python 请求/响应、成功失败、报告索引和异常事件，Vue History 展示事件时间线，Dashboard 展示最近平台事件，为后续 SSE/WebSocket 实时日志、运行回放和平台审计打基础。
- 技术框架扩展落地第三步已新增 SSE 实时事件推送雏形：`RunEventSseService` 管理任务订阅者，`GET /api/platform/runs/{platformRunId}/events/stream` 通过 `text/event-stream` 推送 Java 平台事件，Vue RunConsole 和 RunHistory 可订阅实时事件流。
- 技术框架扩展落地第四步已新增 Python Agent Engine 细粒度事件上报：Python 工作流输出 `workflow_events`，Java 平台层保存为 `RunEventEntity` 并通过已有 SSE 机制推送，Vue 可展示 Product/Coder/Tester/Runner/Sentry/Quality/Report 等 Agent 事件。
- 技术框架扩展落地第五步已新增工作流回放功能：Java 提供 `GET /api/platform/runs/{platformRunId}/replay`，Vue 新增 `/replay/:platformRunId` 页面，支持基于 MySQL 事件记录逐步回放工作流。
- 技术框架扩展落地第六步已新增 Agent 注册中心与 Prompt 模板管理：Python Agent Engine 提供 `agent_registry/` 和 `prompts/`，FastAPI `/agents`、Java `/api/agents`、Vue `/agents` 已可查看 Agent 元信息。
- 技术框架扩展落地第七步已新增 Workflow 模板管理：Python Agent Engine 提供 `workflow_templates/` 和 `/api/workflows/templates`，Vue 新增 `/workflows/templates` 页面，可查看模板、模板 Markdown、Agent 顺序和阶段顺序，并生成轻量模板任务视图；Java Gateway 通过 `/api/workflows/templates` 和 `/api/workflows/instantiate` 保持代理兼容。
- 技术框架扩展落地第八步已新增 Vue 可视化工作流拖拽编辑器：Vue 新增 `/workflows/editor` 页面，支持从 Agent Palette 拖入节点、调整节点位置和执行顺序、编辑输入输出字段和阶段、加载模板、本地保存模板、Java/MySQL 保存自定义模板、模板详情预览、MySQL 模板删除、MySQL 模板生成可回放任务、导出 JSON，并通过现有 Workflow instantiate API 生成轻量任务视图。
- 已新增简化 CodeAgent 执行模块：Python 提供 `/api/code-agent/execute`，支持 `read_file`、`write_file`、`list_files`；Java Gateway 提供 `/api/code-agent/execute` 并将 CodeAgent 事件写入 MySQL `run_event`、通过 SSE 推送；Vue Workflow Editor 可选中 CodeAgent 节点后触发文件操作。
- 页面暂不实现复杂动画；后续逐步替代 Streamlit 的正式交互体验。

## 为什么当前要先保留 Streamlit

- v1.0 比赛稳定：Streamlit 部署简单，现场问题少。
- 开发成本低：当前团队可以快速完成 UI、运行、日志和报告展示。
- 快速演示：不需要前后端联调，也不需要额外构建步骤。
- 后续可替换为 Vue：当前已经抽离 `ui_view_model` 和 `run_service`，未来可以用 Vue 前端替换展示层，而不重写 LangGraph 核心。

换句话说，Streamlit 是 v1.0 的演示前端，不是系统架构的终点。

## 升级路线

### 阶段 1：FastAPI 包装 Python Agent Engine

- 已将 `services/run_service.py` 暴露为 HTTP API。
- 已对齐 `docs/API_CONTRACT.md`。
- 保留 Streamlit 作为比赛演示和本地备用入口。

### 阶段 2：Vue3 + TS 实现正式前端

- 已使用 Vue3 + TypeScript 搭建 `frontend-vue/` 骨架。
- 已直接消费 API 返回的 `run_summary` 和 `ui_view_model` 渲染 Dashboard 统计、摘要、工作流节点、结果详情、历史详情、Agent 输出、插件结果和报告入口。
- 已提供前端侧模型和插件配置管理；当前配置通过 localStorage 保存，后续可升级为 Java 后端统一配置管理。
- 已提供比赛演示模式，面向答辩现场突出多 Agent 协作、自愈修复、质量评分和报告生成。
- 已支持 `npm run build` 生产构建，并通过 Nginx 支持 Vue Router history 路由回退。
- 已通过 Docker Compose 将 `frontend-vue`、`backend-java` 和 `ai-agent-api` 作为 v2 预览服务联调，同时保留 `streamlit-web` 的 Streamlit v1 服务。
- 已通过 `.env.development` / `.env.production` 支持 `VITE_API_MODE=python|java`：`python` 模式直连 FastAPI，`java` 模式通过 Spring Boot API Gateway 代理；页面组件不直接处理 API 路径差异。
- 已在 Dashboard、History、Models、Plugins 页面展示当前数据模式和数据来源；Java Gateway 模式下展示 MySQL 平台运行记录和持久化配置视图。
- Reports 页面在 Java Gateway 模式下优先展示 MySQL 报告索引，并在详情中显示 platformRunId、pythonRunId、需求摘要、成功状态、质量评分和 Markdown 正文。
- Dashboard 在 Java Gateway 模式下优先读取 `/api/platform/stats`，展示 MySQL 运行统计、报告索引数量、自动修复数量和测试通过数量。
- 后续增加更自然的时间轴动画、模型对比表格和更完整的报告阅读体验。

### 阶段 3：Java Spring Boot 接入任务管理

- 已新增 `backend-java/` 最小 Spring Boot 3.x 骨架。
- 当前 Java API 负责平台层入口和 Python Agent Engine 代理，不替换现有 Python FastAPI。
- 当前已提供 `/api/health`、`/api/agent/health`、`/api/models`、`/api/plugins`、`/api/runs`、`/api/reports`、`/api/reports/{reportName}`、`/api/platform/runs`、`/api/platform/runs/{platformRunId}`、`/api/settings`。
- 当前已新增 `RunRecordService`、`SettingsService`、`ApiResponse` 和全局异常处理，Java 层开始承担任务记录、前端配置保存和平台接口统一响应。
- 当前已新增 JPA 实体与 Repository：`RunRecordEntity`、`FrontendSettingsEntity`、`ModelConfigEntity`、`PluginConfigEntity`，数据保存到 MySQL。
- 当前 `/api/models` 和 `/api/plugins` 已优先返回 MySQL 配置表数据，表为空时回退 Python Agent Engine 配置。
- 当前已新增 `ReportIndexEntity`、`ReportIndexRepository`、`ReportIndexService` 和平台报告接口，用于保存报告索引并关联 platformRunId / pythonRunId。
- 当前已新增 `/api/platform/stats`，从 MySQL 聚合运行总数、成功失败数、平均质量评分、测试通过数、自动修复数和报告数量。
- 当前已新增 `RunEventEntity`、`RunEventRepository`、`RunEventService` 和 `/api/platform/runs/{platformRunId}/events`、`/api/platform/events/recent`，记录 Java 平台层可观察任务事件。
- 当前已新增 `RunEventSseService` 和 `/api/platform/runs/{platformRunId}/events/stream`，作为 SSE 实时事件流预留接口；后续可升级为 WebSocket、实时 Agent 日志和运行回放。
- 当前 Java 会从 Python `state.workflow_events` 或 `ui_view_model.workflow_events` 提取细粒度工作流事件并保存到 MySQL，不改变 Python Agent 输出内容和 LangGraph 分支逻辑。
- 当前已新增工作流回放 API 和 Vue 回放页，复用 `RunRecordEntity` 与 `RunEventEntity`，用于比赛演示、问题复盘和调试分析。
- 当前 Python Agent Engine 已开始从函数式 Agent 走向注册式 Agent 管理；Prompt 逐步从代码硬编码迁移到 `prompts/` Markdown 模板，便于后续调优和可视化编排。
- 当前 Python Agent Engine 已开始支持 Workflow 模板管理；模板只描述可复用流程和生成轻量任务视图，不改变默认 LangGraph 主流程。
- 当前数据流是 Vue Workflow Editor → Java Gateway 或 Python Direct → Workflow instantiate API → 返回 `run_summary` / `ui_view_model` 任务视图。Java Gateway 模式下，自定义模板也可以通过 `/api/platform/workflows/templates` 保存到 MySQL，并通过 `/api/platform/workflows/templates/{templateKey}/instantiate` 生成可回放平台任务。当前不会让自定义模板直接驱动 LangGraph 分支，后续如需动态编排必须先确认模板协议和安全边界。
- 当前 Dashboard 和 History 会将 `runnerMode=workflow_template` 的记录标记为“模板回放”，与真实 Agent 运行、CodeAgent 文件操作区分，避免比赛讲解时混淆“回放任务”和“真实 LangGraph 执行”。
- CodeAgent 数据流是 Vue Workflow Editor → Java Gateway 或 Python Direct → Python CodeAgent 文件操作 → 事件返回；Java Gateway 模式下事件进入 RunEvent + SSE + Replay，不需要修改 LangGraph 主流程。
- `model_config` 和 `plugin_config` 表为空时会初始化 DeepSeek、Qwen、GLM 以及 Doc/Security/Refactor/UI Agent 默认配置。
- 后续增加用户、权限、任务队列、配置中心、审计、团队协作和更完整的运行记录管理。

### 阶段 4：C++ Runner Sandbox 增强安全执行

- 已新增 `runner-cpp/` 最小 CMake 工程。
- 当前 Runner 是命令行程序，输入 `task.json`，输出 JSON 执行结果。
- 已实现危险关键词扫描和 Windows 优先的 Python 进程执行。
- Python `utils/cpp_runner_adapter.py` 负责发现 `runner.exe`、生成任务 JSON、解析结果和 fallback。
- 默认仍使用 Python Runner；只有 `config/settings.yaml` 设置 `runner_mode: cpp` 时才尝试调用 C++ Runner。
- 后续增加更强的进程隔离、资源限制、文件访问控制和危险操作拦截。

### 阶段 5：Docker Compose 多服务部署

- 使用 Docker Compose 编排：
  - `frontend-vue`
  - `backend-java`
  - `ai-agent-api`
  - `streamlit-web`
  - `mysql`
  - `runner-cpp` 挂载目录
- 统一环境变量、网络、端口和数据卷。
- 当前 C++ Runner 采用方案 A，不单独作为服务启动；后续可升级为 `cpp-runner` 独立服务或构建阶段。
- 保留 v1.0 单容器启动作为比赛演示备用方案。

## 兼容原则

- v1.0 Streamlit 演示入口不依赖新增 Vue 前端。
- Vue 前端独立位于 `frontend-vue/`，不修改 LangGraph 核心和 v1.0 启动链路。
- v1.0 不改变 Streamlit 启动方式。
- v1.0 不破坏 CLI、Docker、插件系统、报告和历史记录。
- v2.0 升级优先复用 `run_service`、`run_summary` 和 `ui_view_model`。
- Python LangGraph 核心保持为 Agent Engine 的稳定内核。

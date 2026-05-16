# v2.0 多技术栈架构预留规划

本文用于规划项目从 v1.0 比赛演示版升级到 v2.0 多技术栈平台版的路线。当前阶段已新增 Python Agent Engine API 服务层和独立 Vue3 + TypeScript 前端骨架，但不新增 Java、C++ 工程代码，不影响 v1.0 Streamlit 演示稳定性。

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
- 后续增加更自然的时间轴动画、模型对比表格和更完整的报告阅读体验。

### 阶段 3：Java Spring Boot 接入任务管理

- 增加用户、权限、任务、审计和运行记录管理。
- Java API 负责平台层，Python Agent Engine 负责 AI 工作流。
- Java 后端通过 API 调用 Python 服务。

### 阶段 4：C++ Runner Sandbox 增强安全执行

- 将代码运行从 Python subprocess 逐步迁移到更隔离的 Runner Sandbox。
- 增加超时、资源限制、文件访问控制和危险操作拦截。
- Runner 返回标准化执行结果给 Python Agent Engine。

### 阶段 5：Docker Compose 多服务部署

- 使用 Docker Compose 编排：
  - `frontend-vue`
  - `backend-java`
  - `agent-engine-python`
  - `runner-sandbox-cpp`
- 统一环境变量、网络、端口和数据卷。
- 保留 v1.0 单容器启动作为比赛演示备用方案。

## 兼容原则

- v1.0 Streamlit 演示入口不依赖新增 Vue 前端。
- Vue 前端独立位于 `frontend-vue/`，不修改 LangGraph 核心和 v1.0 启动链路。
- v1.0 不改变 Streamlit 启动方式。
- v1.0 不破坏 CLI、Docker、插件系统、报告和历史记录。
- v2.0 升级优先复用 `run_service`、`run_summary` 和 `ui_view_model`。
- Python LangGraph 核心保持为 Agent Engine 的稳定内核。

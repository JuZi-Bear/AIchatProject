# v2.0 多技术栈架构预留规划

本文用于规划项目从 v1.0 比赛演示版升级到 v2.0 多技术栈平台版的路线。当前阶段只做架构预留和文档说明，不新增 Vue、TypeScript、Java、C++ 代码，不影响 v1.0 Streamlit 演示稳定性。

## v1.0 当前架构

v1.0 目标是稳定完成比赛演示，强调“可运行、可展示、可复盘”。

- Python：项目主语言，承载 Agent、工作流、测试、运行、报告和 Web UI。
- LangGraph：多 Agent 状态机，负责 Product、Coder、Tester、Approval、Runner、Sentry、Plugins、Quality、Report 等节点编排。
- Streamlit：v1.0 Web UI 演示前端，负责案例选择、运行控制、工作流可视化、报告和历史记录展示。
- Docker：固定 Python 运行环境，降低跨设备部署风险。
- 插件系统：通过 `plugins/` 和 `config/agents.yaml` 支持 Doc、Security、Refactor、UI 等自定义 AI 模块。
- run_summary：统一运行摘要，供 CLI、Web UI、报告和模型对比复用。
- ui_view_model：统一 UI 数据层，让页面优先读取展示结构而不是反复解析原始 state。
- run_service：Application Service 层，封装创建运行、读取历史、查询报告、模型和插件，为未来 API 层预留统一调用入口。

当前架构可以概括为：

```text
Streamlit Web UI / CLI
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
- 提供 FastAPI 或其他 HTTP API 包装 `services/run_service.py`。
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
  调用 Java API：POST /runs

Java Spring Boot
  做鉴权、任务登记、审计
  转发到 Python Agent Engine

Python Agent Engine
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

v2.0 前端和 Java 后端都应围绕以下统一返回结构设计：

```json
{
  "state": {},
  "run_summary": {},
  "ui_view_model": {}
}
```

其中：

- `state`：完整运行状态，主要用于调试和历史回放。
- `run_summary`：列表、卡片、报告和模型对比的核心摘要。
- `ui_view_model`：前端展示优先消费的数据结构。

## 为什么当前要先保留 Streamlit

- v1.0 比赛稳定：Streamlit 部署简单，现场问题少。
- 开发成本低：当前团队可以快速完成 UI、运行、日志和报告展示。
- 快速演示：不需要前后端联调，也不需要额外构建步骤。
- 后续可替换为 Vue：当前已经抽离 `ui_view_model` 和 `run_service`，未来可以用 Vue 前端替换展示层，而不重写 LangGraph 核心。

换句话说，Streamlit 是 v1.0 的演示前端，不是系统架构的终点。

## 升级路线

### 阶段 1：FastAPI 包装 Python Agent Engine

- 将 `services/run_service.py` 暴露为 HTTP API。
- 对齐 `docs/API_CONTRACT.md`。
- 保留 Streamlit 作为备用演示入口。

### 阶段 2：Vue3 + TS 实现正式前端

- 使用 Vue3 + TypeScript 实现 Dashboard。
- 直接消费 `ui_view_model` 渲染 Header、Summary、Timeline、Result、Tabs、Report 和 History。
- 增加更自然的时间轴动画和模型对比表格。

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

- v1.0 不新增实际 Vue、Java、C++ 工程代码。
- v1.0 不改变 Streamlit 启动方式。
- v1.0 不破坏 CLI、Docker、插件系统、报告和历史记录。
- v2.0 升级优先复用 `run_service`、`run_summary` 和 `ui_view_model`。
- Python LangGraph 核心保持为 Agent Engine 的稳定内核。

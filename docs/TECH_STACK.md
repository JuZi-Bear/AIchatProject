# 技术栈说明

## 当前已落地技术栈

v1.0 比赛交付版已经落地的技术栈如下：

- Python 3.11：核心开发语言。
- DeepSeek / Qwen / GLM：国产大模型服务商。
- OpenAI SDK 兼容接口：统一模型调用方式。
- LangGraph：多 Agent 状态机。
- Streamlit：比赛演示 Web UI。
- FastAPI：Python Agent Engine API 服务层。
- workflow_events：Python Agent Engine 生成的细粒度工作流事件结构。
- Agent Registry：Python 侧统一管理 Agent 元信息，为可视化编排和 Agent 扩展提供基础。
- prompts/：Markdown Prompt 模板目录，用于管理 Product、Coder、Tester、Sentry 等 Agent Prompt。
- workflow_templates/：Workflow 模板目录，用于管理可复用流程、Agent 顺序、阶段顺序和模板 Markdown 描述。
- Simple CodeAgent：Python 提供受控 `read_file`、`write_file`、`list_files` 项目文件操作，支持 `config/settings.yaml` 路径白名单和 JSONL 审计日志，并输出兼容 RunEvent 的 Agent 事件。
- Java 17：v2.0 平台服务层运行时。
- Spring Boot 3.x：Java API Gateway 和后续平台服务框架。
- SSE：Java 平台层通过 `SseEmitter` 向 Vue 推送任务事件流，后续可升级 WebSocket。
- 工作流回放：Java 读取 MySQL 事件记录并提供 replay API，Vue 负责逐步回放可视化。
- Maven：Java 服务构建工具。
- Vue3 + TypeScript：v2.0 前端预览项目。
- Vite：Vue 前端开发和构建工具。
- Vue Router：Vue 前端页面路由。
- Pinia：Vue 前端状态管理。
- Axios：Vue 前端 API 调用封装。
- Element Plus：Vue 前端 UI 组件库。
- Rich：CLI 彩色输出。
- pytest：自动测试。
- coverage：测试覆盖率统计。
- Docker / docker-compose：固定部署环境。
- PyYAML：读取模型、插件和默认配置。
- python-dotenv：读取 API Key 和运行环境变量。
- Markdown 报告：运行结果归档。
- 插件系统：扩展 Doc、Security、Refactor、UI 等 AI 模块。
- run_summary：统一运行摘要。
- ui_view_model：统一 UI 展示数据结构。
- run_service：Application Service 层，统一工作流调用和查询入口。
- Java API Gateway：当前通过 `backend-java` 代理 Python Agent Engine，并通过 MySQL 持久化任务记录、任务状态、任务事件、报告索引、平台统计和前端配置管理雏形，后续承接任务管理、权限控制和配置中心。
- MySQL 8.0：Java 平台服务层数据库，用于任务记录、任务状态、任务事件、运行摘要、UI ViewModel、插件结果摘要、报告索引、前端配置、模型配置和插件配置。

## v2.0 已落地前端能力

- `frontend-vue/`：独立 Vue3 + TypeScript 前端，不影响 v1.0 Streamlit。
- `src/api/`：通过 Axios 调用后端 API，并通过 `VITE_API_MODE` 选择直连 Python Agent Engine 或经由 Java Gateway；Java 模式下 runs/history、reports、settings、models、plugins 优先读取 Java/MySQL 数据视图。
- `src/stores/settings.ts`：通过 Pinia + localStorage 保存前端默认模型、插件开关和运行参数；Java Gateway 模式下优先同步 `/api/settings`，由 Java 保存到 MySQL，失败时回退 localStorage。
- `src/types/model.ts` / `plugin.ts` / `settings.ts`：定义模型、插件和前端配置类型。
- `src/types/run.ts` / `platformRun.ts`：定义 Python 运行结果、`ui_view_model` 和 Java 平台运行记录类型。
- `src/types/agent.ts`：定义 Agent 注册中心元信息类型。
- `src/types/workflow.ts`：定义 Workflow 模板和模板实例化响应类型。
- `DashboardStats` / `RecentRuns` / `RecentReports` / `ModelStatusPanel` / `PluginStatusPanel` / `QuickActions`：组成平台总览 Dashboard，展示运行统计、最近记录、模型状态、插件状态和快捷入口。
- `DemoHero` / `DemoWorkflowStage` / `RepairHighlight` / `DemoResultSummary` / `DemoNarrationPanel`：组成比赛演示模式，突出 Agent 流程、自愈修复、质量评分和报告结果。
- `WorkflowTimeline`：基于 `ui_view_model.workflow_steps` 展示 Agent 工作流。
- `SummaryCards`：基于 `run_summary` 展示成功状态、修复次数、测试、覆盖率、质量评分和报告路径。
- `ResultOverview`：展示 run_id、用户需求、错误摘要和最终结果。
- `AgentOutputTabs`：展示 Product、Coder、Tester、Sentry、Plugins、Report 和 Raw JSON。
- `PluginResultPanel`：优先展示 `plugin_results`，兼容 `doc_result`、`security_result`、`refactor_result`、`ui_result`。
- `ReportPreview`：展示报告路径并支持折叠查看完整 Markdown 报告。
- `RunHistory`：支持历史运行列表、成功/失败筛选、模型筛选、需求搜索、倒序排序和详情复用 `ui_view_model` 展示。
- `Agents`：支持查看 Agent 注册中心、按 stage 筛选和按名称搜索。
- `WorkflowTemplates`：支持查看 Workflow 模板、搜索筛选模板、查看模板 Markdown，并生成轻量模板任务视图。
- `WorkflowEditor`：支持 Agent Palette、拖拽画布、节点位置调整、顺序调整、属性编辑、Pinia 状态管理、本地模板保存、Java/MySQL 模板保存、模板详情预览、MySQL 模板删除、JSON 导出和模板任务视图实例化。
- `CodeAgentPanel`：Workflow Editor 中选中 CodeAgent 节点后可触发 read/write/list 文件操作，并显示操作摘要、返回内容、文件列表和事件时间线。
- `Reports`：支持 Markdown 报告列表、报告名搜索、run_id 解析、内容查看和复制报告内容。
- `Models`：支持模型列表、provider/启用状态筛选、模型搜索、API Key 提示和前端默认模型选择。
- `Plugins`：支持插件卡片、启用/关闭开关、插件说明和本地启用状态管理。

## v2.0 API 调用模式

- FastAPI 负责 Python Agent Engine，提供 `/health`、`/models`、`/plugins`、`/agents`、`/api/workflows/templates`、`/api/workflows/instantiate`、`/api/code-agent/execute`、`/runs` 和 `/reports`。
- Spring Boot 负责平台 API Gateway，提供 `/api/agent/health`、`/api/models`、`/api/plugins`、`/api/agents`、`/api/workflows/templates`、`/api/workflows/instantiate`、`/api/code-agent/execute`、`/api/runs`、`/api/reports`、`/api/platform/runs` 和 `/api/settings`。
- Vue 通过环境变量选择调用模式：`VITE_API_MODE=python` 时使用 `VITE_PYTHON_API_BASE_URL`，`VITE_API_MODE=java` 时使用 `VITE_JAVA_API_BASE_URL`。
- `client.ts` 统一处理 health 路径差异，页面组件只调用封装后的 API 方法。

## v2.0 已落地 Java 平台服务层

- `backend-java/`：Java Spring Boot 3.x 平台服务骨架。
- Java 17 + Maven：用于构建和运行平台服务。
- `PythonAgentClient`：通过 Spring `RestClient` 调用 Python FastAPI Agent Engine。
- `AgentController`：提供 `/api/agents`，代理 Python Agent 注册中心。
- `WorkflowController`：提供 `/api/workflows/templates` 和 `/api/workflows/instantiate`，代理 Python Workflow 模板管理接口。
- `PlatformWorkflowController` / `WorkflowTemplateService` / `WorkflowTemplateEntity`：提供 `/api/platform/workflows/templates`，将 Vue Workflow Editor 自定义模板保存到 MySQL，并支持详情查询、覆盖保存版本递增和删除。
- `CodeAgentController`：提供 `/api/code-agent/execute`，代理 Python CodeAgent 文件操作，并把返回事件写入 `RunEventEntity`。
- `RunService`：代理运行创建、历史列表和历史详情，并在创建运行后写入 Java 平台记录。
- `RunRecordService` / `RunRecordEntity`：使用 Spring Data JPA 保存平台运行记录到 MySQL，并保存 Python `RunResponse` 的 `rawResponse` 供 Vue 历史详情复用 `ui_view_model`。
- `RunEventService` / `RunEventEntity`：使用 Spring Data JPA 保存任务生命周期事件，包括任务创建、状态变化、Python 请求/响应、成功失败、报告索引、异常事件和 Python `workflow_events`。
- `RunEventSseService`：使用 Spring MVC `SseEmitter` 管理任务事件订阅者，把新增任务事件实时推送给 Vue。
- `ReportIndexService` / `ReportIndexEntity`：使用 Spring Data JPA 保存报告索引，关联 platformRunId、pythonRunId、需求摘要、成功状态和质量评分。
- `PlatformStatsService`：从 MySQL 聚合平台统计数据，支持 Dashboard 展示总运行数、成功失败数、平均质量评分、报告数、测试通过数和自动修复数。
- `SettingsService` / `FrontendSettingsEntity`：使用 Spring Data JPA 保存当前前端配置到 MySQL。
- `ModelConfigEntity` / `PluginConfigEntity`：为模型配置和插件配置建立 MySQL 表，启动时为空则初始化默认数据。
- `RunRecordRepository` / `FrontendSettingsRepository` / `ModelConfigRepository` / `PluginConfigRepository`：JPA Repository 层。
- `ApiResponse`：新增平台接口统一响应结构。
- `GlobalExceptionHandler`：统一处理 Java 常见异常，避免把长堆栈直接返回给前端。
- `HealthController`：提供 `GET /api/health`。
- `RunProxyController`：提供 `/api/agent/health`、`/api/runs`、`/api/runs/{runId}`、`/api/reports` 和 `/api/reports/{reportName}`。
- `PlatformRunController`：提供 `/api/platform/runs`、`/api/platform/runs/{platformRunId}`、`/api/platform/runs/{platformRunId}/cancel` 和 `/api/platform/runs/{platformRunId}/events`。
- `PlatformEventController`：提供 `/api/platform/events/recent`。
- `RunEventSseController`：提供 `/api/platform/runs/{platformRunId}/events/stream` 的 SSE 事件流。
- `PlatformRunController`：额外提供 `/api/platform/runs/{platformRunId}/replay`，组合任务基础信息、事件列表、运行摘要和 UI ViewModel。
- `PlatformReportController`：提供 `/api/platform/reports`、`/api/platform/reports/{reportName}` 和 `/api/platform/runs/{platformRunId}/reports`。
- `PlatformStatsController`：提供 `/api/platform/stats`。
- `SettingsController`：提供 `/api/settings` 的读取和覆盖保存。
- `ModelController` / `PluginController`：优先返回 MySQL 中的模型和插件配置，表为空时回退代理 Python 配置。
- `AgentEngineProperties`：通过 `AGENT_ENGINE_BASE_URL` 或 `application.yml` 配置 Python Agent Engine 地址。
- `CorsConfig`：允许 Vue 开发端口 `5173` 和生产端口 `5174` 访问 Java API。

## v2.0 已落地 C++ Runner Sandbox

- `runner-cpp/`：C++17 + CMake 最小 Runner Sandbox 工程。
- `SecurityScanner`：扫描 `os.remove`、`shutil.rmtree`、`subprocess`、`eval(`、`exec(`、`socket`、`requests`、`urllib`、`open(`、`pathlib.Path.unlink` 等危险关键词。
- `SandboxRunner`：Windows 优先，通过进程执行目标 Python 文件，返回 JSON 结果。
- `utils/cpp_runner_adapter.py`：Python 适配层，查找 `runner.exe`、生成任务 JSON、调用 C++ Runner、解析输出。
- `config/settings.yaml`：新增 `runner_mode: python|cpp`，默认 `python` 保持兼容。
- `run_summary`：新增 `runner_mode` 和 `runner_warning`，前端轻量展示当前 Runner 和 fallback 提示。

## Docker Compose 多服务角色

- `mysql`：MySQL 8.0 平台数据库，保存 Java 平台运行记录、任务状态、任务事件、报告索引、配置和统计数据。
- `ai-agent-api`：Python FastAPI Agent Engine 容器，负责 Agent 工作流 API。
- `backend-java`：Spring Boot 平台服务容器，负责 Java Gateway、MySQL 数据视图和平台接口。
- `frontend-vue`：Vue3 生产构建容器，使用 Nginx 托管静态文件，默认通过 Java Gateway 调用。
- `streamlit-web`：Streamlit v1 演示版容器，保留比赛现场稳定入口。
- `runner-cpp`：当前不是独立服务，而是挂载到 Python 容器的可选增强目录；后续可升级为独立 Runner 服务或构建阶段。

## 后续扩展技术栈

v2.0 平台化升级继续预留的技术栈如下：

- Java Spring Boot：当前已作为 API Gateway + MySQL 平台配置 + 任务记录雏形落地，后续负责用户、权限、任务、审计和系统集成。
- C++ Runner Sandbox：当前已落地最小命令行版本，后续增强为更强隔离的安全执行环境。
- Docker Compose 多服务编排：统一启动前端、Java 后端、Python Agent Engine 和 Runner Sandbox。

## 技术作用边界

- Streamlit：仅作为 v1.0 比赛演示前端，优势是启动快、部署简单、适合现场演示。
- Vue3 + TypeScript：v2.0 正式前端方向，当前已支持 Dashboard 总览、比赛演示模式、工作流可视化、工作流回放、细粒度 Agent 事件时间线、历史记录、结果详情、模型默认选择、插件状态管理、报告查看、API 调用模式切换和 Java/MySQL 数据视图。
- Vue Canvas + Pinia：Workflow Editor 当前使用 HTML5 Drag/Drop、Pointer Events、SVG 连线和 Pinia Store 管理节点、连接、选中状态、undo/redo、本地模板保存、Java/MySQL 模板保存和 API 实例化。
- Python Agent Engine：长期保留，负责 LangGraph、多 Agent、模型调用、测试修复、质量评分、报告生成、`workflow_events` 生成、Agent 注册中心和 Prompt 模板管理，并通过 FastAPI 暴露 Agent Engine 接口。
- Workflow Templates：当前只管理模板元信息和 Markdown 描述，供 Vue 查看和轻量实例化，不直接改变默认 LangGraph 主流程。
- CodeAgent：当前是简化文件操作模块，不是完整 Codex；只操作项目目录内显式指定且通过白名单校验的路径，并输出 Agent 事件供 SSE 和回放消费。
- Java Spring Boot：v2.0 平台服务层，当前承担 API Gateway、MySQL 任务记录、任务事件、Python 工作流事件持久化、运行摘要、报告索引、平台统计、前端配置保存、模型配置和插件配置持久化，不替代 Agent Engine；后续处理用户、权限、任务管理和企业集成。
- C++ Runner Sandbox：当前已提供最小可运行命令行版本，不生成代码、不调用模型，只负责执行前安全扫描和运行 AI 生成代码；后续增强真实隔离。

## 技术栈扩展边界

- Python / LangGraph：继续负责 Agent Engine，不承接平台用户、权限和项目空间。
- Agent Registry：只管理 Agent 元信息，不直接改变 LangGraph 默认执行顺序。
- Prompt 模板：优先放在 `prompts/`，代码中只保留必要 fallback。
- FastAPI：继续作为 Python Agent Engine API 层，适合兼容扩展只读接口和服务适配。
- Streamlit：保留为 v1.0 稳定演示入口，不因 Vue 扩展而删除。
- Vue3 + TypeScript：后续承担平台工作台、配置管理、报告中心和运行统计，不直接依赖 LangGraph 内部 state。
- Java Spring Boot：后续承担任务生命周期、配置中心、统一错误响应、报告索引和平台统计；用户、权限、团队协作暂缓。
- MySQL：后续保存平台任务、任务事件、配置、报告索引和统计数据；不替代 Python yaml，除非用户确认。
- C++ Runner：后续增强执行安全；不替代 Python Runner，除非用户确认。
- Docker Compose：继续负责多服务部署；新增服务前应先更新 `DOCKER_COMPOSE_GUIDE.md` 和测试清单。

## 未来职责规划

- Java：从 Gateway 升级为平台服务层，优先做任务生命周期、任务事件记录、回放 API 和配置中心。
- SSE / WebSocket：当前先用 SSE 做单向任务事件推送，后续需要双向控制、多人协作或更高频日志时再升级 WebSocket。
- Vue：从结果展示升级为平台工作台，优先接入平台配置和运行统计。
- Workflow Editor：当前先作为前端模板编辑器，不直接改变 Python LangGraph；Java Gateway 模式已支持把自定义模板保存到 MySQL，后续可继续扩展版本管理和动态编排。
- Python：从单流程 Agent Engine 升级为可注册 Agent、Prompt 模板化和 Workflow 模板化的执行核心，并负责生成工作流事件。
- C++ / Docker：从最小 Runner 预览升级为更强隔离的执行安全层。
- MySQL：从基础记录表升级为任务、任务事件、工作流回放、配置、报告索引、审计事件的持久化基础。
- run_service：连接当前 Streamlit 和未来 API 层的应用服务边界。
- ui_view_model：连接后端结果和前端展示的稳定数据结构。

## Python 3.11

项目主语言，用于实现 Agent 调用、LangGraph 工作流、代码运行、测试执行、报告生成和 Web UI。

## DeepSeek / Qwen / GLM

国产大模型服务商。系统支持 DeepSeek、通义千问 Qwen 和智谱 GLM，方便比赛中展示国产模型能力和多模型对比。

## OpenAI SDK 兼容接口

不同模型通过 OpenAI SDK 的兼容接口调用，统一 client 创建方式，降低切换模型的复杂度。

## LangGraph

用于构建多 Agent 状态机。负责节点流转、条件分支、自动修复循环、人工审批和插件执行顺序。

## Streamlit

用于构建 Web UI。展示演示案例、模型选择、Agent 工作流、pytest 结果、质量评分、插件结果、运行历史和 Markdown 报告。

## Rich

用于 CLI 彩色输出，让命令行演示更清晰地区分 Product、Coder、Tester、Sentry 等 Agent 输出。

## pytest

Tester Agent 自动生成 pytest 测试文件，系统使用 pytest 验证生成代码是否满足需求。

## coverage

配合 pytest 统计测试覆盖率，并将覆盖率写入质量评分和运行报告。

## Docker

用于固定运行环境。Dockerfile 基于 `python:3.11-slim`，docker-compose 默认启动 Web UI，并挂载报告、运行历史和输出目录。

## PyYAML

用于读取 `config/settings.yaml`、`config/models.yaml` 和 `config/agents.yaml`，实现配置化管理。

## python-dotenv

用于读取 `.env` 中的 API Key、base_url、默认模型和离线模式配置，避免硬编码敏感信息。

## Markdown 报告

每次运行后自动生成 Markdown 报告，记录需求、模型、Agent 输出、测试结果、覆盖率、质量评分、插件结果、运行历史路径和错误摘要。

## Application Service 层

`services/run_service.py` 是当前新增的接口适配层。它封装创建运行、读取历史、读取报告、查询模型和查询插件等操作，统一返回 `state`、`run_summary` 和 `ui_view_model`。Streamlit 当前通过该服务层调用 AI 工作流，未来 FastAPI、Vue/TypeScript 或 Java 后端也可以复用同样的数据结构。

## 未来架构预留

- Python Agent Engine：继续保留 LangGraph 核心流程，负责多 Agent 编排、自动修复、测试、质量评分和报告生成。
- Streamlit：v1.0 比赛演示前端，适合快速展示和现场调试。
- FastAPI：当前已作为 Python Agent Engine API 层，将 `services/run_service.py` 暴露为 HTTP 接口。
- Vue3 + TypeScript：当前已作为 v2.0 前端预览，直接消费 `run_summary` 和 `ui_view_model` 渲染 Dashboard、演示模式、工作流、历史详情和报告查看，并通过环境变量选择 Python Direct 或 Java Gateway；Java 模式下优先读取 MySQL 平台运行记录、报告索引、统计数据和配置视图。
- Java Spring Boot：当前已新增 `backend-java/`，通过 REST 调用 Python Agent Engine，承担平台 API Gateway、MySQL 任务记录、运行摘要、报告索引、平台统计、前端配置、模型配置和插件配置管理；后续可作为 v2.0 平台服务层，负责用户、权限、任务队列、审计和企业系统集成。
- C++ Runner Sandbox：当前已作为 `runner-cpp/` 最小版本落地，可选增强代码运行边界；后续可升级为更强隔离的独立服务。

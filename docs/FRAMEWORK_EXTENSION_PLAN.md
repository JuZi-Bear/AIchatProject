# 技术框架扩展总规划

本文用于规划当前双轨并行架构之上的技术框架扩展方向。本阶段只做规划和边界定义，不新增复杂业务功能。

## 当前技术架构现状

- Python Agent Engine：负责 LangGraph 多 Agent 工作流、模型调用、测试、修复、质量评分和报告生成。
- FastAPI API 层：通过 `api_server.py` 将 Python Agent Engine 暴露为 HTTP API。
- Streamlit v1 演示层：通过 `webui.py` 保留比赛现场稳定演示入口。
- Vue3 + TypeScript 前端：通过 `frontend-vue/` 提供 v2 平台化前端预览。
- Java Spring Boot 平台服务层：通过 `backend-java/` 提供 Java Gateway、平台运行记录、配置和报告索引能力。
- MySQL 数据持久化：保存 Java 平台层运行记录、报告索引、模型配置、插件配置和前端设置。
- C++ Runner Sandbox：通过 `runner-cpp/` 提供可选安全执行器雏形。
- Docker Compose 多服务部署：通过 `docker-compose.yml` 编排 Vue、Java、MySQL、FastAPI 和 Streamlit。

## 当前架构优势

- v1.0 稳定演示：Streamlit 和 Python Direct 仍能作为比赛现场主入口。
- v2.0 平台化扩展：Vue、Java、MySQL 和 Docker Compose 已形成平台骨架。
- 多技术栈分层：前端、平台服务、Agent Engine、Runner 和持久化职责分离。
- AI 工作流与平台服务解耦：Java 不直接承载 LangGraph，Python Agent Engine 专注 AI 工作流。
- 前端可替换：Vue 可逐步替代 Streamlit，但 Streamlit 不被删除。
- Runner 可切换：Python Runner 默认稳定，C++ Runner 作为可选增强。
- 配置可迁移：yaml 仍作为 Python 兜底配置，Java/MySQL 可逐步承接平台配置。

## 当前架构不足

- Java 目前仍偏 Gateway，平台任务生命周期能力还不完整。
- Vue 与 Java 的平台能力仍可增强，尤其是配置、统计和任务管理闭环。
- MySQL 表结构仍是基础版本，缺少更规范的任务、事件、配置、审计模型。
- C++ Runner 仍是可选增强，不具备完整安全隔离。
- 缺少统一任务生命周期管理。
- 缺少统一用户 / 项目空间 / 权限系统。
- 缺少可视化工作流编辑能力。
- 缺少本地模型适配层。

## 第一阶段：平台服务层增强

### 目标

让 Java Spring Boot 从 Gateway 逐步升级为真正的平台服务层。

### 涉及技术栈

Java Spring Boot、Spring Validation、Spring Data JPA、MySQL、FastAPI Client。

### 需要修改的模块

`backend-java/`、`docs/`，必要时轻量扩展 `api_server.py` 或 `services/`。

### 方向

- Java 任务生命周期管理。
- 任务运行日志与事件记录：已落地最小版本，Java 平台层会记录任务创建、状态变化、Python 请求/响应、成功/失败、报告索引和异常事件。
- SSE 实时日志预留接口：已落地最小版本，Java 平台层可将任务事件通过 `text/event-stream` 推送给 Vue，后续可升级为 WebSocket、实时 Agent 日志和运行回放。
- Python Agent Engine 细粒度事件上报：已落地最小版本，Python 在 LangGraph 节点执行时生成 `workflow_events`，Java 保存后通过 SSE 推送给 Vue。
- 工作流回放功能：已落地最小版本，Java 基于 MySQL 中的运行记录和事件记录提供 replay API，Vue 支持逐步回放、多速度自动播放和事件高亮。
- Agent 注册中心与 Prompt 模板管理：已落地最小版本，Python 提供 `AgentMeta`、`AgentRegistry` 和 `prompts/` 模板目录，FastAPI/Java/Vue 可读取 Agent 元信息。
- Workflow 模板管理：已落地最小版本，Python 提供 `workflow_templates/` 模板注册和 Markdown 描述，FastAPI/Java/Vue 可读取模板并生成轻量任务视图。
- Vue 可视化工作流拖拽编辑器：已落地最小版本，Vue 提供 Agent Palette、拖拽画布、节点属性面板、模板加载、本地模板保存、JSON 导出和任务视图实例化。
- 简化 CodeAgent 执行模块：已落地最小版本，提供 `read_file`、`write_file`、`list_files` 三类项目文件操作，生成 `AGENT_STARTED` / `AGENT_FINISHED` / `AGENT_FAILED` 事件，并兼容 Java RunEvent、SSE 和 Vue 回放。当前已接入 Workflow Editor 与 RunConsole，Java Gateway 模式下会保存 CodeAgent 平台运行记录，便于 History / Replay 展示执行顺序。
- Java + MySQL 持久化增强。
- 报告索引管理。
- 配置中心。
- 统一错误响应。

### 风险

- 过早引入复杂状态机会增加平台服务复杂度。
- MySQL 表结构调整可能影响已有数据。
- Java 与 Python API 之间的契约必须稳定。

### 是否影响 v1.0

原则上不影响。v1.0 继续走 Python Direct 和 Streamlit。

### 是否适合现在做

适合。当前最推荐先做，但应先从任务生命周期、事件记录、SSE 实时事件流、Python 细粒度工作流事件、工作流回放、Agent 注册中心、Prompt 模板管理、Workflow 模板管理、Vue 可视化编辑器、简化 CodeAgent 文件操作和配置中心的最小增强开始。任务运行日志、SSE 预留接口、Python `workflow_events`、Vue 回放页、Agent 注册中心、Prompt 模板目录、Workflow 模板目录、Vue 拖拽编辑器和 CodeAgent 文件操作已经作为当前落地项完成，为后续 WebSocket 实时日志、运行回放、Prompt 调优和可视化编排打基础。

## 第二阶段：前端平台化增强

### 目标

让 Vue 从展示型前端升级为平台工作台。

### 涉及技术栈

Vue3、TypeScript、Element Plus、Pinia、Axios、Vue Router。

### 需要修改的模块

`frontend-vue/`、`docs/`，必要时配合 `backend-java/` 补接口。

### 方向

- Vue 工作台。
- 可视化工作流展示。
- 可视化工作流拖拽编辑器：已落地最小版本，当前只编辑前端模板视图，不改变后端默认执行流程。
- 模型配置管理。
- 插件配置管理。
- 报告中心。
- 运行统计。

### 风险

- 前端过早承载复杂配置会导致状态分散。
- 如果 Java API 不稳定，Vue 会出现兼容层膨胀。

### 是否影响 v1.0

不应影响。Vue 不删除 Streamlit。

### 是否适合现在做

适合做增强展示、配置接入和轻量拖拽编辑器。完整拖拽式工作流编辑器已完成前端最小版本，但后端保存、版本管理和真正动态 LangGraph 编排仍应后续谨慎推进。

## 第三阶段：AI Agent Engine 增强

### 目标

提升 Python Agent Engine 的可扩展性和可配置性。

### 涉及技术栈

Python、LangGraph、FastAPI、yaml 配置、模型 Provider 适配。

### 需要修改的模块

`services/`、`config/`、`api_server.py`，谨慎扩展 `core/`、`agents.py`、`plugins/`。

### 方向

- Agent 注册中心：已落地最小版本，当前管理 Product、Coder、Tester、Runner、Sentry、Plugins、Quality、Report 的元信息。
- Workflow 模板管理：已落地最小版本，当前提供 `simple_demo`、`full_agent_flow`、`repair_flow` 三个模板，支持通过 API 和 Vue 页面查看、筛选和生成模板任务视图。
- 多模型适配层。
- 本地模型接口预留。
- Prompt 模板管理：已落地最小版本，`prompts/` 管理 Product、Coder、Tester、Sentry 主要 Prompt，插件 Prompt 文件作为扩展入口保留。

### 风险

- 修改 Agent 或 LangGraph 主流程容易破坏 v1.0 稳定演示。
- Prompt 模板迁移可能改变输出行为。

### 是否影响 v1.0

可能影响，需要保持默认行为不变。

### 是否适合现在做

适合先做 Agent 注册中心、Prompt 模板和 Workflow 模板管理，不适合大改 LangGraph 主流程。当前 Workflow 模板只描述和实例化模板视图，不直接改变默认 LangGraph 执行路径。

## 第四阶段：执行安全增强

### 目标

增强 AI 生成代码执行过程的安全性、可控性和可观测性。

### 涉及技术栈

C++17、CMake、Python Runner、Docker、Windows 进程控制。

### 需要修改的模块

`runner-cpp/`、`utils/cpp_runner_adapter.py`、`utils/code_runner.py`、`config/settings.yaml`、`docs/`。

### 方向

- C++ Runner 正式接入。
- 执行器模式切换。
- 安全扫描策略。
- 超时与资源限制。
- Docker 沙箱预留。

### 风险

- 执行器切换可能影响 v1.0 演示稳定。
- C++ Runner 当前不是完整安全沙箱，不能夸大能力。

### 是否影响 v1.0

默认不影响。必须保留 Python Runner fallback。

### 是否适合现在做

适合继续增强，但不建议马上完全替代 Python Runner。

## 第五阶段：平台化能力

### 目标

将项目从单机演示平台升级为可多人使用的平台产品雏形。

### 涉及技术栈

Java Spring Boot、MySQL、Vue、认证授权框架、审计日志。

### 需要修改的模块

`backend-java/`、`frontend-vue/`、MySQL schema、`docs/`。

### 方向

- 用户系统。
- 项目空间。
- 团队协作。
- 权限控制。
- 审计日志。

### 风险

- 会显著增加业务复杂度。
- 容易偏离当前双轨稳定目标。

### 是否影响 v1.0

不应影响，但会增加 v2 平台复杂度。

### 是否适合现在做

暂不适合。应在平台服务层和前端工作台稳定后再做。

## 第六阶段：可视化编排

### 目标

让用户可视化配置 Agent 工作流和执行路径。

### 涉及技术栈

Vue3、图编辑组件、Java 配置服务、Python Workflow 模板。

### 需要修改的模块

`frontend-vue/`、`backend-java/`、`services/`、`config/`，谨慎涉及 `core/workflow.py`。

### 方向

- 前端拖拽式工作流：已落地 Vue 最小版本，支持 Agent Palette、画布拖拽、顺序调整、属性编辑、本地保存和实例化任务视图。
- Agent 节点配置。
- 条件分支配置。
- 执行记录回放。

### 风险

- 需要稳定的 Workflow 模板和节点协议。
- 过早实现会迫使 LangGraph 主流程大改。

### 是否影响 v1.0

若不改默认工作流，则不影响；若改 LangGraph 主流程，则风险较高。

### 是否适合现在做

不建议马上推进到“后端动态编排”。当前可继续完善前端编辑体验和模板 schema，但真正让编辑器驱动 LangGraph 分支前，需要先稳定 Agent 注册中心、Workflow 模板协议和平台配置中心。

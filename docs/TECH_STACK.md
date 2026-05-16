# 技术栈说明

## 当前已落地技术栈

v1.0 比赛交付版已经落地的技术栈如下：

- Python 3.11：核心开发语言。
- DeepSeek / Qwen / GLM：国产大模型服务商。
- OpenAI SDK 兼容接口：统一模型调用方式。
- LangGraph：多 Agent 状态机。
- Streamlit：比赛演示 Web UI。
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

## 后续扩展技术栈

v2.0 平台化升级预留的技术栈如下：

- FastAPI：将 Python Agent Engine 暴露为 HTTP API。
- Vue3 + TypeScript：正式前端 Dashboard。
- Java Spring Boot：平台服务层，负责用户、权限、任务、审计和系统集成。
- C++ Runner Sandbox：更强隔离的安全执行环境。
- Docker Compose 多服务编排：统一启动前端、Java 后端、Python Agent Engine 和 Runner Sandbox。

## 技术作用边界

- Streamlit：仅作为 v1.0 比赛演示前端，优势是启动快、部署简单、适合现场演示。
- Vue3 + TypeScript：后续正式前端，负责复杂交互、动画时间轴、组件化 Dashboard 和更专业的用户体验。
- Python Agent Engine：长期保留，负责 LangGraph、多 Agent、模型调用、测试修复、质量评分和报告生成。
- Java Spring Boot：后续平台服务层，不替代 Agent Engine，主要处理用户、权限、任务管理和企业集成。
- C++ Runner Sandbox：后续安全执行增强，不生成代码、不调用模型，只负责隔离运行 AI 生成代码。
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
- FastAPI：后续可作为 Python API 层，将 `services/run_service.py` 暴露为 HTTP 接口。
- Vue3 + TypeScript：后续可作为 v2.0 正式前端，直接消费 `ui_view_model` 渲染 Dashboard 和工作流页面。
- Java Spring Boot：后续可作为 v2.0 平台服务层，负责用户、权限、任务队列、审计和企业系统集成。
- C++ Runner Sandbox：后续可作为安全执行增强模块，用于更强隔离地运行 AI 生成代码。

# 技术框架扩展示意图

未来架构目标是让 Vue、Java、MySQL、FastAPI、LangGraph、Agent、Runner 各层职责清晰，同时保持 v1.0 Streamlit 稳定入口。

## 文本架构图

```text
Vue3 + TypeScript
↓
Java Spring Boot Platform
↓
MySQL / Config / Run Records
↓
FastAPI Python Agent Engine
↓
LangGraph Workflow
↓
Agent Registry / Plugin System
↓
Python Runner / C++ Runner / Docker Sandbox
```

## 各层职责

### Vue3 + TypeScript

- 平台前端和工作台。
- 展示 Dashboard、运行任务、历史记录、报告中心、模型和插件配置。
- 通过环境变量选择 Python Direct 或 Java Gateway。
- 后续可增强运行过程可视化和平台配置管理。

### Java Spring Boot Platform

- 平台服务层。
- 提供 API Gateway、任务生命周期、配置中心、报告索引、统计和统一错误响应。
- 后续可承接用户、项目空间、权限、审计和团队协作。
- 不直接承载 LangGraph 主流程。

### MySQL / Config / Run Records

- 保存平台运行记录、报告索引、配置和统计数据。
- Java Gateway 模式优先使用 MySQL。
- Python Direct 模式继续保留 yaml、`runs/` 和 `reports/` 兜底。

### FastAPI Python Agent Engine

- Python Agent Engine 的 API 层。
- 暴露模型、插件、运行、历史和报告接口。
- 不直接处理平台用户、权限和项目空间。

### LangGraph Workflow

- AI 工作流编排核心。
- 管理 Product、Coder、Tester、Runner、Sentry、Plugins、Quality、Report 等节点。
- 默认工作流必须保持 v1.0 稳定。

### Agent Registry / Plugin System

- Agent Registry 用于后续统一描述和发现 Agent。
- Plugin System 当前已支持 Doc、Security、Refactor、UI Agent。
- 后续扩展应保持插件协议兼容。

### Python Runner / C++ Runner / Docker Sandbox

- Python Runner 是默认稳定执行器。
- C++ Runner 是可选安全增强。
- Docker Sandbox 是未来更强隔离预留方向。
- 执行器切换必须可回退，不影响 v1.0 演示。

# 技术框架扩展示意图

当前与未来架构均以 v2 平台链路为主。

```text
Vue3 + TypeScript
↓
Java Spring Boot Platform
↓
MySQL / Config / Run Records / Run Events
↓
FastAPI Python Agent Engine
↓
LangGraph Workflow
↓
Agent Registry / Workflow Templates / Plugin System
↓
Python Runner / C++ Runner / Docker Sandbox
```

## 各层职责

- Vue：平台工作台、拖拽编辑器、实时事件、回放和报告中心。
- Java：Gateway、任务生命周期、配置中心、RunEvent、SSE、MySQL 持久化。
- MySQL：任务记录、事件、模板、报告索引和配置。
- FastAPI：Python Agent Engine API 层。
- LangGraph：多 Agent 工作流执行。
- Agent Registry：统一描述 Agent 元信息。
- Workflow Templates：保存和实例化工作流模板。
- Runner：默认 Python Runner，可选 C++ Runner，未来可扩展 Docker Sandbox。

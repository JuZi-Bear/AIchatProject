# v2-only Architecture

当前项目主链路：

```text
Vue3 + TypeScript
  -> Java Spring Boot Gateway
  -> FastAPI Python Agent Engine
  -> LangGraph / Agents / CodeAgent
  -> MySQL / reports / runs / output
```

## 职责

- Vue：Dashboard、RunConsole、Workflow Editor、Replay。
- Java：平台 API、配置、RunEvent、SSE、MySQL 持久化。
- Python：Agent Engine、工作流、模型、插件、报告。
- MySQL：平台记录、事件、模板和报告索引。
- Docker Compose：统一启动 v2 服务。

详细说明见 `docs/V2_ARCHITECTURE_PLAN.md` 与 `docs/FRAMEWORK_EXTENSION_ARCHITECTURE.md`。

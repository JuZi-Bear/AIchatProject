# Python Agent Engine API Contract

本文记录 v2.0 Python Agent Engine FastAPI 预览接口。API 层只负责 HTTP 请求/响应适配，业务逻辑统一调用 `services/run_service.py`，前端和 Java 后端优先消费 `run_summary` 与 `ui_view_model`，不直接耦合 LangGraph 内部 state。

启动方式：

```powershell
python -m uvicorn api_server:app --reload --host 127.0.0.1 --port 8001
```

默认地址：

```text
http://localhost:8001
```

本阶段也新增了 Java Spring Boot 平台服务层。Java 服务默认地址：

```text
http://127.0.0.1:8088/api
```

Docker Compose 模式下服务访问地址：

```text
Vue 前端: http://localhost:5174
Java 平台服务: http://localhost:8088/api/health
FastAPI Docs: http://localhost:8001/docs
MySQL: localhost:3306
```

容器网络内部调用关系：

```text
backend-java -> http://ai-agent-api:8001
backend-java -> jdbc:mysql://mysql:3306/aichat_platform
frontend-vue 生产构建默认调用 http://localhost:8088/api
```

Vue 可选择两种 API 调用方式，模式由 `frontend-vue/.env.*` 控制：

- 直接调用 Python Agent Engine：`http://127.0.0.1:8001`
- 通过 Java 平台服务代理：`http://127.0.0.1:8088/api`

```text
VITE_API_MODE=python
VITE_PYTHON_API_BASE_URL=http://127.0.0.1:8001
VITE_JAVA_API_BASE_URL=http://127.0.0.1:8088/api
```

生产构建默认推荐：

```text
VITE_API_MODE=java
VITE_PYTHON_API_BASE_URL=http://localhost:8001
VITE_JAVA_API_BASE_URL=http://localhost:8088/api
```

API 模式映射：

| VITE_API_MODE | 调用模式 | Base URL | Health 路径 | 其他接口路径 |
| --- | --- | --- | --- | --- |
| `python` | Python Direct | `VITE_PYTHON_API_BASE_URL` | `/health` | `/models`、`/plugins`、`/agents`、`/api/workflows/templates`、`/api/workflows/instantiate`、`/runs`、`/reports` |
| `java` | Java Gateway | `VITE_JAVA_API_BASE_URL` | `/agent/health` | `/models`、`/plugins`、`/agents`、`/workflows/templates`、`/workflows/instantiate`、`/platform/workflows/templates`、`/platform/workspaces`、`/runs`、`/reports`、`/settings`、`/platform/runs`、`/platform/events/recent` |

v2-only 演示版默认推荐 Java Gateway；Python Direct 保留为开发调试模式。

## GET /health

健康检查。

### Response

```json
{
  "status": "ok",
  "service": "python-agent-engine",
  "version": "v2-api-preview"
}
```

## Java Platform Service API

Java 层当前承担 API Gateway + 平台雏形职责，不替换 Python FastAPI。新增平台接口使用统一响应结构：

```json
{
  "success": true,
  "message": "ok",
  "data": {}
}
```

Java 平台服务层已接入 MySQL。当前通过 JPA 持久化任务记录、前端配置、模型配置和插件配置；Python Agent Engine 仍负责 AI 工作流，`reports/` 和 `runs/` 文件仍保留用于大文本产物存储。

### GET /api/health

Java 平台服务自身健康检查。

```json
{
  "status": "ok",
  "service": "java-platform-service",
  "version": "v2-java-preview"
}
```

### GET /api/agent/health

代理调用 Python：

```text
GET http://127.0.0.1:8001/health
```

### GET /api/models

代理调用 Python `GET /models`，响应结构与 Python API 保持一致。

### GET /api/plugins

代理调用 Python `GET /plugins`，响应结构与 Python API 保持一致。

### GET /api/agents

代理调用 Python `GET /agents`，返回 Agent 注册中心列表，响应使用 `ApiResponse` 包装。

```json
{
  "success": true,
  "message": "ok",
  "data": [
    {
      "key": "product",
      "name": "Product Agent",
      "role": "需求分析智能体",
      "description": "负责将用户自然语言需求拆解为功能需求和技术需求。",
      "input_fields": ["requirement"],
      "output_fields": ["product_result"],
      "stage": "analysis",
      "enabled": true,
      "version": "1.0"
    }
  ]
}
```

### GET /api/workflows/templates

代理调用 Python `GET /api/workflows/templates`，返回 Workflow 模板列表，响应使用 `ApiResponse` 包装。

```json
{
  "success": true,
  "message": "ok",
  "data": [
    {
      "key": "simple_demo",
      "name": "简单演示流程",
      "description": "适合快速展示需求拆解、代码生成、测试和报告结果。",
      "agent_sequence": ["product", "coder", "tester", "runner", "quality", "report"],
      "stage_sequence": ["分析", "生成", "测试", "执行", "评分", "报告"],
      "enabled": true,
      "version": "1.0",
      "md_path": "workflow_templates/template_md/simple_demo.md",
      "markdown": "# 简单演示流程"
    }
  ]
}
```

### POST /api/workflows/instantiate

代理调用 Python `POST /api/workflows/instantiate`，根据模板生成轻量任务视图。当前不会触发真实 LangGraph 运行，主要用于 Vue 模板选择和后续可视化编排预留。

```json
{
  "template_key": "simple_demo",
  "input_data": {
    "requirement": "写一个函数 get_second_largest(nums)"
  }
}
```

```json
{
  "success": true,
  "message": "ok",
  "data": {
    "platformRunId": "workflow_template_20260518_101500",
    "template_key": "simple_demo",
    "workflow_events": [],
    "run_summary": {
      "workflow_template": "simple_demo",
      "event_count": 0
    },
    "ui_view_model": {
      "workflow_template": {},
      "workflow_steps": []
    }
  }
}
```

### POST /api/code-agent/execute

代理调用 Python `POST /api/code-agent/execute`，执行简化 CodeAgent 文件操作。Java Gateway 模式下会把本次操作登记为一条 `run_record`，并把 Python 返回的 `AGENT_STARTED`、`AGENT_FINISHED`、`AGENT_FAILED` 事件保存到 MySQL `run_event` 表，通过已有 SSE 通道推送给 Vue。该 `platformRunId` 可直接用于 History 和 `/replay/{platformRunId}` 查看 CodeAgent 操作顺序。

```json
{
  "platformRunId": "code_agent_20260518_001",
  "operation": "write_file",
  "filePath": "output/code_agent_demo.txt",
  "content": "# 添加新函数 my_func"
}
```

```json
{
  "success": true,
  "message": "ok",
  "data": {
    "success": true,
    "agent": "code_agent",
    "operation": "write_file",
    "filePath": "output/code_agent_demo.txt",
    "platformRunId": "code_agent_20260518_001",
    "message": "CodeAgent 操作完成",
    "results": [
      {
        "success": true,
        "filePath": "output/code_agent_demo.txt",
        "message": "已修改或生成文件内容",
        "operation": "write_file"
      }
    ],
    "events": [
      {
        "event_type": "AGENT_STARTED",
        "event_text": "CodeAgent 操作开始",
        "agent": "code_agent",
        "status": "RUNNING",
        "message": "开始执行 write_file: output/code_agent_demo.txt"
      },
      {
        "event_type": "AGENT_FINISHED",
        "event_text": "CodeAgent 操作完成",
        "agent": "code_agent",
        "status": "SUCCESS",
        "message": "已修改或生成文件内容"
      }
    ]
  }
}
```

### POST /api/runs

代理调用 Python `POST /runs`。请求体与 Python `POST /runs` 一致：

```json
{
  "requirement": "写一个函数 get_second_largest(nums)，返回第二大的不同数字",
  "model_provider": "deepseek",
  "enabled_plugins": ["Doc Agent", "Security Agent"],
  "max_retry_count": 3,
  "require_human_approval": false,
  "demo_mode": true,
  "offline_mode": false
}
```

Java Gateway 模式下，响应会在保持 Python `RunResponse` 结构兼容的基础上额外返回 `platform_run_id`，用于前端跳转到 Java 平台运行记录和事件时间线。

```json
{
  "run_id": "run_20260518_101500",
  "platform_run_id": "platform_20260518_101500_12ab34cd",
  "run_summary": {
    "success": true,
    "retry_count": 1,
    "quality_score": 92.5
  },
  "ui_view_model": {}
}
```

### GET /api/runs

代理调用 Python `GET /runs`，用于读取历史运行列表。

### GET /api/runs/{runId}

代理调用 Python `GET /runs/{run_id}`，用于读取历史运行详情。

### GET /api/reports

代理调用 Python `GET /reports`，用于读取报告列表。

### GET /api/reports/{reportName}

代理调用 Python `GET /reports/{report_name}`，用于读取指定 Markdown 报告内容。

### GET /api/platform/runs

返回 Java 平台层保存在 MySQL 中的运行记录列表。

```json
{
  "success": true,
  "message": "ok",
  "data": [
    {
      "platformRunId": "platform_20260517_022215_12ab34cd",
      "pythonRunId": "run_20260517_102215",
      "requirement": "写一个函数 get_second_largest(nums)",
      "modelProvider": "deepseek",
      "success": true,
      "retryCount": 1,
      "testSuccess": true,
      "coveragePercent": 86.5,
      "qualityScore": 92.5,
      "securityStatus": "passed",
      "reportPath": "reports/run_20260517_102215.md",
      "statePath": "runs/run_20260517_102215.json",
      "rawResponse": "{\"run_id\":\"run_20260517_102215\",\"run_summary\":{},\"ui_view_model\":{}}",
      "createdAt": "2026-05-17T10:22:15",
      "updatedAt": "2026-05-17T10:22:15"
    }
  ]
}
```

### GET /api/platform/runs/{platformRunId}

返回 Java 平台层单条 MySQL 运行记录详情。Vue 在 `VITE_API_MODE=java` 时会点击历史记录后调用该接口；如果 `rawResponse` 中包含 `ui_view_model`，前端会复用 `SummaryCards`、`WorkflowTimeline`、`ResultOverview`、`AgentOutputTabs` 和 `ReportPreview` 展示完整运行详情。如果缺少 `rawResponse`，前端会用平台记录摘要字段做兼容展示。

增强运行记录会包含：

```json
{
  "runSummaryJson": "{\"success\":true,\"quality_score\":92.5}",
  "uiViewModelJson": "{\"workflow_steps\":[]}",
  "pluginResultsJson": "[{\"plugin_name\":\"Security Agent\",\"status\":\"success\"}]",
  "errorSummary": "",
  "modelName": "deepseek-chat",
  "modelBaseUrl": "https://api.deepseek.com",
  "approved": true,
  "requireHumanApproval": false
}
```

### POST /api/platform/runs/{platformRunId}/cancel

将 Java 平台任务标记为取消。当前阶段这是平台层状态记录能力，不会强制中断已经同步提交给 Python Agent Engine 的运行进程。若任务已经结束，会返回当前记录并写入一条提示事件。

```json
{
  "success": true,
  "message": "ok",
  "data": {
    "platformRunId": "platform_20260518_101500_12ab34cd",
    "status": "CANCELLED"
  }
}
```

### GET /api/platform/runs/{platformRunId}/events

返回某次 Java 平台运行的事件时间线，按 `createdAt` 升序排列。Vue History 页面在 Java Gateway 模式下会展示该事件时间线。

```json
{
  "success": true,
  "message": "ok",
  "data": [
    {
      "id": 1,
      "platformRunId": "platform_20260518_101500_12ab34cd",
      "pythonRunId": null,
      "eventType": "RUN_CREATED",
      "eventText": "任务创建",
      "status": "CREATED",
      "message": "Java 平台任务已创建",
      "detailJson": "{\"requirement\":\"写一个函数 get_second_largest(nums)\"}",
      "createdAt": "2026-05-18T10:15:00"
    },
    {
      "id": 5,
      "platformRunId": "platform_20260518_101500_12ab34cd",
      "pythonRunId": "run_20260518_101501",
      "eventType": "RUN_SUCCESS",
      "eventText": "任务成功",
      "status": "SUCCESS",
      "message": "任务运行成功",
      "detailJson": "{\"qualityScore\":92.5}",
      "createdAt": "2026-05-18T10:16:12"
    }
  ]
}
```

### GET /api/platform/runs/{platformRunId}/replay

返回某次 Java 平台运行的工作流回放数据。该接口复用 MySQL 中的 `run_record` 和 `run_event`，不改变原有事件查询接口。

```json
{
  "success": true,
  "message": "ok",
  "data": {
    "platformRunId": "platform_20260518_101500_12ab34cd",
    "pythonRunId": "run_20260518_101501",
    "requirement": "写一个函数 get_second_largest(nums)",
    "status": "SUCCESS",
    "statusText": "成功",
    "success": true,
    "qualityScore": 90,
    "durationMs": 12800,
    "events": [
      {
        "id": 1,
        "platformRunId": "platform_20260518_101500_12ab34cd",
        "pythonRunId": "run_20260518_101501",
        "eventType": "AGENT_STARTED",
        "eventText": "Product Agent 开始执行",
        "agent": "product",
        "status": "RUNNING",
        "message": "正在拆解用户需求",
        "detailJson": "{\"detail\":{}}",
        "createdAt": "2026-05-18T10:15:02"
      }
    ],
    "runSummary": {},
    "uiViewModel": {}
  }
}
```

Vue 在 Java Gateway 模式下通过 `/replay/{platformRunId}` 页面消费该接口，支持上一步、下一步、自动播放、暂停、重置和播放速度选择。

### GET /api/platform/runs/{platformRunId}/events/stream

通过 SSE 订阅某次 Java 平台运行的实时事件流。

- 仅 Java Gateway 模式支持。
- Python Direct 模式不支持实时事件流，前端应回退到 `GET /platform/runs/{platformRunId}/events` 查询历史事件。
- 返回类型为 `text/event-stream`。
- 首次连接会发送 `connected` 事件。
- 连接建立后会回放该任务最近若干条历史事件，事件名为 `run-event`。
- 新增事件写入 MySQL 后，Java 会主动推送 `run-event`。
- 当任务进入 `SUCCESS`、`FAILED`、`CANCELLED` 时，会发送 `final` 事件并关闭当前任务的 SSE 连接。

请求示例：

```text
GET /api/platform/runs/platform_20260518_101500_12ab34cd/events/stream
Accept: text/event-stream
```

事件示例：

```text
event: connected
data: {"platformRunId":"platform_20260518_101500_12ab34cd","message":"SSE 连接已建立","createdAt":"2026-05-18T10:15:02"}

event: run-event
id: 5
data: {"id":5,"platformRunId":"platform_20260518_101500_12ab34cd","pythonRunId":"run_20260518_101501","eventType":"PYTHON_RESPONSE_RECEIVED","eventText":"收到 Python 响应","status":"RUNNING","message":"Python Agent Engine 已返回运行结果","detailJson":"{}","createdAt":"2026-05-18T10:16:10"}

event: final
id: 8
data: {"id":8,"platformRunId":"platform_20260518_101500_12ab34cd","eventType":"RUN_SUCCESS","eventText":"任务成功","status":"SUCCESS","message":"任务运行成功","createdAt":"2026-05-18T10:16:12"}
```

当前 SSE 是平台层事件推送雏形。Java 会推送自身平台事件，也会保存并推送 Python `workflow_events` 中的细粒度 Agent 事件；这些事件来自 Python 工作流执行结果，仍不是真正的 Python 进程内流式回调。

### GET /api/platform/events/recent

返回最近平台事件，默认 20 条，可通过 `limit` 参数调整。Dashboard 在 Java Gateway 模式下会展示最近 10 条平台事件。

```text
GET /api/platform/events/recent?limit=10
```

```json
{
  "success": true,
  "message": "ok",
  "data": [
    {
      "id": 8,
      "platformRunId": "platform_20260518_101500_12ab34cd",
      "pythonRunId": "run_20260518_101501",
      "eventType": "REPORT_INDEXED",
      "eventText": "报告已索引",
      "status": "SUCCESS",
      "message": "报告索引已保存",
      "detailJson": "{\"reportName\":\"report_run_20260518_101501.md\"}",
      "createdAt": "2026-05-18T10:16:13"
    }
  ]
}
```

### GET /api/platform/stats

返回 Java/MySQL 平台统计数据。

```json
{
  "success": true,
  "message": "ok",
  "data": {
    "totalRuns": 12,
    "successRuns": 10,
    "failedRuns": 2,
    "averageQualityScore": 88.4,
    "totalReports": 12,
    "testSuccessRuns": 10,
    "repairedRuns": 4
  }
}
```

### GET /api/platform/reports

返回 Java/MySQL 中保存的报告索引列表。

```json
{
  "success": true,
  "message": "ok",
  "data": [
    {
      "reportName": "report_run_20260517_102215.md",
      "reportPath": "reports/report_run_20260517_102215.md",
      "platformRunId": "platform_20260517_022215_12ab34cd",
      "pythonRunId": "run_20260517_102215",
      "requirement": "写一个函数 get_second_largest(nums)",
      "success": true,
      "qualityScore": 92.5,
      "createdAt": "2026-05-17T10:22:15",
      "updatedAt": "2026-05-17T10:22:15"
    }
  ]
}
```

### GET /api/platform/reports/{reportName}

优先代理 Python `GET /reports/{reportName}` 获取 Markdown 报告正文，同时返回 MySQL 报告索引。若 Python 报告正文读取失败，则仍返回索引信息和错误提示。

```json
{
  "success": true,
  "message": "ok",
  "data": {
    "reportName": "report_run_20260517_102215.md",
    "reportIndex": {
      "platformRunId": "platform_20260517_022215_12ab34cd",
      "pythonRunId": "run_20260517_102215"
    },
    "content": "# AI Agent Workflow Report"
  }
}
```

### GET /api/platform/runs/{platformRunId}/reports

返回某次 Java 平台运行关联的 MySQL 报告索引列表。

### GET /api/settings

返回当前前端配置。

```json
{
  "success": true,
  "message": "ok",
  "data": {
    "selectedModelProvider": "deepseek",
    "enabledPlugins": ["Doc Agent", "Security Agent"],
    "demoMode": true,
    "maxRetryCount": 3,
    "requireHumanApproval": false,
    "offlineMode": false,
    "apiMode": "java"
  }
}
```

### POST /api/settings

覆盖当前前端配置。请求体：

```json
{
  "selectedModelProvider": "deepseek",
  "enabledPlugins": ["Doc Agent"],
  "demoMode": true,
  "maxRetryCount": 3,
  "requireHumanApproval": false,
  "offlineMode": false,
  "apiMode": "java"
}
```

响应结构同 `GET /api/settings`。

### Vue 前端数据源规则

| VITE_API_MODE | runs/history | settings | models | plugins |
| --- | --- | --- | --- | --- |
| `python` | `GET /runs`，读取 Python `runs/` 历史 | localStorage | Python `GET /models`，读取 Python 文件配置 | Python `GET /plugins`，读取 Python 文件配置 |
| `java` | `GET /platform/runs` 和 `GET /platform/runs/{platformRunId}`，读取 Java/MySQL 平台记录 | Java `GET /settings` / `POST /settings`，失败回退 localStorage | Java `GET /models`，优先读取 MySQL `model_config` | Java `GET /plugins`，优先读取 MySQL `plugin_config` |

Java Gateway 模式下，`POST /runs` 仍由 Java 代理到 Python Agent Engine 执行真实 AI 工作流；Java 保存平台侧运行索引、配置数据和平台可观察事件，不解析 LangGraph 内部逻辑。

Vue Reports 在 Java Gateway 模式下会优先调用 `GET /platform/reports` 展示 MySQL 报告索引，点击报告后调用 `GET /platform/reports/{reportName}` 展示索引和 Markdown 正文。Dashboard 在 Java Gateway 模式下会优先调用 `GET /platform/stats` 展示平台统计，并调用 `GET /platform/events/recent` 展示最近平台事件；接口失败时对应模块降级为空状态。

Java 本地启动方式：

```powershell
cd backend-java
mvn spring-boot:run
```

Java 服务配置：

```yaml
server:
  port: 8088

agent:
  engine:
    base-url: http://127.0.0.1:8001
```

Docker Compose 中通过环境变量连接 Python 服务：

```text
AGENT_ENGINE_BASE_URL=http://ai-agent-api:8001
```

## GET /models

读取 `config/models.yaml` 和环境变量覆盖后的模型列表。

### Response

```json
[
  {
    "name": "DeepSeek",
    "provider": "deepseek",
    "model": "deepseek-chat",
    "base_url": "https://api.deepseek.com",
    "env_key": "DEEPSEEK_API_KEY",
    "enabled": true,
    "offline_mode": false,
    "api_key_configured": true,
    "is_default": true
  }
]
```

Vue 前端会兼容可选字段：

- `api_key_configured`：如果 API 返回 `false`，Models 页面显示黄色 API Key 警告。
- `default` / `is_default`：如果 API 返回，Models 页面显示后端默认标记。
- 前端默认模型不写回 Python 配置，保存在 localStorage。

## GET /plugins

读取 `config/agents.yaml` 中的插件配置，并返回插件展示信息。

### Response

```json
[
  {
    "name": "security_agent",
    "display_name": "Security Agent",
    "description": "检查最终代码是否包含危险操作",
    "enabled": true,
    "latest_result": {
      "status": "success",
      "summary": "安全检查通过"
    }
  }
]
```

Vue 前端会兼容可选字段：

- `latest_result`：如果 API 返回，Plugins 页面展示最近一次执行结果。
- 插件开关当前保存于前端 localStorage，不写回 `config/agents.yaml`。

## GET /agents

读取 Python Agent 注册中心，返回 Product、Coder、Tester、Runner、Sentry、Plugins、Quality、Report 等 Agent 元信息。

### Response

```json
[
  {
    "key": "product",
    "name": "Product Agent",
    "role": "需求分析智能体",
    "description": "负责将用户自然语言需求拆解为功能需求和技术需求。",
    "input_fields": ["requirement"],
    "output_fields": ["product_result"],
    "stage": "analysis",
    "enabled": true,
    "version": "1.0"
  }
]
```

Vue `Agents` 页面会调用该接口展示 Agent 名称、角色、阶段、输入字段、输出字段和启用状态。Java Gateway 模式下前端调用 `/api/agents`，Python Direct 模式下前端调用 `/agents`。

## GET /api/workflows/templates

读取 Python Workflow 模板注册表，返回可复用模板列表和 Markdown 描述内容。

### Response

```json
[
  {
    "key": "repair_flow",
    "name": "自动修复重点流程",
    "description": "突出测试失败、错误分析、自动修复和再次验证，适合比赛答辩演示。",
    "agent_sequence": ["product", "coder", "tester", "runner", "sentry", "coder", "tester", "runner", "quality", "report"],
    "stage_sequence": ["分析", "生成", "测试", "执行", "修复", "再测试", "再执行", "评分", "报告"],
    "enabled": true,
    "version": "1.0",
    "md_path": "workflow_templates/template_md/repair_flow.md",
    "markdown": "# 自动修复重点流程"
  }
]
```

## POST /api/workflows/instantiate

根据 Workflow 模板生成轻量任务视图。该接口用于模板选择和后续工作流编辑器预留，当前不执行 LangGraph、不生成报告、不写入 `runs/`。

### Request

```json
{
  "template_key": "repair_flow",
  "input_data": {
    "requirement": "演示一个需要自动修复的任务",
    "model_provider": "deepseek"
  },
  "template_data": {
    "workflowTemplateKey": "custom_repair_flow",
    "name": "自定义修复流程",
    "description": "从 Vue Workflow Editor 生成的模板",
    "nodes": [],
    "connections": [],
    "version": "1.0"
  }
}
```

### Response

```json
{
  "platformRunId": "workflow_template_20260518_101500",
  "run_id": "workflow_template_20260518_101500",
  "template_key": "repair_flow",
  "workflow_events": [],
  "run_summary": {
    "success": false,
    "retry_count": 0,
    "workflow_template": "repair_flow",
    "event_count": 0
  },
  "ui_view_model": {
    "workflow_template": {},
    "workflow_steps": [
      {
        "key": "product_1",
        "agent_key": "product",
        "label": "Product Agent",
        "status": "waiting",
        "summary": "分析阶段等待执行",
        "order": 1
      }
    ],
    "workflow_events": []
  }
}
```

Vue `WorkflowTemplates` 页面在 Python Direct 模式下调用 `/api/workflows/templates` 和 `/api/workflows/instantiate`；在 Java Gateway 模式下调用 `/api/workflows/templates` 和 `/api/workflows/instantiate`，由 Java 代理到 Python。

Vue `WorkflowEditor` 页面会把当前画布导出为 `template_data`，再调用 `POST /api/workflows/instantiate` 生成轻量任务视图。若 `template_key` 不是内置模板，Python 会使用 `template_data.nodes` 生成临时 `agent_sequence` 和 `stage_sequence`，仍不会执行 LangGraph。

## Java 平台 Workflow 模板持久化

Java Gateway 模式下，Vue `WorkflowEditor` 可以把自定义模板保存到 MySQL。该能力只保存模板元数据、节点和连接，不改变 Python 默认 LangGraph 主流程。

### GET /api/platform/workflows/templates

返回 MySQL 中保存的自定义 Workflow 模板列表。

```json
{
  "success": true,
  "message": "ok",
  "data": [
    {
      "workflowTemplateKey": "custom_repair_flow",
      "templateKey": "custom_repair_flow",
      "key": "custom_repair_flow",
      "name": "自定义修复流程",
      "description": "通过 Vue Workflow Editor 创建",
      "nodes": [],
      "connections": [],
      "agent_sequence": ["product", "coder", "tester"],
      "stage_sequence": ["analysis", "generation", "testing"],
      "source": "java-mysql",
      "version": "1.0"
    }
  ]
}
```

### GET /api/platform/workflows/templates/{templateKey}

返回单个 MySQL Workflow 模板。不存在时返回 `success=false`。

### POST /api/platform/workflows/templates

保存或覆盖一个自定义 Workflow 模板。Vue 在 Java Gateway 模式下点击“保存到 MySQL”会调用该接口；Python Direct 模式继续使用 localStorage。首次保存默认版本为 `1.0`；覆盖保存同一 `templateKey` 时，Java 会自动递增版本号并更新 `updatedAt`。

### Request

```json
{
  "workflowTemplateKey": "custom_repair_flow",
  "name": "自定义修复流程",
  "description": "通过 Vue Workflow Editor 创建",
  "nodes": [
    {
      "nodeId": "product_1",
      "agentKey": "product",
      "name": "Product Agent",
      "position": { "x": 80, "y": 80 },
      "input_fields": ["requirement"],
      "output_fields": ["product_result"],
      "stage": "analysis",
      "enabled": true,
      "description": "需求拆解节点"
    }
  ],
  "connections": [],
  "version": "1.0"
}
```

### DELETE /api/platform/workflows/templates/{templateKey}

删除一个 MySQL 自定义 Workflow 模板。该接口只影响 Java 平台层保存的自定义模板，不删除 Python `workflow_templates/` 中的内置模板，也不影响浏览器 localStorage。

```json
{
  "success": true,
  "message": "ok",
  "data": {
    "workflowTemplateKey": "custom_repair_flow",
    "templateKey": "custom_repair_flow",
    "name": "自定义修复流程",
    "version": "1.1",
    "source": "java-mysql"
  }
}
```

### Response

```json
{
  "success": true,
  "message": "ok",
  "data": {
    "workflowTemplateKey": "custom_repair_flow",
    "templateKey": "custom_repair_flow",
    "name": "自定义修复流程",
    "nodes": [],
    "connections": [],
    "agent_sequence": ["product"],
    "stage_sequence": ["analysis"],
    "source": "java-mysql"
  }
}
```

### POST /api/platform/workflows/templates/{templateKey}/instantiate

从 MySQL 自定义 Workflow 模板生成一条轻量平台任务记录和可回放事件。该接口不会执行 LangGraph、不会调用模型、不会生成报告，只用于演示“模板中心 → 平台运行记录 → Replay”的闭环。

### Request

```json
{
  "input_data": {
    "requirement": "从 MySQL Workflow 模板生成回放任务"
  }
}
```

### Response

```json
{
  "success": true,
  "message": "ok",
  "data": {
    "platformRunId": "workflow_template_20260519_105500_ab12cd34",
    "run_id": "workflow_template_20260519_105500_ab12cd34",
    "template_key": "custom_repair_flow",
    "workflow_events": [
      {
        "event_type": "WORKFLOW_STARTED",
        "event_text": "Workflow 模板任务开始",
        "agent": "workflow",
        "status": "RUNNING"
      },
      {
        "event_type": "AGENT_STARTED",
        "event_text": "Product Agent 开始执行",
        "agent": "product",
        "status": "RUNNING"
      }
    ],
    "run_summary": {
      "success": true,
      "workflow_template": "custom_repair_flow",
      "runner_mode": "workflow_template"
    },
    "ui_view_model": {
      "workflow_steps": [],
      "workflow_events": []
    }
  }
}
```

Vue `WorkflowEditor` 在 Java Gateway 模式下会在 MySQL 模板详情弹窗中显示“生成可回放任务”，成功后跳转 `/replay/{platformRunId}`。

## POST /api/code-agent/execute

执行简化 CodeAgent 文件操作。该接口不是完整 Codex，只提供受控的项目文件操作能力。

### 配置约束

CodeAgent 读取 `config/settings.yaml` 中的 `code_agent` 配置：

```yaml
code_agent:
  enabled: true
  allowed_paths:
    - src
    - output
    - docs
    - frontend-vue/src
  blocked_paths:
    - .git
    - .venv
    - node_modules
    - .env
  audit_log_path: output/code_agent_audit.jsonl
  max_read_chars: 200000
```

- `allowed_paths`：仅允许操作这些项目内路径。
- `blocked_paths`：即使在白名单内也禁止访问。
- `audit_log_path`：每次操作开始、完成或失败都会追加 JSONL 审计记录。
- `max_read_chars`：读取大文件时的最大返回字符数。

### 支持操作

| operation | 字段 | 说明 |
| --- | --- | --- |
| `read_file` | `filePath` | 读取项目目录内指定文件内容。父目录不存在时会创建，但文件不存在会返回失败。 |
| `write_file` | `filePath`、`content` | 写入或生成项目目录内指定文件，自动创建父目录。 |
| `list_files` | `filePath`、`recursive` | 列出项目目录中的文件，目录不存在时自动创建。 |

### Request

```json
{
  "operation": "read_file",
  "filePath": "src/moduleA.py"
}
```

批量操作也可使用 `operations`：

```json
{
  "operations": [
    {
      "operation": "read_file",
      "filePath": "src/moduleA.py"
    },
    {
      "operation": "write_file",
      "filePath": "src/moduleB.py",
      "content": "# 添加新函数 my_func"
    },
    {
      "operation": "list_files",
      "filePath": "src",
      "recursive": false
    }
  ]
}
```

### Response

```json
{
  "success": true,
  "agent": "code_agent",
  "operation": "read_file",
  "filePath": "src/moduleA.py",
  "message": "CodeAgent 操作完成",
  "results": [
    {
      "success": true,
      "filePath": "src/moduleA.py",
      "message": "已读取文件内容",
      "content": "print('hello')",
      "auditPath": "output/code_agent_audit.jsonl",
      "operation": "read_file"
    }
  ],
  "events": [
    {
      "event_type": "AGENT_STARTED",
      "event_text": "CodeAgent 操作开始",
      "agent": "code_agent",
      "status": "RUNNING",
      "message": "开始执行 read_file: src/moduleA.py",
      "detail": {
        "operation": "read_file",
        "filePath": "src/moduleA.py"
      },
      "created_at": "2026-05-18T12:00:00"
    },
    {
      "event_type": "AGENT_FINISHED",
      "event_text": "CodeAgent 操作完成",
      "agent": "code_agent",
      "status": "SUCCESS",
      "message": "已读取文件内容",
      "detail": {
        "operation": "read_file"
      },
      "created_at": "2026-05-18T12:00:01"
    }
  ]
}
```

Python Direct 模式下 Vue 直接读取响应中的 `events` 展示。Java Gateway 模式下 Vue 会先订阅 `/api/platform/runs/{platformRunId}/events/stream`，再调用 `/api/code-agent/execute`，Java 会将这些事件保存到 MySQL 并通过 SSE 推送。

## POST /runs

创建一次 AI 工作流运行。接口内部调用 `services.run_service.create_run(request)`。

### Request

```json
{
  "requirement": "写一个函数 get_second_largest(nums)，返回第二大的不同数字",
  "model_provider": "deepseek",
  "enabled_plugins": ["Doc Agent", "Security Agent", "Refactor Agent", "UI Agent"],
  "max_retry_count": 3,
  "require_human_approval": false,
  "demo_mode": true,
  "offline_mode": false
}
```

字段说明：

- `requirement`：用户需求，必填。
- `model_provider`：模型服务商，例如 `deepseek`、`qwen`、`zhipu`。
- `enabled_plugins`：本次运行展示层记录的启用插件名称。
- `max_retry_count`：最大自动修复次数。
- `require_human_approval`：是否要求人工审批；API 自动化调用可传 `false`。
- `demo_mode`：是否以演示模式展示。
- `offline_mode`：是否启用离线演示模式标记。

### Response

```json
{
  "run_id": "run_20260516_124408",
  "run_summary": {
    "success": true,
    "retry_count": 1,
    "test_success": true,
    "coverage_percent": 86,
    "quality_score": 90,
    "security_status": "安全检查通过",
    "enabled_plugins": ["Doc Agent", "Security Agent"],
    "model_provider": "deepseek",
    "runner_mode": "python",
    "runner_warning": "",
    "event_count": 13,
    "last_event": {
      "event_type": "WORKFLOW_FINISHED",
      "event_text": "工作流执行完成",
      "agent": "workflow",
      "status": "SUCCESS"
    },
    "workflow_event_summary": {
      "total": 13,
      "failed_count": 0,
      "agents": ["coder", "product", "quality", "report", "runner", "tester", "workflow"]
    },
    "report_path": "reports/run_20260516_124408.md"
  },
  "state": {
    "workflow_events": [
      {
        "event_type": "WORKFLOW_STARTED",
        "event_text": "工作流开始执行",
        "agent": "workflow",
        "status": "RUNNING",
        "message": "LangGraph 工作流已启动",
        "detail": {},
        "created_at": "2026-05-16T12:44:08"
      }
    ]
  },
  "ui_view_model": {
    "header": {
      "title": "AI Multi-Agent Pipeline",
      "run_status": "Waiting",
      "model_provider": "deepseek"
    },
    "summary_cards": {},
    "workflow_steps": [
      {
        "key": "requirement",
        "label": "Requirement",
        "status": "done",
        "summary": "写一个函数 get_second_largest(nums)",
        "order": 1
      }
    ],
    "workflow_events": [
      {
        "event_type": "AGENT_STARTED",
        "event_text": "Product Agent 开始执行",
        "agent": "product",
        "status": "RUNNING",
        "message": "正在拆解用户需求",
        "detail": {},
        "created_at": "2026-05-16T12:44:09"
      }
    ],
    "agent_outputs": {},
    "plugin_outputs": {},
    "report": {},
    "result_index": {}
  }
}
```

## GET /runs/{run_id}

根据 `runs/{run_id}.json` 读取历史运行详情。

### Response

```json
{
  "run_id": "run_20260516_124408",
  "state": {
    "run_id": "run_20260516_124408",
    "requirement": "写一个函数 get_second_largest(nums)",
    "success": true,
    "report_path": "reports/run_20260516_124408.md"
  },
  "run_summary": {
    "success": true,
    "retry_count": 1,
    "test_success": true,
    "coverage_percent": 86,
    "quality_score": 90,
    "security_status": "安全检查通过",
    "enabled_plugins": ["Doc Agent", "Security Agent"],
    "model_provider": "deepseek",
    "runner_mode": "python",
    "runner_warning": "",
    "event_count": 13,
    "last_event": {
      "event_type": "WORKFLOW_FINISHED",
      "event_text": "工作流执行完成",
      "agent": "workflow",
      "status": "SUCCESS"
    },
    "workflow_event_summary": {
      "total": 13,
      "failed_count": 0
    },
    "report_path": "reports/run_20260516_124408.md"
  },
  "ui_view_model": {
    "header": {},
    "summary_cards": {},
    "workflow_steps": [],
    "workflow_events": [],
    "agent_outputs": {},
    "plugin_outputs": {},
    "report": {},
    "result_index": {},
    "raw": {}
  }
}
```

`workflow_events` 是 Python Agent Engine 生成的细粒度工作流事件，事件结构如下：

```json
{
  "event_type": "AGENT_FINISHED",
  "event_text": "Coder Agent 完成代码输出",
  "agent": "coder",
  "status": "SUCCESS",
  "message": "代码输出完成",
  "detail": {
    "repair": false,
    "retry_count": 0
  },
  "created_at": "2026-05-16T12:44:20"
}
```

当前支持的事件类型包括：`WORKFLOW_STARTED`、`AGENT_STARTED`、`AGENT_FINISHED`、`AGENT_FAILED`、`RUNNER_STARTED`、`RUNNER_FINISHED`、`TEST_STARTED`、`TEST_FINISHED`、`REPAIR_STARTED`、`REPAIR_FINISHED`、`QUALITY_EVALUATED`、`REPORT_GENERATED`、`WORKFLOW_FINISHED`。

不存在时返回：

```json
{
  "detail": "run not found: run_20260516_000000"
}
```

## GET /runs

返回历史运行列表，优先提供每个 run 的 `run_summary`，同时保留兼容旧 UI 的扁平字段。

### Response

```json
[
  {
    "run_id": "run_20260516_124408",
    "run_summary": {
      "success": true,
      "retry_count": 1,
      "test_success": true,
      "coverage_percent": 86,
      "quality_score": 90,
      "security_status": "安全检查通过",
      "enabled_plugins": ["Doc Agent", "Security Agent"],
      "model_provider": "deepseek",
      "report_path": "reports/run_20260516_124408.md"
    },
    "success": true,
    "retry_count": 1,
    "test_success": true,
    "coverage_percent": 86,
    "quality_score": 90,
    "model_provider": "deepseek",
    "model_name": "deepseek-chat",
    "requirement": "写一个函数 get_second_largest(nums)",
    "created_at": "2026-05-16 12:44:08",
    "report_path": "reports/run_20260516_124408.md",
    "state_path": "runs/run_20260516_124408.json"
  }
]
```

Vue 前端会对历史列表做轻量兼容：

- `created_at` 优先读取 API 字段，缺失时从 `run_id` 解析。
- `coverage_percent` 优先读取扁平字段，缺失时读取 `run_summary.coverage_percent`。
- 历史详情通过 `GET /runs/{run_id}` 读取完整 `ui_view_model`。

## GET /reports

返回 `reports/` 目录中的 Markdown 报告列表。

### Response

```json
[
  {
    "name": "run_20260516_124408.md",
    "path": "reports/run_20260516_124408.md",
    "size": 7422,
    "modified_time": "2026-05-16 12:44:08"
  }
]
```

## GET /reports/{report_name}

返回指定 Markdown 报告内容。`report_name` 只能是 `reports/` 目录下的文件名。

### Response

```json
{
  "name": "run_20260516_124408.md",
  "path": "reports/run_20260516_124408.md",
  "content": "# AI Multi-Agent Pipeline 运行报告\n..."
}
```

## Vue / TypeScript 调用示例

当前 `frontend-vue/` 使用 Axios 封装 API 客户端，基础地址和调用模式来自 `.env.development`：

```text
VITE_API_MODE=python
VITE_PYTHON_API_BASE_URL=http://127.0.0.1:8001
VITE_JAVA_API_BASE_URL=http://127.0.0.1:8088/api
```

`src/api/client.ts`：

```ts
import axios from "axios";

export type ApiMode = "python" | "java";

export const currentApiMode: ApiMode = import.meta.env.VITE_API_MODE === "java" ? "java" : "python";
export const currentApiBaseUrl =
  currentApiMode === "java"
    ? import.meta.env.VITE_JAVA_API_BASE_URL
    : import.meta.env.VITE_PYTHON_API_BASE_URL;
export const currentHealthPath = currentApiMode === "java" ? "/agent/health" : "/health";

export const apiClient = axios.create({
  baseURL: currentApiBaseUrl,
  timeout: 600000,
  headers: {
    "Content-Type": "application/json",
  },
});

export const getHealth = () => apiClient.get(currentHealthPath).then((response) => response.data);
```

`src/api/runs.ts`：

```ts
import { apiClient } from "./client";

type RunRequest = {
  requirement: string;
  model_provider: string;
  enabled_plugins: string[];
  max_retry_count: number;
  require_human_approval: boolean;
  demo_mode: boolean;
  offline_mode: boolean;
};

export function getRuns(): Promise<RunHistoryItem[]> {
  return apiClient.get("/runs").then((response) => response.data);
}

export function postRun(payload: RunRequest): Promise<RunResponse> {
  return apiClient.post("/runs", payload).then((response) => response.data);
}
```

页面中调用：

```ts
const result = await postRun({
  requirement: "写一个函数 get_second_largest(nums)，返回第二大的不同数字",
  model_provider: "deepseek",
  enabled_plugins: ["Doc Agent", "Security Agent"],
  max_retry_count: 3,
  require_human_approval: false,
  demo_mode: true,
  offline_mode: false,
});

console.log(result.run_id, result.ui_view_model.workflow_steps);
```

其他基础接口：

```ts
export const getModels = () => apiClient.get("/models").then((response) => response.data);
export const getPlugins = () => apiClient.get("/plugins").then((response) => response.data);
export const getReports = () => apiClient.get("/reports").then((response) => response.data);
```

Dashboard 总览页会并行读取基础接口，并对每个模块独立容错：

```ts
const [health, runs, reports, models, plugins] = await Promise.allSettled([
  getHealth(),
  getRuns(),
  getReports(),
  getModels(),
  getPlugins(),
]);
```

Dashboard 基于 `GET /runs` 的历史摘要列表计算：

```ts
const totalRuns = runs.length;
const successRuns = runs.filter((run) => run.success).length;
const failedRuns = totalRuns - successRuns;
const averageQualityScore =
  totalRuns === 0 ? 0 : runs.reduce((sum, run) => sum + run.quality_score, 0) / totalRuns;
```

Dashboard 顶部会展示当前 API 模式、API 地址和连接状态。如果 health 检测失败，顶部显示“API 未连接”；如果某个列表接口失败，仅对应卡片显示错误或 Empty 状态。

模型、插件和前端设置：

```ts
type FrontendSettings = {
  selectedModelProvider: string;
  enabledPlugins: string[];
  demoMode: boolean;
  maxRetryCount: number;
  requireHumanApproval: boolean;
  offlineMode: boolean;
};

export function getModels(): Promise<ModelConfig[]> {
  return apiClient.get("/models").then((response) => response.data);
}

export function getPlugins(): Promise<PluginConfig[]> {
  return apiClient.get("/plugins").then((response) => response.data);
}
```

当前 `frontend-vue/src/stores/settings.ts` 将 `FrontendSettings` 保存到浏览器 localStorage。`RunConsole` 读取 `selectedModelProvider` 和 `enabledPlugins` 作为默认模型和默认插件列表，用户仍可在运行前临时修改，最终请求体会携带当前表单值。

当 `VITE_API_MODE=java` 时，Vue 会优先调用 `GET /settings` 读取 MySQL 中的前端配置，并在修改默认模型、插件开关或运行默认参数时尝试 `POST /settings`。如果 Java settings 接口失败，则继续使用 localStorage，不影响 Python Direct 模式。

演示模式仍然使用同一个 `POST /runs` 契约，只是在前端预置演示案例并设置 `demo_mode=true`：

```ts
await postRun({
  requirement: "写一个函数 get_second_largest(nums)，返回列表中第二大的不同数字",
  model_provider: selectedModelProvider,
  enabled_plugins: enabledPlugins,
  max_retry_count: 3,
  require_human_approval: false,
  demo_mode: true,
  offline_mode: false,
});
```

当前 Python Agent Engine 会在返回结果中提供 `ui_view_model.workflow_events`，Java Gateway 模式还可以通过 SSE 推送已保存的平台事件。由于 Python 工作流仍是同步请求，Vue 演示模式会在请求返回后基于 `run_summary`、`ui_view_model.workflow_steps` 和 `ui_view_model.workflow_events` 展示工作流阶段、自动修复高光、最终质量评分和报告结果。请求失败时展示“演示运行失败”，并提示检查当前 API 模式对应的 Python Agent Engine 或 Java Gateway。

历史和报告页调用：

```ts
export function getRuns(): Promise<RunHistoryItem[]> {
  return apiClient.get("/runs").then((response) => response.data);
}

export function getRun(runId: string): Promise<RunResponse> {
  return apiClient.get(`/runs/${runId}`).then((response) => response.data);
}

export function getReports(): Promise<ReportItem[]> {
  return apiClient.get("/reports").then((response) => response.data);
}

export function getReport(reportName: string): Promise<ReportDetail> {
  return apiClient.get(`/reports/${reportName}`).then((response) => response.data);
}
```

当前 Vue 前端的结果展示约定：

```ts
type WorkflowStep = {
  key: string;
  label: string;
  status: "waiting" | "running" | "done" | "failed" | "repairing" | "skipped" | string;
  summary: string;
  order: number;
};

type PluginResult = {
  plugin_name?: string;
  name?: string;
  status?: "success" | "warning" | "failed" | "disabled" | string;
  summary?: string;
  detail?: string;
};

type UIViewModel = {
  workflow_steps?: WorkflowStep[];
  agent_outputs?: {
    product_result?: string;
    code?: string;
    tester_result?: string;
    sentry_result?: string;
    stdout?: string;
    error_summary?: string;
    error_log?: string;
  };
  plugin_outputs?: {
    plugin_results?: PluginResult[];
    doc_result?: string;
    security_result?: string;
    refactor_result?: string;
    ui_result?: string;
  };
  report?: {
    report_path?: string;
    report_markdown?: string;
    run_id?: string;
  };
};
```

Vue 组件消费关系：

- `SummaryCards` 读取 `run_summary`。
- `SummaryCards` 和 `ResultOverview` 会轻量展示 `runner_mode` / `runner_warning`：`cpp` 显示 C++ Sandbox Runner，fallback 时展示 warning。
- `WorkflowTimeline` 读取 `ui_view_model.workflow_steps`，按 `order` 展示节点。
- `WorkflowTimeline` 可读取 `ui_view_model.workflow_events` 作为 Agent 事件提示增强，不替代原有 `workflow_steps`。
- `ResultOverview` 读取 `run_id`、`run_summary` 和 `ui_view_model.agent_outputs.error_summary`。
- `AgentOutputTabs` 读取 `ui_view_model.agent_outputs`、`plugin_outputs`、`report` 和 Raw JSON。
- `PluginResultPanel` 优先读取 `plugin_outputs.plugin_results`，缺失时兼容旧字段。
- `ReportPreview` 读取 `ui_view_model.report.report_path` 和 `report_markdown`。
- `RunHistory` 先读取 `GET /runs` 列表，再用 `GET /runs/{run_id}` 加载右侧详情。
- `Reports` 先读取 `GET /reports` 列表，再用 `GET /reports/{report_name}` 查看 Markdown 内容。
- `DashboardStats` 基于 `GET /runs` 和 `GET /reports` 展示总数、成功/失败、平均质量评分、最近运行和最近报告。
- `RecentRuns` 展示最近 5 条运行摘要，并可跳转到 `/history`。
- `RecentReports` 展示最近 5 个 Markdown 报告，并可跳转到 `/reports`。
- `ModelStatusPanel` 读取 `GET /models` 和 `settings.selectedModelProvider` 展示可用模型、默认模型和 API Key 警告。
- `PluginStatusPanel` 读取 `GET /plugins` 和 `settings.enabledPlugins` 展示后端插件状态与前端运行时启用状态。
- `QuickActions` 提供 `/runs/new`、`/history`、`/reports`、`/models`、`/plugins`、`/agents` 快捷入口。
- `Agents` 页面读取 `GET /agents` 或 Java Gateway 的 `GET /api/agents`，展示 Agent 注册中心元信息。
- `DemoHero` 展示项目名称、当前模型、演示案例和运行状态。
- `DemoWorkflowStage` 基于运行状态回放需求输入、Product、Coder、Tester、Runner、Sentry、修复、Quality 和 Report 阶段。
- `RepairHighlight` 基于 `retry_count`、`error_summary`、`sentry_result` 和测试结果展示自动修复高光。
- `DemoResultSummary` 展示成功状态、修复次数、pytest、覆盖率、质量评分、安全状态和报告路径。
- `DemoNarrationPanel` 生成不超过 8 条答辩讲解提示。

## Java Spring Boot 调用示例

```java
import java.util.List;

import org.springframework.http.MediaType;
import org.springframework.web.reactive.function.client.WebClient;

record RunRequest(
    String requirement,
    String model_provider,
    List<String> enabled_plugins,
    int max_retry_count,
    boolean require_human_approval,
    boolean demo_mode,
    boolean offline_mode
) {}

WebClient client = WebClient.builder()
    .baseUrl("http://localhost:8001")
    .build();

String responseJson = client.post()
    .uri("/runs")
    .contentType(MediaType.APPLICATION_JSON)
    .bodyValue(new RunRequest(
        "写一个函数 get_second_largest(nums)，返回第二大的不同数字",
        "deepseek",
        List.of("Doc Agent", "Security Agent"),
        3,
        false,
        true,
        false
    ))
    .retrieve()
    .bodyToMono(String.class)
    .block();
```

## 前后端解耦约定

- Vue 前端优先读取 `ui_view_model` 渲染页面。
- Java 后端只做任务、权限、审计和业务元数据，不解析 LangGraph state。
- Python Agent Engine 继续负责 Agent、LangGraph、插件、报告和运行历史。
- `state` 只在历史详情和调试场景使用，不能作为正式前端的强依赖。

## Platform Human Approval API

### POST `/api/platform/runs/{platformRunId}/approval`

Java Gateway 模式下用于提交 Human Approval 节点的人工确认结果。该接口只写入平台任务状态和 RunEvent，不会动态改写 LangGraph。

请求：

```json
{
  "approved": true,
  "comment": "确认继续执行后续节点"
}
```

响应：

```json
{
  "success": true,
  "message": "ok",
  "data": {
    "platformRunId": "workflow_template_20260526_034500_ab12cd34",
    "status": "APPROVED",
    "approved": true,
    "requireHumanApproval": false
  }
}
```

相关事件：

- `HUMAN_APPROVAL_REQUIRED`
- `HUMAN_APPROVED`
- `HUMAN_REJECTED`
- `STATUS_CHANGED`

## Platform Workflow Runtime Lite API

### POST `/api/platform/workflows/templates/{templateKey}/execute`

Java Gateway 模式下执行 MySQL 中保存的 Workflow 模板。该接口属于平台层演示执行器：它会读取模板节点与连线，按拓扑顺序记录 RunEvent 并通过 SSE 推送；`code_agent` 节点会调用现有 Python CodeAgent 执行文件操作，`human_approval` 节点会让任务进入 `WAITING_FOR_HUMAN`，其它 Agent 节点第一版作为 `simulated` 平台事件，不动态改写 LangGraph。

请求：

```json
{
  "input_data": {
    "requirement": "执行 Workflow Runtime Lite: CodeAgent 文件夹演示",
    "runtime_mode": "workflow_runtime_lite"
  }
}
```

响应：

```json
{
  "success": true,
  "message": "ok",
  "data": {
    "platformRunId": "workflow_runtime_1780000000000",
    "run_id": "workflow_runtime_1780000000000",
    "template_key": "codeagent_demo",
    "status": "WAITING_FOR_HUMAN",
    "events": [],
    "workflow_events": [],
    "warnings": [],
    "run_summary": {
      "runner_mode": "workflow_runtime",
      "runtime_mode": "workflow_runtime_lite",
      "require_human_approval": true
    },
    "ui_view_model": {
      "workflow_steps": [],
      "workflow_events": []
    }
  }
}
```

执行模式标记：

- `executed`：真实执行节点，目前主要是 CodeAgent。
- `simulated`：平台事件节点，例如 Product / Coder / Tester 等 no-op 节点。
- `waiting`：Human Approval 节点等待人工确认。

边界：

- 不修改 Python FastAPI `/runs`。
- 不动态改写 LangGraph 执行拓扑。
- 不改变 `run_summary`、`ui_view_model`、`workflow_events` 兼容结构。

## Platform Model Secret API

### GET `/api/platform/secrets/models`

返回模型 API Key 配置状态。该接口不会返回明文密钥。

```json
{
  "success": true,
  "message": "ok",
  "data": [
    {
      "provider": "deepseek",
      "name": "DeepSeek",
      "envKey": "DEEPSEEK_API_KEY",
      "configured": true,
      "stored": true,
      "envConfigured": false,
      "maskedKey": "sk-****abcd",
      "updatedAt": "2026-05-26T11:40:00",
      "message": "密钥已加密保存到 Java 平台层。当前不会通过 GET 接口返回明文。"
    }
  ]
}
```

### POST `/api/platform/secrets/models/{provider}`

提交一次新的模型 API Key。明文只允许出现在请求体中，Java 保存加密值，前端不写入 localStorage。

```json
{
  "apiKey": "sk-..."
}
```

### DELETE `/api/platform/secrets/models/{provider}`

清除 Java 平台层保存的模型 API Key。Python Direct 模式仍通过 `.env` 管理密钥。

## Platform Workspace API

Java Gateway 模式下用于管理 CodeAgent 文件夹模式的受控工作区。Workspace 是平台体验层配置，用于 Vue 默认填充文件夹路径、dry-run、备份和读取限制；Python CodeAgent 仍会依据 `config/settings.yaml` 做最终路径白名单和阻断校验。

### GET `/api/platform/workspaces`

返回平台层保存的 Workspace 列表。如果数据库为空，Java 会初始化一个默认演示工作区。

```json
{
  "success": true,
  "message": "ok",
  "data": [
    {
      "id": 1,
      "name": "CodeAgent Demo Workspace",
      "rootPath": "output/code_agent_workspace",
      "enabled": true,
      "isDefault": true,
      "description": "默认受控文件夹工作区。",
      "maxFiles": 80,
      "maxReadChars": 500000,
      "dryRunDefault": true,
      "backupBeforeWrite": true
    }
  ]
}
```

### POST `/api/platform/workspaces`

新增 Workspace。若请求中 `isDefault=true`，Java 会取消其他 Workspace 的默认状态。

### PUT `/api/platform/workspaces/{id}`

更新 Workspace。默认 Workspace 不允许被更新成禁用状态；如果设为默认，会自动启用。

### DELETE `/api/platform/workspaces/{id}`

删除 Workspace。若删除的是默认 Workspace，Java 会把剩余第一条工作区设为默认。

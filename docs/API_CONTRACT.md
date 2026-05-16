# Python Agent Engine API Contract

本文记录 v2.0 Python Agent Engine FastAPI 预览接口。API 层只负责 HTTP 请求/响应适配，业务逻辑统一调用 `services/run_service.py`，前端和 Java 后端优先消费 `run_summary` 与 `ui_view_model`，不直接耦合 LangGraph 内部 state。

启动方式：

```powershell
python -m uvicorn api_server:app --reload --port 8000
```

默认地址：

```text
http://localhost:8000
```

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
    "report_path": "reports/run_20260516_124408.md"
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
    "report_path": "reports/run_20260516_124408.md"
  },
  "ui_view_model": {
    "header": {},
    "summary_cards": {},
    "workflow_steps": [],
    "agent_outputs": {},
    "plugin_outputs": {},
    "report": {},
    "result_index": {},
    "raw": {}
  }
}
```

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

当前 `frontend-vue/` 使用 Axios 封装 API 客户端，基础地址来自 `.env.development`：

```text
VITE_API_BASE_URL=http://127.0.0.1:8001
```

`src/api/client.ts`：

```ts
import axios from "axios";

const baseURL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8001";

export const apiClient = axios.create({
  baseURL,
  timeout: 600000,
  headers: {
    "Content-Type": "application/json",
  },
});
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
export const getHealth = () => apiClient.get("/health").then((response) => response.data);
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

如果 `GET /health` 失败，顶部显示“Python Agent Engine API 未连接”；如果某个列表接口失败，仅对应卡片显示错误或 Empty 状态。

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

当前后端暂不提供流式阶段事件，Vue 演示模式会在请求返回后基于 `run_summary` 和 `ui_view_model` 回放工作流阶段、自动修复高光、最终质量评分和报告结果。请求失败时展示“演示运行失败”，并提示检查 Python Agent Engine API。

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
- `WorkflowTimeline` 读取 `ui_view_model.workflow_steps`，按 `order` 展示节点。
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
- `QuickActions` 提供 `/runs/new`、`/history`、`/reports`、`/models`、`/plugins` 快捷入口。
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
    .baseUrl("http://localhost:8000")
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

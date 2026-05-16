# API Contract 草案

本文记录未来 FastAPI、Vue/TypeScript、Java Spring Boot 可复用的接口结构。v1.0 仍使用 Streamlit，但 Web UI 已通过 `services/run_service.py` 的 Application Service 层调用工作流，返回结构统一为：

```json
{
  "state": {},
  "run_summary": {},
  "ui_view_model": {}
}
```

`ui_view_model` 是前端优先使用的数据结构，负责 Header、摘要卡片、工作流节点、Agent 输出、插件输出、报告入口和结果索引。

## POST /runs

创建一次 AI 工作流运行。

### Request

```json
{
  "requirement": "写一个函数 get_second_largest(nums)，返回第二大的不同数字",
  "model_provider": "deepseek",
  "enabled_plugins": ["Doc Agent", "Security Agent", "Refactor Agent", "UI Agent"],
  "max_retry_count": 3,
  "require_human_approval": true,
  "approved": true,
  "demo_mode": true,
  "offline_mode": false
}
```

说明：

- `requirement`：用户需求，必填。
- `model_provider`：模型服务商，例如 `deepseek`、`qwen`、`zhipu`。
- `enabled_plugins`：本次展示层记录的启用插件名称。
- `max_retry_count`：最大自动修复次数。
- `require_human_approval`：是否启用人工审批。
- `approved`：是否已通过人工审批。未来接口可显式传入，Streamlit 当前由 checkbox 生成。
- `demo_mode`：是否以演示模式展示。
- `offline_mode`：是否启用离线兜底展示。

### Response

```json
{
  "state": {
    "run_id": "run_20260427_153000",
    "requirement": "写一个函数 get_second_largest(nums)，返回第二大的不同数字",
    "success": true,
    "retry_count": 1,
    "test_success": true,
    "coverage_percent": 86,
    "quality_score": 90,
    "report_path": "reports/run_20260427_153000.md"
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
    "report_path": "reports/run_20260427_153000.md"
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

## GET /runs/{run_id}

读取某次历史运行。

### Response

返回结构与 `POST /runs` 一致：

```json
{
  "state": {},
  "run_summary": {},
  "ui_view_model": {}
}
```

前端展示历史详情时优先读取 `ui_view_model`，开发模式才读取 `raw.state`。

## GET /runs

读取历史运行列表。

### Response

```json
[
  {
    "run_id": "run_20260427_153000",
    "success": true,
    "retry_count": 1,
    "test_success": true,
    "quality_score": 90,
    "model_provider": "deepseek",
    "model_name": "deepseek-chat",
    "requirement": "写一个函数 get_second_largest(nums)",
    "report_path": "reports/run_20260427_153000.md",
    "state_path": "runs/run_20260427_153000.json"
  }
]
```

## GET /models

读取可选模型列表。

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
    "offline_mode": false
  }
]
```

## GET /plugins

读取插件列表和启用状态。

### Response

```json
[
  {
    "name": "security_agent",
    "display_name": "Security Agent",
    "description": "检查最终代码是否包含危险操作",
    "enabled": true
  }
]
```

## GET /reports

读取最新 Markdown 报告。

### Response

```json
{
  "exists": true,
  "path": "reports/run_20260427_153000.md",
  "name": "run_20260427_153000.md",
  "content": "# AI Multi-Agent Pipeline 运行报告...",
  "success": true,
  "error_summary": "无错误"
}
```

## 与 ui_view_model 的关系

- API 层负责调用 `services.run_service`。
- 前端页面优先读取 `ui_view_model`，避免重复解析原始 `state`。
- `state` 保留完整调试信息，用于开发模式、历史回放和问题定位。
- `run_summary` 用于列表页、卡片、报告摘要和模型对比。
- CLI 当前可继续使用原有 `graph_demo.py`，后续也可以迁移到 `run_service`，保持与 Web UI 相同的返回结构。

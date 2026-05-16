from datetime import datetime
from pathlib import Path

from config.config_loader import get_setting
from graph import run_graph_demo
from model_manager import (
    get_available_models as load_model_configs,
    get_current_model_info,
    is_offline_mode,
)
from plugin_loader import PLUGIN_CLASSES, load_plugin_config
from report_generator import (
    build_error_summary_section,
    build_plugin_results_section,
    build_run_summary_section,
)
from utils.model_comparator import save_compare_report
from utils.run_store import (
    create_run_id,
    get_latest_run as get_latest_run_id,
    get_run_state_path,
    list_runs,
    load_run_state,
    save_run_state,
)
from utils.summary_builder import build_run_summary
from utils.ui_state_builder import build_report_display_data, build_ui_view_model


REPORT_DIR = Path("reports")
LATEST_REPORT_FILE = REPORT_DIR / "latest_report.md"


def build_markdown_report(state):
    run_summary = build_run_summary(state)
    success_text = "成功" if run_summary["success"] else "失败"
    enabled_plugins_text = "、".join(run_summary["enabled_plugins"]) or "无"

    return f"""# AI Multi-Agent Pipeline 运行报告

## 用户需求

{state.get("requirement", "")}

## 运行结果

- run_id：{state.get("run_id", "未生成")}
- 运行时间：{state.get("run_time", "未记录")}
- 模型服务商：{run_summary["model_provider"]}
- 模型名称：{state.get("model_name", "未记录")}
- base_url：{state.get("model_base_url", "未记录")}
- 是否成功：{success_text}
- 修复次数：{run_summary["retry_count"]}
- 最大修复次数：{state.get("max_retry_count", get_setting("max_retry_count"))}
- pytest 是否通过：{"是" if run_summary["test_success"] else "否"}
- 测试覆盖率：{run_summary["coverage_percent"]}%
- 质量评分：{run_summary["quality_score"]}
- 安全状态：{run_summary["security_status"]}
- 已启用插件：{enabled_plugins_text}
- 是否启用人工审批：{"是" if state.get("require_human_approval") else "否"}
- 是否通过审批：{"是" if state.get("approved") else "否"}
- 审批说明：{state.get("approval_message", "无")}
- 状态文件路径：{state.get("state_path", "未保存")}
- 报告文件路径：{run_summary["report_path"]}

{build_run_summary_section(state)}

## Product Agent

{state.get("product_result", "")}

## Coder Agent 生成代码

```python
{state.get("code", "")}
```

## Tester Agent

{state.get("tester_result", "")}

{build_error_summary_section(state)}

## pytest 自动测试

- test_success：{"通过" if state.get("test_success") else "未通过"}

### 自动生成的 pytest 测试代码

```python
{state.get("test_code", "")}
```

### pytest stdout

```text
{state.get("test_stdout", "")}
```

### pytest stderr

```text
{state.get("test_stderr", "")}
```

### coverage report

```text
{state.get("coverage_stdout", "")}
```

## 质量评分

- coverage_percent：{run_summary["coverage_percent"]}%
- quality_score：{run_summary["quality_score"]}
- 自动修复次数：{run_summary["retry_count"]}
- 安全检查结果：{run_summary["security_status"]}

```text
{state.get("quality_summary", "")}
```

## 测试驱动修复过程

当 pytest 或 Runner 任一失败时，系统会将测试失败信息、运行错误日志和 Sentry Agent 分析结果反馈给 Coder Agent，要求修复业务代码本身，而不是修改测试用例。

## Sentry Agent

{state.get("sentry_result", "")}

{build_plugin_results_section(state)}

## stdout

```text
{state.get("stdout", "")}
```

## stderr

```text
{state.get("error_log", "")}
```

## Refactor Agent

{state.get("refactor_result", "")}

## UI Agent

{state.get("ui_result", "")}
"""


def save_report(report, report_file=None):
    REPORT_DIR.mkdir(exist_ok=True)
    target_file = Path(report_file) if report_file else LATEST_REPORT_FILE
    target_file.parent.mkdir(exist_ok=True)
    target_file.write_text(report, encoding="utf-8")
    LATEST_REPORT_FILE.write_text(report, encoding="utf-8")
    return target_file


def _build_approval_message(request, approved):
    if not request.get("require_human_approval", True):
        return "未启用人工审批，系统自动通过。"

    if request.get("approval_message"):
        return request["approval_message"]

    if approved:
        return "人工审批通过，允许运行 AI 生成代码。"

    return "等待人工确认：用户未批准执行 AI 生成代码，已停止执行 Runner。"


def _build_response(state):
    run_summary = build_run_summary(state)
    return {
        "run_id": state.get("run_id", ""),
        "state": state,
        "run_summary": run_summary,
        "ui_view_model": build_ui_view_model(state, run_summary),
    }


def create_run(request: dict) -> dict:
    """Run the AI workflow once and return state, run_summary and ui_view_model."""
    request = request or {}
    requirement = str(request.get("requirement", "")).strip()

    if not requirement:
        raise ValueError("requirement 不能为空")

    max_retry_count = int(request.get("max_retry_count", get_setting("max_retry_count", 3)) or 3)
    model_provider = request.get(
        "model_provider",
        get_setting("default_model_provider", "deepseek"),
    )
    require_human_approval = bool(request.get("require_human_approval", True))
    approved = bool(request.get("approved", not require_human_approval))
    approval_message = _build_approval_message(request, approved)
    progress_callback = request.get("_progress_callback")

    state = run_graph_demo(
        requirement,
        progress_callback=progress_callback,
        max_retry_count=max_retry_count,
        require_human_approval=require_human_approval,
        approved=approved,
        model_provider=model_provider,
        approval_message=approval_message,
    )

    run_id = request.get("_run_id") or create_run_id()
    state_path = get_run_state_path(run_id)
    report_file = REPORT_DIR / f"{run_id}.md"

    state["run_id"] = run_id
    state["run_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    state["enabled_plugins"] = request.get("enabled_plugins", state.get("enabled_plugins", []))
    state["demo_mode"] = bool(request.get("demo_mode", True))
    state["offline_mode"] = bool(request.get("offline_mode", is_offline_mode()))
    state["state_path"] = str(state_path)
    state["report_path"] = str(report_file)

    report = build_markdown_report(state)
    save_report(report, report_file)
    save_run_state(run_id, state)

    return _build_response(state)


def get_run(run_id: str) -> dict:
    """Load one saved run and return the same response shape as create_run."""
    state = load_run_state(run_id)

    if not state:
        return {
            "run_id": run_id,
            "found": False,
            "state": {},
            "run_summary": {},
            "ui_view_model": build_ui_view_model({}),
        }

    state.setdefault("run_id", run_id)
    state.setdefault("state_path", str(get_run_state_path(run_id)))
    response = _build_response(state)
    response["found"] = True
    return response


def list_run_history() -> list[dict]:
    """Return lightweight run history rows for UI or API list pages."""
    history = []

    for run_id in list_runs():
        state = load_run_state(run_id) or {}
        run_summary = build_run_summary(state)
        history.append(
            {
                "run_id": run_id,
                "run_summary": run_summary,
                "success": run_summary.get("success", False),
                "retry_count": run_summary.get("retry_count", 0),
                "test_success": run_summary.get("test_success", False),
                "quality_score": run_summary.get("quality_score", 0),
                "model_provider": run_summary.get("model_provider", ""),
                "model_name": state.get("model_name", ""),
                "requirement": state.get("requirement", ""),
                "report_path": run_summary.get("report_path", ""),
                "state_path": state.get("state_path", str(get_run_state_path(run_id))),
            }
        )

    return history


def list_reports() -> list[dict]:
    """Return Markdown reports saved under reports/, newest first."""
    if not REPORT_DIR.exists():
        return []

    report_files = sorted(
        REPORT_DIR.glob("*.md"),
        key=lambda file: file.stat().st_mtime,
        reverse=True,
    )

    reports = []
    for report_file in report_files:
        file_stat = report_file.stat()
        reports.append(
            {
                "name": report_file.name,
                "path": str(report_file),
                "size": file_stat.st_size,
                "modified_time": datetime.fromtimestamp(file_stat.st_mtime).strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
            }
        )

    return reports


def get_report(report_name: str) -> dict:
    """Return one Markdown report by filename, guarding against path traversal."""
    if not report_name:
        raise ValueError("report_name 不能为空")

    report_root = REPORT_DIR.resolve()
    report_file = (REPORT_DIR / report_name).resolve()

    if report_file.parent != report_root:
        raise ValueError("report_name 只能是 reports/ 目录下的文件名")

    if report_file.suffix.lower() != ".md":
        raise ValueError("只支持读取 Markdown 报告")

    if not report_file.exists():
        raise FileNotFoundError(f"报告不存在：{report_name}")

    return {
        "name": report_file.name,
        "path": str(REPORT_DIR / report_file.name),
        "content": report_file.read_text(encoding="utf-8"),
    }


def get_latest_report() -> dict:
    """Return latest Markdown report metadata and content."""
    latest_run_id = get_latest_run_id()
    state = load_run_state(latest_run_id) if latest_run_id else {}
    return build_report_display_data(state or {})


def get_available_models() -> list[dict]:
    """Return configured model choices for UI or future API clients."""
    models = []

    for item in load_model_configs():
        model_info = dict(item)
        provider = model_info.get("provider", "")
        current_info = get_current_model_info(provider)
        model_info.setdefault("name", current_info.get("name", provider))
        model_info.setdefault("model", current_info.get("model", ""))
        model_info.setdefault("base_url", current_info.get("base_url", ""))
        model_info["offline_mode"] = is_offline_mode()
        models.append(model_info)

    return models


def get_available_plugins() -> list[dict]:
    """Return plugin metadata and enabled state from config/agents.yaml."""
    plugins = []

    for item in load_plugin_config():
        plugin_name = item.get("name", "")
        plugin_class = PLUGIN_CLASSES.get(plugin_name)

        if plugin_class:
            plugin = plugin_class()
            display_name = plugin.name
            description = plugin.description
        else:
            display_name = plugin_name or "Unknown Plugin"
            description = "plugin_loader.py 中未登记该插件"

        plugins.append(
            {
                "name": plugin_name,
                "display_name": display_name,
                "description": description,
                "enabled": bool(item.get("enabled", False)),
            }
        )

    return plugins


def create_compare_report(compare_run_id, states):
    """Save a Markdown comparison report for multi-model runs."""
    return save_compare_report(compare_run_id, states)

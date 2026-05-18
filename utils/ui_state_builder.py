from pathlib import Path

from utils.error_utils import summarize_error
from utils.summary_builder import build_run_summary


WORKFLOW_STEP_DEFINITIONS = [
    ("requirement", "Requirement"),
    ("product", "Product Agent"),
    ("coder", "Coder Agent"),
    ("tester", "Tester Agent"),
    ("approval", "Approval Node"),
    ("runner", "Runner"),
    ("sentry", "Sentry Agent"),
    ("plugins", "Plugins"),
    ("quality", "Quality"),
    ("report", "Report"),
]

WORKFLOW_STEPS = [label for _, label in WORKFLOW_STEP_DEFINITIONS]

PLUGIN_DISPLAY_ITEMS = [
    ("doc_agent", "doc_result", "Doc Agent"),
    ("security_agent", "security_result", "Security Agent"),
    ("refactor_agent", "refactor_result", "Refactor Agent"),
    ("ui_agent", "ui_result", "UI Agent"),
]

REPORT_DIR = Path("reports")
LATEST_REPORT_FILE = REPORT_DIR / "latest_report.md"


def _status_to_title(status):
    return str(status or "waiting").strip().lower().title()


def _base_workflow_status():
    return {key: "waiting" for key, _ in WORKFLOW_STEP_DEFINITIONS}


def _apply_completed_state(status, state):
    if not state:
        return status

    if state.get("requirement"):
        status["requirement"] = "done"
    if state.get("product_result"):
        status["product"] = "done"
    if state.get("code"):
        status["coder"] = "done"
    if state.get("tester_result") or state.get("test_code"):
        status["tester"] = "done"
    if state.get("approval_message") or state.get("approved") is not None:
        status["approval"] = "done" if state.get("approved", True) else "failed"
    if state.get("approved") is not False and (
        state.get("stdout") or state.get("error_log") or state.get("success")
    ):
        status["runner"] = "done" if state.get("success") and state.get("test_success") else "failed"
    if state.get("approved") is False:
        status["runner"] = "skipped"
    if state.get("sentry_result"):
        status["sentry"] = "done"
    if state.get("plugin_results"):
        status["plugins"] = "done"
    if state.get("quality_summary") or state.get("quality_score"):
        status["quality"] = "done"
    if state.get("report_path") or state.get("run_id"):
        status["report"] = "done"

    return status


def _workflow_summary(key, state):
    state = state or {}
    summaries = {
        "requirement": state.get("requirement", "等待用户输入需求"),
        "product": state.get("product_result", "等待 Product Agent 拆解需求"),
        "coder": "已生成代码" if state.get("code") else "等待 Coder Agent 生成代码",
        "tester": "已生成 pytest 测试" if state.get("test_code") else "等待 Tester Agent 生成测试",
        "approval": state.get("approval_message", "等待人工审批"),
        "runner": state.get("stdout") or state.get("error_log") or "等待 Runner 执行代码",
        "sentry": state.get("sentry_result", "未触发 Sentry Agent"),
        "plugins": "插件已执行" if state.get("plugin_results") else "等待插件执行",
        "quality": state.get("quality_summary", "等待质量评分"),
        "report": state.get("report_path", "等待报告生成"),
    }

    return summaries.get(key, "")


def build_workflow_status(state: dict) -> list[dict]:
    """Build display-ready workflow steps from state plus optional _current_node."""
    state = state or {}
    status = _apply_completed_state(_base_workflow_status(), state)
    current_node = state.get("_current_node", "")
    max_retry_count = int(state.get("_max_retry_count", state.get("max_retry_count", 3)) or 3)

    if current_node == "start":
        status["requirement"] = "done"
        status["product"] = "running"

    if current_node == "product_node":
        status["product"] = "done"
        status["coder"] = "running"

    if current_node == "coder_node":
        status["coder"] = "done"
        status["tester"] = "running"

    if current_node == "tester_node":
        status["tester"] = "done"
        status["approval"] = "running"

    if current_node == "approval_node":
        if state.get("approved"):
            status["approval"] = "done"
            status["runner"] = "running"
        else:
            status["approval"] = "failed"
            status["runner"] = "skipped"
            status["plugins"] = "running"

    if current_node == "runner_node":
        if state.get("success") and state.get("test_success"):
            status["runner"] = "done"
            status["plugins"] = "running"
        else:
            status["runner"] = "failed"
            if int(state.get("retry_count", 0) or 0) >= max_retry_count:
                status["plugins"] = "running"
            else:
                status["sentry"] = "repairing"

    if current_node == "sentry_node":
        status["sentry"] = "done"
        status["coder"] = "repairing"
        status["tester"] = "waiting"
        status["approval"] = "waiting"
        status["runner"] = "waiting"

    if current_node == "plugins_node":
        status["plugins"] = "done"
        status["quality"] = "running"

    if current_node == "quality_node":
        status["quality"] = "done"
        status["report"] = "running"

    if current_node == "report_node":
        status["report"] = "done"

    if current_node == "error":
        status["report"] = "failed"

    return [
        {
            "key": key,
            "label": label,
            "status": status.get(key, "waiting"),
            "summary": _workflow_summary(key, state),
            "order": index + 1,
        }
        for index, (key, label) in enumerate(WORKFLOW_STEP_DEFINITIONS)
    ]


def build_workflow_status_map(state: dict) -> dict:
    """Build the legacy label -> TitleCase status map used by the current Streamlit UI."""
    return {
        item["label"]: _status_to_title(item["status"])
        for item in build_workflow_status(state)
    }


def build_result_index(state: dict, run_summary: dict | None = None) -> dict:
    """Build quick lookup flags for important run outputs."""
    state = state or {}
    run_summary = run_summary or build_run_summary(state)
    report_path = run_summary.get("report_path") or state.get("report_path", "")
    report_available = bool(report_path and report_path != "未生成")

    return {
        "run_id": state.get("run_id", ""),
        "final_code_available": bool(state.get("code")),
        "test_result_available": bool(state.get("test_code") or state.get("test_stdout") or state.get("test_stderr")),
        "error_available": bool(state.get("error_log") or state.get("test_stderr")),
        "report_available": report_available,
        "quality_available": bool(state.get("quality_summary") or state.get("quality_score") is not None),
        "plugins_available": bool(state.get("plugin_results")),
    }


def build_ui_view_model(state: dict, run_summary: dict | None = None) -> dict:
    """Build a stable UI ViewModel from raw LangGraph state."""
    state = state or {}
    run_summary = run_summary or build_run_summary(state)
    report_data = build_report_display_data(state)

    return {
        "header": {
            "title": "AI Multi-Agent Pipeline",
            "subtitle": "多 Agent 自动开发流水线演示控制台",
            "run_status": state.get("_run_status", "Waiting"),
            "model_name": state.get("model_name", ""),
            "model_provider": run_summary.get("model_provider", state.get("model_provider", "")),
        },
        "summary_cards": {
            "success": run_summary.get("success", False),
            "retry_count": run_summary.get("retry_count", 0),
            "test_success": run_summary.get("test_success", False),
            "coverage_percent": run_summary.get("coverage_percent", 0),
            "quality_score": run_summary.get("quality_score", 0),
            "security_status": run_summary.get("security_status", "等待安全检查"),
            "report_path": run_summary.get("report_path", state.get("report_path", "未生成")),
            "runner_mode": run_summary.get("runner_mode", state.get("runner_mode", "python")),
            "runner_warning": run_summary.get("runner_warning", state.get("runner_warning", "")),
        },
        "workflow_steps": build_workflow_status(state),
        "workflow_events": state.get("workflow_events", []) if isinstance(state.get("workflow_events", []), list) else [],
        "agent_outputs": {
            "product_result": state.get("product_result", ""),
            "code": state.get("code", ""),
            "tester_result": state.get("tester_result", ""),
            "sentry_result": state.get("sentry_result", ""),
            "stdout": state.get("stdout", ""),
            "error_summary": summarize_error(state.get("error_log", "")),
            "error_log": state.get("error_log", ""),
        },
        "plugin_outputs": {
            "plugin_results": state.get("plugin_results", []),
            "doc_result": state.get("doc_result", ""),
            "security_result": state.get("security_result", ""),
            "refactor_result": state.get("refactor_result", ""),
            "ui_result": state.get("ui_result", ""),
        },
        "report": {
            "report_path": report_data.get("path") or state.get("report_path", ""),
            "report_markdown": report_data.get("content", ""),
            "run_id": state.get("run_id", ""),
        },
        "result_index": build_result_index(state, run_summary),
        "raw": {
            "state": state,
            "run_summary": run_summary,
        },
    }


def _legacy_plugin_status(content, enabled=True):
    if not enabled:
        return "disabled", "未启用"
    if not content:
        return "warning", "等待输出"
    if any(word in content for word in ["失败", "错误", "危险", "禁止", "Error", "Exception"]):
        return "failed", "风险"
    if any(word in content for word in ["风险", "警告", "建议", "需要", "可优化"]):
        return "warning", "建议"
    return "success", "通过"


def build_plugin_display_data(state):
    """Build display-ready plugin rows, preferring standardized plugin_results."""
    state = state or {}
    plugin_results = state.get("plugin_results", []) or []
    result_map = {
        item.get("plugin_name", item.get("name", "")): item
        for item in plugin_results
        if isinstance(item, dict)
    }

    rows = []
    for plugin_key, field_name, display_name in PLUGIN_DISPLAY_ITEMS:
        result = result_map.get(display_name)
        if result:
            status = result.get("status", "warning")
            rows.append(
                {
                    "plugin_key": plugin_key,
                    "field_name": field_name,
                    "display_name": display_name,
                    "status": status,
                    "summary": result.get("summary", "无摘要"),
                    "detail": result.get("detail", ""),
                    "enabled": status != "disabled",
                }
            )
            continue

        content = state.get(field_name, "")
        status, summary = _legacy_plugin_status(content, enabled=True)
        rows.append(
            {
                "plugin_key": plugin_key,
                "field_name": field_name,
                "display_name": display_name,
                "status": status,
                "summary": summary,
                "detail": content,
                "enabled": status != "disabled",
            }
        )

    return rows


def _get_latest_report_file():
    if not REPORT_DIR.exists():
        return None

    report_files = sorted(
        REPORT_DIR.glob("report_*.md"),
        key=lambda file: file.stat().st_mtime,
        reverse=True,
    )

    if report_files:
        return report_files[0]

    if LATEST_REPORT_FILE.exists():
        return LATEST_REPORT_FILE

    return None


def _detect_report_success(report_content):
    success_markers = ["✅", "是否成功：成功", "success: True", "success：True", "运行成功"]
    fail_markers = ["❌", "是否成功：失败", "success: False", "success：False", "运行失败"]

    if any(marker in report_content for marker in success_markers):
        return True

    if any(marker in report_content for marker in fail_markers):
        return False

    return None


def build_report_display_data(state):
    """Build display-ready report data from state or latest report file."""
    state = state or {}
    report_path = state.get("report_path") or state.get("latest_report")
    report_file = Path(report_path) if report_path else _get_latest_report_file()

    if not report_file or not report_file.exists():
        return {
            "exists": False,
            "path": "",
            "name": "暂无报告",
            "content": "",
            "success": None,
            "error_summary": "无错误",
        }

    content = report_file.read_text(encoding="utf-8")
    return {
        "exists": True,
        "path": str(report_file),
        "name": report_file.name,
        "content": content,
        "success": _detect_report_success(content),
        "error_summary": summarize_error(content),
    }

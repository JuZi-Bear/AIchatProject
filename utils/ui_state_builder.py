from pathlib import Path

from utils.error_utils import summarize_error


WORKFLOW_STEPS = [
    "Requirement",
    "Product Agent",
    "Coder Agent",
    "Tester Agent",
    "Approval Node",
    "Runner",
    "Sentry Agent",
    "Plugins",
    "Quality",
    "Report",
]

PLUGIN_DISPLAY_ITEMS = [
    ("doc_agent", "doc_result", "Doc Agent"),
    ("security_agent", "security_result", "Security Agent"),
    ("refactor_agent", "refactor_result", "Refactor Agent"),
    ("ui_agent", "ui_result", "UI Agent"),
]

REPORT_DIR = Path("reports")
LATEST_REPORT_FILE = REPORT_DIR / "latest_report.md"


def _base_workflow_status():
    return {step: "Waiting" for step in WORKFLOW_STEPS}


def _apply_completed_state(status, state):
    if not state:
        return status

    if state.get("requirement"):
        status["Requirement"] = "Done"
    if state.get("product_result"):
        status["Product Agent"] = "Done"
    if state.get("code"):
        status["Coder Agent"] = "Done"
    if state.get("tester_result") or state.get("test_code"):
        status["Tester Agent"] = "Done"
    if state.get("approval_message") or state.get("approved") is not None:
        status["Approval Node"] = "Done" if state.get("approved", True) else "Failed"
    if state.get("approved") is not False and (
        state.get("stdout") or state.get("error_log") or state.get("success")
    ):
        status["Runner"] = "Done" if state.get("success") and state.get("test_success") else "Failed"
    if state.get("sentry_result"):
        status["Sentry Agent"] = "Done"
    if state.get("plugin_results"):
        status["Plugins"] = "Done"
    if state.get("quality_summary") or state.get("quality_score"):
        status["Quality"] = "Done"
    if state.get("report_path") or state.get("run_id"):
        status["Report"] = "Done"

    return status


def build_workflow_status(state):
    """Build Agent workflow node status from state plus optional _current_node."""
    state = state or {}
    status = _apply_completed_state(_base_workflow_status(), state)
    current_node = state.get("_current_node", "")
    max_retry_count = int(state.get("_max_retry_count", state.get("max_retry_count", 3)) or 3)

    if current_node == "start":
        status["Requirement"] = "Done"
        status["Product Agent"] = "Running"

    if current_node == "product_node":
        status["Product Agent"] = "Done"
        status["Coder Agent"] = "Running"

    if current_node == "coder_node":
        status["Coder Agent"] = "Done"
        status["Tester Agent"] = "Running"

    if current_node == "tester_node":
        status["Tester Agent"] = "Done"
        status["Approval Node"] = "Running"

    if current_node == "approval_node":
        if state.get("approved"):
            status["Approval Node"] = "Done"
            status["Runner"] = "Running"
        else:
            status["Approval Node"] = "Failed"
            status["Plugins"] = "Running"

    if current_node == "runner_node":
        if state.get("success") and state.get("test_success"):
            status["Runner"] = "Done"
            status["Plugins"] = "Running"
        else:
            status["Runner"] = "Failed"
            if int(state.get("retry_count", 0) or 0) >= max_retry_count:
                status["Plugins"] = "Running"
            else:
                status["Sentry Agent"] = "Repairing"

    if current_node == "sentry_node":
        status["Sentry Agent"] = "Done"
        status["Coder Agent"] = "Repairing"
        status["Tester Agent"] = "Waiting"
        status["Approval Node"] = "Waiting"
        status["Runner"] = "Waiting"

    if current_node == "plugins_node":
        status["Plugins"] = "Done"
        status["Quality"] = "Running"

    if current_node == "quality_node":
        status["Quality"] = "Done"
        status["Report"] = "Running"

    if current_node == "report_node":
        status["Report"] = "Done"

    if current_node == "error":
        status["Report"] = "Failed"

    return status


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

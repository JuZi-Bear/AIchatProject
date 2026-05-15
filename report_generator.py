from utils.error_utils import summarize_error
from utils.summary_builder import build_run_summary


def build_error_summary_section(state):
    """Build a small Markdown section that summarizes runtime and pytest errors."""
    runtime_error = state.get("error_log", "")
    test_error = "\n".join(
        text
        for text in [state.get("test_stderr", ""), state.get("test_stdout", "")]
        if text
    )

    return f"""## 错误摘要

- Runtime：{summarize_error(runtime_error)}
- pytest：{summarize_error(test_error)}
"""


def build_run_summary_section(state):
    """Build a Markdown section for the shared run summary."""
    run_summary = build_run_summary(state)
    enabled_plugins = "、".join(run_summary["enabled_plugins"]) or "无"
    success_text = "成功" if run_summary["success"] else "失败"
    test_success_text = "通过" if run_summary["test_success"] else "未通过"

    return f"""## 运行摘要

- success：{success_text}
- retry_count：{run_summary["retry_count"]}
- test_success：{test_success_text}
- coverage_percent：{run_summary["coverage_percent"]}%
- quality_score：{run_summary["quality_score"]}
- security_status：{run_summary["security_status"]}
- enabled_plugins：{enabled_plugins}
- model_provider：{run_summary["model_provider"]}
- report_path：{run_summary["report_path"]}
"""


def build_plugin_results_section(state):
    """Build a Markdown section from standardized plugin_results."""
    plugin_results = (state or {}).get("plugin_results", [])

    if not plugin_results:
        return "## 插件结果\n\n暂无插件结果。"

    lines = ["## 插件结果"]

    for item in plugin_results:
        plugin_name = item.get("plugin_name", item.get("name", "Plugin"))
        status = item.get("status", "warning")
        summary = item.get("summary", item.get("description", "无摘要"))
        detail = item.get("detail", item.get("content", "无详细输出"))

        lines.append(
            f"""### {plugin_name}

- status：{status}
- summary：{summary}

{detail}
"""
        )

    return "\n".join(lines)

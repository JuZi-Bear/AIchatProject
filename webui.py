import json
from datetime import datetime
from html import escape
from pathlib import Path

import streamlit as st
import yaml

from config.config_loader import get_setting
from demo_cases import DEMO_CASES
from graph import run_graph_demo
from model_manager import (
    get_available_models,
    get_config,
    get_current_model_info,
    get_default_model,
    is_offline_mode,
)
from plugin_loader import CONFIG_FILE, PLUGIN_CLASSES
from report_generator import (
    build_error_summary_section,
    build_plugin_results_section,
    build_run_summary_section,
)
from utils.code_runner import check_code_safety
from utils.error_utils import format_error_for_display, summarize_error
from utils.model_comparator import create_compare_rows, save_compare_report
from utils.run_store import (
    create_run_id,
    get_latest_run,
    get_run_state_path,
    list_runs,
    load_run_state,
    save_run_state,
)
from utils.summary_builder import build_run_summary
from utils.ui_state_builder import (
    build_plugin_display_data,
    build_report_display_data,
    build_workflow_status,
)


REPORT_DIR = Path("reports")
LATEST_REPORT_FILE = REPORT_DIR / "latest_report.md"
LEGACY_REPORT_FILE = Path("output") / "web_report.md"
GENERATED_CODE_FILE = Path("output") / "generated_code.py"

PLUGIN_ORDER = ["doc_agent", "security_agent", "refactor_agent", "ui_agent"]
PLUGIN_RESULT_FIELDS = [
    ("doc_agent", "doc_result", "Doc Agent"),
    ("security_agent", "security_result", "Security Agent"),
    ("refactor_agent", "refactor_result", "Refactor Agent"),
    ("ui_agent", "ui_result", "UI Agent"),
]

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

RUN_STATE_KEYS = [
    "run_id",
    "result_state",
    "run_state",
    "run_status",
    "workflow_status",
    "progress_log",
    "latest_report",
    "report_path",
    "stdout",
    "stderr",
    "test_stdout",
    "test_stderr",
    "coverage_stdout",
    "compare_states",
    "compare_report_path",
    "repair_events",
]

STATUS_LABELS = {
    "Waiting": "等待中",
    "Running": "运行中",
    "Done": "已完成",
    "Failed": "失败",
    "Repairing": "修复中",
}

RUN_STATUS_LABELS = {
    "Waiting": "等待中",
    "Running": "运行中",
    "Completed": "已完成",
    "Failed": "失败",
    "Waiting Approval": "等待人工确认",
}

def get_demo_options():
    return {
        "简单成功案例": DEMO_CASES["1"]["requirement"],
        "翻车修复案例": DEMO_CASES["2"]["requirement"],
        "综合案例": DEMO_CASES["3"]["requirement"],
        "自定义输入": "",
    }


def apply_page_style():
    st.markdown(
        """
        <style>
        .stApp {
            background: #f5f7fb;
            color: #111827;
        }
        .main .block-container {
            max-width: 1440px;
            padding-top: 1.5rem;
            padding-bottom: 3rem;
        }
        section[data-testid="stSidebar"] {
            background: #0f172a;
        }
        section[data-testid="stSidebar"] h1,
        section[data-testid="stSidebar"] h2,
        section[data-testid="stSidebar"] h3,
        section[data-testid="stSidebar"] label,
        section[data-testid="stSidebar"] p {
            color: #f8fafc;
        }
        .dashboard-title {
            background: linear-gradient(135deg, #111827 0%, #1f2937 58%, #0f766e 100%);
            border-radius: 10px;
            padding: 22px 26px;
            color: white;
            margin-bottom: 16px;
        }
        .dashboard-title h1 {
            font-size: 32px;
            margin: 0 0 8px 0;
            letter-spacing: 0;
        }
        .dashboard-title p {
            color: #d1d5db;
            margin: 0;
            font-size: 15px;
        }
        .summary-grid {
            display: grid;
            grid-template-columns: repeat(5, minmax(0, 1fr));
            gap: 12px;
            margin: 12px 0 18px 0;
        }
        .summary-card {
            background: white;
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            padding: 14px 16px;
            box-shadow: 0 8px 20px rgba(15, 23, 42, 0.05);
            min-height: 92px;
        }
        .summary-label {
            color: #64748b;
            font-size: 12px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0;
            margin-bottom: 8px;
        }
        .summary-value {
            color: #111827;
            font-size: 18px;
            font-weight: 800;
            line-height: 1.25;
            word-break: break-word;
        }
        .workflow-grid {
            display: grid;
            grid-template-columns: repeat(5, minmax(0, 1fr));
            gap: 12px;
            margin: 10px 0 18px 0;
        }
        .workflow-node {
            background: white;
            border: 1px solid #e5e7eb;
            border-left: 5px solid #94a3b8;
            border-radius: 8px;
            padding: 12px 14px;
            box-shadow: 0 8px 20px rgba(15, 23, 42, 0.04);
        }
        .workflow-title {
            color: #111827;
            font-weight: 800;
            font-size: 14px;
            margin-bottom: 8px;
        }
        .workflow-status {
            display: inline-block;
            border-radius: 999px;
            padding: 4px 9px;
            font-size: 12px;
            font-weight: 800;
        }
        .status-waiting {
            border-left-color: #94a3b8;
        }
        .status-waiting .workflow-status {
            background: #f1f5f9;
            color: #475569;
        }
        .status-running {
            border-left-color: #2563eb;
        }
        .status-running .workflow-status {
            background: #dbeafe;
            color: #1d4ed8;
        }
        .status-done {
            border-left-color: #16a34a;
        }
        .status-done .workflow-status {
            background: #dcfce7;
            color: #15803d;
        }
        .status-failed {
            border-left-color: #dc2626;
        }
        .status-failed .workflow-status {
            background: #fee2e2;
            color: #b91c1c;
        }
        .status-repairing {
            border-left-color: #eab308;
        }
        .status-repairing .workflow-status {
            background: #fef9c3;
            color: #854d0e;
        }
        .status-retry {
            border-color: #facc15;
            border-left-color: #eab308;
            box-shadow: 0 10px 24px rgba(234, 179, 8, 0.18);
        }
        .status-final-success {
            border-color: #16a34a;
            border-left-color: #15803d;
            box-shadow: 0 10px 24px rgba(22, 163, 74, 0.18);
        }
        .status-final-success .workflow-title {
            color: #15803d;
            font-weight: 900;
        }
        .workflow-meta {
            color: #64748b;
            font-size: 12px;
            font-weight: 700;
            margin-top: 8px;
        }
        .workflow-meta.retry-active {
            color: #a16207;
        }
        .status-final-success .workflow-meta {
            color: #15803d;
        }
        .demo-grid {
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: 12px;
            margin: 10px 0 16px 0;
        }
        .demo-card {
            background: white;
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            padding: 14px 16px;
            min-height: 110px;
            box-shadow: 0 8px 20px rgba(15, 23, 42, 0.04);
        }
        .demo-card.success-card {
            border-color: #86efac;
            background: #f0fdf4;
        }
        .demo-card.fail-card {
            border-color: #fecaca;
            background: #fef2f2;
        }
        .demo-label {
            color: #64748b;
            font-size: 12px;
            font-weight: 800;
            margin-bottom: 8px;
        }
        .demo-value {
            color: #111827;
            font-size: 15px;
            font-weight: 750;
            line-height: 1.45;
        }
        .highlight-box {
            background: #fff7ed;
            border: 1px solid #fed7aa;
            border-left: 6px solid #f97316;
            border-radius: 8px;
            padding: 16px 18px;
            margin: 14px 0 18px 0;
        }
        .highlight-box h3 {
            color: #9a3412;
            margin: 0 0 10px 0;
            font-size: 20px;
        }
        .highlight-box ul {
            margin-bottom: 0;
        }
        .result-grid {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 12px;
            margin: 10px 0 16px 0;
        }
        .result-card {
            background: white;
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            padding: 14px 16px;
            box-shadow: 0 8px 20px rgba(15, 23, 42, 0.04);
            min-height: 88px;
        }
        .result-card.success-card {
            border-color: #86efac;
            background: #f0fdf4;
        }
        .result-card.fail-card {
            border-color: #fecaca;
            background: #fef2f2;
        }
        .plugin-card {
            border: 1px solid #e5e7eb;
            border-left: 6px solid #94a3b8;
            border-radius: 8px;
            background: white;
            padding: 14px 16px;
            margin: 10px 0;
            box-shadow: 0 8px 20px rgba(15, 23, 42, 0.04);
        }
        .plugin-ok {
            border-left-color: #16a34a;
            background: #f0fdf4;
        }
        .plugin-warn {
            border-left-color: #eab308;
            background: #fefce8;
        }
        .plugin-fail {
            border-left-color: #dc2626;
            background: #fef2f2;
        }
        .plugin-disabled {
            border-left-color: #94a3b8;
            background: #f8fafc;
            color: #64748b;
        }
        .plugin-title {
            color: #111827;
            font-weight: 900;
            margin-bottom: 6px;
        }
        .plugin-status {
            display: inline-block;
            border-radius: 999px;
            padding: 3px 9px;
            font-size: 12px;
            font-weight: 850;
            background: #e5e7eb;
            color: #374151;
            margin-bottom: 8px;
        }
        .plugin-ok .plugin-status {
            background: #dcfce7;
            color: #15803d;
        }
        .plugin-warn .plugin-status {
            background: #fef9c3;
            color: #854d0e;
        }
        .plugin-fail .plugin-status {
            background: #fee2e2;
            color: #b91c1c;
        }
        .plugin-disabled .plugin-status {
            background: #e5e7eb;
            color: #64748b;
        }
        .compare-table {
            width: 100%;
            border-collapse: collapse;
            background: white;
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 8px 20px rgba(15, 23, 42, 0.04);
            font-size: 14px;
        }
        .compare-table th {
            background: #111827;
            color: white;
            text-align: left;
            padding: 11px 12px;
        }
        .compare-table td {
            border-top: 1px solid #e5e7eb;
            padding: 10px 12px;
            vertical-align: top;
        }
        .compare-success-best {
            background: #f0fdf4;
        }
        .compare-success-best td {
            background: #f0fdf4;
        }
        .compare-repair-best {
            background: #f7fee7;
        }
        .compare-repair-best td:first-child {
            box-shadow: inset 5px 0 0 #86efac;
        }
        .compare-coverage-best {
            color: #15803d;
            font-weight: 850;
        }
        .compare-quality-best {
            color: #15803d;
            font-weight: 950;
        }
        .report-status-success {
            border: 1px solid #86efac;
            background: #f0fdf4;
            color: #15803d;
            border-radius: 8px;
            padding: 14px 16px;
            font-size: 24px;
            font-weight: 950;
            margin: 10px 0 14px 0;
        }
        .report-status-fail {
            border: 1px solid #fecaca;
            background: #fef2f2;
            color: #b91c1c;
            border-radius: 8px;
            padding: 14px 16px;
            font-size: 24px;
            font-weight: 950;
            margin: 10px 0 14px 0;
        }
        .section-title {
            color: #111827;
            font-size: 18px;
            font-weight: 850;
            margin: 18px 0 10px 0;
        }
        .small-note {
            color: #64748b;
            font-size: 13px;
            margin-top: -4px;
            margin-bottom: 12px;
        }
        @media (max-width: 1100px) {
            .summary-grid,
            .workflow-grid,
            .demo-grid,
            .result-grid {
                grid-template-columns: repeat(2, minmax(0, 1fr));
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def summarize_text(text, max_length=140):
    clean_text = " ".join((text or "").split())

    if not clean_text:
        return "等待输出"

    if len(clean_text) <= max_length:
        return clean_text

    return clean_text[:max_length] + "..."


def summarize_test_result(state):
    if not state:
        return "等待测试"

    if state.get("test_success"):
        return "pytest 自动测试通过"

    test_log = "\n".join(
        text
        for text in [state.get("test_stderr", ""), state.get("test_stdout", "")]
        if text
    )

    if not test_log:
        return "pytest 暂无结果"

    error_summary = summarize_error(test_log)
    if error_summary != "无错误":
        return error_summary

    return summarize_text(test_log, 260)


def get_builtin_security_summary(state):
    if not state or not state.get("code"):
        return "等待安全检查"

    problems = check_code_safety(state.get("code", ""))

    if not problems:
        return "安全检查通过"

    return "发现风险：" + "；".join(problems)


def status_to_chinese(status):
    return STATUS_LABELS.get(status, status)


def run_status_to_chinese(status):
    return RUN_STATUS_LABELS.get(status, status)


def get_current_agent_label(workflow_status):
    for status in ("Repairing", "Running"):
        for step in WORKFLOW_STEPS:
            if workflow_status.get(step) == status:
                return f"{step} · {status_to_chinese(status)}"

    if workflow_status.get("Report") == "Done":
        return "流程已完成"

    if workflow_status.get("Report") == "Failed":
        return "流程失败"

    return "暂无运行中的 Agent"


def summarize_code_fix(code):
    if not code:
        return "等待 Coder Agent 生成修复代码"

    if "EOFError" in code:
        return "Coder Agent 已加入 EOFError 兜底，保证无人输入时也能运行结束。"

    if "try" in code and "except" in code:
        return "Coder Agent 已加入异常处理逻辑，让代码在自动运行环境中更稳。"

    return "Coder Agent 已根据 Sentry 建议重新生成完整代码。"


def safe_int(value, default=0):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def parse_percent(value):
    text = str(value or "").replace("%", "").strip()
    return safe_int(text)


def get_card_class(label, value):
    text = str(value)

    if label in ["最终状态", "pytest 测试"] and any(word in text for word in ["成功", "通过"]):
        return "result-card success-card"

    if label in ["最终状态", "pytest 测试", "人工审批"] and any(
        word in text for word in ["失败", "未通过", "拒绝"]
    ):
        return "result-card fail-card"

    if label in ["安全检查结果", "安全状态", "安全检查"]:
        if any(word in text for word in ["通过", "未发现"]):
            return "result-card success-card"
        if any(word in text for word in ["风险", "危险", "失败", "错误"]):
            return "result-card fail-card"

    if label == "质量评分":
        score = safe_int(text.split("/")[0])
        if score >= 80:
            return "result-card success-card"
        if score and score < 60:
            return "result-card fail-card"

    if label == "覆盖率":
        coverage = parse_percent(text)
        if coverage >= 70:
            return "result-card success-card"
        if coverage and coverage < 50:
            return "result-card fail-card"

    if label == "文档生成状态" and "已生成" in text:
        return "result-card success-card"

    return "result-card"


def get_plugin_visual_status(content, enabled):
    if not enabled:
        return "未启用", "plugin-disabled"

    text = content or ""
    if not text.strip():
        return "等待输出", "plugin-warn"

    fail_words = ["失败", "错误", "危险", "禁止", "高风险", "Exception", "Error"]
    warn_words = ["警告", "风险", "建议", "需要", "注意", "可优化", "重复"]

    if any(word in text for word in fail_words):
        return "风险", "plugin-fail"

    if any(word in text for word in warn_words):
        return "建议", "plugin-warn"

    return "通过", "plugin-ok"


def render_compare_table(rows):
    if not rows:
        st.info("暂无模型对比数据。")
        return

    successful_rows = [row for row in rows if row.get("成功状态") == "成功"]
    min_retry = min(safe_int(row.get("修复次数")) for row in rows)
    max_coverage = max(parse_percent(row.get("覆盖率")) for row in rows)
    max_quality = max(safe_int(row.get("质量评分")) for row in rows)

    headers = ["模型", "成功状态", "失败次数", "修复次数", "pytest", "覆盖率", "质量评分", "插件摘要"]
    html = '<table class="compare-table"><thead><tr>'
    for header in headers:
        html += f"<th>{escape(header)}</th>"
    html += "</tr></thead><tbody>"

    for row in rows:
        row_classes = []
        if row in successful_rows:
            row_classes.append("compare-success-best")
        if safe_int(row.get("修复次数")) == min_retry:
            row_classes.append("compare-repair-best")

        row_class = " ".join(row_classes)
        html += f'<tr class="{row_class}">'

        for header in headers:
            cell_classes = []
            if header == "覆盖率" and parse_percent(row.get(header)) == max_coverage:
                cell_classes.append("compare-coverage-best")
            if header == "质量评分" and safe_int(row.get(header)) == max_quality:
                cell_classes.append("compare-quality-best")

            cell_class = " ".join(cell_classes)
            html += f'<td class="{cell_class}">{escape(str(row.get(header, "")))}</td>'

        html += "</tr>"

    html += "</tbody></table>"
    st.markdown(html, unsafe_allow_html=True)


def render_markdown_with_code_blocks(markdown_text):
    parts = (markdown_text or "").split("```")

    for index, part in enumerate(parts):
        if index % 2 == 0:
            if part.strip():
                st.markdown(part)
            continue

        lines = part.splitlines()
        language = "text"
        code = part

        if lines:
            first_line = lines[0].strip()
            if first_line and " " not in first_line and len(first_line) <= 30:
                language = first_line
                code = "\n".join(lines[1:])

        st.code(code.strip() or " ", language=language)


def get_report_success_status(report_content):
    success_markers = ["✅", "是否成功：成功", "success: True", "success：True", "运行成功"]
    fail_markers = ["❌", "是否成功：失败", "success: False", "success：False", "运行失败"]

    if any(marker in report_content for marker in success_markers):
        return True

    if any(marker in report_content for marker in fail_markers):
        return False

    return None


def load_plugin_enabled_map():
    """Read config/agents.yaml and return plugin enabled states."""
    enabled_map = {plugin_name: True for plugin_name in PLUGIN_ORDER}

    if not CONFIG_FILE.exists():
        return enabled_map

    config = yaml.safe_load(CONFIG_FILE.read_text(encoding="utf-8")) or {}

    for item in config.get("plugins", []):
        plugin_name = item.get("name")
        if plugin_name in enabled_map:
            enabled_map[plugin_name] = bool(item.get("enabled", False))

    return enabled_map


def save_plugin_enabled_map(enabled_map):
    """Write plugin enabled states back to config/agents.yaml."""
    CONFIG_FILE.parent.mkdir(exist_ok=True)

    lines = ["plugins:"]
    for plugin_name in PLUGIN_ORDER:
        enabled_text = "true" if enabled_map.get(plugin_name, False) else "false"
        lines.append(f"  - name: {plugin_name}")
        lines.append(f"    enabled: {enabled_text}")

    CONFIG_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")


def get_plugin_display_info(plugin_name):
    plugin_class = PLUGIN_CLASSES[plugin_name]
    plugin = plugin_class()
    return plugin.name, plugin.description


def get_enabled_plugin_names(enabled_map):
    names = []

    for plugin_name in PLUGIN_ORDER:
        if enabled_map.get(plugin_name, False):
            display_name, _ = get_plugin_display_info(plugin_name)
            names.append(display_name)

    return names


def make_initial_workflow_status():
    return build_workflow_status(None)


def initialize_session_state():
    demo_options = get_demo_options()
    default_case = list(demo_options.keys())[0]

    if "selected_case" not in st.session_state:
        st.session_state["selected_case"] = default_case

    if "requirement" not in st.session_state:
        st.session_state["requirement"] = demo_options[default_case]

    if "result_state" not in st.session_state:
        st.session_state["result_state"] = None

    if "run_id" not in st.session_state:
        st.session_state["run_id"] = None

    if "run_status" not in st.session_state:
        st.session_state["run_status"] = "Waiting"

    if "workflow_status" not in st.session_state:
        st.session_state["workflow_status"] = make_initial_workflow_status()

    if "progress_log" not in st.session_state:
        st.session_state["progress_log"] = []

    if "latest_report" not in st.session_state:
        st.session_state["latest_report"] = None

    if "stdout" not in st.session_state:
        st.session_state["stdout"] = ""

    if "stderr" not in st.session_state:
        st.session_state["stderr"] = ""

    if "repair_events" not in st.session_state:
        st.session_state["repair_events"] = []

    if "test_stdout" not in st.session_state:
        st.session_state["test_stdout"] = ""

    if "test_stderr" not in st.session_state:
        st.session_state["test_stderr"] = ""

    if "coverage_stdout" not in st.session_state:
        st.session_state["coverage_stdout"] = ""

    if "model_provider" not in st.session_state:
        st.session_state["model_provider"] = get_setting(
            "default_model_provider",
            get_default_model().get("provider", "deepseek"),
        )

    if "compare_states" not in st.session_state:
        st.session_state["compare_states"] = []

    if "compare_report_path" not in st.session_state:
        st.session_state["compare_report_path"] = None


def reset_run_state():
    for key in RUN_STATE_KEYS:
        st.session_state.pop(key, None)

    st.session_state["result_state"] = None
    st.session_state["run_id"] = None
    st.session_state["run_status"] = "Waiting"
    st.session_state["workflow_status"] = make_initial_workflow_status()
    st.session_state["progress_log"] = []
    st.session_state["latest_report"] = None
    st.session_state["stdout"] = ""
    st.session_state["stderr"] = ""
    st.session_state["test_stdout"] = ""
    st.session_state["test_stderr"] = ""
    st.session_state["coverage_stdout"] = ""
    st.session_state["compare_states"] = []
    st.session_state["compare_report_path"] = None
    st.session_state["repair_events"] = []


def get_current_model_label(provider=None):
    model_info = get_current_model_info(provider or st.session_state.get("model_provider"))
    model_text = f"{model_info.get('name')} / {model_info.get('model')}"
    env_key = model_info.get("env_key", "")

    if is_offline_mode() or not get_config(env_key):
        return f"{model_text} / Offline"

    return model_text


def get_mode_label(provider=None):
    model_info = get_current_model_info(provider or st.session_state.get("model_provider"))
    env_key = model_info.get("env_key", "")

    if is_offline_mode():
        return "离线演示模式"

    if not get_config(env_key):
        return f"未配置 {env_key}，自动离线兜底"

    return "在线 API 模式"


def render_model_selector_sidebar():
    st.sidebar.markdown("### 模型选择")
    models = get_available_models()

    if not models:
        st.sidebar.warning("没有找到模型配置，已使用 DeepSeek 默认配置。")
        return "deepseek", get_current_model_info("deepseek")

    provider_options = [model_info.get("provider", "") for model_info in models]
    label_map = {
        model_info.get("provider", ""): f"{model_info.get('name')} / {model_info.get('model')}"
        for model_info in models
    }
    default_provider = st.session_state.get("model_provider") or get_default_model().get("provider", "deepseek")

    if default_provider not in provider_options:
        default_provider = provider_options[0]

    selected_provider = st.sidebar.selectbox(
        "当前使用模型",
        provider_options,
        index=provider_options.index(default_provider),
        format_func=lambda provider: label_map.get(provider, provider),
    )

    st.session_state["model_provider"] = selected_provider
    model_info = get_current_model_info(selected_provider)
    env_key = model_info.get("env_key", "")

    st.sidebar.caption(f"模型名称：{model_info.get('model')}")
    st.sidebar.caption(f"base_url：{model_info.get('base_url')}")

    if not get_config(env_key) and not is_offline_mode():
        st.sidebar.warning(f"未配置 {env_key}，运行时会自动使用离线演示响应。")

    return selected_provider, model_info


def render_model_compare_sidebar():
    st.sidebar.markdown("### 模型对比")
    compare_mode = st.sidebar.checkbox("启用模型对比模式")
    models = get_available_models()
    provider_options = [model_info.get("provider", "") for model_info in models]
    label_map = {
        model_info.get("provider", ""): f"{model_info.get('name')} / {model_info.get('model')}"
        for model_info in models
    }

    default_selection = provider_options[:2]
    selected_providers = st.sidebar.multiselect(
        "选择 2-3 个模型",
        provider_options,
        default=default_selection,
        format_func=lambda provider: label_map.get(provider, provider),
        disabled=not compare_mode,
    )

    if compare_mode:
        if len(selected_providers) < 2:
            st.sidebar.warning("模型对比至少需要选择 2 个模型。")
        if len(selected_providers) > 3:
            st.sidebar.warning("最多对比 3 个模型，运行时会使用前 3 个。")
            selected_providers = selected_providers[:3]

    return compare_mode, selected_providers


def render_summary_cards(model_label, run_status, state, enabled_plugins):
    run_summary = build_run_summary(state)
    success_value = "等待中"
    retry_count = "0"

    if state:
        success_value = "✅ 成功" if run_summary["success"] else "❌ 失败"
        retry_count = str(run_summary["retry_count"])

    summary_plugins = run_summary["enabled_plugins"] or enabled_plugins
    plugin_text = f"{len(summary_plugins)} 个启用"
    if summary_plugins:
        plugin_text += "：" + "、".join(summary_plugins)

    cards = [
        ("当前模型", model_label),
        ("当前运行状态", run_status_to_chinese(run_status)),
        ("success", success_value),
        ("retry_count", retry_count),
        ("enabled_plugins", plugin_text),
    ]

    html = '<div class="summary-grid">'
    for label, value in cards:
        html += (
            '<div class="summary-card">'
            f'<div class="summary-label">{escape(label)}</div>'
            f'<div class="summary-value">{escape(str(value))}</div>'
            "</div>"
        )
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)


def render_workflow_progress(workflow_status, state=None):
    retry_count = safe_int((state or {}).get("retry_count", 0))
    final_success = bool((state or {}).get("success"))
    repair_related_steps = {"Coder Agent", "Tester Agent", "Runner", "Sentry Agent"}
    html = '<div class="workflow-grid">'

    for step in WORKFLOW_STEPS:
        status = workflow_status.get(step, "Waiting")
        status_class = f"status-{status.lower()}"
        node_classes = ["workflow-node", status_class]
        meta_classes = ["workflow-meta"]

        if retry_count > 0 and step in repair_related_steps:
            node_classes.append("status-retry")
            meta_classes.append("retry-active")

        if final_success and step == "Report" and status == "Done":
            node_classes.append("status-final-success")

        html += (
            f'<div class="{" ".join(node_classes)}">'
            f'<div class="workflow-title">{escape(step)}</div>'
            f'<div class="workflow-status">{escape(status_to_chinese(status))}</div>'
            f'<div class="{" ".join(meta_classes)}">修复次数：{escape(str(retry_count))}</div>'
            "</div>"
        )

    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)


def render_plugin_config_sidebar():
    st.sidebar.markdown("### 自定义 AI 插件开关")

    enabled_map = load_plugin_enabled_map()
    updated_map = {}

    for plugin_name in PLUGIN_ORDER:
        display_name, description = get_plugin_display_info(plugin_name)
        checkbox_key = f"plugin_enabled_{plugin_name}"

        if checkbox_key not in st.session_state:
            st.session_state[checkbox_key] = enabled_map[plugin_name]

        st.sidebar.markdown(f"**{display_name}**")
        st.sidebar.caption(description)
        updated_map[plugin_name] = st.sidebar.checkbox(
            "启用",
            key=checkbox_key,
        )

    if updated_map != enabled_map:
        save_plugin_enabled_map(updated_map)
        st.sidebar.success("插件配置已保存")

    return updated_map


def render_sidebar():
    st.sidebar.title("AI Pipeline")
    st.sidebar.caption("比赛演示控制台")

    demo_options = get_demo_options()
    case_names = list(demo_options.keys())
    current_case = st.session_state.get("selected_case", case_names[0])
    current_index = case_names.index(current_case) if current_case in case_names else 0

    selected_case = st.sidebar.selectbox(
        "演示案例选择",
        case_names,
        index=current_index,
        key="selected_case",
    )

    previous_case = st.session_state.get("_previous_selected_case")
    if previous_case != selected_case:
        if selected_case != "自定义输入":
            st.session_state["requirement"] = demo_options[selected_case]
        st.session_state["_previous_selected_case"] = selected_case

    requirement = st.sidebar.text_area(
        "自定义需求输入",
        height=160,
        placeholder="请输入你想让 AI 开发的 Python 程序需求",
        key="requirement",
    )

    default_max_retry_count = int(get_setting("max_retry_count"))
    require_human_approval = bool(get_setting("require_human_approval", True))
    default_demo_mode = bool(get_setting("demo_mode", True))

    max_retry_count = st.sidebar.number_input(
        "最大修复次数设置",
        min_value=0,
        max_value=10,
        value=default_max_retry_count,
        step=1,
    )

    st.sidebar.divider()
    model_provider, model_info = render_model_selector_sidebar()
    compare_mode, compare_providers = render_model_compare_sidebar()

    st.sidebar.markdown("### 在线 / 离线模式")
    st.sidebar.info(get_mode_label(model_provider))

    display_mode = st.sidebar.radio(
        "显示模式",
        ["演示模式", "开发模式"],
        index=0 if default_demo_mode else 1,
        horizontal=True,
    )

    st.sidebar.divider()
    enabled_map = render_plugin_config_sidebar()

    st.sidebar.divider()
    if require_human_approval:
        allow_run = st.sidebar.checkbox("我确认允许运行 AI 生成的代码")
    else:
        allow_run = True
        st.sidebar.success("当前配置未启用人工审批，Runner 将自动通过。")

    start_button = st.sidebar.button(
        "开始运行",
        type="primary",
        use_container_width=True,
    )
    clear_button = st.sidebar.button("清空结果", use_container_width=True)

    if clear_button:
        reset_run_state()
        st.sidebar.success("运行结果已清空")
        st.rerun()

    if require_human_approval and not allow_run:
        st.sidebar.warning("请先确认允许运行 AI 生成的代码。")

    return {
        "requirement": requirement,
        "max_retry_count": int(max_retry_count),
        "display_mode": display_mode,
        "enabled_map": enabled_map,
        "enabled_plugins": get_enabled_plugin_names(enabled_map),
        "allow_run": allow_run,
        "require_human_approval": require_human_approval,
        "start_button": start_button,
        "model_provider": model_provider,
        "model_info": model_info,
        "compare_mode": compare_mode,
        "compare_providers": compare_providers,
    }


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

## error_log

```text
{state.get("error_log", "")}
```
"""


def save_report(report, report_file=None):
    REPORT_DIR.mkdir(exist_ok=True)
    LEGACY_REPORT_FILE.parent.mkdir(exist_ok=True)

    if report_file is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = REPORT_DIR / f"report_{timestamp}.md"
    else:
        report_file = Path(report_file)

    report_file.write_text(report, encoding="utf-8")
    LATEST_REPORT_FILE.write_text(report, encoding="utf-8")
    LEGACY_REPORT_FILE.write_text(report, encoding="utf-8")

    return report_file


def persist_compare_states(compare_run_id, states, enabled_plugins):
    saved_states = []

    for index, state in enumerate(states, start=1):
        state_run_id = f"{compare_run_id}_model{index}"
        state_path = Path("runs") / f"{state_run_id}.json"
        report_file = Path("reports") / f"{state_run_id}.md"

        state["run_id"] = state_run_id
        state["compare_run_id"] = compare_run_id
        state["run_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        state["enabled_plugins"] = enabled_plugins
        state["state_path"] = str(state_path)
        state["report_path"] = str(report_file)

        report = build_markdown_report(state)
        save_report(report, report_file)
        save_run_state(state_run_id, state)
        saved_states.append(state)

    compare_report_path = save_compare_report(compare_run_id, saved_states)
    return saved_states, compare_report_path


def get_latest_report_file():
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


def render_stdout_stderr(state, display_mode):
    stdout = state.get("stdout", "") if state else ""
    error_log = state.get("error_log", "") if state else ""

    with st.expander("stdout", expanded=False):
        st.code(stdout or "无 stdout", language="text")

    with st.expander("stderr / error_log", expanded=bool(error_log)):
        demo_mode = display_mode == "演示模式"
        if not demo_mode and error_log:
            st.error("检测到 stderr / error_log，下面显示完整日志。")
        st.code(format_error_for_display(error_log, demo_mode=demo_mode), language="text")


def render_test_result_area(state, display_mode):
    st.markdown('<div class="section-title">pytest 自动测试结果</div>', unsafe_allow_html=True)

    if not state:
        st.info("运行后这里会展示 Tester Agent 自动生成的 pytest 测试和执行结果。")
        return

    col1, col2 = st.columns(2)
    col1.metric("test_success", "通过" if state.get("test_success") else "未通过")
    col2.metric("coverage_percent", f"{state.get('coverage_percent', 0)}%")
    st.caption("测试摘要：" + summarize_test_result(state))

    test_code = state.get("test_code", "")
    test_stdout = state.get("test_stdout", "")
    test_stderr = state.get("test_stderr", "")

    if display_mode == "开发模式":
        st.markdown("**自动生成的 pytest 测试代码**")
        st.code(test_code or "# 暂无测试代码", language="python")

    with st.expander("pytest stdout", expanded=False):
        if display_mode == "演示模式":
            st.code(summarize_text(test_stdout, 500), language="text")
        else:
            st.code(test_stdout or "无 pytest stdout", language="text")

    with st.expander("pytest stderr", expanded=bool(test_stderr)):
        st.code(
            format_error_for_display(test_stderr, demo_mode=display_mode == "演示模式"),
            language="text",
        )

    if display_mode == "开发模式":
        with st.expander("coverage report", expanded=False):
            st.code(state.get("coverage_stdout", "") or "无 coverage 输出", language="text")


def render_quality_area(state, display_mode):
    st.markdown('<div class="section-title">质量评分</div>', unsafe_allow_html=True)

    if not state:
        st.info("运行后这里会展示最终代码质量评分。")
        return

    run_summary = build_run_summary(state)
    quality_score = run_summary["quality_score"]
    coverage_percent = run_summary["coverage_percent"]
    test_status = "通过" if run_summary["test_success"] else "未通过"
    safety_status = run_summary["security_status"]

    if display_mode == "演示模式":
        score_class = get_card_class("质量评分", f"{quality_score}/100")
        coverage_class = get_card_class("覆盖率", f"{coverage_percent}%")
        test_class = get_card_class("pytest 测试", test_status)
        safety_class = get_card_class("安全状态", safety_status)
        html = f"""
        <div class="result-grid">
            <div class="{score_class}">
                <div class="demo-label">质量总分</div>
                <div class="demo-value" style="font-size:32px;">{escape(str(quality_score))}/100</div>
            </div>
            <div class="{coverage_class}">
                <div class="demo-label">覆盖率</div>
                <div class="demo-value">{escape(str(coverage_percent))}%</div>
            </div>
            <div class="{test_class}">
                <div class="demo-label">测试状态</div>
                <div class="demo-value">{escape(test_status)}</div>
            </div>
            <div class="{safety_class}">
                <div class="demo-label">安全状态</div>
                <div class="demo-value">{escape(safety_status)}</div>
            </div>
        </div>
        """
        st.markdown(html, unsafe_allow_html=True)
        st.caption(summarize_text(state.get("quality_summary", ""), 260))
        return

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("quality_score", f"{quality_score}/100")
    col2.metric("coverage_percent", f"{coverage_percent}%")
    col3.metric("test_success", test_status)
    col4.metric("retry_count", state.get("retry_count", 0))

    st.markdown("**安全检查结果**")
    st.write(safety_status)

    st.markdown("**完整评分依据**")
    st.code(state.get("quality_summary", "") or "暂无评分依据", language="text")

    with st.expander("coverage_stdout", expanded=False):
        st.code(state.get("coverage_stdout", "") or "无 coverage 输出", language="text")


def render_plugin_result_panel(state, enabled_map, display_mode="开发模式"):
    st.markdown('<div class="section-title">插件执行结果</div>', unsafe_allow_html=True)
    status_labels = {
        "success": "通过",
        "warning": "警告",
        "failed": "失败",
        "disabled": "未启用",
    }
    status_classes = {
        "success": "plugin-ok",
        "warning": "plugin-warn",
        "failed": "plugin-fail",
        "disabled": "plugin-disabled",
    }

    for item in build_plugin_display_data(state):
        status = item.get("status", "warning")
        status_text = status_labels.get(status, status)
        status_class = status_classes.get(status, "plugin-warn")
        display_name = item.get("display_name", "Plugin")
        field_name = item.get("field_name", "")
        summary = item.get("summary", "无摘要")
        content = item.get("detail", "")

        st.markdown(
            f"""
            <div class="plugin-card {status_class}">
                <div class="plugin-title">{escape(display_name)} / {escape(field_name)}</div>
                <div class="plugin-status">{escape(status_text)}</div>
                <div>{escape(summary)}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if status == "disabled":
            st.info(content or "该插件未启用")
            continue

        if display_mode == "演示模式":
            st.markdown(summarize_text(content, 260) or "等待插件执行")
        else:
            st.markdown(content or "等待插件执行")


def render_model_compare_tab(compare_states, compare_report_path, display_mode):
    if not compare_states:
        st.info("启用模型对比模式并运行后，这里会展示多模型效果对比。")
        return

    rows = create_compare_rows(compare_states)
    render_compare_table(rows)

    if compare_report_path and Path(compare_report_path).exists():
        report_content = Path(compare_report_path).read_text(encoding="utf-8")
        st.write(f"对比报告：`{Path(compare_report_path).name}`")
        st.download_button(
            "下载模型对比报告",
            data=report_content,
            file_name=Path(compare_report_path).name,
            mime="text/markdown",
        )

    for state in compare_states:
        title = f"{state.get('model_provider', 'model')} / {state.get('model_name', '')}"
        with st.expander(title, expanded=False):
            col1, col2, col3, col4, col5 = st.columns(5)
            col1.metric("success", "成功" if state.get("success") else "失败")
            col2.metric("retry_count", state.get("retry_count", 0))
            col3.metric("test_success", "通过" if state.get("test_success") else "未通过")
            col4.metric("coverage", f"{state.get('coverage_percent', 0)}%")
            col5.metric("quality", f"{state.get('quality_score', 0)}/100")

            with st.expander("stdout", expanded=False):
                st.code(state.get("stdout", "") or "无 stdout", language="text")

            with st.expander("stderr / error_log", expanded=False):
                st.code(
                    format_error_for_display(
                        state.get("error_log", ""),
                        demo_mode=display_mode == "演示模式",
                    ),
                    language="text",
                )

            st.markdown("**插件详细输出**")
            for item in build_plugin_display_data(state):
                st.markdown(f"**{item.get('display_name')} / {item.get('status')}**")
                content = item.get("detail", "") or item.get("summary", "") or "无"
                if display_mode == "演示模式":
                    st.write(summarize_text(content, 220))
                else:
                    st.write(content)


def get_security_summary(state, enabled_map):
    if not enabled_map.get("security_agent", False):
        return "该插件未启用"

    for item in build_plugin_display_data(state):
        if item.get("field_name") != "security_result":
            continue

        if item.get("status") == "disabled":
            return "该插件未启用"

        summary = item.get("summary", "")
        detail = item.get("detail", "")
        if item.get("status") == "success":
            return "安全检查通过"
        if summary and summary != "等待输出":
            return summarize_text(summary, 120)
        if detail:
            return summarize_text(detail, 120)

    return "等待安全检查"


def get_doc_summary(state, enabled_map):
    if not enabled_map.get("doc_agent", False):
        return "该插件未启用"

    for item in build_plugin_display_data(state):
        if item.get("field_name") != "doc_result":
            continue

        if item.get("status") == "disabled":
            return "该插件未启用"

        if item.get("detail"):
            return "文档说明已生成"

    return "等待文档生成"


def get_report_name(report_path):
    return build_report_display_data({"report_path": report_path}).get("name", "暂无报告")


def render_demo_cards(cards):
    html = '<div class="demo-grid">'

    for label, value in cards:
        card_class = "demo-card"
        result_class = get_card_class(label, value)
        if result_class != "result-card":
            card_class = f"demo-card {result_class.replace('result-card', '').strip()}"
        html += (
            f'<div class="{card_class}">'
            f'<div class="demo-label">{escape(label)}</div>'
            f'<div class="demo-value">{escape(str(value))}</div>'
            "</div>"
        )

    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)


def render_demo_overview(state, workflow_status, report_path, enabled_map):
    st.markdown('<div class="section-title">演示模式总览</div>', unsafe_allow_html=True)

    run_summary = build_run_summary(state)
    requirement = (state or {}).get("requirement") or st.session_state.get("requirement", "")
    repair_events = st.session_state.get("repair_events", [])
    has_error = bool(repair_events or (state or {}).get("error_log"))
    has_repair = bool(repair_events or run_summary["retry_count"] > 0)
    if (state or {}).get("approved") is False:
        error_status = "未通过审批，Runner 未执行"
    elif has_error:
        error_status = "是，已进入自动修复"
    else:
        error_status = "否，流程正常"
    sentry_summary = summarize_text((state or {}).get("sentry_result"), 120)
    final_success = "等待运行" if not state else ("成功" if run_summary["success"] else "失败")
    report_data = build_report_display_data({"report_path": report_path})
    report_status = "已生成" if report_data["exists"] else "暂无报告"

    cards = [
        ("用户输入需求", summarize_text(requirement, 110)),
        ("当前执行 Agent", get_current_agent_label(workflow_status)),
        ("人工审批", (state or {}).get("approval_message", "等待人工确认")),
        ("是否发生错误", error_status),
        ("Sentry 分析", sentry_summary if has_repair else "未触发 Sentry Agent"),
        ("pytest 测试", summarize_test_result(state)),
        ("最终结果", final_success),
        ("修复次数", run_summary["retry_count"]),
        ("质量评分", run_summary["quality_score"] if state else "等待评分"),
        ("覆盖率", f"{run_summary['coverage_percent']}%"),
        ("安全检查", run_summary["security_status"]),
        ("报告生成", report_status),
    ]

    render_demo_cards(cards)


def render_highlight_moment(state):
    st.markdown('<div class="section-title">自动修复高光时刻</div>', unsafe_allow_html=True)

    if not state:
        st.info("运行任务后，这里会展示自动修复是否触发。")
        return

    repair_events = st.session_state.get("repair_events", [])
    has_repair = bool(repair_events or (state or {}).get("retry_count", 0) > 0)

    if not has_repair:
        if state.get("approved") is False:
            st.info("本次任务等待人工确认，未执行 Runner，也未触发自动修复。")
            return

        st.info("本次任务一次运行成功，未触发自动修复。")
        return

    first_event = repair_events[0] if repair_events else {}
    error_summary = first_event.get("error_summary") or summarize_error((state or {}).get("error_log"))
    failure_type = first_event.get("failure_type", "Runner 运行")
    sentry_result = first_event.get("sentry_result") or summarize_text((state or {}).get("sentry_result"), 180)
    coder_fix = first_event.get("coder_fix") or summarize_code_fix((state or {}).get("code", ""))
    rerun_result = "再次运行成功" if (state or {}).get("success") else "再次运行仍失败"

    html = f"""
    <div class="highlight-box">
        <h3>自动修复高光时刻</h3>
        <ul>
            <li><strong>第一次校验失败：</strong>{escape(failure_type)} 未通过，流程自动进入 Sentry Agent。</li>
            <li><strong>错误摘要：</strong>{escape(error_summary)}</li>
            <li><strong>Sentry Agent 分析结果：</strong>{escape(sentry_result)}</li>
            <li><strong>Coder Agent 修复结果：</strong>{escape(coder_fix)}</li>
            <li><strong>最终结果：</strong>{escape(rerun_result)}</li>
        </ul>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def render_result_summary_cards(state, enabled_map, report_path):
    if not state:
        return

    run_summary = build_run_summary(state)
    report_name = get_report_name(report_path)
    code_file = str(GENERATED_CODE_FILE)
    if state.get("approved") is False:
        code_file = "未执行 Runner，未保存新代码文件"

    cards = [
        ("最终状态", "✅ 成功" if run_summary["success"] else "❌ 失败"),
        ("人工审批", "已通过" if state.get("approved") else "未通过"),
        ("修复次数", run_summary["retry_count"]),
        ("pytest 测试", "通过" if run_summary["test_success"] else "未通过"),
        ("覆盖率", f"{run_summary['coverage_percent']}%"),
        ("质量评分", f"{run_summary['quality_score']}/100"),
        ("生成代码文件", code_file),
        ("安全检查结果", run_summary["security_status"]),
        ("文档生成状态", get_doc_summary(state, enabled_map)),
        ("报告文件名", report_name),
    ]

    html = '<div class="result-grid">'
    for label, value in cards:
        card_class = get_card_class(label, value)
        html += (
            f'<div class="{card_class}">'
            f'<div class="demo-label">{escape(label)}</div>'
            f'<div class="demo-value">{escape(str(value))}</div>'
            "</div>"
        )
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)


def render_speaker_notes(state, enabled_plugins):
    with st.expander("讲解提示", expanded=False):
        if not state:
            st.markdown(
                """
                - 本项目解决的是从需求到代码、测试、修复和报告的自动化问题。
                - 运行后可以重点讲 Product、Coder、Tester、Runner、Sentry 和插件模块如何协作。
                - 建议先跑简单案例，再跑翻车修复案例突出自动修复能力。
                """
            )
            return

        has_repair = state.get("retry_count", 0) > 0
        final_result = "运行成功" if state.get("success") else "运行失败"
        repair_text = (
            f"本次触发自动修复，共修复 {state.get('retry_count', 0)} 次。"
            if has_repair
            else "本次一次运行成功，没有触发自动修复。"
        )
        plugin_text = "、".join(enabled_plugins) if enabled_plugins else "未启用插件"

        st.markdown(
            f"""
            - 项目解决了自然语言需求到可运行代码的自动化交付问题。
            - Product Agent 负责拆解需求，Coder Agent 负责生成和修复代码，Tester Agent 负责生成 pytest 并自动测试，Runner 负责真实运行。
            - {repair_text}
            - 插件模块本次启用：{plugin_text}。
            - 最终结果：{final_result}，报告已自动生成用于复盘和展示。
            """
        )


def render_agent_tabs(state, enabled_map, display_mode):
    tab_product, tab_coder, tab_tester, tab_sentry, tab_plugins, tab_compare, tab_final = st.tabs(
        ["Product Agent", "Coder Agent", "Tester Agent", "Sentry Agent", "Plugins", "模型对比", "Final State"]
    )

    with tab_product:
        product_result = (state or {}).get("product_result") or "等待 Product Agent 输出"
        if display_mode == "演示模式":
            st.markdown(summarize_text(product_result, 320))
        else:
            st.markdown(product_result)

    with tab_coder:
        code = (state or {}).get("code") or ""
        if display_mode == "演示模式" and code:
            code_lines = code.splitlines()
            preview_code = "\n".join(code_lines[:80])
            if len(code_lines) > 80:
                preview_code += "\n# ... 演示模式仅展示前 80 行"
            st.code(preview_code, language="python")
        else:
            st.code(code or "# 等待 Coder Agent 生成代码", language="python")

    with tab_tester:
        tester_result = (state or {}).get("tester_result") or "等待 Tester Agent 输出"
        if display_mode == "演示模式":
            st.markdown(summarize_text(tester_result, 260))
            st.info(summarize_test_result(state))
        else:
            st.markdown(tester_result)
            st.metric("test_success", "通过" if (state or {}).get("test_success") else "未通过")
            st.markdown("**pytest 测试代码**")
            st.code((state or {}).get("test_code", "") or "# 等待 Tester Agent 生成测试代码", language="python")
            render_stdout_stderr(
                {
                    "stdout": (state or {}).get("test_stdout", ""),
                    "error_log": (state or {}).get("test_stderr", ""),
                },
                display_mode,
            )
            with st.expander("coverage report", expanded=False):
                st.code((state or {}).get("coverage_stdout", "") or "无 coverage 输出", language="text")

    with tab_sentry:
        sentry_result = (state or {}).get("sentry_result") or ""
        if sentry_result:
            if display_mode == "演示模式":
                st.markdown(summarize_text(sentry_result, 300))
            else:
                st.markdown(sentry_result)
        else:
            st.info("Sentry Agent 尚未触发，或本次运行无需自动修复。")

    with tab_plugins:
        render_plugin_result_panel(state or {}, enabled_map, display_mode)

    with tab_compare:
        render_model_compare_tab(
            st.session_state.get("compare_states", []),
            st.session_state.get("compare_report_path"),
            display_mode,
        )

    with tab_final:
        if not state:
            st.info("暂无运行结果")
        else:
            run_summary = build_run_summary(state)
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("success", "成功" if run_summary["success"] else "失败")
            col2.metric("retry_count", run_summary["retry_count"])
            col3.metric("max_retry_count", state.get("max_retry_count", get_setting("max_retry_count")))
            col4.metric("quality_score", f"{run_summary['quality_score']}/100")

            render_stdout_stderr(state, display_mode)

            if display_mode == "开发模式":
                st.markdown("**完整 state**")
                st.json(json.loads(json.dumps(state, ensure_ascii=False, default=str)))
            else:
                st.markdown("**演示摘要**")
                st.write(
                    {
                        "requirement": summarize_text(state.get("requirement"), 90),
                        "success": run_summary["success"],
                        "retry_count": run_summary["retry_count"],
                        "test_success": run_summary["test_success"],
                        "coverage_percent": run_summary["coverage_percent"],
                        "quality_score": run_summary["quality_score"],
                        "security_status": run_summary["security_status"],
                        "model_provider": run_summary["model_provider"],
                        "report_path": run_summary["report_path"],
                        "test_summary": summarize_test_result(state),
                        "error_summary": summarize_error(state.get("error_log")),
                    }
                )


def render_report_area(report_path=None):
    st.markdown('<div class="section-title">报告区域</div>', unsafe_allow_html=True)
    report_data = build_report_display_data({"report_path": report_path})

    if not report_data["exists"]:
        st.info("暂无报告")
        return

    st.write(f"最新报告文件名：`{report_data['name']}`")
    report_content = report_data["content"]
    report_success = report_data["success"]

    if report_success is True:
        st.markdown(
            '<div class="report-status-success">✅ 报告状态：成功</div>',
            unsafe_allow_html=True,
        )
    elif report_success is False:
        st.markdown(
            '<div class="report-status-fail">❌ 报告状态：失败</div>',
            unsafe_allow_html=True,
        )

    with st.expander("查看报告内容", expanded=False):
        render_markdown_with_code_blocks(report_content)

    with st.expander("错误摘要 / 日志", expanded=False):
        st.code(report_data["error_summary"], language="text")

    st.download_button(
        "下载 Markdown 报告",
        data=report_content,
        file_name=report_data["name"],
        mime="text/markdown",
    )


def render_history_area(display_mode):
    st.markdown('<div class="section-title">历史运行记录</div>', unsafe_allow_html=True)

    run_ids = list_runs()
    latest_run = get_latest_run()

    if not run_ids:
        st.info("暂无历史运行记录。完成一次运行后，会在这里看到 run_id。")
        return

    default_index = run_ids.index(latest_run) if latest_run in run_ids else 0
    selected_run_id = st.selectbox(
        "选择历史 run_id",
        run_ids,
        index=default_index,
        key="history_run_id",
    )
    history_state = load_run_state(selected_run_id)

    if not history_state:
        st.warning("没有找到该 run_id 对应的状态文件。")
        return

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("run_id", history_state.get("run_id", selected_run_id))
    col2.metric("success", "成功" if history_state.get("success") else "失败")
    col3.metric("retry_count", history_state.get("retry_count", 0))
    col4.metric("test_success", "通过" if history_state.get("test_success") else "未通过")
    col5.metric("quality_score", f"{history_state.get('quality_score', 0)}/100")

    st.write(f"需求：{history_state.get('requirement', '无需求')}")
    st.write(
        f"模型：`{history_state.get('model_provider', '未记录')}` / "
        f"`{history_state.get('model_name', '未记录')}`"
    )
    st.write(f"人工审批：`{history_state.get('approval_message', '未记录')}`")
    st.write(f"报告路径：`{history_state.get('report_path', '未生成')}`")
    st.write(f"状态文件：`{history_state.get('state_path', get_run_state_path(selected_run_id))}`")

    if st.button("加载为当前结果", key="load_history_as_current"):
        st.session_state["result_state"] = history_state
        st.session_state["run_state"] = history_state
        st.session_state["run_id"] = history_state.get("run_id", selected_run_id)
        st.session_state["run_status"] = "Completed" if history_state.get("success") else "Failed"
        st.session_state["latest_report"] = history_state.get("report_path")
        st.session_state["stdout"] = history_state.get("stdout", "")
        st.session_state["stderr"] = history_state.get("error_log", "")
        st.session_state["test_stdout"] = history_state.get("test_stdout", "")
        st.session_state["test_stderr"] = history_state.get("test_stderr", "")
        st.session_state["coverage_stdout"] = history_state.get("coverage_stdout", "")
        st.success("已加载该历史记录到当前展示区。")
        st.rerun()

    with st.expander("过程回放", expanded=False):
        st.markdown("**Product Agent**")
        st.markdown(summarize_text(history_state.get("product_result", ""), 360))
        st.markdown("**Coder Agent**")
        st.markdown(summarize_text(history_state.get("code", ""), 360))
        st.markdown("**Tester Agent**")
        st.markdown(summarize_text(history_state.get("tester_result", ""), 360))
        st.markdown("**Sentry Agent**")
        st.markdown(summarize_text(history_state.get("sentry_result", ""), 360))

    with st.expander("查看历史生成代码", expanded=False):
        code = history_state.get("code", "")
        if display_mode == "演示模式" and code:
            st.code("\n".join(code.splitlines()[:80]), language="python")
        else:
            st.code(code or "# 无历史代码", language="python")

    with st.expander("查看历史错误日志", expanded=False):
        error_log = history_state.get("error_log", "")
        st.code(
            format_error_for_display(error_log, demo_mode=display_mode == "演示模式"),
            language="text",
        )

    with st.expander("查看历史 pytest 测试", expanded=False):
        st.markdown("**测试摘要**")
        st.write(summarize_test_result(history_state))
        if display_mode == "开发模式":
            st.markdown("**测试代码**")
            st.code(history_state.get("test_code", "") or "# 无历史测试代码", language="python")
            st.markdown("**pytest stdout**")
            st.code(history_state.get("test_stdout", "") or "无 pytest stdout", language="text")
            st.markdown("**pytest stderr**")
            st.code(history_state.get("test_stderr", "") or "无 pytest stderr", language="text")

    with st.expander("查看历史质量评分", expanded=False):
        st.write(f"覆盖率：{history_state.get('coverage_percent', 0)}%")
        st.write(f"质量评分：{history_state.get('quality_score', 0)}/100")
        st.code(history_state.get("quality_summary", "") or "无质量评分摘要", language="text")
        if display_mode == "开发模式":
            st.markdown("**coverage report**")
            st.code(history_state.get("coverage_stdout", "") or "无 coverage 输出", language="text")


def update_workflow_for_node(node_name, state, workflow_status, max_retry_count):
    display_state = dict(state or {})
    display_state["_current_node"] = node_name
    display_state["_max_retry_count"] = max_retry_count
    workflow_status.clear()
    workflow_status.update(build_workflow_status(display_state))


def render_page_header():
    st.markdown(
        """
        <div class="dashboard-title">
            <h1>AI Multi-Agent Pipeline</h1>
            <p>AI Dashboard · Developer Console · Agent Workflow · Pipeline Dashboard</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def main():
    st.set_page_config(page_title="AI Multi-Agent Pipeline", layout="wide")
    apply_page_style()
    initialize_session_state()

    controls = render_sidebar()
    enabled_map = controls["enabled_map"]
    enabled_plugins = controls["enabled_plugins"]
    st.session_state["enabled_plugins"] = enabled_plugins

    state = st.session_state.get("result_state")
    run_status = st.session_state.get("run_status", "Waiting")
    workflow_status = st.session_state.get("workflow_status", make_initial_workflow_status())

    render_page_header()

    summary_placeholder = st.empty()
    workflow_placeholder = st.empty()
    progress_placeholder = st.empty()

    with summary_placeholder.container():
        render_summary_cards(get_current_model_label(controls["model_provider"]), run_status, state, enabled_plugins)

    st.markdown('<div class="section-title">Agent 工作流进度</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="small-note">Requirement → Product → Coder → Tester → Approval → Runner → Sentry → Plugins → Quality → Report</div>',
        unsafe_allow_html=True,
    )
    with workflow_placeholder.container():
        render_workflow_progress(workflow_status, state)

    if (
        controls["start_button"]
        and controls["require_human_approval"]
        and not controls["allow_run"]
    ):
        st.warning("等待人工确认：本次会生成和检查代码，但不会执行 Runner。")

    if controls["start_button"]:
        requirement = controls["requirement"].strip()

        if not requirement:
            st.error("需求不能为空。")
            return

        max_retry_count = controls["max_retry_count"]
        run_approved = controls["allow_run"] if controls["require_human_approval"] else True
        approval_message = (
            "未启用人工审批，系统自动通过。"
            if not controls["require_human_approval"]
            else (
                "Web UI 人工审批通过，允许运行 AI 生成代码。"
                if run_approved
                else "等待人工确认：用户未勾选运行确认框，已停止执行 Runner。"
            )
        )
        workflow_status = build_workflow_status(
            {"requirement": requirement, "_current_node": "start"}
        )
        progress_log = ["Requirement 已确认"]
        repair_events = []

        st.session_state["run_status"] = "Running"
        st.session_state["workflow_status"] = workflow_status
        st.session_state["progress_log"] = progress_log
        st.session_state["repair_events"] = repair_events

        with summary_placeholder.container():
            render_summary_cards(get_current_model_label(controls["model_provider"]), "Running", None, enabled_plugins)

        with workflow_placeholder.container():
            render_workflow_progress(workflow_status, None)

        if controls["compare_mode"]:
            selected_providers = controls["compare_providers"][:3]

            if len(selected_providers) < 2:
                st.error("模型对比模式至少需要选择 2 个模型。")
                return

            compare_run_id = create_run_id()
            compare_states = []

            try:
                with st.spinner("多模型对比正在运行，每个模型会独立执行完整 Agent 流程..."):
                    for provider in selected_providers:
                        progress_log.append(f"开始运行模型：{provider}")
                        progress_placeholder.markdown("\n".join(f"- {item}" for item in progress_log))
                        model_state = run_graph_demo(
                            requirement,
                            max_retry_count=max_retry_count,
                            require_human_approval=controls["require_human_approval"],
                            approved=run_approved,
                            model_provider=provider,
                            approval_message=approval_message,
                        )
                        compare_states.append(model_state)
                        progress_log.append(f"模型 {provider} 运行完成")

                saved_states, compare_report_path = persist_compare_states(
                    compare_run_id,
                    compare_states,
                    enabled_plugins,
                )
                best_state = max(
                    saved_states,
                    key=lambda item: item.get("quality_score", 0),
                )

                workflow_status = build_workflow_status(
                    {**best_state, "_current_node": "report_node"}
                )

                run_status = "Completed" if all(item.get("success") for item in saved_states) else "Failed"
                st.session_state["run_id"] = compare_run_id
                st.session_state["result_state"] = best_state
                st.session_state["run_state"] = best_state
                st.session_state["run_status"] = run_status
                st.session_state["workflow_status"] = workflow_status
                st.session_state["progress_log"] = progress_log
                st.session_state["latest_report"] = str(compare_report_path)
                st.session_state["report_path"] = str(compare_report_path)
                st.session_state["stdout"] = best_state.get("stdout", "")
                st.session_state["stderr"] = best_state.get("error_log", "")
                st.session_state["test_stdout"] = best_state.get("test_stdout", "")
                st.session_state["test_stderr"] = best_state.get("test_stderr", "")
                st.session_state["coverage_stdout"] = best_state.get("coverage_stdout", "")
                st.session_state["compare_states"] = saved_states
                st.session_state["compare_report_path"] = str(compare_report_path)
                st.session_state["repair_events"] = []
                st.rerun()

            except Exception as error:
                workflow_status = build_workflow_status({"_current_node": "error"})
                st.session_state["run_status"] = "Failed"
                st.session_state["workflow_status"] = workflow_status
                st.session_state["stderr"] = str(error)
                st.error(f"模型对比运行失败：{error}")
                return

        def on_progress(node_name, node_state):
            update_workflow_for_node(node_name, node_state, workflow_status, max_retry_count)
            progress_log.append(f"{node_name} 已执行")

            if node_name == "runner_node" and not (
                node_state.get("success") and node_state.get("test_success")
            ):
                failure_log = "\n".join(
                    text
                    for text in [
                        node_state.get("error_log", ""),
                        node_state.get("test_stderr", ""),
                        node_state.get("test_stdout", ""),
                    ]
                    if text
                )
                repair_events.append(
                    {
                        "round": node_state.get("retry_count", 0) + 1,
                        "error_summary": summarize_error(failure_log),
                        "failure_type": "pytest 自动测试" if not node_state.get("test_success") else "Runner 运行",
                        "rerun_success": False,
                    }
                )

            if node_name == "sentry_node" and repair_events:
                repair_events[-1]["sentry_result"] = summarize_text(
                    node_state.get("sentry_result", ""),
                    220,
                )

            if (
                node_name == "coder_node"
                and node_state.get("retry_count", 0) > 0
                and repair_events
            ):
                repair_events[-1]["coder_fix"] = summarize_code_fix(node_state.get("code", ""))

            if (
                node_name == "runner_node"
                and node_state.get("success")
                and node_state.get("test_success")
                and repair_events
            ):
                repair_events[-1]["rerun_success"] = True

            st.session_state["repair_events"] = repair_events

            with workflow_placeholder.container():
                render_workflow_progress(workflow_status, node_state)

            progress_placeholder.markdown("\n".join(f"- {item}" for item in progress_log))

        try:
            with st.spinner("LangGraph 正在运行，多 Agent 正在协作..."):
                state = run_graph_demo(
                    requirement,
                    progress_callback=on_progress,
                    max_retry_count=max_retry_count,
                    require_human_approval=controls["require_human_approval"],
                    approved=run_approved,
                    model_provider=controls["model_provider"],
                    approval_message=approval_message,
                )

            run_id = create_run_id()
            state_path = Path("runs") / f"{run_id}.json"
            report_file = Path("reports") / f"{run_id}.md"

            state["run_id"] = run_id
            state["run_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            state["enabled_plugins"] = enabled_plugins
            state["state_path"] = str(state_path)
            state["report_path"] = str(report_file)

            report = build_markdown_report(state)
            save_report(report, report_file)
            save_run_state(run_id, state)

            workflow_status = build_workflow_status(
                {**state, "_current_node": "report_node"}
            )
            if state.get("approved") is False:
                run_status = "Waiting Approval"
            else:
                run_status = "Completed" if state.get("success") else "Failed"

            st.session_state["run_id"] = run_id
            st.session_state["result_state"] = state
            st.session_state["run_state"] = state
            st.session_state["run_status"] = run_status
            st.session_state["workflow_status"] = workflow_status
            st.session_state["progress_log"] = progress_log
            st.session_state["latest_report"] = str(report_file)
            st.session_state["report_path"] = str(report_file)
            st.session_state["stdout"] = state.get("stdout", "")
            st.session_state["stderr"] = state.get("error_log", "")
            st.session_state["test_stdout"] = state.get("test_stdout", "")
            st.session_state["test_stderr"] = state.get("test_stderr", "")
            st.session_state["coverage_stdout"] = state.get("coverage_stdout", "")
            st.session_state["repair_events"] = repair_events

        except Exception as error:
            workflow_status = build_workflow_status({"_current_node": "error"})
            run_status = "Failed"
            st.session_state["run_status"] = run_status
            st.session_state["workflow_status"] = workflow_status
            st.session_state["stderr"] = str(error)
            st.error(f"运行失败：{error}")

    state = st.session_state.get("result_state")
    run_status = st.session_state.get("run_status", run_status)
    workflow_status = st.session_state.get("workflow_status", workflow_status)
    report_path = st.session_state.get("latest_report")

    with summary_placeholder.container():
        render_summary_cards(get_current_model_label(controls["model_provider"]), run_status, state, enabled_plugins)

    with workflow_placeholder.container():
        render_workflow_progress(workflow_status, state)

    if st.session_state.get("progress_log"):
        progress_placeholder.markdown(
            "\n".join(f"- {item}" for item in st.session_state["progress_log"])
        )
    else:
        progress_placeholder.info("在左侧选择案例或输入需求，确认运行权限后点击“开始运行”。")

    if controls["display_mode"] == "演示模式":
        render_demo_overview(state, workflow_status, report_path, enabled_map)
        render_highlight_moment(state)
        render_result_summary_cards(state, enabled_map, report_path)

    render_quality_area(state, controls["display_mode"])
    render_test_result_area(state, controls["display_mode"])
    render_speaker_notes(state, enabled_plugins)

    st.markdown('<div class="section-title">Agent 输出</div>', unsafe_allow_html=True)
    render_agent_tabs(state, enabled_map, controls["display_mode"])

    render_report_area(report_path)
    render_history_area(controls["display_mode"])


if __name__ == "__main__":
    main()

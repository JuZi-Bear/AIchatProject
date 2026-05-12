from pathlib import Path

import streamlit as st

from demo_cases import DEMO_CASES
from graph import run_graph_demo


REPORT_FILE = Path("output") / "web_report.md"

AGENT_CONFIG = {
    "Product Agent": {"color": "#3b82f6"},
    "Coder Agent": {"color": "#22c55e"},
    "Tester Agent": {"color": "#eab308"},
    "Sentry Agent": {"color": "#ef4444"},
}

NODE_TO_AGENT = {
    "product_node": "Product Agent",
    "coder_node": "Coder Agent",
    "tester_node": "Tester Agent",
    "sentry_node": "Sentry Agent",
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
            background: #f6f8fb;
            color: #111827;
        }
        .main .block-container {
            padding-top: 2rem;
            max-width: 1320px;
        }
        section[data-testid="stSidebar"] {
            background: #111827;
        }
        section[data-testid="stSidebar"] * {
            color: #f9fafb;
        }
        .hero {
            background: linear-gradient(135deg, #111827 0%, #1f2937 55%, #0f766e 100%);
            border-radius: 10px;
            padding: 28px 32px;
            color: white;
            margin-bottom: 18px;
        }
        .hero h1 {
            font-size: 34px;
            margin: 0 0 8px 0;
            letter-spacing: 0;
        }
        .hero p {
            font-size: 16px;
            margin: 0;
            color: #d1d5db;
        }
        .workflow {
            display: flex;
            align-items: center;
            gap: 8px;
            flex-wrap: wrap;
            margin: 12px 0 20px 0;
        }
        .workflow-step {
            background: white;
            border: 1px solid #dbe3ef;
            border-radius: 8px;
            padding: 8px 12px;
            font-size: 14px;
            font-weight: 650;
            color: #111827;
        }
        .workflow-arrow {
            color: #6b7280;
            font-weight: 700;
        }
        .agent-card {
            background: white;
            border: 1px solid #e5e7eb;
            border-left: 5px solid var(--agent-color);
            border-radius: 8px;
            padding: 14px;
            min-height: 150px;
            box-shadow: 0 8px 22px rgba(15, 23, 42, 0.06);
        }
        .agent-title {
            font-size: 15px;
            font-weight: 800;
            margin-bottom: 8px;
            color: #111827;
        }
        .agent-status {
            display: inline-block;
            padding: 3px 8px;
            border-radius: 999px;
            background: #eef2ff;
            color: #3730a3;
            font-size: 12px;
            font-weight: 700;
            margin-bottom: 10px;
        }
        .agent-summary {
            color: #374151;
            font-size: 13px;
            line-height: 1.45;
            min-height: 42px;
        }
        .agent-done {
            color: #047857;
            font-size: 13px;
            font-weight: 700;
            margin-top: 8px;
        }
        .metric-panel {
            background: white;
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            padding: 16px;
            box-shadow: 0 8px 22px rgba(15, 23, 42, 0.05);
        }
        .section-title {
            font-size: 18px;
            font-weight: 800;
            margin: 10px 0 10px 0;
            color: #111827;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def summarize_text(text, max_length=120):
    clean_text = " ".join((text or "").split())

    if not clean_text:
        return "等待输出"

    if len(clean_text) <= max_length:
        return clean_text

    return clean_text[:max_length] + "..."


def make_initial_agent_status():
    return {
        name: {
            "status": "等待中",
            "summary": "等待输出",
            "done": False,
        }
        for name in AGENT_CONFIG
    }


def render_workflow():
    steps = ["需求", "Product", "Coder", "Tester", "Runner", "Sentry", "Coder"]
    html = '<div class="workflow">'

    for index, step in enumerate(steps):
        html += f'<div class="workflow-step">{step}</div>'
        if index < len(steps) - 1:
            html += '<div class="workflow-arrow">→</div>'

    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)


def render_agent_cards(agent_status):
    columns = st.columns(4)

    for column, agent_name in zip(columns, AGENT_CONFIG):
        info = agent_status[agent_name]
        color = AGENT_CONFIG[agent_name]["color"]
        done_text = "已完成" if info["done"] else "未完成"
        column.markdown(
            f"""
            <div class="agent-card" style="--agent-color:{color}">
                <div class="agent-title">{agent_name}</div>
                <div class="agent-status">{info["status"]}</div>
                <div class="agent-summary">{info["summary"]}</div>
                <div class="agent-done">{done_text}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_sidebar():
    st.sidebar.title("AI Pipeline")
    st.sidebar.caption("比赛演示控制台")

    st.sidebar.markdown("### 项目简介")
    st.sidebar.write("从自然语言需求到代码生成、运行测试、错误分析与自动修复。")

    st.sidebar.markdown("### 技术栈")
    st.sidebar.markdown(
        """
        - Python
        - DeepSeek API
        - LangGraph
        - Streamlit
        - Rich
        """
    )

    st.sidebar.markdown("### 演示案例")
    st.sidebar.write("简单成功案例、翻车修复案例、综合案例。")

    st.sidebar.markdown("### 运行入口")
    return st.sidebar.button("开始运行", type="primary", use_container_width=True)


def build_markdown_report(state):
    success_text = "成功" if state["success"] else "失败"

    return f"""# AI Multi-Agent Pipeline 运行报告

## 用户需求

{state["requirement"]}

## 运行结果

- 是否成功：{success_text}
- 修复次数：{state["retry_count"]}

## Product Agent

{state["product_result"]}

## Coder Agent 生成代码

```python
{state["code"]}
```

## Tester Agent

{state["tester_result"]}

## Sentry Agent

{state["sentry_result"]}

## stdout

```text
{state["stdout"]}
```

## error_log

```text
{state["error_log"]}
```
"""


def save_report(report):
    REPORT_FILE.parent.mkdir(exist_ok=True)
    REPORT_FILE.write_text(report, encoding="utf-8")


def show_result_panel(state):
    success_label = "成功" if state["success"] else "失败"

    col1, col2 = st.columns(2)
    col1.metric("success", success_label)
    col2.metric("retry_count", state["retry_count"])

    st.markdown('<div class="section-title">stdout</div>', unsafe_allow_html=True)
    st.code(state["stdout"] or "无 stdout", language="text")

    st.markdown('<div class="section-title">error_log</div>', unsafe_allow_html=True)
    st.code(state["error_log"] or "无 error_log", language="text")


def render_report(report):
    st.markdown(report)
    st.download_button(
        "下载 Markdown 报告",
        data=report,
        file_name="ai_pipeline_report.md",
        mime="text/markdown",
    )


def main():
    st.set_page_config(page_title="AI Multi-Agent Pipeline", layout="wide")
    apply_page_style()

    sidebar_run = render_sidebar()

    st.markdown(
        """
        <div class="hero">
            <h1>AI Multi-Agent Pipeline</h1>
            <p>AI Dashboard · Developer Console · Agent Workflow</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    demo_options = get_demo_options()
    selected_case = st.selectbox("演示案例选择", list(demo_options.keys()))

    default_requirement = demo_options[selected_case]
    requirement = st.text_area(
        "需求输入",
        value=default_requirement,
        height=120,
        placeholder="请输入你想让 AI 开发的 Python 程序需求",
    )

    main_run = st.button("开始运行", type="primary")
    run_button = sidebar_run or main_run

    st.markdown('<div class="section-title">Agent Workflow</div>', unsafe_allow_html=True)
    render_workflow()

    cards_placeholder = st.empty()
    agent_status = make_initial_agent_status()

    with cards_placeholder.container():
        render_agent_cards(agent_status)

    st.markdown('<div class="section-title">运行日志与结果</div>', unsafe_allow_html=True)
    progress_box = st.empty()
    result_box = st.container(border=True)
    with result_box:
        result_placeholder = st.empty()

    tab_product, tab_coder, tab_tester, tab_sentry, tab_report = st.tabs(
        ["Product Agent", "Coder Agent", "Tester Agent", "Sentry Agent", "Markdown 报告"]
    )

    with tab_product:
        product_placeholder = st.empty()

    with tab_coder:
        code_placeholder = st.empty()

    with tab_tester:
        tester_placeholder = st.empty()

    with tab_sentry:
        sentry_placeholder = st.empty()

    with tab_report:
        report_placeholder = st.empty()

    if not run_button:
        st.info("选择演示案例或输入自定义需求后，点击“开始运行”。")
        return

    if not requirement.strip():
        st.error("需求不能为空。")
        return

    progress_log = []

    def update_agent(agent_name, status, summary, done):
        agent_status[agent_name]["status"] = status
        agent_status[agent_name]["summary"] = summary
        agent_status[agent_name]["done"] = done

        with cards_placeholder.container():
            render_agent_cards(agent_status)

    def on_progress(node_name, state):
        progress_log.append(f"{node_name} 已执行")
        progress_box.markdown("\n".join(f"- {item}" for item in progress_log))

        if node_name == "product_node":
            update_agent("Product Agent", "已完成", summarize_text(state["product_result"]), True)
            product_placeholder.markdown(state["product_result"] or "等待输出")

        if node_name == "coder_node":
            update_agent("Coder Agent", "已完成", summarize_text(state["code"]), True)
            code_placeholder.code(state["code"] or "", language="python")

        if node_name == "tester_node":
            update_agent("Tester Agent", "已完成", summarize_text(state["tester_result"]), True)
            tester_placeholder.markdown(state["tester_result"] or "等待输出")

        if node_name == "sentry_node":
            update_agent("Sentry Agent", "已完成", summarize_text(state["sentry_result"]), True)
            sentry_placeholder.markdown(state["sentry_result"] or "等待输出")

        if node_name == "runner_node":
            with result_placeholder.container():
                show_result_panel(state)

    with st.spinner("LangGraph 正在运行..."):
        state = run_graph_demo(requirement.strip(), progress_callback=on_progress)

    if not state["sentry_result"]:
        update_agent("Sentry Agent", "未触发", "本次运行未进入错误修复流程", False)

    report = build_markdown_report(state)
    save_report(report)

    with result_placeholder.container():
        show_result_panel(state)

    with report_placeholder.container():
        render_report(report)


if __name__ == "__main__":
    main()

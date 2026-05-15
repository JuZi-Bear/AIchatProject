from pathlib import Path


PLUGIN_FIELDS = [
    ("doc_result", "Doc"),
    ("security_result", "Security"),
    ("refactor_result", "Refactor"),
    ("ui_result", "UI"),
]


def summarize_text(text, max_length=80):
    clean_text = " ".join((text or "").split())

    if not clean_text:
        return "无"

    if len(clean_text) <= max_length:
        return clean_text

    return clean_text[:max_length] + "..."


def get_model_label(state):
    provider = state.get("model_provider", "unknown")
    model_name = state.get("model_name", "unknown")
    return f"{provider} / {model_name}"


def summarize_plugins(state):
    summaries = []

    for field_name, label in PLUGIN_FIELDS:
        content = state.get(field_name, "")
        summaries.append(f"{label}: {summarize_text(content, 36)}")

    return "；".join(summaries)


def create_compare_rows(states):
    """Create simple row dicts for CLI or Web UI tables."""
    rows = []

    for state in states:
        rows.append(
            {
                "模型": get_model_label(state),
                "成功状态": "成功" if state.get("success") else "失败",
                "失败次数": 0 if state.get("success") else 1,
                "修复次数": state.get("retry_count", 0),
                "pytest": "通过" if state.get("test_success") else "未通过",
                "覆盖率": f"{state.get('coverage_percent', 0)}%",
                "质量评分": state.get("quality_score", 0),
                "插件摘要": summarize_plugins(state),
            }
        )

    return rows


def build_compare_markdown(states, compare_run_id=""):
    """Build a Markdown comparison report for multiple model states."""
    rows = create_compare_rows(states)
    title = "# 多模型效果对比报告"

    if compare_run_id:
        title += f"\n\n- compare_run_id：{compare_run_id}"

    requirement = states[0].get("requirement", "") if states else ""
    markdown = f"""{title}

## 用户需求

{requirement}

## 对比表格

| 模型 | 成功状态 | 失败次数 | 修复次数 | pytest | 覆盖率 | 质量评分 | 插件摘要 |
| --- | --- | --- | --- | --- | --- | --- | --- |
"""

    for row in rows:
        markdown += (
            f"| {row['模型']} | {row['成功状态']} | {row['失败次数']} | "
            f"{row['修复次数']} | {row['pytest']} | {row['覆盖率']} | "
            f"{row['质量评分']} | {row['插件摘要']} |\n"
        )

    markdown += "\n## 模型详情\n"

    for index, state in enumerate(states, start=1):
        markdown += f"""
### 模型 {index}: {get_model_label(state)}

- success：{state.get("success")}
- retry_count：{state.get("retry_count", 0)}
- test_success：{state.get("test_success")}
- coverage_percent：{state.get("coverage_percent", 0)}%
- quality_score：{state.get("quality_score", 0)}
- state_path：{state.get("state_path", "未保存")}
- report_path：{state.get("report_path", "未生成")}

#### stdout

```text
{state.get("stdout", "")}
```

#### stderr / error_log

```text
{state.get("error_log", "")}
```

#### 插件结果

**doc_result**

{state.get("doc_result", "") or "无"}

**security_result**

{state.get("security_result", "") or "无"}

**refactor_result**

{state.get("refactor_result", "") or "无"}

**ui_result**

{state.get("ui_result", "") or "无"}
"""

    return markdown


def save_compare_report(compare_run_id, states, reports_dir="reports"):
    """Save report_compare_{run_id}.md and return the path."""
    reports_path = Path(reports_dir)
    reports_path.mkdir(exist_ok=True)

    report_path = reports_path / f"report_compare_{compare_run_id}.md"
    report = build_compare_markdown(states, compare_run_id)
    report_path.write_text(report, encoding="utf-8")
    (reports_path / "latest_compare_report.md").write_text(report, encoding="utf-8")

    return report_path

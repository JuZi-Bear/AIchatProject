from datetime import datetime
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule
from rich.syntax import Syntax

from config.config_loader import get_setting
from demo_cases import DEMO_CASES
from graph import run_graph_demo
from model_manager import get_available_models, get_default_model
from plugin_loader import load_enabled_plugins
from report_generator import (
    build_error_summary_section,
    build_plugin_results_section,
    build_run_summary_section,
)
from utils.error_utils import summarize_error
from utils.model_comparator import build_compare_markdown, save_compare_report
from utils.run_store import create_run_id, save_run_state
from utils.summary_builder import build_run_summary


console = Console()
REPORT_DIR = Path("reports")


def clean_input(text):
    return text.lstrip("\ufeff").strip()


def show_text(title, text, style):
    console.print(Panel(str(text), title=title, border_style=style))


def show_code(title, code):
    syntax = Syntax(code or "", "python", theme="monokai", line_numbers=True)
    console.print(Panel(syntax, title=title, border_style="green"))


def choose_requirement():
    menu = "\n".join(
        [
            "1. 简单成功案例",
            "2. 翻车修复案例",
            "3. 综合案例",
            "4. 自定义输入",
        ]
    )
    console.print(Panel(menu, title="LangGraph 演示菜单", border_style="magenta"))

    choice = clean_input(console.input("[bold]请输入选项 1-4：[/bold]"))

    if choice in DEMO_CASES:
        case = DEMO_CASES[choice]
        show_text("已选择案例", case["name"], "magenta")
        show_text("用户输入需求", case["requirement"], "magenta")
        return case["requirement"]

    if choice == "4":
        return clean_input(console.input("[bold]请输入自定义需求：[/bold]"))

    console.print("[bold red]无效选项，请输入 1、2、3 或 4。[/bold red]")
    return None


def choose_human_approval():
    default_value = bool(get_setting("require_human_approval", True))
    default_text = "是" if default_value else "否"
    answer = clean_input(
        console.input(f"[bold]是否启用人工审批？y/n，直接回车使用默认({default_text})：[/bold]")
    ).lower()

    if not answer:
        return default_value

    return answer == "y"


def choose_run_mode():
    menu = "\n".join(
        [
            "1. 单模型运行",
            "2. 多模型对比运行",
        ]
    )
    console.print(Panel(menu, title="运行模式", border_style="cyan"))
    choice = clean_input(console.input("[bold]请选择运行模式，直接回车使用单模型：[/bold]"))

    if choice == "2":
        return "compare"

    return "single"


def choose_model_provider():
    models = get_available_models()
    default_provider = get_setting(
        "default_model_provider",
        get_default_model().get("provider", "deepseek"),
    )
    lines = []

    for index, model_info in enumerate(models, start=1):
        enabled_text = "默认启用" if model_info.get("enabled") else "可选"
        lines.append(
            f"{index}. {model_info.get('name')} - {model_info.get('model')} ({enabled_text})"
        )

    console.print(Panel("\n".join(lines), title="模型选择", border_style="cyan"))
    choice = clean_input(
        console.input(f"[bold]请选择模型，直接回车使用默认模型({default_provider})：[/bold]")
    )

    if not choice:
        return default_provider

    try:
        selected_index = int(choice) - 1
    except ValueError:
        console.print("[yellow]输入无效，已使用默认模型。[/yellow]")
        return default_provider

    if 0 <= selected_index < len(models):
        selected_model = models[selected_index]
        show_text(
            "已选择模型",
            f"{selected_model.get('name')} / {selected_model.get('model')}",
            "cyan",
        )
        return selected_model.get("provider", default_provider)

    console.print("[yellow]选项超出范围，已使用默认模型。[/yellow]")
    return default_provider


def choose_model_providers():
    models = get_available_models()
    lines = []

    for index, model_info in enumerate(models, start=1):
        lines.append(f"{index}. {model_info.get('name')} - {model_info.get('model')}")

    console.print(Panel("\n".join(lines), title="多模型对比选择", border_style="cyan"))
    choice = clean_input(console.input("[bold]请输入 2-3 个模型编号，用逗号分隔，例如 1,2,3：[/bold]"))

    selected_models = []
    for item in choice.split(","):
        item = item.strip()

        if not item:
            continue

        try:
            selected_index = int(item) - 1
        except ValueError:
            continue

        if 0 <= selected_index < len(models):
            provider = models[selected_index].get("provider")
            if provider not in selected_models:
                selected_models.append(provider)

    if len(selected_models) < 2:
        console.print("[yellow]至少需要选择 2 个模型，已默认选择前 2 个模型。[/yellow]")
        selected_models = [model.get("provider") for model in models[:2]]

    if len(selected_models) > 3:
        selected_models = selected_models[:3]

    return selected_models


def show_final_summary(state):
    run_summary = build_run_summary(state)
    success_text = "✅ 成功" if run_summary["success"] else "❌ 失败"
    success_style = "green" if run_summary["success"] else "red"

    console.print(Rule("[bold magenta]LangGraph 最终结果[/bold magenta]"))
    show_text("是否成功", success_text, success_style)
    show_text("修复次数", run_summary["retry_count"], "magenta")
    show_text("pytest 是否通过", "✅ True" if run_summary["test_success"] else "❌ False", "green" if run_summary["test_success"] else "red")
    show_text("coverage_percent", f"{run_summary['coverage_percent']}%", "cyan")
    show_text("quality_score", run_summary["quality_score"], "magenta")
    show_text("安全状态", run_summary["security_status"], "yellow")
    show_text("模型服务商", run_summary["model_provider"], "cyan")
    show_text("模型名称", state.get("model_name", ""), "cyan")
    show_text("报告路径", run_summary["report_path"], "magenta")
    show_text("runner_mode", run_summary.get("runner_mode", "python"), "magenta")
    show_text("runner_warning", run_summary.get("runner_warning", ""), "yellow")
    show_text("人工审批", state.get("approval_message", "无"), "magenta")
    show_text("最终 stdout", state["stdout"], "cyan")
    show_text("最终 error_log 摘要", summarize_error(state["error_log"]), "red")
    show_text("quality_summary", state.get("quality_summary", ""), "magenta")
    show_text("pytest stdout", state.get("test_stdout", ""), "cyan")
    show_text("pytest stderr 摘要", summarize_error(state.get("test_stderr", "")), "red")
    show_text("doc_result", state.get("doc_result", ""), "cyan")
    show_text("security_result", state.get("security_result", ""), "yellow")
    show_text("refactor_result", state.get("refactor_result", ""), "magenta")
    show_text("ui_result", state.get("ui_result", ""), "blue")


def show_full_state(state):
    console.print(Rule("[bold magenta]LangGraph 完整 State[/bold magenta]"))
    show_text("requirement", state["requirement"], "blue")
    show_text("model_provider", state.get("model_provider", ""), "cyan")
    show_text("model_name", state.get("model_name", ""), "cyan")
    show_text("model_base_url", state.get("model_base_url", ""), "cyan")
    show_text("product_result", state["product_result"], "blue")
    show_code("code", state["code"])
    show_text("tester_result", state["tester_result"], "yellow")
    show_code("test_code", state.get("test_code", ""))
    show_text("test_stdout", state.get("test_stdout", ""), "cyan")
    show_text("test_stderr", state.get("test_stderr", ""), "red")
    show_text("test_success", "✅ True" if state.get("test_success") else "❌ False", "green" if state.get("test_success") else "red")
    show_text("coverage_stdout", state.get("coverage_stdout", ""), "cyan")
    show_text("coverage_percent", f"{state.get('coverage_percent', 0)}%", "cyan")
    show_text("quality_score", state.get("quality_score", 0), "magenta")
    show_text("quality_summary", state.get("quality_summary", ""), "magenta")
    show_text("stdout", state["stdout"], "cyan")
    show_text("error_log", state["error_log"], "red")
    show_text("doc_result", state.get("doc_result", ""), "cyan")
    show_text("security_result", state.get("security_result", ""), "yellow")
    show_text("refactor_result", state.get("refactor_result", ""), "magenta")
    show_text("ui_result", state.get("ui_result", ""), "blue")
    show_text("require_human_approval", state.get("require_human_approval", False), "magenta")
    show_text("approved", state.get("approved", False), "magenta")
    show_text("approval_message", state.get("approval_message", ""), "magenta")
    show_text("retry_count", state["retry_count"], "magenta")
    show_text("success", "✅ True" if state["success"] else "❌ False", "green" if state["success"] else "red")


def show_plugin_results(state):
    console.print(Rule("[bold magenta]自定义 AI 模块结果[/bold magenta]"))

    plugin_results = state.get("plugin_results", [])
    if not plugin_results:
        show_text("插件结果", "未启用自定义 AI 模块", "magenta")
        return

    for result in plugin_results:
        title = f"{result.get('plugin_name', result.get('name', 'Plugin'))} - {result.get('status', 'unknown')}"
        detail = (
            f"摘要：{result.get('summary', '无摘要')}\n\n"
            f"{result.get('detail', result.get('content', '无内容'))}"
        )
        show_text(title, detail, "magenta")


def get_enabled_plugin_names():
    return [plugin.name for plugin in load_enabled_plugins()]


def build_markdown_report(state):
    run_summary = build_run_summary(state)
    enabled_plugins = "、".join(run_summary["enabled_plugins"]) or "无"
    return f"""# AI Multi-Agent Pipeline 运行报告

## 运行信息

- run_id：{state.get("run_id", "未生成")}
- 运行时间：{state.get("run_time", "未记录")}
- 模型服务商：{run_summary["model_provider"]}
- 模型名称：{state.get("model_name", "未记录")}
- base_url：{state.get("model_base_url", "未记录")}
- 状态文件路径：{state.get("state_path", "未保存")}
- 报告文件路径：{run_summary["report_path"]}
- 是否成功：{"成功" if run_summary["success"] else "失败"}
- 修复次数：{run_summary["retry_count"]}
- pytest 是否通过：{"是" if run_summary["test_success"] else "否"}
- 测试覆盖率：{run_summary["coverage_percent"]}%
- 质量评分：{run_summary["quality_score"]}
- 安全状态：{run_summary["security_status"]}
- 已启用插件：{enabled_plugins}
- 是否启用人工审批：{"是" if state.get("require_human_approval") else "否"}
- 是否通过审批：{"是" if state.get("approved") else "否"}
- 审批说明：{state.get("approval_message", "无")}

{build_run_summary_section(state)}

## 用户需求

{state.get("requirement", "")}

## Product Agent

{state.get("product_result", "")}

## Coder Agent 生成代码

```python
{state.get("code", "")}
```

## Tester Agent

{state.get("tester_result", "")}

{build_error_summary_section(state)}

## 自动生成的 pytest 测试代码

```python
{state.get("test_code", "")}
```

## pytest 运行结果

- test_success：{"通过" if state.get("test_success") else "未通过"}

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

当 pytest 或 Runner 任一失败时，LangGraph 会把测试失败信息、运行错误和 Sentry Agent 分析结果反馈给 Coder Agent，要求修复业务代码而不是修改测试。

## Sentry Agent

{state.get("sentry_result", "")}

## stdout

```text
{state.get("stdout", "")}
```

## error_log

```text
{state.get("error_log", "")}
```

{build_plugin_results_section(state)}
"""


def save_report(report, report_path):
    REPORT_DIR.mkdir(exist_ok=True)
    report_path = Path(report_path)
    report_path.parent.mkdir(exist_ok=True)
    report_path.write_text(report, encoding="utf-8")
    (REPORT_DIR / "latest_report.md").write_text(report, encoding="utf-8")
    return report_path


def persist_run_state(state):
    run_id = create_run_id()
    state_path = Path("runs") / f"{run_id}.json"
    report_path = Path("reports") / f"{run_id}.md"

    state["run_id"] = run_id
    state["run_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    state["enabled_plugins"] = get_enabled_plugin_names()
    state["state_path"] = str(state_path)
    state["report_path"] = str(report_path)

    report = build_markdown_report(state)
    save_report(report, report_path)
    saved_state_path = save_run_state(run_id, state)

    return run_id, saved_state_path, report_path


def persist_compare_states(compare_run_id, states):
    saved_paths = []

    for index, state in enumerate(states, start=1):
        state_run_id = f"{compare_run_id}_model{index}"
        state_path = Path("runs") / f"{state_run_id}.json"
        report_path = Path("reports") / f"{state_run_id}.md"

        state["run_id"] = state_run_id
        state["compare_run_id"] = compare_run_id
        state["run_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        state["enabled_plugins"] = get_enabled_plugin_names()
        state["state_path"] = str(state_path)
        state["report_path"] = str(report_path)

        report = build_markdown_report(state)
        save_report(report, report_path)
        saved_state_path = save_run_state(state_run_id, state)
        saved_paths.append(saved_state_path)

    compare_report_path = save_compare_report(compare_run_id, states)
    return saved_paths, compare_report_path


def run_compare_mode(requirement, require_human_approval, max_retry_count):
    providers = choose_model_providers()
    compare_run_id = create_run_id()
    states = []

    for provider in providers:
        show_text("正在运行模型", provider, "cyan")
        state = run_graph_demo(
            requirement,
            max_retry_count=max_retry_count,
            require_human_approval=require_human_approval,
            approved=not require_human_approval,
            model_provider=provider,
        )
        states.append(state)

    saved_paths, compare_report_path = persist_compare_states(compare_run_id, states)

    console.print(Rule("[bold magenta]多模型对比结果[/bold magenta]"))
    console.print(build_compare_markdown(states, compare_run_id))
    show_text("compare_run_id", compare_run_id, "magenta")
    show_text("状态文件", "\n".join(str(path) for path in saved_paths), "magenta")
    show_text("对比报告", compare_report_path, "magenta")


def main():
    requirement = choose_requirement()

    if requirement is None:
        return

    if not requirement:
        console.print("[bold red]需求不能为空。[/bold red]")
        return

    max_retry_count = int(get_setting("max_retry_count"))
    require_human_approval = choose_human_approval()
    run_mode = choose_run_mode()

    if run_mode == "compare":
        run_compare_mode(requirement, require_human_approval, max_retry_count)
        return

    model_provider = choose_model_provider()

    console.print(Rule("[bold magenta]LangGraph Demo 开始[/bold magenta]"))
    state = run_graph_demo(
        requirement,
        max_retry_count=max_retry_count,
        require_human_approval=require_human_approval,
        approved=not require_human_approval,
        model_provider=model_provider,
    )
    run_id, state_path, report_path = persist_run_state(state)

    show_final_summary(state)
    show_full_state(state)
    show_plugin_results(state)
    show_text("run_id", run_id, "magenta")
    show_text("状态保存路径", state_path, "magenta")
    show_text("报告路径", report_path, "magenta")


if __name__ == "__main__":
    main()

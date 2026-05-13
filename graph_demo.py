from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule
from rich.syntax import Syntax

from demo_cases import DEMO_CASES
from graph import run_graph_demo


console = Console()


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


def show_final_summary(state):
    success_text = "✅ 成功" if state["success"] else "❌ 失败"
    success_style = "green" if state["success"] else "red"

    console.print(Rule("[bold magenta]LangGraph 最终结果[/bold magenta]"))
    show_text("是否成功", success_text, success_style)
    show_text("修复次数", state["retry_count"], "magenta")
    show_text("最终 stdout", state["stdout"], "cyan")
    show_text("最终 error_log", state["error_log"], "red")


def show_full_state(state):
    console.print(Rule("[bold magenta]LangGraph 完整 State[/bold magenta]"))
    show_text("requirement", state["requirement"], "blue")
    show_text("product_result", state["product_result"], "blue")
    show_code("code", state["code"])
    show_text("tester_result", state["tester_result"], "yellow")
    show_text("stdout", state["stdout"], "cyan")
    show_text("error_log", state["error_log"], "red")
    show_text("retry_count", state["retry_count"], "magenta")
    show_text("success", "✅ True" if state["success"] else "❌ False", "green" if state["success"] else "red")


def show_plugin_results(state):
    console.print(Rule("[bold magenta]自定义 AI 模块结果[/bold magenta]"))

    plugin_results = state.get("plugin_results", [])
    if not plugin_results:
        show_text("插件结果", "未启用自定义 AI 模块", "magenta")
        return

    for result in plugin_results:
        title = f"{result.get('name', 'Plugin')} - {result.get('status', 'unknown')}"
        show_text(title, result.get("content", "无内容"), "magenta")


def main():
    requirement = choose_requirement()

    if requirement is None:
        return

    if not requirement:
        console.print("[bold red]需求不能为空。[/bold red]")
        return

    console.print(Rule("[bold magenta]LangGraph Demo 开始[/bold magenta]"))
    state = run_graph_demo(requirement)

    show_final_summary(state)
    show_full_state(state)
    show_plugin_results(state)


if __name__ == "__main__":
    main()

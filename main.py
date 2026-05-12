from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule
from rich.syntax import Syntax

from agents import coder_agent, product_agent, sentry_agent, tester_agent
from demo_cases import DEMO_CASES
from utils.code_runner import run_code, save_code


MAX_FIX_TIMES = 3

console = Console()


def clean_input(text):
    """Remove hidden characters that may appear in piped input."""
    return text.lstrip("\ufeff").strip()


def get_error_summary(stderr):
    """Return the first useful line from stderr."""
    lines = stderr.strip().splitlines()

    if not lines:
        return "没有 stderr，可能是运行超时或未知错误。"

    return lines[-1]


def show_stage(title, style):
    console.print(Rule(f"[bold {style}]{title}[/bold {style}]", style=style))


def show_text(title, text, style):
    console.print(Panel(text or "无内容", title=title, border_style=style))


def show_code(title, code):
    syntax = Syntax(code or "", "python", theme="monokai", line_numbers=True)
    console.print(Panel(syntax, title=title, border_style="green"))


def print_run_result(run_result):
    """Print stdout, stderr, and success state."""
    console.print(f"[bold]returncode:[/bold] {run_result['returncode']}")

    if run_result["stdout"]:
        show_text("stdout", run_result["stdout"], "cyan")

    if run_result["returncode"] == 0:
        console.print("[bold green]✅ 运行成功[/bold green]")
    else:
        console.print("[bold red]❌ 运行失败[/bold red]")
        if run_result["stderr"]:
            show_text("stderr", run_result["stderr"], "red")


def show_fix_status(fix_count, error_summary, status, style):
    content = (
        f"当前第 {fix_count} 轮修复\n"
        f"错误摘要：{error_summary}\n"
        f"修复状态：{status}"
    )
    console.print(Panel(content, title="自动修复状态", border_style=style))


def choose_requirement():
    menu = "\n".join(
        [
            "1. 简单案例",
            "2. 翻车修复案例",
            "3. 综合案例",
            "4. 自定义输入",
        ]
    )
    console.print(Panel(menu, title="请选择演示案例", border_style="magenta"))

    choice = clean_input(console.input("[bold]请输入选项 1-4：[/bold]"))

    if choice in DEMO_CASES:
        case = DEMO_CASES[choice]
        show_text("已选择演示案例", case["name"], "magenta")
        show_text("用户输入需求", case["requirement"], "magenta")
        return case["requirement"]

    if choice == "4":
        return clean_input(console.input("[bold]请输入自定义需求：[/bold]"))

    console.print("[bold red]无效选项，请输入 1、2、3 或 4。[/bold red]")
    return None


def run_pipeline(requirement):
    """Run the multi-agent development pipeline."""
    if not requirement:
        console.print("[bold red]需求不能为空。[/bold red]")
        return

    show_stage("Product Agent 正在分析需求", "blue")
    product_result = product_agent(requirement)
    show_text("Product Agent 结果：产品方案", product_result, "blue")

    show_stage("Coder Agent 正在生成代码", "green")
    code_result = coder_agent(product_result)
    show_code("Coder Agent 结果：生成代码", code_result)

    show_stage("Tester Agent 正在静态检查代码", "yellow")
    test_result = tester_agent(code_result)
    show_text("Tester Agent 结果：静态检查", test_result, "yellow")

    show_stage("Code Runner 正在保存代码", "cyan")
    code_file = save_code(code_result)
    show_text("代码保存结果", f"已保存到：{code_file}", "cyan")

    show_stage("Code Runner 正在运行代码", "cyan")
    run_result = run_code()
    show_text("代码运行阶段", "首次运行 generated_code.py", "cyan")
    print_run_result(run_result)

    for fix_count in range(1, MAX_FIX_TIMES + 1):
        if run_result["returncode"] == 0:
            break

        error_summary = get_error_summary(run_result["stderr"])
        show_fix_status(fix_count, error_summary, "准备修复", "yellow")

        show_stage("Sentry Agent 正在分析错误", "red")
        sentry_result = sentry_agent(code_result, run_result["stderr"])
        show_text("Sentry Agent 结果：错误分析", sentry_result, "red")

        show_stage("Coder Agent 正在修复代码", "green")
        code_result = coder_agent(
            product_result,
            code=code_result,
            error_log=run_result["stderr"],
            sentry_result=sentry_result,
        )
        show_code("Coder Agent 结果：修复代码", code_result)

        show_stage("Code Runner 正在保存并重新运行", "cyan")
        save_code(code_result)
        run_result = run_code()
        print_run_result(run_result)
        show_fix_status(
            fix_count,
            error_summary,
            "✅ 修复成功" if run_result["returncode"] == 0 else "❌ 修复失败",
            "green" if run_result["returncode"] == 0 else "red",
        )

    if run_result["returncode"] != 0:
        show_stage("最终错误", "red")
        show_text("自动修复 3 次后仍然失败", run_result["stderr"], "red")


def main():
    try:
        requirement = choose_requirement()
        if requirement is not None:
            run_pipeline(requirement)
    except Exception as error:
        console.print(f"[bold red]运行失败：{error}[/bold red]")


if __name__ == "__main__":
    main()

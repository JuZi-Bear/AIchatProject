import ast
import os
import subprocess
import sys
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parent.parent

load_dotenv(PROJECT_ROOT / ".env")

OUTPUT_DIR = PROJECT_ROOT / "output"
CODE_FILE = OUTPUT_DIR / "generated_code.py"
DEFAULT_TIMEOUT = 10


def get_timeout():
    """Read the code run timeout from .env or environment variables."""
    timeout_text = os.getenv("CODE_RUN_TIMEOUT", str(DEFAULT_TIMEOUT)).strip()

    try:
        timeout = int(timeout_text)
    except ValueError:
        return DEFAULT_TIMEOUT

    if timeout <= 0:
        return DEFAULT_TIMEOUT

    return timeout


def check_code_safety(code):
    """Return safety problems found in generated Python code."""
    problems = []

    try:
        tree = ast.parse(code)
    except SyntaxError:
        return problems

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == "subprocess":
                    problems.append("禁止导入 subprocess")

        if isinstance(node, ast.ImportFrom):
            if node.module == "subprocess":
                problems.append("禁止导入 subprocess")
            if node.module == "os":
                for alias in node.names:
                    if alias.name == "remove":
                        problems.append("禁止使用 os.remove")
            if node.module == "shutil":
                for alias in node.names:
                    if alias.name == "rmtree":
                        problems.append("禁止使用 shutil.rmtree")

        if isinstance(node, ast.Call):
            function = node.func

            if isinstance(function, ast.Name):
                if function.id == "eval":
                    problems.append("禁止使用 eval")
                if function.id == "exec":
                    problems.append("禁止使用 exec")

            if isinstance(function, ast.Attribute) and isinstance(function.value, ast.Name):
                module_name = function.value.id
                function_name = function.attr

                if module_name == "os" and function_name == "remove":
                    problems.append("禁止调用 os.remove")
                if module_name == "shutil" and function_name == "rmtree":
                    problems.append("禁止调用 shutil.rmtree")
                if module_name == "subprocess":
                    problems.append("禁止使用 subprocess")

    return list(dict.fromkeys(problems))


def clean_code(code):
    """Remove Markdown code fences from generated code."""
    lines = code.strip().splitlines()

    if lines and lines[0].startswith("```"):
        lines = lines[1:]

    if lines and lines[-1].startswith("```"):
        lines = lines[:-1]

    return "\n".join(lines).strip() + "\n"


def save_code(code):
    """Save generated Python code to output/generated_code.py."""
    OUTPUT_DIR.mkdir(exist_ok=True)

    clean_python_code = clean_code(code)
    CODE_FILE.write_text(clean_python_code, encoding="utf-8")

    return CODE_FILE


def run_code(timeout=None):
    """Run output/generated_code.py and return stdout, stderr, and returncode."""
    if not CODE_FILE.exists():
        return {
            "stdout": "",
            "stderr": "代码文件不存在，请先生成并保存代码。",
            "returncode": 1,
        }

    code = CODE_FILE.read_text(encoding="utf-8")
    safety_problems = check_code_safety(code)

    if safety_problems:
        return {
            "stdout": "",
            "stderr": "安全检查失败：\n" + "\n".join(f"- {problem}" for problem in safety_problems),
            "returncode": 1,
        }

    run_timeout = timeout or get_timeout()

    try:
        result = subprocess.run(
            [sys.executable, str(CODE_FILE)],
            input="",
            capture_output=True,
            text=True,
            timeout=run_timeout,
            encoding="utf-8",
            errors="replace",
        )
    except subprocess.TimeoutExpired as error:
        return {
            "stdout": error.stdout or "",
            "stderr": f"代码运行超时，超过 {run_timeout} 秒，可能在等待用户输入或进入了死循环。",
            "returncode": 1,
        }

    return {
        "stdout": result.stdout,
        "stderr": result.stderr,
        "returncode": result.returncode,
    }

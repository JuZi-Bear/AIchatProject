import os
import subprocess
import sys
from pathlib import Path

from dotenv import load_dotenv

from utils.code_runner import CODE_FILE, check_code_safety, clean_code


PROJECT_ROOT = Path(__file__).resolve().parent.parent

load_dotenv(PROJECT_ROOT / ".env")

TESTS_DIR = PROJECT_ROOT / "tests"
TEST_FILE = TESTS_DIR / "test_generated_code.py"
DEFAULT_TIMEOUT = 20


def get_test_timeout():
    timeout_text = os.getenv("TEST_RUN_TIMEOUT", str(DEFAULT_TIMEOUT)).strip()

    try:
        timeout = int(timeout_text)
    except ValueError:
        return DEFAULT_TIMEOUT

    if timeout <= 0:
        return DEFAULT_TIMEOUT

    return timeout


def save_test_code(test_code):
    """Save pytest code to tests/test_generated_code.py."""
    TESTS_DIR.mkdir(exist_ok=True)
    clean_test_code = clean_code(test_code)
    TEST_FILE.write_text(clean_test_code, encoding="utf-8")
    return TEST_FILE


def run_tests(timeout=None):
    """Run pytest and return stdout, stderr, and returncode."""
    if not TEST_FILE.exists():
        return {
            "stdout": "",
            "stderr": "测试文件不存在，请先生成并保存 pytest 测试代码。",
            "returncode": 1,
        }

    if not CODE_FILE.exists():
        return {
            "stdout": "",
            "stderr": "被测代码文件不存在，请先保存 output/generated_code.py。",
            "returncode": 1,
        }

    code = CODE_FILE.read_text(encoding="utf-8")
    safety_problems = check_code_safety(code)

    if safety_problems:
        return {
            "stdout": "",
            "stderr": "测试前安全检查失败：\n" + "\n".join(f"- {problem}" for problem in safety_problems),
            "returncode": 1,
        }

    run_timeout = timeout or get_test_timeout()

    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", str(TEST_FILE), "-q"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=run_timeout,
            encoding="utf-8",
            errors="replace",
        )
    except subprocess.TimeoutExpired as error:
        return {
            "stdout": error.stdout or "",
            "stderr": f"pytest 运行超时，超过 {run_timeout} 秒。",
            "returncode": 1,
        }

    return {
        "stdout": result.stdout,
        "stderr": result.stderr,
        "returncode": result.returncode,
    }


def parse_coverage_percent(coverage_output):
    """Extract TOTAL coverage percent from coverage report output."""
    for line in coverage_output.splitlines():
        parts = line.split()

        if not parts:
            continue

        if parts[0] == "TOTAL" and parts[-1].endswith("%"):
            percent_text = parts[-1].replace("%", "")

            try:
                return int(percent_text)
            except ValueError:
                return 0

    return 0


def run_tests_with_coverage(timeout=None):
    """Run pytest with coverage and return test and coverage results."""
    if not TEST_FILE.exists():
        return {
            "test_stdout": "",
            "test_stderr": "测试文件不存在，请先生成并保存 pytest 测试代码。",
            "coverage_stdout": "",
            "coverage_percent": 0,
            "returncode": 1,
        }

    if not CODE_FILE.exists():
        return {
            "test_stdout": "",
            "test_stderr": "被测代码文件不存在，请先保存 output/generated_code.py。",
            "coverage_stdout": "",
            "coverage_percent": 0,
            "returncode": 1,
        }

    code = CODE_FILE.read_text(encoding="utf-8")
    safety_problems = check_code_safety(code)

    if safety_problems:
        return {
            "test_stdout": "",
            "test_stderr": "测试前安全检查失败：\n" + "\n".join(f"- {problem}" for problem in safety_problems),
            "coverage_stdout": "",
            "coverage_percent": 0,
            "returncode": 1,
        }

    run_timeout = timeout or get_test_timeout()

    try:
        subprocess.run(
            [sys.executable, "-m", "coverage", "erase"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=run_timeout,
            encoding="utf-8",
            errors="replace",
        )

        test_result = subprocess.run(
            [sys.executable, "-m", "coverage", "run", "-m", "pytest", str(TEST_FILE), "-q"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=run_timeout,
            encoding="utf-8",
            errors="replace",
        )

        coverage_result = subprocess.run(
            [sys.executable, "-m", "coverage", "report"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=run_timeout,
            encoding="utf-8",
            errors="replace",
        )
    except subprocess.TimeoutExpired as error:
        return {
            "test_stdout": error.stdout or "",
            "test_stderr": f"pytest + coverage 运行超时，超过 {run_timeout} 秒。",
            "coverage_stdout": "",
            "coverage_percent": 0,
            "returncode": 1,
        }

    test_stderr = test_result.stderr
    coverage_stdout = coverage_result.stdout

    if coverage_result.stderr:
        test_stderr = (test_stderr + "\n" + coverage_result.stderr).strip()

    if test_result.returncode != 0:
        returncode = test_result.returncode
    else:
        returncode = coverage_result.returncode

    return {
        "test_stdout": test_result.stdout,
        "test_stderr": test_stderr,
        "coverage_stdout": coverage_stdout,
        "coverage_percent": parse_coverage_percent(coverage_stdout),
        "returncode": returncode,
    }

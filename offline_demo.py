def product_demo(requirement):
    return f"""1. 功能列表
- 根据用户需求生成一个最小可运行 Python 程序
- 展示代码运行结果
- 如果运行失败，进入自动修复流程

2. 技术需求
- Python 3
- 命令行运行
- 不依赖复杂外部服务

3. 开发步骤
- 读取用户需求：{requirement}
- 生成简单 Python 代码
- 保存并运行代码
- 根据结果判断是否需要修复
"""


def coder_demo(product_plan="", error_log=None):
    """Return simple preset code when the real API is unavailable."""
    if error_log:
        if (
            "get_second_largest" in error_log
            or "第二大" in product_plan
            or "AssertionError" in error_log
            or "test_generated_code" in error_log
            or "pytest" in error_log
        ):
            return """def get_second_largest(nums):
    unique_numbers = sorted(set(nums), reverse=True)

    if len(unique_numbers) < 2:
        return None

    return unique_numbers[1]


if __name__ == "__main__":
    demo_numbers = [5, 1, 5, 3, 2]
    print("第二大的不同数字是:", get_second_largest(demo_numbers))
"""

        if "EOFError" in error_log or "input" in error_log:
            return """try:
    name = input("请输入你的姓名: ")
except EOFError:
    name = "默认用户"
print("hello", name)
"""

        return """try:
    print("离线修复后的演示代码运行成功")
except Exception as error:
    print("运行时出现错误：", error)
"""

    if "成绩" in product_plan or "学生" in product_plan:
        return """students = [
    {"name": "小明", "score": 92},
    {"name": "小红", "score": 85},
    {"name": "小刚", "score": 76},
    {"name": "小丽", "score": 98},
    {"name": "小王", "score": 61},
]


def show_score_report():
    scores = [student["score"] for student in students]
    average_score = sum(scores) / len(scores)
    best_student = max(students, key=lambda student: student["score"])
    lowest_student = min(students, key=lambda student: student["score"])
    passed_count = len([score for score in scores if score >= 60])

    print("平均分:", round(average_score, 2))
    print("最高分学生:", best_student["name"], best_student["score"])
    print("最低分学生:", lowest_student["name"], lowest_student["score"])
    print("及格人数:", passed_count)


show_score_report()
"""

    if "get_second_largest" in product_plan or "第二大" in product_plan:
        return """def get_second_largest(nums):
    return sorted(nums)[-2]


if __name__ == "__main__":
    print(get_second_largest([1, 2, 3]))
"""

    if "input" in product_plan or "姓名" in product_plan:
        return """name = input("请输入你的姓名: ")
print("hello", name)
"""

    return """print("hello world")
"""


def tester_demo(code=""):
    if "input(" in code:
        risk_note = "存在 input 调用，自动运行时可能因为没有人工输入而失败"
        conclusion = "需要关注"
    else:
        risk_note = "无明显风险"
        conclusion = "通过"

    return """1. 是否有明显语法问题：无
2. 是否有明显逻辑问题：无
3. 是否缺少入口函数、主循环或必要的调用：无，简单脚本可直接运行
4. 修改建议：{risk_note}
5. 检查结论：{conclusion}
""".format(risk_note=risk_note, conclusion=conclusion)


def pytest_demo(requirement="", code=""):
    if "get_second_largest" in requirement or "第二大" in requirement or "get_second_largest" in code:
        return """import importlib.util
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "output" / "generated_code.py"
spec = importlib.util.spec_from_file_location("generated_code", MODULE_PATH)
generated_code = importlib.util.module_from_spec(spec)
spec.loader.exec_module(generated_code)


def test_get_second_largest_normal_input():
    assert generated_code.get_second_largest([1, 3, 2]) == 2


def test_get_second_largest_with_duplicates():
    assert generated_code.get_second_largest([5, 5, 4, 3]) == 4


def test_get_second_largest_with_negative_numbers():
    assert generated_code.get_second_largest([-10, -3, -7]) == -7


def test_get_second_largest_empty_list():
    assert generated_code.get_second_largest([]) is None


def test_get_second_largest_single_item():
    assert generated_code.get_second_largest([1]) is None
"""

    return """import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CODE_FILE = PROJECT_ROOT / "output" / "generated_code.py"


def test_generated_script_runs_successfully():
    result = subprocess.run(
        [sys.executable, str(CODE_FILE)],
        input="测试用户\\n",
        capture_output=True,
        text=True,
        timeout=5,
        encoding="utf-8",
        errors="replace",
    )

    assert result.returncode == 0
    assert result.stdout.strip() != ""
"""


def sentry_demo(error_log):
    if "安全检查失败" in error_log:
        reason = "代码包含被禁止的危险操作，运行器在执行前主动拦截。"
        suggestion = "移除 os.remove、shutil.rmtree、subprocess、eval 或 exec 等危险调用。"
        problem_type = "运行安全问题。"
    elif "No module named pytest" in error_log:
        reason = "运行环境缺少 pytest，测试命令无法启动。"
        suggestion = "先安装 requirements.txt 中的依赖，或执行 python -m pip install pytest。"
        problem_type = "运行环境问题。"
    elif "pytest" in error_log or "test_generated_code" in error_log or "AssertionError" in error_log:
        reason = "pytest 自动测试失败，通常说明代码逻辑没有覆盖正常输入、重复值或边界情况。"
        suggestion = "保持测试用例不变，修复业务代码，让函数正确处理空列表、单元素列表、重复数字和负数。"
        problem_type = "代码逻辑问题或边界条件没处理。"
    else:
        reason = "如果错误与 input 或 EOFError 有关，说明自动运行环境没有人工输入。"
        suggestion = "使用 try-except 捕获 EOFError，并提供默认值，确保代码在无人输入时也能结束。"
        problem_type = "运行环境问题或交互输入问题。"

    return f"""1. 错误摘要
代码运行失败，错误日志为：
{error_log}

2. 错误原因
{reason}

3. 问题类型
{problem_type}

4. 修复建议
{suggestion}
"""

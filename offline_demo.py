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


def sentry_demo(error_log):
    if "安全检查失败" in error_log:
        reason = "代码包含被禁止的危险操作，运行器在执行前主动拦截。"
        suggestion = "移除 os.remove、shutil.rmtree、subprocess、eval 或 exec 等危险调用。"
    else:
        reason = "如果错误与 input 或 EOFError 有关，说明自动运行环境没有人工输入。"
        suggestion = "使用 try-except 捕获 EOFError，并提供默认值，确保代码在无人输入时也能结束。"

    return f"""1. 错误摘要
代码运行失败，错误日志为：
{error_log}

2. 错误原因
{reason}

3. 修复建议
{suggestion}
"""

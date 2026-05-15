from utils.code_runner import check_code_safety, clean_code


def get_coverage_score(coverage_percent):
    if coverage_percent >= 90:
        return 20

    if coverage_percent >= 70:
        return 15

    if coverage_percent >= 50:
        return 10

    return 5


def get_retry_score(retry_count):
    if retry_count == 0:
        return 15

    if retry_count == 1:
        return 10

    if retry_count == 2:
        return 5

    return 0


def evaluate_quality(state):
    """Evaluate final code quality and write score fields into state."""
    test_score = 30 if state.get("test_success") else 0
    run_score = 20 if state.get("success") else 0

    coverage_percent = int(state.get("coverage_percent", 0) or 0)
    coverage_score = get_coverage_score(coverage_percent)

    clean_python_code = clean_code(state.get("code", ""))
    safety_problems = check_code_safety(clean_python_code)
    safety_passed = len(safety_problems) == 0
    safety_score = 15 if safety_passed else 0

    retry_count = int(state.get("retry_count", 0) or 0)
    retry_score = get_retry_score(retry_count)

    quality_score = test_score + run_score + coverage_score + safety_score + retry_score

    summary_lines = [
        f"pytest 通过：{test_score}/30",
        f"程序运行成功：{run_score}/20",
        f"测试覆盖率 {coverage_percent}%：{coverage_score}/20",
        f"安全检查：{safety_score}/15",
        f"自动修复次数 {retry_count}：{retry_score}/15",
    ]

    if safety_problems:
        summary_lines.append("安全问题：" + "；".join(safety_problems))

    state["quality_score"] = quality_score
    state["quality_summary"] = "\n".join(summary_lines)

    return state


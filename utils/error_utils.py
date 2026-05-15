ERROR_KEYWORDS = [
    "Error",
    "Exception",
    "Traceback",
    "SyntaxError",
    "NameError",
    "TypeError",
    "IndexError",
    "ValueError",
    "AssertionError",
    "ImportError",
    "ModuleNotFoundError",
    "FAILED",
    "failed",
    "timeout",
    "超时",
    "失败",
    "错误",
]

NON_RETRYABLE_KEYWORDS = [
    "用户拒绝执行",
    "人工审批未通过",
    "等待人工确认",
    "安全检查失败",
    "API Key",
    "未检测到",
]

RETRYABLE_KEYWORDS = [
    "Traceback",
    "SyntaxError",
    "NameError",
    "TypeError",
    "IndexError",
    "ValueError",
    "AssertionError",
    "EOFError",
    "ZeroDivisionError",
    "FAILED",
    "pytest",
    "test_generated_code",
    "代码运行超时",
    "运行超时",
]


def summarize_error(error_log, max_length=260):
    """Return a short, demo-friendly summary from stderr or pytest output."""
    lines = [line.strip() for line in (error_log or "").splitlines() if line.strip()]

    if not lines:
        return "无错误"

    keyword_lines = [
        line
        for line in lines
        if any(keyword in line for keyword in ERROR_KEYWORDS)
    ]
    selected_lines = keyword_lines[:3] or lines[:3]
    summary = "\n".join(selected_lines)

    if len(summary) > max_length:
        return summary[:max_length] + "..."

    return summary


def format_error_for_display(error_log, demo_mode=True):
    """Show summary in demo mode and full error in development mode."""
    if demo_mode:
        return summarize_error(error_log)

    return error_log or "无错误"


def is_retryable_error(error_log):
    """Return True when an error is likely fixable by regenerating code."""
    text = error_log or ""

    if not text.strip():
        return False

    if any(keyword in text for keyword in NON_RETRYABLE_KEYWORDS):
        return False

    return any(keyword in text for keyword in RETRYABLE_KEYWORDS)


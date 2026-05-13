import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

from offline_demo import coder_demo, product_demo, sentry_demo, tester_demo


PROJECT_ROOT = Path(__file__).resolve().parent

load_dotenv(PROJECT_ROOT / ".env")

DEFAULT_BASE_URL = "https://api.deepseek.com"
DEFAULT_MODEL = "deepseek-chat"


def get_config(name, default=""):
    return os.getenv(name, default).strip()


def is_offline_mode():
    return get_config("OFFLINE_MODE", "false").lower() in ("1", "true", "yes", "on")


def should_use_offline_demo():
    return is_offline_mode() or not get_config("DEEPSEEK_API_KEY")


def create_deepseek_client():
    """Create a DeepSeek client with the OpenAI-compatible API."""
    api_key = get_config("DEEPSEEK_API_KEY")
    base_url = get_config("DEEPSEEK_BASE_URL", DEFAULT_BASE_URL)

    if not api_key:
        raise RuntimeError("请先设置 DEEPSEEK_API_KEY，或将 OFFLINE_MODE 设置为 true")

    return OpenAI(
        api_key=api_key,
        base_url=base_url,
    )


def ask_deepseek(system_prompt, user_prompt):
    """Send one request to DeepSeek and return the text result."""
    client = create_deepseek_client()
    model = get_config("DEEPSEEK_MODEL", DEFAULT_MODEL)

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )

    return response.choices[0].message.content


def product_agent(requirement):
    """Turn the user's idea into a simple product plan."""
    prompt = f"""
请拆解下面的用户需求：

{requirement}

必须严格围绕上面的用户需求，不要假设其他产品。

请用简单清晰的中文输出：
1. 功能列表
2. 技术需求
3. 开发步骤
"""

    if should_use_offline_demo():
        return product_demo(requirement)

    try:
        return ask_deepseek(
            system_prompt="你是一名专业产品经理，擅长把想法拆成可开发任务。",
            user_prompt=prompt,
        )
    except Exception as error:
        print(f"DeepSeek Product Agent 调用失败，使用离线演示响应：{error}")
        return product_demo(requirement)


def coder_agent(product_plan, code=None, error_log=None, sentry_result=None):
    """Generate new code first, or fix code after a failed run."""
    if code and error_log:
        prompt = f"""
下面的 Python 代码运行失败了，请根据错误日志和修复建议重新生成完整代码。

原始产品方案：
{product_plan}

原始代码：
{code}

错误日志：
{error_log}

Sentry Agent 的分析和修复建议：
{sentry_result}

要求：
1. 输出修复后的完整 Python 代码
2. 代码简单，适合初学者阅读
3. 不要实现复杂功能
4. 必须根据错误修改代码，不要原样返回旧代码
5. 如果错误和 input 或 EOFError 有关，即使原需求提到 input，也必须使用 try-except 捕获 EOFError，并提供默认值，确保代码在没有人工输入时也能运行结束
6. 只输出 Python 代码，不要使用 Markdown 代码块，不要解释
"""
    else:
        prompt = f"""
请根据下面的产品方案编写一个最小可运行的 Python 示例：

{product_plan}

要求：
1. 代码简单，适合初学者阅读
2. 不要实现复杂功能
3. 只输出 Python 代码，不要使用 Markdown 代码块，不要解释
"""

    if should_use_offline_demo():
        return coder_demo(product_plan, error_log)

    try:
        return ask_deepseek(
            system_prompt="你是一名 Python 程序员，擅长写简单清晰的入门代码。",
            user_prompt=prompt,
        )
    except Exception as error:
        print(f"DeepSeek Coder Agent 调用失败，使用离线演示响应：{error}")
        return coder_demo(product_plan, error_log)


def sentry_agent(code, error_log):
    """Use DeepSeek to analyze a failed Python run."""
    prompt = f"""
下面的 Python 代码运行失败了。

原始代码：
{code}

错误日志 stderr：
{error_log}

请用简单清晰的中文输出：
1. 错误摘要
2. 错误原因
3. 修复建议

注意：
如果错误是 EOFError 或 input 读取失败，请明确建议使用 try-except 捕获 EOFError，并在没有输入时使用默认值。
本项目的代码会被自动运行，不能依赖人工在终端输入。
"""

    if should_use_offline_demo():
        return sentry_demo(error_log)

    try:
        return ask_deepseek(
            system_prompt="你是一名错误分析工程师，擅长根据 Python stderr 定位问题并给出修复建议。",
            user_prompt=prompt,
        )
    except Exception as error:
        print(f"DeepSeek Sentry Agent 调用失败，使用离线演示响应：{error}")
        return sentry_demo(error_log)


def tester_agent(code):
    """Use DeepSeek to review generated Python code without running it."""
    prompt = f"""
请静态检查下面这段 Python 代码，不要运行代码：

{code}

请用简单清晰的中文输出：
1. 是否有明显语法问题
2. 是否有明显逻辑问题
3. 是否缺少入口函数、主循环或必要的调用
4. 修改建议
5. 检查结论：通过 / 需要修改
"""

    if should_use_offline_demo():
        return tester_demo(code)

    try:
        return ask_deepseek(
            system_prompt="你是一名 Python 测试工程师，擅长做简单的代码静态检查。",
            user_prompt=prompt,
        )
    except Exception as error:
        print(f"DeepSeek Tester Agent 调用失败，使用离线演示响应：{error}")
        return tester_demo(code)

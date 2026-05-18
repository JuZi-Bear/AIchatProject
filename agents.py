from offline_demo import coder_demo, product_demo, pytest_demo, sentry_demo, tester_demo
from model_manager import (
    DEFAULT_PROVIDER,
    get_config,
    get_current_model_info,
    get_llm_client,
    is_offline_mode,
)
from utils.prompt_loader import render_prompt_by_name


DEFAULT_MODEL = get_current_model_info(DEFAULT_PROVIDER).get("model", "deepseek-chat")
missing_api_key_warned = False


def _render_prompt_or_fallback(prompt_name, variables, fallback):
    try:
        return render_prompt_by_name(prompt_name, variables)
    except Exception as error:
        print(f"Prompt 模板加载失败，使用内置 Prompt：{prompt_name}，原因：{error}")
        return fallback


def show_missing_api_key_tip(provider=None):
    global missing_api_key_warned

    if missing_api_key_warned:
        return

    model_info = get_current_model_info(provider)
    env_key = model_info.get("env_key", "")
    model_name = model_info.get("name", "当前模型")

    print(f"未检测到 {env_key}，{model_name} 已自动切换到离线演示模式。")
    print("如需调用真实模型 API，请复制 .env.example 为 .env，并填写对应 API Key。")
    missing_api_key_warned = True


def should_use_offline_demo(provider=None):
    if is_offline_mode():
        return True

    model_info = get_current_model_info(provider)
    env_key = model_info.get("env_key", "")

    if not get_config(env_key):
        show_missing_api_key_tip(provider)
        return True

    return False


def ask_llm(system_prompt, user_prompt, provider=None):
    """Send one request to the selected OpenAI-compatible model."""
    client = get_llm_client(provider)
    model_info = get_current_model_info(provider)

    response = client.chat.completions.create(
        model=model_info.get("model", DEFAULT_MODEL),
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )

    return response.choices[0].message.content


def product_agent(requirement, provider=None):
    """Turn the user's idea into a simple product plan."""
    fallback_prompt = f"""
请拆解下面的用户需求：

{requirement}

必须严格围绕上面的用户需求，不要假设其他产品。

请用简单清晰的中文输出：
1. 功能列表
2. 技术需求
3. 开发步骤
"""
    prompt = _render_prompt_or_fallback(
        "product_agent",
        {"requirement": requirement},
        fallback_prompt,
    )

    if should_use_offline_demo(provider):
        return product_demo(requirement)

    try:
        return ask_llm(
            system_prompt="你是一名专业产品经理，擅长把想法拆成可开发任务。",
            user_prompt=prompt,
            provider=provider,
        )
    except Exception as error:
        print(f"Product Agent 模型调用失败，使用离线演示响应：{error}")
        return product_demo(requirement)


def coder_agent(
    product_plan,
    code=None,
    error_log=None,
    sentry_result=None,
    requirement=None,
    test_code=None,
    test_stdout=None,
    test_stderr=None,
    provider=None,
):
    """Generate new code first, or fix code after a failed run."""
    has_test_failure = bool(test_stdout or test_stderr)
    has_runtime_failure = bool(error_log)

    if code and (has_runtime_failure or has_test_failure):
        mode_instruction = "下面的 Python 代码运行或 pytest 自动测试失败了，请根据用户需求、错误日志、测试结果和修复建议重新生成完整代码。"
        fallback_prompt = f"""
下面的 Python 代码运行或 pytest 自动测试失败了，请根据用户需求、错误日志、测试结果和修复建议重新生成完整代码。

原始用户需求：
{requirement or "未提供"}

原始产品方案：
{product_plan}

原始代码：
{code}

错误日志：
{error_log}

pytest 测试代码：
{test_code or "未提供"}

pytest stdout：
{test_stdout or "无"}

pytest stderr：
{test_stderr or "无"}

Sentry Agent 的分析和修复建议：
{sentry_result}

要求：
1. 输出修复后的完整 Python 代码
2. 代码简单，适合初学者阅读
3. 不要实现复杂功能
4. 必须根据错误修改代码，不要原样返回旧代码
5. 如果错误和 input 或 EOFError 有关，即使原需求提到 input，也必须使用 try-except 捕获 EOFError，并提供默认值，确保代码在没有人工输入时也能运行结束
6. 如果 pytest 失败，请修复业务代码本身，不要修改测试用例来强行通过
7. 只输出 Python 代码，不要使用 Markdown 代码块，不要解释
"""
    else:
        mode_instruction = "请根据下面的产品方案编写一个最小可运行的 Python 示例。"
        fallback_prompt = f"""
请根据下面的产品方案编写一个最小可运行的 Python 示例：

{product_plan}

要求：
1. 代码简单，适合初学者阅读
2. 不要实现复杂功能
3. 只输出 Python 代码，不要使用 Markdown 代码块，不要解释
"""

    prompt = _render_prompt_or_fallback(
        "coder_agent",
        {
            "mode_instruction": mode_instruction,
            "requirement": requirement or "未提供",
            "product_result": product_plan,
            "code": code or "无",
            "error_log": error_log or "无",
            "test_code": test_code or "未提供",
            "test_stdout": test_stdout or "无",
            "test_stderr": test_stderr or "无",
            "sentry_result": sentry_result or "无",
        },
        fallback_prompt,
    )

    if should_use_offline_demo(provider):
        repair_log = "\n".join(
            text
            for text in [error_log or "", test_stdout or "", test_stderr or "", sentry_result or ""]
            if text
        )
        return coder_demo(product_plan, repair_log or None)

    try:
        return ask_llm(
            system_prompt="你是一名 Python 程序员，擅长写简单清晰的入门代码。",
            user_prompt=prompt,
            provider=provider,
        )
    except Exception as error:
        print(f"Coder Agent 模型调用失败，使用离线演示响应：{error}")
        repair_log = "\n".join(
            text
            for text in [error_log or "", test_stdout or "", test_stderr or "", sentry_result or ""]
            if text
        )
        return coder_demo(product_plan, repair_log or None)


def sentry_agent(code, error_log, test_code=None, test_stdout=None, test_stderr=None, provider=None):
    """Use DeepSeek to analyze a failed Python run."""
    fallback_prompt = f"""
下面的 Python 代码运行或 pytest 自动测试失败了。

原始代码：
{code}

错误日志 stderr：
{error_log}

pytest 测试代码：
{test_code or "未提供"}

pytest stdout：
{test_stdout or "无"}

pytest stderr：
{test_stderr or "无"}

请用简单清晰的中文输出：
1. 错误摘要
2. 错误原因
3. 判断问题类型：代码逻辑问题 / 测试用例问题 / 边界条件没处理 / 运行环境问题
4. 修复建议

注意：
如果错误是 EOFError 或 input 读取失败，请明确建议使用 try-except 捕获 EOFError，并在没有输入时使用默认值。
本项目的代码会被自动运行，不能依赖人工在终端输入。
如果 pytest 失败，请优先建议修复业务代码，而不是修改测试用例。
"""
    prompt = _render_prompt_or_fallback(
        "sentry_agent",
        {
            "code": code,
            "error_log": error_log,
            "test_code": test_code or "未提供",
            "test_stdout": test_stdout or "无",
            "test_stderr": test_stderr or "无",
        },
        fallback_prompt,
    )

    if should_use_offline_demo(provider):
        combined_log = "\n".join(
            text for text in [error_log or "", test_stdout or "", test_stderr or ""] if text
        )
        return sentry_demo(combined_log)

    try:
        return ask_llm(
            system_prompt="你是一名错误分析工程师，擅长根据 Python stderr 定位问题并给出修复建议。",
            user_prompt=prompt,
            provider=provider,
        )
    except Exception as error:
        print(f"Sentry Agent 模型调用失败，使用离线演示响应：{error}")
        combined_log = "\n".join(
            text for text in [error_log or "", test_stdout or "", test_stderr or ""] if text
        )
        return sentry_demo(combined_log)


def tester_agent(requirement_or_code, code=None, provider=None):
    """Review code in the old flow, or generate pytest code in the LangGraph flow."""
    if code is not None:
        requirement = requirement_or_code
        fallback_prompt = f"""
请根据用户需求和生成代码，编写 pytest 测试代码。

用户需求：
{requirement}

生成代码：
{code}

测试代码要求：
1. 使用 pytest
2. 测试核心功能
3. 测试正常输入
4. 测试边界情况
5. 测试异常输入
6. 尽量避免复杂依赖
7. 被测代码文件路径是 output/generated_code.py
8. 如果被测代码提供函数，优先用 importlib.util 从 output/generated_code.py 加载模块后测试函数
9. 如果被测代码只是脚本，可以用 subprocess 运行脚本并检查 returncode/stdout
10. 只输出 Python 测试代码，不要使用 Markdown 代码块，不要解释
"""
        prompt = _render_prompt_or_fallback(
            "tester_agent",
            {
                "requirement": requirement,
                "code": code,
            },
            fallback_prompt,
        )

        if should_use_offline_demo(provider):
            return pytest_demo(requirement, code)

        try:
            return ask_llm(
                system_prompt="你是一名 Python 测试工程师，擅长为简单代码编写 pytest 测试。",
                user_prompt=prompt,
                provider=provider,
            )
        except Exception as error:
            print(f"Tester Agent 模型调用失败，使用离线 pytest 演示响应：{error}")
            return pytest_demo(requirement, code)

    generated_code = requirement_or_code
    prompt = f"""
请静态检查下面这段 Python 代码，不要运行代码：

{generated_code}

请用简单清晰的中文输出：
1. 是否有明显语法问题
2. 是否有明显逻辑问题
3. 是否缺少入口函数、主循环或必要的调用
4. 修改建议
5. 检查结论：通过 / 需要修改
"""

    if should_use_offline_demo(provider):
        return tester_demo(generated_code)

    try:
        return ask_llm(
            system_prompt="你是一名 Python 测试工程师，擅长做简单的代码静态检查。",
            user_prompt=prompt,
            provider=provider,
        )
    except Exception as error:
        print(f"Tester Agent 模型调用失败，使用离线演示响应：{error}")
        return tester_demo(generated_code)

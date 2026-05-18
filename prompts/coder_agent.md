{{mode_instruction}}

原始用户需求：
{{requirement}}

原始产品方案：
{{product_result}}

原始代码：
{{code}}

错误日志：
{{error_log}}

pytest 测试代码：
{{test_code}}

pytest stdout：
{{test_stdout}}

pytest stderr：
{{test_stderr}}

Sentry Agent 的分析和修复建议：
{{sentry_result}}

要求：
1. 输出完整 Python 代码
2. 代码简单，适合初学者阅读
3. 不要实现复杂功能
4. 如果是修复场景，必须根据错误修改代码，不要原样返回旧代码
5. 如果错误和 input 或 EOFError 有关，即使原需求提到 input，也必须使用 try-except 捕获 EOFError，并提供默认值，确保代码在没有人工输入时也能运行结束
6. 如果 pytest 失败，请修复业务代码本身，不要修改测试用例来强行通过
7. 只输出 Python 代码，不要使用 Markdown 代码块，不要解释

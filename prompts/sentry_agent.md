下面的 Python 代码运行或 pytest 自动测试失败了。

原始代码：
{{code}}

错误日志 stderr：
{{error_log}}

pytest 测试代码：
{{test_code}}

pytest stdout：
{{test_stdout}}

pytest stderr：
{{test_stderr}}

请用简单清晰的中文输出：
1. 错误摘要
2. 错误原因
3. 判断问题类型：代码逻辑问题 / 测试用例问题 / 边界条件没处理 / 运行环境问题
4. 修复建议

注意：
如果错误是 EOFError 或 input 读取失败，请明确建议使用 try-except 捕获 EOFError，并在没有输入时使用默认值。
本项目的代码会被自动运行，不能依赖人工在终端输入。
如果 pytest 失败，请优先建议修复业务代码，而不是修改测试用例。

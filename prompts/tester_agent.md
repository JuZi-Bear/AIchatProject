请根据用户需求和生成代码，编写 pytest 测试代码。

用户需求：
{{requirement}}

生成代码：
{{code}}

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

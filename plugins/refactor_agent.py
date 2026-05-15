import ast

from plugins.base_plugin import BasePluginAgent


class RefactorAgent(BasePluginAgent):
    name = "Refactor Agent"
    description = "分析最终代码结构，并给出重构和可读性优化建议"
    result_field = "refactor_result"

    def run(self, state):
        code = state.get("code", "")
        result = self.analyze_code(code)
        status = "warning" if "语法问题" in result or "暂时无法" in result else "success"
        summary = "代码重构建议已生成" if status == "success" else "代码需要先处理基础问题"

        state["refactor_result"] = result
        return self.build_result(status=status, summary=summary, detail=result)

    def analyze_code(self, code):
        if not code.strip():
            return "本次流程没有生成代码，暂时无法进行重构分析。"

        suggestions = []
        function_names = []

        try:
            tree = ast.parse(code)
            function_names = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
        except SyntaxError:
            suggestions.append("代码存在语法问题，建议先修复语法错误后再重构。")

        lines = [line.strip() for line in code.splitlines() if line.strip()]
        duplicate_lines = sorted({line for line in lines if lines.count(line) > 1 and not line.startswith("#")})

        if duplicate_lines:
            suggestions.append("发现重复代码，可以考虑提取为函数。")
        else:
            suggestions.append("未发现明显重复代码。")

        if function_names:
            unclear_names = [name for name in function_names if len(name) <= 2 or name in ("foo", "bar", "test")]
            if unclear_names:
                suggestions.append("部分函数命名不够清晰：" + "、".join(unclear_names))
            else:
                suggestions.append("函数命名整体较清晰。")
        else:
            suggestions.append("当前代码没有函数。如果逻辑继续变复杂，可以考虑拆分函数。")

        if len(lines) > 40 and len(function_names) == 0:
            suggestions.append("代码行数较多且没有函数，建议按功能拆分。")
        else:
            suggestions.append("代码规模较小，可读性基本适合演示。")

        optimized_hint = self.build_optimized_hint(function_names)

        return f"""## Refactor Agent 分析结果

### 代码结构

- 代码行数：{len(lines)}
- 函数数量：{len(function_names)}
- 函数列表：{", ".join(function_names) if function_names else "暂无函数"}

### 重构建议

{chr(10).join(f"- {item}" for item in suggestions)}

### 可选优化片段

```python
{optimized_hint}
```
"""

    def build_optimized_hint(self, function_names):
        if function_names:
            return "# 当前已有函数结构，可以继续保持清晰命名和单一职责。"

        return """def main():
    # 将主要流程放在 main 函数中，方便阅读和复用
    print("把原来的脚本逻辑放到这里")


main()"""

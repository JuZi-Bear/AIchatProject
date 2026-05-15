from plugins.base_plugin import BasePluginAgent


class PluginTemplate(BasePluginAgent):
    """Copy this file when creating a new custom plugin."""

    name = "Template Agent"
    description = "插件模板：复制后改成自己的 Agent"
    enabled = False
    result_field = "template_result"

    def run(self, state):
        """Run the plugin and return a standard plugin result."""
        # 1. 读取用户原始需求：
        requirement = state.get("requirement", "")

        # 2. 读取最终生成的代码：
        code = state.get("code", "")

        # 3. 如需调用大模型，可以复用 agents.py 中的 ask_deepseek：
        # from agents import ask_deepseek
        # result = ask_deepseek(
        #     system_prompt="你是一个自定义 AI Agent。",
        #     user_prompt=f"用户需求：{requirement}\n\n代码：{code}",
        # )

        # 4. 也可以先写简单规则，比赛现场更稳定：
        result = f"""模板插件运行成功。

用户需求：
{requirement}

代码长度：
{len(code)} 个字符
"""

        # 5. 将结果写回 state，字段名建议使用 xxx_result：
        state["template_result"] = result

        # 6. 返回统一插件结果。plugin_loader 会写入 state["plugin_results"]：
        return self.build_result(
            status="success",
            summary="模板插件运行成功",
            detail=result,
        )

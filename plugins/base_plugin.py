class BasePluginAgent:
    """Base class for custom AI module plugins."""

    name = "BasePluginAgent"
    description = "自定义 AI 模块基类"
    enabled = True

    def run(self, state):
        """Run the plugin with the final LangGraph state."""
        raise NotImplementedError("插件必须实现 run(state) 方法")

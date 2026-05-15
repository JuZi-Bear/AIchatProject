class BasePluginAgent:
    """Base class for custom AI module plugins."""

    name = "Base Plugin Agent"
    description = "自定义 AI 模块基类"
    enabled = True
    result_field = ""
    allowed_status = {"success", "warning", "failed", "disabled"}

    def build_result(self, status="success", summary="", detail=""):
        """Build one standard plugin result dict."""
        if status not in self.allowed_status:
            status = "warning"

        return {
            "plugin_name": self.name,
            "status": status,
            "summary": summary or "插件已执行",
            "detail": detail or summary or "无详细输出",
        }

    def normalize_result(self, result):
        """Convert old plugin result fields to the standard structure."""
        if not isinstance(result, dict):
            return self.build_result(
                status="warning",
                summary="插件返回值不是标准字典",
                detail=str(result),
            )

        if "plugin_name" in result:
            return self.build_result(
                status=result.get("status", "success"),
                summary=result.get("summary", ""),
                detail=result.get("detail", ""),
            )

        return self.build_result(
            status=result.get("status", "success"),
            summary=result.get("summary") or result.get("description") or self.description,
            detail=result.get("detail") or result.get("content") or "",
        )

    def run(self, state):
        """Run the plugin and return a standard plugin result dict."""
        raise NotImplementedError("插件必须实现 run(state) 方法")

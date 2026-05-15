def _to_int(value, default=0):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _normalize_plugins(value):
    if not value:
        return []

    if isinstance(value, list):
        return [str(item) for item in value if str(item).strip()]

    return [item.strip() for item in str(value).split(",") if item.strip()]


def _build_security_status(state):
    enabled_plugins = _normalize_plugins(state.get("enabled_plugins", []))
    security_result = state.get("security_result", "") or ""
    plugin_results = state.get("plugin_results", []) or []

    for item in plugin_results:
        plugin_name = item.get("plugin_name", item.get("name", ""))
        if plugin_name != "Security Agent":
            continue

        status = item.get("status", "")
        if status == "disabled":
            return "该插件未启用"
        if status == "success":
            return "安全检查通过"
        if status in ("warning", "failed"):
            return item.get("summary", "发现安全风险")

    if not security_result:
        if "Security Agent" in enabled_plugins or "security_agent" in enabled_plugins:
            return "等待安全检查"
        return "该插件未启用"

    if security_result.startswith("未发现") or "安全检查通过" in security_result:
        return "安全检查通过"

    risky_words = ["风险", "危险", "禁止", "失败", "错误"]
    if any(word in security_result for word in risky_words):
        return "发现安全风险"

    return security_result[:120]


def build_run_summary(state):
    """Build one shared summary dict for CLI, Web UI, and reports."""
    state = state or {}

    return {
        "success": bool(state.get("success", False)),
        "retry_count": _to_int(state.get("retry_count", 0)),
        "test_success": bool(state.get("test_success", False)),
        "coverage_percent": _to_int(state.get("coverage_percent", 0)),
        "quality_score": _to_int(state.get("quality_score", 0)),
        "security_status": _build_security_status(state),
        "enabled_plugins": _normalize_plugins(state.get("enabled_plugins", [])),
        "model_provider": state.get("model_provider", "") or "未记录",
        "report_path": state.get("report_path", "") or "未生成",
    }

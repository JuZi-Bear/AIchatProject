from pathlib import Path

import yaml

from plugins.doc_agent import DocAgent
from plugins.refactor_agent import RefactorAgent
from plugins.security_agent import SecurityAgent
from plugins.ui_agent import UIAgent


PROJECT_ROOT = Path(__file__).resolve().parent
CONFIG_FILE = PROJECT_ROOT / "config" / "agents.yaml"

PLUGIN_CLASSES = {
    "doc_agent": DocAgent,
    "security_agent": SecurityAgent,
    "refactor_agent": RefactorAgent,
    "ui_agent": UIAgent,
}


def load_plugin_config():
    """Read plugin config from config/agents.yaml."""
    if not CONFIG_FILE.exists():
        return []

    config = yaml.safe_load(CONFIG_FILE.read_text(encoding="utf-8")) or {}
    return config.get("plugins", [])


def load_enabled_plugins():
    """Create plugin instances from simple name/enabled config."""
    plugins = []

    for item in load_plugin_config():
        if not item.get("enabled", False):
            continue

        plugin_name = item.get("name", "")
        plugin_class = PLUGIN_CLASSES.get(plugin_name)

        if plugin_class is None:
            continue

        plugin = plugin_class()
        plugin.enabled = True
        plugins.append(plugin)

    return plugins


def run_plugins(state):
    """Run all enabled plugins in order and return the updated state."""
    state["plugin_results"] = []

    for item in load_plugin_config():
        plugin_name = item.get("name", "")
        plugin_class = PLUGIN_CLASSES.get(plugin_name)

        if plugin_class is None:
            state["plugin_results"].append(
                {
                    "plugin_name": plugin_name or "Unknown Plugin",
                    "status": "failed",
                    "summary": "插件未登记",
                    "detail": f"plugin_loader.py 中没有找到插件：{plugin_name}",
                }
            )
            continue

        plugin = plugin_class()

        if not item.get("enabled", False):
            state["plugin_results"].append(
                plugin.build_result(
                    status="disabled",
                    summary="该插件未启用",
                    detail="config/agents.yaml 中 enabled=false",
                )
            )
            continue

        plugin.enabled = True

        try:
            result = plugin.run(state)
            state["plugin_results"].append(plugin.normalize_result(result))
        except Exception as error:
            state["plugin_results"].append(
                plugin.build_result(
                    status="failed",
                    summary=f"{plugin.name} 运行失败",
                    detail=f"插件运行失败：{error}",
                )
            )

    return state

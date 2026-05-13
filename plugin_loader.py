from pathlib import Path
from importlib import import_module

import yaml


PROJECT_ROOT = Path(__file__).resolve().parent
DEFAULT_CONFIG_FILE = PROJECT_ROOT / "config" / "agents.yaml"


def load_plugin_config(config_file=DEFAULT_CONFIG_FILE):
    """Read plugin config from config/agents.yaml."""
    if not config_file.exists():
        return []

    config = yaml.safe_load(config_file.read_text(encoding="utf-8")) or {}
    return config.get("plugins", [])


def load_enabled_plugins(config_file=DEFAULT_CONFIG_FILE):
    """Load enabled plugin classes and return plugin instances."""
    plugins = []

    for item in load_plugin_config(config_file):
        if not item.get("enabled", False):
            continue

        module_name = item.get("module", "")
        class_name = item.get("class", "")

        if not module_name or not class_name:
            continue

        module = import_module(module_name)
        plugin_class = getattr(module, class_name)
        plugin = plugin_class()
        plugin.enabled = True
        plugins.append(plugin)

    return plugins


def run_enabled_plugins(state):
    """Run all enabled plugins and collect their results."""
    results = []

    for plugin in load_enabled_plugins():
        try:
            results.append(plugin.run(state))
        except Exception as error:
            results.append(
                {
                    "name": getattr(plugin, "name", plugin.__class__.__name__),
                    "description": getattr(plugin, "description", ""),
                    "status": "error",
                    "content": f"插件运行失败：{error}",
                }
            )

    return results

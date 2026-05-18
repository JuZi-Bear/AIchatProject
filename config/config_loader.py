from pathlib import Path

import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SETTINGS_FILE = PROJECT_ROOT / "config" / "settings.yaml"

DEFAULT_SETTINGS = {
    "max_retry_count": 3,
    "offline_mode": False,
    "require_human_approval": True,
    "default_model_provider": "deepseek",
    "demo_mode": True,
    "save_reports": True,
    "save_runs": True,
    "runner_mode": "python",
    "code_agent": {
        "enabled": True,
        "allowed_paths": [
            "src",
            "output",
            "docs",
            "frontend-vue/src",
            "backend-java/src",
            "utils",
            "services",
            "config",
            "workflow_templates",
            "agent_registry",
            "plugins",
            "tests",
        ],
        "blocked_paths": [
            ".git",
            ".venv",
            "node_modules",
            "frontend-vue/node_modules",
            "frontend-vue/dist",
            "backend-java/target",
            "runner-cpp/build",
            ".env",
        ],
        "audit_log_path": "output/code_agent_audit.jsonl",
        "max_read_chars": 200000,
    },
}


def load_yaml(path):
    """Load a YAML file and return an empty dict when it does not exist."""
    yaml_path = Path(path)
    if not yaml_path.is_absolute():
        yaml_path = PROJECT_ROOT / yaml_path

    if not yaml_path.exists():
        return {}

    return yaml.safe_load(yaml_path.read_text(encoding="utf-8")) or {}


def load_settings():
    """Load project settings with simple defaults."""
    settings = DEFAULT_SETTINGS.copy()
    settings.update(load_yaml(SETTINGS_FILE))
    return settings


def get_setting(key, default=None):
    """Read one setting value from config/settings.yaml."""
    return load_settings().get(key, default)

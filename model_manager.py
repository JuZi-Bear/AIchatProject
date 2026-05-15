import os
from pathlib import Path

import yaml
from dotenv import load_dotenv
from openai import OpenAI

from config.config_loader import get_setting


PROJECT_ROOT = Path(__file__).resolve().parent
MODELS_CONFIG_FILE = PROJECT_ROOT / "config" / "models.yaml"
DEFAULT_PROVIDER = "deepseek"

load_dotenv(PROJECT_ROOT / ".env")

DEFAULT_MODELS = [
    {
        "name": "DeepSeek",
        "provider": "deepseek",
        "model": "deepseek-chat",
        "base_url": "https://api.deepseek.com",
        "env_key": "DEEPSEEK_API_KEY",
        "enabled": True,
    },
    {
        "name": "Qwen",
        "provider": "qwen",
        "model": "qwen-plus",
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "env_key": "QWEN_API_KEY",
        "enabled": False,
    },
    {
        "name": "GLM",
        "provider": "zhipu",
        "model": "glm-4-flash",
        "base_url": "https://open.bigmodel.cn/api/paas/v4",
        "env_key": "GLM_API_KEY",
        "enabled": False,
    },
]


def get_config(name, default=""):
    return os.getenv(name, default).strip()


def is_offline_mode():
    env_value = get_config("OFFLINE_MODE", "")
    if env_value:
        return env_value.lower() in ("1", "true", "yes", "on")

    return bool(get_setting("offline_mode", False))


def load_models_config():
    """Load model configs from config/models.yaml."""
    if not MODELS_CONFIG_FILE.exists():
        return {"models": DEFAULT_MODELS}

    config = yaml.safe_load(MODELS_CONFIG_FILE.read_text(encoding="utf-8")) or {}
    models = config.get("models") or DEFAULT_MODELS
    return {"models": models}


def get_available_models():
    """Return all configured models so the UI can show every provider option."""
    return load_models_config().get("models", [])


def get_default_model():
    """Return the default model selected by DEFAULT_MODEL_PROVIDER."""
    provider = (
        get_config("DEFAULT_MODEL_PROVIDER", "")
        or get_setting("default_model_provider", DEFAULT_PROVIDER)
        or DEFAULT_PROVIDER
    )
    return get_current_model_info(provider)


def get_current_model_info(provider=None):
    """Return one model config by provider, falling back to the default model."""
    models = get_available_models()
    selected_provider = (
        provider
        or get_config("DEFAULT_MODEL_PROVIDER", "")
        or get_setting("default_model_provider", DEFAULT_PROVIDER)
        or DEFAULT_PROVIDER
    )

    for model_info in models:
        if model_info.get("provider") == selected_provider:
            return model_info

    for model_info in models:
        if model_info.get("provider") == DEFAULT_PROVIDER:
            return model_info

    if models:
        return models[0]

    return DEFAULT_MODELS[0]


def get_llm_client(provider=None):
    """Create an OpenAI-compatible client for the selected provider."""
    model_info = get_current_model_info(provider)
    env_key = model_info.get("env_key", "")
    api_key = get_config(env_key)

    if not api_key:
        raise RuntimeError(
            f"未检测到 {env_key}。请在 .env 或系统环境变量中配置该 API Key，"
            "或将 OFFLINE_MODE 设置为 true 使用离线演示模式。"
        )

    return OpenAI(
        api_key=api_key,
        base_url=model_info.get("base_url", ""),
    )

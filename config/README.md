# config

## 目录作用

`config/` 是共享配置目录，服务于 v1.0 Python Direct 演示和 v2.0 Python Agent Engine。Java/MySQL 模式会保存平台配置，但 Python 配置文件仍是核心兜底来源。

## 核心文件

- `models.yaml`：模型提供商、模型名、base_url、env_key 等配置。
- `agents.yaml`：插件和 Agent 启用配置。
- `settings.yaml`：运行设置，例如 `runner_mode`。
- `config_loader.py`：配置加载逻辑。
- `__init__.py`：配置包入口。

## 不能随便修改

- 不要提交真实 API Key。
- 不要删除默认模型或插件配置。
- 不要把 `runner_mode` 默认改成未验证的 `cpp`。
- 不要让 v2 Java 配置完全取代 Python yaml 兜底配置。

## 轨道归属

shared-core。

## 当前开发状态

stable。

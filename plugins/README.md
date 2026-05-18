# plugins

## 目录作用

`plugins/` 是共享插件系统目录，服务于 v1.0 Streamlit 演示和 v2.0 平台化展示。当前包含文档、安全、重构和 UI 等插件 Agent。

## 核心文件

- `base_plugin.py`：插件基类和统一接口。
- `doc_agent.py`：文档插件。
- `security_agent.py`：安全检查插件。
- `refactor_agent.py`：重构建议插件。
- `ui_agent.py`：UI 建议插件。
- `plugin_template.py`：新增插件模板。
- `__init__.py`：插件包入口。

## 不能随便修改

- 不要删除现有插件名称或输出字段。
- 不要破坏 `plugin_loader.py` 对插件的加载方式。
- 不要让插件直接修改核心 LangGraph 流程。
- 不要在插件中写死模型 Key 或外部服务地址。

## 轨道归属

shared-core。

## 当前开发状态

stable。

# 插件开发指南

本文档说明如何基于现有插件系统创建新的 AI 进程模块，例如 UI Agent、Deploy Agent、Database Agent。

## 1. 插件系统简介

插件系统用于在 LangGraph 主流程结束前运行额外的自定义 Agent。

当前主流程是：

```text
用户需求 → Product Agent → Coder Agent → Tester Agent → Runner → Sentry 修复循环 → Plugins
```

插件会接收最终的 `state`，读取其中的需求、代码、运行结果等信息，然后返回统一的插件结果结构。`plugin_loader.py` 会把这些结果写入 `state["plugin_results"]`。

统一结果结构：

```python
{
    "plugin_name": "Doc Agent",
    "status": "success",
    "summary": "README 风格说明已生成",
    "detail": "完整插件输出内容",
}
```

`status` 只能使用：

- `success`：执行成功。
- `warning`：执行完成，但有风险或建议。
- `failed`：插件执行失败。
- `disabled`：插件未启用。

## 2. 插件目录结构

插件相关文件：

```text
plugins/
  __init__.py
  base_plugin.py
  plugin_template.py
  doc_agent.py
  security_agent.py
  refactor_agent.py
  ui_agent.py

config/
  agents.yaml

plugin_loader.py
```

说明：

- `plugins/base_plugin.py`：所有插件的基类。
- `plugins/plugin_template.py`：新插件开发模板。
- `config/agents.yaml`：控制插件是否启用。
- `plugin_loader.py`：根据配置加载并执行插件。

## 3. 使用模板创建新插件

复制模板文件：

```powershell
copy plugins\plugin_template.py plugins\deploy_agent.py
```

然后修改类名、插件名称和结果字段。

示例：

```python
from plugins.base_plugin import BasePluginAgent


class DeployAgent(BasePluginAgent):
    name = "Deploy Agent"
    description = "根据最终代码给出部署建议"
    enabled = True
    result_field = "deploy_result"

    def run(self, state):
        requirement = state.get("requirement", "")
        code = state.get("code", "")

        result = f"部署建议：可以先使用本地 Python 环境运行。需求：{requirement}"

        # 可选：保留 xxx_result 字段，方便旧逻辑或固定报告区域读取。
        state["deploy_result"] = result

        # 必须：返回统一插件结果。plugin_loader 会统一写入 state["plugin_results"]。
        return self.build_result(
            status="success",
            summary="部署建议已生成",
            detail=result,
        )
```

## 4. 在 plugin_loader.py 中登记插件

在 `plugin_loader.py` 中导入新插件：

```python
from plugins.deploy_agent import DeployAgent
```

然后加入 `PLUGIN_CLASSES`：

```python
PLUGIN_CLASSES = {
    "doc_agent": DocAgent,
    "security_agent": SecurityAgent,
    "refactor_agent": RefactorAgent,
    "ui_agent": UIAgent,
    "deploy_agent": DeployAgent,
}
```

## 5. 在 config/agents.yaml 中启用插件

加入插件配置：

```yaml
plugins:
  - name: deploy_agent
    enabled: true
```

如果要关闭插件：

```yaml
plugins:
  - name: deploy_agent
    enabled: false
```

## 6. 在 Web UI 中查看插件结果

启动 Web UI：

```powershell
python -m streamlit run webui.py
```

在左侧栏“自定义 AI 模块配置”中可以勾选启用或关闭已登记的插件。

运行后，在“自定义 AI 模块”和“插件执行结果”区域查看插件输出。Web UI 会优先读取 `state["plugin_results"]`，再兼容读取旧的 `doc_result`、`security_result`、`refactor_result`、`ui_result` 等字段。

## 7. 插件 state 字段说明

常用输入字段：

- `state["requirement"]`：用户原始需求。
- `state["product_result"]`：Product Agent 的需求分析结果。
- `state["code"]`：Coder Agent 最终生成的 Python 代码。
- `state["tester_result"]`：Tester Agent 的静态检查结果。
- `state["stdout"]`：代码运行输出。
- `state["error_log"]`：代码运行错误日志。
- `state["sentry_result"]`：Sentry Agent 的错误分析结果。
- `state["retry_count"]`：自动修复次数。
- `state["success"]`：最终是否运行成功。

常用输出字段：

- `state["doc_result"]`：文档插件输出。
- `state["security_result"]`：安全检查插件输出。
- `state["refactor_result"]`：重构建议插件输出。
- `state["ui_result"]`：UI 设计建议插件输出。
- `state["plugin_results"]`：统一插件结果列表。

`plugin_results` 中每个元素都应包含：

- `plugin_name`：插件名称。
- `status`：`success` / `warning` / `failed` / `disabled`。
- `summary`：一句话摘要，适合 Web UI 卡片展示。
- `detail`：完整插件输出，适合报告和开发模式展示。

## 8. 开发建议

- 插件逻辑尽量简单，先用规则判断，比赛现场更稳定。
- 每个插件只负责一件事。
- 输出字段使用 `xxx_result` 命名。
- `run(state)` 返回统一结构，不要自己追加 `state["plugin_results"]`。
- 插件运行失败时不要影响主流程。
- 新插件写完后先运行：

```powershell
python -m py_compile plugins\your_agent.py
python graph_demo.py
```

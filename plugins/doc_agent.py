from plugins.base_plugin import BasePluginAgent


class DocAgent(BasePluginAgent):
    name = "DocAgent"
    description = "根据最终代码生成项目说明文档"

    def run(self, state):
        code = state.get("code", "").strip()
        stdout = state.get("stdout", "").strip()
        success = state.get("success", False)

        if not code:
            content = "本次流程没有生成代码，暂时无法生成项目说明文档。"
        else:
            status_text = "运行成功" if success else "运行失败"
            content = f"""# 生成代码说明

## 项目目标

{state.get("requirement", "无需求信息")}

## 运行状态

{status_text}

## 使用方式

生成代码已保存到 `output/generated_code.py`，可以使用 Python 直接运行。

## 运行输出

```text
{stdout or "无 stdout"}
```
"""

        return {
            "name": self.name,
            "description": self.description,
            "status": "success",
            "content": content,
        }

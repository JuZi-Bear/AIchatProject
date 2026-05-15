from plugins.base_plugin import BasePluginAgent


class UIAgent(BasePluginAgent):
    name = "UI Agent"
    description = "根据用户需求和最终代码生成 UI 设计建议"
    result_field = "ui_result"

    def run(self, state):
        requirement = state.get("requirement", "")
        code = state.get("code", "")
        result = self.build_ui_suggestion(requirement, code)

        state["ui_result"] = result
        return self.build_result(
            status="success",
            summary="UI 设计建议已生成",
            detail=result,
        )

    def build_ui_suggestion(self, requirement, code):
        output_hint = "运行结果输出区"
        if "input(" in code:
            input_hint = "用户输入表单"
        else:
            input_hint = "演示案例选择或开始运行按钮"

        return f"""## UI Agent 设计建议

### 页面目标

围绕用户需求展示一个简单、清晰、适合比赛演示的界面。

用户需求：
{requirement or "无需求信息"}

### 推荐页面布局

- 顶部：项目标题和一句简短说明
- 中部：{input_hint}
- 右侧或下方：{output_hint}
- 底部：运行状态、错误日志和操作提示

### 核心组件

- 标题组件：展示当前程序名称
- 输入组件：用于录入用户需要的数据
- 运行按钮：触发代码运行或演示流程
- 结果面板：展示 stdout、统计结果或生成内容
- 错误提示：展示 stderr 或修复建议

### 交互说明

- 用户先填写输入或选择演示案例
- 点击运行按钮后显示加载状态
- 运行成功时展示绿色成功状态和结果
- 运行失败时展示红色错误状态，并给出修复建议

### 可选优化

如果后续要做成完整 Web 应用，可以优先使用 Streamlit 实现，保持页面结构简单，方便现场讲解。
"""

from plugins.base_plugin import BasePluginAgent


class SecurityAgent(BasePluginAgent):
    name = "Security Agent"
    description = "检查生成代码中是否包含危险操作"
    result_field = "security_result"

    def run(self, state):
        code = state.get("code", "")
        danger_keywords = [
            "os.remove",
            "shutil.rmtree",
            "subprocess",
            "eval",
            "exec",
        ]
        problems = [keyword for keyword in danger_keywords if keyword in code]

        if problems:
            content = "发现危险操作：\n" + "\n".join(f"- {problem}" for problem in problems)
            status = "warning"
            summary = "发现危险操作：" + "、".join(problems)
        else:
            content = "未发现 os.remove、shutil.rmtree、subprocess、eval、exec 等危险操作。"
            status = "success"
            summary = "安全检查通过"

        state["security_result"] = content
        return self.build_result(status=status, summary=summary, detail=content)

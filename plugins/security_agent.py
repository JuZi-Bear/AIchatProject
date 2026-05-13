from plugins.base_plugin import BasePluginAgent
from utils.code_runner import check_code_safety


class SecurityAgent(BasePluginAgent):
    name = "SecurityAgent"
    description = "检查生成代码中是否包含危险操作"

    def run(self, state):
        code = state.get("code", "")
        problems = check_code_safety(code)

        if problems:
            content = "发现危险操作：\n" + "\n".join(f"- {problem}" for problem in problems)
            status = "warning"
        else:
            content = "未发现 os.remove、shutil.rmtree、subprocess、eval、exec 等危险操作。"
            status = "success"

        return {
            "name": self.name,
            "description": self.description,
            "status": status,
            "content": content,
        }

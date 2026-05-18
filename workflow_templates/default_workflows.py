from dataclasses import asdict, dataclass
from pathlib import Path


TEMPLATE_MD_DIR = Path(__file__).resolve().parent / "template_md"


@dataclass
class WorkflowTemplate:
    key: str
    name: str
    description: str
    agent_sequence: list[str]
    stage_sequence: list[str]
    enabled: bool = True
    version: str = "1.0"
    md_path: str = ""

    def to_dict(self, include_markdown=False) -> dict:
        data = asdict(self)

        if include_markdown:
            data["markdown"] = load_template_markdown(self.md_path)

        return data


def load_template_markdown(md_path: str) -> str:
    if not md_path:
        return ""

    template_path = Path(md_path)
    if not template_path.is_absolute():
        template_path = Path.cwd() / template_path

    try:
        return template_path.read_text(encoding="utf-8")
    except OSError:
        return ""


def get_default_workflows(include_markdown=False) -> list[dict]:
    templates = [
        WorkflowTemplate(
            key="simple_demo",
            name="简单演示流程",
            description="适合快速展示需求拆解、代码生成、测试和报告结果。",
            agent_sequence=["product", "coder", "tester", "runner", "quality", "report"],
            stage_sequence=["分析", "生成", "测试", "执行", "评分", "报告"],
            md_path=str(TEMPLATE_MD_DIR / "simple_demo.md"),
        ),
        WorkflowTemplate(
            key="full_agent_flow",
            name="完整多 Agent 流程",
            description="覆盖 Product、Coder、Tester、Runner、Sentry、Plugins、Quality 和 Report 的完整平台流程。",
            agent_sequence=["product", "coder", "tester", "runner", "sentry", "coder", "plugins", "quality", "report"],
            stage_sequence=["分析", "生成", "测试", "执行", "修复", "插件", "评分", "报告"],
            md_path=str(TEMPLATE_MD_DIR / "full_agent_flow.md"),
        ),
        WorkflowTemplate(
            key="repair_flow",
            name="自动修复重点流程",
            description="突出测试失败、错误分析、自动修复和再次验证，适合比赛答辩演示。",
            agent_sequence=["product", "coder", "tester", "runner", "sentry", "coder", "tester", "runner", "quality", "report"],
            stage_sequence=["分析", "生成", "测试", "执行", "修复", "再测试", "再执行", "评分", "报告"],
            md_path=str(TEMPLATE_MD_DIR / "repair_flow.md"),
        ),
        WorkflowTemplate(
            key="code_agent_file_ops",
            name="CodeAgent 文件操作流程",
            description="演示简化 CodeAgent 节点读取、写入和列出项目文件，并输出事件供 SSE 和回放使用。",
            agent_sequence=["code_agent"],
            stage_sequence=["文件操作"],
            md_path=str(TEMPLATE_MD_DIR / "code_agent_file_ops.md"),
        ),
    ]

    return [template.to_dict(include_markdown=include_markdown) for template in templates]

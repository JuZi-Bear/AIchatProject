from agent_registry.agent_meta import AgentMeta
from agent_registry.registry import AgentRegistry


def get_default_agent_registry():
    registry = AgentRegistry()

    registry.register(AgentMeta(
        key="product",
        name="Product Agent",
        role="需求分析智能体",
        description="负责将用户自然语言需求拆解为功能需求和技术需求。",
        input_fields=["requirement"],
        output_fields=["product_result"],
        stage="analysis",
    ))
    registry.register(AgentMeta(
        key="coder",
        name="Coder Agent",
        role="代码生成与修复智能体",
        description="根据产品方案生成 Python 代码，并在失败后结合错误日志进行修复。",
        input_fields=["product_result", "code", "error_log", "test_stdout", "test_stderr"],
        output_fields=["code"],
        stage="implementation",
    ))
    registry.register(AgentMeta(
        key="tester",
        name="Tester Agent",
        role="测试生成智能体",
        description="根据用户需求和生成代码编写 pytest 测试，并触发覆盖率验证。",
        input_fields=["requirement", "code"],
        output_fields=["test_code", "tester_result", "test_success", "coverage_percent"],
        stage="testing",
    ))
    registry.register(AgentMeta(
        key="runner",
        name="Runner",
        role="代码执行器",
        description="执行生成代码，捕获 stdout、stderr、returncode 和 Runner 模式。",
        input_fields=["code", "approved"],
        output_fields=["stdout", "error_log", "success", "runner_mode"],
        stage="execution",
    ))
    registry.register(AgentMeta(
        key="code_agent",
        name="CodeAgent",
        role="简化代码执行模块",
        description="提供 read_file、write_file、list_files 三类受控项目文件操作，并输出可回放事件。",
        input_fields=["operation", "filePath", "content"],
        output_fields=["operation_summary", "events"],
        stage="code_ops",
    ))
    registry.register(AgentMeta(
        key="sentry",
        name="Sentry Agent",
        role="错误分析智能体",
        description="分析 Runner 或 pytest 失败原因，并给出修复建议。",
        input_fields=["code", "error_log", "test_code", "test_stdout", "test_stderr"],
        output_fields=["sentry_result", "retry_count"],
        stage="repair",
    ))
    registry.register(AgentMeta(
        key="plugins",
        name="Plugin Executor",
        role="插件执行器",
        description="统一执行 Doc、Security、Refactor、UI 等插件 Agent。",
        input_fields=["state", "enabled_plugins"],
        output_fields=["plugin_results", "doc_result", "security_result", "refactor_result", "ui_result"],
        stage="extension",
    ))
    registry.register(AgentMeta(
        key="quality",
        name="Quality Evaluator",
        role="质量评分器",
        description="根据运行成功、pytest、覆盖率、安全检查和修复次数生成质量评分。",
        input_fields=["success", "test_success", "coverage_percent", "security_result", "retry_count"],
        output_fields=["quality_score", "quality_summary"],
        stage="quality",
    ))
    registry.register(AgentMeta(
        key="report",
        name="Report Generator",
        role="报告生成器",
        description="汇总工作流结果并生成 Markdown 报告。",
        input_fields=["state", "run_summary", "plugin_results"],
        output_fields=["report_path"],
        stage="report",
    ))

    return registry

import warnings

from langchain_core._api.deprecation import LangChainPendingDeprecationWarning

warnings.filterwarnings("ignore", category=LangChainPendingDeprecationWarning)

from langgraph.graph import END, START, StateGraph

from agents import coder_agent, product_agent, sentry_agent, tester_agent
from config.config_loader import get_setting
from core.quality_evaluator import evaluate_quality
from core.state import AgentState
from model_manager import get_current_model_info
from plugin_loader import run_plugins
from utils.code_runner import run_code, save_code
from utils.test_runner import run_tests_with_coverage, save_test_code
from utils.workflow_event_builder import append_workflow_event_from_parts


def _append_event(state, event_type, event_text, agent=None, status=None, message="", detail=None):
    return append_workflow_event_from_parts(
        state,
        event_type,
        event_text,
        agent=agent,
        status=status,
        message=message,
        detail=detail,
    )


def _error_detail(error):
    return {
        "error_type": error.__class__.__name__,
        "error": str(error),
    }


def product_node(state):
    _append_event(state, "AGENT_STARTED", "Product Agent 开始执行", agent="product", status="RUNNING", message="正在拆解用户需求")
    try:
        model_info = get_current_model_info(state.get("model_provider"))
        state["model_provider"] = model_info.get("provider", "")
        state["model_name"] = model_info.get("model", "")
        state["model_base_url"] = model_info.get("base_url", "")
        state["product_result"] = product_agent(
            state["requirement"],
            provider=state["model_provider"],
        )
        _append_event(
            state,
            "AGENT_FINISHED",
            "Product Agent 完成需求拆解",
            agent="product",
            status="SUCCESS",
            message="需求拆解完成",
            detail={"model_provider": state.get("model_provider", "")},
        )
    except Exception as error:
        _append_event(
            state,
            "AGENT_FAILED",
            "Product Agent 执行失败",
            agent="product",
            status="FAILED",
            message=str(error),
            detail=_error_detail(error),
        )
        raise
    return state


def coder_node(state):
    has_test_result = bool(state.get("test_stdout") or state.get("test_stderr"))
    test_failed = has_test_result and not state.get("test_success", False)
    needs_repair = bool(state.get("error_log")) or test_failed
    message = "正在修复代码" if state.get("code") and needs_repair else "正在生成代码"
    _append_event(state, "AGENT_STARTED", "Coder Agent 开始生成或修复代码", agent="coder", status="RUNNING", message=message)

    try:
        if state.get("code") and needs_repair:
            state["code"] = coder_agent(
                state["product_result"],
                code=state["code"],
                error_log=state["error_log"],
                sentry_result=state["sentry_result"],
                requirement=state["requirement"],
                test_code=state.get("test_code", ""),
                test_stdout=state.get("test_stdout", ""),
                test_stderr=state.get("test_stderr", ""),
                provider=state.get("model_provider"),
            )
        else:
            state["code"] = coder_agent(
                state["product_result"],
                provider=state.get("model_provider"),
            )

        _append_event(
            state,
            "AGENT_FINISHED",
            "Coder Agent 完成代码输出",
            agent="coder",
            status="SUCCESS",
            message="代码输出完成",
            detail={"repair": bool(needs_repair), "retry_count": state.get("retry_count", 0)},
        )
    except Exception as error:
        _append_event(
            state,
            "AGENT_FAILED",
            "Coder Agent 执行失败",
            agent="coder",
            status="FAILED",
            message=str(error),
            detail=_error_detail(error),
        )
        raise

    return state


def tester_node(state):
    _append_event(state, "TEST_STARTED", "Tester Agent 开始生成并运行测试", agent="tester", status="RUNNING", message="正在生成 pytest 并执行覆盖率测试")
    try:
        test_code = tester_agent(
            state["requirement"],
            state["code"],
            provider=state.get("model_provider"),
        )
        save_code(state["code"])
        save_test_code(test_code)
        test_result = run_tests_with_coverage()

        state["test_code"] = test_code
        state["test_stdout"] = test_result["test_stdout"]
        state["test_stderr"] = test_result["test_stderr"]
        state["test_success"] = test_result["returncode"] == 0
        state["coverage_stdout"] = test_result["coverage_stdout"]
        state["coverage_percent"] = test_result["coverage_percent"]

        if state["test_success"]:
            state["tester_result"] = "Tester Agent 已生成 pytest 测试代码，自动测试通过。"
        else:
            state["tester_result"] = "Tester Agent 已生成 pytest 测试代码，自动测试未通过，需要进入修复流程。"

        _append_event(
            state,
            "TEST_FINISHED",
            "Tester Agent 测试完成",
            agent="tester",
            status="SUCCESS" if state["test_success"] else "FAILED",
            message=state["tester_result"],
            detail={
                "test_success": state["test_success"],
                "coverage_percent": state.get("coverage_percent", 0),
            },
        )
    except Exception as error:
        _append_event(
            state,
            "AGENT_FAILED",
            "Tester Agent 执行失败",
            agent="tester",
            status="FAILED",
            message=str(error),
            detail=_error_detail(error),
        )
        raise

    return state


def approval_node(state):
    if not state.get("require_human_approval", False):
        state["approved"] = True
        state["approval_message"] = "未启用人工审批，系统自动通过。"
        return state

    if state.get("approved", False):
        if not state.get("approval_message"):
            state["approval_message"] = "人工审批通过，允许运行 AI 生成代码。"
        return state

    if state.get("approval_message"):
        state["approved"] = False
        state["success"] = False
        state["error_log"] = "用户拒绝执行 AI 生成代码"
        return state

    answer = input("是否允许运行 AI 生成的代码？y/n：").strip().lower()

    if answer == "y":
        state["approved"] = True
        state["approval_message"] = "人工审批通过，允许运行 AI 生成代码。"
    else:
        state["approved"] = False
        state["success"] = False
        state["error_log"] = "用户拒绝执行 AI 生成代码"
        state["approval_message"] = "人工审批未通过，已停止执行 Runner。"

    return state


def sentry_node(state):
    _append_event(state, "REPAIR_STARTED", "Sentry Agent 开始分析错误", agent="sentry", status="RUNNING", message="正在分析 Runner 或 pytest 失败原因")
    try:
        state["sentry_result"] = sentry_agent(
            state["code"],
            state["error_log"],
            test_code=state.get("test_code", ""),
            test_stdout=state.get("test_stdout", ""),
            test_stderr=state.get("test_stderr", ""),
            provider=state.get("model_provider"),
        )
        state["retry_count"] = state["retry_count"] + 1
        _append_event(
            state,
            "REPAIR_FINISHED",
            "Sentry Agent 完成错误分析",
            agent="sentry",
            status="SUCCESS",
            message="错误分析完成，准备进入修复循环",
            detail={"retry_count": state.get("retry_count", 0)},
        )
    except Exception as error:
        _append_event(
            state,
            "AGENT_FAILED",
            "Sentry Agent 执行失败",
            agent="sentry",
            status="FAILED",
            message=str(error),
            detail=_error_detail(error),
        )
        raise
    return state


def runner_node(state):
    _append_event(state, "RUNNER_STARTED", "Runner 开始执行代码", agent="runner", status="RUNNING", message="正在运行 AI 生成代码")
    if not state.get("approved", True):
        state["stdout"] = ""
        state["error_log"] = "用户拒绝执行 AI 生成代码"
        state["success"] = False
        state["runner_mode"] = get_setting("runner_mode", "python")
        state["runner_warning"] = "人工审批未通过，Runner 未执行"
        _append_event(
            state,
            "RUNNER_FINISHED",
            "Runner 执行完成",
            agent="runner",
            status="FAILED",
            message=state["runner_warning"],
            detail={"approved": False},
        )
        return state

    try:
        save_code(state["code"])
        run_result = run_code()
        state["stdout"] = run_result["stdout"]
        state["error_log"] = run_result["stderr"]
        state["success"] = run_result["returncode"] == 0
        state["runner_mode"] = run_result.get("runner_mode", get_setting("runner_mode", "python"))
        state["runner_warning"] = run_result.get("runner_warning", "")
        _append_event(
            state,
            "RUNNER_FINISHED",
            "Runner 执行完成",
            agent="runner",
            status="SUCCESS" if state["success"] else "FAILED",
            message="代码执行成功" if state["success"] else "代码执行失败",
            detail={
                "returncode": run_result.get("returncode"),
                "runner_mode": state.get("runner_mode", "python"),
                "runner_warning": state.get("runner_warning", ""),
            },
        )
    except Exception as error:
        _append_event(
            state,
            "AGENT_FAILED",
            "Runner 执行失败",
            agent="runner",
            status="FAILED",
            message=str(error),
            detail=_error_detail(error),
        )
        raise
    return state


def plugins_node(state):
    state["success"] = bool(
        state.get("approved", True)
        and state.get("success", False)
        and state.get("test_success", False)
    )
    return run_plugins(state)


def quality_node(state):
    try:
        state = evaluate_quality(state)
        _append_event(
            state,
            "QUALITY_EVALUATED",
            "质量评分完成",
            agent="quality",
            status="SUCCESS",
            message="质量评分已生成",
            detail={
                "quality_score": state.get("quality_score", 0),
                "coverage_percent": state.get("coverage_percent", 0),
            },
        )
        return state
    except Exception as error:
        _append_event(
            state,
            "AGENT_FAILED",
            "Quality 节点执行失败",
            agent="quality",
            status="FAILED",
            message=str(error),
            detail=_error_detail(error),
        )
        raise


def report_node(state):
    _append_event(
        state,
        "REPORT_GENERATED",
        "报告生成完成",
        agent="report",
        status="SUCCESS",
        message="报告节点执行完成，等待服务层保存 Markdown 报告",
    )
    return state


def should_continue(state):
    if not state.get("approved", True):
        return "plugins"

    if state["success"] and state.get("test_success", False):
        return "plugins"

    max_retry_count = state.get("max_retry_count", get_setting("max_retry_count"))

    if state["retry_count"] >= max_retry_count:
        return "plugins"

    return "repair"


def should_run_code(state):
    if state.get("approved", False):
        return "runner"

    return "plugins"


def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("product_node", product_node)
    graph.add_node("coder_node", coder_node)
    graph.add_node("tester_node", tester_node)
    graph.add_node("approval_node", approval_node)
    graph.add_node("sentry_node", sentry_node)
    graph.add_node("runner_node", runner_node)
    graph.add_node("plugins_node", plugins_node)
    graph.add_node("quality_node", quality_node)
    graph.add_node("report_node", report_node)

    graph.add_edge(START, "product_node")
    graph.add_edge("product_node", "coder_node")
    graph.add_edge("coder_node", "tester_node")
    graph.add_edge("tester_node", "approval_node")
    graph.add_conditional_edges(
        "approval_node",
        should_run_code,
        {
            "runner": "runner_node",
            "plugins": "plugins_node",
        },
    )
    graph.add_conditional_edges(
        "runner_node",
        should_continue,
        {
            "plugins": "plugins_node",
            "repair": "sentry_node",
        },
    )
    graph.add_edge("sentry_node", "coder_node")
    graph.add_edge("plugins_node", "quality_node")
    graph.add_edge("quality_node", "report_node")
    graph.add_edge("report_node", END)

    return graph.compile()


def create_initial_state(
    requirement,
    max_retry_count=None,
    require_human_approval=None,
    approved=None,
    approval_message="",
    model_provider=None,
):
    if max_retry_count is None:
        max_retry_count = get_setting("max_retry_count")

    if require_human_approval is None:
        require_human_approval = get_setting("require_human_approval", True)

    if approved is None:
        approved = not require_human_approval

    if not model_provider:
        model_provider = get_setting("default_model_provider", "deepseek")

    model_info = get_current_model_info(model_provider)
    return {
        "requirement": requirement,
        "model_provider": model_info.get("provider", ""),
        "model_name": model_info.get("model", ""),
        "model_base_url": model_info.get("base_url", ""),
        "product_result": "",
        "code": "",
        "tester_result": "",
        "test_code": "",
        "test_stdout": "",
        "test_stderr": "",
        "test_success": False,
        "coverage_stdout": "",
        "coverage_percent": 0,
        "stdout": "",
        "error_log": "",
        "runner_mode": get_setting("runner_mode", "python"),
        "runner_warning": "",
        "sentry_result": "",
        "doc_result": "",
        "security_result": "",
        "refactor_result": "",
        "ui_result": "",
        "plugin_results": [],
        "enabled_plugins": [],
        "retry_count": 0,
        "max_retry_count": int(max_retry_count),
        "approved": bool(approved),
        "approval_message": approval_message,
        "require_human_approval": bool(require_human_approval),
        "success": False,
        "quality_score": 0,
        "quality_summary": "",
        "run_id": "",
        "report_path": "",
        "workflow_events": [],
    }


def run_graph_demo(
    requirement,
    progress_callback=None,
    max_retry_count=None,
    require_human_approval=None,
    approved=None,
    approval_message="",
    model_provider=None,
):
    app = build_graph()
    state = create_initial_state(
        requirement,
        max_retry_count=max_retry_count,
        require_human_approval=require_human_approval,
        approved=approved,
        approval_message=approval_message,
        model_provider=model_provider,
    )
    _append_event(
        state,
        "WORKFLOW_STARTED",
        "工作流开始执行",
        agent="workflow",
        status="RUNNING",
        message="LangGraph 工作流已启动",
        detail={"model_provider": state.get("model_provider", "")},
    )

    if progress_callback:
        result = state
        for event in app.stream(state):
            for node_name, node_state in event.items():
                result = node_state
                progress_callback(node_name, result)
    else:
        result = app.invoke(state)

    _append_event(
        result,
        "WORKFLOW_FINISHED",
        "工作流执行完成",
        agent="workflow",
        status="SUCCESS" if result.get("success") and result.get("test_success") else "FAILED",
        message="LangGraph 工作流已完成",
        detail={
            "success": bool(result.get("success", False)),
            "test_success": bool(result.get("test_success", False)),
            "retry_count": result.get("retry_count", 0),
        },
    )
    return result

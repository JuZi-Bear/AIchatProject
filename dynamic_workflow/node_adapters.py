from __future__ import annotations

from typing import Any, Callable

from core.workflow import (
    coder_node,
    plugins_node,
    product_node,
    quality_node,
    report_node,
    runner_node,
    sentry_node,
    tester_node,
)
from dynamic_workflow.template_schema import DynamicWorkflowNode, as_string
from utils.simple_code_agent import execute_code_agent
from utils.workflow_event_builder import append_workflow_event_from_parts


REAL_AGENT_ADAPTERS: dict[str, Callable[[dict[str, Any]], dict[str, Any]]] = {
    "product": product_node,
    "coder": coder_node,
    "tester": tester_node,
    "runner": runner_node,
    "sentry": sentry_node,
    "plugins": plugins_node,
    "quality": quality_node,
    "report": report_node,
    "report_generator": report_node,
}


def append_node_event(
    state: dict[str, Any],
    event_type: str,
    event_text: str,
    node: DynamicWorkflowNode,
    status: str,
    message: str,
    detail: dict[str, Any] | None = None,
) -> dict[str, Any]:
    payload = {
        "nodeId": node.node_id,
        "nodeType": node.node_type,
        "agentKey": node.agent_key,
        "stage": node.stage,
        **(detail or {}),
    }
    return append_workflow_event_from_parts(
        state,
        event_type,
        event_text,
        agent=node.agent_key,
        status=status,
        message=message,
        detail=payload,
    )


def _node_name(node: DynamicWorkflowNode) -> str:
    return node.name or node.agent_key or node.node_id


def execute_code_agent_node(state: dict[str, Any], node: DynamicWorkflowNode) -> dict[str, Any]:
    config = node.raw.get("codeAgentConfig") or node.raw.get("code_agent_config") or {}

    if not isinstance(config, dict):
        config = {}

    operation = as_string(config.get("operation") or "write_file")
    target_path = as_string(config.get("target_path") or config.get("baseDir") or "output/dynamic_code_agent.txt")
    request = {
        "operation": operation,
        "filePath": target_path,
        "content": config.get("content") or "# Dynamic LangGraph CodeAgent output\n",
        "includePatterns": config.get("includePatterns") or "**/*.md, **/*.txt, **/*.py",
        "excludePatterns": config.get("excludePatterns") or ".env, .git/**, node_modules/**, dist/**, target/**",
        "outputFile": config.get("outputFile") or "dynamic_code_agent_result.md",
        "dryRun": config.get("dryRun", True),
        "backupBeforeWrite": config.get("backupBeforeWrite", True),
    }
    append_node_event(
        state,
        "AGENT_STARTED",
        f"{_node_name(node)} 开始执行",
        node,
        "RUNNING",
        "Dynamic LangGraph 调用 CodeAgent 受控文件操作",
        {"executionMode": "executed", "operation": operation, "filePath": target_path},
    )
    result = execute_code_agent(request)
    state["code_agent_result"] = result
    state["success"] = bool(result.get("success"))
    state["stdout"] = result.get("message", "")

    for event in result.get("events", []) if isinstance(result.get("events"), list) else []:
        if isinstance(event, dict):
            state.setdefault("workflow_events", []).append(event)

    status = "SUCCESS" if result.get("success") else "FAILED"
    append_node_event(
        state,
        "AGENT_FINISHED" if result.get("success") else "AGENT_FAILED",
        f"{_node_name(node)} 执行{'完成' if result.get('success') else '失败'}",
        node,
        status,
        result.get("message", "CodeAgent 操作完成"),
        {
            "executionMode": "executed",
            "operation": result.get("operation", operation),
            "filePath": result.get("filePath", target_path),
            "auditPath": result.get("auditPath", ""),
            "result": result,
        },
    )
    return state


def execute_human_approval_node(state: dict[str, Any], node: DynamicWorkflowNode) -> dict[str, Any]:
    approved = bool(state.get("_dynamic_resume_approved", False))
    config = node.raw.get("humanApprovalConfig") or node.raw.get("human_approval_config") or {}

    if not isinstance(config, dict):
        config = {}

    if approved:
        state["approved"] = True
        state["approval_message"] = as_string(state.get("_dynamic_resume_comment") or "人工确认已批准，继续执行动态工作流")
        state["_dynamic_status"] = "RUNNING"
        append_node_event(
            state,
            "HUMAN_APPROVED",
            f"{_node_name(node)} 已批准",
            node,
            "APPROVED",
            state["approval_message"],
            {"executionMode": "paused", "resume": True},
        )
        return state

    state["approved"] = False
    state["require_human_approval"] = True
    state["_dynamic_status"] = "WAITING_FOR_HUMAN"
    state["_dynamic_pause_node"] = node.node_id
    state["approval_message"] = as_string(config.get("question") or "请确认是否继续执行后续节点")
    append_node_event(
        state,
        "HUMAN_APPROVAL_REQUIRED",
        f"{_node_name(node)} 等待人工确认",
        node,
        "WAITING_FOR_HUMAN",
        state["approval_message"],
        {"executionMode": "paused", "approval": config},
    )
    return state


def execute_condition_node(state: dict[str, Any], node: DynamicWorkflowNode) -> dict[str, Any]:
    for field_name in node.output_fields:
        state.setdefault(field_name, True)

    append_node_event(
        state,
        "STATUS_CHANGED",
        f"{_node_name(node)} 条件节点通过",
        node,
        "SUCCESS",
        "Dynamic LangGraph 条件节点已进入路由判断",
        {"executionMode": "control"},
    )
    return state


def execute_simulated_node(state: dict[str, Any], node: DynamicWorkflowNode) -> dict[str, Any]:
    received_inputs = [
        f"{field_name}={as_string(state.get(field_name))[:120]}"
        for field_name in node.input_fields
        if state.get(field_name) not in (None, "")
    ]
    input_note = "; ".join(received_inputs) if received_inputs else "no mapped inputs"

    for field_name in node.output_fields:
        state.setdefault(
            field_name,
            f"{_node_name(node)} simulated output for {field_name}; inputs: {input_note}",
        )

    append_node_event(
        state,
        "AGENT_STARTED",
        f"{_node_name(node)} 开始执行",
        node,
        "RUNNING",
        "Dynamic LangGraph 暂以平台事件模拟该自定义节点",
        {"executionMode": "simulated"},
    )
    append_node_event(
        state,
        "AGENT_FINISHED",
        f"{_node_name(node)} 执行完成",
        node,
        "SUCCESS",
        "自定义节点第一版仅记录事件，不调用真实 Agent",
        {"executionMode": "simulated"},
    )
    return state


def adapter_for(node: DynamicWorkflowNode) -> Callable[[dict[str, Any]], dict[str, Any]]:
    if node.node_type == "code_agent" or node.agent_key == "code_agent":
        return lambda state: execute_code_agent_node(state, node)

    if node.node_type == "human_approval" or node.agent_key == "human_approval":
        return lambda state: execute_human_approval_node(state, node)

    if node.node_type in {"condition", "join", "loop", "branch"}:
        return lambda state: execute_condition_node(state, node)

    adapter = REAL_AGENT_ADAPTERS.get(node.agent_key)

    if adapter is None:
        return lambda state: execute_simulated_node(state, node)

    def wrapped(state: dict[str, Any]) -> dict[str, Any]:
        state["_dynamic_current_node"] = node.node_id
        return adapter(state)

    return wrapped

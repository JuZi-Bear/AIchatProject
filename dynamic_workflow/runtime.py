from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from core.workflow import create_initial_state
from dynamic_workflow.graph_builder import build_connection_mappings, build_dynamic_graph, first_outgoing_target
from dynamic_workflow.graph_validator import validate_dynamic_template
from dynamic_workflow.resume_store import load_dynamic_run, save_dynamic_run
from dynamic_workflow.runtime_context import summarize_runtime_context
from dynamic_workflow.template_schema import DynamicWorkflowTemplate, parse_template
from utils.summary_builder import build_run_summary
from utils.ui_state_builder import build_ui_view_model
from utils.workflow_event_builder import append_workflow_event_from_parts


def _now_run_id() -> str:
    return "dynamic_langgraph_" + datetime.now().strftime("%Y%m%d_%H%M%S_") + uuid4().hex[:8]


def _request_template(request: dict[str, Any]) -> dict[str, Any]:
    raw_template = (
        request.get("template")
        or request.get("template_data")
        or request.get("templateData")
        or request.get("workflow_template")
        or {}
    )
    return raw_template if isinstance(raw_template, dict) else {}


def _input_data(request: dict[str, Any]) -> dict[str, Any]:
    raw_input = request.get("input_data") or request.get("inputData") or {}
    return raw_input if isinstance(raw_input, dict) else {}


def _event_status(state: dict[str, Any]) -> str:
    if state.get("_dynamic_status") == "WAITING_FOR_HUMAN":
        return "WAITING_FOR_HUMAN"

    if state.get("_dynamic_status") == "REJECTED":
        return "REJECTED"

    if state.get("_dynamic_error"):
        return "FAILED"

    if state.get("success") and state.get("test_success"):
        return "SUCCESS"

    if state.get("error_log"):
        return "FAILED"

    return "SUCCESS"


def _loop_counts_from_events(state: dict[str, Any]) -> dict[str, int]:
    counts: dict[str, int] = {}

    for event in state.get("workflow_events", []) if isinstance(state.get("workflow_events"), list) else []:
        detail = event.get("detail") if isinstance(event, dict) else {}

        if not isinstance(detail, dict) or detail.get("edgeType") != "loop":
            continue

        key = f"{detail.get('fromNodeId', '')}->{detail.get('toNodeId', '')}"
        counts[key] = max(counts.get(key, 0), int(detail.get("iteration") or 0))

    return counts


def _write_dynamic_report(run_id: str, template: DynamicWorkflowTemplate, state: dict[str, Any]) -> str:
    reports_dir = Path("reports")
    reports_dir.mkdir(parents=True, exist_ok=True)
    report_path = reports_dir / f"{run_id}_dynamic_langgraph_report.md"
    events = state.get("workflow_events", [])
    mappings = build_connection_mappings(template)
    lines = [
        "# Dynamic LangGraph Runtime Report",
        "",
        f"- Run ID: `{run_id}`",
        f"- Template: `{template.name}`",
        f"- Status: `{_event_status(state)}`",
        f"- Generated At: `{datetime.now().isoformat(timespec='seconds')}`",
        "",
        "## Nodes",
        "",
    ]

    for index, node in enumerate(template.nodes, start=1):
        lines.append(f"{index}. **{node.name}** - `{node.node_type}` - `{node.stage}`")

    lines.extend(["", "## Field Mappings", ""])

    if mappings:
        for mapping in mappings:
            lines.append(
                "- `"
                + str(mapping.get("fromNodeName", ""))
                + "."
                + str(mapping.get("fromOutputField", ""))
                + "` -> `"
                + str(mapping.get("toNodeName", ""))
                + "."
                + str(mapping.get("toInputField", ""))
                + "`"
            )
    else:
        lines.append("No field mappings configured.")

    runtime_context = summarize_runtime_context(state)
    lines.extend(["", "## Runtime Context Transfers", ""])

    transfers = runtime_context.get("transfers", [])
    if transfers:
        for transfer in transfers:
            lines.append(
                "- `"
                + str(transfer.get("fromNodeId", ""))
                + "."
                + str(transfer.get("fromOutputField", ""))
                + "` -> `"
                + str(transfer.get("toNodeId", ""))
                + "."
                + str(transfer.get("toInputField", ""))
                + "` = "
                + str((transfer.get("value") or {}).get("preview", ""))
            )
    else:
        lines.append("No runtime field values were transferred.")

    warnings = runtime_context.get("warnings", [])
    if warnings:
        lines.extend(["", "## Runtime Context Warnings", ""])
        for warning in warnings:
            lines.append(
                "- "
                + str(warning.get("fromNodeId", ""))
                + "."
                + str(warning.get("fromOutputField", ""))
                + " -> "
                + str(warning.get("toNodeId", ""))
                + "."
                + str(warning.get("toInputField", ""))
                + ": "
                + str(warning.get("message", ""))
            )

    lines.extend(["", "## Recent Events", ""])

    for event in events[-20:] if isinstance(events, list) else []:
        lines.append(
            f"- `{event.get('status', '')}` {event.get('event_text', '')} - {event.get('message', '')}"
        )

    report_path.write_text("\n".join(lines), encoding="utf-8")
    return report_path.as_posix()


def _build_response(
    run_id: str,
    template: DynamicWorkflowTemplate,
    state: dict[str, Any],
    validation_result: dict[str, Any],
    state_path: str = "",
) -> dict[str, Any]:
    status = _event_status(state)
    report_path = state.get("report_path", "")
    run_summary = build_run_summary(state)
    run_summary.update(
        {
            "status": status,
            "runtime_mode": "dynamic_langgraph",
            "dynamic_langgraph": True,
            "validation_result": validation_result,
            "platformRunId": run_id,
            "report_path": report_path,
            "state_path": state_path,
            "connection_mappings": build_connection_mappings(template),
            "runtime_context": summarize_runtime_context(state),
        }
    )
    ui_view_model = build_ui_view_model(state, run_summary)
    ui_view_model["runtime_summary"] = {
        "mode": "dynamic_langgraph",
        "status": status,
        "validation_result": validation_result,
        "connection_mappings": build_connection_mappings(template),
        "runtime_context": summarize_runtime_context(state),
        "pause_node": state.get("_dynamic_pause_node", ""),
        "resume_node": state.get("_dynamic_resume_node", ""),
        "loop_counts": state.get("_dynamic_loop_counts", {}),
        "observed_loop_counts": _loop_counts_from_events(state),
        "report_path": report_path,
    }
    ui_view_model["workflow_template"] = template.raw

    return {
        "platformRunId": run_id,
        "run_id": run_id,
        "status": status,
        "template_key": template.template_key,
        "validation_result": validation_result,
        "workflow_events": state.get("workflow_events", []),
        "events": state.get("workflow_events", []),
        "run_summary": run_summary,
        "ui_view_model": ui_view_model,
        "state": state,
    }


def validate_dynamic_workflow(request: dict[str, Any]) -> dict[str, Any]:
    template = parse_template(_request_template(request or {}))
    validation = validate_dynamic_template(template)
    validation["template_key"] = template.template_key
    return validation


def execute_dynamic_workflow(request: dict[str, Any]) -> dict[str, Any]:
    request = request or {}
    template = parse_template(_request_template(request))
    validation = validate_dynamic_template(template)
    run_id = str(request.get("platform_run_id") or request.get("platformRunId") or request.get("run_id") or _now_run_id())
    input_data = _input_data(request)

    if not validation.get("valid"):
        state = create_initial_state(
            input_data.get("requirement") or f"Dynamic LangGraph validation failed: {template.name}",
            require_human_approval=False,
            approved=True,
            model_provider=input_data.get("model_provider"),
        )
        state["run_id"] = run_id
        state["_dynamic_error"] = "validation_failed"
        append_workflow_event_from_parts(
            state,
            "AGENT_FAILED",
            "Dynamic LangGraph 校验失败",
            agent="workflow",
            status="FAILED",
            message="模板未通过校验，未执行 LangGraph",
            detail=validation,
        )
        return _build_response(run_id, template, state, validation)

    state = create_initial_state(
        input_data.get("requirement") or f"执行 Dynamic LangGraph: {template.name}",
        max_retry_count=input_data.get("max_retry_count"),
        require_human_approval=False,
        approved=True,
        model_provider=input_data.get("model_provider"),
    )
    state["run_id"] = run_id
    state["_dynamic_template_key"] = template.template_key
    state["_dynamic_runtime_mode"] = "dynamic_langgraph"
    state["_dynamic_connection_mappings"] = build_connection_mappings(template)
    append_workflow_event_from_parts(
        state,
        "WORKFLOW_STARTED",
        "Dynamic LangGraph 工作流开始执行",
        agent="workflow",
        status="RUNNING",
        message="已根据 Workflow Editor 模板动态编译 LangGraph",
        detail={
            "templateKey": template.template_key,
            "nodeCount": len(template.nodes),
            "edgeCount": len(template.edges),
            "connectionMappings": build_connection_mappings(template),
        },
    )

    try:
        app = build_dynamic_graph(template)
        result = app.invoke(state, {"recursion_limit": int(input_data.get("recursion_limit") or 80)})
    except Exception as error:
        state["_dynamic_error"] = str(error)
        state["success"] = False
        state["error_log"] = str(error)
        append_workflow_event_from_parts(
            state,
            "AGENT_FAILED",
            "Dynamic LangGraph 执行失败",
            agent="workflow",
            status="FAILED",
            message=str(error),
            detail={"error_type": error.__class__.__name__},
        )
        result = state

    if result.get("_dynamic_status") == "WAITING_FOR_HUMAN":
        pause_node = result.get("_dynamic_pause_node", "")
        result["_dynamic_resume_node"] = first_outgoing_target(template, pause_node)
        state_path = save_dynamic_run(
            run_id,
            {
                "run_id": run_id,
                "template": template.raw,
                "state": result,
                "resume_node_id": result.get("_dynamic_resume_node", ""),
                "validation_result": validation,
            },
        )
        return _build_response(run_id, template, result, validation, state_path=state_path)

    result["report_path"] = _write_dynamic_report(run_id, template, result)
    append_workflow_event_from_parts(
        result,
        "WORKFLOW_FINISHED",
        "Dynamic LangGraph 工作流执行完成",
        agent="workflow",
        status=_event_status(result),
        message="动态 LangGraph 执行路径已完成",
        detail={
            "templateKey": template.template_key,
            "loopCounts": result.get("_dynamic_loop_counts", {}) or _loop_counts_from_events(result),
            "reportPath": result.get("report_path", ""),
        },
    )
    state_path = save_dynamic_run(
        run_id,
        {
            "run_id": run_id,
            "template": template.raw,
            "state": result,
            "resume_node_id": "",
            "validation_result": validation,
        },
    )
    return _build_response(run_id, template, result, validation, state_path=state_path)


def resume_dynamic_workflow(run_id: str, request: dict[str, Any]) -> dict[str, Any]:
    request = request or {}
    stored = load_dynamic_run(run_id)
    template = parse_template(stored.get("template") or {})
    validation = stored.get("validation_result") or validate_dynamic_template(template)
    state = stored.get("state") if isinstance(stored.get("state"), dict) else {}
    approved = bool(request.get("approved", True))
    comment = str(request.get("comment") or "")

    if not approved:
        state["_dynamic_status"] = "REJECTED"
        state["approved"] = False
        state["success"] = False
        state["approval_message"] = comment or "人工确认已拒绝"
        append_workflow_event_from_parts(
            state,
            "HUMAN_REJECTED",
            "Dynamic LangGraph 人工确认已拒绝",
            agent="human_approval",
            status="REJECTED",
            message=state["approval_message"],
            detail={"run_id": run_id},
        )
        save_dynamic_run(run_id, {**stored, "state": state, "resume_node_id": ""})
        return _build_response(run_id, template, state, validation)

    resume_node_id = str(stored.get("resume_node_id") or "")
    state["_dynamic_resume_approved"] = True
    state["_dynamic_resume_comment"] = comment
    state["_dynamic_status"] = "RUNNING"

    try:
        if resume_node_id:
            app = build_dynamic_graph(template, start_node_id=resume_node_id)
            result = app.invoke(state, {"recursion_limit": int(request.get("recursion_limit") or 80)})
        else:
            result = state
    except Exception as error:
        state["_dynamic_error"] = str(error)
        state["success"] = False
        state["error_log"] = str(error)
        append_workflow_event_from_parts(
            state,
            "AGENT_FAILED",
            "Dynamic LangGraph 恢复执行失败",
            agent="workflow",
            status="FAILED",
            message=str(error),
            detail={"error_type": error.__class__.__name__},
        )
        result = state

    if result.get("_dynamic_status") == "WAITING_FOR_HUMAN":
        pause_node = result.get("_dynamic_pause_node", "")
        result["_dynamic_resume_node"] = first_outgoing_target(template, pause_node)
        state_path = save_dynamic_run(
            run_id,
            {
                "run_id": run_id,
                "template": template.raw,
                "state": result,
                "resume_node_id": result.get("_dynamic_resume_node", ""),
                "validation_result": validation,
            },
        )
        return _build_response(run_id, template, result, validation, state_path=state_path)

    result["report_path"] = _write_dynamic_report(run_id, template, result)
    append_workflow_event_from_parts(
        result,
        "WORKFLOW_FINISHED",
        "Dynamic LangGraph 恢复后执行完成",
        agent="workflow",
        status=_event_status(result),
        message="动态 LangGraph 暂停任务已恢复并完成",
        detail={
            "reportPath": result.get("report_path", ""),
            "loopCounts": result.get("_dynamic_loop_counts", {}) or _loop_counts_from_events(result),
        },
    )
    state_path = save_dynamic_run(
        run_id,
        {
            "run_id": run_id,
            "template": template.raw,
            "state": result,
            "resume_node_id": "",
            "validation_result": validation,
        },
    )
    return _build_response(run_id, template, result, validation, state_path=state_path)

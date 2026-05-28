from __future__ import annotations

from typing import Any

from dynamic_workflow.template_schema import DynamicWorkflowEdge, DynamicWorkflowNode, DynamicWorkflowTemplate
from utils.workflow_event_builder import append_workflow_event_from_parts


def _ensure_context(state: dict[str, Any]) -> dict[str, Any]:
    context = state.setdefault("_dynamic_runtime_context", {})

    if not isinstance(context, dict):
        context = {}
        state["_dynamic_runtime_context"] = context

    context.setdefault("node_inputs", {})
    context.setdefault("node_outputs", {})
    context.setdefault("transfers", [])
    context.setdefault("warnings", [])

    return context


def preview_value(value: Any, max_chars: int = 220) -> dict[str, Any]:
    text = ""
    value_type = type(value).__name__

    if value is None:
        text = ""
    elif isinstance(value, str):
        text = value
    elif isinstance(value, (int, float, bool)):
        text = str(value)
    elif isinstance(value, dict):
        text = str({key: value.get(key) for key in list(value.keys())[:8]})
    elif isinstance(value, list):
        text = str(value[:8])
    else:
        text = str(value)

    truncated = len(text) > max_chars
    if truncated:
        text = text[:max_chars] + "..."

    return {
        "present": value is not None,
        "type": value_type,
        "preview": text,
        "truncated": truncated,
    }


def summarize_runtime_context(state: dict[str, Any]) -> dict[str, Any]:
    context = _ensure_context(state)
    node_inputs = context.get("node_inputs", {}) if isinstance(context.get("node_inputs"), dict) else {}
    node_outputs = context.get("node_outputs", {}) if isinstance(context.get("node_outputs"), dict) else {}
    transfers = context.get("transfers", []) if isinstance(context.get("transfers"), list) else []
    warnings = context.get("warnings", []) if isinstance(context.get("warnings"), list) else []

    return {
        "node_inputs": {
            node_id: {
                field: preview_value(value)
                for field, value in fields.items()
            }
            for node_id, fields in node_inputs.items()
            if isinstance(fields, dict)
        },
        "node_outputs": {
            node_id: {
                field: preview_value(value)
                for field, value in fields.items()
            }
            for node_id, fields in node_outputs.items()
            if isinstance(fields, dict)
        },
        "transfers": [
            {
                **transfer,
                "value": preview_value(transfer.get("value")),
            }
            for transfer in transfers
            if isinstance(transfer, dict)
        ],
        "warnings": warnings,
    }


def _incoming_field_edges(template: DynamicWorkflowTemplate, node: DynamicWorkflowNode) -> list[DynamicWorkflowEdge]:
    return [
        edge
        for edge in template.edges
        if edge.to_node_id == node.node_id and edge.from_output_field and edge.to_input_field
    ]


def _field_value_from_context(
    state: dict[str, Any],
    source_node_id: str,
    field_name: str,
) -> tuple[Any, str]:
    context = _ensure_context(state)
    node_outputs = context.get("node_outputs", {})

    if isinstance(node_outputs, dict):
        source_outputs = node_outputs.get(source_node_id)
        if isinstance(source_outputs, dict) and field_name in source_outputs:
            return source_outputs.get(field_name), "node_output"

    if field_name in state:
        return state.get(field_name), "state"

    return None, "missing"


def inject_node_inputs(
    state: dict[str, Any],
    template: DynamicWorkflowTemplate,
    node: DynamicWorkflowNode,
) -> dict[str, Any]:
    context = _ensure_context(state)
    incoming_edges = _incoming_field_edges(template, node)
    injected: list[dict[str, Any]] = []

    for edge in incoming_edges:
        value, source = _field_value_from_context(state, edge.from_node_id, edge.from_output_field)
        transfer = {
            "fromNodeId": edge.from_node_id,
            "fromOutputField": edge.from_output_field,
            "toNodeId": edge.to_node_id,
            "toInputField": edge.to_input_field,
            "edgeType": edge.edge_type,
            "dataType": edge.data_type,
            "label": edge.label or f"{edge.from_output_field} -> {edge.to_input_field}",
            "source": source,
            "value": value,
        }

        if source == "missing":
            warning = {
                **transfer,
                "message": "source output missing; target input was not overwritten",
            }
            context["warnings"].append(warning)
            continue

        state[edge.to_input_field] = value
        context["node_inputs"].setdefault(node.node_id, {})[edge.to_input_field] = value
        context["transfers"].append(transfer)
        injected.append(transfer)

    if injected:
        append_workflow_event_from_parts(
            state,
            "STATUS_CHANGED",
            f"{node.name} 已接收字段级输入",
            agent=node.agent_key,
            status="RUNNING",
            message=f"已注入 {len(injected)} 个字段映射输入",
            detail={
                "nodeId": node.node_id,
                "nodeType": node.node_type,
                "executionMode": "runtime_context",
                "fieldTransfers": [
                    {
                        **item,
                        "value": preview_value(item.get("value")),
                    }
                    for item in injected
                ],
            },
        )

    return state


def capture_node_outputs(state: dict[str, Any], node: DynamicWorkflowNode) -> dict[str, Any]:
    context = _ensure_context(state)
    captured: dict[str, Any] = {}

    for field_name in node.output_fields:
        if field_name in state:
            captured[field_name] = state.get(field_name)

    if captured:
        context["node_outputs"].setdefault(node.node_id, {}).update(captured)
        append_workflow_event_from_parts(
            state,
            "STATUS_CHANGED",
            f"{node.name} 已发布字段级输出",
            agent=node.agent_key,
            status="SUCCESS",
            message=f"已捕获 {len(captured)} 个输出字段",
            detail={
                "nodeId": node.node_id,
                "nodeType": node.node_type,
                "executionMode": "runtime_context",
                "fieldOutputs": {
                    field: preview_value(value)
                    for field, value in captured.items()
                },
            },
        )

    return state


def wrap_node_with_runtime_context(
    template: DynamicWorkflowTemplate,
    node: DynamicWorkflowNode,
    handler,
):
    def wrapped(state: dict[str, Any]) -> dict[str, Any]:
        state["_dynamic_current_node"] = node.node_id
        inject_node_inputs(state, template, node)
        result = handler(state)
        if result is None:
            result = state
        capture_node_outputs(result, node)
        return result

    return wrapped

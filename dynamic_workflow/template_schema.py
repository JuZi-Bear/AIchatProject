from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


CONTROL_EDGE_TYPES = {"", "control", "branch", "loop", "resume"}
NODE_TYPES = {
    "agent",
    "code_agent",
    "human_approval",
    "condition",
    "join",
    "loop",
    "report",
    "custom_agent",
    "branch",
}


@dataclass
class DynamicWorkflowNode:
    node_id: str
    agent_key: str
    node_type: str
    name: str
    stage: str = "custom"
    enabled: bool = True
    input_fields: list[str] = field(default_factory=list)
    output_fields: list[str] = field(default_factory=list)
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass
class DynamicWorkflowEdge:
    from_node_id: str
    to_node_id: str
    edge_type: str = "control"
    condition: str = ""
    from_output_field: str = ""
    to_input_field: str = ""
    data_type: str = ""
    label: str = ""
    max_iterations: int = 0
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass
class DynamicWorkflowTemplate:
    template_key: str
    name: str
    description: str
    nodes: list[DynamicWorkflowNode]
    edges: list[DynamicWorkflowEdge]
    raw: dict[str, Any]


def as_string(value: Any) -> str:
    return "" if value is None else str(value)


def as_bool(value: Any, default: bool = True) -> bool:
    if isinstance(value, bool):
        return value

    if value is None:
        return default

    if isinstance(value, str):
        return value.strip().lower() not in {"0", "false", "no", "off", "disabled"}

    return bool(value)


def string_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value if str(item).strip()]

    if isinstance(value, str):
        return [item.strip() for item in value.split(",") if item.strip()]

    return []


def nested_int(source: dict[str, Any], key: str, nested_key: str, default: int = 0) -> int:
    value = source.get(key)

    if isinstance(value, dict):
        value = value.get(nested_key)
    else:
        value = source.get(nested_key)

    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def int_value(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def normalize_node(raw_node: dict[str, Any], index: int) -> DynamicWorkflowNode:
    agent_key = as_string(raw_node.get("agentKey") or raw_node.get("agent_key")).strip()
    node_type = as_string(raw_node.get("nodeType") or raw_node.get("node_type")).strip()

    if not node_type:
        if agent_key == "code_agent":
            node_type = "code_agent"
        elif agent_key == "human_approval":
            node_type = "human_approval"
        elif agent_key in {"report", "report_generator"}:
            node_type = "report"
        elif agent_key in {"branch_if", "branch_and", "branch_or"}:
            node_type = "condition"
        else:
            node_type = "agent"

    node_id = as_string(raw_node.get("nodeId") or raw_node.get("node_id") or f"{agent_key or node_type}_{index + 1}").strip()
    name = as_string(raw_node.get("name") or agent_key or node_type or node_id).strip()

    return DynamicWorkflowNode(
        node_id=node_id,
        agent_key=agent_key or node_type,
        node_type=node_type,
        name=name,
        stage=as_string(raw_node.get("stage") or "custom"),
        enabled=as_bool(raw_node.get("enabled"), True),
        input_fields=string_list(raw_node.get("input_fields") or raw_node.get("inputFields")),
        output_fields=string_list(raw_node.get("output_fields") or raw_node.get("outputFields")),
        raw=raw_node,
    )


def normalize_edge(raw_edge: dict[str, Any]) -> DynamicWorkflowEdge:
    edge_type = as_string(raw_edge.get("edgeType") or raw_edge.get("edge_type") or "control").strip() or "control"
    loop_policy = raw_edge.get("loopPolicy") or raw_edge.get("loop_policy")
    max_iterations = 0

    if isinstance(loop_policy, dict):
        max_iterations = int_value(loop_policy.get("maxIterations") or loop_policy.get("max_iterations"), 0)

    if not max_iterations:
        max_iterations = nested_int(raw_edge, "loopPolicy", "maxIterations", 0)

    return DynamicWorkflowEdge(
        from_node_id=as_string(raw_edge.get("fromNodeId") or raw_edge.get("from_node_id")).strip(),
        to_node_id=as_string(raw_edge.get("toNodeId") or raw_edge.get("to_node_id")).strip(),
        edge_type=edge_type,
        condition=as_string(raw_edge.get("condition")).strip(),
        from_output_field=as_string(raw_edge.get("fromOutputField") or raw_edge.get("from_output_field")).strip(),
        to_input_field=as_string(raw_edge.get("toInputField") or raw_edge.get("to_input_field")).strip(),
        data_type=as_string(raw_edge.get("dataType") or raw_edge.get("data_type")).strip(),
        label=as_string(raw_edge.get("label")).strip(),
        max_iterations=max_iterations,
        raw=raw_edge,
    )


def parse_template(raw_template: dict[str, Any]) -> DynamicWorkflowTemplate:
    if raw_template is None:
        raw_template = {}

    nodes = [
        normalize_node(node, index)
        for index, node in enumerate(raw_template.get("nodes") or [])
        if isinstance(node, dict)
    ]
    edges = [
        normalize_edge(edge)
        for edge in raw_template.get("connections") or raw_template.get("edges") or []
        if isinstance(edge, dict)
    ]
    template_key = as_string(
        raw_template.get("workflowTemplateKey")
        or raw_template.get("templateKey")
        or raw_template.get("key")
        or "dynamic_workflow"
    )

    return DynamicWorkflowTemplate(
        template_key=template_key,
        name=as_string(raw_template.get("name") or template_key),
        description=as_string(raw_template.get("description")),
        nodes=nodes,
        edges=edges,
        raw=raw_template,
    )

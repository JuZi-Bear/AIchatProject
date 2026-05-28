from __future__ import annotations

from collections import defaultdict
from typing import Any

from langgraph.graph import END, START, StateGraph

from core.state import AgentState
from dynamic_workflow.condition_evaluator import evaluate_condition
from dynamic_workflow.node_adapters import adapter_for
from dynamic_workflow.runtime_context import wrap_node_with_runtime_context
from dynamic_workflow.template_schema import DynamicWorkflowEdge, DynamicWorkflowTemplate
from utils.workflow_event_builder import append_workflow_event_from_parts


END_ROUTE = "__dynamic_end__"


def _control_edges(template: DynamicWorkflowTemplate) -> list[DynamicWorkflowEdge]:
    return [edge for edge in template.edges if edge.edge_type != "data"]


def entry_node_id(template: DynamicWorkflowTemplate) -> str:
    node_ids = {node.node_id for node in template.nodes}
    incoming: dict[str, int] = {node_id: 0 for node_id in node_ids}

    for edge in _control_edges(template):
        if edge.from_node_id in node_ids and edge.to_node_id in node_ids and edge.edge_type != "loop":
            incoming[edge.to_node_id] = incoming.get(edge.to_node_id, 0) + 1

    for node in template.nodes:
        if incoming.get(node.node_id, 0) == 0:
            return node.node_id

    return template.nodes[0].node_id


def first_outgoing_target(template: DynamicWorkflowTemplate, node_id: str) -> str:
    for edge in _control_edges(template):
        if edge.from_node_id == node_id and edge.to_node_id and edge.edge_type != "loop":
            return edge.to_node_id

    return ""


def build_connection_mappings(template: DynamicWorkflowTemplate) -> list[dict[str, Any]]:
    node_by_id = {node.node_id: node for node in template.nodes}
    mappings: list[dict[str, Any]] = []

    for edge in template.edges:
        source = node_by_id.get(edge.from_node_id)
        target = node_by_id.get(edge.to_node_id)

        if source is None or target is None:
            continue

        from_field = edge.from_output_field or (source.output_fields[0] if source.output_fields else "output")
        to_field = edge.to_input_field or (target.input_fields[0] if target.input_fields else "input")
        mappings.append(
            {
                "fromNodeId": source.node_id,
                "fromNodeName": source.name,
                "fromOutputField": from_field,
                "toNodeId": target.node_id,
                "toNodeName": target.name,
                "toInputField": to_field,
                "edgeType": edge.edge_type,
                "condition": edge.condition,
                "dataType": edge.data_type,
                "label": edge.label or f"{from_field} -> {to_field}",
            }
        )

    return mappings


def _route_for_node(
    template: DynamicWorkflowTemplate,
    source_node_id: str,
    outgoing: list[DynamicWorkflowEdge],
):
    closure_loop_counts: dict[str, int] = {}

    def route(state: dict[str, Any]) -> str:
        if state.get("_dynamic_status") == "WAITING_FOR_HUMAN":
            return END_ROUTE

        loop_counts = closure_loop_counts
        fallback_route = END_ROUTE

        for index, edge in enumerate(outgoing):
            route_key = f"edge_{source_node_id}_{index}"
            condition = (edge.condition or "").strip()

            if condition.lower() == "else":
                fallback_route = route_key
                continue

            if edge.edge_type == "loop":
                edge_key = f"{edge.from_node_id}->{edge.to_node_id}:{edge.condition or 'loop'}"
                current_count = int(loop_counts.get(edge_key, 0) or 0)
                max_iterations = edge.max_iterations

                if max_iterations <= 0 or current_count >= max_iterations:
                    continue

                if not condition or evaluate_condition(condition, state):
                    loop_counts[edge_key] = current_count + 1
                    state["_dynamic_loop_counts"] = dict(loop_counts)
                    append_workflow_event_from_parts(
                        state,
                        "STATUS_CHANGED",
                        "Dynamic LangGraph 进入循环边",
                        agent="workflow",
                        status="RUNNING",
                        message=f"循环 {edge.from_node_id} -> {edge.to_node_id} 第 {current_count + 1}/{max_iterations} 次",
                        detail={
                            "edgeType": "loop",
                            "fromNodeId": edge.from_node_id,
                            "toNodeId": edge.to_node_id,
                            "iteration": current_count + 1,
                            "maxIterations": max_iterations,
                        },
                    )
                    return route_key

                continue

            if not condition or evaluate_condition(condition, state):
                if edge.edge_type == "branch" or condition:
                    append_workflow_event_from_parts(
                        state,
                        "STATUS_CHANGED",
                        "Dynamic LangGraph 分支已选择",
                        agent="workflow",
                        status="RUNNING",
                        message=f"{edge.from_node_id} -> {edge.to_node_id}",
                        detail={
                            "edgeType": edge.edge_type or "control",
                            "condition": condition,
                            "fromNodeId": edge.from_node_id,
                            "toNodeId": edge.to_node_id,
                        },
                    )
                return route_key

        return fallback_route

    return route


def build_dynamic_graph(template: DynamicWorkflowTemplate, start_node_id: str | None = None):
    graph = StateGraph(AgentState)
    node_ids = {node.node_id for node in template.nodes}
    outgoing: dict[str, list[DynamicWorkflowEdge]] = defaultdict(list)

    for node in template.nodes:
        graph.add_node(node.node_id, wrap_node_with_runtime_context(template, node, adapter_for(node)))

    for edge in _control_edges(template):
        if edge.from_node_id in node_ids and edge.to_node_id in node_ids:
            outgoing[edge.from_node_id].append(edge)

    start = start_node_id if start_node_id in node_ids else entry_node_id(template)
    graph.add_edge(START, start)

    for node in template.nodes:
        edges = outgoing.get(node.node_id, [])

        if not edges:
            graph.add_edge(node.node_id, END)
            continue

        is_pause_node = node.node_type == "human_approval" or node.agent_key == "human_approval"

        if len(edges) == 1 and not edges[0].condition and edges[0].edge_type not in {"branch", "loop"} and not is_pause_node:
            graph.add_edge(node.node_id, edges[0].to_node_id)
            continue

        route_map = {
            f"edge_{node.node_id}_{index}": edge.to_node_id
            for index, edge in enumerate(edges)
        }
        route_map[END_ROUTE] = END
        graph.add_conditional_edges(node.node_id, _route_for_node(template, node.node_id, edges), route_map)

    return graph.compile()

from __future__ import annotations

from collections import defaultdict

from dynamic_workflow.condition_evaluator import validate_condition
from dynamic_workflow.template_schema import CONTROL_EDGE_TYPES, NODE_TYPES, DynamicWorkflowTemplate


def _issue(severity: str, title: str, message: str, node_id: str = "", edge: dict | None = None) -> dict:
    payload = {
        "severity": severity,
        "title": title,
        "message": message,
    }

    if node_id:
        payload["nodeId"] = node_id

    if edge:
        payload["edge"] = edge

    return payload


def _has_cycle(node_ids: set[str], outgoing: dict[str, list[str]]) -> bool:
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node_id: str) -> bool:
        if node_id in visiting:
            return True

        if node_id in visited:
            return False

        visiting.add(node_id)

        for target in outgoing.get(node_id, []):
            if visit(target):
                return True

        visiting.remove(node_id)
        visited.add(node_id)
        return False

    return any(visit(node_id) for node_id in node_ids if node_id not in visited)


def validate_dynamic_template(template: DynamicWorkflowTemplate) -> dict:
    issues: list[dict] = []
    node_by_id = {node.node_id: node for node in template.nodes}
    node_ids = set(node_by_id.keys())
    incoming: dict[str, list[str]] = defaultdict(list)
    outgoing: dict[str, list[str]] = defaultdict(list)
    non_loop_outgoing: dict[str, list[str]] = defaultdict(list)

    if not template.nodes:
        issues.append(_issue("error", "缺少节点", "动态 LangGraph 模板至少需要一个节点"))

    if len(node_by_id) != len(template.nodes):
        issues.append(_issue("error", "节点 ID 重复", "模板中存在重复 nodeId，无法编译为 LangGraph"))

    for node in template.nodes:
        if not node.node_id:
            issues.append(_issue("error", "节点缺少 ID", "每个节点都必须有稳定 nodeId"))

        if node.node_type not in NODE_TYPES:
            issues.append(
                _issue(
                    "warning",
                    "未知节点类型",
                    f"节点 {node.name} 的 nodeType={node.node_type} 将按 custom_agent 处理",
                    node.node_id,
                )
            )

        if not node.enabled:
            issues.append(_issue("warning", "节点未启用", f"节点 {node.name} 当前 disabled，执行时会跳过", node.node_id))

    seen_edges: set[tuple[str, str, str, str]] = set()
    input_bindings: dict[tuple[str, str], list[str]] = defaultdict(list)

    for edge in template.edges:
        edge_payload = {
            "fromNodeId": edge.from_node_id,
            "toNodeId": edge.to_node_id,
            "edgeType": edge.edge_type,
            "condition": edge.condition,
            "fromOutputField": edge.from_output_field,
            "toInputField": edge.to_input_field,
        }

        if edge.from_node_id not in node_ids:
            issues.append(_issue("error", "连线 source 不存在", f"source={edge.from_node_id}", edge=edge_payload))
            continue

        if edge.to_node_id not in node_ids:
            issues.append(_issue("error", "连线 target 不存在", f"target={edge.to_node_id}", edge=edge_payload))
            continue

        if edge.from_node_id == edge.to_node_id and edge.edge_type != "loop":
            issues.append(_issue("error", "非法自连接", "只有 edgeType=loop 的连线允许回到自身", edge.from_node_id, edge_payload))

        if edge.edge_type not in CONTROL_EDGE_TYPES and edge.edge_type != "data":
            issues.append(_issue("warning", "未知连线类型", f"edgeType={edge.edge_type} 将按 control 处理", edge=edge_payload))

        if edge.edge_type == "loop" and edge.max_iterations <= 0:
            issues.append(_issue("error", "循环缺少上限", "loop 连线必须配置 maxIterations，避免无限循环", edge.from_node_id, edge_payload))

        condition_ok, condition_message = validate_condition(edge.condition)
        if not condition_ok:
            issues.append(_issue("error", "非法条件表达式", condition_message, edge.from_node_id, edge_payload))

        source = node_by_id[edge.from_node_id]
        target = node_by_id[edge.to_node_id]

        if edge.from_output_field and edge.from_output_field not in source.output_fields:
            issues.append(_issue("error", "输出字段不存在", f"{source.name}.{edge.from_output_field}", source.node_id, edge_payload))

        if edge.to_input_field and edge.to_input_field not in target.input_fields:
            issues.append(_issue("error", "输入字段不存在", f"{target.name}.{edge.to_input_field}", target.node_id, edge_payload))

        key = (edge.from_node_id, edge.to_node_id, edge.from_output_field, edge.to_input_field)
        if key in seen_edges:
            issues.append(_issue("warning", "重复连线", "存在完全相同的字段级连线", edge.from_node_id, edge_payload))
        seen_edges.add(key)

        if edge.to_input_field:
            input_bindings[(edge.to_node_id, edge.to_input_field)].append(edge.from_node_id)

        if edge.edge_type != "data":
            if edge.edge_type != "loop":
                incoming[edge.to_node_id].append(edge.from_node_id)
            outgoing[edge.from_node_id].append(edge.to_node_id)

            if edge.edge_type != "loop":
                non_loop_outgoing[edge.from_node_id].append(edge.to_node_id)

    for (node_id, input_field), sources in input_bindings.items():
        if len(sources) > 1:
            issues.append(
                _issue(
                    "warning",
                    "输入字段有多个来源",
                    f"{node_id}.{input_field} 同时连接了 {len(sources)} 个上游，执行时只作为映射信息展示",
                    node_id,
                )
            )

    if template.nodes:
        entry_nodes = [node.node_id for node in template.nodes if not incoming.get(node.node_id)]
        terminal_nodes = [node.node_id for node in template.nodes if not non_loop_outgoing.get(node.node_id)]

        if not entry_nodes:
            issues.append(_issue("error", "缺少入口节点", "模板没有无入边节点，无法确定 START"))
        elif len(entry_nodes) > 1:
            issues.append(_issue("warning", "多个入口节点", f"将使用第一个入口节点: {entry_nodes[0]}"))

        if not terminal_nodes:
            issues.append(_issue("error", "缺少终止节点", "模板没有可到达 END 的节点"))

        graph_without_loop = defaultdict(list)
        for edge in template.edges:
            if edge.edge_type in {"data", "loop"}:
                continue
            if edge.from_node_id in node_ids and edge.to_node_id in node_ids:
                graph_without_loop[edge.from_node_id].append(edge.to_node_id)

        if _has_cycle(node_ids, graph_without_loop):
            issues.append(_issue("error", "存在未标记循环", "检测到环路，但相关连线没有声明 edgeType=loop"))

    errors = [issue for issue in issues if issue.get("severity") == "error"]
    warnings = [issue for issue in issues if issue.get("severity") == "warning"]

    return {
        "valid": not errors,
        "errors": errors,
        "warnings": warnings,
        "issues": issues,
        "node_count": len(template.nodes),
        "edge_count": len(template.edges),
    }

import type { AgentNodeData, ConnectionData, WorkflowDataType } from "@/types/workflowEditor";

export const WORKFLOW_PORT_COLORS: Record<WorkflowDataType, string> = {
  requirement: "#1a73e8",
  product: "#4285f4",
  code: "#34a853",
  test: "#f9ab00",
  error: "#ea4335",
  file: "#0f9d58",
  report: "#7c3aed",
  approval: "#f97316",
  custom: "#64748b",
};

export const WORKFLOW_PORT_TYPE_LABELS: Record<WorkflowDataType, string> = {
  requirement: "req",
  product: "product",
  code: "code",
  test: "test",
  error: "error",
  file: "file",
  report: "report",
  approval: "approval",
  custom: "custom",
};

export function classifyWorkflowField(field = "", fallback: WorkflowDataType = "custom"): WorkflowDataType {
  const normalized = field.toLowerCase();

  if (normalized.includes("requirement") || normalized.includes("input") || normalized.includes("prompt")) {
    return "requirement";
  }

  if (normalized.includes("product") || normalized.includes("plan") || normalized.includes("spec")) {
    return "product";
  }

  if (normalized.includes("code") || normalized.includes("diff") || normalized.includes("patch")) {
    return "code";
  }

  if (
    normalized.includes("test") ||
    normalized.includes("pytest") ||
    normalized.includes("coverage") ||
    normalized.includes("quality")
  ) {
    return "test";
  }

  if (
    normalized.includes("error") ||
    normalized.includes("stderr") ||
    normalized.includes("exception") ||
    normalized.includes("sentry")
  ) {
    return "error";
  }

  if (
    normalized.includes("file") ||
    normalized.includes("path") ||
    normalized.includes("audit") ||
    normalized.includes("folder")
  ) {
    return "file";
  }

  if (normalized.includes("report") || normalized.includes("markdown") || normalized.includes("summary")) {
    return "report";
  }

  if (normalized.includes("approval") || normalized.includes("human") || normalized.includes("approved")) {
    return "approval";
  }

  return fallback;
}

export function workflowPortColor(field = "", dataType?: WorkflowDataType) {
  return WORKFLOW_PORT_COLORS[dataType || classifyWorkflowField(field)];
}

export function workflowPortTypeLabel(field = "", dataType?: WorkflowDataType) {
  return WORKFLOW_PORT_TYPE_LABELS[dataType || classifyWorkflowField(field)];
}

export function primaryInputField(node?: Pick<AgentNodeData, "input_fields"> | null) {
  return node?.input_fields?.[0] || "";
}

export function primaryOutputField(node?: Pick<AgentNodeData, "output_fields"> | null) {
  return node?.output_fields?.[0] || "";
}

export function workflowConnectionKey(connection: Pick<ConnectionData, "fromNodeId" | "toNodeId" | "fromOutputField" | "toInputField">) {
  return [
    connection.fromNodeId,
    connection.fromOutputField || "*",
    connection.toNodeId,
    connection.toInputField || "*",
  ].join("::");
}

export function workflowConnectionLabel(connection: ConnectionData, sourceName = "", targetName = "") {
  const from = connection.fromOutputField || "default";
  const to = connection.toInputField || "default";
  const nodeLabel = sourceName && targetName ? `${sourceName} → ${targetName}` : "";

  return nodeLabel ? `${nodeLabel} · ${from} → ${to}` : `${from} → ${to}`;
}

export function enrichConnectionFields(
  connection: ConnectionData,
  sourceNode?: AgentNodeData,
  targetNode?: AgentNodeData,
): ConnectionData {
  const fromOutputField = connection.fromOutputField || primaryOutputField(sourceNode);
  const toInputField = connection.toInputField || primaryInputField(targetNode);
  const dataType = connection.dataType || classifyWorkflowField(fromOutputField || toInputField);

  return {
    ...connection,
    fromOutputField,
    toInputField,
    dataType,
    color: connection.color || workflowPortColor(fromOutputField || toInputField, dataType),
    label: connection.label || `${fromOutputField || "output"} → ${toInputField || "input"}`,
  };
}

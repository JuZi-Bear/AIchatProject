import { apiClient, currentApiMode } from "./client";

import type { ApiResponse } from "@/types/api";
import type {
  DynamicLangGraphExecutionResult,
  DynamicLangGraphValidationResult,
  InstantiateWorkflowRequest,
  InstantiateWorkflowResponse,
  WorkflowRuntimeExecutionResult,
  WorkflowRuntimeNodeEvent,
  WorkflowSkillExportResult,
  WorkflowTemplate,
} from "@/types/workflow";
import type { AgentNodeData, ConnectionData, WorkflowTemplateData } from "@/types/workflowEditor";

type RawWorkflowTemplate = Partial<WorkflowTemplate> & {
  agentSequence?: string[];
  stageSequence?: string[];
  mdPath?: string;
};

type RawInstantiateWorkflowResponse = Partial<InstantiateWorkflowResponse> & {
  platform_run_id?: string;
};

type RawWorkflowRuntimeExecutionResult = RawInstantiateWorkflowResponse &
  Partial<WorkflowRuntimeExecutionResult> & {
    events?: WorkflowRuntimeNodeEvent[];
    warnings?: string[];
    status?: string;
    validation_result?: DynamicLangGraphValidationResult;
  };

type RawPlatformWorkflowTemplate = Partial<WorkflowTemplateData> & {
  id?: number;
  key?: string;
  templateKey?: string;
  workflow_template_key?: string;
  agent_sequence?: string[];
  stage_sequence?: string[];
};

function workflowPath(path: string) {
  return currentApiMode === "java" ? `/workflows${path}` : `/api/workflows${path}`;
}

function platformWorkflowPath(path: string) {
  return `/platform/workflows${path}`;
}

function unwrapApiResponse<T>(response: ApiResponse<T> | T): T {
  if (currentApiMode === "java") {
    const apiResponse = response as ApiResponse<T>;
    if (!apiResponse.success) {
      throw new Error(apiResponse.message || "Java workflow request failed");
    }

    return apiResponse.data;
  }

  return response as T;
}

function normalizeTemplate(template: RawWorkflowTemplate): WorkflowTemplate {
  return {
    key: template.key || "",
    name: template.name || template.key || "",
    description: template.description || "",
    agent_sequence: template.agent_sequence || template.agentSequence || [],
    stage_sequence: template.stage_sequence || template.stageSequence || [],
    enabled: template.enabled ?? true,
    version: template.version || "1.0",
    md_path: template.md_path || template.mdPath || "",
    markdown: template.markdown || "",
  };
}

function normalizeInstantiateResponse(response: RawInstantiateWorkflowResponse): InstantiateWorkflowResponse {
  const platformRunId = response.platformRunId || response.platform_run_id || response.run_id || "";

  return {
    platformRunId,
    platform_run_id: response.platform_run_id || platformRunId,
    run_id: response.run_id || platformRunId,
    template_key: response.template_key || "",
    input_data: response.input_data || {},
    workflow_events: response.workflow_events || [],
    run_summary: response.run_summary || {},
    ui_view_model: response.ui_view_model || {},
  };
}

function normalizeRuntimeExecutionResponse(response: RawWorkflowRuntimeExecutionResult): WorkflowRuntimeExecutionResult {
  return {
    ...normalizeInstantiateResponse(response),
    status: response.status || String(response.run_summary?.status || ""),
    events: response.events || response.workflow_events || [],
    warnings: response.warnings || [],
    validation_result: response.validation_result,
  };
}

function normalizeNode(node: Partial<AgentNodeData>, index: number): AgentNodeData {
  return {
    nodeId: node.nodeId || `${node.agentKey || "agent"}_${index + 1}`,
    agentKey: node.agentKey || "",
    nodeType: node.nodeType,
    executionMode: node.executionMode,
    langGraphKey: node.langGraphKey,
    name: node.name || node.agentKey || `Agent ${index + 1}`,
    role: node.role,
    position: {
      x: Number(node.position?.x ?? 80 + (index % 3) * 260),
      y: Number(node.position?.y ?? 80 + Math.floor(index / 3) * 150),
    },
    input_fields: node.input_fields || [],
    output_fields: node.output_fields || [],
    stage: node.stage || "custom",
    enabled: node.enabled ?? true,
    description: node.description || "",
    codeAgentConfig: node.codeAgentConfig,
    humanApprovalConfig: node.humanApprovalConfig,
    customAgentMeta: node.customAgentMeta,
    pausePolicy: node.pausePolicy,
    loopPolicy: node.loopPolicy,
  };
}

function normalizeConnection(connection: Partial<ConnectionData>): ConnectionData {
  return {
    fromNodeId: connection.fromNodeId || "",
    toNodeId: connection.toNodeId || "",
    fromOutputField: connection.fromOutputField || "",
    toInputField: connection.toInputField || "",
    dataType: connection.dataType,
    color: connection.color || "",
    label: connection.label || "",
    edgeType: connection.edgeType || "control",
    condition: connection.condition || "",
    loopPolicy: connection.loopPolicy,
  };
}

function normalizePlatformTemplate(template: RawPlatformWorkflowTemplate): WorkflowTemplateData {
  const workflowTemplateKey =
    template.workflowTemplateKey || template.templateKey || template.workflow_template_key || template.key || "";

  return {
    workflowTemplateKey,
    name: template.name || workflowTemplateKey || "未命名工作流模板",
    description: template.description || "",
    nodes: (template.nodes || []).map(normalizeNode),
    connections: (template.connections || []).map(normalizeConnection),
    version: template.version || "1.0",
    source: template.source || "java-mysql",
    createdAt: template.createdAt || "",
    updatedAt: template.updatedAt || "",
  };
}

export function getWorkflowTemplates(): Promise<WorkflowTemplate[]> {
  return apiClient
    .get<ApiResponse<RawWorkflowTemplate[]> | RawWorkflowTemplate[]>(workflowPath("/templates"))
    .then((response) => unwrapApiResponse<RawWorkflowTemplate[]>(response.data).map(normalizeTemplate));
}

export function instantiateWorkflow(
  templateKey: string,
  inputData: Record<string, unknown>,
  templateData?: Record<string, unknown>,
): Promise<InstantiateWorkflowResponse> {
  const payload: InstantiateWorkflowRequest = {
    template_key: templateKey,
    input_data: inputData,
    template_data: templateData,
  };

  return apiClient
    .post<ApiResponse<RawInstantiateWorkflowResponse> | RawInstantiateWorkflowResponse>(
      workflowPath("/instantiate"),
      payload,
    )
    .then((response) => normalizeInstantiateResponse(unwrapApiResponse<RawInstantiateWorkflowResponse>(response.data)));
}

export function getPlatformWorkflowTemplates(): Promise<WorkflowTemplateData[]> {
  if (currentApiMode !== "java") {
    return Promise.resolve([]);
  }

  return apiClient
    .get<ApiResponse<RawPlatformWorkflowTemplate[]>>(platformWorkflowPath("/templates"))
    .then((response) => unwrapApiResponse<RawPlatformWorkflowTemplate[]>(response.data).map(normalizePlatformTemplate));
}

export function savePlatformWorkflowTemplate(template: WorkflowTemplateData): Promise<WorkflowTemplateData> {
  if (currentApiMode !== "java") {
    return Promise.reject(new Error("保存到 MySQL 仅 Java Gateway 模式支持"));
  }

  return apiClient
    .post<ApiResponse<RawPlatformWorkflowTemplate>>(platformWorkflowPath("/templates"), template)
    .then((response) => normalizePlatformTemplate(unwrapApiResponse<RawPlatformWorkflowTemplate>(response.data)));
}

export function instantiatePlatformWorkflowTemplate(
  templateKey: string,
  inputData: Record<string, unknown>,
): Promise<InstantiateWorkflowResponse> {
  if (currentApiMode !== "java") {
    return Promise.reject(new Error("从 MySQL 模板生成回放任务仅 Java Gateway 模式支持"));
  }

  return apiClient
    .post<ApiResponse<RawInstantiateWorkflowResponse>>(platformWorkflowPath(`/templates/${templateKey}/instantiate`), {
      input_data: inputData,
    })
    .then((response) => normalizeInstantiateResponse(unwrapApiResponse<RawInstantiateWorkflowResponse>(response.data)));
}

export function executePlatformWorkflowTemplate(
  templateKey: string,
  inputData: Record<string, unknown>,
): Promise<WorkflowRuntimeExecutionResult> {
  if (currentApiMode !== "java") {
    return Promise.reject(new Error("Workflow Runtime Lite 仅 Java Gateway 模式支持"));
  }

  return apiClient
    .post<ApiResponse<RawWorkflowRuntimeExecutionResult>>(platformWorkflowPath(`/templates/${templateKey}/execute`), {
      input_data: inputData,
    })
    .then((response) =>
      normalizeRuntimeExecutionResponse(unwrapApiResponse<RawWorkflowRuntimeExecutionResult>(response.data)),
    );
}

export function validatePlatformDynamicLangGraphTemplate(
  templateKey: string,
  inputData: Record<string, unknown> = {},
): Promise<DynamicLangGraphValidationResult> {
  if (currentApiMode !== "java") {
    return Promise.reject(new Error("Dynamic LangGraph 校验仅 Java Gateway 模式支持"));
  }

  return apiClient
    .post<ApiResponse<DynamicLangGraphValidationResult>>(
      platformWorkflowPath(`/templates/${templateKey}/validate-langgraph`),
      { input_data: inputData },
    )
    .then((response) => unwrapApiResponse<DynamicLangGraphValidationResult>(response.data));
}

export function executePlatformDynamicLangGraphTemplate(
  templateKey: string,
  inputData: Record<string, unknown>,
): Promise<DynamicLangGraphExecutionResult> {
  if (currentApiMode !== "java") {
    return Promise.reject(new Error("Dynamic LangGraph 执行仅 Java Gateway 模式支持"));
  }

  return apiClient
    .post<ApiResponse<RawWorkflowRuntimeExecutionResult>>(platformWorkflowPath(`/templates/${templateKey}/execute-langgraph`), {
      input_data: inputData,
    })
    .then((response) =>
      normalizeRuntimeExecutionResponse(
        unwrapApiResponse<RawWorkflowRuntimeExecutionResult>(response.data),
      ) as DynamicLangGraphExecutionResult,
    );
}

export function resumePlatformDynamicLangGraphRun(
  platformRunId: string,
  approved: boolean,
  comment = "",
): Promise<DynamicLangGraphExecutionResult> {
  if (currentApiMode !== "java") {
    return Promise.reject(new Error("Dynamic LangGraph 恢复仅 Java Gateway 模式支持"));
  }

  return apiClient
    .post<ApiResponse<RawWorkflowRuntimeExecutionResult>>(platformWorkflowPath(`/runs/${platformRunId}/resume`), {
      approved,
      comment,
    })
    .then((response) =>
      normalizeRuntimeExecutionResponse(
        unwrapApiResponse<RawWorkflowRuntimeExecutionResult>(response.data),
      ) as DynamicLangGraphExecutionResult,
    );
}

export function exportPlatformWorkflowSkill(templateKey: string): Promise<WorkflowSkillExportResult> {
  if (currentApiMode !== "java") {
    return Promise.reject(new Error("Workflow Skill 导出仅 Java Gateway 模式支持"));
  }

  return apiClient
    .post<ApiResponse<WorkflowSkillExportResult>>(platformWorkflowPath(`/templates/${templateKey}/export-skill`))
    .then((response) => unwrapApiResponse<WorkflowSkillExportResult>(response.data));
}

export function deletePlatformWorkflowTemplate(templateKey: string): Promise<WorkflowTemplateData> {
  if (currentApiMode !== "java") {
    return Promise.reject(new Error("删除 MySQL 模板仅 Java Gateway 模式支持"));
  }

  return apiClient
    .delete<ApiResponse<RawPlatformWorkflowTemplate>>(platformWorkflowPath(`/templates/${templateKey}`))
    .then((response) => normalizePlatformTemplate(unwrapApiResponse<RawPlatformWorkflowTemplate>(response.data)));
}

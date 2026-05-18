import { apiClient, currentApiMode } from "./client";

import type { ApiResponse } from "@/types/api";
import type {
  InstantiateWorkflowRequest,
  InstantiateWorkflowResponse,
  WorkflowTemplate,
} from "@/types/workflow";

type RawWorkflowTemplate = Partial<WorkflowTemplate> & {
  agentSequence?: string[];
  stageSequence?: string[];
  mdPath?: string;
};

type RawInstantiateWorkflowResponse = Partial<InstantiateWorkflowResponse> & {
  platform_run_id?: string;
};

function workflowPath(path: string) {
  return currentApiMode === "java" ? `/workflows${path}` : `/api/workflows${path}`;
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

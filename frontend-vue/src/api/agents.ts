import { apiClient, currentApiMode } from "./client";

import type { AgentMeta } from "@/types/agent";
import type { ApiResponse } from "@/types/api";

type RawAgentMeta = Partial<AgentMeta> & {
  inputFields?: string[];
  outputFields?: string[];
};

function unwrapApiResponse<T>(response: ApiResponse<T> | T): T {
  if (currentApiMode === "java") {
    const apiResponse = response as ApiResponse<T>;
    if (!apiResponse.success) {
      throw new Error(apiResponse.message || "Java agents request failed");
    }

    return apiResponse.data;
  }

  return response as T;
}

function normalizeAgent(agent: RawAgentMeta): AgentMeta {
  return {
    key: agent.key || "",
    name: agent.name || agent.key || "",
    role: agent.role || "",
    description: agent.description || "",
    input_fields: agent.input_fields || agent.inputFields || [],
    output_fields: agent.output_fields || agent.outputFields || [],
    stage: agent.stage || "",
    enabled: agent.enabled ?? true,
    version: agent.version || "1.0",
  };
}

export function getAgents(): Promise<AgentMeta[]> {
  return apiClient
    .get<ApiResponse<RawAgentMeta[]> | RawAgentMeta[]>("/agents")
    .then((response) => unwrapApiResponse<RawAgentMeta[]>(response.data).map(normalizeAgent));
}

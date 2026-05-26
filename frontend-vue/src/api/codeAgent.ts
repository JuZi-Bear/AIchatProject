import { apiClient, currentApiMode } from "./client";
import { normalizeRunEvent } from "./events";

import type { ApiResponse } from "@/types/api";
import type {
  CodeAgentOperationResult,
  CodeAgentRequest,
  CodeAgentResponse,
} from "@/types/codeAgent";
import type { RunEvent } from "@/types/runEvent";

type RawCodeAgentResult = Omit<Partial<CodeAgentOperationResult>, "events"> & {
  events?: Array<Partial<RunEvent> & Record<string, unknown>>;
};

type RawCodeAgentResponse = Omit<Partial<CodeAgentResponse>, "results" | "events"> & {
  platform_run_id?: string;
  results?: RawCodeAgentResult[];
  events?: Array<Partial<RunEvent> & Record<string, unknown>>;
};

function codeAgentPath(path: string) {
  return currentApiMode === "java" ? `/code-agent${path}` : `/api/code-agent${path}`;
}

function unwrapApiResponse<T>(response: ApiResponse<T> | T): T {
  if (currentApiMode === "java") {
    const apiResponse = response as ApiResponse<T>;
    if (!apiResponse.success) {
      throw new Error(apiResponse.message || "Java CodeAgent request failed");
    }

    return apiResponse.data;
  }

  return response as T;
}

function normalizeOperationResult(result: RawCodeAgentResult): CodeAgentOperationResult {
  return {
    success: Boolean(result.success),
    operation: result.operation || "",
    filePath: result.filePath || "",
    message: result.message || "",
    content: result.content,
    files: result.files || [],
    fileTree: result.fileTree || [],
    folderFiles: result.folderFiles || [],
    blockedFiles: result.blockedFiles || [],
    changes: result.changes || [],
    backups: result.backups || [],
    summary: result.summary || {},
    baseDir: result.baseDir || "",
    dryRun: Boolean(result.dryRun),
    auditPath: result.auditPath || "",
    truncated: Boolean(result.truncated),
    events: (result.events || []).map(normalizeRunEvent),
  };
}

function normalizeCodeAgentResponse(response: RawCodeAgentResponse): CodeAgentResponse {
  return {
    success: Boolean(response.success),
    agent: response.agent || "code_agent",
    operation: response.operation || "",
    filePath: response.filePath || "",
    message: response.message || "",
    auditPath: response.auditPath || "",
    platformRunId: response.platformRunId || response.platform_run_id || "",
    results: (response.results || []).map(normalizeOperationResult),
    events: (response.events || []).map(normalizeRunEvent),
  };
}

export function executeCodeAgent(payload: CodeAgentRequest): Promise<CodeAgentResponse> {
  return apiClient
    .post<ApiResponse<RawCodeAgentResponse> | RawCodeAgentResponse>(codeAgentPath("/execute"), payload)
    .then((response) => normalizeCodeAgentResponse(unwrapApiResponse<RawCodeAgentResponse>(response.data)));
}

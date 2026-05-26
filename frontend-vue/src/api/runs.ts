import { apiClient, currentApiMode } from "./client";

import type { ApiResponse } from "@/types/api";
import type { PlatformRunRecord, RawPlatformRunResponse } from "@/types/platformRun";
import type { RunHistoryItem, RunRequest, RunResponse, RunSummary } from "@/types/run";

type RawRunHistoryItem = Partial<RunHistoryItem> & {
  run_summary?: Partial<RunSummary>;
};

type RawPlatformRunRecord = Partial<PlatformRunRecord> & {
  platform_run_id?: string;
  python_run_id?: string;
  status?: string;
  model_provider?: string;
  model_name?: string;
  model_base_url?: string;
  retry_count?: number;
  test_success?: boolean;
  coverage_percent?: number;
  quality_score?: number;
  security_status?: string;
  report_path?: string;
  state_path?: string;
  runner_mode?: string;
  runner_warning?: string;
  created_at?: string;
  updated_at?: string;
  run_summary_json?: string;
  ui_view_model_json?: string;
  plugin_results_json?: string;
  error_summary?: string;
  approved?: boolean;
  require_human_approval?: boolean;
  raw_response?: RawPlatformRunResponse;
};

function createdAtFromRunId(runId?: string) {
  const match = (runId || "").match(/run_(\d{4})(\d{2})(\d{2})_(\d{2})(\d{2})(\d{2})/);

  if (!match) {
    return "";
  }

  const [, year, month, day, hour, minute, second] = match;
  return `${year}-${month}-${day} ${hour}:${minute}:${second}`;
}

function normalizeHistoryItem(item: RawRunHistoryItem): RunHistoryItem {
  const summary: Partial<RunSummary> = item.run_summary || {};

  return {
    run_id: item.run_id || "",
    source: item.source || "python",
    run_summary: item.run_summary as RunHistoryItem["run_summary"],
    success: summary.success ?? item.success ?? false,
    retry_count: summary.retry_count ?? item.retry_count ?? 0,
    test_success: summary.test_success ?? item.test_success ?? false,
    coverage_percent: summary.coverage_percent ?? item.coverage_percent ?? 0,
    quality_score: summary.quality_score ?? item.quality_score ?? 0,
    model_provider: summary.model_provider ?? item.model_provider ?? "",
    model_name: item.model_name || "",
    requirement: item.requirement || "",
    created_at: item.created_at || createdAtFromRunId(item.run_id),
    report_path: summary.report_path ?? item.report_path ?? "",
    state_path: item.state_path || "",
  };
}

function unwrapApiResponse<T>(response: ApiResponse<T>): T {
  if (!response.success) {
    throw new Error(response.message || "Java platform request failed");
  }

  return response.data;
}

function parseRawResponse(rawResponse: RawPlatformRunResponse): RunResponse | null {
  if (!rawResponse) {
    return null;
  }

  if (typeof rawResponse === "string") {
    try {
      return JSON.parse(rawResponse) as RunResponse;
    } catch {
      return null;
    }
  }

  if (typeof rawResponse === "object" && "run_id" in rawResponse) {
    return rawResponse as RunResponse;
  }

  return null;
}

function parseJsonObject<T>(rawJson?: string): Partial<T> | null {
  if (!rawJson) {
    return null;
  }

  try {
    return JSON.parse(rawJson) as Partial<T>;
  } catch {
    return null;
  }
}

function normalizePlatformRun(item: RawPlatformRunRecord): PlatformRunRecord {
  return {
    id: item.id,
    platformRunId: item.platformRunId || item.platform_run_id || "",
    pythonRunId: item.pythonRunId || item.python_run_id || "",
    status: item.status || "",
    requirement: item.requirement || "",
    modelProvider: item.modelProvider || item.model_provider || "",
    modelName: item.modelName || item.model_name || "",
    modelBaseUrl: item.modelBaseUrl || item.model_base_url || "",
    success: Boolean(item.success),
    retryCount: Number(item.retryCount ?? item.retry_count ?? 0),
    testSuccess: Boolean(item.testSuccess ?? item.test_success ?? false),
    coveragePercent: Number(item.coveragePercent ?? item.coverage_percent ?? 0),
    qualityScore: Number(item.qualityScore ?? item.quality_score ?? 0),
    securityStatus: item.securityStatus || item.security_status || "",
    reportPath: item.reportPath || item.report_path || "",
    statePath: item.statePath || item.state_path || "",
    runnerMode: item.runnerMode || item.runner_mode || "",
    runnerWarning: item.runnerWarning || item.runner_warning || "",
    createdAt: item.createdAt || item.created_at || "",
    updatedAt: item.updatedAt || item.updated_at || "",
    runSummaryJson: item.runSummaryJson || item.run_summary_json || "",
    uiViewModelJson: item.uiViewModelJson || item.ui_view_model_json || "",
    pluginResultsJson: item.pluginResultsJson || item.plugin_results_json || "",
    errorSummary: item.errorSummary || item.error_summary || "",
    approved: Boolean(item.approved),
    requireHumanApproval: Boolean(item.requireHumanApproval ?? item.require_human_approval ?? false),
    rawResponse: item.rawResponse ?? item.raw_response,
  };
}

export function platformRunToHistoryItem(record: PlatformRunRecord): RunHistoryItem {
  return {
    run_id: record.platformRunId,
    platform_run_id: record.platformRunId,
    python_run_id: record.pythonRunId,
    source: "java",
    success: record.success,
    retry_count: record.retryCount,
    test_success: Boolean(record.testSuccess),
    coverage_percent: Number(record.coveragePercent || 0),
    quality_score: record.qualityScore,
    model_provider: record.modelProvider,
    model_name: record.modelName || "",
    requirement: record.requirement,
    created_at: record.createdAt,
    updated_at: record.updatedAt,
    report_path: record.reportPath,
    state_path: record.statePath || "",
    runner_mode: record.runnerMode,
    runner_warning: record.runnerWarning,
  };
}

export function platformRunToRunResponse(record: PlatformRunRecord): RunResponse {
  const rawResponse = parseRawResponse(record.rawResponse);

  if (rawResponse?.run_summary || rawResponse?.ui_view_model) {
    return rawResponse;
  }

  const parsedRunSummary = parseJsonObject<RunSummary>(record.runSummaryJson);
  const parsedUIViewModel = parseJsonObject<RunResponse["ui_view_model"]>(record.uiViewModelJson);
  const parsedPluginResults = parseJsonObject<Record<string, unknown>>(record.pluginResultsJson);
  const runId = record.pythonRunId || record.platformRunId;
  const runSummary: RunSummary = {
    ...(parsedRunSummary || {}),
    run_id: runId,
    requirement: record.requirement,
    success: record.success,
    retry_count: record.retryCount,
    test_success: Boolean(record.testSuccess),
    coverage_percent: Number(record.coveragePercent || 0),
    quality_score: record.qualityScore,
    security_status: record.securityStatus || "",
    enabled_plugins: [],
    model_provider: record.modelProvider,
    model_name: record.modelName || parsedRunSummary?.model_name,
    report_path: record.reportPath,
    state_path: record.statePath,
    runner_mode: record.runnerMode || parsedRunSummary?.runner_mode,
    runner_warning: record.runnerWarning || parsedRunSummary?.runner_warning,
  };

  return {
    run_id: runId,
    platform_run_id: record.platformRunId,
    platformRunId: record.platformRunId,
    run_summary: runSummary,
    ui_view_model: {
      ...(parsedUIViewModel || {}),
      summary_cards: runSummary,
      workflow_steps: parsedUIViewModel?.workflow_steps || [],
      agent_outputs: {
        ...parsedUIViewModel?.agent_outputs,
        product_result: record.requirement,
        error_summary: record.errorSummary || parsedUIViewModel?.agent_outputs?.error_summary,
      },
      plugin_outputs: parsedUIViewModel?.plugin_outputs || {
        plugin_results: Array.isArray(parsedPluginResults) ? parsedPluginResults : undefined,
        ...(parsedPluginResults && !Array.isArray(parsedPluginResults) ? parsedPluginResults : {}),
      },
      report: {
        ...parsedUIViewModel?.report,
        report_path: record.reportPath,
        run_id: runId,
      },
      raw: {
        ...(parsedUIViewModel?.raw || {}),
        platformRunId: record.platformRunId,
        pythonRunId: record.pythonRunId,
        createdAt: record.createdAt,
        modelName: record.modelName,
        modelBaseUrl: record.modelBaseUrl,
        runnerMode: record.runnerMode,
        runnerWarning: record.runnerWarning,
        approved: record.approved,
        requireHumanApproval: record.requireHumanApproval,
      },
    },
  };
}

export function getRuns(): Promise<RunHistoryItem[]> {
  return apiClient
    .get<RawRunHistoryItem[]>("/runs")
    .then((response) => response.data.map(normalizeHistoryItem));
}

export function getRun(runId: string): Promise<RunResponse> {
  return apiClient.get<RunResponse>(`/runs/${runId}`).then((response) => response.data);
}

export function getPlatformRuns(): Promise<PlatformRunRecord[]> {
  if (currentApiMode !== "java") {
    return Promise.resolve([]);
  }

  return apiClient
    .get<ApiResponse<RawPlatformRunRecord[]>>("/platform/runs")
    .then((response) => unwrapApiResponse(response.data).map(normalizePlatformRun));
}

export function getPlatformRunDetail(platformRunId: string): Promise<PlatformRunRecord> {
  if (currentApiMode !== "java") {
    return Promise.reject(new Error("Platform run detail is only available in Java Gateway mode"));
  }

  return apiClient
    .get<ApiResponse<RawPlatformRunRecord>>(`/platform/runs/${platformRunId}`)
    .then((response) => normalizePlatformRun(unwrapApiResponse(response.data)));
}

export function approvePlatformRun(
  platformRunId: string,
  approved: boolean,
  comment = "",
): Promise<PlatformRunRecord> {
  if (currentApiMode !== "java") {
    return Promise.reject(new Error("Human approval is only available in Java Gateway mode"));
  }

  return apiClient
    .post<ApiResponse<RawPlatformRunRecord>>(`/platform/runs/${platformRunId}/approval`, {
      approved,
      comment,
    })
    .then((response) => normalizePlatformRun(unwrapApiResponse(response.data)));
}

export function postRun(payload: RunRequest): Promise<RunResponse> {
  return apiClient.post<RunResponse>("/runs", payload).then((response) => response.data);
}

export const createRun = postRun;

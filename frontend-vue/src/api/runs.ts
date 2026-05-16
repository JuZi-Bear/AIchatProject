import { apiClient } from "./client";

import type { RunHistoryItem, RunRequest, RunResponse, RunSummary } from "@/types/run";

type RawRunHistoryItem = Partial<RunHistoryItem> & {
  run_summary?: Partial<RunSummary>;
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

export function getRuns(): Promise<RunHistoryItem[]> {
  return apiClient
    .get<RawRunHistoryItem[]>("/runs")
    .then((response) => response.data.map(normalizeHistoryItem));
}

export function getRun(runId: string): Promise<RunResponse> {
  return apiClient.get<RunResponse>(`/runs/${runId}`).then((response) => response.data);
}

export function postRun(payload: RunRequest): Promise<RunResponse> {
  return apiClient.post<RunResponse>("/runs", payload).then((response) => response.data);
}

export const createRun = postRun;

import { apiClient, currentApiMode } from "./client";

import type { ApiResponse } from "@/types/api";
import type { ReplayEvent, WorkflowReplayData } from "@/types/replay";

type RawReplayEvent = Partial<ReplayEvent> & {
  platform_run_id?: string;
  python_run_id?: string;
  event_type?: string;
  event_text?: string;
  detail_json?: string;
  created_at?: string;
};

type RawWorkflowReplayData = Partial<WorkflowReplayData> & {
  platform_run_id?: string;
  python_run_id?: string;
  status_text?: string;
  quality_score?: number;
  duration_ms?: number;
  run_summary?: WorkflowReplayData["runSummary"];
  ui_view_model?: WorkflowReplayData["uiViewModel"];
  events?: RawReplayEvent[];
};

function unwrapApiResponse<T>(response: ApiResponse<T>): T {
  if (!response.success) {
    throw new Error(response.message || "Java workflow replay request failed");
  }

  return response.data;
}

function normalizeReplayEvent(event: RawReplayEvent): ReplayEvent {
  return {
    id: Number(event.id || 0),
    platformRunId: event.platformRunId || event.platform_run_id || "",
    pythonRunId: event.pythonRunId || event.python_run_id || "",
    eventType: event.eventType || event.event_type || "",
    eventText: event.eventText || event.event_text || "",
    agent: event.agent || "",
    status: event.status || "",
    message: event.message || "",
    detailJson: event.detailJson || event.detail_json || "",
    createdAt: event.createdAt || event.created_at || "",
  };
}

function normalizeReplayData(data: RawWorkflowReplayData): WorkflowReplayData {
  return {
    platformRunId: data.platformRunId || data.platform_run_id || "",
    pythonRunId: data.pythonRunId || data.python_run_id || "",
    requirement: data.requirement || "",
    status: data.status || "",
    statusText: data.statusText || data.status_text || "",
    success: Boolean(data.success),
    qualityScore: Number(data.qualityScore ?? data.quality_score ?? 0),
    durationMs: Number(data.durationMs ?? data.duration_ms ?? 0),
    events: (data.events || []).map(normalizeReplayEvent),
    runSummary: data.runSummary || data.run_summary || {},
    uiViewModel: data.uiViewModel || data.ui_view_model || {},
  };
}

export function getWorkflowReplay(platformRunId: string): Promise<WorkflowReplayData> {
  if (currentApiMode !== "java") {
    return Promise.reject(new Error("工作流回放仅 Java Gateway + MySQL 模式支持"));
  }

  return apiClient
    .get<ApiResponse<RawWorkflowReplayData>>(`/platform/runs/${platformRunId}/replay`)
    .then((response) => normalizeReplayData(unwrapApiResponse(response.data)));
}

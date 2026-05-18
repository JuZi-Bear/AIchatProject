import { apiClient, currentApiMode } from "./client";

import type { ApiResponse } from "@/types/api";
import type { RunEvent } from "@/types/runEvent";

type RawRunEvent = Partial<RunEvent> & {
  platform_run_id?: string;
  python_run_id?: string;
  event_type?: string;
  event_text?: string;
  detail_json?: string;
  created_at?: string;
};

function unwrapApiResponse<T>(response: ApiResponse<T>): T {
  if (!response.success) {
    throw new Error(response.message || "Java platform event request failed");
  }

  return response.data;
}

export function normalizeRunEvent(event: RawRunEvent): RunEvent {
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

export function getRunEvents(platformRunId: string): Promise<RunEvent[]> {
  if (currentApiMode !== "java" || !platformRunId) {
    return Promise.resolve([]);
  }

  return apiClient
    .get<ApiResponse<RawRunEvent[]>>(`/platform/runs/${platformRunId}/events`)
    .then((response) => unwrapApiResponse(response.data).map(normalizeRunEvent));
}

export function getRecentEvents(limit = 20): Promise<RunEvent[]> {
  if (currentApiMode !== "java") {
    return Promise.resolve([]);
  }

  return apiClient
    .get<ApiResponse<RawRunEvent[]>>("/platform/events/recent", { params: { limit } })
    .then((response) => unwrapApiResponse(response.data).map(normalizeRunEvent));
}

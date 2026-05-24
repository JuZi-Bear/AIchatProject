import type { RunSummary, UIViewModel } from "./run";

export type ReplayStatus = "CREATED" | "RUNNING" | "SUCCESS" | "FAILED" | "CANCELLED" | string;

export type ReplayEvent = {
  id?: number;
  platformRunId: string;
  pythonRunId?: string;
  eventType: string;
  eventText: string;
  agent?: string;
  status?: string;
  message?: string;
  detailJson?: string;
  createdAt: string;
};

export type WorkflowReplayData = {
  platformRunId: string;
  pythonRunId?: string;
  requirement: string;
  status: ReplayStatus;
  statusText: string;
  success: boolean;
  qualityScore: number;
  durationMs: number;
  events: ReplayEvent[];
  runSummary: Partial<RunSummary> & Record<string, unknown>;
  uiViewModel: Partial<UIViewModel> & Record<string, unknown>;
};

export type ReplayControlState = {
  currentIndex: number;
  playing: boolean;
  speedMs: number;
};

export type ReplayFilterState = {
  agent: string;
  status: string;
  keyword: string;
};

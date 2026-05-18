import type { RunResponse } from "./run";

export type RawPlatformRunResponse = RunResponse | string | Record<string, unknown> | null | undefined;

export type PlatformRunRecord = {
  id?: number;
  platformRunId: string;
  pythonRunId: string;
  status?: string;
  requirement: string;
  modelProvider: string;
  modelName?: string;
  modelBaseUrl?: string;
  success: boolean;
  retryCount: number;
  testSuccess?: boolean;
  coveragePercent?: number;
  qualityScore: number;
  securityStatus?: string;
  reportPath: string;
  statePath?: string;
  runnerMode?: string;
  runnerWarning?: string;
  createdAt: string;
  updatedAt?: string;
  runSummaryJson?: string;
  uiViewModelJson?: string;
  pluginResultsJson?: string;
  errorSummary?: string;
  approved?: boolean;
  requireHumanApproval?: boolean;
  rawResponse?: RawPlatformRunResponse;
};

export type PlatformStats = {
  totalRuns: number;
  successRuns: number;
  failedRuns: number;
  averageQualityScore: number;
  totalReports: number;
  testSuccessRuns: number;
  repairedRuns: number;
};

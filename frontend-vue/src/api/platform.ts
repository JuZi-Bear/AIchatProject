export {
  getPlatformRunDetail as getPlatformRun,
  getPlatformRuns,
  platformRunToHistoryItem,
  platformRunToRunResponse,
} from "./runs";

import { apiClient, currentApiMode } from "./client";

import type { ApiResponse } from "@/types/api";
import type { PlatformStats } from "@/types/platformRun";

const emptyPlatformStats: PlatformStats = {
  totalRuns: 0,
  successRuns: 0,
  failedRuns: 0,
  averageQualityScore: 0,
  totalReports: 0,
  testSuccessRuns: 0,
  repairedRuns: 0,
};

function unwrapApiResponse<T>(response: ApiResponse<T>): T {
  if (!response.success) {
    throw new Error(response.message || "Java platform request failed");
  }

  return response.data;
}

function normalizePlatformStats(stats: Partial<PlatformStats>): PlatformStats {
  return {
    totalRuns: Number(stats.totalRuns || 0),
    successRuns: Number(stats.successRuns || 0),
    failedRuns: Number(stats.failedRuns || 0),
    averageQualityScore: Number(stats.averageQualityScore || 0),
    totalReports: Number(stats.totalReports || 0),
    testSuccessRuns: Number(stats.testSuccessRuns || 0),
    repairedRuns: Number(stats.repairedRuns || 0),
  };
}

export function getPlatformStats(): Promise<PlatformStats> {
  if (currentApiMode !== "java") {
    return Promise.resolve(emptyPlatformStats);
  }

  return apiClient
    .get<ApiResponse<Partial<PlatformStats>>>("/platform/stats")
    .then((response) => normalizePlatformStats(unwrapApiResponse(response.data)));
}

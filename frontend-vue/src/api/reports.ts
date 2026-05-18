import { apiClient, currentApiMode } from "./client";

import type { ApiResponse } from "@/types/api";
import type { ReportDetail, ReportItem } from "@/types/run";

type RawReportItem = {
  name?: string;
  path?: string;
  size?: number;
  modified_time?: string;
  created_at?: string;
};

type RawReportDetail = {
  name?: string;
  path?: string;
  content?: string;
};

type RawPlatformReportItem = {
  reportName?: string;
  report_name?: string;
  reportPath?: string;
  report_path?: string;
  platformRunId?: string;
  platform_run_id?: string;
  pythonRunId?: string;
  python_run_id?: string;
  requirement?: string;
  success?: boolean;
  qualityScore?: number;
  quality_score?: number;
  createdAt?: string;
  created_at?: string;
  updatedAt?: string;
  updated_at?: string;
};

type RawPlatformReportDetail = {
  reportName?: string;
  reportIndex?: RawPlatformReportItem;
  report?: RawReportDetail;
  content?: string;
  error?: string;
};

function runIdFromReportName(reportName?: string) {
  const match = (reportName || "").match(/(run_\d{8}_\d{6}(?:_model\d+)?)/);
  return match?.[1] || "";
}

function normalizeReportItem(item: RawReportItem): ReportItem {
  const reportName = item.name || "";

  return {
    report_name: reportName,
    name: reportName,
    path: item.path || "",
    created_at: item.created_at || item.modified_time || "",
    modified_time: item.modified_time,
    file_size: item.size,
    size: item.size,
    run_id: runIdFromReportName(reportName),
    source: "python",
  };
}

function normalizeReportDetail(item: RawReportDetail): ReportDetail {
  const reportName = item.name || "";

  return {
    report_name: reportName,
    name: reportName,
    path: item.path || "",
    content: item.content || "",
    run_id: runIdFromReportName(reportName),
    source: "python",
  };
}

function unwrapApiResponse<T>(response: ApiResponse<T>): T {
  if (!response.success) {
    throw new Error(response.message || "Java platform report request failed");
  }

  return response.data;
}

function normalizePlatformReportItem(item: RawPlatformReportItem): ReportItem {
  const reportName = item.reportName || item.report_name || "";
  const pythonRunId = item.pythonRunId || item.python_run_id || runIdFromReportName(reportName);

  return {
    report_name: reportName,
    name: reportName,
    path: item.reportPath || item.report_path || "",
    created_at: item.createdAt || item.created_at || "",
    run_id: pythonRunId,
    platformRunId: item.platformRunId || item.platform_run_id || "",
    pythonRunId,
    requirement: item.requirement || "",
    success: Boolean(item.success),
    qualityScore: Number(item.qualityScore ?? item.quality_score ?? 0),
    source: "java",
  };
}

function normalizePlatformReportDetail(item: RawPlatformReportDetail, fallbackReportName: string): ReportDetail {
  const reportIndex = item.reportIndex || {};
  const report = item.report || {};
  const baseItem = normalizePlatformReportItem({
    ...reportIndex,
    reportName: reportIndex.reportName || item.reportName || fallbackReportName,
  });

  return {
    report_name: baseItem.report_name,
    name: baseItem.name,
    path: baseItem.path || report.path || "",
    content: item.content || report.content || "",
    run_id: baseItem.run_id,
    platformRunId: baseItem.platformRunId,
    pythonRunId: baseItem.pythonRunId,
    requirement: baseItem.requirement,
    success: baseItem.success,
    qualityScore: baseItem.qualityScore,
    created_at: baseItem.created_at,
    error: item.error,
    source: "java",
  };
}

export function getReports(): Promise<ReportItem[]> {
  if (currentApiMode === "java") {
    return apiClient
      .get<ApiResponse<RawPlatformReportItem[]>>("/platform/reports")
      .then((response) => unwrapApiResponse(response.data).map(normalizePlatformReportItem));
  }

  return apiClient.get<RawReportItem[]>("/reports").then((response) => response.data.map(normalizeReportItem));
}

export function getReport(reportName: string): Promise<ReportDetail> {
  if (currentApiMode === "java") {
    return apiClient
      .get<ApiResponse<RawPlatformReportDetail>>(`/platform/reports/${encodeURIComponent(reportName)}`)
      .then((response) => normalizePlatformReportDetail(unwrapApiResponse(response.data), reportName));
  }

  return apiClient.get<RawReportDetail>(`/reports/${reportName}`).then((response) => normalizeReportDetail(response.data));
}
